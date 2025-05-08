"""
任务调度器
负责管理周期性任务的调度和执行
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional, List
from sqlalchemy.orm import Session
from croniter import croniter
import pytz

from models.domain.dataset import ProcessingTask
from core.processing.task_queue import task_queue

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.running = False
        self.check_interval = 60  # 检查间隔，单位：秒
        self._task = None
    
    async def start(self, get_db: Callable) -> None:
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行")
            return
        
        self.running = True
        logger.info("启动任务调度器")
        
        while self.running:
            try:
                # 获取数据库会话
                db_generator = get_db()
                db = next(db_generator)
                
                # 检查并调度任务
                await self._check_and_schedule_tasks(db)
                
                # 关闭数据库会话
                db.close()
            except Exception as e:
                logger.error(f"调度任务时出错: {str(e)}")
            
            # 等待下一次检查
            await asyncio.sleep(self.check_interval)
    
    async def stop(self) -> None:
        """停止调度器"""
        if not self.running:
            logger.warning("调度器未运行")
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        logger.info("停止任务调度器")
    
    async def _check_and_schedule_tasks(self, db: Session) -> None:
        """检查并调度任务"""
        # 获取当前时间
        now = datetime.now(pytz.UTC)
        
        # 查询需要调度的任务
        tasks = self._get_tasks_to_schedule(db, now)
        
        if not tasks:
            return
        
        logger.info(f"找到 {len(tasks)} 个需要调度的任务")
        
        # 调度任务
        for task in tasks:
            await self._schedule_task(db, task, now)
    
    def _get_tasks_to_schedule(self, db: Session, now: datetime) -> List[ProcessingTask]:
        """获取需要调度的任务"""
        # 查询所有周期性任务，且下次运行时间小于等于当前时间
        tasks = db.query(ProcessingTask).filter(
            ProcessingTask.is_recurring == True,
            ProcessingTask.next_run_time <= now,
            ProcessingTask.status.in_(["completed", "failed", "cancelled"])  # 只调度已完成、失败或取消的任务
        ).all()
        
        return tasks
    
    async def _schedule_task(self, db: Session, task: ProcessingTask, now: datetime) -> None:
        """调度任务"""
        try:
            # 检查是否达到最大运行次数
            if task.max_runs is not None and task.run_count >= task.max_runs:
                logger.info(f"任务 {task.id} 已达到最大运行次数 {task.max_runs}，停止调度")
                task.is_recurring = False
                db.commit()
                return
            
            # 创建新任务
            new_task = ProcessingTask(
                name=task.name,
                description=task.description,
                task_type=task.task_type,
                parameters=task.parameters,
                priority=task.priority,
                data_source_id=task.data_source_id,
                user_id=task.user_id,
                status="pending"
            )
            
            db.add(new_task)
            db.flush()
            
            # 更新原任务的调度信息
            task.last_run_time = now
            task.run_count += 1
            task.next_run_time = self._calculate_next_run_time(task, now)
            
            db.commit()
            
            # 将新任务添加到任务队列
            await task_queue.add_task(new_task.id)
            
            logger.info(f"成功调度任务 {task.id}，创建新任务 {new_task.id}，下次运行时间: {task.next_run_time}")
        except Exception as e:
            db.rollback()
            logger.error(f"调度任务 {task.id} 时出错: {str(e)}")
    
    def _calculate_next_run_time(self, task: ProcessingTask, now: datetime) -> datetime:
        """计算下次运行时间"""
        if not task.schedule_type or not task.schedule_value:
            # 默认每天运行一次
            return now + timedelta(days=1)
        
        if task.schedule_type == "once":
            # 一次性任务，不再调度
            task.is_recurring = False
            return None
        
        if task.schedule_type == "daily":
            # 每天运行
            days = int(task.schedule_value) if task.schedule_value.isdigit() else 1
            return now + timedelta(days=days)
        
        if task.schedule_type == "weekly":
            # 每周运行
            weeks = int(task.schedule_value) if task.schedule_value.isdigit() else 1
            return now + timedelta(weeks=weeks)
        
        if task.schedule_type == "monthly":
            # 每月运行（简化处理，按30天计算）
            months = int(task.schedule_value) if task.schedule_value.isdigit() else 1
            return now + timedelta(days=30 * months)
        
        if task.schedule_type == "cron":
            # 使用cron表达式
            try:
                cron = croniter(task.schedule_value, now)
                return cron.get_next(datetime)
            except Exception as e:
                logger.error(f"解析cron表达式 '{task.schedule_value}' 时出错: {str(e)}")
                # 出错时默认每天运行一次
                return now + timedelta(days=1)
        
        # 默认每天运行一次
        return now + timedelta(days=1)
    
    def schedule_task(self, db: Session, task_id: int, schedule_info: Dict[str, Any]) -> Optional[ProcessingTask]:
        """设置任务调度"""
        try:
            # 获取任务
            task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
            if not task:
                logger.error(f"任务 {task_id} 不存在")
                return None
            
            # 设置调度信息
            task.is_recurring = True
            task.schedule_type = schedule_info.get("schedule_type")
            task.schedule_value = schedule_info.get("schedule_value")
            task.max_runs = schedule_info.get("max_runs")
            
            # 计算下次运行时间
            now = datetime.now(pytz.UTC)
            task.next_run_time = self._calculate_next_run_time(task, now)
            
            db.commit()
            logger.info(f"成功设置任务 {task_id} 的调度，下次运行时间: {task.next_run_time}")
            
            return task
        except Exception as e:
            db.rollback()
            logger.error(f"设置任务 {task_id} 的调度时出错: {str(e)}")
            return None
    
    def cancel_task_schedule(self, db: Session, task_id: int) -> bool:
        """取消任务调度"""
        try:
            # 获取任务
            task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
            if not task:
                logger.error(f"任务 {task_id} 不存在")
                return False
            
            # 取消调度
            task.is_recurring = False
            task.next_run_time = None
            
            db.commit()
            logger.info(f"成功取消任务 {task_id} 的调度")
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"取消任务 {task_id} 的调度时出错: {str(e)}")
            return False


# 创建全局调度器实例
task_scheduler = TaskScheduler()

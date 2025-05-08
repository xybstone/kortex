"""
任务队列系统
管理和调度数据处理任务
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime

from models.domain.dataset import ProcessingTask, DataSource
from core.processing.base import DataProcessor
from core.processing.database_processor import DatabaseProcessor
from core.processing.file_processor import FileProcessor
from core.processing.url_processor import URLProcessor
from services import task_dependency_service, task_history_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskQueue:
    """任务队列管理器"""

    def __init__(self):
        self.processors: Dict[str, DataProcessor] = {}
        self.running_tasks: Dict[int, asyncio.Task] = {}
        self.is_running = False
        self._register_processors()

    def _register_processors(self):
        """注册处理器"""
        # 注册数据库处理器
        db_processor = DatabaseProcessor()
        for task_type in db_processor.get_supported_task_types():
            self.processors[task_type] = db_processor

        # 注册文件处理器
        file_processor = FileProcessor()
        for task_type in file_processor.get_supported_task_types():
            self.processors[task_type] = file_processor

        # 注册URL处理器
        url_processor = URLProcessor()
        for task_type in url_processor.get_supported_task_types():
            self.processors[task_type] = url_processor

    async def start(self, db_factory):
        """
        启动任务队列
        :param db_factory: 数据库会话工厂函数
        """
        if self.is_running:
            logger.warning("任务队列已经在运行中")
            return

        self.is_running = True
        logger.info("启动任务队列")

        while self.is_running:
            try:
                # 创建数据库会话
                db = next(db_factory())

                # 获取待处理的任务
                pending_tasks = await self._get_pending_tasks(db)

                # 处理任务
                for task in pending_tasks:
                    if task.id not in self.running_tasks:
                        # 启动任务处理
                        self.running_tasks[task.id] = asyncio.create_task(
                            self._process_task(task.id, db_factory)
                        )

                # 清理已完成的任务
                self._cleanup_completed_tasks()

                # 关闭数据库会话
                db.close()

                # 等待一段时间再检查新任务
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"任务队列处理出错: {str(e)}")
                await asyncio.sleep(10)  # 出错后等待较长时间再重试

    def stop(self):
        """停止任务队列"""
        if not self.is_running:
            logger.warning("任务队列未运行")
            return

        logger.info("停止任务队列")
        self.is_running = False

        # 取消所有运行中的任务
        for task_id, task in self.running_tasks.items():
            if not task.done():
                task.cancel()

        self.running_tasks.clear()

    async def _get_pending_tasks(self, db: Session) -> List[ProcessingTask]:
        """获取待处理的任务"""
        # 获取所有待处理的任务
        pending_tasks = db.query(ProcessingTask).filter(
            ProcessingTask.status == "pending"
        ).order_by(
            ProcessingTask.priority.desc(),
            ProcessingTask.created_at.asc()
        ).limit(20).all()

        # 过滤出依赖已满足的任务
        ready_tasks = []
        for task in pending_tasks:
            # 检查任务依赖是否满足
            if await task_dependency_service.check_dependencies_satisfied(db, task.id):
                ready_tasks.append(task)

                # 限制同时处理的任务数量
                if len(ready_tasks) >= 10:
                    break

        return ready_tasks

    def _cleanup_completed_tasks(self):
        """清理已完成的任务"""
        completed_task_ids = []
        for task_id, task in self.running_tasks.items():
            if task.done():
                completed_task_ids.append(task_id)

        for task_id in completed_task_ids:
            del self.running_tasks[task_id]

    async def _process_task(self, task_id: int, db_factory):
        """
        处理单个任务
        :param task_id: 任务ID
        :param db_factory: 数据库会话工厂函数
        """
        # 创建新的数据库会话
        db = next(db_factory())

        try:
            # 获取任务
            task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return

            # 获取处理器
            processor = self.processors.get(task.task_type)
            if not processor:
                logger.error(f"找不到处理器: {task.task_type}")
                task.status = "failed"
                task.error_message = f"找不到处理器: {task.task_type}"
                db.commit()
                return

            # 更新任务状态
            task.status = "running"
            task.started_at = datetime.now()
            db.commit()

            # 执行处理
            logger.info(f"开始处理任务: {task_id}, 类型: {task.task_type}")
            result = await processor.process(task, db)

            # 处理结果
            if result.get("success", False):
                logger.info(f"任务处理成功: {task_id}")
                task.status = "completed"
                task.completed_at = datetime.now()
                task.result = result.get("result")
            else:
                logger.error(f"任务处理失败: {task_id}, 错误: {result.get('error')}")
                task.status = "failed"
                task.error_message = result.get("error")

            db.commit()

            # 创建执行历史记录
            await task_history_service.create_history_from_task(db, task)

        except Exception as e:
            logger.exception(f"处理任务时出错: {task_id}, 错误: {str(e)}")
            try:
                task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
                if task:
                    task.status = "failed"
                    task.error_message = str(e)
                    db.commit()
            except Exception:
                logger.exception("更新任务状态时出错")
        finally:
            db.close()

    async def add_task(self, db: Session, task_data: Dict[str, Any]) -> Optional[ProcessingTask]:
        """
        添加新任务
        :param db: 数据库会话
        :param task_data: 任务数据
        :return: 创建的任务
        """
        try:
            # 创建任务
            task = ProcessingTask(
                name=task_data.get("name"),
                description=task_data.get("description"),
                task_type=task_data.get("task_type"),
                priority=task_data.get("priority", 0),
                parameters=task_data.get("parameters"),
                data_source_id=task_data.get("data_source_id"),
                is_recurring=task_data.get("is_recurring", False),
                wait_for_dependencies=task_data.get("wait_for_dependencies", True),
                user_id=task_data.get("user_id")
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            # 处理依赖关系
            dependencies = task_data.get("dependencies")
            if dependencies:
                await task_dependency_service.create_dependencies_for_task(db, task.id, dependencies)

            logger.info(f"添加新任务: {task.id}, 类型: {task.task_type}")
            return task

        except Exception as e:
            logger.error(f"添加任务时出错: {str(e)}")
            db.rollback()
            return None

    async def cancel_task(self, db: Session, task_id: int) -> bool:
        """
        取消任务
        :param db: 数据库会话
        :param task_id: 任务ID
        :return: 是否成功取消
        """
        try:
            # 获取任务
            task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False

            # 如果任务已经完成或失败，无法取消
            if task.status in ["completed", "failed", "cancelled"]:
                logger.warning(f"任务已经处于终态，无法取消: {task_id}, 状态: {task.status}")
                return False

            # 如果任务正在运行，尝试取消
            if task_id in self.running_tasks:
                # 获取处理器
                processor = self.processors.get(task.task_type)
                if processor:
                    return processor.cancel(task_id, db)

            # 如果任务未开始，直接更新状态
            task.status = "cancelled"
            db.commit()
            logger.info(f"取消任务: {task_id}")
            return True

        except Exception as e:
            logger.error(f"取消任务时出错: {task_id}, 错误: {str(e)}")
            return False


# 全局任务队列实例
task_queue = TaskQueue()

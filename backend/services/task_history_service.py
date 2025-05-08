"""
任务执行历史记录服务
提供任务执行历史记录的管理功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.domain.dataset import TaskExecutionHistory, ProcessingTask
from models.schemas.dataset import TaskExecutionHistoryCreate, TaskExecutionHistoryResponse


async def create_execution_history(db: Session, history: TaskExecutionHistoryCreate) -> TaskExecutionHistory:
    """创建任务执行历史记录"""
    db_history = TaskExecutionHistory(
        task_id=history.task_id,
        task_name=history.task_name,
        task_type=history.task_type,
        status=history.status,
        started_at=history.started_at,
        completed_at=history.completed_at,
        duration_seconds=history.duration_seconds,
        result_summary=history.result_summary,
        error_message=history.error_message,
        user_id=history.user_id
    )
    
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return db_history


async def get_task_execution_history(db: Session, task_id: int, limit: int = 10, offset: int = 0) -> List[TaskExecutionHistory]:
    """获取任务的执行历史记录"""
    return db.query(TaskExecutionHistory).filter(
        TaskExecutionHistory.task_id == task_id
    ).order_by(desc(TaskExecutionHistory.created_at)).offset(offset).limit(limit).all()


async def get_user_execution_history(db: Session, user_id: int, limit: int = 10, offset: int = 0) -> List[TaskExecutionHistory]:
    """获取用户的执行历史记录"""
    return db.query(TaskExecutionHistory).filter(
        TaskExecutionHistory.user_id == user_id
    ).order_by(desc(TaskExecutionHistory.created_at)).offset(offset).limit(limit).all()


async def create_history_from_task(db: Session, task: ProcessingTask) -> Optional[TaskExecutionHistory]:
    """从任务创建执行历史记录"""
    if not task.started_at or not task.completed_at:
        return None
    
    # 计算执行时长（秒）
    duration = int((task.completed_at - task.started_at).total_seconds())
    
    # 准备结果摘要
    result_summary = None
    if task.result:
        # 如果结果太大，只保留摘要
        if isinstance(task.result, dict):
            result_summary = {}
            for key, value in task.result.items():
                if key in ['summary', 'count', 'status', 'affected_rows', 'success']:
                    result_summary[key] = value
                elif key == 'sample_data' and isinstance(value, list):
                    # 只保留前几条样本数据
                    result_summary['sample_count'] = len(value)
                    if len(value) > 0:
                        result_summary['sample_first'] = value[0]
    
    # 创建历史记录
    history = TaskExecutionHistoryCreate(
        task_id=task.id,
        task_name=task.name,
        task_type=task.task_type,
        status=task.status,
        started_at=task.started_at,
        completed_at=task.completed_at,
        duration_seconds=duration,
        result_summary=result_summary,
        error_message=task.error_message,
        user_id=task.user_id
    )
    
    return await create_execution_history(db, history)


async def get_execution_statistics(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取执行统计信息"""
    query = db.query(TaskExecutionHistory)
    
    if user_id:
        query = query.filter(TaskExecutionHistory.user_id == user_id)
    
    # 总执行次数
    total_count = query.count()
    
    # 成功次数
    success_count = query.filter(TaskExecutionHistory.status == "completed").count()
    
    # 失败次数
    failure_count = query.filter(TaskExecutionHistory.status == "failed").count()
    
    # 取消次数
    cancelled_count = query.filter(TaskExecutionHistory.status == "cancelled").count()
    
    # 平均执行时长
    avg_duration = db.query(
        db.func.avg(TaskExecutionHistory.duration_seconds)
    ).scalar() or 0
    
    # 按任务类型统计
    task_type_stats = {}
    task_types = db.query(TaskExecutionHistory.task_type).distinct().all()
    
    for task_type in task_types:
        type_name = task_type[0]
        type_count = query.filter(TaskExecutionHistory.task_type == type_name).count()
        task_type_stats[type_name] = type_count
    
    return {
        "total_count": total_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "cancelled_count": cancelled_count,
        "avg_duration": round(float(avg_duration), 2),
        "task_type_stats": task_type_stats
    }

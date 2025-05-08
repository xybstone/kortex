"""
处理任务服务
提供处理任务的创建、查询、取消等功能
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import or_

from models.domain.dataset import ProcessingTask, DataSource
from models.schemas.dataset import (
    ProcessingTaskCreate, ProcessingTaskUpdate, ProcessingTaskResponse
)
from core.processing.task_queue import task_queue


async def create_task(db: Session, task: ProcessingTaskCreate) -> Optional[ProcessingTaskResponse]:
    """
    创建处理任务
    :param db: 数据库会话
    :param task: 任务创建请求
    :return: 创建的任务
    """
    # 检查数据源是否存在
    data_source = db.query(DataSource).filter(DataSource.id == task.data_source_id).first()
    if not data_source:
        return None

    # 创建任务
    task_data = {
        "name": task.name,
        "description": task.description,
        "task_type": task.task_type,
        "priority": task.priority,
        "parameters": task.parameters,
        "data_source_id": task.data_source_id,
        "is_recurring": task.is_recurring
    }

    db_task = await task_queue.add_task(db, task_data)
    if not db_task:
        return None

    # 转换为响应模型
    return ProcessingTaskResponse(
        id=db_task.id,
        name=db_task.name,
        description=db_task.description,
        task_type=db_task.task_type,
        data_source_id=db_task.data_source_id,
        status=db_task.status,
        priority=db_task.priority,
        parameters=db_task.parameters,
        result=db_task.result,
        error_message=db_task.error_message,
        started_at=db_task.started_at,
        completed_at=db_task.completed_at,
        progress=db_task.progress,
        is_recurring=db_task.is_recurring,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )


async def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    data_source_id: Optional[int] = None
) -> List[ProcessingTaskResponse]:
    """
    获取处理任务列表
    :param db: 数据库会话
    :param skip: 跳过记录数
    :param limit: 返回记录数
    :param search: 搜索关键词
    :param status: 任务状态
    :param data_source_id: 数据源ID
    :return: 任务列表
    """
    query = db.query(ProcessingTask)

    # 按数据源过滤
    if data_source_id:
        query = query.filter(ProcessingTask.data_source_id == data_source_id)

    # 按状态过滤
    if status:
        query = query.filter(ProcessingTask.status == status)

    # 按关键词搜索
    if search:
        query = query.filter(
            or_(
                ProcessingTask.name.ilike(f"%{search}%"),
                ProcessingTask.description.ilike(f"%{search}%")
            )
        )

    # 获取分页结果
    tasks = query.order_by(
        ProcessingTask.created_at.desc()
    ).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        ProcessingTaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            data_source_id=task.data_source_id,
            status=task.status,
            priority=task.priority,
            parameters=task.parameters,
            result=task.result,
            error_message=task.error_message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            progress=task.progress,
            is_recurring=task.is_recurring,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]


async def get_task(db: Session, task_id: int) -> Optional[ProcessingTaskResponse]:
    """
    获取单个处理任务详情
    :param db: 数据库会话
    :param task_id: 任务ID
    :return: 任务详情
    """
    task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
    if not task:
        return None

    # 转换为响应模型
    return ProcessingTaskResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        task_type=task.task_type,
        data_source_id=task.data_source_id,
        status=task.status,
        priority=task.priority,
        parameters=task.parameters,
        result=task.result,
        error_message=task.error_message,
        started_at=task.started_at,
        completed_at=task.completed_at,
        progress=task.progress,
        is_recurring=task.is_recurring,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


async def update_task(db: Session, task_id: int, task_update: ProcessingTaskUpdate) -> Optional[ProcessingTaskResponse]:
    """
    更新处理任务
    :param db: 数据库会话
    :param task_id: 任务ID
    :param task_update: 任务更新请求
    :return: 更新后的任务
    """
    db_task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
    if not db_task:
        return None

    # 只有待处理的任务才能更新
    if db_task.status != "pending":
        return None

    # 更新任务
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    # 转换为响应模型
    return ProcessingTaskResponse(
        id=db_task.id,
        name=db_task.name,
        description=db_task.description,
        task_type=db_task.task_type,
        data_source_id=db_task.data_source_id,
        status=db_task.status,
        priority=db_task.priority,
        parameters=db_task.parameters,
        result=db_task.result,
        error_message=db_task.error_message,
        started_at=db_task.started_at,
        completed_at=db_task.completed_at,
        progress=db_task.progress,
        is_recurring=db_task.is_recurring,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )


async def cancel_task(db: Session, task_id: int) -> bool:
    """
    取消处理任务
    :param db: 数据库会话
    :param task_id: 任务ID
    :return: 是否成功取消
    """
    return await task_queue.cancel_task(db, task_id)


async def delete_task(db: Session, task_id: int) -> bool:
    """
    删除处理任务
    :param db: 数据库会话
    :param task_id: 任务ID
    :return: 是否成功删除
    """
    db_task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
    if not db_task:
        return False

    # 只有已完成、失败或取消的任务才能删除
    if db_task.status not in ["completed", "failed", "cancelled"]:
        return False

    db.delete(db_task)
    db.commit()
    return True

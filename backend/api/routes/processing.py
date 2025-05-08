"""
处理任务API路由
提供处理任务的创建、查询、取消等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas import (
    ProcessingTaskCreate, ProcessingTaskUpdate, ProcessingTaskResponse,
    UserResponse, ScheduleInfo
)
from services import processing_service
from core.processing.scheduler import task_scheduler

router = APIRouter()


@router.post("/", response_model=ProcessingTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: ProcessingTaskCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建处理任务"""
    # 设置用户ID
    task.user_id = current_user.id

    db_task = await processing_service.create_task(db=db, task=task)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )
    return db_task


@router.get("/", response_model=List[ProcessingTaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    data_source_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取处理任务列表"""
    return await processing_service.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        data_source_id=data_source_id
    )


@router.get("/{task_id}", response_model=ProcessingTaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取处理任务详情"""
    db_task = await processing_service.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return db_task


@router.put("/{task_id}", response_model=ProcessingTaskResponse)
async def update_task(
    task_id: int,
    task_update: ProcessingTaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新处理任务"""
    db_task = await processing_service.update_task(db=db, task_id=task_id, task_update=task_update)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在或无法更新"
        )
    return db_task


@router.post("/{task_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """取消处理任务"""
    success = await processing_service.cancel_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法取消任务"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除处理任务"""
    success = await processing_service.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除任务"
        )


@router.post("/{task_id}/schedule", response_model=ProcessingTaskResponse)
async def schedule_task(
    task_id: int,
    schedule_info: ScheduleInfo,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """设置任务调度"""
    # 检查任务是否存在
    task = await processing_service.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    # 设置任务调度
    scheduled_task = task_scheduler.schedule_task(
        db=db,
        task_id=task_id,
        schedule_info={
            "schedule_type": schedule_info.schedule_type,
            "schedule_value": schedule_info.schedule_value,
            "max_runs": schedule_info.max_runs
        }
    )

    if scheduled_task is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法设置任务调度"
        )

    return scheduled_task


@router.post("/{task_id}/cancel-schedule", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task_schedule(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """取消任务调度"""
    # 检查任务是否存在
    task = await processing_service.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    # 取消任务调度
    success = task_scheduler.cancel_task_schedule(db=db, task_id=task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法取消任务调度"
        )

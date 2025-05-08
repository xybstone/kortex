"""
任务执行历史记录API路由
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from models.schemas.dataset import TaskExecutionHistoryResponse
from models.schemas.user import UserResponse
from services import task_history_service
from api.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/task/{task_id}", response_model=List[TaskExecutionHistoryResponse])
async def get_task_history(
    task_id: int,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务的执行历史记录"""
    history = await task_history_service.get_task_execution_history(
        db=db,
        task_id=task_id,
        limit=limit,
        offset=offset
    )
    
    return history


@router.get("/user", response_model=List[TaskExecutionHistoryResponse])
async def get_user_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户的执行历史记录"""
    history = await task_history_service.get_user_execution_history(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return history


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取执行统计信息"""
    statistics = await task_history_service.get_execution_statistics(
        db=db,
        user_id=current_user.id
    )
    
    return statistics


@router.get("/admin/statistics", response_model=Dict[str, Any])
async def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取所有用户的执行统计信息（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    statistics = await task_history_service.get_execution_statistics(db=db)
    
    return statistics

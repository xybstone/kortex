"""
任务依赖关系API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from models.schemas.dataset import TaskDependencyCreate, TaskDependencyResponse
from models.schemas.user import UserResponse
from services import task_dependency_service
from api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TaskDependencyResponse)
async def create_dependency(
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建任务依赖关系"""
    try:
        db_dependency = await task_dependency_service.create_dependency(db=db, dependency=dependency)
        return db_dependency
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{dependency_id}")
async def delete_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除任务依赖关系"""
    success = await task_dependency_service.delete_dependency(db=db, dependency_id=dependency_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="依赖关系不存在"
        )
    
    return {"message": "依赖关系已删除"}


@router.get("/task/{task_id}/children", response_model=List[TaskDependencyResponse])
async def get_task_children(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务的子任务依赖关系"""
    dependencies = await task_dependency_service.get_task_dependencies(
        db=db,
        task_id=task_id,
        as_parent=True
    )
    
    return dependencies


@router.get("/task/{task_id}/parents", response_model=List[TaskDependencyResponse])
async def get_task_parents(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务的父任务依赖关系"""
    dependencies = await task_dependency_service.get_task_dependencies(
        db=db,
        task_id=task_id,
        as_parent=False
    )
    
    return dependencies


@router.get("/task/{task_id}/check", response_model=bool)
async def check_dependencies_satisfied(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """检查任务的依赖是否满足"""
    satisfied = await task_dependency_service.check_dependencies_satisfied(db=db, task_id=task_id)
    
    return satisfied

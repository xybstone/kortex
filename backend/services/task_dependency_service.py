"""
任务依赖关系服务
提供任务依赖关系的管理功能
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.domain.dataset import TaskDependency, ProcessingTask
from models.schemas.dataset import TaskDependencyCreate, TaskDependencyResponse, DependencyInfo


async def create_dependency(db: Session, dependency: TaskDependencyCreate) -> TaskDependency:
    """创建任务依赖关系"""
    # 检查父任务是否存在
    parent_task = db.query(ProcessingTask).filter(ProcessingTask.id == dependency.parent_task_id).first()
    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"父任务 {dependency.parent_task_id} 不存在"
        )
    
    # 检查子任务是否存在
    child_task = db.query(ProcessingTask).filter(ProcessingTask.id == dependency.child_task_id).first()
    if not child_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"子任务 {dependency.child_task_id} 不存在"
        )
    
    # 检查是否已存在相同的依赖关系
    existing_dependency = db.query(TaskDependency).filter(
        TaskDependency.parent_task_id == dependency.parent_task_id,
        TaskDependency.child_task_id == dependency.child_task_id
    ).first()
    
    if existing_dependency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="依赖关系已存在"
        )
    
    # 检查是否会形成循环依赖
    if await _would_create_cycle(db, dependency.parent_task_id, dependency.child_task_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能创建循环依赖"
        )
    
    # 创建依赖关系
    db_dependency = TaskDependency(
        parent_task_id=dependency.parent_task_id,
        child_task_id=dependency.child_task_id,
        dependency_type=dependency.dependency_type
    )
    
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    
    return db_dependency


async def delete_dependency(db: Session, dependency_id: int) -> bool:
    """删除任务依赖关系"""
    dependency = db.query(TaskDependency).filter(TaskDependency.id == dependency_id).first()
    if not dependency:
        return False
    
    db.delete(dependency)
    db.commit()
    
    return True


async def get_task_dependencies(db: Session, task_id: int, as_parent: bool = True) -> List[TaskDependency]:
    """获取任务的依赖关系"""
    if as_parent:
        # 获取任务作为父任务的依赖关系
        dependencies = db.query(TaskDependency).filter(TaskDependency.parent_task_id == task_id).all()
    else:
        # 获取任务作为子任务的依赖关系
        dependencies = db.query(TaskDependency).filter(TaskDependency.child_task_id == task_id).all()
    
    return dependencies


async def create_dependencies_for_task(db: Session, task_id: int, dependencies: List[DependencyInfo]) -> List[TaskDependency]:
    """为任务创建多个依赖关系"""
    result = []
    
    for dep_info in dependencies:
        # 创建依赖关系
        dependency = TaskDependencyCreate(
            parent_task_id=dep_info.parent_task_id,
            child_task_id=task_id,
            dependency_type=dep_info.dependency_type
        )
        
        try:
            db_dependency = await create_dependency(db, dependency)
            result.append(db_dependency)
        except HTTPException as e:
            # 记录错误但继续处理其他依赖
            print(f"创建依赖关系时出错: {e.detail}")
    
    return result


async def check_dependencies_satisfied(db: Session, task_id: int) -> bool:
    """检查任务的依赖是否满足"""
    # 获取任务
    task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
    if not task:
        return False
    
    # 如果任务不等待依赖，直接返回True
    if not task.wait_for_dependencies:
        return True
    
    # 获取任务的依赖
    dependencies = await get_task_dependencies(db, task_id, as_parent=False)
    
    # 如果没有依赖，返回True
    if not dependencies:
        return True
    
    # 检查每个依赖是否满足
    for dependency in dependencies:
        parent_task = db.query(ProcessingTask).filter(ProcessingTask.id == dependency.parent_task_id).first()
        if not parent_task:
            continue
        
        # 根据依赖类型检查
        if dependency.dependency_type == "success" and parent_task.status != "completed":
            return False
        elif dependency.dependency_type == "failure" and parent_task.status != "failed":
            return False
        elif dependency.dependency_type == "completion" and parent_task.status not in ["completed", "failed", "cancelled"]:
            return False
    
    return True


async def _would_create_cycle(db: Session, parent_id: int, child_id: int) -> bool:
    """检查添加依赖关系是否会形成循环"""
    # 如果父任务和子任务相同，直接形成循环
    if parent_id == child_id:
        return True
    
    # 检查子任务是否已经是父任务的祖先
    visited = set()
    
    def dfs(current_id: int) -> bool:
        if current_id == child_id:
            return True
        
        if current_id in visited:
            return False
        
        visited.add(current_id)
        
        # 获取当前任务的所有父任务
        parents = db.query(TaskDependency).filter(TaskDependency.child_task_id == current_id).all()
        
        for dep in parents:
            if dfs(dep.parent_task_id):
                return True
        
        return False
    
    return dfs(parent_id)

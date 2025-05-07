from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Optional
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from core.config import settings
from models.schemas import (
    DatasetCreate, DatasetUpdate, DatasetResponse,
    DatabaseSourceCreate, FileSourceResponse, URLSourceCreate,
    UserResponse
)
from services import dataset_service

router = APIRouter()

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建新数据集"""
    # 确保数据集关联到当前用户
    dataset.user_id = current_user.id
    return dataset_service.create_dataset(db=db, dataset=dataset)

@router.get("/", response_model=List[DatasetResponse])
def get_datasets(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户的数据集列表"""
    return dataset_service.get_datasets(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        user_id=current_user.id
    )

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取单个数据集详情"""
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return dataset

@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: int,
    dataset_update: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新数据集"""
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return dataset_service.update_dataset(
        db=db, dataset_id=dataset_id, dataset_update=dataset_update
    )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除数据集"""
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    result = dataset_service.delete_dataset(db=db, dataset_id=dataset_id)
    if not result:
        raise HTTPException(status_code=500, detail="删除数据集失败")
    
    return None

@router.post("/{dataset_id}/database-sources", response_model=DatasetResponse)
def add_database_source(
    dataset_id: int,
    source: DatabaseSourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加数据库类型数据源"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 确保数据源关联到正确的数据集
    source.dataset_id = dataset_id
    
    # 添加数据源
    dataset_service.add_database_source(db=db, source=source)
    
    # 返回更新后的数据集
    return dataset_service.get_dataset(db=db, dataset_id=dataset_id)

@router.post("/{dataset_id}/file-sources", response_model=FileSourceResponse)
async def add_file_source(
    dataset_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加文件类型数据源"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 添加文件数据源
    return await dataset_service.add_file_source(
        db=db,
        name=name,
        description=description,
        dataset_id=dataset_id,
        file=file,
        upload_dir=settings.UPLOAD_DIR
    )

@router.post("/{dataset_id}/url-sources", response_model=DatasetResponse)
def add_url_source(
    dataset_id: int,
    source: URLSourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加URL类型数据源"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 确保数据源关联到正确的数据集
    source.dataset_id = dataset_id
    
    # 添加数据源
    dataset_service.add_url_source(db=db, source=source)
    
    # 返回更新后的数据集
    return dataset_service.get_dataset(db=db, dataset_id=dataset_id)

@router.delete("/{dataset_id}/data-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_source(
    dataset_id: int,
    source_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除数据源"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 删除数据源
    result = dataset_service.delete_data_source(db=db, source_id=source_id)
    if not result:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    return None

@router.post("/{dataset_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def associate_note(
    dataset_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """关联笔记与数据集"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 关联笔记
    result = dataset_service.associate_note_with_dataset(db=db, note_id=note_id, dataset_id=dataset_id)
    if not result:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    return None

@router.delete("/{dataset_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def disassociate_note(
    dataset_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """解除笔记与数据集的关联"""
    # 检查数据集是否存在且属于当前用户
    dataset = dataset_service.get_dataset(db=db, dataset_id=dataset_id)
    if dataset is None or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 解除关联
    result = dataset_service.disassociate_note_from_dataset(db=db, note_id=note_id, dataset_id=dataset_id)
    if not result:
        raise HTTPException(status_code=404, detail="笔记不存在或未关联")
    
    return None

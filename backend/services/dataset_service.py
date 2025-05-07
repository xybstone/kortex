from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict, Any
from sqlalchemy import or_
from fastapi import UploadFile, HTTPException
import os
from pathlib import Path
import uuid

from models.domain.dataset import Dataset, DataSource, DatabaseSource, FileSource, URLSource
from models.domain.note import Note, note_dataset
from models.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetResponse, DatasetBrief,
    DatabaseSourceCreate, FileSourceCreate, URLSourceCreate,
    DatabaseSourceResponse, FileSourceResponse, URLSourceResponse
)

def create_dataset(db: Session, dataset: DatasetCreate) -> DatasetResponse:
    """创建新数据集"""
    db_dataset = Dataset(
        name=dataset.name,
        description=dataset.description,
        user_id=dataset.user_id
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)

    # 转换为响应模型
    return DatasetResponse(
        id=db_dataset.id,
        name=db_dataset.name,
        description=db_dataset.description,
        user_id=db_dataset.user_id,
        created_at=db_dataset.created_at,
        updated_at=db_dataset.updated_at,
        data_sources=[]
    )

def get_datasets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[DatasetResponse]:
    """获取数据集列表"""
    query = db.query(Dataset)

    # 如果提供了用户ID，只返回该用户的数据集
    if user_id:
        query = query.filter(Dataset.user_id == user_id)

    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        query = query.filter(
            or_(
                Dataset.name.ilike(f"%{search}%"),
                Dataset.description.ilike(f"%{search}%")
            )
        )

    # 获取分页结果
    datasets = query.order_by(Dataset.name).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            user_id=dataset.user_id,
            created_at=dataset.created_at,
            updated_at=dataset.updated_at,
            data_sources=_get_data_sources_responses(dataset.data_sources)
        )
        for dataset in datasets
    ]

def get_dataset(db: Session, dataset_id: int) -> Optional[DatasetResponse]:
    """获取单个数据集详情"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return None

    # 转换为响应模型
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        user_id=dataset.user_id,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        data_sources=_get_data_sources_responses(dataset.data_sources)
    )

def update_dataset(db: Session, dataset_id: int, dataset_update: DatasetUpdate) -> Optional[DatasetResponse]:
    """更新数据集"""
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        return None

    # 更新数据集基本信息
    update_data = dataset_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dataset, key, value)

    db.commit()
    db.refresh(db_dataset)

    # 转换为响应模型
    return DatasetResponse(
        id=db_dataset.id,
        name=db_dataset.name,
        description=db_dataset.description,
        user_id=db_dataset.user_id,
        created_at=db_dataset.created_at,
        updated_at=db_dataset.updated_at,
        data_sources=_get_data_sources_responses(db_dataset.data_sources)
    )

def delete_dataset(db: Session, dataset_id: int) -> bool:
    """删除数据集"""
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        return False

    db.delete(db_dataset)
    db.commit()
    return True

def add_database_source(db: Session, source: DatabaseSourceCreate) -> DatabaseSourceResponse:
    """添加数据库类型数据源"""
    # 检查数据集是否存在
    dataset = db.query(Dataset).filter(Dataset.id == source.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # 创建数据源
    db_source = DatabaseSource(
        name=source.name,
        description=source.description,
        dataset_id=source.dataset_id,
        connection_string=source.connection_string,
        database_type=source.database_type
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)

    # 转换为响应模型
    return DatabaseSourceResponse(
        id=db_source.id,
        name=db_source.name,
        description=db_source.description,
        type=db_source.type,
        dataset_id=db_source.dataset_id,
        processing_status=db_source.processing_status,
        last_processed_at=db_source.last_processed_at,
        processing_error=db_source.processing_error,
        created_at=db_source.created_at,
        updated_at=db_source.updated_at,
        connection_string=db_source.connection_string,
        database_type=db_source.database_type
    )

async def add_file_source(
    db: Session,
    name: str,
    description: Optional[str],
    dataset_id: int,
    file: UploadFile,
    upload_dir: Path
) -> FileSourceResponse:
    """添加文件类型数据源"""
    # 检查数据集是否存在
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # 保存上传的文件
    file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    file_path = upload_dir / f"{uuid.uuid4()}{file_extension}"
    
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 确定文件类型
    file_type = file_extension.lstrip(".") if file_extension else "unknown"

    # 创建数据源
    db_source = FileSource(
        name=name,
        description=description,
        dataset_id=dataset_id,
        file_path=str(file_path),
        file_type=file_type,
        file_size=file_size
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)

    # 转换为响应模型
    return FileSourceResponse(
        id=db_source.id,
        name=db_source.name,
        description=db_source.description,
        type=db_source.type,
        dataset_id=db_source.dataset_id,
        processing_status=db_source.processing_status,
        last_processed_at=db_source.last_processed_at,
        processing_error=db_source.processing_error,
        created_at=db_source.created_at,
        updated_at=db_source.updated_at,
        file_path=db_source.file_path,
        file_type=db_source.file_type,
        file_size=db_source.file_size
    )

def add_url_source(db: Session, source: URLSourceCreate) -> URLSourceResponse:
    """添加URL类型数据源"""
    # 检查数据集是否存在
    dataset = db.query(Dataset).filter(Dataset.id == source.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # 创建数据源
    db_source = URLSource(
        name=source.name,
        description=source.description,
        dataset_id=source.dataset_id,
        url=source.url,
        crawl_depth=source.crawl_depth or 1
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)

    # 转换为响应模型
    return URLSourceResponse(
        id=db_source.id,
        name=db_source.name,
        description=db_source.description,
        type=db_source.type,
        dataset_id=db_source.dataset_id,
        processing_status=db_source.processing_status,
        last_processed_at=db_source.last_processed_at,
        processing_error=db_source.processing_error,
        created_at=db_source.created_at,
        updated_at=db_source.updated_at,
        url=db_source.url,
        crawl_depth=db_source.crawl_depth
    )

def get_data_source(db: Session, source_id: int) -> Optional[Union[DatabaseSourceResponse, FileSourceResponse, URLSourceResponse]]:
    """获取数据源详情"""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        return None

    # 根据数据源类型返回不同的响应模型
    return _convert_data_source_to_response(source)

def delete_data_source(db: Session, source_id: int) -> bool:
    """删除数据源"""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        return False

    db.delete(source)
    db.commit()
    return True

def associate_note_with_dataset(db: Session, note_id: int, dataset_id: int) -> bool:
    """关联笔记与数据集"""
    note = db.query(Note).filter(Note.id == note_id).first()
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not note or not dataset:
        return False
    
    # 检查是否已关联
    if dataset in note.datasets:
        return True
    
    # 添加关联
    note.datasets.append(dataset)
    db.commit()
    return True

def disassociate_note_from_dataset(db: Session, note_id: int, dataset_id: int) -> bool:
    """解除笔记与数据集的关联"""
    note = db.query(Note).filter(Note.id == note_id).first()
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not note or not dataset:
        return False
    
    # 检查是否已关联
    if dataset not in note.datasets:
        return True
    
    # 移除关联
    note.datasets.remove(dataset)
    db.commit()
    return True

def _get_data_sources_responses(data_sources: List[DataSource]) -> List[Union[DatabaseSourceResponse, FileSourceResponse, URLSourceResponse]]:
    """将数据源列表转换为响应模型列表"""
    return [_convert_data_source_to_response(source) for source in data_sources]

def _convert_data_source_to_response(source: DataSource) -> Union[DatabaseSourceResponse, FileSourceResponse, URLSourceResponse]:
    """将数据源转换为对应的响应模型"""
    if source.type == "database":
        db_source = source
        return DatabaseSourceResponse(
            id=db_source.id,
            name=db_source.name,
            description=db_source.description,
            type=db_source.type,
            dataset_id=db_source.dataset_id,
            processing_status=db_source.processing_status,
            last_processed_at=db_source.last_processed_at,
            processing_error=db_source.processing_error,
            created_at=db_source.created_at,
            updated_at=db_source.updated_at,
            connection_string=db_source.connection_string,
            database_type=db_source.database_type
        )
    elif source.type == "file":
        file_source = source
        return FileSourceResponse(
            id=file_source.id,
            name=file_source.name,
            description=file_source.description,
            type=file_source.type,
            dataset_id=file_source.dataset_id,
            processing_status=file_source.processing_status,
            last_processed_at=file_source.last_processed_at,
            processing_error=file_source.processing_error,
            created_at=file_source.created_at,
            updated_at=file_source.updated_at,
            file_path=file_source.file_path,
            file_type=file_source.file_type,
            file_size=file_source.file_size
        )
    elif source.type == "url":
        url_source = source
        return URLSourceResponse(
            id=url_source.id,
            name=url_source.name,
            description=url_source.description,
            type=url_source.type,
            dataset_id=url_source.dataset_id,
            processing_status=url_source.processing_status,
            last_processed_at=url_source.last_processed_at,
            processing_error=url_source.processing_error,
            created_at=url_source.created_at,
            updated_at=url_source.updated_at,
            url=url_source.url,
            crawl_depth=url_source.crawl_depth
        )
    else:
        # 默认返回基本数据源响应
        return DataSourceResponse(
            id=source.id,
            name=source.name,
            description=source.description,
            type=source.type,
            dataset_id=source.dataset_id,
            processing_status=source.processing_status,
            last_processed_at=source.last_processed_at,
            processing_error=source.processing_error,
            created_at=source.created_at,
            updated_at=source.updated_at
        )

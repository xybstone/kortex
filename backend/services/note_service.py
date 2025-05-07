from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from models.domain.note import Note, note_dataset
from models.domain.dataset import Dataset
from models.schemas.note import NoteCreate, NoteUpdate, NoteResponse, DatabaseBrief
from models.schemas.dataset import DatasetBrief

def create_note(db: Session, note: NoteCreate) -> NoteResponse:
    """创建新笔记"""
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=note.user_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # 数据库关联功能已移除
    if note.database_ids:
        # 不再支持数据库关联
        pass

    # 如果提供了关联的数据集ID，创建关联关系
    if note.dataset_ids:
        for ds_id in note.dataset_ids:
            # 检查数据集是否存在
            db_dataset = db.query(Dataset).filter(Dataset.id == ds_id).first()
            if db_dataset:
                db_note.datasets.append(db_dataset)
        db.commit()
        db.refresh(db_note)

    # 转换为响应模型
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        user_id=db_note.user_id,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at,
        databases=None,  # 数据库关联功能已移除
        datasets=[DatasetBrief(id=ds.id, name=ds.name) for ds in db_note.datasets] if db_note.datasets else None
    )

def get_notes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[NoteResponse]:
    """获取笔记列表"""
    query = db.query(Note)

    # 如果提供了用户ID，只返回该用户的笔记
    if user_id:
        query = query.filter(Note.user_id == user_id)

    # 如果提供了搜索关键词，在标题和内容中搜索
    if search:
        query = query.filter(
            or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            )
        )

    # 获取分页结果
    notes = query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            created_at=note.created_at,
            updated_at=note.updated_at,
            databases=None,  # 数据库关联功能已移除
            datasets=None  # 添加数据集字段
        )
        for note in notes
    ]

def get_note(db: Session, note_id: int) -> Optional[NoteResponse]:
    """获取单个笔记详情"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        return None

    # 转换为响应模型
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        user_id=note.user_id,
        created_at=note.created_at,
        updated_at=note.updated_at,
        databases=None,  # 数据库关联功能已移除
        datasets=[DatasetBrief(id=ds.id, name=ds.name) for ds in note.datasets] if note.datasets else None
    )

def update_note(db: Session, note_id: int, note_update: NoteUpdate) -> NoteResponse:
    """更新笔记"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        return None

    # 更新笔记基本信息
    update_data = note_update.model_dump(exclude_unset=True, exclude={"database_ids", "dataset_ids"})
    for key, value in update_data.items():
        setattr(db_note, key, value)

    # 数据库关联功能已移除
    if note_update.database_ids is not None:
        # 不再支持数据库关联
        pass

    # 如果提供了数据集ID列表，更新关联关系
    if note_update.dataset_ids is not None:
        # 清除现有关联
        db_note.datasets = []

        # 创建新关联
        for ds_id in note_update.dataset_ids:
            db_dataset = db.query(Dataset).filter(Dataset.id == ds_id).first()
            if db_dataset:
                db_note.datasets.append(db_dataset)

    db.commit()
    db.refresh(db_note)

    # 转换为响应模型
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        user_id=db_note.user_id,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at,
        databases=None,  # 数据库关联功能已移除
        datasets=[DatasetBrief(id=ds.id, name=ds.name) for ds in db_note.datasets] if db_note.datasets else None
    )

def delete_note(db: Session, note_id: int) -> None:
    """删除笔记"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from models.domain.note import Note, note_database
from models.domain.database import Database
from models.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from models.schemas.database import DatabaseBrief

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

    # 如果提供了关联的数据库ID，创建关联关系
    if note.database_ids:
        for db_id in note.database_ids:
            # 检查数据库是否存在
            db_database = db.query(Database).filter(Database.id == db_id).first()
            if db_database:
                db_note.databases.append(db_database)
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
        databases=[DatabaseBrief(id=db.id, name=db.name) for db in db_note.databases] if db_note.databases else None
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
            databases=[DatabaseBrief(id=db.id, name=db.name) for db in note.databases] if note.databases else None
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
        databases=[DatabaseBrief(id=db.id, name=db.name) for db in note.databases] if note.databases else None
    )

def update_note(db: Session, note_id: int, note_update: NoteUpdate) -> NoteResponse:
    """更新笔记"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        return None

    # 更新笔记基本信息
    update_data = note_update.model_dump(exclude_unset=True, exclude={"database_ids"})
    for key, value in update_data.items():
        setattr(db_note, key, value)

    # 如果提供了数据库ID列表，更新关联关系
    if note_update.database_ids is not None:
        # 清除现有关联
        db_note.databases = []

        # 创建新关联
        for db_id in note_update.database_ids:
            db_database = db.query(Database).filter(Database.id == db_id).first()
            if db_database:
                db_note.databases.append(db_database)

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
        databases=[DatabaseBrief(id=db.id, name=db.name) for db in db_note.databases] if db_note.databases else None
    )

def delete_note(db: Session, note_id: int) -> None:
    """删除笔记"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()

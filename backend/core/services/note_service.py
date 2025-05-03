from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from backend.models.models import Note, NoteDatabase
from backend.models.schemas import NoteCreate, NoteUpdate

def create_note(db: Session, note: NoteCreate) -> Note:
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
            db_note_db = NoteDatabase(note_id=db_note.id, database_id=db_id)
            db.add(db_note_db)
        db.commit()
    
    return db_note

def get_notes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Note]:
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
    
    return query.offset(skip).limit(limit).all()

def get_note(db: Session, note_id: int) -> Optional[Note]:
    """获取单个笔记详情"""
    return db.query(Note).filter(Note.id == note_id).first()

def update_note(db: Session, note_id: int, note: NoteUpdate) -> Note:
    """更新笔记"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    
    # 更新笔记基本信息
    for key, value in note.dict(exclude_unset=True).items():
        if key != "database_ids":
            setattr(db_note, key, value)
    
    # 如果提供了数据库ID列表，更新关联关系
    if note.database_ids is not None:
        # 删除现有关联
        db.query(NoteDatabase).filter(NoteDatabase.note_id == note_id).delete()
        
        # 创建新关联
        for db_id in note.database_ids:
            db_note_db = NoteDatabase(note_id=note_id, database_id=db_id)
            db.add(db_note_db)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> None:
    """删除笔记"""
    # 删除笔记与数据库的关联
    db.query(NoteDatabase).filter(NoteDatabase.note_id == note_id).delete()
    
    # 删除笔记
    db.query(Note).filter(Note.id == note_id).delete()
    db.commit()

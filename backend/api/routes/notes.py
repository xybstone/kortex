from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.models.schemas import NoteCreate, NoteUpdate, NoteResponse
from backend.core.services import note_service

router = APIRouter()

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """创建新笔记"""
    return note_service.create_note(db=db, note=note)

@router.get("/", response_model=List[NoteResponse])
def get_notes(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取笔记列表"""
    return note_service.get_notes(db=db, skip=skip, limit=limit, search=search)

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """获取单个笔记详情"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """更新笔记"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note_service.update_note(db=db, note_id=note_id, note=note)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """删除笔记"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    note_service.delete_note(db=db, note_id=note_id)
    return {"detail": "笔记已删除"}

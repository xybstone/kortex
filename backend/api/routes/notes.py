from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas import NoteCreate, NoteUpdate, NoteResponse, UserResponse
from services import note_service

router = APIRouter()

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建新笔记"""
    # 确保笔记关联到当前用户
    note.user_id = current_user.id
    return note_service.create_note(db=db, note=note)

@router.get("/", response_model=List[NoteResponse])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户的笔记列表"""
    return note_service.get_notes(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        user_id=current_user.id
    )

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取单个笔记详情"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 检查笔记是否属于当前用户
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问此笔记")

    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新笔记"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 检查笔记是否属于当前用户
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限修改此笔记")

    return note_service.update_note(db=db, note_id=note_id, note=note)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除笔记"""
    db_note = note_service.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 检查笔记是否属于当前用户
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除此笔记")

    note_service.delete_note(db=db, note_id=note_id)
    return {"detail": "笔记已删除"}

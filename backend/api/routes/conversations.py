from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.models.schemas import (
    ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse
)
from backend.core.services import conversation_service

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    """创建新的对话"""
    return conversation_service.create_conversation(db=db, conversation=conversation)

@router.get("/note/{note_id}", response_model=List[ConversationResponse])
async def get_note_conversations(
    note_id: int,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取笔记的对话列表"""
    return conversation_service.get_conversations(
        db=db, 
        note_id=note_id,
        skip=skip, 
        limit=limit
    )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """获取单个对话详情"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")
    return db_conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """删除对话"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")
    conversation_service.delete_conversation(db=db, conversation_id=conversation_id)
    return {"detail": "对话已删除"}

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取对话的消息列表"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return conversation_service.get_messages(
        db=db, 
        conversation_id=conversation_id,
        skip=skip, 
        limit=limit
    )

@router.post("/{conversation_id}/messages", response_model=dict)
async def send_message(
    conversation_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """发送消息并获取AI响应"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    try:
        result = await conversation_service.send_message_and_get_response(
            db=db,
            conversation_id=conversation_id,
            user_message=message
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"发送消息失败: {str(e)}"
        )

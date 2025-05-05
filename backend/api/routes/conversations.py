from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas import ConversationCreate, ConversationResponse, MessageResponse, UserResponse
from core.services import conversation_service

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建新的对话"""
    # 确保对话关联到当前用户
    conversation.user_id = current_user.id
    return conversation_service.create_conversation(db=db, conversation=conversation)

@router.get("/note/{note_id}", response_model=List[ConversationResponse])
async def get_note_conversations(
    note_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取笔记的对话列表"""
    return conversation_service.get_conversations(
        db=db,
        note_id=note_id,
        skip=skip,
        limit=limit,
        user_id=current_user.id
    )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取单个对话详情"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 检查对话是否属于当前用户
    if db_conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问此对话")

    return db_conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除对话"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 检查对话是否属于当前用户
    if db_conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除此对话")

    conversation_service.delete_conversation(db=db, conversation_id=conversation_id)
    return {"detail": "对话已删除"}

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取对话的消息列表"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 检查对话是否属于当前用户
    if db_conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问此对话")

    return conversation_service.get_messages(
        db=db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit
    )

@router.post("/{conversation_id}/messages", response_model=dict)
async def send_message(
    conversation_id: int,
    message_data: dict,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """发送消息并获取AI响应"""
    db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 检查对话是否属于当前用户
    if db_conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问此对话")

    # 从请求体中获取消息内容
    user_message = message_data.get("message", "")
    if not user_message.strip():
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    try:
        result = await conversation_service.send_message_and_get_response(
            db=db,
            conversation_id=conversation_id,
            user_message=user_message
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"发送消息失败: {str(e)}"
        )

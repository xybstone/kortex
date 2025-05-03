from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import or_

from backend.models.models import NoteConversation, ConversationMessage, LLMRole
from backend.models.schemas import ConversationCreate, MessageCreate
from backend.core.services import llm_service

def create_conversation(db: Session, conversation: ConversationCreate) -> NoteConversation:
    """创建新的对话"""
    db_conversation = NoteConversation(
        note_id=conversation.note_id,
        role_id=conversation.role_id,
        user_id=conversation.user_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    # 添加系统消息
    role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
    if role and role.system_prompt:
        system_message = ConversationMessage(
            conversation_id=db_conversation.id,
            content=role.system_prompt,
            role="system"
        )
        db.add(system_message)
        db.commit()

    return db_conversation

def get_conversations(
    db: Session,
    note_id: int,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[NoteConversation]:
    """获取笔记的对话列表"""
    query = db.query(NoteConversation).filter(
        NoteConversation.note_id == note_id
    )

    # 如果指定了用户ID，只返回该用户的对话
    if user_id:
        query = query.filter(NoteConversation.user_id == user_id)

    return query.offset(skip).limit(limit).all()

def get_conversation(db: Session, conversation_id: int) -> Optional[NoteConversation]:
    """获取单个对话详情"""
    return db.query(NoteConversation).filter(
        NoteConversation.id == conversation_id
    ).first()

def delete_conversation(db: Session, conversation_id: int) -> None:
    """删除对话"""
    # 删除所有消息
    db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).delete()

    # 删除对话
    db.query(NoteConversation).filter(
        NoteConversation.id == conversation_id
    ).delete()

    db.commit()

def add_message(db: Session, message: MessageCreate) -> ConversationMessage:
    """添加新消息"""
    db_message = ConversationMessage(
        conversation_id=message.conversation_id,
        content=message.content,
        role=message.role
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(
    db: Session,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ConversationMessage]:
    """获取对话的消息列表"""
    return db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.created_at).offset(skip).limit(limit).all()

async def send_message_and_get_response(
    db: Session,
    conversation_id: int,
    user_message: str
) -> Dict[str, Any]:
    """发送用户消息并获取AI响应"""
    # 获取对话
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise ValueError(f"对话 {conversation_id} 不存在")

    # 获取角色
    role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
    if not role:
        raise ValueError(f"角色 {conversation.role_id} 不存在")

    # 添加用户消息
    user_db_message = add_message(db, MessageCreate(
        conversation_id=conversation_id,
        content=user_message,
        role="user"
    ))

    # 获取对话历史
    messages = get_messages(db, conversation_id)

    # 准备发送给LLM的消息
    llm_messages = []
    for msg in messages:
        llm_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # 调用LLM服务获取响应
    response = await llm_service.chat_with_llm(
        db=db,
        model_id=role.model_id,
        messages=llm_messages
    )

    # 添加AI响应消息
    assistant_db_message = add_message(db, MessageCreate(
        conversation_id=conversation_id,
        content=response["result"],
        role="assistant"
    ))

    return {
        "user_message": user_db_message,
        "assistant_message": assistant_db_message
    }

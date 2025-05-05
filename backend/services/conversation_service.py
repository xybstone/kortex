from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from models.domain.llm import Conversation, Message, LLMRole
from models.domain.note import Note
from models.schemas.conversation import (
    ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse
)
# 避免循环导入
import services.llm_service as llm_service

def create_conversation(db: Session, conversation: ConversationCreate) -> ConversationResponse:
    """创建新的对话"""
    # 检查笔记是否存在
    note = db.query(Note).filter(Note.id == conversation.note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 检查角色是否存在
    role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 创建对话
    db_conversation = Conversation(
        note_id=conversation.note_id,
        role_id=conversation.role_id,
        user_id=conversation.user_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    # 创建初始消息（系统消息）
    system_message = Message(
        content=role.system_prompt,
        role="system",
        conversation_id=db_conversation.id
    )
    db.add(system_message)

    # 创建欢迎消息（助手消息）
    welcome_message = Message(
        content="你好，我是AI助手，有什么可以帮助你的？",
        role="assistant",
        conversation_id=db_conversation.id
    )
    db.add(welcome_message)

    db.commit()

    # 转换为响应模型
    return ConversationResponse(
        id=db_conversation.id,
        note_id=db_conversation.note_id,
        role_id=db_conversation.role_id,
        user_id=db_conversation.user_id,
        created_at=db_conversation.created_at,
        updated_at=db_conversation.updated_at,
        messages=[
            MessageResponse(
                id=welcome_message.id,
                content=welcome_message.content,
                role=welcome_message.role,
                created_at=welcome_message.created_at
            )
        ],
        role=role
    )

def get_conversations(
    db: Session,
    note_id: int,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[ConversationResponse]:
    """获取笔记的对话列表"""
    query = db.query(Conversation).filter(Conversation.note_id == note_id)

    # 如果提供了用户ID，只返回该用户的对话
    if user_id:
        query = query.filter(Conversation.user_id == user_id)

    # 获取分页结果
    conversations = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

    # 转换为响应模型
    result = []
    for conversation in conversations:
        # 获取角色信息
        role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
        if not role:
            continue

        # 获取最新的消息（不包括系统消息）
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.role != "system"
        ).order_by(Message.created_at.desc()).limit(5).all()

        result.append(
            ConversationResponse(
                id=conversation.id,
                note_id=conversation.note_id,
                role_id=conversation.role_id,
                user_id=conversation.user_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                messages=[
                    MessageResponse(
                        id=message.id,
                        content=message.content,
                        role=message.role,
                        created_at=message.created_at
                    )
                    for message in reversed(messages)  # 按时间正序排列
                ],
                role=role
            )
        )

    return result

def get_conversation(db: Session, conversation_id: int) -> Optional[ConversationResponse]:
    """获取单个对话详情"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        return None

    # 获取角色信息
    role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
    if not role:
        return None

    # 获取消息（不包括系统消息）
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.role != "system"
    ).order_by(Message.created_at).all()

    # 转换为响应模型
    return ConversationResponse(
        id=conversation.id,
        note_id=conversation.note_id,
        role_id=conversation.role_id,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=message.id,
                content=message.content,
                role=message.role,
                created_at=message.created_at
            )
            for message in messages
        ],
        role=role
    )

def delete_conversation(db: Session, conversation_id: int) -> None:
    """删除对话"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        db.delete(conversation)
        db.commit()

def get_messages(
    db: Session,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[MessageResponse]:
    """获取对话的消息列表"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        MessageResponse(
            id=message.id,
            content=message.content,
            role=message.role,
            created_at=message.created_at
        )
        for message in messages
    ]

def create_message(db: Session, message: MessageCreate) -> MessageResponse:
    """创建新消息"""
    db_message = Message(
        content=message.content,
        role=message.role,
        conversation_id=message.conversation_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # 更新对话的更新时间
    conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
    if conversation:
        conversation.updated_at = db_message.created_at
        db.commit()

    # 转换为响应模型
    return MessageResponse(
        id=db_message.id,
        content=db_message.content,
        role=db_message.role,
        created_at=db_message.created_at
    )

async def send_message_and_get_response(
    db: Session,
    conversation_id: int,
    user_message: str
) -> Dict[str, Any]:
    """发送用户消息并获取AI响应"""
    # 获取对话
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail=f"对话 {conversation_id} 不存在")

    # 获取角色
    role = db.query(LLMRole).filter(LLMRole.id == conversation.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"角色 {conversation.role_id} 不存在")

    # 添加用户消息
    user_db_message = Message(
        content=user_message,
        role="user",
        conversation_id=conversation_id
    )
    db.add(user_db_message)
    db.commit()
    db.refresh(user_db_message)

    # 获取对话历史（包括系统消息）
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    # 准备发送给LLM的消息
    llm_messages = []
    for msg in messages:
        llm_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    try:
        # 调用LLM服务获取响应
        response = await llm_service.chat_with_llm(
            db=db,
            model_id=role.model_id,
            messages=llm_messages
        )

        # 添加AI响应消息
        assistant_db_message = Message(
            content=response["result"],
            role="assistant",
            conversation_id=conversation_id
        )
        db.add(assistant_db_message)
        db.commit()
        db.refresh(assistant_db_message)

        # 更新对话的更新时间
        conversation.updated_at = assistant_db_message.created_at
        db.commit()

        # 返回用户消息和AI响应
        return {
            "user_message": MessageResponse(
                id=user_db_message.id,
                content=user_db_message.content,
                role=user_db_message.role,
                created_at=user_db_message.created_at
            ),
            "assistant_message": MessageResponse(
                id=assistant_db_message.id,
                content=assistant_db_message.content,
                role=assistant_db_message.role,
                created_at=assistant_db_message.created_at
            )
        }
    except Exception as e:
        # 如果调用LLM服务失败，返回一个默认响应
        error_message = f"抱歉，我无法处理您的请求。错误: {str(e)}"
        assistant_db_message = Message(
            content=error_message,
            role="assistant",
            conversation_id=conversation_id
        )
        db.add(assistant_db_message)
        db.commit()
        db.refresh(assistant_db_message)

        # 更新对话的更新时间
        conversation.updated_at = assistant_db_message.created_at
        db.commit()

        # 返回用户消息和错误响应
        return {
            "user_message": MessageResponse(
                id=user_db_message.id,
                content=user_db_message.content,
                role=user_db_message.role,
                created_at=user_db_message.created_at
            ),
            "assistant_message": MessageResponse(
                id=assistant_db_message.id,
                content=assistant_db_message.content,
                role=assistant_db_message.role,
                created_at=assistant_db_message.created_at
            )
        }

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.schemas.llm import LLMRoleResponse

# 对话消息相关模式
class MessageBase(BaseModel):
    content: str
    role: str  # user, assistant, system

class MessageCreate(MessageBase):
    conversation_id: int

class MessageResponse(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 对话相关模式
class ConversationBase(BaseModel):
    note_id: int
    role_id: int

class ConversationCreate(ConversationBase):
    user_id: Optional[int] = None

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []
    role: LLMRoleResponse

    class Config:
        from_attributes = True

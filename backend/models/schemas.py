from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 用户相关模式
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# 认证相关模式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# 笔记相关模式
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    user_id: int
    database_ids: Optional[List[int]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    database_ids: Optional[List[int]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    databases: Optional[List["DatabaseBrief"]] = None
    conversations: Optional[List["ConversationResponse"]] = None

    class Config:
        from_attributes = True

# 数据库相关模式
class DatabaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatabaseCreate(DatabaseBase):
    user_id: int

class DatabaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DatabaseBrief(DatabaseBase):
    id: int

    class Config:
        from_attributes = True

class DatabaseResponse(DatabaseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tables: Optional[List["TableBrief"]] = None

    class Config:
        from_attributes = True

# 表格相关模式
class TableBase(BaseModel):
    name: str

class TableBrief(TableBase):
    id: int

    class Config:
        from_attributes = True

class TableResponse(TableBase):
    id: int
    database_id: int
    columns: List["ColumnResponse"]

    class Config:
        from_attributes = True

# 列相关模式
class ColumnBase(BaseModel):
    name: str
    type: str

class ColumnResponse(ColumnBase):
    id: int

    class Config:
        from_attributes = True

# LLM相关模式
class LLMRequest(BaseModel):
    content: str
    options: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    result: Any
    type: str

# LLM供应商相关模式
class LLMProviderBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_public: bool = True

class LLMProviderCreate(LLMProviderBase):
    user_id: Optional[int] = None

class LLMProviderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_public: Optional[bool] = None

class LLMProviderResponse(LLMProviderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# LLM模型相关模式
class LLMModelBase(BaseModel):
    name: str
    provider_id: int
    api_key: Optional[str] = None
    is_active: bool = True
    is_public: bool = False
    max_tokens: int = 4096
    temperature: float = 0.7

class LLMModelCreate(LLMModelBase):
    user_id: Optional[int] = None

class LLMModelUpdate(BaseModel):
    name: Optional[str] = None
    provider_id: Optional[int] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class LLMModelResponse(LLMModelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    provider: LLMProviderResponse

    class Config:
        from_attributes = True

# LLM角色相关模式
class LLMRoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    model_id: int
    is_default: bool = False
    is_public: bool = False

class LLMRoleCreate(LLMRoleBase):
    user_id: Optional[int] = None

class LLMRoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[int] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None

class LLMRoleResponse(LLMRoleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model: LLMModelResponse

    class Config:
        from_attributes = True

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

# 更新引用
NoteResponse.model_rebuild()
DatabaseResponse.model_rebuild()
TableResponse.model_rebuild()
ConversationResponse.model_rebuild()
LLMModelResponse.model_rebuild()
LLMRoleResponse.model_rebuild()

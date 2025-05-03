from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 用户相关模式
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
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

# 更新引用
NoteResponse.update_forward_refs()
DatabaseResponse.update_forward_refs()
TableResponse.update_forward_refs()

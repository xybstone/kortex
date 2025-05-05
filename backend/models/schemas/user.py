from pydantic import BaseModel, EmailStr, Field
from typing import Optional
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

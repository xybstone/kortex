from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from core.dependencies import get_db, get_current_user
    from models.schemas import *
    from core.services import *
else:
    try:
        # 尝试使用相对导入
        from core.dependencies import get_db, get_current_user
        from models.schemas import *
        from core.services import *
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.core.dependencies import get_db, get_current_user
        from backend.models.schemas import *
        from backend.core.services import *

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    # 简单模拟登录，返回一个固定的token
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE4MzgwODAwfQ.8H7MnKTCZl4L6ICv8cj8O9K9l1fU1TEyQ7QgQxpLNSo",
        "token_type": "bearer"
    }

@router.post("/register")
async def register(email: str, password: str, full_name: str = None):
    """用户注册"""
    # 简单模拟注册，返回成功消息
    return {"message": "注册成功"}

@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    # 简单模拟返回用户信息
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "测试用户",
        "is_active": True,
        "is_admin": False
    }

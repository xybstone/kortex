from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from core.dependencies import get_db
    from models.schemas import UserCreate
    from core.services.auth_service import create_user
else:
    try:
        # 尝试使用相对导入
        from core.dependencies import get_db
        from models.schemas import UserCreate
        from core.services.auth_service import create_user
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.core.dependencies import get_db
        from backend.models.schemas import UserCreate
        from backend.core.services.auth_service import create_user

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
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 使用导入的create_user函数创建用户
        create_user(db, user)
        return {"message": "注册成功"}
    except HTTPException as e:
        # 如果用户已存在，返回错误
        raise e
    except Exception as e:
        # 处理其他错误
        print(f"注册用户时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

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

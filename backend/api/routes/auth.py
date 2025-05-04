from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session
import os

# 导入依赖项
from api.dependencies import get_db, get_current_user
from core.security import verify_password, get_password_hash, create_access_token
from models.db_models import User
from models.schemas import Token, UserCreate, UserResponse, UserBase

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查邮箱是否已被注册
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_admin=False
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "is_active": db_user.is_active,
        "is_admin": db_user.is_admin,
        "created_at": db_user.created_at
    }

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录获取访问令牌"""
    # 查询用户
    user = db.query(User).filter(User.email == form_data.username).first()

    # 验证用户和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at
    }

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

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    db_user = auth_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    return auth_service.create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录获取访问令牌"""
    user = auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user

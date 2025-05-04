# 路由模块初始化文件
from fastapi import APIRouter

from api.routes import auth

api_router = APIRouter()

# 添加认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

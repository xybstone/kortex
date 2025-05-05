from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.router import api_router
from core.config import settings
from database.session import engine
from database.base import Base

# 初始化数据库表
# 注意：在生产环境中，应该使用Alembic进行数据库迁移
# 这里为了简单起见，直接创建表
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    # 使用create_all时添加checkfirst=True参数，避免重复创建表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("已初始化数据库表")
    yield
    # 关闭时执行
    print("应用关闭")

# 创建FastAPI应用
app = FastAPI(
    title="Kortex API",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 根路由
@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查端点，用于Docker容器监控"""
    return {"status": "healthy"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

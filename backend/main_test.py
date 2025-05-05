from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from database.session import engine
from models.domain import BaseModel
from api.router import api_router

# 创建FastAPI应用
app = FastAPI(
    title="Kortex API Test",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# 初始化数据库表
# 注意：在生产环境中，应该使用Alembic进行数据库迁移
# 这里为了简单起见，直接创建表
# 不使用事件，直接创建表
BaseModel.metadata.create_all(bind=engine, checkfirst=True)
print("已初始化数据库表")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_test:app", host="0.0.0.0", port=8003, reload=True)

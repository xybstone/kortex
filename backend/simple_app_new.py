from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from contextlib import asynccontextmanager

# 导入路由模块
from api.routes import api_router

# 导入数据库初始化
from database.init_db import init_db

app = FastAPI(
    title="Kortex API",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # 支持本地和Docker环境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

@app.get("/api/health")
async def health_check():
    """健康检查端点，用于Docker容器监控"""
    return {"status": "healthy"}

# 使用lifespan上下文管理器

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    init_db()
    yield
    # 关闭时执行
    pass

# 重新创建应用，使用lifespan
app = FastAPI(
    title="Kortex API",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # 支持本地和Docker环境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")

# 主函数
if __name__ == "__main__":
    # 获取端口
    port = int(os.environ.get("PORT", 8000))

    # 启动服务器
    uvicorn.run(
        "simple_app_new:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

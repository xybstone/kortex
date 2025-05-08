from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from api.router import api_router
from core.config import settings
from database.session import engine
from database.base import Base
from core.dependencies import get_db
from core.processing.task_queue import task_queue
from core.processing.scheduler import task_scheduler
from core.nlp import llm_manager, init_llm_manager

# 初始化数据库表
# 注意：在生产环境中，应该使用Alembic进行数据库迁移
# 这里为了简单起见，直接创建表
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    # 使用create_all时添加checkfirst=True参数，避免重复创建表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("已初始化数据库表")

    # 初始化LLM管理器
    llm_config = {
        "openai": {
            "api_key": settings.LLM_API_KEY,
            "models": [
                {
                    "name": "gpt-3.5-turbo",
                    "temperature": 0.0,
                    "max_tokens": 1000,
                    "is_default": True
                },
                {
                    "name": "gpt-4",
                    "temperature": 0.0,
                    "max_tokens": 1000
                }
            ]
        },
        "deepseek": {
            "api_key": settings.DEEPSEEK_API_KEY,
            "models": [
                {
                    "name": "deepseek-chat",
                    "temperature": 0.0,
                    "max_tokens": 1000
                }
            ]
        }
    }
    init_llm_manager(llm_config)
    print("已初始化LLM管理器")

    # 启动任务队列
    task_queue_task = asyncio.create_task(task_queue.start(get_db))
    print("已启动任务队列")

    # 启动任务调度器
    scheduler_task = asyncio.create_task(task_scheduler.start(get_db))
    print("已启动任务调度器")

    yield

    # 关闭时执行
    # 停止任务队列
    task_queue.running = False
    await task_queue_task
    print("已停止任务队列")

    # 停止任务调度器
    await task_scheduler.stop()
    print("已停止任务调度器")

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

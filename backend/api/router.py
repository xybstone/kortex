from fastapi import APIRouter

from api.routes import auth, notes, datasets, llm, llm_config, conversations, processing, nlp
from api.routes import task_dependency, task_history
from api.endpoints import pdf

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(notes.router, prefix="/notes", tags=["笔记"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["数据集"])
api_router.include_router(llm.router, prefix="/llm", tags=["大模型"])
api_router.include_router(llm_config.router, prefix="/llm-config", tags=["大模型配置"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["对话"])
api_router.include_router(processing.router, prefix="/processing", tags=["数据处理"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["自然语言处理"])
api_router.include_router(task_dependency.router, prefix="/task-dependencies", tags=["任务依赖"])
api_router.include_router(task_history.router, prefix="/task-history", tags=["任务历史"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["PDF处理"])

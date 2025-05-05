from fastapi import APIRouter

from api.routes import auth, notes, databases, llm, llm_config, conversations

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(notes.router, prefix="/notes", tags=["笔记"])
api_router.include_router(databases.router, prefix="/databases", tags=["数据库"])
api_router.include_router(llm.router, prefix="/llm", tags=["大模型"])
api_router.include_router(llm_config.router, prefix="/llm-config", tags=["大模型配置"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["对话"])

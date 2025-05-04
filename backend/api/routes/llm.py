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

# Docker环境下的简化路由
if IS_DOCKER:
    @router.post("/chat", response_model=Dict[str, Any])
    async def chat(message: str, role_id: int = None, conversation_id: int = None):
        """与大模型聊天"""
        # 模拟大模型响应
        response = {
            "content": f"这是对\"{message}\"的回复。在实际应用中，这里会调用大模型API获取响应。",
            "role": "assistant",
            "model": "gpt-3.5-turbo",
            "conversation_id": conversation_id or 0,
            "created_at": "2023-05-12T10:00:00Z"
        }

        return response

    @router.get("/status", response_model=Dict[str, Any])
    async def get_status():
        """获取大模型状态"""
        return {
            "status": "可用",
            "models": [
                {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
                {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
                {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True}
            ]
        }

# 非Docker环境下的完整路由
else:
    @router.post("/analyze", response_model=LLMResponse)
    async def analyze_text(request: LLMRequest, db: Session = Depends(get_db)):
        """使用大模型分析文本"""
        return await llm_service.analyze_text(db=db, request=request)

    @router.post("/generate", response_model=LLMResponse)
    async def generate_text(request: LLMRequest, db: Session = Depends(get_db)):
        """使用大模型生成文本"""
        return await llm_service.generate_text(db=db, request=request)

    @router.post("/summarize", response_model=LLMResponse)
    async def summarize_text(request: LLMRequest, db: Session = Depends(get_db)):
        """使用大模型生成摘要"""
        return await llm_service.summarize_text(db=db, request=request)

    @router.post("/extract-keywords", response_model=LLMResponse)
    async def extract_keywords(request: LLMRequest, db: Session = Depends(get_db)):
        """使用大模型提取关键词"""
        return await llm_service.extract_keywords(db=db, request=request)

    @router.post("/analyze-database", response_model=LLMResponse)
    async def analyze_database(
        database_id: int,
        prompt: str,
        db: Session = Depends(get_db)
    ):
        """使用大模型分析数据库内容"""
        return await llm_service.analyze_database(
            db=db,
            database_id=database_id,
            prompt=prompt
        )

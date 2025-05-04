from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from core.dependencies import get_db
    from models.schemas import LLMRequest, LLMResponse
    from core.services.llm_service import llm_service
else:
    try:
        # 尝试使用相对导入
        from core.dependencies import get_db
        from models.schemas import LLMRequest, LLMResponse
        from core.services.llm_service import llm_service
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.core.dependencies import get_db
        from backend.models.schemas import LLMRequest, LLMResponse
        from backend.core.services.llm_service import llm_service

router = APIRouter()

# 统一的路由，不再区分Docker和非Docker环境
@router.post("/analyze", response_model=LLMResponse)
async def analyze_text(request: LLMRequest, db: Session = Depends(get_db)):
    """使用大模型分析文本"""
    try:
        return await llm_service.analyze_text(db=db, request=request)
    except Exception as e:
        # 记录错误
        print(f"分析文本时出错: {str(e)}")
        # 返回友好的错误信息
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.post("/generate", response_model=LLMResponse)
async def generate_text(request: LLMRequest, db: Session = Depends(get_db)):
    """使用大模型生成文本"""
    try:
        return await llm_service.generate_text(db=db, request=request)
    except Exception as e:
        print(f"生成文本时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.post("/summarize", response_model=LLMResponse)
async def summarize_text(request: LLMRequest, db: Session = Depends(get_db)):
    """使用大模型生成摘要"""
    try:
        return await llm_service.summarize_text(db=db, request=request)
    except Exception as e:
        print(f"生成摘要时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.post("/extract-keywords", response_model=LLMResponse)
async def extract_keywords(request: LLMRequest, db: Session = Depends(get_db)):
    """使用大模型提取关键词"""
    try:
        return await llm_service.extract_keywords(db=db, request=request)
    except Exception as e:
        print(f"提取关键词时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

class DatabaseAnalysisRequest(BaseModel):
    database_id: int
    model_id: Optional[int] = None
    prompt: str

@router.post("/analyze-database", response_model=LLMResponse)
async def analyze_database(
    request: DatabaseAnalysisRequest,
    db: Session = Depends(get_db)
):
    """使用大模型分析数据库内容"""
    try:
        return await llm_service.analyze_database(
            db=db,
            database_id=request.database_id,
            prompt=request.prompt,
            model_id=request.model_id
        )
    except Exception as e:
        print(f"分析数据库时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """获取大模型状态"""
    return {
        "status": "可用"
    }

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_models(db: Session = Depends(get_db)):
    """获取所有可用的大模型列表"""
    try:
        # 从数据库获取模型列表
        from backend.core.services.llm_config_service import get_models
        models = get_models(db=db)

        # 转换为前端需要的格式
        result = []
        for model in models:
            provider_name = model.provider.name if model.provider else "未知"
            result.append({
                "id": model.id,
                "name": model.name,
                "provider": provider_name,
                "is_active": model.is_active
            })

        # 如果没有模型，返回默认模型列表
        if not result:
            result = [
                {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
                {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
                {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
                {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
            ]

        return result
    except Exception as e:
        # 如果出错，返回默认模型列表
        print(f"获取模型列表失败: {e}")
        return [
            {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
            {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
            {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
            {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
        ]

class ChatRequest(BaseModel):
    message: str
    role_id: int = None
    conversation_id: int = None

@router.post("/chat", response_model=Dict[str, Any])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """与大模型聊天"""
    # 如果没有实际的大模型API，返回模拟响应
    # 注意：这里的db参数在实际应用中会用于获取模型和角色信息
    _ = db  # 避免未使用警告

    response = {
        "result": f"这是对\"{request.message}\"的回复。在实际应用中，这里会调用大模型API获取响应。",
        "type": "chat",
        "model": "gpt-3.5-turbo",
        "conversation_id": request.conversation_id or 0,
        "created_at": "2023-05-12T10:00:00Z"
    }

    return response

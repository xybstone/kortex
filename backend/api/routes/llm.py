from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_db
from models.schemas import LLMRequest, LLMResponse
from core.services import llm_service

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
        # 使用llm_service获取模型列表
        return await llm_service.get_available_models(db=db)
    except Exception as e:
        # 如果出错，返回默认模型列表
        print(f"获取模型列表失败: {e}")

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

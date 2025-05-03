from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.models.schemas import LLMRequest, LLMResponse
from backend.core.services import llm_service

router = APIRouter()

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

"""
自然语言处理API路由
提供自然语言指令解析和任务创建功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas import UserResponse
from core.nlp import task_creator
from services import processing_service

router = APIRouter()


class NLProcessingRequest(BaseModel):
    """自然语言处理请求"""
    instruction: str
    data_source_id: int


class NLProcessingResponse(BaseModel):
    """自然语言处理响应"""
    success: bool
    task_id: Optional[int] = None
    task_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    error: Optional[str] = None


@router.post("/process", response_model=NLProcessingResponse)
async def process_nl_instruction(
    request: NLProcessingRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    处理自然语言指令
    根据自然语言指令创建处理任务
    """
    try:
        # 调用任务创建器创建任务
        result = await task_creator.create_task_from_instruction(
            instruction=request.instruction,
            data_source_id=request.data_source_id,
            user_id=current_user.id,
            db=db
        )
        
        if not result.get("success", False):
            # 如果创建失败，返回错误信息
            return NLProcessingResponse(
                success=False,
                error=result.get("error", "创建任务失败")
            )
            
        # 创建成功，返回任务信息
        return NLProcessingResponse(
            success=True,
            task_id=result.get("task_id"),
            task_type=result.get("task_type"),
            parameters=result.get("parameters"),
            confidence=result.get("confidence"),
            reasoning=result.get("reasoning")
        )
        
    except Exception as e:
        # 记录错误
        print(f"处理自然语言指令时出错: {str(e)}")
        # 返回友好的错误信息
        return NLProcessingResponse(
            success=False,
            error=f"处理指令时出错: {str(e)}"
        )


class NLAnalysisRequest(BaseModel):
    """自然语言分析请求"""
    instruction: str


class NLAnalysisResponse(BaseModel):
    """自然语言分析响应"""
    task_type: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str


@router.post("/analyze", response_model=NLAnalysisResponse)
async def analyze_nl_instruction(
    request: NLAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    分析自然语言指令
    解析指令但不创建任务
    """
    try:
        # 调用指令解析器解析指令
        if not task_creator.is_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="自然语言处理功能不可用，请检查LLM配置"
            )
            
        parse_result = await task_creator.instruction_parser.parse_instruction(request.instruction)
        
        if not parse_result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parse_result.get("error", "解析指令失败")
            )
            
        # 返回解析结果
        return NLAnalysisResponse(
            task_type=parse_result.get("task_type", "unknown"),
            parameters=parse_result.get("parameters", {}),
            confidence=parse_result.get("confidence", 0.0),
            reasoning=parse_result.get("reasoning", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 记录错误
        print(f"分析自然语言指令时出错: {str(e)}")
        # 返回友好的错误信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析指令时出错: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.models.schemas import (
    LLMProviderCreate, LLMProviderUpdate, LLMProviderResponse,
    LLMModelCreate, LLMModelUpdate, LLMModelResponse,
    LLMRoleCreate, LLMRoleUpdate, LLMRoleResponse
)
from backend.core.services import llm_config_service

router = APIRouter()

# LLM供应商路由
@router.post("/providers", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: LLMProviderCreate, db: Session = Depends(get_db)):
    """创建新的LLM供应商"""
    return llm_config_service.create_provider(db=db, provider=provider)

@router.get("/providers", response_model=List[LLMProviderResponse])
def get_providers(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取LLM供应商列表"""
    return llm_config_service.get_providers(db=db, skip=skip, limit=limit, search=search)

@router.get("/providers/{provider_id}", response_model=LLMProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """获取单个LLM供应商详情"""
    db_provider = llm_config_service.get_provider(db=db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return db_provider

@router.put("/providers/{provider_id}", response_model=LLMProviderResponse)
def update_provider(provider_id: int, provider: LLMProviderUpdate, db: Session = Depends(get_db)):
    """更新LLM供应商"""
    db_provider = llm_config_service.get_provider(db=db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return llm_config_service.update_provider(db=db, provider_id=provider_id, provider=provider)

@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """删除LLM供应商"""
    db_provider = llm_config_service.get_provider(db=db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    llm_config_service.delete_provider(db=db, provider_id=provider_id)
    return {"detail": "供应商已删除"}

# LLM模型路由
@router.post("/models", response_model=LLMModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(model: LLMModelCreate, db: Session = Depends(get_db)):
    """创建新的LLM模型"""
    return llm_config_service.create_model(db=db, model=model)

@router.get("/models", response_model=List[LLMModelResponse])
def get_models(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    provider_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取LLM模型列表"""
    return llm_config_service.get_models(
        db=db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        provider_id=provider_id
    )

@router.get("/models/{model_id}", response_model=LLMModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """获取单个LLM模型详情"""
    db_model = llm_config_service.get_model(db=db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="模型不存在")
    return db_model

@router.put("/models/{model_id}", response_model=LLMModelResponse)
def update_model(model_id: int, model: LLMModelUpdate, db: Session = Depends(get_db)):
    """更新LLM模型"""
    db_model = llm_config_service.get_model(db=db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="模型不存在")
    return llm_config_service.update_model(db=db, model_id=model_id, model=model)

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """删除LLM模型"""
    db_model = llm_config_service.get_model(db=db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="模型不存在")
    llm_config_service.delete_model(db=db, model_id=model_id)
    return {"detail": "模型已删除"}

# LLM角色路由
@router.post("/roles", response_model=LLMRoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: LLMRoleCreate, db: Session = Depends(get_db)):
    """创建新的LLM角色"""
    return llm_config_service.create_role(db=db, role=role)

@router.get("/roles", response_model=List[LLMRoleResponse])
def get_roles(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    model_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取LLM角色列表"""
    return llm_config_service.get_roles(
        db=db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        model_id=model_id
    )

@router.get("/roles/{role_id}", response_model=LLMRoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取单个LLM角色详情"""
    db_role = llm_config_service.get_role(db=db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return db_role

@router.put("/roles/{role_id}", response_model=LLMRoleResponse)
def update_role(role_id: int, role: LLMRoleUpdate, db: Session = Depends(get_db)):
    """更新LLM角色"""
    db_role = llm_config_service.get_role(db=db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return llm_config_service.update_role(db=db, role_id=role_id, role=role)

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除LLM角色"""
    db_role = llm_config_service.get_role(db=db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    llm_config_service.delete_role(db=db, role_id=role_id)
    return {"detail": "角色已删除"}

@router.get("/models/{model_id}/default-role", response_model=LLMRoleResponse)
def get_default_role(model_id: int, db: Session = Depends(get_db)):
    """获取模型的默认角色"""
    db_role = llm_config_service.get_default_role(db=db, model_id=model_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="该模型没有默认角色")
    return db_role

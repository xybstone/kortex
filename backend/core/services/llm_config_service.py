from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import or_

import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from models.models import LLMProvider, LLMModel, LLMRole
    from models.schemas import (
        LLMProviderCreate, LLMProviderUpdate,
        LLMModelCreate, LLMModelUpdate,
        LLMRoleCreate, LLMRoleUpdate
    )
else:
    try:
        # 尝试使用相对导入
        from models.models import LLMProvider, LLMModel, LLMRole
        from models.schemas import (
            LLMProviderCreate, LLMProviderUpdate,
            LLMModelCreate, LLMModelUpdate,
            LLMRoleCreate, LLMRoleUpdate
        )
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.models.models import LLMProvider, LLMModel, LLMRole
        from backend.models.schemas import (
            LLMProviderCreate, LLMProviderUpdate,
            LLMModelCreate, LLMModelUpdate,
            LLMRoleCreate, LLMRoleUpdate
        )

# LLM供应商服务
def create_provider(db: Session, provider: LLMProviderCreate) -> LLMProvider:
    """创建新的LLM供应商"""
    db_provider = LLMProvider(
        name=provider.name,
        description=provider.description,
        base_url=provider.base_url,
        user_id=provider.user_id,
        is_public=provider.is_public
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def get_providers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[LLMProvider]:
    """获取LLM供应商列表"""
    query = db.query(LLMProvider)

    # 按用户ID过滤
    if user_id:
        query = query.filter(
            or_(
                LLMProvider.user_id == user_id,
                LLMProvider.is_public == True
            )
        )
    else:
        # 如果没有指定用户ID，只返回公开的供应商
        query = query.filter(LLMProvider.is_public == True)

    if search:
        query = query.filter(
            or_(
                LLMProvider.name.ilike(f"%{search}%"),
                LLMProvider.description.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all()

def get_provider(db: Session, provider_id: int) -> Optional[LLMProvider]:
    """获取单个LLM供应商详情"""
    return db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()

def update_provider(db: Session, provider_id: int, provider: LLMProviderUpdate) -> LLMProvider:
    """更新LLM供应商"""
    db_provider = db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()

    for key, value in provider.model_dump(exclude_unset=True).items():
        setattr(db_provider, key, value)

    db.commit()
    db.refresh(db_provider)
    return db_provider

def delete_provider(db: Session, provider_id: int) -> None:
    """删除LLM供应商"""
    db.query(LLMProvider).filter(LLMProvider.id == provider_id).delete()
    db.commit()

# LLM模型服务
def create_model(db: Session, model: LLMModelCreate) -> LLMModel:
    """创建新的LLM模型"""
    db_model = LLMModel(
        name=model.name,
        provider_id=model.provider_id,
        user_id=model.user_id,
        api_key=model.api_key,
        is_active=model.is_active,
        is_public=model.is_public,
        max_tokens=model.max_tokens,
        temperature=model.temperature
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_models(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    provider_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> List[LLMModel]:
    """获取LLM模型列表"""
    query = db.query(LLMModel)

    if provider_id:
        query = query.filter(LLMModel.provider_id == provider_id)

    # 按用户ID过滤
    if user_id:
        query = query.filter(
            or_(
                LLMModel.user_id == user_id,
                LLMModel.is_public == True
            )
        )
    else:
        # 如果没有指定用户ID，只返回公开的模型
        query = query.filter(LLMModel.is_public == True)

    if search:
        query = query.filter(LLMModel.name.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()

def get_model(db: Session, model_id: int) -> Optional[LLMModel]:
    """获取单个LLM模型详情"""
    return db.query(LLMModel).filter(LLMModel.id == model_id).first()

def update_model(db: Session, model_id: int, model: LLMModelUpdate) -> LLMModel:
    """更新LLM模型"""
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()

    for key, value in model.model_dump(exclude_unset=True).items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model

def delete_model(db: Session, model_id: int) -> None:
    """删除LLM模型"""
    db.query(LLMModel).filter(LLMModel.id == model_id).delete()
    db.commit()

# LLM角色服务
def create_role(db: Session, role: LLMRoleCreate) -> LLMRole:
    """创建新的LLM角色"""
    # 如果设置为默认角色，先将该模型的其他默认角色取消默认
    if role.is_default:
        db.query(LLMRole).filter(
            LLMRole.model_id == role.model_id,
            LLMRole.is_default == True
        ).update({"is_default": False})

    db_role = LLMRole(
        name=role.name,
        description=role.description,
        system_prompt=role.system_prompt,
        model_id=role.model_id,
        user_id=role.user_id,
        is_default=role.is_default,
        is_public=role.is_public
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    model_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> List[LLMRole]:
    """获取LLM角色列表"""
    query = db.query(LLMRole)

    if model_id:
        query = query.filter(LLMRole.model_id == model_id)

    # 按用户ID过滤
    if user_id:
        query = query.filter(
            or_(
                LLMRole.user_id == user_id,
                LLMRole.is_public == True
            )
        )
    else:
        # 如果没有指定用户ID，只返回公开的角色
        query = query.filter(LLMRole.is_public == True)

    if search:
        query = query.filter(
            or_(
                LLMRole.name.ilike(f"%{search}%"),
                LLMRole.description.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all()

def get_role(db: Session, role_id: int) -> Optional[LLMRole]:
    """获取单个LLM角色详情"""
    return db.query(LLMRole).filter(LLMRole.id == role_id).first()

def update_role(db: Session, role_id: int, role: LLMRoleUpdate) -> LLMRole:
    """更新LLM角色"""
    db_role = db.query(LLMRole).filter(LLMRole.id == role_id).first()

    # 如果要设置为默认角色，先将该模型的其他默认角色取消默认
    if role.is_default and role.is_default != db_role.is_default:
        db.query(LLMRole).filter(
            LLMRole.model_id == db_role.model_id,
            LLMRole.id != role_id,
            LLMRole.is_default == True
        ).update({"is_default": False})

    for key, value in role.model_dump(exclude_unset=True).items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int) -> None:
    """删除LLM角色"""
    db.query(LLMRole).filter(LLMRole.id == role_id).delete()
    db.commit()

# 获取默认角色
def get_default_role(db: Session, model_id: int) -> Optional[LLMRole]:
    """获取模型的默认角色"""
    return db.query(LLMRole).filter(
        LLMRole.model_id == model_id,
        LLMRole.is_default == True
    ).first()

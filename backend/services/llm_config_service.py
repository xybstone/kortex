from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from models.domain.llm import LLMProvider, LLMModel, LLMRole
from models.schemas.llm import (
    LLMProviderCreate, LLMProviderUpdate, LLMProviderResponse,
    LLMModelCreate, LLMModelUpdate, LLMModelResponse,
    LLMRoleCreate, LLMRoleUpdate, LLMRoleResponse
)
from utils.security import encrypt_text

# LLM供应商相关服务
def create_provider(db: Session, provider: LLMProviderCreate) -> LLMProviderResponse:
    """创建新的LLM供应商"""
    db_provider = LLMProvider(
        name=provider.name,
        description=provider.description,
        base_url=provider.base_url,
        is_public=provider.is_public,
        user_id=provider.user_id
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)

    # 转换为响应模型
    return LLMProviderResponse(
        id=db_provider.id,
        name=db_provider.name,
        description=db_provider.description,
        base_url=db_provider.base_url,
        is_public=db_provider.is_public,
        user_id=db_provider.user_id,
        created_at=db_provider.created_at,
        updated_at=db_provider.updated_at
    )

def get_providers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[LLMProviderResponse]:
    """获取LLM供应商列表"""
    query = db.query(LLMProvider)

    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        query = query.filter(
            (LLMProvider.name.ilike(f"%{search}%")) |
            (LLMProvider.description.ilike(f"%{search}%"))
        )

    # 获取分页结果
    providers = query.order_by(LLMProvider.name).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        LLMProviderResponse(
            id=provider.id,
            name=provider.name,
            description=provider.description,
            base_url=provider.base_url,
            is_public=provider.is_public,
            user_id=provider.user_id,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
        for provider in providers
    ]

def get_provider(db: Session, provider_id: int) -> Optional[LLMProviderResponse]:
    """获取单个LLM供应商详情"""
    provider = db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMProviderResponse(
        id=provider.id,
        name=provider.name,
        description=provider.description,
        base_url=provider.base_url,
        is_public=provider.is_public,
        user_id=provider.user_id,
        created_at=provider.created_at,
        updated_at=provider.updated_at
    )

def update_provider(
    db: Session,
    provider_id: int,
    provider_update: LLMProviderUpdate
) -> Optional[LLMProviderResponse]:
    """更新LLM供应商"""
    db_provider = db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()
    if not db_provider:
        return None

    # 更新供应商信息
    update_data = provider_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_provider, key, value)

    db.commit()
    db.refresh(db_provider)

    # 转换为响应模型
    return LLMProviderResponse(
        id=db_provider.id,
        name=db_provider.name,
        description=db_provider.description,
        base_url=db_provider.base_url,
        is_public=db_provider.is_public,
        user_id=db_provider.user_id,
        created_at=db_provider.created_at,
        updated_at=db_provider.updated_at
    )

def delete_provider(db: Session, provider_id: int) -> None:
    """删除LLM供应商"""
    db_provider = db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()
    if db_provider:
        db.delete(db_provider)
        db.commit()

# LLM模型相关服务
def create_model(db: Session, model: LLMModelCreate) -> LLMModelResponse:
    """创建新的LLM模型"""
    # 检查供应商是否存在
    provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 如果提供了API密钥，进行加密
    api_key = model.api_key
    if api_key:
        api_key = encrypt_text(api_key)

    db_model = LLMModel(
        name=model.name,
        provider_id=model.provider_id,
        api_key=api_key,
        is_active=model.is_active,
        is_public=model.is_public,
        max_tokens=model.max_tokens,
        temperature=model.temperature,
        user_id=model.user_id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    # 转换为响应模型
    return LLMModelResponse(
        id=db_model.id,
        name=db_model.name,
        provider_id=db_model.provider_id,
        api_key="********" if db_model.api_key else None,  # 不返回实际API密钥
        is_active=db_model.is_active,
        is_public=db_model.is_public,
        max_tokens=db_model.max_tokens,
        temperature=db_model.temperature,
        user_id=db_model.user_id,
        created_at=db_model.created_at,
        updated_at=db_model.updated_at,
        provider=LLMProviderResponse(
            id=provider.id,
            name=provider.name,
            description=provider.description,
            base_url=provider.base_url,
            is_public=provider.is_public,
            user_id=provider.user_id,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
    )

def get_models(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    provider_id: Optional[int] = None
) -> List[LLMModelResponse]:
    """获取LLM模型列表"""
    query = db.query(LLMModel)

    # 如果提供了供应商ID，只返回该供应商的模型
    if provider_id:
        query = query.filter(LLMModel.provider_id == provider_id)

    # 如果提供了搜索关键词，在名称中搜索
    if search:
        query = query.filter(LLMModel.name.ilike(f"%{search}%"))

    # 获取分页结果
    models = query.order_by(LLMModel.name).offset(skip).limit(limit).all()

    # 转换为响应模型
    result = []
    for model in models:
        provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
        if provider:
            result.append(
                LLMModelResponse(
                    id=model.id,
                    name=model.name,
                    provider_id=model.provider_id,
                    api_key="********" if model.api_key else None,  # 不返回实际API密钥
                    is_active=model.is_active,
                    is_public=model.is_public,
                    max_tokens=model.max_tokens,
                    temperature=model.temperature,
                    user_id=model.user_id,
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                    provider=LLMProviderResponse(
                        id=provider.id,
                        name=provider.name,
                        description=provider.description,
                        base_url=provider.base_url,
                        is_public=provider.is_public,
                        user_id=provider.user_id,
                        created_at=provider.created_at,
                        updated_at=provider.updated_at
                    )
                )
            )

    return result

def get_model(db: Session, model_id: int) -> Optional[LLMModelResponse]:
    """获取单个LLM模型详情"""
    model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if not model:
        return None

    provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMModelResponse(
        id=model.id,
        name=model.name,
        provider_id=model.provider_id,
        api_key="********" if model.api_key else None,  # 不返回实际API密钥
        is_active=model.is_active,
        is_public=model.is_public,
        max_tokens=model.max_tokens,
        temperature=model.temperature,
        user_id=model.user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        provider=LLMProviderResponse(
            id=provider.id,
            name=provider.name,
            description=provider.description,
            base_url=provider.base_url,
            is_public=provider.is_public,
            user_id=provider.user_id,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
    )

def update_model(
    db: Session,
    model_id: int,
    model_update: LLMModelUpdate
) -> Optional[LLMModelResponse]:
    """更新LLM模型"""
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if not db_model:
        return None

    # 更新模型信息
    update_data = model_update.model_dump(exclude_unset=True)

    # 如果更新API密钥，进行加密
    if "api_key" in update_data and update_data["api_key"]:
        update_data["api_key"] = encrypt_text(update_data["api_key"])

    for key, value in update_data.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)

    # 获取供应商信息
    provider = db.query(LLMProvider).filter(LLMProvider.id == db_model.provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMModelResponse(
        id=db_model.id,
        name=db_model.name,
        provider_id=db_model.provider_id,
        api_key="********" if db_model.api_key else None,  # 不返回实际API密钥
        is_active=db_model.is_active,
        is_public=db_model.is_public,
        max_tokens=db_model.max_tokens,
        temperature=db_model.temperature,
        user_id=db_model.user_id,
        created_at=db_model.created_at,
        updated_at=db_model.updated_at,
        provider=LLMProviderResponse(
            id=provider.id,
            name=provider.name,
            description=provider.description,
            base_url=provider.base_url,
            is_public=provider.is_public,
            user_id=provider.user_id,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
    )

def delete_model(db: Session, model_id: int) -> None:
    """删除LLM模型"""
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if db_model:
        db.delete(db_model)
        db.commit()

# LLM角色相关服务
def create_role(db: Session, role: LLMRoleCreate) -> LLMRoleResponse:
    """创建新的LLM角色"""
    # 检查模型是否存在
    model = db.query(LLMModel).filter(LLMModel.id == role.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    db_role = LLMRole(
        name=role.name,
        description=role.description,
        system_prompt=role.system_prompt,
        model_id=role.model_id,
        is_default=role.is_default,
        is_public=role.is_public,
        user_id=role.user_id
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    # 获取模型和供应商信息
    provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMRoleResponse(
        id=db_role.id,
        name=db_role.name,
        description=db_role.description,
        system_prompt=db_role.system_prompt,
        model_id=db_role.model_id,
        is_default=db_role.is_default,
        is_public=db_role.is_public,
        user_id=db_role.user_id,
        created_at=db_role.created_at,
        updated_at=db_role.updated_at,
        model=LLMModelResponse(
            id=model.id,
            name=model.name,
            provider_id=model.provider_id,
            api_key="********" if model.api_key else None,
            is_active=model.is_active,
            is_public=model.is_public,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            provider=LLMProviderResponse(
                id=provider.id,
                name=provider.name,
                description=provider.description,
                base_url=provider.base_url,
                is_public=provider.is_public,
                user_id=provider.user_id,
                created_at=provider.created_at,
                updated_at=provider.updated_at
            )
        )
    )

def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    model_id: Optional[int] = None
) -> List[LLMRoleResponse]:
    """获取LLM角色列表"""
    query = db.query(LLMRole)

    # 如果提供了模型ID，只返回该模型的角色
    if model_id:
        query = query.filter(LLMRole.model_id == model_id)

    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        query = query.filter(
            (LLMRole.name.ilike(f"%{search}%")) |
            (LLMRole.description.ilike(f"%{search}%"))
        )

    # 获取分页结果
    roles = query.order_by(LLMRole.name).offset(skip).limit(limit).all()

    # 转换为响应模型
    result = []
    for role in roles:
        model = db.query(LLMModel).filter(LLMModel.id == role.model_id).first()
        if model:
            provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
            if provider:
                result.append(
                    LLMRoleResponse(
                        id=role.id,
                        name=role.name,
                        description=role.description,
                        system_prompt=role.system_prompt,
                        model_id=role.model_id,
                        is_default=role.is_default,
                        is_public=role.is_public,
                        user_id=role.user_id,
                        created_at=role.created_at,
                        updated_at=role.updated_at,
                        model=LLMModelResponse(
                            id=model.id,
                            name=model.name,
                            provider_id=model.provider_id,
                            api_key="********" if model.api_key else None,
                            is_active=model.is_active,
                            is_public=model.is_public,
                            max_tokens=model.max_tokens,
                            temperature=model.temperature,
                            user_id=model.user_id,
                            created_at=model.created_at,
                            updated_at=model.updated_at,
                            provider=LLMProviderResponse(
                                id=provider.id,
                                name=provider.name,
                                description=provider.description,
                                base_url=provider.base_url,
                                is_public=provider.is_public,
                                user_id=provider.user_id,
                                created_at=provider.created_at,
                                updated_at=provider.updated_at
                            )
                        )
                    )
                )

    return result

def get_role(db: Session, role_id: int) -> Optional[LLMRoleResponse]:
    """获取单个LLM角色详情"""
    role = db.query(LLMRole).filter(LLMRole.id == role_id).first()
    if not role:
        return None

    model = db.query(LLMModel).filter(LLMModel.id == role.model_id).first()
    if not model:
        return None

    provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMRoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        system_prompt=role.system_prompt,
        model_id=role.model_id,
        is_default=role.is_default,
        is_public=role.is_public,
        user_id=role.user_id,
        created_at=role.created_at,
        updated_at=role.updated_at,
        model=LLMModelResponse(
            id=model.id,
            name=model.name,
            provider_id=model.provider_id,
            api_key="********" if model.api_key else None,
            is_active=model.is_active,
            is_public=model.is_public,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            provider=LLMProviderResponse(
                id=provider.id,
                name=provider.name,
                description=provider.description,
                base_url=provider.base_url,
                is_public=provider.is_public,
                user_id=provider.user_id,
                created_at=provider.created_at,
                updated_at=provider.updated_at
            )
        )
    )

def update_role(
    db: Session,
    role_id: int,
    role_update: LLMRoleUpdate
) -> Optional[LLMRoleResponse]:
    """更新LLM角色"""
    db_role = db.query(LLMRole).filter(LLMRole.id == role_id).first()
    if not db_role:
        return None

    # 更新角色信息
    update_data = role_update.model_dump(exclude_unset=True)

    # 如果更新了模型ID，检查模型是否存在
    if "model_id" in update_data:
        model = db.query(LLMModel).filter(LLMModel.id == update_data["model_id"]).first()
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")

    for key, value in update_data.items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)

    # 获取模型和供应商信息
    model = db.query(LLMModel).filter(LLMModel.id == db_role.model_id).first()
    if not model:
        return None

    provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
    if not provider:
        return None

    # 转换为响应模型
    return LLMRoleResponse(
        id=db_role.id,
        name=db_role.name,
        description=db_role.description,
        system_prompt=db_role.system_prompt,
        model_id=db_role.model_id,
        is_default=db_role.is_default,
        is_public=db_role.is_public,
        user_id=db_role.user_id,
        created_at=db_role.created_at,
        updated_at=db_role.updated_at,
        model=LLMModelResponse(
            id=model.id,
            name=model.name,
            provider_id=model.provider_id,
            api_key="********" if model.api_key else None,
            is_active=model.is_active,
            is_public=model.is_public,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            provider=LLMProviderResponse(
                id=provider.id,
                name=provider.name,
                description=provider.description,
                base_url=provider.base_url,
                is_public=provider.is_public,
                user_id=provider.user_id,
                created_at=provider.created_at,
                updated_at=provider.updated_at
            )
        )
    )

def delete_role(db: Session, role_id: int) -> None:
    """删除LLM角色"""
    db_role = db.query(LLMRole).filter(LLMRole.id == role_id).first()
    if db_role:
        db.delete(db_role)
        db.commit()

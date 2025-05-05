from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# LLM请求和响应
class LLMRequest(BaseModel):
    content: str
    model_id: Optional[int] = None
    options: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    result: Any
    type: str

class DatabaseAnalysisRequest(BaseModel):
    database_id: int
    model_id: Optional[int] = None
    prompt: str

# LLM供应商相关模式
class LLMProviderBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_public: bool = True

class LLMProviderCreate(LLMProviderBase):
    user_id: Optional[int] = None

class LLMProviderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_public: Optional[bool] = None

class LLMProviderResponse(LLMProviderBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# LLM模型相关模式
class LLMModelBase(BaseModel):
    name: str
    provider_id: int
    api_key: Optional[str] = None
    is_active: bool = True
    is_public: bool = False
    max_tokens: int = 4096
    temperature: float = 0.7

class LLMModelCreate(LLMModelBase):
    user_id: Optional[int] = None

class LLMModelUpdate(BaseModel):
    name: Optional[str] = None
    provider_id: Optional[int] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class LLMModelResponse(LLMModelBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    provider: LLMProviderResponse

    class Config:
        from_attributes = True

# LLM角色相关模式
class LLMRoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    model_id: int
    is_default: bool = False
    is_public: bool = False

class LLMRoleCreate(LLMRoleBase):
    user_id: Optional[int] = None

class LLMRoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[int] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None

class LLMRoleResponse(LLMRoleBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model: LLMModelResponse

    class Config:
        from_attributes = True

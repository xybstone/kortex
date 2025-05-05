from pydantic import BaseModel
from typing import Optional

# 认证相关模式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

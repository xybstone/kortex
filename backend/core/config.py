from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import secrets
from pathlib import Path

class Settings(BaseSettings):
    # 基本配置
    PROJECT_NAME: str = "Kortex"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/kortex"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # 文件存储配置
    UPLOAD_DIR: Path = Path("./uploads")
    
    # LLM配置
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 确保上传目录存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

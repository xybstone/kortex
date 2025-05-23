from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
import os

class Settings(BaseSettings):
    # 基本配置
    PROJECT_NAME: str = "Kortex"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/kortex"

    # CORS配置
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def BACKEND_CORS_ORIGINS_LIST(self) -> List[str]:
        """获取CORS源列表"""
        cors_origins = os.environ.get("BACKEND_CORS_ORIGINS", "")
        if cors_origins:
            # 按逗号分隔的字符串处理
            return [origin.strip() for origin in cors_origins.split(",")]
        return self.BACKEND_CORS_ORIGINS

    # 文件存储配置
    UPLOAD_DIR: Path = Path("./uploads")

    # LLM配置
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    DEEPSEEK_API_KEY: Optional[str] = None

    # 加密配置
    ENCRYPTION_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 确保上传目录存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 初始化加密密钥
if not settings.ENCRYPTION_KEY:
    settings.ENCRYPTION_KEY = Fernet.generate_key().decode()

# 注意：加密和解密函数已移至utils.security模块
# 这里保留get_cipher函数供utils.security使用
def get_cipher():
    key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
    return Fernet(key)

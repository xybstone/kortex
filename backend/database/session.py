from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from core.config import settings
else:
    try:
        # 尝试使用相对导入
        from core.config import settings
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.core.config import settings

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, connect_args={'connect_timeout': 10})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

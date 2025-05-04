from sqlalchemy.orm import Session

from core.security import get_password_hash
from database.session import SessionLocal, engine
from models.db_models import Base, User

def init_db() -> None:
    """初始化数据库"""
    # 创建表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("已初始化数据库表")
    
    # 创建初始用户
    db = SessionLocal()
    try:
        # 检查是否已存在用户
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user:
            # 创建默认用户
            hashed_password = get_password_hash("password")
            default_user = User(
                email="user@example.com",
                full_name="测试用户",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=False
            )
            db.add(default_user)
            db.commit()
            print("已创建默认用户: user@example.com")
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
    finally:
        db.close()

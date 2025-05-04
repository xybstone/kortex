#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构和初始用户
"""

import os
import sys
import sqlalchemy
from sqlalchemy import text
from passlib.context import CryptContext

# 添加当前目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入数据库相关模块
from database.session import SessionLocal, engine
from models.simple_models import Base, User
from core.config import settings

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def init_db():
    """初始化数据库"""
    print(f"SQLAlchemy版本: {sqlalchemy.__version__}")
    print(f"数据库URL: {settings.DATABASE_URL}")

    try:
        # 创建所有表
        print("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")

        # 创建会话
        db = SessionLocal()

        # 测试数据库连接
        try:
            # 执行简单查询
            result = db.execute(text("SELECT 1")).fetchone()
            print(f"数据库连接成功: {result}")

            # 创建默认用户
            print("检查默认用户...")
            user = db.query(User).filter(User.email == "user@example.com").first()
            if not user:
                print("创建默认用户...")
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
                print("默认用户创建成功: user@example.com (密码: password)")
            else:
                print(f"默认用户已存在: {user.email}")

            # 查询所有用户
            users = db.query(User).all()
            print(f"用户数量: {len(users)}")
            for user in users:
                print(f"用户ID: {user.id}, 邮箱: {user.email}")

        except Exception as e:
            print(f"数据库操作失败: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    init_db()

#!/usr/bin/env python3
"""
验证数据库连接的脚本
"""

import os
import sys
import time
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# 添加当前目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 直接创建数据库引擎和会话
docker_db_url = "postgresql://postgres:postgres@172.19.0.2:5432/kortex"
engine = create_engine(docker_db_url, connect_args={'connect_timeout': 10})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_db_connection():
    """验证数据库连接"""
    print("开始验证数据库连接...")
    print(f"数据库URL: {engine.url}")

    try:
        # 创建会话
        print("创建数据库会话...")
        start_time = time.time()
        db = SessionLocal()
        print(f"会话创建成功! 耗时: {time.time() - start_time:.2f}秒")

        # 执行简单查询
        print("执行简单查询: SELECT 1 as test")
        start_time = time.time()
        result = db.execute(text("SELECT 1 as test")).fetchone()
        print(f"查询完成! 耗时: {time.time() - start_time:.2f}秒")
        print(f"查询结果: {result.test}")

        # 查询用户表
        print("查询用户表: SELECT * FROM users LIMIT 10")
        start_time = time.time()
        users = db.execute(text("SELECT * FROM users LIMIT 10")).fetchall()
        print(f"查询完成! 耗时: {time.time() - start_time:.2f}秒")
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"用户ID: {user.id}, 邮箱: {user.email}")

        # 关闭会话
        db.close()
        print("数据库会话已关闭")
        print("数据库连接验证成功")

    except Exception as e:
        print(f"数据库连接验证失败: {e}")

if __name__ == "__main__":
    verify_db_connection()

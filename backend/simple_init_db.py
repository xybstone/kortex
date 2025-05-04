#!/usr/bin/env python3
"""
简单的数据库初始化脚本，使用psycopg2直接连接到数据库
"""

import psycopg2
import time
from passlib.context import CryptContext

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

# 数据库连接参数
db_params = {
    'host': 'localhost',  # 本地主机
    'port': 5432,
    'database': 'kortex',
    'user': 'postgres',
    'password': 'postgres',
    'connect_timeout': 10
}

def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    try:
        # 尝试连接
        print("连接到PostgreSQL数据库...")
        start_time = time.time()
        conn = psycopg2.connect(**db_params)
        print(f"连接成功! 耗时: {time.time() - start_time:.2f}秒")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 创建表
        print("创建数据库表...")
        
        # 用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """)
        
        # 笔记表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """)
        
        # 数据库表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS databases (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """)
        
        # 提交事务
        conn.commit()
        print("数据库表创建成功")
        
        # 创建默认用户
        print("检查默认用户...")
        cursor.execute("SELECT id, email FROM users WHERE email = %s", ("user@example.com",))
        user = cursor.fetchone()
        
        if not user:
            print("创建默认用户...")
            hashed_password = get_password_hash("password")
            cursor.execute(
                "INSERT INTO users (email, hashed_password, full_name, is_active, is_admin) VALUES (%s, %s, %s, %s, %s)",
                ("user@example.com", hashed_password, "测试用户", True, False)
            )
            conn.commit()
            print("默认用户创建成功: user@example.com (密码: password)")
        else:
            print(f"默认用户已存在: {user[1]}")
        
        # 查询所有用户
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"用户ID: {user[0]}, 邮箱: {user[1]}")
        
        # 关闭游标和连接
        cursor.close()
        conn.close()
        print("数据库连接已关闭")
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    init_db()

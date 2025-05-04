import sqlalchemy
from sqlalchemy import text, create_engine
import psycopg2
import time

print(f"SQLAlchemy版本: {sqlalchemy.__version__}")

# 使用Docker容器IP地址
docker_db_url = "postgresql://postgres:postgres@172.19.0.2:5432/kortex"
print(f"数据库URL: {docker_db_url}")

# 测试数据库连接 - 使用psycopg2直接连接
try:
    print("尝试使用psycopg2连接到数据库...")

    # 数据库连接参数
    db_params = {
        'host': '172.19.0.2',  # Docker容器IP地址
        'port': 5432,
        'database': 'kortex',
        'user': 'postgres',
        'password': 'postgres',
        'connect_timeout': 5
    }

    # 尝试连接
    start_time = time.time()
    conn = psycopg2.connect(**db_params)
    print(f"psycopg2连接成功! 耗时: {time.time() - start_time:.2f}秒")

    # 创建游标
    cursor = conn.cursor()

    # 执行简单查询
    cursor.execute("SELECT 1 as test;")
    test_result = cursor.fetchone()
    print(f"测试查询结果: {test_result[0]}")

    # 查询用户表
    cursor.execute("SELECT id, email FROM users;")
    users = cursor.fetchall()
    print(f"用户数量: {len(users)}")
    for user in users:
        print(f"用户ID: {user[0]}, 邮箱: {user[1]}")

    # 关闭游标和连接
    cursor.close()
    conn.close()
    print("psycopg2数据库连接已关闭")

except Exception as e:
    print(f"psycopg2数据库连接失败: {e}")

# 测试数据库连接 - 使用SQLAlchemy
try:
    print("\n尝试使用SQLAlchemy连接到数据库...")

    # 创建引擎
    start_time = time.time()
    engine = create_engine(docker_db_url, connect_args={'connect_timeout': 5})

    # 执行简单查询
    with engine.connect() as connection:
        print(f"SQLAlchemy连接成功! 耗时: {time.time() - start_time:.2f}秒")
        result = connection.execute(text("SELECT 1 as test;"))
        for row in result:
            print(f"测试查询结果: {row.test}")

        # 查询用户表
        result = connection.execute(text("SELECT id, email FROM users;"))
        users = result.fetchall()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"用户ID: {user.id}, 邮箱: {user.email}")

    print("SQLAlchemy数据库连接已关闭")

except Exception as e:
    print(f"SQLAlchemy数据库连接失败: {e}")

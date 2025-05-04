#!/usr/bin/env python3
"""
简单的数据库连接测试脚本
"""

import psycopg2
import time

# 数据库连接参数
db_params = {
    'host': '172.19.0.2',  # Docker容器IP地址
    'port': 5432,
    'database': 'kortex',
    'user': 'postgres',
    'password': 'postgres'
}

def test_connection():
    """测试数据库连接"""
    print("尝试连接到PostgreSQL数据库...")
    print(f"连接参数: {db_params}")

    try:
        # 设置连接超时
        start_time = time.time()
        timeout = 5  # 5秒超时

        print(f"开始连接，超时设置为 {timeout} 秒...")

        # 尝试连接
        conn = psycopg2.connect(**db_params, connect_timeout=timeout)

        # 如果连接成功
        print(f"连接成功! 耗时: {time.time() - start_time:.2f}秒")

        # 创建游标
        cursor = conn.cursor()

        # 执行简单查询
        print("执行查询: SELECT version();")
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQL 版本: {db_version[0]}")

        # 执行另一个简单查询
        print("执行查询: SELECT 1 as test;")
        cursor.execute("SELECT 1 as test;")
        test_result = cursor.fetchone()
        print(f"测试结果: {test_result[0]}")

        # 关闭游标和连接
        cursor.close()
        conn.close()
        print("数据库连接已关闭")

    except Exception as e:
        print(f"连接失败: {e}")
        print("请检查以下可能的问题:")
        print("1. PostgreSQL服务是否正在运行")
        print("2. 数据库用户名和密码是否正确")
        print("3. 数据库名称是否正确")
        print("4. 主机和端口是否正确")
        print("5. 防火墙设置是否允许连接")

if __name__ == "__main__":
    test_connection()

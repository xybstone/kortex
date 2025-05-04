#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "===== 使用本地数据库启动Kortex应用 ====="

# 检查docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装docker，请先安装docker"
    exit 1
fi

# 检查docker compose是否可用（支持新旧两种命令格式）
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "错误: 未安装docker compose，请安装Docker Desktop或单独安装docker compose"
    exit 1
fi

echo "使用 $DOCKER_COMPOSE 命令"

# 检查PostgreSQL是否运行
echo "检查本地PostgreSQL数据库..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
        echo "本地PostgreSQL数据库已运行"
    else
        echo "警告: 本地PostgreSQL数据库未运行，请确保PostgreSQL已启动"
        echo "您可以使用以下命令启动PostgreSQL："
        echo "  macOS: brew services start postgresql"
        echo "  Linux: sudo systemctl start postgresql"
        echo "  Windows: 通过服务管理器启动PostgreSQL服务"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "警告: 未找到pg_isready命令，无法检查PostgreSQL状态"
    echo "请确保PostgreSQL已安装并运行，数据库名为'kortex'，用户名为'postgres'，密码为'postgres'"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建.env文件（如果不存在）
if [ ! -f backend/.env ]; then
    echo "创建后端.env文件..."
    cp backend/.env.example backend/.env
    echo "请编辑backend/.env文件，填入您的配置信息"
fi

if [ ! -f frontend/.env ]; then
    echo "创建前端.env文件..."
    cp frontend/.env.example frontend/.env
    echo "请编辑frontend/.env文件，填入您的配置信息"
fi

# 创建数据库（如果不存在）
echo "尝试创建kortex数据库（如果不存在）..."
if command -v psql &> /dev/null; then
    psql -h localhost -U postgres -c "SELECT 1 FROM pg_database WHERE datname = 'kortex'" | grep -q 1 || psql -h localhost -U postgres -c "CREATE DATABASE kortex"
    echo "数据库已准备就绪"
else
    echo "警告: 未找到psql命令，无法创建数据库"
    echo "请手动创建名为'kortex'的数据库"
fi

# 构建并启动容器
echo "构建并启动Docker容器..."
DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 $DOCKER_COMPOSE -f docker-compose-local-db.yml up -d --build

echo "===== Kortex应用已启动 ====="
echo "前端地址: http://localhost:3000"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"

# 显示容器状态
echo "===== 容器状态 ====="
$DOCKER_COMPOSE -f docker-compose-local-db.yml ps

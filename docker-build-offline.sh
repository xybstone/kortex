#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "===== 离线构建Kortex应用 ====="

# 检查docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装docker，请先安装docker"
    exit 1
fi

# 检查是否有必要的基础镜像
echo "检查本地镜像..."
MISSING_IMAGES=0

if ! docker image inspect postgres:14 &> /dev/null; then
    echo "警告: 本地没有postgres:14镜像"
    MISSING_IMAGES=1
fi

if ! docker image inspect python:3.10-slim &> /dev/null; then
    echo "警告: 本地没有python:3.10-slim镜像"
    MISSING_IMAGES=1
fi

if ! docker image inspect node:18-alpine &> /dev/null; then
    echo "警告: 本地没有node:18-alpine镜像"
    MISSING_IMAGES=1
fi

if [ $MISSING_IMAGES -eq 1 ]; then
    echo "您缺少一些必要的基础镜像。请在有网络连接的环境中运行以下命令拉取镜像："
    echo "docker pull postgres:14"
    echo "docker pull python:3.10-slim"
    echo "docker pull node:18-alpine"
    echo "然后将镜像保存为tar文件："
    echo "docker save postgres:14 -o postgres.tar"
    echo "docker save python:3.10-slim -o python.tar"
    echo "docker save node:18-alpine -o node.tar"
    echo "将tar文件复制到当前环境，然后加载镜像："
    echo "docker load -i postgres.tar"
    echo "docker load -i python.tar"
    echo "docker load -i node.tar"
    echo "然后再次运行此脚本。"
    
    read -p "是否继续尝试构建? (y/n) " -n 1 -r
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

# 手动构建镜像
echo "===== 开始离线构建 ====="

# 构建后端镜像
echo "构建后端镜像..."
docker build -t kortex-backend:latest --network=none ./backend

# 构建前端镜像
echo "构建前端镜像..."
docker build -t kortex-frontend:latest --network=none ./frontend

# 创建网络（如果不存在）
if ! docker network inspect kortex-network &> /dev/null; then
    echo "创建Docker网络..."
    docker network create kortex-network
fi

# 启动数据库
echo "启动数据库..."
docker run -d \
    --name kortex-db \
    --network kortex-network \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=kortex \
    -v postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:14

echo "等待数据库启动..."
sleep 10

# 启动后端
echo "启动后端..."
docker run -d \
    --name kortex-backend \
    --network kortex-network \
    -e DATABASE_URL=postgresql://postgres:postgres@kortex-db/kortex \
    -e SECRET_KEY=supersecretkey \
    -e BACKEND_CORS_ORIGINS=http://localhost:3000,http://kortex-frontend:3000 \
    -v ./backend/uploads:/app/uploads \
    -p 8000:8000 \
    kortex-backend:latest

echo "等待后端启动..."
sleep 10

# 启动前端
echo "启动前端..."
docker run -d \
    --name kortex-frontend \
    --network kortex-network \
    -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
    -p 3000:3000 \
    kortex-frontend:latest

echo "===== Kortex应用已启动 ====="
echo "前端地址: http://localhost:3000"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"

# 显示容器状态
echo "===== 容器状态 ====="
docker ps -a | grep kortex

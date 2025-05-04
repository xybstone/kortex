#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "===== 分步启动Kortex应用 ====="

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

# 分步启动容器
echo "===== 步骤1: 拉取基础镜像 ====="
echo "拉取PostgreSQL镜像..."
docker pull postgres:14 || echo "无法拉取PostgreSQL镜像，将在启动时自动尝试"

echo "拉取Python镜像..."
docker pull python:3.10-slim || echo "无法拉取Python镜像，将在启动时自动尝试"

echo "拉取Node.js镜像..."
docker pull node:18-alpine || echo "无法拉取Node.js镜像，将在启动时自动尝试"

echo "===== 步骤2: 启动数据库 ====="
DOCKER_CLIENT_TIMEOUT=120 COMPOSE_HTTP_TIMEOUT=120 $DOCKER_COMPOSE up -d db
echo "等待数据库启动..."
sleep 10

echo "===== 步骤3: 构建并启动后端 ====="
DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 $DOCKER_COMPOSE build --no-cache --pull=never backend && $DOCKER_COMPOSE up -d backend
echo "等待后端启动..."
sleep 10

echo "===== 步骤4: 构建并启动前端 ====="
DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 $DOCKER_COMPOSE build --no-cache --pull=never frontend && $DOCKER_COMPOSE up -d frontend

echo "===== Kortex应用已启动 ====="
echo "前端地址: http://localhost:3000"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"

# 显示容器状态
echo "===== 容器状态 ====="
$DOCKER_COMPOSE ps

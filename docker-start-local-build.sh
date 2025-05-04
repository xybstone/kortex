#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "===== 使用本地构建启动Kortex应用 ====="

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

# 构建并启动容器
echo "构建并启动Docker容器..."
DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 DOCKER_BUILDKIT=0 $DOCKER_COMPOSE -f docker-compose-local.yml build --no-cache --pull=never
DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 $DOCKER_COMPOSE -f docker-compose-local.yml up -d

echo "===== Kortex应用已启动 ====="
echo "前端地址: http://localhost:3000"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"

# 显示容器状态
echo "===== 容器状态 ====="
$DOCKER_COMPOSE -f docker-compose-local.yml ps

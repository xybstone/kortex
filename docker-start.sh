#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "===== 启动Kortex应用 ====="

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

# 尝试预先拉取镜像
echo "预先拉取基础镜像，这可能需要一些时间..."
docker pull postgres:14 || true
docker pull python:3.10-slim || true
docker pull node:18-alpine || true

# 尝试最多5次构建和启动
MAX_RETRIES=5
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    echo "尝试构建和启动容器 (尝试 $((RETRY_COUNT+1))/$MAX_RETRIES)..."
    if DOCKER_CLIENT_TIMEOUT=300 COMPOSE_HTTP_TIMEOUT=300 $DOCKER_COMPOSE build --no-cache --pull=never && $DOCKER_COMPOSE up -d; then
        SUCCESS=true
        echo "容器启动成功！"
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            WAIT_TIME=$((30 + RETRY_COUNT * 30))
            echo "启动失败，将在${WAIT_TIME}秒后重试..."
            sleep $WAIT_TIME
        else
            echo "达到最大重试次数，请检查网络连接或Docker配置。"
            echo "您可以尝试手动运行以下命令来拉取镜像："
            echo "docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/postgres:14"
            echo "docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/python:3.10-slim"
            echo "docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/node:18-alpine"
            echo "然后再次运行 ./docker-start.sh"
            exit 1
        fi
    fi
done

echo "===== Kortex应用已启动 ====="
echo "前端地址: http://localhost:3000"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"

# 显示容器状态
echo "===== 容器状态 ====="
$DOCKER_COMPOSE ps

#!/bin/bash

echo "===== 停止Kortex应用 ====="

# 检查docker compose是否可用（支持新旧两种命令格式）
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "错误: 未安装docker compose，请安装Docker Desktop或单独安装docker compose"
    exit 1
fi

# 停止容器
echo "使用 $DOCKER_COMPOSE 命令停止容器..."
$DOCKER_COMPOSE down

echo "===== Kortex应用已停止 ====="

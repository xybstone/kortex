#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 设置默认值
USE_CACHE=1  # 默认不使用缓存
# 禁用BuildKit
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --use-cache) USE_CACHE=0; shift ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

echo -e "${YELLOW}===== Kortex 构建脚本 =====${NC}"

# 清理旧的悬空镜像
echo -e "${YELLOW}清理旧的悬空镜像...${NC}"
docker image prune -f

# 构建后端
echo -e "${YELLOW}构建后端镜像...${NC}"
if [ $USE_CACHE -eq 0 ]; then
    echo -e "${YELLOW}使用缓存构建${NC}"
    docker compose build backend
else
    echo -e "${YELLOW}不使用缓存构建${NC}"
    docker compose build --no-cache backend
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}后端构建失败!${NC}"
    exit 1
fi
echo -e "${GREEN}后端构建成功!${NC}"

# 构建前端
echo -e "${YELLOW}构建前端镜像...${NC}"
if [ $USE_CACHE -eq 0 ]; then
    docker compose build frontend
else
    docker compose build --no-cache frontend
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}前端构建失败!${NC}"
    exit 1
fi
echo -e "${GREEN}前端构建成功!${NC}"

# 清理构建过程中产生的悬空镜像
echo -e "${YELLOW}清理构建过程中产生的悬空镜像...${NC}"
docker image prune -f

echo -e "${GREEN}===== 构建完成! =====${NC}"
echo -e "${GREEN}使用 'docker compose up -d' 启动服务${NC}"

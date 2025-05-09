#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Kortex PDF测试构建脚本 =====${NC}"

# 清理旧的悬空镜像
echo -e "${YELLOW}清理旧的悬空镜像...${NC}"
docker image prune -f

# 构建后端
echo -e "${YELLOW}构建后端镜像...${NC}"
docker compose -f docker-compose.pdf-test.yml build backend

if [ $? -ne 0 ]; then
    echo -e "${RED}后端构建失败!${NC}"
    exit 1
fi
echo -e "${GREEN}后端构建成功!${NC}"

# 清理构建过程中产生的悬空镜像
echo -e "${YELLOW}清理构建过程中产生的悬空镜像...${NC}"
docker image prune -f

echo -e "${GREEN}===== 构建完成! =====${NC}"
echo -e "${GREEN}使用 'docker compose -f docker-compose.pdf-test.yml up -d' 启动服务${NC}"

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker compose -f docker-compose.pdf-test.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}服务启动失败!${NC}"
    exit 1
fi
echo -e "${GREEN}服务启动成功!${NC}"

# 显示服务状态
echo -e "${YELLOW}服务状态:${NC}"
docker compose -f docker-compose.pdf-test.yml ps

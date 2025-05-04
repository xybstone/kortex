#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Kortex 完整重建脚本 =====${NC}"

# 停止并移除所有容器
echo -e "${YELLOW}停止并移除所有容器...${NC}"
docker compose down

# 清理所有无用的镜像
echo -e "${YELLOW}清理无用的镜像...${NC}"
docker image prune -f

# 清理无用的卷
echo -e "${YELLOW}清理无用的卷...${NC}"
docker volume prune -f

# 清理无用的网络
echo -e "${YELLOW}清理无用的网络...${NC}"
docker network prune -f

# 构建后端
echo -e "${YELLOW}构建后端镜像...${NC}"
docker compose build backend
if [ $? -ne 0 ]; then
    echo -e "${RED}后端构建失败!${NC}"
    exit 1
fi
echo -e "${GREEN}后端构建成功!${NC}"

# 构建前端
echo -e "${YELLOW}构建前端镜像...${NC}"
docker compose build frontend
if [ $? -ne 0 ]; then
    echo -e "${RED}前端构建失败!${NC}"
    exit 1
fi
echo -e "${GREEN}前端构建成功!${NC}"

# 清理构建过程中产生的悬空镜像
echo -e "${YELLOW}清理构建过程中产生的悬空镜像...${NC}"
docker image prune -f

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker compose up -d

echo -e "${GREEN}===== 重建完成! =====${NC}"
echo -e "${GREEN}服务已启动${NC}"

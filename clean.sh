#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Kortex Docker 清理脚本 =====${NC}"

# 停止并移除所有容器
echo -e "${YELLOW}停止并移除所有容器...${NC}"
docker compose down

# 清理所有悬空镜像
echo -e "${YELLOW}清理悬空镜像...${NC}"
docker image prune -f

# 询问是否要清理所有未使用的镜像
echo -e "${YELLOW}是否要清理所有未使用的镜像? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}清理所有未使用的镜像...${NC}"
    docker image prune -a -f
fi

# 清理无用的卷
echo -e "${YELLOW}清理无用的卷...${NC}"
docker volume prune -f

# 清理无用的网络
echo -e "${YELLOW}清理无用的网络...${NC}"
docker network prune -f

# 显示当前镜像列表
echo -e "${YELLOW}当前镜像列表:${NC}"
docker image list

echo -e "${GREEN}===== 清理完成! =====${NC}"

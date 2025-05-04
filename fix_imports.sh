#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== 修复导入路径脚本 =====${NC}"

# 获取所有路由文件
ROUTE_FILES=$(find backend/api/routes -name "*.py")

for file in $ROUTE_FILES; do
    echo -e "${YELLOW}处理文件: ${file}${NC}"
    
    # 检查文件是否包含 "from backend."
    if grep -q "from backend\." "$file"; then
        echo -e "${YELLOW}修改文件: ${file}${NC}"
        
        # 创建临时文件
        TMP_FILE=$(mktemp)
        
        # 添加环境检测代码
        cat > "$TMP_FILE" << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

EOF
        
        # 提取导入部分
        IMPORTS=$(grep -n "^from " "$file" | head -1 | cut -d: -f1)
        ROUTER_LINE=$(grep -n "^router = APIRouter" "$file" | head -1 | cut -d: -f1)
        
        # 如果找不到router行，使用默认值
        if [ -z "$ROUTER_LINE" ]; then
            ROUTER_LINE=30
        fi
        
        # 计算导入部分的结束行
        IMPORT_END=$((ROUTER_LINE - 1))
        
        # 提取导入内容
        IMPORT_CONTENT=$(sed -n "${IMPORTS},${IMPORT_END}p" "$file" | grep -v "^from fastapi\|^from typing\|^from sqlalchemy")
        
        # 创建Docker环境下的导入
        DOCKER_IMPORTS=$(echo "$IMPORT_CONTENT" | sed 's/from backend\./from /g')
        
        # 添加条件导入
        cat >> "$TMP_FILE" << EOF
if IS_DOCKER:
    # Docker环境下使用相对导入
$DOCKER_IMPORTS
else:
    try:
        # 尝试使用相对导入
$(echo "$DOCKER_IMPORTS")
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
$IMPORT_CONTENT
EOF
        
        # 添加路由部分
        sed -n "${ROUTER_LINE},\$p" "$file" >> "$TMP_FILE"
        
        # 替换原文件
        mv "$TMP_FILE" "$file"
        
        echo -e "${GREEN}文件已修改: ${file}${NC}"
    else
        echo -e "${GREEN}文件无需修改: ${file}${NC}"
    fi
done

echo -e "${GREEN}===== 修复完成! =====${NC}"

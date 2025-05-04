#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== 修复路由文件 =====${NC}"

# 获取所有路由文件
ROUTE_FILES=$(find backend/api/routes -name "*.py" -not -name "__init__.py" -not -name "llm_config.py")

for file in $ROUTE_FILES; do
    echo -e "${YELLOW}处理文件: ${file}${NC}"
    
    # 创建临时文件
    TMP_FILE=$(mktemp)
    
    # 添加标准导入和环境检测
    cat > "$TMP_FILE" << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

if IS_DOCKER:
    # Docker环境下使用相对导入
    from core.dependencies import get_db, get_current_user
    from models.schemas import *
    from core.services import *
else:
    try:
        # 尝试使用相对导入
        from core.dependencies import get_db, get_current_user
        from models.schemas import *
        from core.services import *
    except ImportError:
        # 尝试使用绝对导入（本地开发环境）
        from backend.core.dependencies import get_db, get_current_user
        from backend.models.schemas import *
        from backend.core.services import *

EOF
    
    # 提取路由部分
    ROUTER_LINE=$(grep -n "^router = APIRouter" "$file" | head -1 | cut -d: -f1)
    
    # 如果找不到router行，使用默认值
    if [ -z "$ROUTER_LINE" ]; then
        echo -e "${RED}无法找到router行，跳过文件: ${file}${NC}"
        rm "$TMP_FILE"
        continue
    fi
    
    # 添加路由部分
    sed -n "${ROUTER_LINE},\$p" "$file" >> "$TMP_FILE"
    
    # 替换原文件
    mv "$TMP_FILE" "$file"
    
    echo -e "${GREEN}文件已修复: ${file}${NC}"
done

echo -e "${GREEN}===== 修复完成! =====${NC}"

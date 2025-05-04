#!/bin/bash

# 确保在backend目录下运行
cd "$(dirname "$0")"

# 运行数据库初始化脚本
echo "开始初始化数据库..."
python init_db.py

echo "数据库初始化完成"

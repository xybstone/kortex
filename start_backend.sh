#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 切换到后端目录
cd backend

# 设置Python路径
export PYTHONPATH=$PYTHONPATH:$(pwd)/..

# 启动后端服务器
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 如果服务器停止，提示用户
echo "后端服务器已停止。"

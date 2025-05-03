#!/bin/bash

# 切换到前端目录
cd frontend

# 安装依赖（如果尚未安装）
if [ ! -d "node_modules" ]; then
  echo "正在安装前端依赖..."
  npm install
fi

# 启动前端开发服务器
npm run dev

# 如果服务器停止，提示用户
echo "前端服务器已停止。"

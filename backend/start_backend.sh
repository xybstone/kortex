#!/bin/bash

# 启动后端应用程序
echo "启动后端应用程序..."
python -m uvicorn simple_app:app --reload --host 0.0.0.0 --port 8001

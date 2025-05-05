#!/bin/bash

# 运行测试
echo "运行测试..."
# 使用Python直接运行测试
python tests/run_direct_test.py

# 尝试运行auth测试
echo "尝试运行auth测试..."
python tests/test_auth_direct.py

# 尝试运行pytest测试
echo "尝试运行pytest测试..."
pytest -xvs tests/test_auth.py

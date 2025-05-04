#!/bin/bash

# 为Docker配置镜像加速器
echo "为Docker配置镜像加速器..."

# 检查操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS系统
    echo "检测到macOS系统"
    
    # 检查Docker Desktop配置文件是否存在
    DOCKER_CONFIG_FILE="$HOME/Library/Group Containers/group.com.docker/settings.json"
    if [ -f "$DOCKER_CONFIG_FILE" ]; then
        echo "找到Docker Desktop配置文件，添加镜像加速器配置..."
        
        # 备份原配置文件
        cp "$DOCKER_CONFIG_FILE" "$DOCKER_CONFIG_FILE.bak"
        
        # 检查是否已经配置了registry-mirrors
        if grep -q "registry-mirrors" "$DOCKER_CONFIG_FILE"; then
            echo "已存在镜像加速器配置，跳过..."
        else
            # 使用临时文件添加配置
            TMP_FILE=$(mktemp)
            jq '. + {"registry-mirrors": ["https://docker.m.daocloud.io", "https://registry.docker-cn.com", "https://hub-mirror.c.163.com"]}' "$DOCKER_CONFIG_FILE" > "$TMP_FILE"
            mv "$TMP_FILE" "$DOCKER_CONFIG_FILE"
            echo "镜像加速器配置已添加"
        fi
        
        echo "请重启Docker Desktop以使配置生效"
    else
        echo "未找到Docker Desktop配置文件，请手动配置镜像加速器"
        echo "打开Docker Desktop -> Preferences -> Docker Engine，添加以下配置："
        echo '{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com"
  ]
}'
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux系统
    echo "检测到Linux系统"
    
    # 检查是否有sudo权限
    if command -v sudo &> /dev/null; then
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    # 创建Docker配置目录
    $SUDO mkdir -p /etc/docker
    
    # 配置镜像加速器
    echo '{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com"
  ]
}' | $SUDO tee /etc/docker/daemon.json > /dev/null
    
    # 重启Docker服务
    $SUDO systemctl daemon-reload
    $SUDO systemctl restart docker
    
    echo "镜像加速器配置已添加并重启Docker服务"
else
    echo "不支持的操作系统，请手动配置镜像加速器"
fi

echo "配置完成"

# Kortex 离线安装指南

如果您的网络环境无法连接到Docker Hub或其他镜像源，可以按照以下步骤进行离线安装。

## 准备工作

在有网络连接的环境中执行以下步骤：

1. 拉取所需的Docker镜像

```bash
# 拉取PostgreSQL镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/postgres:14

# 拉取Python镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/python:3.10-slim

# 拉取Node.js镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library-mirror/node:18-alpine
```

2. 将镜像保存为tar文件

```bash
# 保存PostgreSQL镜像
docker save registry.cn-hangzhou.aliyuncs.com/library-mirror/postgres:14 -o postgres.tar

# 保存Python镜像
docker save registry.cn-hangzhou.aliyuncs.com/library-mirror/python:3.10-slim -o python.tar

# 保存Node.js镜像
docker save registry.cn-hangzhou.aliyuncs.com/library-mirror/node:18-alpine -o node.tar
```

3. 将tar文件和项目代码一起复制到离线环境中

## 离线安装步骤

在离线环境中执行以下步骤：

1. 加载Docker镜像

```bash
# 加载PostgreSQL镜像
docker load -i postgres.tar

# 加载Python镜像
docker load -i python.tar

# 加载Node.js镜像
docker load -i node.tar
```

2. 创建必要的环境文件

```bash
# 创建后端环境文件
cp backend/.env.example backend/.env

# 创建前端环境文件
cp frontend/.env.example frontend/.env
```

3. 使用分步启动脚本启动应用

```bash
./docker-start-step-by-step.sh
```

## 注意事项

- 离线环境中需要预先安装Docker和Docker Compose
- 如果构建过程中需要下载npm或pip依赖，可能需要提前准备离线包
- 对于前端依赖，可以考虑在有网络的环境中先运行`npm install`，然后将`node_modules`目录一起复制到离线环境
- 对于后端依赖，可以考虑使用`pip download -r requirements.txt -d ./pip-packages`下载依赖包，然后在离线环境中使用`pip install --no-index --find-links=./pip-packages -r requirements.txt`安装

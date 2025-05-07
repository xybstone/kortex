# Kortex

## 项目概述

**项目名称**：Kortex
**项目简介**：一个在线笔记工具，支持Markdown编辑、数据库管理和大模型集成
**项目语言**：Python (后端)，JavaScript/TypeScript (前端)
**项目版本**：0.1.0

## 主要功能

- **Markdown笔记编辑器**：类似于Obsidian的笔记编辑体验
- **数据库管理**：支持创建、导入和管理数据库
- **笔记与数据库关联**：在笔记中引用和可视化数据
- **大模型集成**：利用AI分析数据并生成笔记内容
  - 支持多种大模型供应商配置
  - 可自定义AI角色和系统提示词
  - 笔记页面集成AI助手对话功能

## 项目架构

### 前端 (Frontend)

- **技术栈**：React + TypeScript
- **主要组件**：
  - Markdown编辑器
  - 数据库管理界面
  - 数据可视化组件
  - 大模型交互界面

### 后端 (Backend)

- **技术栈**：FastAPI + SQLAlchemy
- **主要模块**：
  - API层：处理HTTP请求
  - 核心层：实现业务逻辑
  - 服务层：集成第三方服务
  - 数据层：管理数据存储和访问
  - 模型层：定义数据模型和关系
- **安全特性**：
  - API密钥加密存储
  - JWT认证
  - CORS保护
- **模型设计**：
  - 使用SQLAlchemy ORM进行数据建模
  - 模型命名避免冲突，使用明确的前缀或后缀
  - 支持模型扩展和继承

### 数据库

- **笔记数据**：存储用户笔记内容和元数据
- **用户数据**：管理用户账户和权限
- **数据库管理**：支持用户创建的数据集
- **关联数据**：管理笔记与数据库之间的关联

## 开发路线图

### 一期

- [x] 项目的架构设计
- [x] 大模型API接入功能开发，支持在页面上设置常见的大模型(GPT-3.5-turbo, Claude-3,DeepSeek等)
- [x] 开发用户认证与授权系统，支持用户登录、注册每个用户可以创建笔记、数据库、大模型、大模型角色等
- [x] 大模型角色配置功能，支持创建和管理不同的AI角色
- [x] 笔记页面集成AI助手功能，支持与大模型对话
- [x] 在线笔记的功能开发
- [x] 大模型助手功能完善，支持对话和回复
- [x] 笔记页面优化(1):1. 去掉markdown的预览页面，直接在编辑页面显示预览内容；2.把大模型AI助手放在编辑器的左侧，可以更好的显示和控制大模型的输出； 
- [ ] 数据集管理模块
- [ ] 笔记页面优化(2):1. AI助手能引用笔记中的内容，以便更好的提高回复的准确性；
- [ ] 用本地服务器存储数据，比如：用户信息,用户配置,数据库,大模型配置等
- [ ] 数据的功能开发，支持导入数据(Excel, CSV, JSON)
- [ ] 笔记与数据库的关联功能开发（可以在笔记中引用数据）

### 二期

- [ ] 笔记版本控制
- [ ] 协作编辑功能
- [ ] 高级数据可视化
- [ ] 移动端适配

## 安装与使用

### 环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### 方法一：使用Docker部署（推荐）

如果您已安装Docker和Docker Compose，可以使用以下命令快速部署：

1. 克隆仓库

   ```bash
   git clone https://github.com/yourusername/kortex.git
   cd kortex
   ```

2. 构建并启动应用

   ```bash
   # 使用缓存构建（推荐，速度更快）
   ./build.sh --use-cache

   # 或从头构建
   ./build.sh

   # 启动服务
   docker compose up -d
   ```

   这将自动构建并启动所有必要的服务，包括PostgreSQL数据库、后端API和前端应用。

3. 访问应用

   - 前端界面：[http://localhost:3000](http://localhost:3000)
   - API文档：[http://localhost:8000/docs](http://localhost:8000/docs)

4. 停止应用

   ```bash
   docker compose down
   ```

5. 查看日志

   ```bash
   # 查看后端日志
   docker logs kortex-backend

   # 查看前端日志
   docker logs kortex-frontend

   # 查看数据库日志
   docker logs kortex-db
   ```

### 方法二：手动安装

1. 克隆仓库

   ```bash
   git clone https://github.com/yourusername/kortex.git
   cd kortex
   ```

2. 创建并激活Python虚拟环境

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   .\venv\Scripts\activate  # Windows
   ```

   也可以使用提供的激活脚本：

   ```bash
   ./activate.sh  # Linux/macOS
   ```

3. 安装后端依赖

   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. 安装前端依赖

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. 启动开发服务器

   使用提供的启动脚本：

   ```bash
   # 启动后端
   ./start_backend.sh

   # 启动前端（在另一个终端）
   ./start_frontend.sh
   ```

   或手动启动：

   ```bash
   # 后端
   cd backend
   uvicorn main:app --reload

   # 前端（在另一个终端）
   cd frontend
   npm run dev
   ```

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请参阅[贡献指南](docs/CONTRIBUTING.md)了解详情。

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

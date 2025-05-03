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

### 数据库

- **笔记数据**：存储用户笔记内容和元数据
- **用户数据**：管理用户账户和权限
- **数据库管理**：支持用户创建的数据集
- **关联数据**：管理笔记与数据库之间的关联

## 开发路线图

### 一期

- [x] 项目的架构设计
- [ ] 在线笔记本的功能开发
- [ ] 数据的功能开发，支持导入数据(Excel, CSV, JSON)
- [ ] 大模型API接入功能开发
- [ ] 笔记与数据库的关联功能开发（可以在笔记中引用数据）

### 二期

- [ ] 用户认证与授权系统
- [ ] 笔记版本控制
- [ ] 协作编辑功能
- [ ] 高级数据可视化
- [ ] 移动端适配

## 安装与使用

### 环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/kortex.git
   cd kortex
   ```

2. 安装后端依赖
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. 安装前端依赖
   ```bash
   cd ../frontend
   npm install
   ```

4. 启动开发服务器
   ```bash
   # 后端
   cd ../backend
   uvicorn main:app --reload

   # 前端
   cd ../frontend
   npm run dev
   ```

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请参阅[贡献指南](docs/CONTRIBUTING.md)了解详情。

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
# Kortex 项目架构文档

## 1. 项目概述

Kortex 是一个在线笔记工具，支持 Markdown 编辑、数据库管理和大模型集成。项目采用模块化架构，遵循现代 Python 应用的最佳实践。

## 2. 技术栈

- **后端**：FastAPI + SQLAlchemy + Pydantic
- **数据库**：PostgreSQL
- **部署**：Docker
- **大模型集成**：支持多种大模型 API（OpenAI、Anthropic、DeepSeek 等）

## 3. 目录结构

```
backend/
├── api/                  # API层
│   ├── dependencies/     # 依赖项（认证、权限等）
│   ├── endpoints/        # 路由端点定义
│   └── middleware/       # 中间件
├── core/                 # 核心配置
│   ├── config.py         # 配置
│   └── security.py       # 安全相关
├── database/             # 数据库
│   ├── init_db.py        # 数据库初始化
│   └── session.py        # 会话管理
├── models/               # 数据模型
│   ├── domain/           # 领域模型（数据库模型）
│   └── schemas/          # Pydantic模型（API模型）
├── services/             # 业务逻辑
│   ├── auth_service.py
│   ├── note_service.py
│   └── ...
├── tests/                # 测试
│   ├── conftest.py       # 测试配置
│   └── ...
├── utils/                # 工具函数
├── main.py               # 应用入口
└── Dockerfile            # Docker配置
```

## 4. 架构设计

### 4.1 分层架构

项目采用分层架构，各层职责如下：

1. **API 层**：处理 HTTP 请求和响应，包括路由定义、请求验证和响应格式化。
2. **服务层**：实现业务逻辑，处理数据的增删改查和业务规则。
3. **数据访问层**：通过 SQLAlchemy ORM 与数据库交互。
4. **模型层**：定义数据结构，包括数据库模型和 API 模型。

### 4.2 依赖注入

项目使用 FastAPI 的依赖注入系统，实现以下功能：

1. **数据库会话**：通过依赖项提供数据库会话。
2. **用户认证**：通过依赖项获取当前用户。
3. **权限控制**：通过依赖项检查用户权限。

### 4.3 模块化设计

项目采用模块化设计，按功能划分模块：

1. **认证模块**：处理用户注册、登录和认证。
2. **笔记模块**：处理笔记的增删改查。
3. **数据库模块**：处理数据库的管理和操作。
4. **大模型模块**：处理与大模型的交互。

## 5. 数据模型

### 5.1 用户模型

```python
class User(BaseModel, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # 关系
    notes = relationship("Note", back_populates="user")
    databases = relationship("Database", back_populates="user")
    llm_providers = relationship("LLMProvider", back_populates="user")
    llm_models = relationship("LLMModel", back_populates="user")
    llm_roles = relationship("LLMRole", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
```

### 5.2 笔记模型

```python
class Note(BaseModel, TimestampMixin):
    """笔记模型"""
    __tablename__ = "notes"

    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(ForeignKey("users.id"))

    # 关系
    user = relationship("User", back_populates="notes")
    databases = relationship("Database", secondary=note_database, back_populates="notes")
    conversations = relationship("Conversation", back_populates="note")
```

### 5.3 大模型相关模型

```python
class LLMProvider(BaseModel, TimestampMixin):
    """LLM供应商模型"""
    __tablename__ = "llm_providers"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    base_url = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    user = relationship("User", back_populates="llm_providers")
    models = relationship("LLMModel", back_populates="provider", cascade="all, delete-orphan")

class LLMModel(BaseModel, TimestampMixin):
    """LLM模型"""
    __tablename__ = "llm_models"

    name = Column(String, index=True)
    provider_id = Column(ForeignKey("llm_providers.id"))
    api_key = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    max_tokens = Column(Integer, default=4096)
    temperature = Column(Float, default=0.7)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    provider = relationship("LLMProvider", back_populates="models")
    user = relationship("User", back_populates="llm_models")
    roles = relationship("LLMRole", back_populates="model", cascade="all, delete-orphan")

class LLMRole(BaseModel, TimestampMixin):
    """LLM角色"""
    __tablename__ = "llm_roles"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text)
    model_id = Column(ForeignKey("llm_models.id"))
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    model = relationship("LLMModel", back_populates="roles")
    user = relationship("User", back_populates="llm_roles")
    conversations = relationship("Conversation", back_populates="role")
```

## 6. API 设计

### 6.1 认证 API

- `POST /api/auth/register`：注册新用户
- `POST /api/auth/login`：用户登录
- `GET /api/auth/me`：获取当前用户信息

### 6.2 笔记 API

- `POST /api/notes/`：创建新笔记
- `GET /api/notes/`：获取笔记列表
- `GET /api/notes/{note_id}`：获取单个笔记
- `PUT /api/notes/{note_id}`：更新笔记
- `DELETE /api/notes/{note_id}`：删除笔记

### 6.3 大模型 API

- `POST /api/llm/analyze`：使用大模型分析文本
- `POST /api/llm/generate`：使用大模型生成文本
- `POST /api/llm/summarize`：使用大模型生成摘要
- `POST /api/llm/extract-keywords`：使用大模型提取关键词
- `POST /api/llm/analyze-database`：使用大模型分析数据库内容
- `GET /api/llm/models`：获取可用的大模型列表

### 6.4 大模型配置 API

- `POST /api/llm-config/providers`：创建新的LLM供应商
- `GET /api/llm-config/providers`：获取LLM供应商列表
- `GET /api/llm-config/providers/{provider_id}`：获取单个LLM供应商
- `PUT /api/llm-config/providers/{provider_id}`：更新LLM供应商
- `DELETE /api/llm-config/providers/{provider_id}`：删除LLM供应商
- `POST /api/llm-config/models`：创建新的LLM模型
- `GET /api/llm-config/models`：获取LLM模型列表
- `GET /api/llm-config/models/{model_id}`：获取单个LLM模型
- `PUT /api/llm-config/models/{model_id}`：更新LLM模型
- `DELETE /api/llm-config/models/{model_id}`：删除LLM模型
- `POST /api/llm-config/roles`：创建新的LLM角色
- `GET /api/llm-config/roles`：获取LLM角色列表
- `GET /api/llm-config/roles/{role_id}`：获取单个LLM角色
- `PUT /api/llm-config/roles/{role_id}`：更新LLM角色
- `DELETE /api/llm-config/roles/{role_id}`：删除LLM角色

## 7. 部署

项目使用 Docker 进行部署，包括以下组件：

1. **后端服务**：FastAPI 应用
2. **数据库**：PostgreSQL
3. **前端**：React 应用（单独的容器）

## 8. 测试

项目使用 pytest 进行测试，包括以下类型的测试：

1. **单元测试**：测试单个函数或类
2. **集成测试**：测试多个组件的交互
3. **API 测试**：测试 API 端点

## 9. 安全

项目实现了以下安全措施：

1. **密码哈希**：使用 bcrypt 算法哈希密码
2. **JWT 认证**：使用 JWT 进行用户认证
3. **HTTPS**：使用 HTTPS 加密通信
4. **CORS**：配置 CORS 策略，限制跨域请求
5. **API 密钥加密**：使用加密算法保护 API 密钥

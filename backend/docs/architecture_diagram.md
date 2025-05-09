# Kortex 项目架构图

## 系统架构图

```
+----------------------------------+
|           客户端                  |
|  +---------------------------+   |
|  |        React 前端         |   |
|  +---------------------------+   |
+----------------------------------+
              |
              | HTTP/HTTPS
              |
+----------------------------------+
|           后端服务                |
|  +---------------------------+   |
|  |      FastAPI 应用         |   |
|  |                           |   |
|  |  +---------------------+  |   |
|  |  |      API 层         |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  |   路由定义     |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  |   依赖项      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  |   中间件      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  +---------------------+  |   |
|  |                           |   |
|  |  +---------------------+  |   |
|  |  |      服务层         |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | 认证服务      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | 笔记服务      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | 数据库服务    |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | LLM服务      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  +---------------------+  |   |
|  |                           |   |
|  |  +---------------------+  |   |
|  |  |      模型层         |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | 领域模型      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |                     |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  | API模型      |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  +---------------------+  |   |
|  +---------------------------+   |
+----------------------------------+
              |
              | SQL
              |
+----------------------------------+
|           数据库                  |
|  +---------------------------+   |
|  |      PostgreSQL          |   |
|  +---------------------------+   |
+----------------------------------+
              |
              | API
              |
+----------------------------------+
|           外部服务                |
|  +---------------------------+   |
|  |      LLM API             |   |
|  |  (OpenAI, Anthropic等)    |   |
|  +---------------------------+   |
+----------------------------------+
```

## 数据流图

```
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
|   用户界面   | --> |   API层     | --> |   服务层    |
|             |     |             |     |             |
+-------------+     +-------------+     +-------------+
                                              |
                                              v
                    +-------------+     +-------------+
                    |             |     |             |
                    |   模型层    | <-- |  数据访问层  |
                    |             |     |             |
                    +-------------+     +-------------+
                                              |
                                              v
                                        +-------------+
                                        |             |
                                        |   数据库    |
                                        |             |
                                        +-------------+
```

## 模块依赖图

```
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
|   API层     | --> |   服务层    | --> |  数据访问层  |
|             |     |             |     |             |
+-------------+     +-------------+     +-------------+
      |                   |                   |
      |                   |                   |
      v                   v                   v
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
|  依赖项     |     |   工具函数   |     |   模型层    |
|             |     |             |     |             |
+-------------+     +-------------+     +-------------+
                                              |
                                              v
                                        +-------------+
                                        |             |
                                        |   配置      |
                                        |             |
                                        +-------------+
```

## 数据模型关系图

```
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
|    用户     | --> |    笔记     | --> |    对话     |
|             |     |             |     |             |
+-------------+     +-------------+     +-------------+
      |                   |                   |
      |                   |                   |
      v                   v                   v
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
| LLM供应商   |     |   数据库    |     |  LLM角色    |
|             |     |             |     |             |
+-------------+     +-------------+     +-------------+
      |                   |                   |
      |                   |                   |
      v                   v                   |
+-------------+     +-------------+           |
|             |     |             |           |
|  LLM模型    |     |    表格     |           |
|             |     |             |           |
+-------------+     +-------------+           |
      |                   |                   |
      |                   |                   |
      v                   v                   |
+-------------+     +-------------+           |
|             |     |             |           |
|  API密钥    |     |    列       |           |
|             |     |             |           |
+-------------+     +-------------+           |
                                              |
                                              v
                                        +-------------+
                                        |             |
                                        |   消息      |
                                        |             |
                                        +-------------+
```

## 部署架构图

```
+----------------------------------+
|         Docker Compose           |
|                                  |
|  +-------------+  +------------+ |
|  |             |  |            | |
|  |  前端容器   |  |  后端容器  | |
|  |  (React)    |  |  (FastAPI) | |
|  |             |  |            | |
|  +-------------+  +------------+ |
|                                  |
|  +---------------------------+   |
|  |                           |   |
|  |       数据库容器           |   |
|  |      (PostgreSQL)         |   |
|  |                           |   |
|  +---------------------------+   |
|                                  |
+----------------------------------+
```

这些架构图提供了对项目结构、数据流、模块依赖关系和部署架构的直观理解。

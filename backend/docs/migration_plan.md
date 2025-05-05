# Kortex 项目架构迁移计划

## 1. 迁移目标

将项目从当前的单文件式架构迁移到模块化架构，提高代码的可维护性和可扩展性。

## 2. 迁移策略

采用渐进式迁移策略，分阶段进行迁移，确保每个阶段都能正常工作。

## 3. 迁移阶段

### 阶段1：准备工作

1. **创建新的目录结构**
   - 创建 `api/dependencies`、`api/endpoints`、`api/middleware` 目录
   - 创建 `models/domain`、`models/schemas` 目录
   - 创建 `services` 目录
   - 创建 `tests` 目录

2. **创建基础文件**
   - 创建 `__init__.py` 文件
   - 创建 `main_new.py` 文件
   - 创建 `api/router.py` 文件

### 阶段2：模型迁移

1. **迁移数据库模型**
   - 将 `models/db_models.py` 中的模型拆分到 `models/domain/` 目录下的多个文件中
   - 创建 `models/domain/base.py` 文件，定义基础模型类
   - 创建 `models/domain/user.py` 文件，定义用户模型
   - 创建 `models/domain/note.py` 文件，定义笔记模型
   - 创建 `models/domain/database.py` 文件，定义数据库模型
   - 创建 `models/domain/llm.py` 文件，定义LLM相关模型

2. **迁移API模型**
   - 将 `models/schemas.py` 中的模型拆分到 `models/schemas/` 目录下的多个文件中
   - 创建 `models/schemas/user.py` 文件，定义用户相关的API模型
   - 创建 `models/schemas/note.py` 文件，定义笔记相关的API模型
   - 创建 `models/schemas/database.py` 文件，定义数据库相关的API模型
   - 创建 `models/schemas/llm.py` 文件，定义LLM相关的API模型
   - 创建 `models/schemas/token.py` 文件，定义认证相关的API模型

### 阶段3：服务层迁移

1. **迁移认证服务**
   - 创建 `services/auth_service.py` 文件，实现认证相关的业务逻辑

2. **迁移笔记服务**
   - 创建 `services/note_service.py` 文件，实现笔记相关的业务逻辑

3. **迁移数据库服务**
   - 创建 `services/database_service.py` 文件，实现数据库相关的业务逻辑

4. **迁移LLM服务**
   - 创建 `services/llm_service.py` 文件，实现LLM相关的业务逻辑
   - 创建 `services/llm_config_service.py` 文件，实现LLM配置相关的业务逻辑
   - 创建 `services/conversation_service.py` 文件，实现对话相关的业务逻辑

### 阶段4：API层迁移

1. **迁移依赖项**
   - 创建 `api/dependencies/database.py` 文件，实现数据库会话依赖项
   - 创建 `api/dependencies/auth.py` 文件，实现认证依赖项

2. **迁移路由**
   - 创建 `api/endpoints/auth.py` 文件，实现认证相关的路由
   - 创建 `api/endpoints/notes.py` 文件，实现笔记相关的路由
   - 创建 `api/endpoints/databases.py` 文件，实现数据库相关的路由
   - 创建 `api/endpoints/llm.py` 文件，实现LLM相关的路由
   - 创建 `api/endpoints/llm_config.py` 文件，实现LLM配置相关的路由
   - 创建 `api/endpoints/conversations.py` 文件，实现对话相关的路由

3. **迁移中间件**
   - 创建 `api/middleware/logging.py` 文件，实现日志中间件

### 阶段5：主应用迁移

1. **更新主应用入口**
   - 更新 `main_new.py` 文件，使用新的模块化架构
   - 注册路由
   - 配置中间件
   - 配置数据库初始化

### 阶段6：测试和验证

1. **编写测试**
   - 创建 `tests/conftest.py` 文件，配置测试环境
   - 创建 `tests/test_auth.py` 文件，测试认证功能
   - 创建 `tests/test_notes.py` 文件，测试笔记功能
   - 创建 `tests/test_llm.py` 文件，测试LLM功能

2. **运行测试**
   - 运行单元测试
   - 运行集成测试
   - 运行API测试

### 阶段7：部署配置更新

1. **更新Docker配置**
   - 更新 `Dockerfile`，使用新的主应用入口
   - 更新 `docker-compose.yml`，配置服务依赖关系

2. **更新启动脚本**
   - 更新 `start_backend.sh`，使用新的主应用入口

## 4. 迁移注意事项

1. **保持兼容性**
   - 确保API接口保持兼容性，避免破坏前端功能
   - 保留旧的路由，直到新的路由完全测试通过

2. **数据库迁移**
   - 确保数据库模型变更不会导致数据丢失
   - 使用数据库迁移工具（如Alembic）管理数据库变更

3. **测试覆盖**
   - 确保测试覆盖所有关键功能
   - 编写自动化测试，确保迁移过程中不会引入新的bug

4. **文档更新**
   - 更新API文档，反映新的架构
   - 更新开发文档，说明新的开发流程

## 5. 回滚计划

如果迁移过程中出现问题，可以采取以下回滚措施：

1. **保留旧代码**
   - 保留旧的代码，直到新的代码完全测试通过
   - 使用版本控制系统（如Git）管理代码变更

2. **数据库备份**
   - 在迁移前备份数据库
   - 如果数据库迁移失败，可以恢复备份

3. **分阶段部署**
   - 分阶段部署新的架构，确保每个阶段都能正常工作
   - 如果某个阶段出现问题，可以回滚到上一个阶段

## 6. 迁移时间表

| 阶段 | 任务 | 预计时间 | 负责人 |
| --- | --- | --- | --- |
| 阶段1 | 准备工作 | 1天 | 开发团队 |
| 阶段2 | 模型迁移 | 2天 | 开发团队 |
| 阶段3 | 服务层迁移 | 3天 | 开发团队 |
| 阶段4 | API层迁移 | 3天 | 开发团队 |
| 阶段5 | 主应用迁移 | 1天 | 开发团队 |
| 阶段6 | 测试和验证 | 2天 | 测试团队 |
| 阶段7 | 部署配置更新 | 1天 | 运维团队 |

总计：约2周时间

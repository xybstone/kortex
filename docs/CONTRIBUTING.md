# 贡献指南

感谢您对Kortex项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 代码贡献
- 文档改进
- 问题报告
- 功能建议
- 代码审查

## 开发环境设置

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

4. 设置数据库
   ```bash
   # 创建PostgreSQL数据库
   createdb kortex
   
   # 运行数据库迁移
   cd ../backend
   alembic upgrade head
   ```

5. 启动开发服务器
   ```bash
   # 后端
   cd ../backend
   uvicorn main:app --reload
   
   # 前端（在另一个终端）
   cd ../frontend
   npm run dev
   ```

## 代码风格

- 后端代码遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)规范
- 前端代码使用[Prettier](https://prettier.io/)格式化
- 提交前请运行代码格式化和lint检查

## 提交流程

1. 创建一个新分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 进行更改并提交
   ```bash
   git add .
   git commit -m "描述你的更改"
   ```

3. 推送到你的分支
   ```bash
   git push origin feature/your-feature-name
   ```

4. 创建Pull Request
   - 前往GitHub仓库页面
   - 点击"New Pull Request"
   - 选择你的分支
   - 填写PR描述，包括更改内容和原因

## 问题报告

如果您发现了问题，请在GitHub Issues中报告，并包含以下信息：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、浏览器、Python版本等）
- 相关截图（如适用）

## 功能建议

如果您有功能建议，请在GitHub Issues中提出，并包含以下信息：

- 功能描述
- 使用场景
- 预期行为
- 可能的实现方式（如有）

## 代码审查

所有代码贡献都需要通过代码审查。请确保您的代码：

- 遵循项目的代码风格
- 包含适当的测试
- 文档完善
- 解决了特定问题或实现了特定功能

## 许可证

通过贡献代码，您同意您的贡献将在项目的MIT许可证下发布。

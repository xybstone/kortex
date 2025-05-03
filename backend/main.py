from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由模块
from backend.api.routes import auth_simple
from backend.api.routes import llm_config
from backend.api.routes import conversations

app = FastAPI(
    title="Kortex API",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_simple.router, prefix="/api/auth", tags=["认证"])
app.include_router(llm_config.router, prefix="/api/llm-config", tags=["大模型配置"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["对话"])

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

@app.get("/api/notes")
async def get_notes():
    """获取笔记列表"""
    return {"message": "笔记列表功能尚未实现"}

@app.get("/api/databases")
async def get_databases():
    """获取数据库列表"""
    return {"message": "数据库列表功能尚未实现"}

@app.get("/api/llm/status")
async def get_llm_status():
    """获取大模型状态"""
    return {"status": "可用", "model": "gpt-3.5-turbo"}

@app.get("/api/llm-config/providers")
async def get_providers():
    """获取大模型供应商列表（模拟数据）"""
    return [
        {"id": 1, "name": "OpenAI", "description": "OpenAI API", "base_url": "https://api.openai.com/v1"},
        {"id": 2, "name": "Anthropic", "description": "Anthropic Claude API", "base_url": "https://api.anthropic.com"},
        {"id": 3, "name": "Gemini", "description": "Google Gemini API", "base_url": "https://generativelanguage.googleapis.com"}
    ]

@app.get("/api/llm-config/models")
async def get_models():
    """获取大模型列表（模拟数据）"""
    return [
        {"id": 1, "name": "gpt-4", "provider_id": 1, "api_key": "***********", "is_active": True, "max_tokens": 8192, "temperature": 0.7},
        {"id": 2, "name": "gpt-3.5-turbo", "provider_id": 1, "api_key": "***********", "is_active": True, "max_tokens": 4096, "temperature": 0.7},
        {"id": 3, "name": "claude-3-opus", "provider_id": 2, "api_key": "***********", "is_active": True, "max_tokens": 100000, "temperature": 0.7}
    ]

@app.get("/api/llm-config/roles")
async def get_roles():
    """获取大模型角色列表（模拟数据）"""
    return [
        {"id": 1, "name": "通用助手", "description": "通用AI助手", "system_prompt": "你是一个有用的AI助手。", "model_id": 1, "is_default": True},
        {"id": 2, "name": "程序员", "description": "编程助手", "system_prompt": "你是一个专业的程序员，擅长解决编程问题。", "model_id": 1, "is_default": False},
        {"id": 3, "name": "写作助手", "description": "写作辅助", "system_prompt": "你是一个专业的写作助手，擅长文学创作和文章润色。", "model_id": 2, "is_default": True}
    ]

@app.get("/api/auth/status")
async def get_auth_status():
    """获取认证状态"""
    return {"status": "未登录"}

@app.get("/api/conversations/note/{note_id}")
async def get_note_conversations(note_id: int):
    """获取笔记的对话列表（模拟数据）"""
    conversations = [
        {"id": 1, "note_id": 1, "role_id": 1, "created_at": "2023-05-10T10:00:00Z", "updated_at": "2023-05-10T10:02:00Z"},
        {"id": 2, "note_id": 1, "role_id": 3, "created_at": "2023-05-11T14:00:00Z", "updated_at": "2023-05-11T14:02:00Z"}
    ]
    return [c for c in conversations if c["note_id"] == note_id]

@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int):
    """获取对话的消息列表（模拟数据）"""
    messages = {
        1: [
            {"id": 1, "conversation_id": 1, "content": "你好，我是通用助手，有什么可以帮助你的？", "role": "assistant", "created_at": "2023-05-10T10:00:00Z"},
            {"id": 2, "conversation_id": 1, "content": "我想了解一下人工智能的基础知识", "role": "user", "created_at": "2023-05-10T10:01:00Z"},
            {"id": 3, "conversation_id": 1, "content": "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n主要的AI领域包括：\n\n1. **机器学习** - 使计算机能够从数据中学习，而无需明确编程\n2. **深度学习** - 使用神经网络进行复杂模式识别\n3. **自然语言处理** - 使计算机能够理解和生成人类语言\n4. **计算机视觉** - 使计算机能够解释和理解视觉信息\n\n人工智能已经在许多领域找到了应用，包括医疗保健、金融、制造业和客户服务等。", "role": "assistant", "created_at": "2023-05-10T10:02:00Z"}
        ],
        2: [
            {"id": 4, "conversation_id": 2, "content": "你好，我是写作助手，有什么可以帮助你的？", "role": "assistant", "created_at": "2023-05-11T14:00:00Z"},
            {"id": 5, "conversation_id": 2, "content": "我需要写一篇关于环保的文章，有什么建议？", "role": "user", "created_at": "2023-05-11T14:01:00Z"},
            {"id": 6, "conversation_id": 2, "content": "为了写一篇关于环保的文章，我建议以下结构和内容：\n\n## 标题\n**\"保护地球，从我做起：日常生活中的环保实践\"**\n\n## 引言\n- 简述当前环境面临的挑战\n- 强调个人行动的重要性\n- 提出文章的主要目的：分享实用的环保方法\n\n## 主体部分\n\n### 1. 减少塑料使用\n- 使用可重复使用的购物袋\n- 避免一次性塑料制品\n- 选择无塑料包装的产品\n\n### 2. 节约能源\n- 使用节能灯具和电器\n- 合理设置空调温度\n- 不用时关闭电器电源\n\n### 3. 水资源保护\n- 修复漏水的水龙头\n- 收集雨水用于浇花\n- 减少洗澡时间\n\n### 4. 垃圾分类与回收\n- 学习正确的垃圾分类方法\n- 将可回收物品送去回收\n- 尝试堆肥厨余垃圾\n\n### 5. 绿色出行\n- 使用公共交通工具\n- 骑自行车或步行\n- 考虑拼车或电动汽车\n\n## 结论\n- 总结环保行动的集体影响\n- 鼓励读者从小事做起\n- 展望更可持续的未来\n\n希望这个框架对你有所帮助！", "role": "assistant", "created_at": "2023-05-11T14:02:00Z"}
        ]
    }
    return messages.get(conversation_id, [])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

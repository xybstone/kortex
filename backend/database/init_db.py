from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database.session import SessionLocal, engine
from models.domain import BaseModel, User, LLMProvider, LLMModel, LLMRole
from utils.security import encrypt_text

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def init_db() -> None:
    """初始化数据库"""
    # 创建表
    BaseModel.metadata.create_all(bind=engine, checkfirst=True)
    print("已初始化数据库表")

    # 获取数据库会话
    db = SessionLocal()
    try:
        # 创建默认用户
        create_default_user(db)

        # 创建默认LLM供应商
        create_default_providers(db)

        # 创建默认LLM模型
        create_default_models(db)

        # 创建默认LLM角色
        create_default_roles(db)
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
    finally:
        db.close()

def create_default_user(db: Session) -> None:
    """创建默认用户"""
    # 检查是否已存在用户
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        # 创建默认用户
        hashed_password = get_password_hash("password")
        default_user = User(
            email="user@example.com",
            full_name="测试用户",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True  # 默认用户是管理员
        )
        db.add(default_user)
        db.commit()
        print("已创建默认用户: user@example.com")

def create_default_providers(db: Session) -> None:
    """创建默认LLM供应商"""
    # 默认供应商列表
    default_providers = [
        {
            "name": "OpenAI",
            "description": "OpenAI API",
            "base_url": "https://api.openai.com/v1",
            "is_public": True
        },
        {
            "name": "Anthropic",
            "description": "Anthropic Claude API",
            "base_url": "https://api.anthropic.com",
            "is_public": True
        },
        {
            "name": "Gemini",
            "description": "Google Gemini API",
            "base_url": "https://generativelanguage.googleapis.com",
            "is_public": True
        },
        {
            "name": "DeepSeek",
            "description": "DeepSeek AI API",
            "base_url": "https://api.deepseek.com",
            "is_public": True
        }
    ]

    # 检查并创建供应商
    for provider_data in default_providers:
        provider = db.query(LLMProvider).filter(LLMProvider.name == provider_data["name"]).first()
        if not provider:
            provider = LLMProvider(**provider_data)
            db.add(provider)
            db.commit()
            print(f"已创建默认供应商: {provider_data['name']}")

def create_default_models(db: Session) -> None:
    """创建默认LLM模型"""
    # 获取供应商
    openai = db.query(LLMProvider).filter(LLMProvider.name == "OpenAI").first()
    anthropic = db.query(LLMProvider).filter(LLMProvider.name == "Anthropic").first()
    deepseek = db.query(LLMProvider).filter(LLMProvider.name == "DeepSeek").first()

    if not openai or not anthropic or not deepseek:
        print("无法创建默认模型：缺少供应商")
        return

    # 默认模型列表
    default_models = [
        {
            "name": "gpt-4",
            "provider_id": openai.id,
            "api_key": encrypt_text("sk-***********"),
            "is_active": True,
            "is_public": True,
            "max_tokens": 8192,
            "temperature": 0.7
        },
        {
            "name": "gpt-3.5-turbo",
            "provider_id": openai.id,
            "api_key": encrypt_text("sk-***********"),
            "is_active": True,
            "is_public": True,
            "max_tokens": 4096,
            "temperature": 0.7
        },
        {
            "name": "claude-3-opus",
            "provider_id": anthropic.id,
            "api_key": encrypt_text("sk_ant-***********"),
            "is_active": True,
            "is_public": True,
            "max_tokens": 100000,
            "temperature": 0.7
        },
        {
            "name": "deepseek-chat",
            "provider_id": deepseek.id,
            "api_key": encrypt_text("sk-***********"),
            "is_active": True,
            "is_public": True,
            "max_tokens": 4096,
            "temperature": 0.7
        },
        {
            "name": "deepseek-reasoner",
            "provider_id": deepseek.id,
            "api_key": encrypt_text("sk-***********"),
            "is_active": True,
            "is_public": True,
            "max_tokens": 4096,
            "temperature": 0.7
        }
    ]

    # 检查并创建模型
    for model_data in default_models:
        model = db.query(LLMModel).filter(
            LLMModel.name == model_data["name"],
            LLMModel.provider_id == model_data["provider_id"]
        ).first()
        if not model:
            model = LLMModel(**model_data)
            db.add(model)
            db.commit()
            print(f"已创建默认模型: {model_data['name']}")

def create_default_roles(db: Session) -> None:
    """创建默认LLM角色"""
    # 获取模型
    gpt4 = db.query(LLMModel).filter(LLMModel.name == "gpt-4").first()
    gpt35 = db.query(LLMModel).filter(LLMModel.name == "gpt-3.5-turbo").first()
    claude = db.query(LLMModel).filter(LLMModel.name == "claude-3-opus").first()
    deepseek_chat = db.query(LLMModel).filter(LLMModel.name == "deepseek-chat").first()
    deepseek_reasoner = db.query(LLMModel).filter(LLMModel.name == "deepseek-reasoner").first()

    if not gpt4 or not gpt35 or not claude or not deepseek_chat or not deepseek_reasoner:
        print("无法创建默认角色：缺少模型")
        return

    # 默认角色列表
    default_roles = [
        {
            "name": "通用助手",
            "description": "通用AI助手",
            "system_prompt": "你是一个有用的AI助手。",
            "model_id": gpt4.id,
            "is_default": True,
            "is_public": True
        },
        {
            "name": "程序员",
            "description": "编程助手",
            "system_prompt": "你是一个专业的程序员，擅长解决编程问题。",
            "model_id": gpt4.id,
            "is_default": False,
            "is_public": True
        },
        {
            "name": "写作助手",
            "description": "写作辅助",
            "system_prompt": "你是一个专业的写作助手，擅长文学创作和文章润色。",
            "model_id": gpt35.id,
            "is_default": True,
            "is_public": True
        },
        {
            "name": "默认助手",
            "description": "DeepSeek 默认助手",
            "system_prompt": "你是由DeepSeek AI开发的智能助手，可以回答用户的各种问题并提供帮助。",
            "model_id": deepseek_chat.id,
            "is_default": True,
            "is_public": True
        },
        {
            "name": "推理助手",
            "description": "DeepSeek 推理助手",
            "system_prompt": "你是由DeepSeek AI开发的推理助手，擅长分析问题并提供详细的推理过程。",
            "model_id": deepseek_reasoner.id,
            "is_default": True,
            "is_public": True
        }
    ]

    # 检查并创建角色
    for role_data in default_roles:
        role = db.query(LLMRole).filter(
            LLMRole.name == role_data["name"],
            LLMRole.model_id == role_data["model_id"]
        ).first()
        if not role:
            role = LLMRole(**role_data)
            db.add(role)
            db.commit()
            print(f"已创建默认角色: {role_data['name']}")

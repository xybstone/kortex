#!/usr/bin/env python
"""
添加DeepSeek提供商和模型到数据库
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir.parent))

# 设置环境变量
os.environ["IS_DOCKER"] = "false"

from sqlalchemy.orm import Session
try:
    # 尝试使用相对导入
    from database.session import SessionLocal
    from models.models import LLMProvider, LLMModel, LLMRole, User
except ImportError:
    # 尝试使用绝对导入
    from backend.database.session import SessionLocal
    from backend.models.models import LLMProvider, LLMModel, LLMRole, User

def add_deepseek_provider():
    """添加DeepSeek提供商和模型到数据库"""
    db = SessionLocal()
    try:
        # 检查是否已存在DeepSeek提供商
        existing_provider = db.query(LLMProvider).filter(LLMProvider.name == "DeepSeek").first()
        if existing_provider:
            print("DeepSeek提供商已存在，ID:", existing_provider.id)
            provider_id = existing_provider.id
        else:
            # 获取管理员用户
            admin_user = db.query(User).filter(User.is_admin == True).first()
            if not admin_user:
                print("错误: 未找到管理员用户")
                return

            # 创建DeepSeek提供商
            deepseek_provider = LLMProvider(
                name="DeepSeek",
                description="DeepSeek AI API",
                base_url="https://api.deepseek.com",
                user_id=admin_user.id,
                is_public=True
            )
            db.add(deepseek_provider)
            db.commit()
            db.refresh(deepseek_provider)
            print("已添加DeepSeek提供商，ID:", deepseek_provider.id)
            provider_id = deepseek_provider.id

        # 添加DeepSeek模型
        models_to_add = [
            {
                "name": "deepseek-chat",
                "description": "DeepSeek Chat - 通用对话模型",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            {
                "name": "deepseek-reasoner",
                "description": "DeepSeek Reasoner - 推理增强模型",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        ]

        for model_data in models_to_add:
            # 检查模型是否已存在
            existing_model = db.query(LLMModel).filter(
                LLMModel.name == model_data["name"],
                LLMModel.provider_id == provider_id
            ).first()

            if existing_model:
                print(f"模型 {model_data['name']} 已存在，ID:", existing_model.id)
                model_id = existing_model.id
            else:
                # 创建模型
                new_model = LLMModel(
                    name=model_data["name"],
                    provider_id=provider_id,
                    user_id=admin_user.id,
                    is_active=True,
                    is_public=True,
                    max_tokens=model_data["max_tokens"],
                    temperature=model_data["temperature"]
                )
                db.add(new_model)
                db.commit()
                db.refresh(new_model)
                print(f"已添加模型 {model_data['name']}，ID:", new_model.id)
                model_id = new_model.id

            # 为每个模型添加默认角色
            role_name = "默认助手" if model_data["name"] == "deepseek-chat" else "推理助手"
            existing_role = db.query(LLMRole).filter(
                LLMRole.model_id == model_id,
                LLMRole.is_default == True
            ).first()

            if existing_role:
                print(f"模型 {model_data['name']} 的默认角色已存在")
            else:
                system_prompt = (
                    "你是由DeepSeek AI开发的智能助手，可以回答用户的各种问题并提供帮助。"
                    if model_data["name"] == "deepseek-chat" else
                    "你是由DeepSeek AI开发的推理助手，擅长分析问题并提供详细的推理过程。"
                )

                new_role = LLMRole(
                    name=role_name,
                    description=f"DeepSeek {role_name}",
                    system_prompt=system_prompt,
                    model_id=model_id,
                    user_id=admin_user.id,
                    is_default=True,
                    is_public=True
                )
                db.add(new_role)
                db.commit()
                print(f"已为模型 {model_data['name']} 添加默认角色")

        print("DeepSeek提供商和模型添加完成")

    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_deepseek_provider()

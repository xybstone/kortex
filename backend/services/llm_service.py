from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio

from models.domain.llm import LLMModel, LLMProvider
from models.schemas.llm import LLMRequest, LLMResponse, DatabaseAnalysisRequest
from utils.security import decrypt_text

# 模拟LLM响应
async def analyze_text(db: Session, request: LLMRequest) -> LLMResponse:
    """使用大模型分析文本（模拟）"""
    # 在实际应用中，这里会调用LLM API
    return LLMResponse(
        result=f"## 分析结果\n\n这段文本主要讨论了以下几个方面：\n\n1. 主题：人工智能在现代社会的应用\n2. 观点：人工智能正在改变各个行业的工作方式\n3. 情感：中性，偏向积极\n\n### 关键观点\n\n- 人工智能技术正在快速发展\n- 各行各业都在采用AI解决方案\n- 需要关注AI的伦理问题",
        type="analysis"
    )

async def generate_text(db: Session, request: LLMRequest) -> LLMResponse:
    """使用大模型生成文本（模拟）"""
    # 在实际应用中，这里会调用LLM API
    return LLMResponse(
        result=f"# {request.content}\n\n人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n## 主要应用领域\n\n1. **医疗保健** - 疾病诊断、药物研发、个性化治疗\n2. **金融** - 风险评估、欺诈检测、算法交易\n3. **制造业** - 预测性维护、质量控制、供应链优化\n4. **客户服务** - 聊天机器人、个性化推荐、情感分析",
        type="generation"
    )

async def summarize_text(db: Session, request: LLMRequest) -> LLMResponse:
    """使用大模型生成摘要（模拟）"""
    # 在实际应用中，这里会调用LLM API
    return LLMResponse(
        result=f"## 摘要\n\n该文本讨论了人工智能的发展及其对社会的影响。主要观点包括AI技术正在各行业广泛应用，带来效率提升和创新，但也引发了关于隐私、就业和伦理的担忧。作者认为需要平衡技术进步与社会影响，建立适当的监管框架。",
        type="summary"
    )

async def extract_keywords(db: Session, request: LLMRequest) -> LLMResponse:
    """使用大模型提取关键词（模拟）"""
    # 在实际应用中，这里会调用LLM API
    return LLMResponse(
        result=["人工智能", "机器学习", "自动化", "效率提升", "技术创新", "伦理考量", "隐私保护", "就业影响", "监管框架", "社会变革"],
        type="keywords"
    )

async def analyze_database(
    db: Session,
    database_id: int,
    prompt: str,
    model_id: Optional[int] = None
) -> LLMResponse:
    """使用大模型分析数据库内容（模拟）"""
    # 在实际应用中，这里会调用LLM API
    return LLMResponse(
        result=f"## 数据库分析结果\n\n基于数据库ID {database_id}的分析：\n\n### 主要发现\n\n1. 销售趋势呈现季节性波动，第四季度表现最佳\n2. 客户满意度与产品质量高度相关\n3. 价格变动对销量的影响因产品类别而异\n\n### 建议\n\n- 增加第四季度的库存和营销预算\n- 重点关注产品质量改进\n- 针对不同产品类别制定差异化定价策略",
        type="database_analysis"
    )

async def get_available_models(db: Session) -> List[Dict[str, Any]]:
    """获取所有可用的大模型列表"""
    try:
        # 从数据库获取模型列表
        models = db.query(LLMModel).filter(LLMModel.is_active == True).all()

        # 转换为前端需要的格式
        result = []
        for model in models:
            provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
            provider_name = provider.name if provider else "未知"
            result.append({
                "id": model.id,
                "name": model.name,
                "provider": provider_name,
                "is_active": model.is_active
            })

        # 如果没有模型，返回默认模型列表
        if not result:
            result = [
                {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
                {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
                {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
                {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
            ]

        return result
    except Exception as e:
        # 如果出错，返回默认模型列表
        print(f"获取模型列表失败: {e}")
        return [
            {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
            {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
            {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
            {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
        ]

# 在实际应用中，这里会实现与各种LLM API的集成
# 例如：OpenAI、Anthropic Claude、Google Gemini等
# 以下是一个示例实现（未实际调用API）

async def chat_with_llm(
    db: Session,
    model_id: int,
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """与LLM进行对话"""
    try:
        # 获取模型信息
        model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
        if not model:
            # 如果找不到模型，返回默认响应
            return {
                "result": "抱歉，我无法处理您的请求，因为找不到指定的模型。",
                "type": "chat"
            }

        # 获取供应商信息
        provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
        if not provider:
            # 如果找不到供应商，返回默认响应
            return {
                "result": "抱歉，我无法处理您的请求，因为找不到模型的供应商信息。",
                "type": "chat"
            }

        # 获取API密钥
        api_key = model.api_key
        if api_key:
            # 解密API密钥
            try:
                api_key = decrypt_text(api_key)
            except Exception as e:
                print(f"解密API密钥失败: {e}")
                # 使用默认响应
                return {
                    "result": "抱歉，我无法处理您的请求，因为API密钥解密失败。",
                    "type": "chat"
                }

        # 如果API密钥为空，尝试使用环境变量中的API密钥
        if not api_key:
            print(f"模型 {model.name} 没有配置API密钥，尝试使用环境变量中的API密钥")
            # 这里可以添加从环境变量获取API密钥的逻辑
            return {
                "result": "抱歉，模型没有配置API密钥。请在模型配置中添加API密钥。",
                "type": "chat"
            }

        # 提取用户最后一条消息作为prompt（用于日志记录）
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            return {
                "result": "请先发送一条消息。",
                "type": "chat"
            }

        last_user_message = user_messages[-1]["content"]
        print(f"处理用户消息: {last_user_message[:50]}...")

        # 根据不同的供应商调用相应的API
        provider_name = provider.name.lower()
        model_name = model.name.lower()

        # 获取模型参数
        max_tokens = model.max_tokens or 4096
        temperature = model.temperature or 0.7

        # 获取API基础URL
        api_base = provider.base_url

        print(f"调用LLM API: 供应商={provider_name}, 模型={model_name}, API基础URL={api_base}")

        # 根据不同的供应商调用不同的API
        if provider_name == "openai":
            # 调用OpenAI API
            import openai

            # 配置OpenAI客户端
            client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base or "https://api.openai.com/v1"
            )

            # 调用API
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model.name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 提取响应内容
            result = response.choices[0].message.content

        elif provider_name == "anthropic":
            # 调用Anthropic API
            import anthropic

            # 配置Anthropic客户端
            client = anthropic.Anthropic(
                api_key=api_key,
                base_url=api_base or "https://api.anthropic.com"
            )

            # 转换消息格式
            anthropic_messages = []
            for msg in messages:
                role = msg["role"]
                # Anthropic只支持user和assistant角色，将system消息作为user消息处理
                if role == "system":
                    role = "user"
                anthropic_messages.append({"role": role, "content": msg["content"]})

            # 调用API
            response = await asyncio.to_thread(
                client.messages.create,
                model=model.name,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 提取响应内容
            result = response.content[0].text

        elif provider_name == "deepseek":
            # 调用DeepSeek API
            import requests

            # 准备请求头和数据
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model.name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # 调用API - 根据官方文档，正确的端点是 /chat/completions
            endpoint = "/chat/completions"
            base_url = api_base or "https://api.deepseek.com"
            # 确保base_url不以/结尾，endpoint以/开头
            if base_url.endswith("/"):
                base_url = base_url[:-1]
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            full_url = f"{base_url}{endpoint}"
            print(f"调用DeepSeek API，完整URL: {full_url}")

            # 调用API
            response = await asyncio.to_thread(
                requests.post,
                full_url,
                headers=headers,
                json=data
            )

            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"DeepSeek API调用失败: {response.status_code} {response.text}"
                print(error_msg)
                return {
                    "result": f"抱歉，调用DeepSeek API时出错: {error_msg}",
                    "type": "chat"
                }

            # 提取响应内容
            response_json = response.json()
            result = response_json["choices"][0]["message"]["content"]

        else:
            # 不支持的供应商
            return {
                "result": f"抱歉，不支持的供应商: {provider.name}",
                "type": "chat"
            }

        print(f"LLM响应成功，响应长度: {len(result)}")

        return {
            "result": result,
            "type": "chat"
        }
    except Exception as e:
        error_msg = str(e)
        print(f"与LLM对话时出错: {error_msg}")
        return {
            "result": f"抱歉，处理您的请求时出现了错误: {error_msg}",
            "type": "chat"
        }

async def call_llm_api(
    model_name: str,
    provider_name: str,
    api_key: str,
    prompt: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    api_base: str = None
) -> str:
    """调用LLM API"""
    try:
        print(f"调用LLM API: 供应商={provider_name}, 模型={model_name}, 提示长度={len(prompt)}")

        # 准备消息格式
        messages = [{"role": "user", "content": prompt}]

        # 根据不同的供应商调用不同的API
        provider_name = provider_name.lower()

        if provider_name == "openai":
            # 调用OpenAI API
            import openai

            # 配置OpenAI客户端
            client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base or "https://api.openai.com/v1"
            )

            # 调用API
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 提取响应内容
            result = response.choices[0].message.content

        elif provider_name == "anthropic":
            # 调用Anthropic API
            import anthropic

            # 配置Anthropic客户端
            client = anthropic.Anthropic(
                api_key=api_key,
                base_url=api_base or "https://api.anthropic.com"
            )

            # 调用API
            response = await asyncio.to_thread(
                client.messages.create,
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 提取响应内容
            result = response.content[0].text

        elif provider_name == "deepseek":
            # 调用DeepSeek API
            import requests

            # 准备请求头和数据
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # 调用API - 根据官方文档，正确的端点是 /chat/completions
            endpoint = "/chat/completions"
            base_url = api_base or "https://api.deepseek.com"
            # 确保base_url不以/结尾，endpoint以/开头
            if base_url.endswith("/"):
                base_url = base_url[:-1]
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            full_url = f"{base_url}{endpoint}"
            print(f"调用DeepSeek API，完整URL: {full_url}")

            # 调用API
            response = await asyncio.to_thread(
                requests.post,
                full_url,
                headers=headers,
                json=data
            )

            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"DeepSeek API调用失败: {response.status_code} {response.text}"
                print(error_msg)
                return f"调用DeepSeek API时出错: {error_msg}"

            # 提取响应内容
            response_json = response.json()
            result = response_json["choices"][0]["message"]["content"]

        else:
            # 不支持的供应商
            return f"不支持的供应商: {provider_name}"

        print(f"LLM响应成功，响应长度: {len(result)}")
        return result

    except Exception as e:
        error_msg = str(e)
        print(f"调用LLM API时出错: {error_msg}")
        return f"调用LLM API时出错: {error_msg}"

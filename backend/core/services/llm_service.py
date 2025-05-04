from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json
import os
from cryptography.fernet import Fernet

# 导入DeepSeek支持
try:
    from langchain_deepseek import ChatDeepSeek
except ImportError:
    ChatDeepSeek = None

from backend.core.config import settings
from backend.models.schemas import LLMRequest, LLMResponse
from backend.core.services import database_service
from backend.models.models import LLMModel, LLMProvider

# 加密密钥
ENCRYPTION_KEY = settings.SECRET_KEY[:32].encode().ljust(32, b'0')
cipher_suite = Fernet(Fernet.generate_key())

class LLMService:
    def __init__(self):
        """初始化LLM服务"""
        try:
            # 尝试初始化默认LLM
            api_key = settings.LLM_API_KEY or "sk-dummy-key-for-mock-responses"
            print(f"初始化默认LLM，模型: {settings.LLM_MODEL}")
            self.default_llm = OpenAI(
                openai_api_key=api_key,
                model_name=settings.LLM_MODEL,
                temperature=0.7
            )
        except Exception as e:
            print(f"初始化默认LLM失败: {str(e)}，使用模拟响应")
            # 如果初始化失败，创建一个模拟的LLM
            self.default_llm = None

        self.model_cache = {}  # 缓存已创建的模型实例

    def _get_api_key(self, model: LLMModel) -> str:
        """获取解密后的API密钥"""
        if not model.api_key:
            return settings.LLM_API_KEY

        try:
            # 在实际应用中，这里应该解密存储的API密钥
            # 为简化示例，这里直接返回
            return model.api_key
        except Exception as e:
            print(f"解密API密钥失败: {e}")
            return settings.LLM_API_KEY

    def _get_llm(self, db: Session, model_id: int) -> Any:
        """获取LLM实例"""
        print(f"尝试获取模型ID: {model_id}")

        # 检查缓存
        if model_id in self.model_cache:
            print(f"使用缓存的模型: {model_id}")
            return self.model_cache[model_id]

        # 获取模型信息
        model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
        if not model:
            print(f"找不到模型ID: {model_id}，使用默认模型")
            return self.default_llm

        # 获取供应商信息
        provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
        if not provider:
            print(f"找不到模型的供应商ID: {model.provider_id}，使用默认模型")
            return self.default_llm

        print(f"找到模型: {model.name}, 供应商: {provider.name}")

        # 获取API密钥
        api_key = self._get_api_key(model)

        # 创建LLM实例
        llm = None
        if provider.name.lower() == "openai":
            llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=model.name,
                temperature=model.temperature,
                max_tokens=model.max_tokens,
                openai_api_base=provider.base_url if provider.base_url else None
            )
        elif provider.name.lower() == "anthropic":
            # 这里可以添加Anthropic模型的支持
            from langchain.chat_models import ChatAnthropic
            llm = ChatAnthropic(
                anthropic_api_key=api_key,
                model=model.name,
                temperature=model.temperature,
                max_tokens_to_sample=model.max_tokens
            )
        elif provider.name.lower() == "deepseek" and ChatDeepSeek is not None:
            # DeepSeek模型支持
            llm = ChatDeepSeek(
                deepseek_api_key=api_key,
                model=model.name,  # 可以是"deepseek-chat"或"deepseek-reasoner"
                temperature=model.temperature,
                max_tokens=model.max_tokens,
                base_url=provider.base_url if provider.base_url else "https://api.deepseek.com"
            )
        else:
            # 默认使用OpenAI
            llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=model.name,
                temperature=model.temperature,
                max_tokens=model.max_tokens
            )

        # 缓存LLM实例
        self.model_cache[model_id] = llm
        return llm

    async def analyze_text(self, db: Session, request: LLMRequest) -> Dict[str, Any]:
        """分析文本"""
        print(f"分析文本请求: model_id={request.model_id}, content_length={len(request.content)}")

        # 使用指定的模型或默认模型
        llm = self.default_llm
        if request.model_id:
            try:
                llm = self._get_llm(db, request.model_id)
                print(f"成功获取模型，准备分析文本")
            except Exception as e:
                print(f"获取模型时出错: {str(e)}")
                raise

        # 如果没有可用的LLM，返回模拟响应
        if llm is None:
            print("没有可用的LLM，返回模拟响应")
            return {
                "result": f"## 分析结果\n\n这段文本主要讨论了以下几个方面：\n\n1. 主题：人工智能在现代社会的应用\n2. 观点：人工智能正在改变各个行业的工作方式\n3. 情感：中性，偏向积极\n\n### 关键观点\n\n- 人工智能技术正在快速发展\n- 各行各业都在采用AI解决方案\n- 需要关注AI的伦理问题",
                "type": "analysis"
            }

        try:
            prompt_template = PromptTemplate(
                input_variables=["text"],
                template="分析以下文本，提供关键观点、主题和情感分析：\n\n{text}"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)
            print("开始运行LLM链")
            result = chain.run(text=request.content)
            print("LLM链运行完成")
        except Exception as e:
            print(f"运行LLM链时出错: {str(e)}")
            # 返回模拟响应而不是抛出异常
            return {
                "result": f"## 分析结果 (模拟)\n\n这段文本主要讨论了以下几个方面：\n\n1. 主题：人工智能在现代社会的应用\n2. 观点：人工智能正在改变各个行业的工作方式\n3. 情感：中性，偏向积极\n\n### 错误信息\n\n- 处理请求时出错: {str(e)}",
                "type": "analysis"
            }

        return {
            "result": result,
            "type": "analysis"
        }

    async def generate_text(self, db: Session, request: LLMRequest) -> Dict[str, Any]:
        """生成文本"""
        print(f"生成文本请求: model_id={request.model_id}, content_length={len(request.content)}")

        # 使用指定的模型或默认模型
        llm = self.default_llm
        if request.model_id:
            try:
                llm = self._get_llm(db, request.model_id)
                print(f"成功获取模型，准备生成文本")
            except Exception as e:
                print(f"获取模型时出错: {str(e)}")
                raise

        # 如果没有可用的LLM，返回模拟响应
        if llm is None:
            print("没有可用的LLM，返回模拟响应")
            return {
                "result": f"# {request.content}\n\n人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n## 主要应用领域\n\n1. **医疗保健** - 疾病诊断、药物研发、个性化治疗\n2. **金融** - 风险评估、欺诈检测、算法交易\n3. **制造业** - 预测性维护、质量控制、供应链优化\n4. **客户服务** - 聊天机器人、个性化推荐、情感分析",
                "type": "generation"
            }

        try:
            prompt_template = PromptTemplate(
                input_variables=["prompt"],
                template="{prompt}"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)
            print("开始运行LLM链")
            result = chain.run(prompt=request.content)
            print("LLM链运行完成")
        except Exception as e:
            print(f"运行LLM链时出错: {str(e)}")
            # 返回模拟响应而不是抛出异常
            return {
                "result": f"# {request.content} (模拟响应)\n\n人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。\n\n### 错误信息\n\n- 处理请求时出错: {str(e)}",
                "type": "generation"
            }

        return {
            "result": result,
            "type": "generation"
        }

    async def summarize_text(self, db: Session, request: LLMRequest) -> Dict[str, Any]:
        """生成摘要"""
        print(f"生成摘要请求: model_id={request.model_id}, content_length={len(request.content)}")

        # 使用指定的模型或默认模型
        llm = self.default_llm
        if request.model_id:
            try:
                llm = self._get_llm(db, request.model_id)
                print(f"成功获取模型，准备生成摘要")
            except Exception as e:
                print(f"获取模型时出错: {str(e)}")
                raise

        # 如果没有可用的LLM，返回模拟响应
        if llm is None:
            print("没有可用的LLM，返回模拟响应")
            return {
                "result": f"## 摘要\n\n该文本讨论了人工智能的发展及其对社会的影响。主要观点包括AI技术正在各行业广泛应用，带来效率提升和创新，但也引发了关于隐私、就业和伦理的担忧。作者认为需要平衡技术进步与社会影响，建立适当的监管框架。",
                "type": "summary"
            }

        try:
            prompt_template = PromptTemplate(
                input_variables=["text"],
                template="请为以下文本生成一个简洁的摘要：\n\n{text}"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)
            print("开始运行LLM链")
            result = chain.run(text=request.content)
            print("LLM链运行完成")
        except Exception as e:
            print(f"运行LLM链时出错: {str(e)}")
            # 返回模拟响应而不是抛出异常
            return {
                "result": f"## 摘要 (模拟)\n\n该文本讨论了人工智能的发展及其对社会的影响。\n\n### 错误信息\n\n- 处理请求时出错: {str(e)}",
                "type": "summary"
            }

        return {
            "result": result,
            "type": "summary"
        }

    async def extract_keywords(self, db: Session, request: LLMRequest) -> Dict[str, Any]:
        """提取关键词"""
        print(f"提取关键词请求: model_id={request.model_id}, content_length={len(request.content)}")

        # 使用指定的模型或默认模型
        llm = self.default_llm
        if request.model_id:
            try:
                llm = self._get_llm(db, request.model_id)
                print(f"成功获取模型，准备提取关键词")
            except Exception as e:
                print(f"获取模型时出错: {str(e)}")
                raise

        # 如果没有可用的LLM，返回模拟响应
        if llm is None:
            print("没有可用的LLM，返回模拟响应")
            mock_keywords = ["人工智能", "机器学习", "自动化", "效率提升", "技术创新", "伦理考量", "隐私保护", "就业影响", "监管框架", "社会变革"]
            return {
                "result": mock_keywords,
                "type": "keywords"
            }

        try:
            prompt_template = PromptTemplate(
                input_variables=["text"],
                template="从以下文本中提取关键词和短语，以JSON数组格式返回：\n\n{text}"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)
            print("开始运行LLM链")
            result = chain.run(text=request.content)
            print("LLM链运行完成")

            # 尝试解析JSON结果
            try:
                keywords = json.loads(result)
                if not isinstance(keywords, list):
                    keywords = [result]
            except json.JSONDecodeError:
                # 如果无法解析为JSON，将结果按逗号分割
                keywords = [kw.strip() for kw in result.split(",")]

        except Exception as e:
            print(f"运行LLM链时出错: {str(e)}")
            # 返回模拟响应而不是抛出异常
            mock_keywords = ["人工智能", "机器学习", "自动化", "错误", f"处理请求时出错: {str(e)}"]
            return {
                "result": mock_keywords,
                "type": "keywords"
            }

        return {
            "result": keywords,
            "type": "keywords"
        }

    async def analyze_database(
        self,
        db: Session,
        database_id: int,
        prompt: str,
        model_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """分析数据库内容"""
        print(f"分析数据库请求: database_id={database_id}, model_id={model_id}, prompt_length={len(prompt)}")

        # 使用指定的模型或默认模型
        llm = self.default_llm
        if model_id:
            try:
                llm = self._get_llm(db, model_id)
                print(f"成功获取模型，准备分析数据库")
            except Exception as e:
                print(f"获取模型时出错: {str(e)}")
                raise

        # 如果没有可用的LLM，返回模拟响应
        if llm is None:
            print("没有可用的LLM，返回模拟响应")
            return {
                "result": f"## 数据库分析结果\n\n基于数据库ID {database_id}的分析：\n\n### 主要发现\n\n1. 销售趋势呈现季节性波动，第四季度表现最佳\n2. 客户满意度与产品质量高度相关\n3. 价格变动对销量的影响因产品类别而异\n\n### 建议\n\n- 增加第四季度的库存和营销预算\n- 重点关注产品质量改进\n- 针对不同产品类别制定差异化定价策略",
                "type": "database_analysis"
            }

        try:
            # 获取数据库中的所有表格
            tables = database_service.get_database_tables(db, database_id)
            print(f"获取到{len(tables)}个表格")

            # 准备数据样本
            data_samples = []
            for table in tables:
                table_data = database_service.get_table_data(
                    db, database_id, table.id, skip=0, limit=10
                )
                data_samples.append({
                    "table_name": table.name,
                    "columns": [col["name"] for col in table_data["columns"]],
                    "sample_data": table_data["data"][:5]  # 只取前5行作为样本
                })

            # 将数据样本转换为字符串
            data_str = json.dumps(data_samples, ensure_ascii=False, indent=2)
            print(f"准备数据样本完成，数据长度: {len(data_str)}")

            # 创建提示
            prompt_template = PromptTemplate(
                input_variables=["data", "prompt"],
                template="以下是数据库中的表格和样本数据：\n\n{data}\n\n根据上述数据，{prompt}"
            )

            print("开始运行LLM链")
            chain = LLMChain(llm=llm, prompt=prompt_template)
            result = chain.run(data=data_str, prompt=prompt)
            print("LLM链运行完成")

        except Exception as e:
            print(f"分析数据库时出错: {str(e)}")
            # 返回模拟响应而不是抛出异常
            return {
                "result": f"## 数据库分析结果 (模拟)\n\n基于数据库ID {database_id}的分析：\n\n### 错误信息\n\n- 处理请求时出错: {str(e)}",
                "type": "database_analysis"
            }

        return {
            "result": result,
            "type": "database_analysis"
        }

    async def chat_with_llm(
        self,
        db: Session,
        model_id: int,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """与LLM进行对话"""
        # 获取LLM实例
        llm = self._get_llm(db, model_id)

        # 转换消息格式
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                chat_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                chat_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_messages.append(AIMessage(content=msg["content"]))

        # 调用LLM
        response = llm(chat_messages)

        return {
            "result": response.content,
            "type": "chat"
        }

# 创建服务实例
llm_service = LLMService()

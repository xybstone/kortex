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
        self.default_llm = OpenAI(
            openai_api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.7
        )
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
        # 检查缓存
        if model_id in self.model_cache:
            return self.model_cache[model_id]

        # 获取模型信息
        model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
        if not model:
            return self.default_llm

        # 获取供应商信息
        provider = db.query(LLMProvider).filter(LLMProvider.id == model.provider_id).first()
        if not provider:
            return self.default_llm

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

    async def analyze_text(self, request: LLMRequest) -> Dict[str, Any]:
        """分析文本"""
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="分析以下文本，提供关键观点、主题和情感分析：\n\n{text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(text=request.content)

        return {
            "result": result,
            "type": "analysis"
        }

    async def generate_text(self, request: LLMRequest) -> Dict[str, Any]:
        """生成文本"""
        prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(prompt=request.content)

        return {
            "result": result,
            "type": "generation"
        }

    async def summarize_text(self, request: LLMRequest) -> Dict[str, Any]:
        """生成摘要"""
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="请为以下文本生成一个简洁的摘要：\n\n{text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(text=request.content)

        return {
            "result": result,
            "type": "summary"
        }

    async def extract_keywords(self, request: LLMRequest) -> Dict[str, Any]:
        """提取关键词"""
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="从以下文本中提取关键词和短语，以JSON数组格式返回：\n\n{text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(text=request.content)

        # 尝试解析JSON结果
        try:
            keywords = json.loads(result)
            if not isinstance(keywords, list):
                keywords = [result]
        except json.JSONDecodeError:
            # 如果无法解析为JSON，将结果按逗号分割
            keywords = [kw.strip() for kw in result.split(",")]

        return {
            "result": keywords,
            "type": "keywords"
        }

    async def analyze_database(
        self,
        db: Session,
        database_id: int,
        prompt: str
    ) -> Dict[str, Any]:
        """分析数据库内容"""
        # 获取数据库中的所有表格
        tables = database_service.get_database_tables(db, database_id)

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

        # 创建提示
        prompt_template = PromptTemplate(
            input_variables=["data", "prompt"],
            template="以下是数据库中的表格和样本数据：\n\n{data}\n\n根据上述数据，{prompt}"
        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(data=data_str, prompt=prompt)

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

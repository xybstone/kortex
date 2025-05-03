from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json

from backend.core.config import settings
from backend.models.schemas import LLMRequest, LLMResponse
from backend.core.services import database_service

class LLMService:
    def __init__(self):
        """初始化LLM服务"""
        self.llm = OpenAI(
            openai_api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.7
        )
    
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

# 创建服务实例
llm_service = LLMService()

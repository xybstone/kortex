"""
大型语言模型管理器
管理不同供应商的大型语言模型
"""
import logging
import os
from typing import Dict, Any, List, Optional

from langchain.llms.base import BaseLLM
from langchain_community.chat_models import ChatOpenAI
# 使用ChatDeepSeek而不是DeepSeekLLM
from langchain_deepseek import ChatDeepSeek

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMManager:
    """大型语言模型管理器"""

    def __init__(self):
        """初始化管理器"""
        self.models = {}
        self.default_model = None

    def register_model(self, model_id: str, model: BaseLLM, is_default: bool = False):
        """
        注册模型
        :param model_id: 模型ID
        :param model: 模型实例
        :param is_default: 是否设为默认模型
        """
        self.models[model_id] = model
        if is_default or self.default_model is None:
            self.default_model = model_id
            logger.info(f"设置默认模型: {model_id}")

    def get_model(self, model_id: Optional[str] = None) -> BaseLLM:
        """
        获取模型
        :param model_id: 模型ID，如果为None则返回默认模型
        :return: 模型实例
        """
        if model_id is None:
            model_id = self.default_model

        if model_id not in self.models:
            raise ValueError(f"模型不存在: {model_id}")

        return self.models[model_id]

    def list_models(self) -> List[str]:
        """
        列出所有可用模型
        :return: 模型ID列表
        """
        return list(self.models.keys())

    def get_default_model_id(self) -> str:
        """
        获取默认模型ID
        :return: 默认模型ID
        """
        return self.default_model


# 创建单例实例
llm_manager = LLMManager()


def init_llm_manager(config: Dict[str, Any]):
    """
    初始化LLM管理器
    :param config: 配置信息
    """
    # 注册OpenAI模型
    if "openai" in config:
        openai_config = config["openai"]
        api_key = openai_config.get("api_key") or os.environ.get("OPENAI_API_KEY")

        if api_key:
            for model_info in openai_config.get("models", []):
                model_name = model_info.get("name", "gpt-3.5-turbo")
                model_id = f"openai/{model_name}"

                try:
                    model = ChatOpenAI(
                        model_name=model_name,
                        openai_api_key=api_key,
                        temperature=model_info.get("temperature", 0.0),
                        max_tokens=model_info.get("max_tokens", 1000)
                    )

                    llm_manager.register_model(
                        model_id=model_id,
                        model=model,
                        is_default=model_info.get("is_default", False)
                    )

                    logger.info(f"已注册OpenAI模型: {model_id}")

                except Exception as e:
                    logger.error(f"注册OpenAI模型时出错: {str(e)}")
        else:
            logger.warning("未找到OpenAI API密钥，跳过注册OpenAI模型")

    # 注册DeepSeek模型
    if "deepseek" in config:
        deepseek_config = config["deepseek"]
        api_key = deepseek_config.get("api_key") or os.environ.get("DEEPSEEK_API_KEY")

        if api_key:
            for model_info in deepseek_config.get("models", []):
                model_name = model_info.get("name", "deepseek-chat")
                model_id = f"deepseek/{model_name}"

                try:
                    model = ChatDeepSeek(
                        model_name=model_name,
                        deepseek_api_key=api_key,
                        temperature=model_info.get("temperature", 0.0),
                        max_tokens=model_info.get("max_tokens", 1000)
                    )

                    llm_manager.register_model(
                        model_id=model_id,
                        model=model,
                        is_default=model_info.get("is_default", False)
                    )

                    logger.info(f"已注册DeepSeek模型: {model_id}")

                except Exception as e:
                    logger.error(f"注册DeepSeek模型时出错: {str(e)}")
        else:
            logger.warning("未找到DeepSeek API密钥，跳过注册DeepSeek模型")

    # 检查是否有可用模型
    if not llm_manager.list_models():
        logger.warning("没有可用的LLM模型，自然语言处理功能将不可用")

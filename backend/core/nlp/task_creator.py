"""
自然语言任务创建器
根据自然语言指令创建处理任务
"""
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from models.domain.dataset import ProcessingTask, DataSource
from core.nlp.instruction_parser import InstructionParser
from core.nlp.llm_manager import llm_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskCreator:
    """自然语言任务创建器"""

    def __init__(self):
        """初始化创建器"""
        # 获取默认模型
        try:
            default_model = llm_manager.get_model()
            self.instruction_parser = InstructionParser(llm=default_model)
            self.is_available = True
        except Exception as e:
            logger.error(f"初始化任务创建器时出错: {str(e)}")
            self.is_available = False

    async def create_task_from_instruction(
        self, 
        instruction: str, 
        data_source_id: int,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        根据自然语言指令创建任务
        :param instruction: 自然语言指令
        :param data_source_id: 数据源ID
        :param user_id: 用户ID
        :param db: 数据库会话
        :return: 创建结果
        """
        if not self.is_available:
            return {
                "success": False,
                "error": "自然语言处理功能不可用，请检查LLM配置"
            }
            
        try:
            # 1. 解析指令
            parse_result = await self.instruction_parser.parse_instruction(instruction)
            
            if not parse_result["success"]:
                return parse_result
                
            # 2. 获取数据源
            data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
            
            if not data_source:
                return {
                    "success": False,
                    "error": f"数据源不存在: {data_source_id}"
                }
                
            # 3. 验证任务类型与数据源类型是否匹配
            task_type = parse_result["task_type"]
            source_type = data_source.type
            
            if not self._validate_task_source_match(task_type, source_type):
                return {
                    "success": False,
                    "error": f"任务类型 {task_type} 与数据源类型 {source_type} 不匹配"
                }
                
            # 4. 创建任务
            task = ProcessingTask(
                name=f"NL: {instruction[:50]}{'...' if len(instruction) > 50 else ''}",
                description=instruction,
                task_type=task_type,
                parameters=parse_result["parameters"],
                status="pending",
                data_source_id=data_source_id,
                user_id=user_id
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            
            # 5. 返回结果
            return {
                "success": True,
                "task_id": task.id,
                "task_type": task_type,
                "parameters": parse_result["parameters"],
                "confidence": parse_result["confidence"],
                "reasoning": parse_result["reasoning"]
            }
            
        except Exception as e:
            logger.error(f"创建任务时出错: {str(e)}")
            return {
                "success": False,
                "error": f"创建任务时出错: {str(e)}"
            }
            
    def _validate_task_source_match(self, task_type: str, source_type: str) -> bool:
        """
        验证任务类型与数据源类型是否匹配
        :param task_type: 任务类型
        :param source_type: 数据源类型
        :return: 是否匹配
        """
        # 数据库任务
        if task_type.startswith("database_") and source_type != "database":
            return False
            
        # 文件任务
        if (task_type.startswith("file_") or task_type.startswith("csv_") or task_type.startswith("text_")) and source_type != "file":
            return False
            
        # URL任务
        if task_type.startswith("url_") and source_type != "url":
            return False
            
        return True


# 创建单例实例
task_creator = TaskCreator()

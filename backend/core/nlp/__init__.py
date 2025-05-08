"""
自然语言处理模块
提供自然语言指令解析和任务创建功能
"""
from core.nlp.llm_manager import llm_manager, init_llm_manager
from core.nlp.instruction_parser import InstructionParser
from core.nlp.task_creator import task_creator

__all__ = [
    'llm_manager',
    'init_llm_manager',
    'InstructionParser',
    'task_creator'
]

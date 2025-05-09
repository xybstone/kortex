"""
数据处理基础模块
定义处理器接口和基础实现
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.domain.dataset import ProcessingTask, DataSource


class DataProcessor(ABC):
    """数据处理器接口"""

    @abstractmethod
    async def process(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """
        处理数据
        :param task: 处理任务
        :param db: 数据库会话
        :return: 处理结果
        """
        pass

    @abstractmethod
    def get_supported_task_types(self) -> List[str]:
        """
        获取支持的任务类型
        :return: 任务类型列表
        """
        pass

    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        验证任务参数
        :param parameters: 任务参数
        :return: 是否有效
        """
        pass

    @abstractmethod
    def get_progress(self, task_id: int, db: Session) -> int:
        """
        获取任务进度
        :param task_id: 任务ID
        :param db: 数据库会话
        :return: 进度百分比(0-100)
        """
        pass

    @abstractmethod
    def cancel(self, task_id: int, db: Session) -> bool:
        """
        取消任务
        :param task_id: 任务ID
        :param db: 数据库会话
        :return: 是否成功取消
        """
        pass


class BaseDataProcessor(DataProcessor):
    """数据处理器基础实现"""

    def __init__(self):
        self.running_tasks = {}  # 正在运行的任务

    async def process(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """
        处理数据的通用流程
        :param task: 处理任务
        :param db: 数据库会话
        :return: 处理结果
        """
        # 检查任务类型是否支持
        if task.task_type not in self.get_supported_task_types():
            return {
                "success": False,
                "error": f"不支持的任务类型: {task.task_type}"
            }

        # 验证参数
        parameters = task.parameters or {}

        # 确保参数中包含任务类型信息
        if isinstance(parameters, dict) and task.task_type:
            # 将任务类型添加到参数中，以便验证
            parameters_with_type = parameters.copy()
            parameters_with_type["task_type"] = task.task_type
        else:
            parameters_with_type = parameters

        if not self.validate_parameters(parameters_with_type):
            return {
                "success": False,
                "error": "无效的任务参数"
            }

        # 更新任务状态为运行中
        task.status = "running"
        task.progress = 0
        db.commit()

        try:
            # 记录任务
            self.running_tasks[task.id] = {
                "task": task,
                "progress": 0,
                "cancel_requested": False
            }

            # 执行具体处理逻辑
            result = await self._execute_task(task, db)

            # 如果请求取消，则返回取消结果
            if self.running_tasks[task.id]["cancel_requested"]:
                task.status = "cancelled"
                task.progress = self.running_tasks[task.id]["progress"]
                db.commit()
                return {
                    "success": False,
                    "error": "任务已取消"
                }

            # 更新任务状态为已完成
            task.status = "completed"
            task.progress = 100
            task.result = result
            db.commit()

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            db.commit()

            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # 清理任务记录
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    @abstractmethod
    async def _execute_task(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """
        执行具体的处理逻辑，由子类实现
        :param task: 处理任务
        :param db: 数据库会话
        :return: 处理结果
        """
        pass

    def update_progress(self, task_id: int, progress: int, db: Session) -> None:
        """
        更新任务进度
        :param task_id: 任务ID
        :param progress: 进度百分比(0-100)
        :param db: 数据库会话
        """
        if task_id in self.running_tasks:
            self.running_tasks[task_id]["progress"] = progress

            # 更新数据库中的进度
            task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
            if task:
                task.progress = progress
                db.commit()

    def get_progress(self, task_id: int, db: Session) -> int:
        """
        获取任务进度
        :param task_id: 任务ID
        :param db: 数据库会话
        :return: 进度百分比(0-100)
        """
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]["progress"]

        # 从数据库获取进度
        task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
        if task:
            return task.progress

        return 0

    def cancel(self, task_id: int, db: Session) -> bool:
        """
        取消任务
        :param task_id: 任务ID
        :param db: 数据库会话
        :return: 是否成功取消
        """
        if task_id in self.running_tasks:
            self.running_tasks[task_id]["cancel_requested"] = True
            return True

        # 如果任务不在运行中，检查数据库中的状态
        task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
        if task and task.status == "pending":
            task.status = "cancelled"
            db.commit()
            return True

        return False

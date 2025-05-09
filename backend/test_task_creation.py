#!/usr/bin/env python
"""
测试任务创建过程
"""
import json
import sys
import os
import asyncio
from sqlalchemy.orm import Session

from database.session import SessionLocal
from models.domain.dataset import ProcessingTask, FileSource, DataSource
from core.processing.file_processor import FileProcessor

async def test_task_creation():
    """测试任务创建过程"""
    db = SessionLocal()

    try:
        # 查找一个文件数据源
        file_source = db.query(FileSource).first()
        if not file_source:
            print("错误: 找不到文件数据源，请先创建一个文件数据源")
            return

        print(f"找到文件数据源: ID={file_source.id}, 名称={file_source.name}")

        # 创建任务参数
        parameters = {"extract_type": "text"}

        # 直接创建任务
        task = ProcessingTask(
            name="测试文件提取任务",
            description="测试任务参数验证",
            task_type="file_extract",
            parameters=parameters,
            data_source_id=file_source.id,
            priority=0,
            is_recurring=False,
            wait_for_dependencies=True,
            user_id=1  # 假设用户ID为1
        )

        # 添加到数据库
        db.add(task)
        db.commit()
        db.refresh(task)

        print(f"任务创建成功: ID={task.id}")
        print(f"任务类型: {task.task_type}")
        print(f"任务参数: {task.parameters}")

        # 检查参数是否正确
        processor = FileProcessor()
        is_valid = processor.validate_parameters(task.parameters or {})
        print(f"参数验证结果: {is_valid}")

        # 检查参数类型
        print(f"参数类型: {type(task.parameters)}")

        # 如果参数是字符串，尝试解析
        if isinstance(task.parameters, str):
            try:
                parsed = json.loads(task.parameters)
                print(f"解析后的参数: {parsed}")
                print(f"解析后的参数类型: {type(parsed)}")
            except Exception as e:
                print(f"解析参数时出错: {str(e)}")

    finally:
        db.close()

async def main():
    """主函数"""
    print("开始测试任务创建过程...")
    await test_task_creation()
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main())

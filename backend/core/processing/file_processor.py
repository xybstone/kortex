"""
文件处理器模块
实现文件数据的嵌入和处理
"""
import asyncio
import os
import logging
import pandas as pd
import numpy as np
import json
import csv
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from models.domain.dataset import ProcessingTask, FileSource
from core.processing.base import BaseDataProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileProcessor(BaseDataProcessor):
    """文件处理器"""

    def get_supported_task_types(self) -> List[str]:
        """获取支持的任务类型"""
        return [
            "file_embed",       # 文件嵌入向量化
            "file_extract",     # 文件内容提取
            "file_convert",     # 文件格式转换
            "file_analyze",     # 文件分析
            "csv_process",      # CSV文件处理
            "text_process"      # 文本文件处理
        ]

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证任务参数"""
        # 根据不同的任务类型验证参数
        task_type = parameters.get("task_type")

        if task_type == "file_embed":
            # 嵌入任务需要指定嵌入模型
            return "embed_model" in parameters

        elif task_type == "file_extract":
            # 提取任务需要指定提取类型
            return "extract_type" in parameters

        elif task_type == "file_convert":
            # 转换任务需要指定目标格式
            return "target_format" in parameters

        elif task_type == "file_analyze":
            # 文件分析任务需要指定分析类型
            return "analysis_type" in parameters

        elif task_type == "csv_process":
            # CSV处理任务需要指定处理操作
            return "operations" in parameters

        elif task_type == "text_process":
            # 文本处理任务需要指定处理操作
            return "operations" in parameters

        return False

    async def _execute_task(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """执行具体的处理逻辑"""
        # 获取数据源
        data_source = db.query(FileSource).filter(
            FileSource.id == task.data_source_id
        ).first()

        if not data_source:
            raise ValueError(f"数据源不存在: {task.data_source_id}")

        # 检查文件是否存在
        if not os.path.exists(data_source.file_path):
            raise FileNotFoundError(f"文件不存在: {data_source.file_path}")

        # 根据任务类型执行不同的处理逻辑
        if task.task_type == "file_embed":
            return await self._embed_file(task, data_source, db)

        elif task.task_type == "file_extract":
            return await self._extract_file(task, data_source, db)

        elif task.task_type == "file_convert":
            return await self._convert_file(task, data_source, db)

        elif task.task_type == "file_analyze":
            return await self._analyze_file(task, data_source, db)

        elif task.task_type == "csv_process":
            return await self._process_csv(task, data_source, db)

        elif task.task_type == "text_process":
            return await self._process_text(task, data_source, db)

        raise ValueError(f"不支持的任务类型: {task.task_type}")

    async def _embed_file(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """嵌入文件数据"""
        parameters = task.parameters or {}
        embed_model = parameters.get("embed_model")

        # 模拟处理过程
        for i in range(10):
            # 检查是否请求取消
            if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                return {"status": "cancelled"}

            # 模拟处理时间
            await asyncio.sleep(0.5)

            # 更新进度
            progress = int((i + 1) / 10 * 100)
            self.update_progress(task.id, progress, db)

        # 返回处理结果
        return {
            "embed_model": embed_model,
            "vector_count": 1000,  # 模拟数据
            "dimensions": 768,
            "file_type": data_source.file_type
        }

    async def _extract_file(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """提取文件数据"""
        parameters = task.parameters or {}
        extract_type = parameters.get("extract_type")

        # 模拟处理过程
        for i in range(5):
            # 检查是否请求取消
            if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                return {"status": "cancelled"}

            # 模拟处理时间
            await asyncio.sleep(0.5)

            # 更新进度
            progress = int((i + 1) / 5 * 100)
            self.update_progress(task.id, progress, db)

        # 返回处理结果
        return {
            "extract_type": extract_type,
            "extracted_items": 50,  # 模拟数据
            "file_type": data_source.file_type
        }

    async def _convert_file(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """转换文件格式"""
        parameters = task.parameters or {}
        target_format = parameters.get("target_format")

        # 模拟处理过程
        for i in range(3):
            # 检查是否请求取消
            if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                return {"status": "cancelled"}

            # 模拟处理时间
            await asyncio.sleep(0.5)

            # 更新进度
            progress = int((i + 1) / 3 * 100)
            self.update_progress(task.id, progress, db)

        # 返回处理结果
        return {
            "source_format": data_source.file_type,
            "target_format": target_format,
            "converted_size": data_source.file_size * 0.8 if data_source.file_size else 1000  # 模拟数据
        }

    async def _analyze_file(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """
        分析文件内容
        :param task: 处理任务
        :param data_source: 文件数据源
        :param db: 数据库会话
        :return: 分析结果
        """
        parameters = task.parameters or {}
        analysis_type = parameters.get("analysis_type")

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            file_path = data_source.file_path
            file_type = data_source.file_type.lower() if data_source.file_type else ""
            file_size = data_source.file_size or os.path.getsize(file_path)

            # 基本文件信息
            file_info = {
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size,
                "file_size_human": self._format_file_size(file_size),
                "last_modified": os.path.getmtime(file_path)
            }

            # 更新进度
            self.update_progress(task.id, 30, db)

            # 根据文件类型和分析类型执行不同的分析
            analysis_result = {}

            if analysis_type == "basic":
                # 基本分析：文件信息、行数等
                analysis_result = await self._basic_file_analysis(file_path, file_type)

            elif analysis_type == "content":
                # 内容分析：文本统计、关键词等
                analysis_result = await self._content_file_analysis(file_path, file_type)

            elif analysis_type == "structure":
                # 结构分析：CSV/JSON结构等
                analysis_result = await self._structure_file_analysis(file_path, file_type)

            else:
                return {"success": False, "error": f"不支持的分析类型: {analysis_type}"}

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回分析结果
            return {
                "success": True,
                "analysis_type": analysis_type,
                "file_info": file_info,
                "analysis_result": analysis_result
            }

        except Exception as e:
            error_msg = f"分析文件时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小为人类可读格式
        :param size_bytes: 文件大小（字节）
        :return: 格式化后的大小
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    async def _basic_file_analysis(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        基本文件分析
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: 分析结果
        """
        result = {}

        # 文件统计信息
        try:
            # 计算行数（对于文本文件）
            if file_type in ["txt", "md", "csv", "json", "py", "js", "html", "css"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    result["line_count"] = len(lines)
                    result["empty_line_count"] = sum(1 for line in lines if line.strip() == "")
                    result["non_empty_line_count"] = result["line_count"] - result["empty_line_count"]

                    # 计算平均行长度
                    if result["non_empty_line_count"] > 0:
                        total_chars = sum(len(line.strip()) for line in lines if line.strip() != "")
                        result["avg_line_length"] = total_chars / result["non_empty_line_count"]
                    else:
                        result["avg_line_length"] = 0

            # 文件哈希值（用于唯一标识）
            import hashlib
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                result["md5_hash"] = file_hash.hexdigest()

            # 文件权限
            result["permissions"] = oct(os.stat(file_path).st_mode)[-3:]

        except Exception as e:
            result["error"] = f"基本分析时出错: {str(e)}"

        return result

    async def _content_file_analysis(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        文件内容分析
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: 分析结果
        """
        result = {}

        try:
            # 文本文件内容分析
            if file_type in ["txt", "md", "csv", "json", "py", "js", "html", "css"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # 字符统计
                    result["char_count"] = len(content)
                    result["letter_count"] = sum(c.isalpha() for c in content)
                    result["digit_count"] = sum(c.isdigit() for c in content)
                    result["whitespace_count"] = sum(c.isspace() for c in content)
                    result["punctuation_count"] = sum(c in ".,;:!?-\"'()[]{}" for c in content)

                    # 单词统计
                    words = re.findall(r'\b\w+\b', content.lower())
                    result["word_count"] = len(words)

                    # 词频统计（前10个）
                    from collections import Counter
                    word_freq = Counter(words)
                    result["top_words"] = [
                        {"word": word, "count": count}
                        for word, count in word_freq.most_common(10)
                    ]

                    # 检测编码
                    import chardet
                    with open(file_path, 'rb') as binary_file:
                        raw_data = binary_file.read(10000)  # 只读取前10000字节进行检测
                        encoding_result = chardet.detect(raw_data)
                        result["detected_encoding"] = encoding_result

            # CSV文件特定分析
            elif file_type == "csv":
                df = pd.read_csv(file_path, nrows=1000)  # 只读取前1000行进行分析
                result["column_count"] = len(df.columns)
                result["columns"] = df.columns.tolist()
                result["data_types"] = {col: str(df[col].dtype) for col in df.columns}
                result["null_counts"] = {col: int(df[col].isnull().sum()) for col in df.columns}
                result["sample_rows"] = df.head(5).to_dict(orient="records")

            # JSON文件特定分析
            elif file_type == "json":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    json_data = json.load(f)

                    if isinstance(json_data, list):
                        result["structure"] = "array"
                        result["array_length"] = len(json_data)
                        if json_data and isinstance(json_data[0], dict):
                            result["sample_keys"] = list(json_data[0].keys())
                    elif isinstance(json_data, dict):
                        result["structure"] = "object"
                        result["top_level_keys"] = list(json_data.keys())
                    else:
                        result["structure"] = "primitive"
                        result["value_type"] = type(json_data).__name__

        except Exception as e:
            result["error"] = f"内容分析时出错: {str(e)}"

        return result

    async def _process_csv(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """
        处理CSV文件
        :param task: 处理任务
        :param data_source: 文件数据源
        :param db: 数据库会话
        :return: 处理结果
        """
        parameters = task.parameters or {}
        operations = parameters.get("operations", [])

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            file_path = data_source.file_path

            # 检查文件类型
            if data_source.file_type.lower() != "csv":
                return {"success": False, "error": "文件类型不是CSV"}

            # 读取CSV文件
            try:
                # 尝试自动检测编码
                encoding = parameters.get("encoding", "utf-8")
                df = pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    import chardet
                    with open(file_path, 'rb') as f:
                        result = chardet.detect(f.read(10000))
                    encoding = result['encoding']
                    df = pd.read_csv(file_path, encoding=encoding)
                except Exception as e:
                    return {"success": False, "error": f"无法读取CSV文件: {str(e)}"}

            # 记录原始数据信息
            original_shape = df.shape
            original_columns = df.columns.tolist()

            # 更新进度
            self.update_progress(task.id, 30, db)

            # 应用操作
            operation_results = []
            total_steps = len(operations)

            for i, operation in enumerate(operations):
                # 检查是否请求取消
                if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                    return {"status": "cancelled"}

                # 获取操作信息
                operation_type = operation.get("type")

                # 应用操作
                result = {"operation": operation, "applied": False, "message": ""}

                try:
                    if operation_type == "filter_rows":
                        # 过滤行
                        column = operation.get("column")
                        condition = operation.get("condition")  # eq, ne, gt, lt, contains, etc.
                        value = operation.get("value")

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        old_count = len(df)

                        if condition == "eq":
                            df = df[df[column] == value]
                        elif condition == "ne":
                            df = df[df[column] != value]
                        elif condition == "gt":
                            df = df[df[column] > value]
                        elif condition == "lt":
                            df = df[df[column] < value]
                        elif condition == "contains":
                            df = df[df[column].astype(str).str.contains(str(value), na=False)]
                        elif condition == "not_contains":
                            df = df[~df[column].astype(str).str.contains(str(value), na=False)]
                        elif condition == "is_null":
                            df = df[df[column].isnull()]
                        elif condition == "is_not_null":
                            df = df[df[column].notnull()]
                        else:
                            result["message"] = f"不支持的条件: {condition}"
                            continue

                        new_count = len(df)
                        result["applied"] = True
                        result["message"] = f"已过滤 {old_count - new_count} 行数据"

                    elif operation_type == "select_columns":
                        # 选择列
                        columns = operation.get("columns", [])

                        # 检查列是否存在
                        missing_columns = [col for col in columns if col not in df.columns]
                        if missing_columns:
                            result["message"] = f"列不存在: {', '.join(missing_columns)}"
                            continue

                        old_columns = df.columns.tolist()
                        df = df[columns]

                        result["applied"] = True
                        result["message"] = f"已选择 {len(columns)} 列，移除 {len(old_columns) - len(columns)} 列"

                    elif operation_type == "rename_columns":
                        # 重命名列
                        rename_map = operation.get("rename_map", {})

                        # 检查列是否存在
                        missing_columns = [col for col in rename_map.keys() if col not in df.columns]
                        if missing_columns:
                            result["message"] = f"列不存在: {', '.join(missing_columns)}"
                            continue

                        df = df.rename(columns=rename_map)

                        result["applied"] = True
                        result["message"] = f"已重命名 {len(rename_map)} 列"

                    elif operation_type == "sort":
                        # 排序
                        column = operation.get("column")
                        ascending = operation.get("ascending", True)

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        df = df.sort_values(by=column, ascending=ascending)

                        result["applied"] = True
                        result["message"] = f"已按列 {column} {'升序' if ascending else '降序'} 排序"

                    elif operation_type == "fill_nulls":
                        # 填充空值
                        column = operation.get("column")
                        method = operation.get("method", "value")  # value, mean, median, mode
                        value = operation.get("value")

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        null_count = df[column].isnull().sum()

                        if method == "value" and value is not None:
                            df[column] = df[column].fillna(value)
                        elif method == "mean" and pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].mean())
                        elif method == "median" and pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].median())
                        elif method == "mode":
                            df[column] = df[column].fillna(df[column].mode()[0] if not df[column].mode().empty else None)
                        else:
                            result["message"] = f"不支持的方法: {method}"
                            continue

                        result["applied"] = True
                        result["message"] = f"已填充 {null_count} 个空值"

                    elif operation_type == "create_column":
                        # 创建新列
                        new_column = operation.get("new_column")
                        expression = operation.get("expression")

                        if not expression:
                            result["message"] = "未指定表达式"
                            continue

                        # 使用eval执行表达式（注意：这在生产环境中可能存在安全风险）
                        try:
                            # 创建一个局部命名空间，包含df和常用库
                            local_dict = {"df": df, "np": np, "pd": pd}
                            # 执行表达式
                            df[new_column] = eval(expression, {"__builtins__": {}}, local_dict)
                            result["applied"] = True
                            result["message"] = f"已创建新列 {new_column}"
                        except Exception as e:
                            result["message"] = f"表达式执行失败: {str(e)}"
                            continue

                    elif operation_type == "drop_duplicates":
                        # 删除重复行
                        subset = operation.get("subset", None)  # 可以指定基于哪些列去重

                        old_count = len(df)
                        df = df.drop_duplicates(subset=subset)
                        new_count = len(df)

                        result["applied"] = True
                        result["message"] = f"已删除 {old_count - new_count} 条重复记录"

                    elif operation_type == "convert_type":
                        # 转换数据类型
                        column = operation.get("column")
                        target_type = operation.get("target_type")  # int, float, str, datetime

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        if target_type == "int":
                            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                        elif target_type == "float":
                            df[column] = pd.to_numeric(df[column], errors='coerce')
                        elif target_type == "str":
                            df[column] = df[column].astype(str)
                        elif target_type == "datetime":
                            df[column] = pd.to_datetime(df[column], errors='coerce')
                        else:
                            result["message"] = f"不支持的目标类型: {target_type}"
                            continue

                        result["applied"] = True
                        result["message"] = f"已将列 {column} 转换为 {target_type} 类型"

                    else:
                        result["message"] = f"不支持的操作类型: {operation_type}"

                except Exception as e:
                    result["message"] = f"应用操作时出错: {str(e)}"

                operation_results.append(result)

                # 更新进度
                progress = 30 + int((i + 1) / total_steps * 60)
                self.update_progress(task.id, progress, db)

            # 保存处理后的CSV文件
            output_path = parameters.get("output_path")
            if not output_path:
                # 如果未指定输出路径，则在原文件旁边创建一个新文件
                file_dir = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                file_name_without_ext = os.path.splitext(file_name)[0]
                output_path = os.path.join(file_dir, f"{file_name_without_ext}_processed.csv")

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存处理后的CSV文件
            df.to_csv(output_path, index=False, encoding='utf-8')

            # 计算处理后的数据信息
            processed_shape = df.shape
            processed_columns = df.columns.tolist()

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "original_rows": original_shape[0],
                "original_columns": original_columns,
                "processed_rows": processed_shape[0],
                "processed_columns": processed_columns,
                "added_columns": [col for col in processed_columns if col not in original_columns],
                "removed_columns": [col for col in original_columns if col not in processed_columns],
                "operation_results": operation_results,
                "output_path": output_path,
                "sample_data": df.head(10).to_dict(orient="records")
            }

        except Exception as e:
            error_msg = f"处理CSV文件时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _process_text(self, task: ProcessingTask, data_source: FileSource, db: Session) -> Dict[str, Any]:
        """
        处理文本文件
        :param task: 处理任务
        :param data_source: 文件数据源
        :param db: 数据库会话
        :return: 处理结果
        """
        parameters = task.parameters or {}
        operations = parameters.get("operations", [])

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            file_path = data_source.file_path
            file_type = data_source.file_type.lower() if data_source.file_type else ""

            # 检查文件类型
            if file_type not in ["txt", "md", "json", "html", "css", "js", "py"]:
                return {"success": False, "error": f"不支持的文件类型: {file_type}"}

            # 读取文本文件
            try:
                # 尝试自动检测编码
                encoding = parameters.get("encoding", "utf-8")
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return {"success": False, "error": f"无法读取文本文件: {str(e)}"}

            # 记录原始内容信息
            original_lines = content.splitlines()
            original_line_count = len(original_lines)
            original_char_count = len(content)

            # 更新进度
            self.update_progress(task.id, 30, db)

            # 应用操作
            operation_results = []
            total_steps = len(operations)

            for i, operation in enumerate(operations):
                # 检查是否请求取消
                if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                    return {"status": "cancelled"}

                # 获取操作信息
                operation_type = operation.get("type")

                # 应用操作
                result = {"operation": operation, "applied": False, "message": ""}

                try:
                    if operation_type == "replace_text":
                        # 替换文本
                        old_text = operation.get("old_text", "")
                        new_text = operation.get("new_text", "")

                        if not old_text:
                            result["message"] = "未指定要替换的文本"
                            continue

                        old_count = content.count(old_text)
                        content = content.replace(old_text, new_text)

                        result["applied"] = True
                        result["message"] = f"已替换 {old_count} 处文本"

                    elif operation_type == "regex_replace":
                        # 正则表达式替换
                        pattern = operation.get("pattern", "")
                        replacement = operation.get("replacement", "")

                        if not pattern:
                            result["message"] = "未指定正则表达式模式"
                            continue

                        try:
                            old_content = content
                            content = re.sub(pattern, replacement, content)

                            # 计算替换次数
                            matches = re.findall(pattern, old_content)
                            match_count = len(matches)

                            result["applied"] = True
                            result["message"] = f"已替换 {match_count} 处匹配项"
                        except re.error as e:
                            result["message"] = f"正则表达式错误: {str(e)}"
                            continue

                    elif operation_type == "insert_text":
                        # 插入文本
                        position = operation.get("position", "start")  # start, end, line
                        line_number = operation.get("line_number", 1)
                        text = operation.get("text", "")

                        if not text:
                            result["message"] = "未指定要插入的文本"
                            continue

                        if position == "start":
                            content = text + content
                        elif position == "end":
                            content = content + text
                        elif position == "line":
                            lines = content.splitlines()
                            if 1 <= line_number <= len(lines) + 1:
                                lines.insert(line_number - 1, text)
                                content = "\n".join(lines)
                            else:
                                result["message"] = f"行号 {line_number} 超出范围"
                                continue
                        else:
                            result["message"] = f"不支持的位置: {position}"
                            continue

                        result["applied"] = True
                        result["message"] = f"已在 {position} 位置插入文本"

                    elif operation_type == "remove_lines":
                        # 删除行
                        start_line = operation.get("start_line", 1)
                        end_line = operation.get("end_line", start_line)

                        lines = content.splitlines()

                        if 1 <= start_line <= len(lines) and 1 <= end_line <= len(lines) and start_line <= end_line:
                            del lines[start_line - 1:end_line]
                            content = "\n".join(lines)

                            result["applied"] = True
                            result["message"] = f"已删除第 {start_line} 到第 {end_line} 行"
                        else:
                            result["message"] = f"行号范围 {start_line}-{end_line} 超出范围"
                            continue

                    elif operation_type == "filter_lines":
                        # 过滤行
                        pattern = operation.get("pattern", "")
                        keep_matching = operation.get("keep_matching", True)

                        if not pattern:
                            result["message"] = "未指定过滤模式"
                            continue

                        try:
                            lines = content.splitlines()
                            if keep_matching:
                                # 保留匹配的行
                                filtered_lines = [line for line in lines if re.search(pattern, line)]
                            else:
                                # 移除匹配的行
                                filtered_lines = [line for line in lines if not re.search(pattern, line)]

                            content = "\n".join(filtered_lines)

                            result["applied"] = True
                            result["message"] = f"已{'保留' if keep_matching else '移除'} {len(lines) - len(filtered_lines)} 行"
                        except re.error as e:
                            result["message"] = f"正则表达式错误: {str(e)}"
                            continue

                    elif operation_type == "convert_case":
                        # 转换大小写
                        case_type = operation.get("case_type", "lower")  # lower, upper, title, sentence

                        if case_type == "lower":
                            content = content.lower()
                        elif case_type == "upper":
                            content = content.upper()
                        elif case_type == "title":
                            content = content.title()
                        elif case_type == "sentence":
                            # 句子大小写：每个句子的第一个字母大写
                            sentences = re.split(r'(?<=[.!?])\s+', content)
                            content = " ".join(s.capitalize() for s in sentences)
                        else:
                            result["message"] = f"不支持的大小写类型: {case_type}"
                            continue

                        result["applied"] = True
                        result["message"] = f"已转换为 {case_type} 大小写"

                    else:
                        result["message"] = f"不支持的操作类型: {operation_type}"

                except Exception as e:
                    result["message"] = f"应用操作时出错: {str(e)}"

                operation_results.append(result)

                # 更新进度
                progress = 30 + int((i + 1) / total_steps * 60)
                self.update_progress(task.id, progress, db)

            # 保存处理后的文本文件
            output_path = parameters.get("output_path")
            if not output_path:
                # 如果未指定输出路径，则在原文件旁边创建一个新文件
                file_dir = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                file_name_without_ext = os.path.splitext(file_name)[0]
                file_ext = os.path.splitext(file_name)[1]
                output_path = os.path.join(file_dir, f"{file_name_without_ext}_processed{file_ext}")

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存处理后的文本文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 计算处理后的内容信息
            processed_lines = content.splitlines()
            processed_line_count = len(processed_lines)
            processed_char_count = len(content)

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "original_line_count": original_line_count,
                "original_char_count": original_char_count,
                "processed_line_count": processed_line_count,
                "processed_char_count": processed_char_count,
                "line_count_diff": processed_line_count - original_line_count,
                "char_count_diff": processed_char_count - original_char_count,
                "operation_results": operation_results,
                "output_path": output_path,
                "sample_content": content[:1000] if len(content) > 1000 else content  # 只返回前1000个字符
            }

        except Exception as e:
            error_msg = f"处理文本文件时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _structure_file_analysis(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        文件结构分析
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: 分析结果
        """
        result = {}

        try:
            # CSV文件结构分析
            if file_type == "csv":
                # 读取CSV文件
                df = pd.read_csv(file_path)

                # 基本信息
                result["row_count"] = len(df)
                result["column_count"] = len(df.columns)
                result["columns"] = df.columns.tolist()

                # 数据类型分析
                result["data_types"] = {col: str(df[col].dtype) for col in df.columns}

                # 缺失值分析
                result["null_counts"] = {col: int(df[col].isnull().sum()) for col in df.columns}
                result["null_percentages"] = {
                    col: float(df[col].isnull().sum() / len(df) * 100)
                    for col in df.columns
                }

                # 唯一值分析
                result["unique_counts"] = {col: int(df[col].nunique()) for col in df.columns}
                result["unique_percentages"] = {
                    col: float(df[col].nunique() / len(df) * 100)
                    for col in df.columns
                }

                # 数值列统计
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_columns:
                    result["numeric_stats"] = {}
                    for col in numeric_columns:
                        result["numeric_stats"][col] = {
                            "min": float(df[col].min()),
                            "max": float(df[col].max()),
                            "mean": float(df[col].mean()),
                            "median": float(df[col].median()),
                            "std": float(df[col].std())
                        }

                # 分类列统计
                categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
                if categorical_columns:
                    result["categorical_stats"] = {}
                    for col in categorical_columns:
                        # 获取前5个最常见的值及其频率
                        value_counts = df[col].value_counts().head(5)
                        result["categorical_stats"][col] = {
                            "top_values": {str(k): int(v) for k, v in value_counts.items()}
                        }

            # JSON文件结构分析
            elif file_type == "json":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    json_data = json.load(f)

                    # 递归分析JSON结构
                    def analyze_json_structure(data, max_depth=3, current_depth=0):
                        if current_depth >= max_depth:
                            return {"type": type(data).__name__, "truncated": True}

                        if isinstance(data, dict):
                            return {
                                "type": "object",
                                "keys_count": len(data),
                                "keys": list(data.keys()),
                                "sample_values": {
                                    k: analyze_json_structure(v, max_depth, current_depth + 1)
                                    for k, v in list(data.items())[:5]  # 只分析前5个键值对
                                }
                            }
                        elif isinstance(data, list):
                            return {
                                "type": "array",
                                "length": len(data),
                                "sample_items": [
                                    analyze_json_structure(item, max_depth, current_depth + 1)
                                    for item in data[:5]  # 只分析前5个元素
                                ] if data else []
                            }
                        else:
                            return {"type": type(data).__name__, "value": str(data)[:100]}

                    result["structure_analysis"] = analyze_json_structure(json_data)

            # 文本文件结构分析
            elif file_type in ["txt", "md"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                    # 段落分析
                    paragraphs = []
                    current_paragraph = []

                    for line in lines:
                        if line.strip():
                            current_paragraph.append(line.strip())
                        elif current_paragraph:
                            paragraphs.append(" ".join(current_paragraph))
                            current_paragraph = []

                    if current_paragraph:
                        paragraphs.append(" ".join(current_paragraph))

                    result["paragraph_count"] = len(paragraphs)

                    # 标题分析（针对Markdown）
                    if file_type == "md":
                        headers = [line for line in lines if line.strip().startswith("#")]
                        result["header_count"] = len(headers)
                        result["headers"] = [h.strip() for h in headers[:10]]  # 只返回前10个标题

                        # 链接分析
                        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                        links = re.findall(link_pattern, "\n".join(lines))
                        result["link_count"] = len(links)
                        result["links"] = [{"text": text, "url": url} for text, url in links[:10]]  # 只返回前10个链接

            # 其他文件类型
            else:
                result["message"] = f"不支持对 {file_type} 文件类型进行结构分析"

        except Exception as e:
            result["error"] = f"结构分析时出错: {str(e)}"

        return result

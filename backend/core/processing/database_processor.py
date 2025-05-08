"""
数据库处理器模块
实现数据库数据的清洗和处理
"""
import asyncio
import logging
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from models.domain.dataset import ProcessingTask, DatabaseSource
from core.processing.base import BaseDataProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseProcessor(BaseDataProcessor):
    """数据库处理器"""

    def get_supported_task_types(self) -> List[str]:
        """获取支持的任务类型"""
        return [
            "database_clean",
            "database_analyze",
            "database_transform",
            "database_query"
        ]

    async def _connect_to_database(self, data_source: DatabaseSource) -> Tuple[Any, str]:
        """
        连接到数据库
        :param data_source: 数据库数据源
        :return: 数据库连接引擎和错误信息（如果有）
        """
        try:
            # 创建数据库连接
            engine = create_engine(data_source.connection_string)
            # 测试连接
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine, None
        except SQLAlchemyError as e:
            error_msg = f"数据库连接失败: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    async def _get_table_names(self, engine: Any) -> List[str]:
        """
        获取数据库中的所有表名
        :param engine: 数据库连接引擎
        :return: 表名列表
        """
        inspector = inspect(engine)
        return inspector.get_table_names()

    async def _execute_query(self, engine: Any, query: str) -> Tuple[pd.DataFrame, str]:
        """
        执行SQL查询
        :param engine: 数据库连接引擎
        :param query: SQL查询语句
        :return: 查询结果DataFrame和错误信息（如果有）
        """
        try:
            # 执行查询并返回结果
            df = pd.read_sql(query, engine)
            return df, None
        except SQLAlchemyError as e:
            error_msg = f"查询执行失败: {str(e)}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证任务参数"""
        # 根据不同的任务类型验证参数
        task_type = parameters.get("task_type")

        if task_type == "database_clean":
            # 清洗任务需要指定清洗规则
            return "clean_rules" in parameters

        elif task_type == "database_analyze":
            # 分析任务需要指定分析类型
            return "analysis_type" in parameters

        elif task_type == "database_transform":
            # 转换任务需要指定转换规则
            return "transform_rules" in parameters

        elif task_type == "database_query":
            # 查询任务需要指定SQL查询语句
            return "query" in parameters

        return False

    async def _execute_task(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """执行具体的处理逻辑"""
        # 获取数据源
        data_source = db.query(DatabaseSource).filter(
            DatabaseSource.id == task.data_source_id
        ).first()

        if not data_source:
            raise ValueError(f"数据源不存在: {task.data_source_id}")

        # 根据任务类型执行不同的处理逻辑
        if task.task_type == "database_clean":
            return await self._clean_database(task, data_source, db)

        elif task.task_type == "database_analyze":
            return await self._analyze_database(task, data_source, db)

        elif task.task_type == "database_transform":
            return await self._transform_database(task, data_source, db)

        elif task.task_type == "database_query":
            return await self._query_database(task, data_source, db)

        raise ValueError(f"不支持的任务类型: {task.task_type}")

    async def _clean_database(self, task: ProcessingTask, data_source: DatabaseSource, db: Session) -> Dict[str, Any]:
        """
        清洗数据库数据
        :param task: 处理任务
        :param data_source: 数据库数据源
        :param db: 数据库会话
        :return: 清洗结果
        """
        parameters = task.parameters or {}
        clean_rules = parameters.get("clean_rules", [])
        table_name = parameters.get("table_name")

        if not table_name:
            return {"success": False, "error": "未指定表名"}

        # 更新进度
        self.update_progress(task.id, 10, db)

        # 连接到数据库
        engine, error = await self._connect_to_database(data_source)
        if error:
            return {"success": False, "error": error}

        # 更新进度
        self.update_progress(task.id, 20, db)

        # 读取表数据
        try:
            query = f"SELECT * FROM {table_name}"
            df, error = await self._execute_query(engine, query)
            if error:
                return {"success": False, "error": error}

            # 记录原始数据统计信息
            original_shape = df.shape
            original_null_count = df.isnull().sum().sum()

            # 更新进度
            self.update_progress(task.id, 30, db)

            # 应用清洗规则
            cleaning_results = []
            total_steps = len(clean_rules)

            for i, rule in enumerate(clean_rules):
                # 检查是否请求取消
                if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                    return {"status": "cancelled"}

                # 获取规则信息
                rule_type = rule.get("type")
                column = rule.get("column")

                # 应用规则
                result = {"rule": rule, "applied": False, "message": ""}

                try:
                    if rule_type == "remove_duplicates":
                        # 去除重复行
                        subset = rule.get("subset", None)  # 可以指定基于哪些列去重
                        old_count = len(df)
                        df = df.drop_duplicates(subset=subset)
                        new_count = len(df)
                        result["applied"] = True
                        result["message"] = f"已删除 {old_count - new_count} 条重复记录"

                    elif rule_type == "fill_nulls" and column:
                        # 填充空值
                        method = rule.get("method", "mean")  # mean, median, mode, value
                        value = rule.get("value")

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        null_count = df[column].isnull().sum()

                        if method == "mean" and pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].mean())
                        elif method == "median" and pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].median())
                        elif method == "mode":
                            df[column] = df[column].fillna(df[column].mode()[0] if not df[column].mode().empty else None)
                        elif method == "value" and value is not None:
                            df[column] = df[column].fillna(value)

                        result["applied"] = True
                        result["message"] = f"已填充 {null_count} 个空值"

                    elif rule_type == "remove_outliers" and column:
                        # 移除异常值
                        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
                            result["message"] = f"列 {column} 不存在或不是数值类型"
                            continue

                        method = rule.get("method", "zscore")  # zscore, iqr
                        threshold = rule.get("threshold", 3.0)  # 对于zscore方法

                        old_count = len(df)

                        if method == "zscore":
                            # 使用Z-score方法检测异常值
                            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                            df = df[z_scores <= threshold]
                        elif method == "iqr":
                            # 使用IQR方法检测异常值
                            q1 = df[column].quantile(0.25)
                            q3 = df[column].quantile(0.75)
                            iqr = q3 - q1
                            lower_bound = q1 - (threshold * iqr)
                            upper_bound = q3 + (threshold * iqr)
                            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

                        new_count = len(df)
                        result["applied"] = True
                        result["message"] = f"已移除 {old_count - new_count} 条异常记录"

                    elif rule_type == "normalize" and column:
                        # 标准化/归一化数据
                        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
                            result["message"] = f"列 {column} 不存在或不是数值类型"
                            continue

                        method = rule.get("method", "minmax")  # minmax, zscore

                        if method == "minmax":
                            # Min-Max归一化
                            min_val = df[column].min()
                            max_val = df[column].max()
                            df[column] = (df[column] - min_val) / (max_val - min_val)
                        elif method == "zscore":
                            # Z-score标准化
                            mean = df[column].mean()
                            std = df[column].std()
                            df[column] = (df[column] - mean) / std

                        result["applied"] = True
                        result["message"] = f"已对列 {column} 进行{method}标准化"

                    else:
                        result["message"] = f"不支持的规则类型: {rule_type}"

                except Exception as e:
                    result["message"] = f"应用规则时出错: {str(e)}"

                cleaning_results.append(result)

                # 更新进度
                progress = 30 + int((i + 1) / total_steps * 60)
                self.update_progress(task.id, progress, db)

            # 计算清洗后的统计信息
            cleaned_shape = df.shape
            cleaned_null_count = df.isnull().sum().sum()

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "table_name": table_name,
                "original_rows": original_shape[0],
                "original_columns": original_shape[1],
                "original_null_count": int(original_null_count),
                "cleaned_rows": cleaned_shape[0],
                "cleaned_columns": cleaned_shape[1],
                "cleaned_null_count": int(cleaned_null_count),
                "removed_rows": original_shape[0] - cleaned_shape[0],
                "filled_nulls": int(original_null_count - cleaned_null_count),
                "cleaning_results": cleaning_results,
                "sample_data": df.head(10).to_dict(orient="records")
            }

        except Exception as e:
            error_msg = f"清洗数据时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _analyze_database(self, task: ProcessingTask, data_source: DatabaseSource, db: Session) -> Dict[str, Any]:
        """
        分析数据库数据
        :param task: 处理任务
        :param data_source: 数据库数据源
        :param db: 数据库会话
        :return: 分析结果
        """
        parameters = task.parameters or {}
        analysis_type = parameters.get("analysis_type")
        table_name = parameters.get("table_name")

        if not table_name:
            return {"success": False, "error": "未指定表名"}

        # 更新进度
        self.update_progress(task.id, 10, db)

        # 连接到数据库
        engine, error = await self._connect_to_database(data_source)
        if error:
            return {"success": False, "error": error}

        # 更新进度
        self.update_progress(task.id, 20, db)

        # 读取表数据
        try:
            query = f"SELECT * FROM {table_name}"
            df, error = await self._execute_query(engine, query)
            if error:
                return {"success": False, "error": error}

            # 更新进度
            self.update_progress(task.id, 40, db)

            # 根据分析类型执行不同的分析
            if analysis_type == "descriptive":
                # 描述性统计分析
                result = await self._descriptive_analysis(df)
            elif analysis_type == "correlation":
                # 相关性分析
                result = await self._correlation_analysis(df)
            elif analysis_type == "distribution":
                # 分布分析
                column = parameters.get("column")
                if not column or column not in df.columns:
                    return {"success": False, "error": f"未指定有效的列名: {column}"}
                result = await self._distribution_analysis(df, column)
            else:
                return {"success": False, "error": f"不支持的分析类型: {analysis_type}"}

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "analysis_type": analysis_type,
                "table_name": table_name,
                "row_count": len(df),
                "column_count": len(df.columns),
                "result": result
            }

        except Exception as e:
            error_msg = f"分析数据时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _descriptive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        描述性统计分析
        :param df: 数据框
        :return: 分析结果
        """
        result = {
            "numeric_columns": {},
            "categorical_columns": {},
            "null_counts": {},
            "unique_counts": {}
        }

        # 分析数值列
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            # 计算基本统计量
            desc = numeric_df.describe().transpose()
            for column in desc.index:
                result["numeric_columns"][column] = {
                    "count": int(desc.loc[column, "count"]),
                    "mean": float(desc.loc[column, "mean"]),
                    "std": float(desc.loc[column, "std"]),
                    "min": float(desc.loc[column, "min"]),
                    "25%": float(desc.loc[column, "25%"]),
                    "50%": float(desc.loc[column, "50%"]),
                    "75%": float(desc.loc[column, "75%"]),
                    "max": float(desc.loc[column, "max"])
                }

        # 分析分类列
        categorical_df = df.select_dtypes(exclude=[np.number])
        if not categorical_df.empty:
            for column in categorical_df.columns:
                # 获取前10个最常见的值及其频率
                value_counts = categorical_df[column].value_counts().head(10)
                result["categorical_columns"][column] = {
                    "top_values": {str(k): int(v) for k, v in value_counts.items()}
                }

        # 计算空值数量
        for column in df.columns:
            result["null_counts"][column] = int(df[column].isnull().sum())

        # 计算唯一值数量
        for column in df.columns:
            result["unique_counts"][column] = int(df[column].nunique())

        return result

    async def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        相关性分析
        :param df: 数据框
        :return: 分析结果
        """
        # 只分析数值列
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {"error": "没有数值列可以进行相关性分析"}

        # 计算相关系数矩阵
        corr_matrix = numeric_df.corr().fillna(0).round(4)

        # 转换为字典格式
        corr_dict = {}
        for column in corr_matrix.columns:
            corr_dict[column] = {
                col: float(corr_matrix.loc[column, col])
                for col in corr_matrix.columns
            }

        # 找出高相关性的列对
        high_correlations = []
        for i, col1 in enumerate(corr_matrix.columns):
            for col2 in corr_matrix.columns[i+1:]:
                corr_value = abs(corr_matrix.loc[col1, col2])
                if corr_value > 0.7:  # 相关系数绝对值大于0.7视为高相关
                    high_correlations.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": float(corr_matrix.loc[col1, col2])
                    })

        return {
            "correlation_matrix": corr_dict,
            "high_correlations": high_correlations
        }

    async def _distribution_analysis(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        分布分析
        :param df: 数据框
        :param column: 列名
        :return: 分析结果
        """
        if column not in df.columns:
            return {"error": f"列 {column} 不存在"}

        result = {}

        # 检查列的数据类型
        if pd.api.types.is_numeric_dtype(df[column]):
            # 数值列分析

            # 基本统计量
            desc = df[column].describe()
            result["statistics"] = {
                "count": int(desc["count"]),
                "mean": float(desc["mean"]),
                "std": float(desc["std"]),
                "min": float(desc["min"]),
                "25%": float(desc["25%"]),
                "50%": float(desc["50%"]),
                "75%": float(desc["75%"]),
                "max": float(desc["max"])
            }

            # 计算分位数
            percentiles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            result["percentiles"] = {
                f"{int(p*100)}%": float(df[column].quantile(p))
                for p in percentiles
            }

            # 计算偏度和峰度
            result["skewness"] = float(df[column].skew())
            result["kurtosis"] = float(df[column].kurtosis())

            # 计算直方图数据
            hist, bin_edges = np.histogram(df[column].dropna(), bins=10)
            result["histogram"] = {
                "counts": [int(count) for count in hist],
                "bin_edges": [float(edge) for edge in bin_edges]
            }

        else:
            # 分类列分析

            # 计算频率分布
            value_counts = df[column].value_counts()
            result["value_counts"] = {
                str(k): int(v) for k, v in value_counts.items()
            }

            # 计算频率占比
            value_percentages = df[column].value_counts(normalize=True) * 100
            result["value_percentages"] = {
                str(k): float(v) for k, v in value_percentages.items()
            }

        return result

    async def _transform_database(self, task: ProcessingTask, data_source: DatabaseSource, db: Session) -> Dict[str, Any]:
        """
        转换数据库数据
        :param task: 处理任务
        :param data_source: 数据库数据源
        :param db: 数据库会话
        :return: 转换结果
        """
        parameters = task.parameters or {}
        transform_rules = parameters.get("transform_rules", [])
        table_name = parameters.get("table_name")

        if not table_name:
            return {"success": False, "error": "未指定表名"}

        # 更新进度
        self.update_progress(task.id, 10, db)

        # 连接到数据库
        engine, error = await self._connect_to_database(data_source)
        if error:
            return {"success": False, "error": error}

        # 更新进度
        self.update_progress(task.id, 20, db)

        # 读取表数据
        try:
            query = f"SELECT * FROM {table_name}"
            df, error = await self._execute_query(engine, query)
            if error:
                return {"success": False, "error": error}

            # 记录原始数据信息
            original_shape = df.shape
            original_columns = df.columns.tolist()

            # 更新进度
            self.update_progress(task.id, 30, db)

            # 应用转换规则
            transform_results = []
            total_steps = len(transform_rules)

            for i, rule in enumerate(transform_rules):
                # 检查是否请求取消
                if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                    return {"status": "cancelled"}

                # 获取规则信息
                rule_type = rule.get("type")

                # 应用规则
                result = {"rule": rule, "applied": False, "message": ""}

                try:
                    if rule_type == "rename_column":
                        # 重命名列
                        old_name = rule.get("old_name")
                        new_name = rule.get("new_name")

                        if old_name not in df.columns:
                            result["message"] = f"列 {old_name} 不存在"
                            continue

                        df = df.rename(columns={old_name: new_name})
                        result["applied"] = True
                        result["message"] = f"已将列 {old_name} 重命名为 {new_name}"

                    elif rule_type == "drop_column":
                        # 删除列
                        column = rule.get("column")

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        df = df.drop(columns=[column])
                        result["applied"] = True
                        result["message"] = f"已删除列 {column}"

                    elif rule_type == "convert_type":
                        # 转换数据类型
                        column = rule.get("column")
                        target_type = rule.get("target_type")  # int, float, str, datetime

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

                    elif rule_type == "create_column":
                        # 创建新列
                        new_column = rule.get("new_column")
                        expression = rule.get("expression")

                        if not expression:
                            result["message"] = "未指定表达式"
                            continue

                        # 使用eval执行表达式（注意：这在生产环境中可能存在安全风险）
                        # 在实际应用中，应该使用更安全的方法，如预定义的函数集
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

                    elif rule_type == "apply_function":
                        # 应用函数到列
                        column = rule.get("column")
                        function = rule.get("function")  # upper, lower, trim, etc.

                        if column not in df.columns:
                            result["message"] = f"列 {column} 不存在"
                            continue

                        if function == "upper" and pd.api.types.is_string_dtype(df[column]):
                            df[column] = df[column].str.upper()
                        elif function == "lower" and pd.api.types.is_string_dtype(df[column]):
                            df[column] = df[column].str.lower()
                        elif function == "trim" and pd.api.types.is_string_dtype(df[column]):
                            df[column] = df[column].str.strip()
                        elif function == "abs" and pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].abs()
                        elif function == "round" and pd.api.types.is_numeric_dtype(df[column]):
                            decimals = rule.get("decimals", 2)
                            df[column] = df[column].round(decimals)
                        else:
                            result["message"] = f"不支持的函数: {function}"
                            continue

                        result["applied"] = True
                        result["message"] = f"已对列 {column} 应用 {function} 函数"

                    else:
                        result["message"] = f"不支持的规则类型: {rule_type}"

                except Exception as e:
                    result["message"] = f"应用规则时出错: {str(e)}"

                transform_results.append(result)

                # 更新进度
                progress = 30 + int((i + 1) / total_steps * 60)
                self.update_progress(task.id, progress, db)

            # 计算转换后的数据信息
            transformed_shape = df.shape
            transformed_columns = df.columns.tolist()

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "table_name": table_name,
                "original_rows": original_shape[0],
                "original_columns": original_columns,
                "transformed_rows": transformed_shape[0],
                "transformed_columns": transformed_columns,
                "added_columns": [col for col in transformed_columns if col not in original_columns],
                "removed_columns": [col for col in original_columns if col not in transformed_columns],
                "transform_results": transform_results,
                "sample_data": df.head(10).to_dict(orient="records")
            }

        except Exception as e:
            error_msg = f"转换数据时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _query_database(self, task: ProcessingTask, data_source: DatabaseSource, db: Session) -> Dict[str, Any]:
        """
        查询数据库
        :param task: 处理任务
        :param data_source: 数据库数据源
        :param db: 数据库会话
        :return: 查询结果
        """
        parameters = task.parameters or {}
        query = parameters.get("query", "")

        # 更新进度
        self.update_progress(task.id, 10, db)

        # 连接到数据库
        engine, error = await self._connect_to_database(data_source)
        if error:
            return {"success": False, "error": error}

        # 更新进度
        self.update_progress(task.id, 30, db)

        # 执行查询
        df, error = await self._execute_query(engine, query)
        if error:
            return {"success": False, "error": error}

        # 更新进度
        self.update_progress(task.id, 70, db)

        # 处理结果
        try:
            # 将DataFrame转换为字典列表
            records = df.to_dict(orient="records")

            # 获取列信息
            columns = df.columns.tolist()

            # 获取基本统计信息
            stats = {}
            for col in df.select_dtypes(include=[np.number]).columns:
                stats[col] = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std())
                }

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回结果
            return {
                "success": True,
                "query": query,
                "row_count": len(df),
                "column_count": len(columns),
                "columns": columns,
                "records": records[:100],  # 只返回前100条记录，避免数据过大
                "has_more": len(records) > 100,
                "total_records": len(records),
                "statistics": stats
            }
        except Exception as e:
            error_msg = f"处理查询结果时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

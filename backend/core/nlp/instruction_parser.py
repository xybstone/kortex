"""
自然语言指令解析器
将用户的自然语言指令转换为处理任务参数
"""
import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Union

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstructionParser:
    """自然语言指令解析器"""

    def __init__(self, llm: BaseLLM):
        """
        初始化解析器
        :param llm: 大型语言模型
        """
        self.llm = llm
        self._init_prompts()

    def _init_prompts(self):
        """初始化提示模板"""
        # 通用任务识别提示
        self.task_identification_template = PromptTemplate(
            input_variables=["instruction"],
            template="""
            你是一个数据处理助手，需要将用户的自然语言指令转换为结构化的任务参数。
            
            用户指令: {instruction}
            
            请分析这个指令，并确定用户想要执行的任务类型。可能的任务类型包括：
            1. 数据库处理 (database_process)
            2. 文件处理 (file_process)
            3. URL处理 (url_process)
            
            对于数据库处理，可能的子任务包括：
            - database_clean: 数据清洗
            - database_analyze: 数据分析
            - database_transform: 数据转换
            - database_query: 数据查询
            
            对于文件处理，可能的子任务包括：
            - file_embed: 文件嵌入
            - file_extract: 内容提取
            - file_convert: 格式转换
            - file_analyze: 文件分析
            - csv_process: CSV处理
            - text_process: 文本处理
            
            对于URL处理，可能的子任务包括：
            - url_crawl: 网页爬取
            - url_extract: 内容提取
            - url_monitor: 变更监控
            - url_analyze: 网页分析
            - url_screenshot: 网页截图
            - url_sitemap: 站点地图生成
            
            请以JSON格式返回以下信息：
            1. task_type: 主任务类型 (database_process, file_process, url_process)
            2. sub_task_type: 子任务类型
            3. confidence: 你对这个分类的置信度 (0-1)
            4. reasoning: 你的推理过程
            
            JSON格式示例:
            {
                "task_type": "database_process",
                "sub_task_type": "database_clean",
                "confidence": 0.85,
                "reasoning": "用户提到了'清理数据库中的重复记录'，这明显是一个数据库清洗任务。"
            }
            
            只返回JSON对象，不要有其他文本。
            """
        )

        # 数据库处理参数提取提示
        self.database_params_template = PromptTemplate(
            input_variables=["instruction", "sub_task_type"],
            template="""
            你是一个数据处理助手，需要将用户关于数据库处理的自然语言指令转换为结构化的任务参数。
            
            用户指令: {instruction}
            任务类型: {sub_task_type}
            
            根据任务类型，请提取以下参数：
            
            对于 database_clean (数据清洗)：
            - table_name: 要清洗的表名
            - clean_rules: 清洗规则列表，每个规则包含type(规则类型)和其他必要参数
              规则类型可以是：remove_duplicates(去重), fill_nulls(填充空值), remove_outliers(移除异常值), normalize(标准化)
            
            对于 database_analyze (数据分析)：
            - table_name: 要分析的表名
            - analysis_type: 分析类型，可以是descriptive(描述性统计), correlation(相关性分析), distribution(分布分析)
            - column: 如果是针对特定列的分析，指定列名
            
            对于 database_transform (数据转换)：
            - table_name: 要转换的表名
            - transform_rules: 转换规则列表，每个规则包含type(规则类型)和其他必要参数
              规则类型可以是：rename_column(重命名列), drop_column(删除列), convert_type(转换类型), create_column(创建新列), apply_function(应用函数)
            
            对于 database_query (数据查询)：
            - query: SQL查询语句
            
            请以JSON格式返回参数，示例：
            {
                "table_name": "users",
                "clean_rules": [
                    {"type": "remove_duplicates", "subset": ["email"]},
                    {"type": "fill_nulls", "column": "age", "method": "mean"}
                ]
            }
            
            只返回JSON对象，不要有其他文本。
            """
        )

        # 文件处理参数提取提示
        self.file_params_template = PromptTemplate(
            input_variables=["instruction", "sub_task_type"],
            template="""
            你是一个数据处理助手，需要将用户关于文件处理的自然语言指令转换为结构化的任务参数。
            
            用户指令: {instruction}
            任务类型: {sub_task_type}
            
            根据任务类型，请提取以下参数：
            
            对于 file_analyze (文件分析)：
            - analysis_type: 分析类型，可以是basic(基本分析), content(内容分析), structure(结构分析)
            
            对于 csv_process (CSV处理)：
            - operations: 操作列表，每个操作包含type(操作类型)和其他必要参数
              操作类型可以是：filter_rows(过滤行), select_columns(选择列), rename_columns(重命名列), sort(排序), 
              fill_nulls(填充空值), create_column(创建新列), drop_duplicates(删除重复行), convert_type(转换类型)
            - encoding: 文件编码，如utf-8
            - output_path: 输出文件路径
            
            对于 text_process (文本处理)：
            - operations: 操作列表，每个操作包含type(操作类型)和其他必要参数
              操作类型可以是：replace_text(替换文本), regex_replace(正则替换), insert_text(插入文本), 
              remove_lines(删除行), filter_lines(过滤行), convert_case(转换大小写)
            - encoding: 文件编码，如utf-8
            - output_path: 输出文件路径
            
            对于 file_embed (文件嵌入)：
            - embed_model: 嵌入模型名称
            
            对于 file_extract (内容提取)：
            - extract_type: 提取类型，如text, table, image
            
            对于 file_convert (格式转换)：
            - target_format: 目标格式，如pdf, docx, txt
            
            请以JSON格式返回参数，示例：
            {
                "operations": [
                    {"type": "filter_rows", "column": "age", "condition": "gt", "value": 18},
                    {"type": "select_columns", "columns": ["name", "email", "age"]}
                ],
                "encoding": "utf-8"
            }
            
            只返回JSON对象，不要有其他文本。
            """
        )

        # URL处理参数提取提示
        self.url_params_template = PromptTemplate(
            input_variables=["instruction", "sub_task_type"],
            template="""
            你是一个数据处理助手，需要将用户关于URL处理的自然语言指令转换为结构化的任务参数。
            
            用户指令: {instruction}
            任务类型: {sub_task_type}
            
            根据任务类型，请提取以下参数：
            
            对于 url_crawl (网页爬取)：
            - crawl_depth: 爬取深度，默认为1
            - max_pages: 最大爬取页面数，默认为100
            - follow_external: 是否跟随外部链接，默认为false
            
            对于 url_extract (内容提取)：
            - extract_rules: 提取规则列表，每个规则包含type(规则类型), selector(选择器), attribute(属性，可选), name(名称，可选)
              规则类型可以是：css, xpath, regex, json
            
            对于 url_monitor (变更监控)：
            - monitor_interval: 监控间隔（秒），默认为60
            - monitor_type: 监控类型，可以是content(内容), text(文本), selector(选择器)
            - selector: 如果monitor_type为selector，需要指定CSS选择器
            - check_count: 检查次数，默认为1
            
            对于 url_analyze (网页分析)：
            - analysis_type: 分析类型，可以是general(通用), seo(SEO分析), performance(性能分析), links(链接分析), content(内容分析), all(全部)
            
            对于 url_screenshot (网页截图)：
            - width: 截图宽度，默认为1280
            - height: 截图高度，默认为800
            - full_page: 是否截取整个页面，默认为false
            
            对于 url_sitemap (站点地图生成)：
            - max_depth: 最大深度，默认为2
            - max_pages: 最大页面数，默认为100
            
            请以JSON格式返回参数，示例：
            {
                "crawl_depth": 2,
                "max_pages": 50,
                "follow_external": false
            }
            
            只返回JSON对象，不要有其他文本。
            """
        )

    async def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        解析用户指令
        :param instruction: 用户指令
        :return: 解析结果
        """
        try:
            # 1. 识别任务类型
            task_chain = LLMChain(llm=self.llm, prompt=self.task_identification_template)
            task_result = await task_chain.arun(instruction=instruction)
            task_info = json.loads(task_result)
            
            logger.info(f"任务识别结果: {task_info}")
            
            # 2. 根据任务类型提取参数
            if task_info["task_type"] == "database_process":
                params_chain = LLMChain(llm=self.llm, prompt=self.database_params_template)
                params_result = await params_chain.arun(
                    instruction=instruction,
                    sub_task_type=task_info["sub_task_type"]
                )
                
            elif task_info["task_type"] == "file_process":
                params_chain = LLMChain(llm=self.llm, prompt=self.file_params_template)
                params_result = await params_chain.arun(
                    instruction=instruction,
                    sub_task_type=task_info["sub_task_type"]
                )
                
            elif task_info["task_type"] == "url_process":
                params_chain = LLMChain(llm=self.llm, prompt=self.url_params_template)
                params_result = await params_chain.arun(
                    instruction=instruction,
                    sub_task_type=task_info["sub_task_type"]
                )
                
            else:
                return {
                    "success": False,
                    "error": f"不支持的任务类型: {task_info['task_type']}"
                }
                
            # 3. 解析参数
            params = json.loads(params_result)
            
            # 4. 返回结果
            return {
                "success": True,
                "task_type": task_info["sub_task_type"],
                "parameters": params,
                "confidence": task_info["confidence"],
                "reasoning": task_info["reasoning"]
            }
            
        except Exception as e:
            logger.error(f"解析指令时出错: {str(e)}")
            return {
                "success": False,
                "error": f"解析指令时出错: {str(e)}"
            }

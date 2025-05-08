"""
URL处理器模块
实现URL数据的爬取和处理
"""
import asyncio
import logging
import re
import json
import time
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from sqlalchemy.orm import Session
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from models.domain.dataset import ProcessingTask, URLSource
from core.processing.base import BaseDataProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLProcessor(BaseDataProcessor):
    """URL处理器"""

    def get_supported_task_types(self) -> List[str]:
        """获取支持的任务类型"""
        return [
            "url_crawl",       # 网页爬取
            "url_extract",     # 内容提取
            "url_monitor",     # 变更监控
            "url_analyze",     # 网页分析
            "url_screenshot",  # 网页截图
            "url_sitemap"      # 站点地图生成
        ]

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证任务参数"""
        # 根据不同的任务类型验证参数
        task_type = parameters.get("task_type")

        if task_type == "url_crawl":
            # 爬取任务需要指定爬取深度
            return "crawl_depth" in parameters

        elif task_type == "url_extract":
            # 提取任务需要指定提取规则
            return "extract_rules" in parameters

        elif task_type == "url_monitor":
            # 监控任务需要指定监控间隔
            return "monitor_interval" in parameters

        elif task_type == "url_analyze":
            # 分析任务需要指定分析类型
            return "analysis_type" in parameters

        elif task_type == "url_screenshot":
            # 截图任务需要指定截图选项
            return True  # 截图任务不需要额外参数

        elif task_type == "url_sitemap":
            # 站点地图生成任务需要指定最大深度
            return "max_depth" in parameters

        return False

    async def _execute_task(self, task: ProcessingTask, db: Session) -> Dict[str, Any]:
        """执行具体的处理逻辑"""
        # 获取数据源
        data_source = db.query(URLSource).filter(
            URLSource.id == task.data_source_id
        ).first()

        if not data_source:
            raise ValueError(f"数据源不存在: {task.data_source_id}")

        # 根据任务类型执行不同的处理逻辑
        if task.task_type == "url_crawl":
            return await self._crawl_url(task, data_source, db)

        elif task.task_type == "url_extract":
            return await self._extract_url(task, data_source, db)

        elif task.task_type == "url_monitor":
            return await self._monitor_url(task, data_source, db)

        elif task.task_type == "url_analyze":
            return await self._analyze_url(task, data_source, db)

        elif task.task_type == "url_screenshot":
            return await self._screenshot_url(task, data_source, db)

        elif task.task_type == "url_sitemap":
            return await self._generate_sitemap(task, data_source, db)

        raise ValueError(f"不支持的任务类型: {task.task_type}")

    async def _crawl_url(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        爬取URL数据
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 爬取结果
        """
        parameters = task.parameters or {}
        crawl_depth = parameters.get("crawl_depth", data_source.crawl_depth)
        max_pages = parameters.get("max_pages", 100)  # 最大爬取页面数
        follow_external = parameters.get("follow_external", False)  # 是否跟随外部链接
        respect_robots = parameters.get("respect_robots", True)  # 是否遵循robots.txt

        # 更新进度
        self.update_progress(task.id, 5, db)

        try:
            # 初始化爬取状态
            start_url = data_source.url
            visited_urls = set()
            pending_urls = {start_url}
            current_depth = 0
            results = {
                "pages": [],
                "links": set(),
                "errors": []
            }

            # 创建一个异步HTTP会话
            async with aiohttp.ClientSession() as session:
                # 按深度爬取
                while current_depth <= crawl_depth and pending_urls and len(visited_urls) < max_pages:
                    # 检查是否请求取消
                    if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                        return {"status": "cancelled"}

                    # 获取当前层级的URL
                    current_urls = pending_urls
                    pending_urls = set()

                    # 爬取当前层级的所有URL
                    for url in current_urls:
                        # 检查是否已访问
                        if url in visited_urls:
                            continue

                        # 标记为已访问
                        visited_urls.add(url)

                        # 检查是否请求取消
                        if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                            return {"status": "cancelled"}

                        try:
                            # 爬取页面
                            page_info = await self._fetch_page(session, url)

                            # 保存页面信息
                            results["pages"].append(page_info)

                            # 提取链接
                            if current_depth < crawl_depth:
                                links = self._extract_links(page_info["html"], url, follow_external)

                                # 添加到待爬取队列
                                for link in links:
                                    if link not in visited_urls:
                                        pending_urls.add(link)
                                        results["links"].add(link)

                        except Exception as e:
                            # 记录错误
                            error = {"url": url, "error": str(e)}
                            results["errors"].append(error)
                            logger.error(f"爬取URL时出错: {url} - {str(e)}")

                        # 更新进度
                        progress = 5 + int(len(visited_urls) / max(max_pages, len(visited_urls) + len(pending_urls)) * 90)
                        self.update_progress(task.id, min(95, progress), db)

                    # 增加深度
                    current_depth += 1

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "url": data_source.url,
                "crawl_depth": crawl_depth,
                "pages_crawled": len(results["pages"]),
                "links_found": len(results["links"]),
                "errors": len(results["errors"]),
                "pages": [
                    {
                        "url": page["url"],
                        "title": page["title"],
                        "status": page["status"],
                        "content_type": page["content_type"],
                        "size": page["size"]
                    }
                    for page in results["pages"][:20]  # 只返回前20个页面信息
                ],
                "sample_links": list(results["links"])[:50],  # 只返回前50个链接
                "error_details": results["errors"][:10]  # 只返回前10个错误详情
            }

        except Exception as e:
            error_msg = f"爬取URL时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """
        获取页面内容
        :param session: HTTP会话
        :param url: 页面URL
        :return: 页面信息
        """
        start_time = time.time()

        try:
            async with session.get(url, timeout=30) as response:
                # 读取响应内容
                html = await response.text()

                # 解析HTML
                soup = BeautifulSoup(html, 'html.parser')

                # 提取标题
                title = soup.title.string if soup.title else ""

                # 计算页面大小
                size = len(html)

                # 获取响应头信息
                headers = dict(response.headers)
                content_type = headers.get('Content-Type', '')

                # 返回页面信息
                return {
                    "url": url,
                    "status": response.status,
                    "title": title,
                    "html": html,
                    "content_type": content_type,
                    "size": size,
                    "headers": headers,
                    "fetch_time": time.time() - start_time
                }

        except Exception as e:
            # 返回错误信息
            return {
                "url": url,
                "status": 0,
                "title": "",
                "html": "",
                "content_type": "",
                "size": 0,
                "headers": {},
                "fetch_time": time.time() - start_time,
                "error": str(e)
            }

    def _extract_links(self, html: str, base_url: str, follow_external: bool = False) -> Set[str]:
        """
        从HTML中提取链接
        :param html: HTML内容
        :param base_url: 基础URL
        :param follow_external: 是否跟随外部链接
        :return: 链接集合
        """
        links = set()

        try:
            # 解析HTML
            soup = BeautifulSoup(html, 'html.parser')

            # 提取基础域名
            base_domain = self._extract_domain(base_url)

            # 提取所有链接
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']

                # 处理相对URL
                if href.startswith('/'):
                    # 构建完整URL
                    if base_url.endswith('/'):
                        full_url = base_url[:-1] + href
                    else:
                        full_url = base_url + href
                elif href.startswith('#') or href.startswith('javascript:'):
                    # 忽略页内链接和JavaScript链接
                    continue
                elif not href.startswith(('http://', 'https://')):
                    # 其他相对路径
                    if base_url.endswith('/'):
                        full_url = base_url + href
                    else:
                        full_url = base_url + '/' + href
                else:
                    # 绝对URL
                    full_url = href

                # 检查是否为外部链接
                if not follow_external and self._extract_domain(full_url) != base_domain:
                    continue

                # 添加到链接集合
                links.add(full_url)

        except Exception as e:
            logger.error(f"提取链接时出错: {str(e)}")

        return links

    def _extract_domain(self, url: str) -> str:
        """
        从URL中提取域名
        :param url: URL
        :return: 域名
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except Exception:
            return ""

    async def _extract_url(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        提取URL数据
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 提取结果
        """
        parameters = task.parameters or {}
        extract_rules = parameters.get("extract_rules", [])

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            # 创建一个异步HTTP会话
            async with aiohttp.ClientSession() as session:
                # 获取页面内容
                page_info = await self._fetch_page(session, data_source.url)

                # 检查是否成功获取页面
                if "error" in page_info:
                    return {
                        "success": False,
                        "error": f"获取页面失败: {page_info.get('error')}"
                    }

                # 更新进度
                self.update_progress(task.id, 30, db)

                # 应用提取规则
                extracted_data = []
                total_steps = len(extract_rules)

                for i, rule in enumerate(extract_rules):
                    # 检查是否请求取消
                    if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                        return {"status": "cancelled"}

                    # 获取规则信息
                    rule_type = rule.get("type")
                    selector = rule.get("selector")
                    attribute = rule.get("attribute")
                    name = rule.get("name", f"item_{i+1}")

                    # 应用规则
                    result = {"rule": rule, "name": name, "items": []}

                    try:
                        if rule_type == "css" and selector:
                            # CSS选择器
                            items = self._extract_by_css(page_info["html"], selector, attribute)
                            result["items"] = items

                        elif rule_type == "xpath" and selector:
                            # XPath选择器
                            items = self._extract_by_xpath(page_info["html"], selector, attribute)
                            result["items"] = items

                        elif rule_type == "regex" and selector:
                            # 正则表达式
                            items = self._extract_by_regex(page_info["html"], selector)
                            result["items"] = items

                        elif rule_type == "json" and selector:
                            # JSON路径
                            items = self._extract_by_json(page_info["html"], selector)
                            result["items"] = items

                        else:
                            result["error"] = f"不支持的规则类型: {rule_type}"

                    except Exception as e:
                        result["error"] = f"应用规则时出错: {str(e)}"

                    extracted_data.append(result)

                    # 更新进度
                    progress = 30 + int((i + 1) / total_steps * 65)
                    self.update_progress(task.id, progress, db)

                # 更新进度
                self.update_progress(task.id, 100, db)

                # 返回处理结果
                return {
                    "success": True,
                    "url": data_source.url,
                    "title": page_info["title"],
                    "rules_applied": len(extract_rules),
                    "extracted_data": extracted_data
                }

        except Exception as e:
            error_msg = f"提取URL数据时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _extract_by_css(self, html: str, selector: str, attribute: str = None) -> List[str]:
        """
        使用CSS选择器提取数据
        :param html: HTML内容
        :param selector: CSS选择器
        :param attribute: 要提取的属性，如果为None则提取文本内容
        :return: 提取的数据列表
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)

            if attribute:
                # 提取指定属性
                return [element.get(attribute, "") for element in elements if element.has_attr(attribute)]
            else:
                # 提取文本内容
                return [element.get_text(strip=True) for element in elements]

        except Exception as e:
            logger.error(f"使用CSS选择器提取数据时出错: {str(e)}")
            return []

    def _extract_by_xpath(self, html: str, xpath: str, attribute: str = None) -> List[str]:
        """
        使用XPath提取数据
        :param html: HTML内容
        :param xpath: XPath表达式
        :param attribute: 要提取的属性，如果为None则提取文本内容
        :return: 提取的数据列表
        """
        try:
            from lxml import etree

            # 解析HTML
            tree = etree.HTML(html)

            # 应用XPath
            elements = tree.xpath(xpath)

            if attribute:
                # 提取指定属性
                return [element.get(attribute, "") for element in elements if hasattr(element, 'get')]
            else:
                # 提取文本内容
                return [element.text.strip() if hasattr(element, 'text') and element.text else "" for element in elements]

        except Exception as e:
            logger.error(f"使用XPath提取数据时出错: {str(e)}")
            return []

    def _extract_by_regex(self, html: str, pattern: str) -> List[str]:
        """
        使用正则表达式提取数据
        :param html: HTML内容
        :param pattern: 正则表达式模式
        :return: 提取的数据列表
        """
        try:
            # 应用正则表达式
            matches = re.findall(pattern, html)

            # 处理结果
            if matches:
                if isinstance(matches[0], tuple):
                    # 如果匹配结果是元组（有分组），则返回第一个分组
                    return [match[0] if match else "" for match in matches]
                else:
                    # 否则返回完整匹配
                    return matches
            else:
                return []

        except Exception as e:
            logger.error(f"使用正则表达式提取数据时出错: {str(e)}")
            return []

    def _extract_by_json(self, html: str, path: str) -> List[Any]:
        """
        从JSON中提取数据
        :param html: HTML内容（可能包含JSON）
        :param path: JSON路径（使用点号分隔，如data.items）
        :return: 提取的数据列表
        """
        try:
            # 尝试解析JSON
            try:
                # 首先尝试直接解析整个内容
                data = json.loads(html)
            except json.JSONDecodeError:
                # 如果失败，尝试从HTML中提取JSON
                json_pattern = r'<script[^>]*type=["\'](application|text)/json["\'][^>]*>(.*?)</script>'
                matches = re.findall(json_pattern, html, re.DOTALL)

                if matches:
                    for _, content in matches:
                        try:
                            data = json.loads(content)
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    # 尝试查找常见的JSON变量
                    var_pattern = r'var\s+(\w+)\s*=\s*({.*?});'
                    matches = re.findall(var_pattern, html, re.DOTALL)

                    if matches:
                        for _, content in matches:
                            try:
                                data = json.loads(content)
                                break
                            except json.JSONDecodeError:
                                continue
                    else:
                        return []

            # 应用JSON路径
            parts = path.split('.')
            current = data

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return []
                else:
                    return []

            # 处理结果
            if isinstance(current, list):
                return current
            else:
                return [current]

        except Exception as e:
            logger.error(f"从JSON中提取数据时出错: {str(e)}")
            return []

    async def _monitor_url(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        监控URL变化
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 监控结果
        """
        parameters = task.parameters or {}
        monitor_interval = parameters.get("monitor_interval", 60)  # 默认60秒
        monitor_type = parameters.get("monitor_type", "content")  # content, hash, selector
        selector = parameters.get("selector")  # CSS选择器，用于监控特定内容
        check_count = parameters.get("check_count", 1)  # 检查次数

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            # 创建一个异步HTTP会话
            async with aiohttp.ClientSession() as session:
                # 获取初始页面内容
                initial_page = await self._fetch_page(session, data_source.url)

                # 检查是否成功获取页面
                if "error" in initial_page:
                    return {
                        "success": False,
                        "error": f"获取页面失败: {initial_page.get('error')}"
                    }

                # 计算初始哈希值
                initial_hash = self._calculate_content_hash(initial_page["html"], monitor_type, selector)

                # 更新进度
                self.update_progress(task.id, 30, db)

                # 监控变化
                changes_detected = 0
                check_results = []

                for i in range(check_count):
                    # 检查是否请求取消
                    if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                        return {"status": "cancelled"}

                    # 等待指定的时间间隔
                    if i > 0:  # 第一次检查不需要等待
                        # 为了演示，我们使用较短的等待时间
                        demo_wait = min(monitor_interval, 3)  # 最多等待3秒
                        await asyncio.sleep(demo_wait)

                    # 再次获取页面内容
                    current_page = await self._fetch_page(session, data_source.url)

                    # 检查是否成功获取页面
                    if "error" in current_page:
                        check_result = {
                            "check_time": datetime.datetime.now().isoformat(),
                            "success": False,
                            "error": current_page.get("error")
                        }
                    else:
                        # 计算当前哈希值
                        current_hash = self._calculate_content_hash(current_page["html"], monitor_type, selector)

                        # 检查是否发生变化
                        changed = initial_hash != current_hash

                        if changed:
                            changes_detected += 1

                        # 记录检查结果
                        check_result = {
                            "check_time": datetime.datetime.now().isoformat(),
                            "success": True,
                            "changed": changed,
                            "initial_hash": initial_hash,
                            "current_hash": current_hash
                        }

                        # 如果使用选择器，添加提取的内容
                        if monitor_type == "selector" and selector:
                            initial_content = self._extract_by_css(initial_page["html"], selector)
                            current_content = self._extract_by_css(current_page["html"], selector)
                            check_result["initial_content"] = initial_content
                            check_result["current_content"] = current_content

                    check_results.append(check_result)

                    # 更新进度
                    progress = 30 + int((i + 1) / check_count * 65)
                    self.update_progress(task.id, progress, db)

                # 更新进度
                self.update_progress(task.id, 100, db)

                # 返回处理结果
                return {
                    "success": True,
                    "url": data_source.url,
                    "monitor_type": monitor_type,
                    "monitor_interval": monitor_interval,
                    "checks_performed": check_count,
                    "changes_detected": changes_detected,
                    "check_results": check_results,
                    "status": "active",
                    "last_check_time": datetime.datetime.now().isoformat()
                }

        except Exception as e:
            error_msg = f"监控URL时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def _analyze_url(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        分析网页内容
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 分析结果
        """
        parameters = task.parameters or {}
        analysis_type = parameters.get("analysis_type", "general")  # general, seo, performance, links

        # 更新进度
        self.update_progress(task.id, 10, db)

        try:
            # 创建一个异步HTTP会话
            async with aiohttp.ClientSession() as session:
                # 获取页面内容
                page_info = await self._fetch_page(session, data_source.url)

                # 检查是否成功获取页面
                if "error" in page_info:
                    return {
                        "success": False,
                        "error": f"获取页面失败: {page_info.get('error')}"
                    }

                # 更新进度
                self.update_progress(task.id, 30, db)

                # 根据分析类型执行不同的分析
                analysis_result = {}

                if analysis_type == "general" or analysis_type == "all":
                    # 通用分析
                    analysis_result["general"] = self._analyze_general(page_info)

                if analysis_type == "seo" or analysis_type == "all":
                    # SEO分析
                    analysis_result["seo"] = self._analyze_seo(page_info)

                if analysis_type == "performance" or analysis_type == "all":
                    # 性能分析
                    analysis_result["performance"] = self._analyze_performance(page_info)

                if analysis_type == "links" or analysis_type == "all":
                    # 链接分析
                    analysis_result["links"] = self._analyze_links(page_info)

                if analysis_type == "content" or analysis_type == "all":
                    # 内容分析
                    analysis_result["content"] = self._analyze_content(page_info)

                # 更新进度
                self.update_progress(task.id, 100, db)

                # 返回处理结果
                return {
                    "success": True,
                    "url": data_source.url,
                    "title": page_info["title"],
                    "analysis_type": analysis_type,
                    "analysis_result": analysis_result
                }

        except Exception as e:
            error_msg = f"分析URL时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _analyze_general(self, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        通用网页分析
        :param page_info: 页面信息
        :return: 分析结果
        """
        try:
            html = page_info["html"]
            soup = BeautifulSoup(html, 'html.parser')

            # 基本信息
            result = {
                "url": page_info["url"],
                "title": page_info["title"],
                "status": page_info["status"],
                "content_type": page_info["content_type"],
                "size": page_info["size"],
                "size_human": self._format_size(page_info["size"]),
                "fetch_time": page_info["fetch_time"]
            }

            # 页面元数据
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content

            result["meta_tags"] = meta_tags

            # 页面统计
            result["stats"] = {
                "images": len(soup.find_all('img')),
                "links": len(soup.find_all('a')),
                "scripts": len(soup.find_all('script')),
                "styles": len(soup.find_all('style')) + len(soup.find_all('link', rel='stylesheet')),
                "forms": len(soup.find_all('form')),
                "tables": len(soup.find_all('table')),
                "iframes": len(soup.find_all('iframe')),
                "paragraphs": len(soup.find_all('p')),
                "headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
            }

            # 文本统计
            text = soup.get_text()
            words = text.split()
            result["text_stats"] = {
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len(re.findall(r'[.!?]+', text)),
                "paragraph_count": len(soup.find_all('p'))
            }

            return result

        except Exception as e:
            logger.error(f"通用分析时出错: {str(e)}")
            return {"error": str(e)}

    def _analyze_seo(self, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        SEO分析
        :param page_info: 页面信息
        :return: 分析结果
        """
        try:
            html = page_info["html"]
            soup = BeautifulSoup(html, 'html.parser')

            # 标题分析
            title = soup.title.string if soup.title else ""
            title_length = len(title) if title else 0

            # 描述分析
            description = ""
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag:
                description = description_tag.get('content', '')
            description_length = len(description) if description else 0

            # 关键词分析
            keywords = ""
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                keywords = keywords_tag.get('content', '')

            # 标题标签分析
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')

            # 图片分析
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]

            # 链接分析
            links = soup.find_all('a')
            internal_links = [link for link in links if link.get('href') and not link['href'].startswith(('http://', 'https://'))]
            external_links = [link for link in links if link.get('href') and link['href'].startswith(('http://', 'https://'))]

            # 移动友好性
            has_viewport = bool(soup.find('meta', attrs={'name': 'viewport'}))

            # 结构化数据
            has_schema = 'application/ld+json' in html or 'itemscope' in html or 'itemtype' in html

            # 规范链接
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            canonical_url = canonical['href'] if canonical else None

            # 返回结果
            return {
                "title": {
                    "text": title,
                    "length": title_length,
                    "is_good_length": 10 <= title_length <= 60
                },
                "description": {
                    "text": description,
                    "length": description_length,
                    "is_good_length": 50 <= description_length <= 160
                },
                "keywords": keywords.split(',') if keywords else [],
                "headings": {
                    "h1_count": len(h1_tags),
                    "h2_count": len(h2_tags),
                    "h3_count": len(h3_tags),
                    "h1_texts": [h.get_text() for h in h1_tags][:3]  # 只返回前3个
                },
                "images": {
                    "total": len(images),
                    "without_alt": len(images_without_alt),
                    "alt_percentage": (len(images) - len(images_without_alt)) / len(images) * 100 if images else 0
                },
                "links": {
                    "total": len(links),
                    "internal": len(internal_links),
                    "external": len(external_links)
                },
                "mobile_friendly": has_viewport,
                "structured_data": has_schema,
                "canonical_url": canonical_url,
                "issues": self._get_seo_issues(
                    title_length, description_length, len(h1_tags),
                    len(images_without_alt), has_viewport
                )
            }

        except Exception as e:
            logger.error(f"SEO分析时出错: {str(e)}")
            return {"error": str(e)}

    def _get_seo_issues(self, title_length: int, desc_length: int, h1_count: int,
                        img_without_alt: int, has_viewport: bool) -> List[str]:
        """
        获取SEO问题列表
        :return: 问题列表
        """
        issues = []

        if title_length == 0:
            issues.append("页面缺少标题")
        elif title_length < 10:
            issues.append("标题太短（建议10-60个字符）")
        elif title_length > 60:
            issues.append("标题太长（建议10-60个字符）")

        if desc_length == 0:
            issues.append("页面缺少描述")
        elif desc_length < 50:
            issues.append("描述太短（建议50-160个字符）")
        elif desc_length > 160:
            issues.append("描述太长（建议50-160个字符）")

        if h1_count == 0:
            issues.append("页面缺少H1标签")
        elif h1_count > 1:
            issues.append(f"页面有多个H1标签（{h1_count}个）")

        if img_without_alt > 0:
            issues.append(f"{img_without_alt}个图片缺少alt属性")

        if not has_viewport:
            issues.append("页面缺少viewport元标签，可能不适合移动设备")

        return issues

    def _analyze_performance(self, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        性能分析
        :param page_info: 页面信息
        :return: 分析结果
        """
        try:
            html = page_info["html"]
            soup = BeautifulSoup(html, 'html.parser')

            # 资源统计
            scripts = soup.find_all('script')
            styles = soup.find_all('link', rel='stylesheet')
            inline_styles = soup.find_all('style')
            images = soup.find_all('img')

            # 计算总大小
            html_size = len(html)

            # 分析脚本
            script_count = len(scripts)
            inline_script_count = len([s for s in scripts if not s.get('src')])
            external_script_count = script_count - inline_script_count

            # 分析样式
            style_count = len(styles) + len(inline_styles)
            inline_style_count = len(inline_styles)
            external_style_count = len(styles)

            # 分析图片
            image_count = len(images)

            # 返回结果
            return {
                "page_size": {
                    "bytes": html_size,
                    "human": self._format_size(html_size)
                },
                "load_time": page_info["fetch_time"],
                "resources": {
                    "total": script_count + style_count + image_count,
                    "scripts": {
                        "total": script_count,
                        "inline": inline_script_count,
                        "external": external_script_count
                    },
                    "styles": {
                        "total": style_count,
                        "inline": inline_style_count,
                        "external": external_style_count
                    },
                    "images": image_count
                },
                "recommendations": self._get_performance_recommendations(
                    html_size, script_count, external_script_count,
                    style_count, external_style_count, image_count
                )
            }

        except Exception as e:
            logger.error(f"性能分析时出错: {str(e)}")
            return {"error": str(e)}

    def _get_performance_recommendations(self, html_size: int, script_count: int,
                                        external_script_count: int, style_count: int,
                                        external_style_count: int, image_count: int) -> List[str]:
        """
        获取性能优化建议
        :return: 建议列表
        """
        recommendations = []

        if html_size > 100 * 1024:  # 100KB
            recommendations.append("HTML大小超过100KB，考虑减少页面大小")

        if script_count > 15:
            recommendations.append(f"页面包含{script_count}个脚本，考虑减少脚本数量")

        if external_script_count > 10:
            recommendations.append(f"页面加载{external_script_count}个外部脚本，考虑合并脚本")

        if style_count > 10:
            recommendations.append(f"页面包含{style_count}个样式表，考虑减少样式表数量")

        if external_style_count > 5:
            recommendations.append(f"页面加载{external_style_count}个外部样式表，考虑合并样式表")

        if image_count > 20:
            recommendations.append(f"页面包含{image_count}个图片，考虑减少图片数量或延迟加载")

        return recommendations

    def _analyze_links(self, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        链接分析
        :param page_info: 页面信息
        :return: 分析结果
        """
        try:
            html = page_info["html"]
            url = page_info["url"]

            # 提取链接
            links = self._extract_links(html, url, True)

            # 分析链接
            base_domain = self._extract_domain(url)
            internal_links = set()
            external_links = set()
            social_links = set()
            file_links = set()

            # 社交媒体域名
            social_domains = [
                'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
                'youtube.com', 'pinterest.com', 'reddit.com', 'tumblr.com',
                'weibo.com', 'wechat.com', 'tiktok.com', 'snapchat.com'
            ]

            # 文件扩展名
            file_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.tar', '.gz', '.mp3', '.mp4', '.avi', '.mov'
            ]

            for link in links:
                link_domain = self._extract_domain(link)

                # 检查是否为内部链接
                if link_domain == base_domain or not link_domain:
                    internal_links.add(link)

                    # 检查是否为文件链接
                    if any(link.lower().endswith(ext) for ext in file_extensions):
                        file_links.add(link)
                else:
                    external_links.add(link)

                    # 检查是否为社交媒体链接
                    if any(social in link_domain for social in social_domains):
                        social_links.add(link)

            # 返回结果
            return {
                "total_links": len(links),
                "unique_links": len(internal_links) + len(external_links),
                "internal_links": {
                    "count": len(internal_links),
                    "percentage": len(internal_links) / len(links) * 100 if links else 0,
                    "sample": list(internal_links)[:10]  # 只返回前10个
                },
                "external_links": {
                    "count": len(external_links),
                    "percentage": len(external_links) / len(links) * 100 if links else 0,
                    "sample": list(external_links)[:10]  # 只返回前10个
                },
                "social_links": {
                    "count": len(social_links),
                    "links": list(social_links)
                },
                "file_links": {
                    "count": len(file_links),
                    "links": list(file_links)
                }
            }

        except Exception as e:
            logger.error(f"链接分析时出错: {str(e)}")
            return {"error": str(e)}

    def _analyze_content(self, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        内容分析
        :param page_info: 页面信息
        :return: 分析结果
        """
        try:
            html = page_info["html"]
            soup = BeautifulSoup(html, 'html.parser')

            # 提取文本内容
            text = soup.get_text(separator=' ', strip=True)

            # 分词
            words = re.findall(r'\b\w+\b', text.lower())

            # 词频统计
            from collections import Counter
            word_freq = Counter(words)

            # 计算可读性
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            word_count = len(words)

            # 计算平均句子长度
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

            # 计算平均单词长度
            avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

            # 返回结果
            return {
                "text_length": len(text),
                "word_count": word_count,
                "sentence_count": sentence_count,
                "paragraph_count": len(soup.find_all('p')),
                "readability": {
                    "avg_sentence_length": avg_sentence_length,
                    "avg_word_length": avg_word_length
                },
                "top_words": [
                    {"word": word, "count": count}
                    for word, count in word_freq.most_common(20)
                    if len(word) > 3  # 忽略短词
                ],
                "content_sections": self._extract_content_sections(soup)
            }

        except Exception as e:
            logger.error(f"内容分析时出错: {str(e)}")
            return {"error": str(e)}

    def _extract_content_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        提取内容章节
        :param soup: BeautifulSoup对象
        :return: 章节列表
        """
        sections = []

        # 查找所有标题
        headings = soup.find_all(['h1', 'h2', 'h3'])

        for heading in headings[:10]:  # 只处理前10个标题
            heading_text = heading.get_text(strip=True)
            heading_tag = heading.name

            # 查找该标题后的内容
            content = []
            for sibling in heading.next_siblings:
                if sibling.name in ['h1', 'h2', 'h3']:
                    break
                if sibling.name == 'p':
                    content.append(sibling.get_text(strip=True))

            sections.append({
                "heading": heading_text,
                "level": heading_tag,
                "content_preview": " ".join(content)[:200] + "..." if content else ""
            })

        return sections

    def _format_size(self, size_bytes: int) -> str:
        """
        格式化大小
        :param size_bytes: 字节大小
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

    async def _screenshot_url(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        截取网页截图
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 截图结果
        """
        # 由于截图功能需要浏览器支持，这里我们只返回一个模拟结果
        # 在实际应用中，可以使用Playwright或Selenium来实现截图功能

        parameters = task.parameters or {}
        width = parameters.get("width", 1280)
        height = parameters.get("height", 800)
        full_page = parameters.get("full_page", False)

        # 更新进度
        self.update_progress(task.id, 50, db)

        # 模拟处理时间
        await asyncio.sleep(1)

        # 更新进度
        self.update_progress(task.id, 100, db)

        # 返回处理结果
        return {
            "success": True,
            "url": data_source.url,
            "width": width,
            "height": height,
            "full_page": full_page,
            "message": "截图功能需要浏览器支持，请使用Playwright或Selenium实现"
        }

    async def _generate_sitemap(self, task: ProcessingTask, data_source: URLSource, db: Session) -> Dict[str, Any]:
        """
        生成站点地图
        :param task: 处理任务
        :param data_source: URL数据源
        :param db: 数据库会话
        :return: 站点地图结果
        """
        parameters = task.parameters or {}
        max_depth = parameters.get("max_depth", 2)
        max_pages = parameters.get("max_pages", 100)

        # 更新进度
        self.update_progress(task.id, 5, db)

        try:
            # 初始化爬取状态
            start_url = data_source.url
            visited_urls = set()
            pending_urls = {start_url}
            current_depth = 0
            sitemap = []

            # 创建一个异步HTTP会话
            async with aiohttp.ClientSession() as session:
                # 按深度爬取
                while current_depth <= max_depth and pending_urls and len(visited_urls) < max_pages:
                    # 检查是否请求取消
                    if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                        return {"status": "cancelled"}

                    # 获取当前层级的URL
                    current_urls = pending_urls
                    pending_urls = set()

                    # 爬取当前层级的所有URL
                    for url in current_urls:
                        # 检查是否已访问
                        if url in visited_urls:
                            continue

                        # 标记为已访问
                        visited_urls.add(url)

                        # 检查是否请求取消
                        if task.id in self.running_tasks and self.running_tasks[task.id]["cancel_requested"]:
                            return {"status": "cancelled"}

                        try:
                            # 爬取页面
                            page_info = await self._fetch_page(session, url)

                            # 添加到站点地图
                            sitemap_entry = {
                                "url": url,
                                "title": page_info["title"],
                                "status": page_info["status"],
                                "depth": current_depth,
                                "links": []
                            }

                            # 提取链接
                            if current_depth < max_depth:
                                links = self._extract_links(page_info["html"], url, False)

                                # 添加到待爬取队列
                                for link in links:
                                    if link not in visited_urls:
                                        pending_urls.add(link)

                                    # 添加到当前页面的链接列表
                                    sitemap_entry["links"].append(link)

                            sitemap.append(sitemap_entry)

                        except Exception as e:
                            # 记录错误
                            logger.error(f"爬取URL时出错: {url} - {str(e)}")

                        # 更新进度
                        progress = 5 + int(len(visited_urls) / max(max_pages, len(visited_urls) + len(pending_urls)) * 90)
                        self.update_progress(task.id, min(95, progress), db)

                    # 增加深度
                    current_depth += 1

            # 更新进度
            self.update_progress(task.id, 100, db)

            # 返回处理结果
            return {
                "success": True,
                "url": data_source.url,
                "max_depth": max_depth,
                "pages_crawled": len(sitemap),
                "sitemap": sitemap
            }

        except Exception as e:
            error_msg = f"生成站点地图时出错: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _calculate_content_hash(self, html: str, monitor_type: str, selector: str = None) -> str:
        """
        计算内容哈希值
        :param html: HTML内容
        :param monitor_type: 监控类型（content, hash, selector）
        :param selector: CSS选择器
        :return: 哈希值
        """
        try:
            content = ""

            if monitor_type == "content":
                # 使用完整HTML内容
                content = html
            elif monitor_type == "text":
                # 只使用文本内容
                soup = BeautifulSoup(html, 'html.parser')
                content = soup.get_text()
            elif monitor_type == "selector" and selector:
                # 使用选择器提取的内容
                items = self._extract_by_css(html, selector)
                content = "\n".join(items)
            else:
                # 默认使用完整HTML内容
                content = html

            # 计算MD5哈希值
            return hashlib.md5(content.encode('utf-8')).hexdigest()

        except Exception as e:
            logger.error(f"计算内容哈希值时出错: {str(e)}")
            return ""

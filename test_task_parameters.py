#!/usr/bin/env python
"""
测试任务参数验证
"""
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.processing.file_processor import FileProcessor
from core.processing.database_processor import DatabaseProcessor
from core.processing.url_processor import URLProcessor

def test_file_processor_parameters():
    """测试文件处理器参数验证"""
    processor = FileProcessor()
    
    # 测试file_extract任务类型
    print("测试file_extract任务类型参数验证:")
    
    # 测试1: 正确的参数
    params1 = {"task_type": "file_extract", "extract_type": "text"}
    result1 = processor.validate_parameters(params1)
    print(f"测试1 (正确参数): {result1}")
    
    # 测试2: 缺少extract_type
    params2 = {"task_type": "file_extract"}
    result2 = processor.validate_parameters(params2)
    print(f"测试2 (缺少extract_type): {result2}")
    
    # 测试3: 参数为空字典
    params3 = {}
    result3 = processor.validate_parameters(params3)
    print(f"测试3 (空参数): {result3}")
    
    # 测试4: 参数为None
    try:
        result4 = processor.validate_parameters(None)
        print(f"测试4 (None参数): {result4}")
    except Exception as e:
        print(f"测试4 (None参数): 异常 - {str(e)}")
    
    # 测试5: 参数为JSON字符串
    params5 = json.dumps({"task_type": "file_extract", "extract_type": "text"})
    try:
        result5 = processor.validate_parameters(params5)
        print(f"测试5 (JSON字符串): {result5}")
    except Exception as e:
        print(f"测试5 (JSON字符串): 异常 - {str(e)}")

def main():
    """主函数"""
    print("开始测试任务参数验证...")
    test_file_processor_parameters()
    print("测试完成")

if __name__ == "__main__":
    main()

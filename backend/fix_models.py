import re
import os

def fix_column_definitions(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 正则表达式匹配Column定义，但不匹配已经修复的定义
    pattern = r'(\s+)(\w+)\s*=\s*Column\((?!"\w+")([\w\(\)]+)(?:,\s*(.+))?\)'
    
    # 替换为正确的格式
    fixed_content = re.sub(pattern, r'\1\2 = Column("\2", \3\4)', content)
    
    # 修复可能出现的双逗号问题
    fixed_content = fixed_content.replace(', )', ')')
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"已修复 {file_path}")

if __name__ == "__main__":
    fix_column_definitions("models/models.py")
    print("完成修复")

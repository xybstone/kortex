"""
安全相关的工具函数
"""
from cryptography.fernet import Fernet
from core.config import settings, get_cipher

# 加密函数
def encrypt_text(text: str) -> str:
    """加密文本"""
    print(f"加密文本: {text[:3]}***")
    if not text:
        print("文本为空，返回空字符串")
        return ""
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(text.encode()).decode()
        print(f"加密成功，结果: {encrypted[:10]}...")
        return encrypted
    except Exception as e:
        print(f"加密失败: {e}")
        # 返回原始文本，避免因加密失败而导致数据丢失
        return text

# 解密函数
def decrypt_text(encrypted_text: str) -> str:
    """解密文本"""
    if not encrypted_text:
        return ""
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception as e:
        print(f"解密失败: {e}")
        return ""

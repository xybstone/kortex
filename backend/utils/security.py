"""
安全相关的工具函数
"""
from cryptography.fernet import Fernet
from core.config import settings, get_cipher

# 加密函数
def encrypt_text(text: str) -> str:
    """加密文本"""
    if not text:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(text.encode()).decode()

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

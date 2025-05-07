# 导入所有模型，以便Alembic可以检测到它们
from database.session import Base

# 导入所有模型
from models.domain.user import User
from models.domain.note import Note, note_dataset
from models.domain.dataset import Dataset, DataSource, DatabaseSource, FileSource, URLSource
from models.domain.llm import (
    LLMProvider, LLMModel, LLMRole,
    Conversation, Message
)

# 所有模型的列表，用于创建表
__all__ = [
    "User", "Note",
    "Dataset", "DataSource", "DatabaseSource", "FileSource", "URLSource",
    "LLMProvider", "LLMModel", "LLMRole", "Conversation", "Message"
]

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models.domain.base import BaseModel, TimestampMixin

class User(BaseModel, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # 关系
    domain_notes = relationship("Note", back_populates="user")
    databases = relationship("Database", back_populates="user")
    llm_providers = relationship("LLMProvider", back_populates="user")
    llm_models = relationship("LLMModel", back_populates="user")
    llm_roles = relationship("LLMRole", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

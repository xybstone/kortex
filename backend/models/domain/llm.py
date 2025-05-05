from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, Float
from sqlalchemy.orm import relationship

from models.domain.base import BaseModel, TimestampMixin

class LLMProvider(BaseModel, TimestampMixin):
    """LLM供应商模型"""
    __tablename__ = "llm_providers"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    base_url = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    user = relationship("User", back_populates="llm_providers")
    models = relationship("LLMModel", back_populates="provider", cascade="all, delete-orphan")

class LLMModel(BaseModel, TimestampMixin):
    """LLM模型"""
    __tablename__ = "llm_models"

    name = Column(String, index=True)
    provider_id = Column(ForeignKey("llm_providers.id"))
    api_key = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    max_tokens = Column(Integer, default=4096)
    temperature = Column(Float, default=0.7)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    provider = relationship("LLMProvider", back_populates="models")
    user = relationship("User", back_populates="llm_models")
    roles = relationship("LLMRole", back_populates="model", cascade="all, delete-orphan")

class LLMRole(BaseModel, TimestampMixin):
    """LLM角色"""
    __tablename__ = "llm_roles"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text)
    model_id = Column(ForeignKey("llm_models.id"))
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    user_id = Column(ForeignKey("users.id"), nullable=True)

    # 关系
    model = relationship("LLMModel", back_populates="roles")
    user = relationship("User", back_populates="llm_roles")
    conversations = relationship("Conversation", back_populates="role")

class Conversation(BaseModel, TimestampMixin):
    """对话模型"""
    __tablename__ = "conversations"

    note_id = Column(ForeignKey("domain_notes.id"))
    role_id = Column(ForeignKey("llm_roles.id"))
    user_id = Column(ForeignKey("users.id"))

    # 关系
    note = relationship("Note", back_populates="conversations")
    role = relationship("LLMRole", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(BaseModel, TimestampMixin):
    """消息模型"""
    __tablename__ = "messages"

    content = Column(Text)
    role = Column(String)  # user, assistant, system
    conversation_id = Column(ForeignKey("conversations.id"))

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

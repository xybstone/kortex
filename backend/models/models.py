from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # 管理员标志
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    notes = relationship("Note", back_populates="user")
    databases = relationship("Database", back_populates="user")
    llm_providers = relationship("LLMProvider", back_populates="user")
    llm_models = relationship("LLMModel", back_populates="user")
    llm_roles = relationship("LLMRole", back_populates="user")

class Note(Base):
    """笔记模型"""
    __tablename__ = "notes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="notes")
    databases = relationship("Database", secondary="note_databases", back_populates="notes")
    conversations = relationship("NoteConversation", back_populates="note", cascade="all, delete-orphan")

class Database(Base):
    """数据库模型"""
    __tablename__ = "databases"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="databases")
    tables = relationship("Table", back_populates="database", cascade="all, delete-orphan")
    notes = relationship("Note", secondary="note_databases", back_populates="databases")

class NoteDatabase(Base):
    """笔记与数据库关联模型"""
    __tablename__ = "note_databases"
    __table_args__ = {'extend_existing': True}

    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    database_id = Column(Integer, ForeignKey("databases.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Table(Base):
    """表格模型"""
    __tablename__ = "tables"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    database_id = Column(Integer, ForeignKey("databases.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    database = relationship("Database", back_populates="tables")
    columns = relationship("TableColumn", back_populates="table", cascade="all, delete-orphan")
    rows = relationship("Row", back_populates="table", cascade="all, delete-orphan")

class TableColumn(Base):
    """列模型"""
    __tablename__ = "columns"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # 数据类型：text, integer, float, boolean, datetime等
    table_id = Column(Integer, ForeignKey("tables.id"))

    # 关系
    table = relationship("Table", back_populates="columns")
    cells = relationship("Cell", back_populates="column", cascade="all, delete-orphan")

class Row(Base):
    """行模型"""
    __tablename__ = "rows"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))

    # 关系
    table = relationship("Table", back_populates="rows")
    cells = relationship("Cell", back_populates="row", cascade="all, delete-orphan")

class Cell(Base):
    """单元格模型"""
    __tablename__ = "cells"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, ForeignKey("rows.id"))
    column_id = Column(Integer, ForeignKey("columns.id"))
    value = Column(Text, nullable=True)

    # 关系
    row = relationship("Row", back_populates="cells")
    column = relationship("TableColumn", back_populates="cells")


class LLMProvider(Base):
    """大模型供应商模型"""
    __tablename__ = "llm_providers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 供应商名称，如OpenAI, Anthropic, Gemini等
    description = Column(Text, nullable=True)
    base_url = Column(String, nullable=True)  # API基础URL
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    is_public = Column(Boolean, default=True)  # 是否公开
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="llm_providers")
    models = relationship("LLMModel", back_populates="provider", cascade="all, delete-orphan")


class LLMModel(Base):
    """大模型模型"""
    __tablename__ = "llm_models"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 模型名称，如gpt-4, claude-3等
    provider_id = Column(Integer, ForeignKey("llm_providers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    api_key = Column(String, nullable=True)  # 加密存储的API密钥
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # 是否公开
    max_tokens = Column(Integer, default=4096)
    temperature = Column(Float, default=0.7)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="llm_models")
    provider = relationship("LLMProvider", back_populates="models")
    roles = relationship("LLMRole", back_populates="model", cascade="all, delete-orphan")


class LLMRole(Base):
    """大模型角色模型"""
    __tablename__ = "llm_roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 角色名称
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)  # 系统提示词
    model_id = Column(Integer, ForeignKey("llm_models.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # 是否公开
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="llm_roles")
    model = relationship("LLMModel", back_populates="roles")


class NoteConversation(Base):
    """笔记与大模型对话模型"""
    __tablename__ = "note_conversations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    role_id = Column(Integer, ForeignKey("llm_roles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User")
    note = relationship("Note")
    role = relationship("LLMRole")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    """对话消息模型"""
    __tablename__ = "conversation_messages"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("note_conversations.id"))
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    conversation = relationship("NoteConversation", back_populates="messages")

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.session import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    notes = relationship("Note", back_populates="user")
    databases = relationship("Database", back_populates="user")

class Note(Base):
    """笔记模型"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="notes")
    databases = relationship("Database", secondary="note_databases", back_populates="notes")

class Database(Base):
    """数据库模型"""
    __tablename__ = "databases"
    
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
    
    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    database_id = Column(Integer, ForeignKey("databases.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Table(Base):
    """表格模型"""
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    database_id = Column(Integer, ForeignKey("databases.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    database = relationship("Database", back_populates="tables")
    columns = relationship("Column", back_populates="table", cascade="all, delete-orphan")
    rows = relationship("Row", back_populates="table", cascade="all, delete-orphan")

class Column(Base):
    """列模型"""
    __tablename__ = "columns"
    
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
    
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    
    # 关系
    table = relationship("Table", back_populates="rows")
    cells = relationship("Cell", back_populates="row", cascade="all, delete-orphan")

class Cell(Base):
    """单元格模型"""
    __tablename__ = "cells"
    
    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, ForeignKey("rows.id"))
    column_id = Column(Integer, ForeignKey("columns.id"))
    value = Column(Text, nullable=True)
    
    # 关系
    row = relationship("Row", back_populates="cells")
    column = relationship("Column", back_populates="cells")

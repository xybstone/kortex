from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.domain.base import BaseModel, TimestampMixin
from models.domain.note import note_database

class Database(BaseModel, TimestampMixin):
    """数据库模型"""
    __tablename__ = "databases"
    __table_args__ = {'extend_existing': True}

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(ForeignKey("users.id"))

    # 关系
    user = relationship("User", back_populates="databases")
    notes = relationship("Note", secondary=note_database, back_populates="databases")
    tables = relationship("Table", back_populates="database", cascade="all, delete-orphan")

class Table(BaseModel, TimestampMixin):
    """表格模型"""
    __tablename__ = "tables"

    name = Column(String, index=True)
    database_id = Column(ForeignKey("databases.id"))

    # 关系
    database = relationship("Database", back_populates="tables")
    columns = relationship("Column", back_populates="table", cascade="all, delete-orphan")

class Column(BaseModel):
    """列模型"""
    __tablename__ = "columns"

    name = Column(String, index=True)
    type = Column(String)
    table_id = Column(ForeignKey("tables.id"))

    # 关系
    table = relationship("Table", back_populates="columns")

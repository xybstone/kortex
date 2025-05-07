from sqlalchemy import Column, String, Text, ForeignKey, Table, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.domain.base import BaseModel, TimestampMixin
from models.domain.note import note_dataset

class Dataset(BaseModel, TimestampMixin):
    """数据集模型"""
    __tablename__ = "datasets"
    __table_args__ = {'extend_existing': True}

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(ForeignKey("users.id"))

    # 关系
    user = relationship("User", back_populates="datasets")
    notes = relationship("Note", secondary=note_dataset, back_populates="datasets")
    data_sources = relationship("DataSource", back_populates="dataset", cascade="all, delete-orphan")

class DataSource(BaseModel, TimestampMixin):
    """数据源基类模型"""
    __tablename__ = "data_sources"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, index=True)  # 数据源类型：database, file, url等
    dataset_id = Column(ForeignKey("datasets.id"))

    # 数据处理相关字段
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    last_processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_error = Column(Text, nullable=True)

    # 关系
    dataset = relationship("Dataset", back_populates="data_sources")

    # 多态关系设置
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "data_source"
    }

class DatabaseSource(DataSource):
    """数据库类型数据源"""
    __tablename__ = "database_sources"

    id = Column(ForeignKey("data_sources.id"), primary_key=True)
    connection_string = Column(String, nullable=True)  # 可以加密存储
    database_type = Column(String)  # mysql, postgresql, etc.

    __mapper_args__ = {
        "polymorphic_identity": "database"
    }

class FileSource(DataSource):
    """文件类型数据源"""
    __tablename__ = "file_sources"

    id = Column(ForeignKey("data_sources.id"), primary_key=True)
    file_path = Column(String)
    file_type = Column(String)  # pdf, md, csv, etc.
    file_size = Column(Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "file"
    }

class URLSource(DataSource):
    """URL类型数据源"""
    __tablename__ = "url_sources"

    id = Column(ForeignKey("data_sources.id"), primary_key=True)
    url = Column(String)
    crawl_depth = Column(Integer, default=1)

    __mapper_args__ = {
        "polymorphic_identity": "url"
    }

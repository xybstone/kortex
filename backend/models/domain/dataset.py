from sqlalchemy import Column, String, Text, ForeignKey, Table, Integer, DateTime, JSON, Boolean
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
    processing_tasks = relationship("ProcessingTask", back_populates="data_source", cascade="all, delete-orphan")

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


class TaskDependency(BaseModel, TimestampMixin):
    """任务依赖关系模型"""
    __tablename__ = "task_dependencies"

    # 依赖类型
    dependency_type = Column(String, default="success")  # success, failure, completion

    # 关联的任务
    parent_task_id = Column(ForeignKey("processing_tasks.id", ondelete="CASCADE"), index=True)
    child_task_id = Column(ForeignKey("processing_tasks.id", ondelete="CASCADE"), index=True)

    # 关系
    parent_task = relationship("ProcessingTask", foreign_keys=[parent_task_id], back_populates="child_tasks")
    child_task = relationship("ProcessingTask", foreign_keys=[child_task_id], back_populates="parent_tasks")


class TaskExecutionHistory(BaseModel, TimestampMixin):
    """任务执行历史记录模型"""
    __tablename__ = "task_execution_history"

    # 任务信息
    task_id = Column(ForeignKey("processing_tasks.id", ondelete="CASCADE"), index=True)
    task_name = Column(String)
    task_type = Column(String)

    # 执行信息
    status = Column(String)  # success, failure, cancelled
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)  # 执行时长（秒）

    # 结果信息
    result_summary = Column(JSON, nullable=True)  # 结果摘要，JSON格式
    error_message = Column(Text, nullable=True)  # 错误信息

    # 关联的任务
    task = relationship("ProcessingTask", back_populates="execution_history")

    # 关联的用户
    user_id = Column(ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="task_execution_history")


class ProcessingTask(BaseModel, TimestampMixin):
    """数据处理任务模型"""
    __tablename__ = "processing_tasks"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    task_type = Column(String, index=True)  # database_clean, file_embed, url_crawl, etc.
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    priority = Column(Integer, default=0)  # 优先级，数字越大优先级越高

    # 任务参数和结果
    parameters = Column(JSON, nullable=True)  # 任务参数，JSON格式
    result = Column(JSON, nullable=True)  # 任务结果，JSON格式
    error_message = Column(Text, nullable=True)  # 错误信息

    # 执行信息
    started_at = Column(DateTime(timezone=True), nullable=True)  # 开始执行时间
    completed_at = Column(DateTime(timezone=True), nullable=True)  # 完成时间
    progress = Column(Integer, default=0)  # 进度，0-100

    # 调度信息
    is_recurring = Column(Boolean, default=False)  # 是否为周期性任务
    schedule_type = Column(String, nullable=True)  # 调度类型：once, daily, weekly, monthly, cron
    schedule_value = Column(String, nullable=True)  # 调度值，如cron表达式或特定时间
    next_run_time = Column(DateTime(timezone=True), nullable=True)  # 下次运行时间
    last_run_time = Column(DateTime(timezone=True), nullable=True)  # 上次运行时间
    run_count = Column(Integer, default=0)  # 运行次数
    max_runs = Column(Integer, nullable=True)  # 最大运行次数，为空表示无限制

    # 依赖关系
    wait_for_dependencies = Column(Boolean, default=True)  # 是否等待依赖任务完成

    # 关联的数据源
    data_source_id = Column(ForeignKey("data_sources.id"))
    data_source = relationship("DataSource", back_populates="processing_tasks")

    # 关联的用户
    user_id = Column(ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="processing_tasks")

    # 关联的依赖任务
    parent_tasks = relationship("TaskDependency", foreign_keys=[TaskDependency.child_task_id], back_populates="child_task", cascade="all, delete-orphan")
    child_tasks = relationship("TaskDependency", foreign_keys=[TaskDependency.parent_task_id], back_populates="parent_task", cascade="all, delete-orphan")

    # 关联的执行历史
    execution_history = relationship("TaskExecutionHistory", back_populates="task", cascade="all, delete-orphan")

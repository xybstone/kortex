from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

# 数据集相关模式
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    user_id: Optional[int] = None

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DatasetBrief(DatasetBase):
    id: int

    class Config:
        from_attributes = True

# 数据源基础模式
class DataSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # database, file, url

class DataSourceCreate(DataSourceBase):
    dataset_id: int

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DataSourceResponse(DataSourceBase):
    id: int
    dataset_id: int
    processing_status: str
    last_processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 数据库源模式
class DatabaseSourceCreate(DataSourceCreate):
    connection_string: Optional[str] = None
    database_type: str

class DatabaseSourceUpdate(DataSourceUpdate):
    connection_string: Optional[str] = None
    database_type: Optional[str] = None

class DatabaseSourceResponse(DataSourceResponse):
    connection_string: Optional[str] = None
    database_type: str

    class Config:
        from_attributes = True

# 文件源模式
class FileSourceCreate(DataSourceCreate):
    file_path: str
    file_type: str
    file_size: Optional[int] = None

class FileSourceUpdate(DataSourceUpdate):
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class FileSourceResponse(DataSourceResponse):
    file_path: str
    file_type: str
    file_size: Optional[int] = None

    class Config:
        from_attributes = True

# URL源模式
class URLSourceCreate(DataSourceCreate):
    url: str
    crawl_depth: Optional[int] = 1

class URLSourceUpdate(DataSourceUpdate):
    url: Optional[str] = None
    crawl_depth: Optional[int] = None

class URLSourceResponse(DataSourceResponse):
    url: str
    crawl_depth: int

    class Config:
        from_attributes = True

# 数据集详细响应
class DatasetResponse(DatasetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    data_sources: List[Union[DatabaseSourceResponse, FileSourceResponse, URLSourceResponse]] = []

    class Config:
        from_attributes = True


# 任务依赖关系相关模式
class TaskDependencyBase(BaseModel):
    dependency_type: str = "success"  # success, failure, completion

class TaskDependencyCreate(TaskDependencyBase):
    parent_task_id: int
    child_task_id: int

class TaskDependencyResponse(TaskDependencyBase):
    id: int
    parent_task_id: int
    child_task_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 任务执行历史记录相关模式
class TaskExecutionHistoryBase(BaseModel):
    task_id: int
    task_name: str
    task_type: str
    status: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: int
    result_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class TaskExecutionHistoryCreate(TaskExecutionHistoryBase):
    user_id: Optional[int] = None

class TaskExecutionHistoryResponse(TaskExecutionHistoryBase):
    id: int
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# 处理任务相关模式
class ProcessingTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: str
    priority: Optional[int] = 0
    is_recurring: Optional[bool] = False
    wait_for_dependencies: Optional[bool] = True

class ScheduleInfo(BaseModel):
    """调度信息"""
    schedule_type: str  # once, daily, weekly, monthly, cron
    schedule_value: str  # 调度值，如cron表达式或特定时间
    max_runs: Optional[int] = None  # 最大运行次数，为空表示无限制

class DependencyInfo(BaseModel):
    """依赖信息"""
    parent_task_id: int
    dependency_type: str = "success"  # success, failure, completion

class ProcessingTaskCreate(ProcessingTaskBase):
    data_source_id: int
    parameters: Optional[Dict[str, Any]] = None
    schedule_info: Optional[ScheduleInfo] = None
    dependencies: Optional[List[DependencyInfo]] = None
    user_id: Optional[int] = None

class ProcessingTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_recurring: Optional[bool] = None
    wait_for_dependencies: Optional[bool] = None
    schedule_info: Optional[ScheduleInfo] = None

class ProcessingTaskResponse(ProcessingTaskBase):
    id: int
    data_source_id: int
    status: str
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int

    # 调度信息
    schedule_type: Optional[str] = None
    schedule_value: Optional[str] = None
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    run_count: Optional[int] = 0
    max_runs: Optional[int] = None

    # 依赖信息
    parent_tasks: Optional[List[TaskDependencyResponse]] = None
    child_tasks: Optional[List[TaskDependencyResponse]] = None

    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

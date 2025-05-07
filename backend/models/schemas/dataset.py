from pydantic import BaseModel
from typing import List, Optional, Union
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

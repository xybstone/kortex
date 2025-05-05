from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 数据库相关模式
class DatabaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatabaseCreate(DatabaseBase):
    user_id: Optional[int] = None

class DatabaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DatabaseBrief(DatabaseBase):
    id: int

    class Config:
        from_attributes = True

# 列相关模式
class ColumnBase(BaseModel):
    name: str
    type: str

class ColumnResponse(ColumnBase):
    id: int

    class Config:
        from_attributes = True

# 表格相关模式
class TableBase(BaseModel):
    name: str

class TableBrief(TableBase):
    id: int

    class Config:
        from_attributes = True

class TableResponse(TableBase):
    id: int
    database_id: int
    columns: List[ColumnResponse]

    class Config:
        from_attributes = True

class DatabaseResponse(DatabaseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tables: Optional[List[TableBrief]] = None

    class Config:
        from_attributes = True

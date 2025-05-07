from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 临时定义数据库简要信息类，以便兼容现有代码
class DatabaseBrief(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

from models.schemas.dataset import DatasetBrief

# 笔记相关模式
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    user_id: Optional[int] = None
    database_ids: Optional[List[int]] = None
    dataset_ids: Optional[List[int]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    database_ids: Optional[List[int]] = None
    dataset_ids: Optional[List[int]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    databases: Optional[List[DatabaseBrief]] = None
    datasets: Optional[List[DatasetBrief]] = None

    class Config:
        from_attributes = True

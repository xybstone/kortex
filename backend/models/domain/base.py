from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from database.session import Base

class TimestampMixin:
    """时间戳混入类，提供创建时间和更新时间"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)

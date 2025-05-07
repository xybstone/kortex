from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

from models.domain.base import BaseModel, TimestampMixin

# 笔记与数据集的多对多关系表
note_dataset = Table(
    "note_dataset",
    BaseModel.metadata,
    Column("note_id", ForeignKey("domain_notes.id"), primary_key=True),
    Column("dataset_id", ForeignKey("datasets.id"), primary_key=True)
)

class Note(BaseModel, TimestampMixin):
    """笔记模型 - 领域模型版本"""
    __tablename__ = "domain_notes"  # 修改表名，避免与simple_models中的表冲突
    __table_args__ = {'extend_existing': True}

    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(ForeignKey("users.id"))

    # 关系
    user = relationship("User", back_populates="domain_notes")
    datasets = relationship("Dataset", secondary=note_dataset, back_populates="notes")
    conversations = relationship("Conversation", back_populates="note")

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.db.session import Base


class BaseModel(Base):
    """所有模型的基类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    create_time = Column(DateTime, default=datetime.now, nullable=False)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 自动生成表名
    @declared_attr
    def __tablename__(cls):
        return f"wh_{cls.__name__.lower()}"

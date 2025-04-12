from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    """通知类型枚举"""
    SYSTEM = "SYSTEM"  # 系统通知
    WORKFLOW = "WORKFLOW"  # 工作流通知
    BUSINESS = "BUSINESS"  # 业务通知


class NotificationLevel(str, enum.Enum):
    """通知级别枚举"""
    INFO = "INFO"  # 信息
    WARNING = "WARNING"  # 警告
    ERROR = "ERROR"  # 错误


class Notification(BaseModel):
    """通知模型"""
    
    title = Column(String(100), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    notification_type = Column(Enum(NotificationType), nullable=False, comment="通知类型")
    level = Column(Enum(NotificationLevel), default=NotificationLevel.INFO, comment="通知级别")
    
    # 关联业务
    business_key = Column(String(64), comment="业务键")
    business_type = Column(String(20), comment="业务类型")
    
    # 发送信息
    sender_id = Column(Integer, ForeignKey("wh_user.id"), comment="发送人ID")
    send_time = Column(DateTime, default=datetime.now, nullable=False, comment="发送时间")
    
    # 关联项
    sender = relationship("User")
    recipients = relationship("NotificationRecipient", back_populates="notification", cascade="all, delete-orphan")


class NotificationRecipient(BaseModel):
    """通知接收人模型"""
    
    notification_id = Column(Integer, ForeignKey("wh_notification.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("wh_user.id"), nullable=False)
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_time = Column(DateTime, comment="阅读时间")
    
    # 关联项
    notification = relationship("Notification", back_populates="recipients")
    recipient = relationship("User")

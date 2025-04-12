from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.notification import NotificationType, NotificationLevel


# 通知基础模型
class NotificationBase(BaseModel):
    title: str
    content: str
    notification_type: NotificationType
    level: Optional[NotificationLevel] = NotificationLevel.INFO
    business_key: Optional[str] = None
    business_type: Optional[str] = None


# 创建通知时需要的属性
class NotificationCreate(NotificationBase):
    sender_id: Optional[int] = None
    recipient_ids: List[int]


# 更新通知时可以更新的属性
class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    level: Optional[NotificationLevel] = None


# 数据库中存储的通知属性
class NotificationInDBBase(NotificationBase):
    id: int
    sender_id: Optional[int] = None
    send_time: datetime
    
    class Config:
        from_attributes = True


# 返回给API的通知信息
class Notification(NotificationInDBBase):
    pass


# 通知接收人基础模型
class NotificationRecipientBase(BaseModel):
    notification_id: int
    recipient_id: int
    is_read: Optional[bool] = False


# 创建通知接收人时需要的属性
class NotificationRecipientCreate(NotificationRecipientBase):
    pass


# 更新通知接收人时可以更新的属性
class NotificationRecipientUpdate(BaseModel):
    is_read: Optional[bool] = None
    read_time: Optional[datetime] = None


# 数据库中存储的通知接收人属性
class NotificationRecipientInDBBase(NotificationRecipientBase):
    id: int
    read_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 返回给API的通知接收人信息
class NotificationRecipient(NotificationRecipientInDBBase):
    pass


# 用户通知列表响应
class UserNotificationsResponse(BaseModel):
    total: int
    unread: int
    notifications: List[Notification]

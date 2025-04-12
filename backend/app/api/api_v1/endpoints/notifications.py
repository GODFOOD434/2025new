from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationRecipient, NotificationType, NotificationLevel
from app.schemas.notification import (
    Notification as NotificationSchema,
    NotificationCreate,
    NotificationUpdate,
    UserNotificationsResponse
)

router = APIRouter()


@router.get("/", response_model=UserNotificationsResponse)
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取用户通知
    """
    # 构建基本查询
    query = db.query(Notification).join(
        NotificationRecipient,
        Notification.id == NotificationRecipient.notification_id
    ).filter(
        NotificationRecipient.recipient_id == current_user.id
    )
    
    # 应用过滤条件
    if is_read is not None:
        query = query.filter(NotificationRecipient.is_read == is_read)
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    # 计算总数和未读数
    total = query.count()
    unread = db.query(Notification).join(
        NotificationRecipient,
        Notification.id == NotificationRecipient.notification_id
    ).filter(
        NotificationRecipient.recipient_id == current_user.id,
        NotificationRecipient.is_read == False
    ).count()
    
    # 分页
    query = query.order_by(Notification.send_time.desc())
    query = query.offset((page - 1) * size).limit(size)
    
    # 获取结果
    notifications = query.all()
    
    return {
        "total": total,
        "unread": unread,
        "notifications": notifications
    }


@router.post("/", response_model=NotificationSchema)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建通知
    """
    # 创建通知
    notification = Notification(
        title=notification_in.title,
        content=notification_in.content,
        notification_type=notification_in.notification_type,
        level=notification_in.level,
        business_key=notification_in.business_key,
        business_type=notification_in.business_type,
        sender_id=notification_in.sender_id or current_user.id,
        send_time=datetime.now()
    )
    db.add(notification)
    db.flush()
    
    # 创建通知接收人
    for recipient_id in notification_in.recipient_ids:
        recipient = NotificationRecipient(
            notification_id=notification.id,
            recipient_id=recipient_id,
            is_read=False
        )
        db.add(recipient)
    
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/{id}/read", response_model=dict)
def mark_notification_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    标记通知为已读
    """
    # 查找通知接收人记录
    recipient = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == id,
        NotificationRecipient.recipient_id == current_user.id
    ).first()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"通知 {id} 不存在或不属于当前用户"
        )
    
    # 标记为已读
    recipient.is_read = True
    recipient.read_time = datetime.now()
    
    db.add(recipient)
    db.commit()
    
    return {
        "success": True,
        "message": "通知已标记为已读"
    }


@router.put("/read-all", response_model=dict)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    标记所有通知为已读
    """
    # 查找所有未读通知
    unread_recipients = db.query(NotificationRecipient).filter(
        NotificationRecipient.recipient_id == current_user.id,
        NotificationRecipient.is_read == False
    ).all()
    
    # 标记为已读
    for recipient in unread_recipients:
        recipient.is_read = True
        recipient.read_time = datetime.now()
        db.add(recipient)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"已将 {len(unread_recipients)} 条通知标记为已读"
    }


@router.delete("/{id}", response_model=dict)
def delete_notification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除通知
    """
    # 查找通知接收人记录
    recipient = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == id,
        NotificationRecipient.recipient_id == current_user.id
    ).first()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"通知 {id} 不存在或不属于当前用户"
        )
    
    # 删除通知接收人记录
    db.delete(recipient)
    db.commit()
    
    return {
        "success": True,
        "message": "通知已删除"
    }

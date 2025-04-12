from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.purchase_order import PurchaseOrder
from app.models.workflow import (
    WorkflowInstance, WorkflowTask, StaffAssignment,
    WorkflowType, WorkflowStatus, TaskStatus
)
from app.models.notification import Notification, NotificationRecipient, NotificationType, NotificationLevel


def assign_tasks(
    db: Session,
    workflow: WorkflowInstance,
    order: PurchaseOrder
) -> List[WorkflowTask]:
    """
    根据大类和用户单位分配任务
    
    Args:
        db: 数据库会话
        workflow: 工作流实例
        order: 采购订单
    
    Returns:
        创建的任务列表
    """
    tasks = []
    
    # 分配保管员任务
    keeper_assignment = db.query(StaffAssignment).filter(
        StaffAssignment.role_type == "keeper",
        StaffAssignment.category == order.category,
        StaffAssignment.user_unit == order.user_unit
    ).first()
    
    if not keeper_assignment:
        # 如果没有精确匹配，尝试只按大类匹配
        keeper_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "keeper",
            StaffAssignment.category == order.category
        ).first()
    
    if not keeper_assignment:
        # 如果仍然没有匹配，尝试只按用户单位匹配
        keeper_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "keeper",
            StaffAssignment.user_unit == order.user_unit
        ).first()
    
    if keeper_assignment:
        keeper_task = WorkflowTask(
            task_id=f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}1",
            workflow_instance_id=workflow.id,
            task_name="保管员确认",
            status=TaskStatus.PENDING,
            assignee_id=keeper_assignment.staff_id
        )
        db.add(keeper_task)
        tasks.append(keeper_task)
        
        # 发送通知给保管员
        send_task_notification(
            db=db,
            recipient_id=keeper_assignment.staff_id,
            title="新的保管员确认任务",
            content=f"您有一个新的保管员确认任务，采购订单号: {order.order_no}",
            business_key=order.order_no,
            business_type="采购订单"
        )
    
    # 分配质检员任务
    inspector_assignment = db.query(StaffAssignment).filter(
        StaffAssignment.role_type == "inspector",
        StaffAssignment.category == order.category,
        StaffAssignment.user_unit == order.user_unit
    ).first()
    
    if not inspector_assignment:
        # 如果没有精确匹配，尝试只按大类匹配
        inspector_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "inspector",
            StaffAssignment.category == order.category
        ).first()
    
    if not inspector_assignment:
        # 如果仍然没有匹配，尝试只按用户单位匹配
        inspector_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "inspector",
            StaffAssignment.user_unit == order.user_unit
        ).first()
    
    if inspector_assignment:
        inspector_task = WorkflowTask(
            task_id=f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}2",
            workflow_instance_id=workflow.id,
            task_name="质检员确认",
            status=TaskStatus.PENDING,
            assignee_id=inspector_assignment.staff_id
        )
        db.add(inspector_task)
        tasks.append(inspector_task)
        
        # 发送通知给质检员
        send_task_notification(
            db=db,
            recipient_id=inspector_assignment.staff_id,
            title="新的质检员确认任务",
            content=f"您有一个新的质检员确认任务，采购订单号: {order.order_no}",
            business_key=order.order_no,
            business_type="采购订单"
        )
    
    return tasks


def send_task_notification(
    db: Session,
    recipient_id: int,
    title: str,
    content: str,
    business_key: str,
    business_type: str
) -> None:
    """
    发送任务通知
    
    Args:
        db: 数据库会话
        recipient_id: 接收人ID
        title: 通知标题
        content: 通知内容
        business_key: 业务键
        business_type: 业务类型
    """
    notification = Notification(
        title=title,
        content=content,
        notification_type=NotificationType.WORKFLOW,
        level=NotificationLevel.INFO,
        business_key=business_key,
        business_type=business_type,
        send_time=datetime.now()
    )
    db.add(notification)
    db.flush()
    
    recipient = NotificationRecipient(
        notification_id=notification.id,
        recipient_id=recipient_id,
        is_read=False
    )
    db.add(recipient)
    db.commit()

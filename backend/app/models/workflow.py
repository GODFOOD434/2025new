from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class WorkflowType(str, enum.Enum):
    """工作流类型枚举"""
    PURCHASE_CONFIRMATION = "PURCHASE_CONFIRMATION"  # 采购订单确认
    QUALITY_INSPECTION = "QUALITY_INSPECTION"  # 质检
    OUTBOUND = "OUTBOUND"  # 出库


class WorkflowStatus(str, enum.Enum):
    """工作流状态枚举"""
    CREATED = "CREATED"  # 已创建
    RUNNING = "RUNNING"  # 运行中
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "PENDING"  # 待处理
    PROCESSING = "PROCESSING"  # 处理中
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


class WorkflowInstance(BaseModel):
    """工作流实例模型"""
    
    process_instance_id = Column(String(64), unique=True, comment="流程实例ID")
    business_key = Column(String(64), index=True, comment="业务键(采购单号)")
    workflow_type = Column(Enum(WorkflowType), nullable=False, comment="工作流类型")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.CREATED, comment="状态")
    
    # 关联项
    initiator_id = Column(Integer, ForeignKey("wh_user.id"), comment="发起人ID")
    initiator = relationship("User")
    
    purchase_order_id = Column(Integer, ForeignKey("wh_purchaseorder.id"))
    purchase_order = relationship("PurchaseOrder", back_populates="workflow")
    
    tasks = relationship("WorkflowTask", back_populates="workflow_instance", cascade="all, delete-orphan")


class WorkflowTask(BaseModel):
    """工作流任务模型"""
    
    task_id = Column(String(64), unique=True, comment="任务ID")
    workflow_instance_id = Column(Integer, ForeignKey("wh_workflowinstance.id"), nullable=False)
    task_name = Column(String(100), nullable=False, comment="任务名称")
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment="状态")
    complete_time = Column(DateTime, comment="完成时间")
    
    # 关联项
    assignee_id = Column(Integer, ForeignKey("wh_user.id"), comment="处理人ID")
    assignee = relationship("User")
    
    workflow_instance = relationship("WorkflowInstance", back_populates="tasks")
    
    # 任务处理结果
    result = Column(String(20), comment="处理结果")
    comment = Column(Text, comment="处理意见")


class StaffAssignment(BaseModel):
    """员工分配规则模型"""
    
    staff_id = Column(Integer, ForeignKey("wh_user.id"), nullable=False, comment="员工ID")
    role_type = Column(String(20), nullable=False, comment="角色类型(保管员/质检员)")
    category = Column(String(50), index=True, comment="负责大类")
    user_unit = Column(String(100), index=True, comment="负责用户单位")
    
    # 关联项
    staff = relationship("User")

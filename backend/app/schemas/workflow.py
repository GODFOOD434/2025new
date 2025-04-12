from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel

from app.models.workflow import WorkflowType, WorkflowStatus, TaskStatus


# 工作流任务基础模型
class WorkflowTaskBase(BaseModel):
    task_name: str
    status: Optional[TaskStatus] = TaskStatus.PENDING


# 创建工作流任务时需要的属性
class WorkflowTaskCreate(WorkflowTaskBase):
    assignee_id: int


# 更新工作流任务时可以更新的属性
class WorkflowTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    result: Optional[str] = None
    comment: Optional[str] = None


# 完成任务请求
class TaskComplete(BaseModel):
    approved: bool
    comment: Optional[str] = None
    attachments: Optional[List[Any]] = None


# 数据库中存储的工作流任务属性
class WorkflowTaskInDBBase(WorkflowTaskBase):
    id: int
    task_id: str
    workflow_instance_id: int
    assignee_id: Optional[int] = None
    complete_time: Optional[datetime] = None
    result: Optional[str] = None
    comment: Optional[str] = None
    
    class Config:
        from_attributes = True


# 返回给API的工作流任务信息
class WorkflowTask(WorkflowTaskInDBBase):
    pass


# 工作流实例基础模型
class WorkflowInstanceBase(BaseModel):
    workflow_type: WorkflowType
    status: Optional[WorkflowStatus] = WorkflowStatus.CREATED


# 创建工作流实例时需要的属性
class WorkflowInstanceCreate(WorkflowInstanceBase):
    business_key: str
    initiator_id: int
    purchase_order_id: Optional[int] = None


# 启动工作流请求
class WorkflowStart(BaseModel):
    order_no: str
    workflow_type: WorkflowType
    delivery_type: Optional[str] = None


# 更新工作流实例时可以更新的属性
class WorkflowInstanceUpdate(BaseModel):
    status: Optional[WorkflowStatus] = None
    process_instance_id: Optional[str] = None


# 数据库中存储的工作流实例属性
class WorkflowInstanceInDBBase(WorkflowInstanceBase):
    id: int
    process_instance_id: Optional[str] = None
    business_key: str
    initiator_id: int
    purchase_order_id: Optional[int] = None
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


# 返回给API的工作流实例信息
class WorkflowInstance(WorkflowInstanceInDBBase):
    tasks: List[WorkflowTask] = []


# 员工分配规则基础模型
class StaffAssignmentBase(BaseModel):
    role_type: str
    category: Optional[str] = None
    user_unit: Optional[str] = None


# 创建员工分配规则时需要的属性
class StaffAssignmentCreate(StaffAssignmentBase):
    staff_id: int


# 更新员工分配规则时可以更新的属性
class StaffAssignmentUpdate(StaffAssignmentBase):
    pass


# 数据库中存储的员工分配规则属性
class StaffAssignmentInDBBase(StaffAssignmentBase):
    id: int
    staff_id: int
    
    class Config:
        from_attributes = True


# 返回给API的员工分配规则信息
class StaffAssignment(StaffAssignmentInDBBase):
    pass

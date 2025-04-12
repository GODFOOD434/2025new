from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.warehouse import ConfirmationStatus


# 确认单基础模型
class DeliveryConfirmationBase(BaseModel):
    confirmation_no: str
    order_id: int
    status: Optional[ConfirmationStatus] = ConfirmationStatus.GENERATED


# 创建确认单时需要的属性
class DeliveryConfirmationCreate(DeliveryConfirmationBase):
    keeper_id: Optional[int] = None
    inspector_id: Optional[int] = None


# 生成确认单请求
class ConfirmationGenerate(BaseModel):
    order_no: str


# 更新确认单时可以更新的属性
class DeliveryConfirmationUpdate(BaseModel):
    status: Optional[ConfirmationStatus] = None
    keeper_id: Optional[int] = None
    inspector_id: Optional[int] = None
    keeper_confirm_time: Optional[datetime] = None
    inspector_confirm_time: Optional[datetime] = None
    print_time: Optional[datetime] = None
    print_by: Optional[int] = None


# 数据库中存储的确认单属性
class DeliveryConfirmationInDBBase(DeliveryConfirmationBase):
    id: int
    keeper_id: Optional[int] = None
    inspector_id: Optional[int] = None
    keeper_confirm_time: Optional[datetime] = None
    inspector_confirm_time: Optional[datetime] = None
    print_time: Optional[datetime] = None
    print_by: Optional[int] = None
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


# 返回给API的确认单信息
class DeliveryConfirmation(DeliveryConfirmationInDBBase):
    pass


# 确认单打印响应
class ConfirmationPrintResponse(BaseModel):
    success: bool
    data: DeliveryConfirmation

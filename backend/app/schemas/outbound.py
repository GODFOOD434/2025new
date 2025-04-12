from typing import Optional, List, Any
from datetime import date
from pydantic import BaseModel

from app.models.outbound import OutboundStatus


# 批量删除请求模型
class BatchDeleteRequest(BaseModel):
    ids: List[int]


# 出库项基础模型
class OutboundItemBase(BaseModel):
    material_code: str
    material_description: str
    unit: str
    actual_quantity: float
    outbound_price: Optional[float] = None
    material_category_code: Optional[str] = None
    project_code: Optional[str] = None
    requested_quantity: Optional[float] = None
    outbound_amount: Optional[float] = None
    purchase_order_no: Optional[str] = None
    remark: Optional[str] = None


# 创建出库项时需要的属性
class OutboundItemCreate(OutboundItemBase):
    pass


# 更新出库项时可以更新的属性
class OutboundItemUpdate(OutboundItemBase):
    pass


# 数据库中存储的出库项属性
class OutboundItemInDBBase(OutboundItemBase):
    id: int
    outbound_id: int

    class Config:
        from_attributes = True


# 返回给API的出库项信息
class OutboundItem(OutboundItemInDBBase):
    pass


# 出库单基础模型
class OutboundOrderBase(BaseModel):
    material_voucher: str
    voucher_date: date
    department: str
    user_unit: str
    document_type: Optional[str] = None
    total_amount: Optional[float] = 0
    issue_date: Optional[date] = None
    sales_amount: Optional[float] = 0
    transfer_order: Optional[str] = None
    management_fee_rate: Optional[float] = None
    material_category: Optional[str] = None  # 添加料单分属字段
    status: Optional[OutboundStatus] = OutboundStatus.PENDING


# 创建出库单时需要的属性
class OutboundOrderCreate(OutboundOrderBase):
    operator_id: int
    items: List[OutboundItemCreate]


# 更新出库单时可以更新的属性
class OutboundOrderUpdate(BaseModel):
    document_type: Optional[str] = None
    total_amount: Optional[float] = None
    issue_date: Optional[date] = None
    sales_amount: Optional[float] = None
    transfer_order: Optional[str] = None
    management_fee_rate: Optional[float] = None
    status: Optional[OutboundStatus] = None
    operator_id: Optional[int] = None


# 数据库中存储的出库单属性
class OutboundOrderInDBBase(OutboundOrderBase):
    id: int
    operator_id: Optional[int] = None

    class Config:
        from_attributes = True


# 返回给API的出库单信息
class OutboundOrder(OutboundOrderInDBBase):
    items: List[OutboundItem] = []


# Excel导入响应
class OutboundExcelImportResponse(BaseModel):
    success: bool
    data: Any

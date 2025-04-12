from typing import Optional, List, Any
from datetime import date
from pydantic import BaseModel, Field

from app.models.purchase_order import DeliveryType, PurchaseOrderStatus


# 采购订单项基础模型
class PurchaseOrderItemBase(BaseModel):
    line_item_number: Optional[str] = None
    material_code: str
    material_description: Optional[str] = None
    unit: Optional[str] = None
    requested_quantity: Optional[int] = None
    contract_price: Optional[float] = None
    product_standard: Optional[str] = None
    contract_amount: Optional[float] = None
    long_description: Optional[str] = None
    price_flag: Optional[str] = None
    purchase_order_quantity: Optional[int] = None


# 创建采购订单项时需要的属性
class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


# 更新采购订单项时可以更新的属性
class PurchaseOrderItemUpdate(PurchaseOrderItemBase):
    pass


# 数据库中存储的采购订单项属性
class PurchaseOrderItemInDBBase(PurchaseOrderItemBase):
    id: int
    order_id: int
    
    class Config:
        from_attributes = True


# 返回给API的采购订单项信息
class PurchaseOrderItem(PurchaseOrderItemInDBBase):
    pass


# 采购订单基础模型
class PurchaseOrderBase(BaseModel):
    order_no: str
    plan_number: Optional[str] = None
    user_unit: Optional[str] = None
    category: Optional[str] = None
    order_date: Optional[date] = None
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    material_group: Optional[str] = None
    first_level_product: Optional[str] = None
    factory: Optional[str] = None
    delivery_type: Optional[DeliveryType] = DeliveryType.WAREHOUSE
    total_amount: Optional[float] = 0
    status: Optional[PurchaseOrderStatus] = PurchaseOrderStatus.PENDING


# 创建采购订单时需要的属性
class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]


# 更新采购订单时可以更新的属性
class PurchaseOrderUpdate(BaseModel):
    plan_number: Optional[str] = None
    user_unit: Optional[str] = None
    category: Optional[str] = None
    order_date: Optional[date] = None
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    material_group: Optional[str] = None
    first_level_product: Optional[str] = None
    factory: Optional[str] = None
    delivery_type: Optional[DeliveryType] = None
    total_amount: Optional[float] = None
    status: Optional[PurchaseOrderStatus] = None


# 数据库中存储的采购订单属性
class PurchaseOrderInDBBase(PurchaseOrderBase):
    id: int
    
    class Config:
        from_attributes = True


# 返回给API的采购订单信息
class PurchaseOrder(PurchaseOrderInDBBase):
    items: List[PurchaseOrderItem] = []


# Excel导入响应
class ExcelImportResponse(BaseModel):
    success: bool
    data: Any

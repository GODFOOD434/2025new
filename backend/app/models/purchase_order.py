from sqlalchemy import Column, String, Integer, Float, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class DeliveryType(str, enum.Enum):
    """交付类型枚举"""
    DIRECT = "DIRECT"  # 直达
    WAREHOUSE = "WAREHOUSE"  # 入库


class PurchaseOrderStatus(str, enum.Enum):
    """采购订单状态枚举"""
    PENDING = "PENDING"  # 待处理
    PROCESSING = "PROCESSING"  # 处理中
    CONFIRMED = "CONFIRMED"  # 已确认
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


class PurchaseOrder(BaseModel):
    """采购订单模型"""
    
    order_no = Column(String(32), unique=True, index=True, nullable=False, comment="采购订单号")
    plan_number = Column(String(32), comment="计划编号")
    user_unit = Column(String(100), comment="用户单位")
    category = Column(String(50), index=True, comment="大类")
    order_date = Column(Date, comment="订单生成日期")
    supplier_name = Column(String(100), comment="供应商名称")
    supplier_code = Column(String(32), comment="供应商代码")
    material_group = Column(String(50), comment="物料组")
    first_level_product = Column(String(100), comment="一级目录产品")
    factory = Column(String(100), comment="工厂")
    delivery_type = Column(Enum(DeliveryType), default=DeliveryType.WAREHOUSE, comment="交付类型")
    total_amount = Column(Float, default=0, comment="总金额")
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING, comment="状态")
    
    # 关联项
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")
    workflow = relationship("WorkflowInstance", back_populates="purchase_order", uselist=False)
    confirmation = relationship("DeliveryConfirmation", back_populates="order", uselist=False)


class PurchaseOrderItem(BaseModel):
    """采购订单项模型"""
    
    order_id = Column(Integer, ForeignKey("wh_purchaseorder.id"), nullable=False)
    line_item_number = Column(String(32), comment="行项目号")
    material_code = Column(String(32), index=True, nullable=False, comment="物料编码")
    material_description = Column(String(255), comment="物资描述")
    unit = Column(String(20), comment="计量单位")
    requested_quantity = Column(Integer, comment="申请数量")
    contract_price = Column(Float, comment="签约单价")
    product_standard = Column(String(100), comment="产品标准")
    contract_amount = Column(Float, comment="签约金额")
    long_description = Column(Text, comment="长描述")
    price_flag = Column(String(20), comment="价格标志")
    purchase_order_quantity = Column(Integer, comment="采购订单数")
    
    # 关联项
    order = relationship("PurchaseOrder", back_populates="items")

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class ConfirmationStatus(str, enum.Enum):
    """确认单状态枚举"""
    GENERATED = "GENERATED"  # 已生成
    PRINTED = "PRINTED"  # 已打印
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


class DeliveryConfirmation(BaseModel):
    """交付确认单模型"""
    
    confirmation_no = Column(String(32), unique=True, index=True, nullable=False, comment="确认单号")
    order_id = Column(Integer, ForeignKey("wh_purchaseorder.id"), nullable=False, comment="采购单ID")
    status = Column(Enum(ConfirmationStatus), default=ConfirmationStatus.GENERATED, comment="状态")
    
    # 确认信息
    keeper_id = Column(Integer, ForeignKey("wh_user.id"), comment="保管员ID")
    inspector_id = Column(Integer, ForeignKey("wh_user.id"), comment="质检员ID")
    keeper_confirm_time = Column(DateTime, comment="保管员确认时间")
    inspector_confirm_time = Column(DateTime, comment="质检员确认时间")
    
    # 打印信息
    print_time = Column(DateTime, comment="打印时间")
    print_by = Column(Integer, ForeignKey("wh_user.id"), comment="打印人ID")
    
    # 关联项
    order = relationship("PurchaseOrder", back_populates="confirmation")
    keeper = relationship("User", foreign_keys=[keeper_id])
    inspector = relationship("User", foreign_keys=[inspector_id])
    printer = relationship("User", foreign_keys=[print_by])


class Inventory(BaseModel):
    """库存模型"""
    
    material_code = Column(String(32), index=True, nullable=False, comment="物料编码")
    material_description = Column(String(255), comment="物资描述")
    category = Column(String(50), index=True, comment="大类")
    unit = Column(String(20), comment="计量单位")
    quantity = Column(Float, default=0, comment="库存数量")
    location = Column(String(50), comment="库位")
    
    # 价值信息
    unit_price = Column(Float, comment="单价")
    total_value = Column(Float, comment="总价值")
    
    # 关联项
    inventory_transactions = relationship("InventoryTransaction", back_populates="inventory")


class InventoryTransactionType(str, enum.Enum):
    """库存事务类型枚举"""
    INBOUND = "INBOUND"  # 入库
    OUTBOUND = "OUTBOUND"  # 出库
    ADJUSTMENT = "ADJUSTMENT"  # 调整


class InventoryTransaction(BaseModel):
    """库存事务模型"""
    
    inventory_id = Column(Integer, ForeignKey("wh_inventory.id"), nullable=False)
    transaction_type = Column(Enum(InventoryTransactionType), nullable=False, comment="事务类型")
    quantity = Column(Float, nullable=False, comment="数量")
    transaction_time = Column(DateTime, default=datetime.now, nullable=False, comment="事务时间")
    
    # 相关单据
    reference_no = Column(String(32), comment="参考单号")
    reference_type = Column(String(20), comment="参考单据类型")
    
    # 操作人
    operator_id = Column(Integer, ForeignKey("wh_user.id"), nullable=False, comment="操作人ID")
    
    # 备注
    remark = Column(Text, comment="备注")
    
    # 关联项
    inventory = relationship("Inventory", back_populates="inventory_transactions")
    operator = relationship("User")

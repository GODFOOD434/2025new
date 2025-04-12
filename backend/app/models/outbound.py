from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from app.models.base import BaseModel


class OutboundStatus(str, enum.Enum):
    """出库状态枚举"""
    PENDING = "PENDING"  # 待处理
    PROCESSING = "PROCESSING"  # 处理中
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消
    # 暂时注释掉PDA相关状态，等数据库迁移完成后再启用
    # PDA_ASSIGNED = "PDA_ASSIGNED"  # 已分配给PDA
    # PDA_PROCESSING = "PDA_PROCESSING"  # PDA处理中
    # PDA_COMPLETED = "PDA_COMPLETED"  # PDA处理完成


class OutboundOrder(BaseModel):
    """出库单模型"""

    material_voucher = Column(String(32), unique=True, index=True, nullable=False, comment="物料凭证")
    voucher_date = Column(Date, nullable=False, comment="开单日期")
    department = Column(String(100), nullable=False, comment="具体用料部门")
    user_unit = Column(String(100), nullable=False, comment="用料单位")
    document_type = Column(String(20), comment="单据类型")
    total_amount = Column(Float, default=0, comment="合计金额")
    issue_date = Column(Date, comment="发料日期")
    sales_amount = Column(Float, default=0, comment="销售金额")
    transfer_order = Column(String(32), comment="转储订单/销售订单")
    management_fee_rate = Column(Float, comment="管理费率")
    material_category = Column(String(100), comment="料单分属")
    status = Column(Enum(OutboundStatus), default=OutboundStatus.PENDING, comment="状态")

    # 操作人
    operator_id = Column(Integer, ForeignKey("wh_user.id"), comment="操作人ID")

    # 关联项
    items = relationship("OutboundItem", back_populates="order", cascade="all, delete-orphan")
    operator = relationship("User")

    # PDA相关字段 - 暂时注释掉，等数据库迁移完成后再启用
    # pda_assigned = Column(Integer, default=0, comment="是否分配给PDA: 0-未分配, 1-已分配")
    # pda_assigned_time = Column(DateTime, comment="PDA分配时间")
    # pda_complete_time = Column(DateTime, comment="PDA完成时间")
    # pda_operations = relationship("OutboundPDAOperation", back_populates="outbound_order")


class OutboundItem(BaseModel):
    """出库项模型"""

    outbound_id = Column(Integer, ForeignKey("wh_outboundorder.id"), nullable=False)
    material_code = Column(String(32), index=True, nullable=False, comment="物料编码")
    material_description = Column(String(255), nullable=False, comment="物资名称及规格型号")
    unit = Column(String(20), nullable=False, comment="计量单位")
    actual_quantity = Column(Float, nullable=False, comment="实拨数量")
    outbound_price = Column(Float, comment="出库单价")
    material_category_code = Column(String(20), comment="物资品种码")
    project_code = Column(String(32), comment="工程编码")
    requested_quantity = Column(Float, comment="应拨数量")
    outbound_amount = Column(Float, comment="出库金额")

    # 补充字段
    purchase_order_no = Column(String(32), comment="采购订单号")
    remark = Column(Text, comment="备注")

    # 关联项
    order = relationship("OutboundOrder", back_populates="items")


class DeletedOutboundRecord(BaseModel):
    """已删除出库单审计记录模型"""

    original_id = Column(Integer, comment="原出库单ID")
    material_voucher = Column(String(32), index=True, nullable=False, comment="物料凭证")
    voucher_date = Column(Date, nullable=False, comment="开单日期")
    department = Column(String(100), nullable=False, comment="具体用料部门")
    user_unit = Column(String(100), nullable=False, comment="用料单位")
    document_type = Column(String(20), comment="单据类型")
    total_amount = Column(Float, default=0, comment="合计金额")
    material_category = Column(String(100), comment="料单分属")
    status = Column(String(20), comment="删除时的状态")
    delete_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="删除时间")
    delete_reason = Column(String(255), comment="删除原因")
    items_data = Column(JSON, comment="出库项数据的JSON存储")

    # 删除操作人
    operator_id = Column(Integer, ForeignKey("wh_user.id"), comment="删除操作人ID")
    operator = relationship("User")


# 暂时注释掉PDA相关模型，等数据库迁移完成后再启用

# class PDAOperationStatus(str, enum.Enum):
#     """移动端操作状态枚举"""
#     ASSIGNED = "ASSIGNED"  # 已分配
#     PROCESSING = "PROCESSING"  # 处理中
#     COMPLETED = "COMPLETED"  # 已完成
#     CANCELLED = "CANCELLED"  # 已取消
#     FAILED = "FAILED"  # 失败


# class OutboundPDAOperation(BaseModel):
#     """出库PDA操作模型"""
#
#     outbound_id = Column(Integer, ForeignKey("wh_outboundorder.id"), nullable=False, comment="出库单ID")
#     pda_device_id = Column(String(100), nullable=False, comment="PDA设备ID")
#     operator_id = Column(Integer, ForeignKey("wh_user.id"), comment="操作人ID")
#     status = Column(Enum(PDAOperationStatus), default=PDAOperationStatus.ASSIGNED, comment="状态")
#     assigned_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="分配时间")
#     start_time = Column(DateTime, comment="开始操作时间")
#     complete_time = Column(DateTime, comment="完成时间")
#     sync_time = Column(DateTime, comment="同步到服务器时间")
#     location_data = Column(JSON, comment="位置数据")
#     operation_data = Column(JSON, comment="操作数据")
#     remark = Column(Text, comment="备注")
#
#     # 关联项
#     outbound_order = relationship("OutboundOrder", back_populates="pda_operations")
#     operator = relationship("User")
#     pda_items = relationship("OutboundPDAItem", back_populates="pda_operation", cascade="all, delete-orphan")


# class OutboundPDAItem(BaseModel):
#     """出库PDA操作项模型"""
#
#     pda_operation_id = Column(Integer, ForeignKey("wh_outboundpdaoperation.id"), nullable=False, comment="PDA操作记录ID")
#     outbound_item_id = Column(Integer, ForeignKey("wh_outbounditem.id"), nullable=False, comment="出库项ID")
#     material_code = Column(String(32), index=True, nullable=False, comment="物料编码")
#     actual_quantity = Column(Float, nullable=False, comment="实际出库数量")
#     location = Column(String(100), comment="库位")
#     scan_time = Column(DateTime, comment="扫描时间")
#     status = Column(String(20), default="COMPLETED", comment="状态")
#     remark = Column(Text, comment="备注")
#
#     # 关联项
#     pda_operation = relationship("OutboundPDAOperation", back_populates="pda_items")
#     outbound_item = relationship("OutboundItem")

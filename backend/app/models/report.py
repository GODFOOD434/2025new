from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class ReportType(str, enum.Enum):
    """报表类型枚举"""
    PURCHASE_SUMMARY = "PURCHASE_SUMMARY"  # 采购汇总
    INVENTORY_STATUS = "INVENTORY_STATUS"  # 库存状态
    OUTBOUND_DETAIL = "OUTBOUND_DETAIL"  # 出库明细
    QUALITY_RATE = "QUALITY_RATE"  # 质检合格率
    TEAM_PERFORMANCE = "TEAM_PERFORMANCE"  # 团队绩效


class Report(BaseModel):
    """报表模型"""
    
    report_name = Column(String(100), nullable=False, comment="报表名称")
    report_type = Column(Enum(ReportType), nullable=False, comment="报表类型")
    report_data = Column(JSON, comment="报表数据")
    parameters = Column(JSON, comment="报表参数")
    
    # 生成信息
    generate_time = Column(DateTime, default=datetime.now, nullable=False, comment="生成时间")
    generator_id = Column(Integer, ForeignKey("wh_user.id"), nullable=False, comment="生成人ID")
    
    # 关联项
    generator = relationship("User")


class ReportSubscription(BaseModel):
    """报表订阅模型"""
    
    user_id = Column(Integer, ForeignKey("wh_user.id"), nullable=False, comment="用户ID")
    report_type = Column(Enum(ReportType), nullable=False, comment="报表类型")
    parameters = Column(JSON, comment="报表参数")
    schedule = Column(String(50), comment="调度计划(cron表达式)")
    is_active = Column(Integer, default=1, comment="是否激活")
    
    # 关联项
    user = relationship("User")

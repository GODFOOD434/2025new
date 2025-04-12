from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from app.models.report import ReportType


# 报表基础模型
class ReportBase(BaseModel):
    report_name: str
    report_type: ReportType
    report_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


# 创建报表时需要的属性
class ReportCreate(ReportBase):
    generator_id: int


# 更新报表时可以更新的属性
class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


# 数据库中存储的报表属性
class ReportInDBBase(ReportBase):
    id: int
    generator_id: int
    generate_time: datetime
    
    class Config:
        from_attributes = True


# 返回给API的报表信息
class Report(ReportInDBBase):
    pass


# 报表订阅基础模型
class ReportSubscriptionBase(BaseModel):
    report_type: ReportType
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    is_active: Optional[int] = 1


# 创建报表订阅时需要的属性
class ReportSubscriptionCreate(ReportSubscriptionBase):
    user_id: int


# 更新报表订阅时可以更新的属性
class ReportSubscriptionUpdate(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    is_active: Optional[int] = None


# 数据库中存储的报表订阅属性
class ReportSubscriptionInDBBase(ReportSubscriptionBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


# 返回给API的报表订阅信息
class ReportSubscription(ReportSubscriptionInDBBase):
    pass


# 领导层看板数据请求
class LeadershipDashboardRequest(BaseModel):
    time_range: str  # TODAY, WEEK, MONTH


# 领导层看板数据响应
class LeadershipDashboardResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


# 运营看板数据响应
class OperationDashboardResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

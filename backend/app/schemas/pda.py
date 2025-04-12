from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, date


class PDAOutboundAssignRequest(BaseModel):
    """PDA出库单分配请求"""
    outbound_id: int = Field(..., description="出库单ID")
    device_id: str = Field(..., description="PDA设备ID")
    remark: Optional[str] = Field(None, description="备注")


class PDAOutboundListItem(BaseModel):
    """PDA出库单列表项"""
    operation_id: int
    outbound_id: int
    material_voucher: str
    voucher_date: date
    department: str
    user_unit: str
    status: str
    assigned_time: datetime
    item_count: int


class PDAOutboundListResponse(BaseModel):
    """PDA出库单列表响应"""
    success: bool
    message: str
    data: List[PDAOutboundListItem]
    total: int


class PDAOutboundItemDetail(BaseModel):
    """PDA出库项详情"""
    item_id: int
    material_code: str
    material_description: str
    unit: str
    requested_quantity: float
    actual_quantity: float
    pda_quantity: Optional[float] = None
    location: Optional[str] = None
    status: str
    scan_time: Optional[datetime] = None


class PDAOutboundDetail(BaseModel):
    """PDA出库单详情"""
    operation_id: int
    outbound_id: int
    material_voucher: str
    voucher_date: date
    department: str
    user_unit: str
    document_type: Optional[str] = None
    status: str
    assigned_time: datetime
    start_time: Optional[datetime] = None
    items: List[PDAOutboundItemDetail]


class PDAOutboundDetailResponse(BaseModel):
    """PDA出库单详情响应"""
    success: bool
    message: str
    data: PDAOutboundDetail


class PDAOutboundItemComplete(BaseModel):
    """PDA出库项完成数据"""
    item_id: int
    actual_quantity: float
    location: Optional[str] = None
    remark: Optional[str] = None


class PDAOutboundCompleteRequest(BaseModel):
    """PDA出库单完成请求"""
    operation_id: int
    items: List[PDAOutboundItemComplete]
    location_data: Optional[Dict[str, Any]] = None
    operation_data: Optional[Dict[str, Any]] = None
    remark: Optional[str] = None


class PDAOutboundCompleteData(BaseModel):
    """PDA出库单完成数据"""
    operation_id: int
    outbound_id: int
    status: str
    complete_time: datetime
    sync_time: datetime


class PDAOutboundCompleteResponse(BaseModel):
    """PDA出库单完成响应"""
    success: bool
    message: str
    data: PDAOutboundCompleteData

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.warehouse import InventoryTransactionType


# 库存基础模型
class InventoryBase(BaseModel):
    material_code: str
    material_description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = 0
    location: Optional[str] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None


# 创建库存时需要的属性
class InventoryCreate(InventoryBase):
    pass


# 更新库存时可以更新的属性
class InventoryUpdate(BaseModel):
    material_description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    location: Optional[str] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None


# 数据库中存储的库存属性
class InventoryInDBBase(InventoryBase):
    id: int
    
    class Config:
        from_attributes = True


# 返回给API的库存信息
class Inventory(InventoryInDBBase):
    pass


# 库存事务基础模型
class InventoryTransactionBase(BaseModel):
    inventory_id: int
    transaction_type: InventoryTransactionType
    quantity: float
    reference_no: Optional[str] = None
    reference_type: Optional[str] = None
    remark: Optional[str] = None


# 创建库存事务时需要的属性
class InventoryTransactionCreate(InventoryTransactionBase):
    operator_id: int


# 更新库存事务时可以更新的属性
class InventoryTransactionUpdate(BaseModel):
    reference_no: Optional[str] = None
    reference_type: Optional[str] = None
    remark: Optional[str] = None


# 数据库中存储的库存事务属性
class InventoryTransactionInDBBase(InventoryTransactionBase):
    id: int
    operator_id: int
    transaction_time: datetime
    
    class Config:
        from_attributes = True


# 返回给API的库存事务信息
class InventoryTransaction(InventoryTransactionInDBBase):
    pass

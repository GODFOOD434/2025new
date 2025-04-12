from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.warehouse import Inventory, InventoryTransaction, InventoryTransactionType
from app.schemas.inventory import (
    Inventory as InventorySchema,
    InventoryCreate,
    InventoryUpdate,
    InventoryTransaction as InventoryTransactionSchema
)

router = APIRouter()


@router.get("/list", response_model=dict)
def list_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    material_code: Optional[str] = None,
    material_description: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取库存列表
    """
    # 构建基本查询
    query = db.query(Inventory)

    # 应用过滤条件
    if material_code:
        query = query.filter(Inventory.material_code.ilike(f"%{material_code}%"))
    if material_description:
        query = query.filter(Inventory.material_description.ilike(f"%{material_description}%"))
    if category:
        query = query.filter(Inventory.category.ilike(f"%{category}%"))
    if location:
        query = query.filter(Inventory.location.ilike(f"%{location}%"))

    # 计算总数
    total = query.count()

    # 分页
    query = query.order_by(Inventory.material_code)
    query = query.offset((page - 1) * size).limit(size)

    # 获取结果
    inventories = query.all()

    return {
        "success": True,
        "data": {
            "total": total,
            "pages": (total + size - 1) // size,
            "current": page,
            "records": inventories
        }
    }


@router.post("/", response_model=InventorySchema)
def create_inventory(
    inventory_in: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建库存记录
    """
    # 检查物料编码是否已存在
    existing = db.query(Inventory).filter(Inventory.material_code == inventory_in.material_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"物料编码 {inventory_in.material_code} 已存在"
        )

    # 创建库存记录
    inventory = Inventory(
        material_code=inventory_in.material_code,
        material_description=inventory_in.material_description,
        category=inventory_in.category,
        unit=inventory_in.unit,
        quantity=inventory_in.quantity,
        location=inventory_in.location,
        unit_price=inventory_in.unit_price,
        total_value=inventory_in.quantity * inventory_in.unit_price if inventory_in.unit_price else 0
    )
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    # 如果初始库存大于0，创建入库事务记录
    if inventory.quantity > 0:
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=InventoryTransactionType.INBOUND,
            quantity=inventory.quantity,
            reference_no="INIT",
            reference_type="初始化",
            operator_id=current_user.id,
            remark="初始库存创建"
        )
        db.add(transaction)
        db.commit()

    return inventory


@router.put("/{id}", response_model=InventorySchema)
def update_inventory(
    id: int,
    inventory_in: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新库存记录
    """
    inventory = db.query(Inventory).filter(Inventory.id == id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"库存记录 {id} 不存在"
        )

    # 记录原始数量
    original_quantity = inventory.quantity

    # 更新库存属性
    update_data = inventory_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inventory, field, value)

    # 如果更新了单价，重新计算总价值
    if "unit_price" in update_data:
        inventory.total_value = inventory.quantity * inventory.unit_price if inventory.unit_price else 0

    # 如果更新了数量，创建库存事务记录
    if "quantity" in update_data and inventory.quantity != original_quantity:
        quantity_diff = inventory.quantity - original_quantity
        transaction_type = InventoryTransactionType.INBOUND if quantity_diff > 0 else InventoryTransactionType.OUTBOUND

        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=transaction_type,
            quantity=abs(quantity_diff),
            reference_no="ADJ",
            reference_type="调整",
            operator_id=current_user.id,
            remark=f"手动调整库存，从 {original_quantity} 到 {inventory.quantity}"
        )
        db.add(transaction)

    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


@router.get("/transactions", response_model=dict)
def list_inventory_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    inventory_id: Optional[int] = None,
    material_code: Optional[str] = None,
    transaction_type: Optional[InventoryTransactionType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取库存事务列表
    """
    # 构建基本查询
    query = db.query(InventoryTransaction)

    # 应用过滤条件
    if inventory_id:
        query = query.filter(InventoryTransaction.inventory_id == inventory_id)
    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(InventoryTransaction.transaction_time >= start_date)
    if end_date:
        query = query.filter(InventoryTransaction.transaction_time <= end_date)

    # 如果指定了物料编码，需要联合查询
    if material_code:
        query = query.join(Inventory).filter(
            Inventory.material_code.ilike(f"%{material_code}%")
        )

    # 计算总数
    total = query.count()

    # 分页
    query = query.order_by(InventoryTransaction.transaction_time.desc())
    query = query.offset((page - 1) * size).limit(size)

    # 获取结果
    transactions = query.all()

    # 构建响应数据
    records = []
    for transaction in transactions:
        inventory = transaction.inventory
        operator = transaction.operator

        records.append({
            "id": transaction.id,
            "inventory_id": transaction.inventory_id,
            "material_code": inventory.material_code if inventory else None,
            "material_description": inventory.material_description if inventory else None,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "transaction_time": transaction.transaction_time,
            "reference_no": transaction.reference_no,
            "reference_type": transaction.reference_type,
            "operator": operator.full_name if operator else None,
            "remark": transaction.remark
        })

    return {
        "success": True,
        "data": {
            "total": total,
            "pages": (total + size - 1) // size,
            "current": page,
            "records": records
        }
    }


@router.get("/{id}", response_model=InventorySchema)
def get_inventory(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取库存详情
    """
    inventory = db.query(Inventory).filter(Inventory.id == id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"库存记录 {id} 不存在"
        )
    return inventory

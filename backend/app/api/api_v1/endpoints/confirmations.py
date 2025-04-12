from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder
from app.models.warehouse import DeliveryConfirmation, ConfirmationStatus
from app.schemas.confirmation import (
    DeliveryConfirmation as DeliveryConfirmationSchema,
    ConfirmationGenerate,
    ConfirmationPrintResponse
)

router = APIRouter()


@router.post("/generate", response_model=dict)
def generate_confirmation(
    confirmation_in: ConfirmationGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    生成确认单
    """
    # 查找采购订单
    order = db.query(PurchaseOrder).filter(PurchaseOrder.order_no == confirmation_in.order_no).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"采购订单 {confirmation_in.order_no} 不存在"
        )

    # 检查是否已有确认单
    existing_confirmation = db.query(DeliveryConfirmation).filter(
        DeliveryConfirmation.order_id == order.id
    ).first()

    if existing_confirmation:
        return {
            "success": True,
            "data": {
                "confirmationId": existing_confirmation.id,
                "confirmationNo": existing_confirmation.confirmation_no,
                "orderNo": confirmation_in.order_no,
                "status": existing_confirmation.status,
                "pdfUrl": f"/api/confirmation/{existing_confirmation.id}/pdf"
            }
        }

    # 生成确认单号
    confirmation_no = f"CF{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 创建确认单
    confirmation = DeliveryConfirmation(
        confirmation_no=confirmation_no,
        order_id=order.id,
        status=ConfirmationStatus.GENERATED
    )

    # 如果订单有关联的工作流，获取保管员和质检员信息
    if order.workflow and order.workflow.tasks:
        for task in order.workflow.tasks:
            if task.task_name == "保管员确认":
                confirmation.keeper_id = task.assignee_id
                confirmation.keeper_confirm_time = task.complete_time
            elif task.task_name == "质检员确认":
                confirmation.inspector_id = task.assignee_id
                confirmation.inspector_confirm_time = task.complete_time

    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)

    return {
        "success": True,
        "data": {
            "confirmationId": confirmation.id,
            "confirmationNo": confirmation.confirmation_no,
            "orderNo": confirmation_in.order_no,
            "status": confirmation.status,
            "pdfUrl": f"/api/confirmation/{confirmation.id}/pdf"
        }
    }


@router.post("/{id}/print", response_model=dict)
def print_confirmation(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    打印确认单
    """
    # 查找确认单
    confirmation = db.query(DeliveryConfirmation).filter(DeliveryConfirmation.id == id).first()
    if not confirmation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"确认单 {id} 不存在"
        )

    # 更新打印信息
    confirmation.status = ConfirmationStatus.PRINTED
    confirmation.print_time = datetime.now()
    confirmation.print_by = current_user.id

    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)

    return {
        "success": True,
        "data": {
            "confirmationId": confirmation.id,
            "printTime": confirmation.print_time,
            "printBy": current_user.full_name,
            "status": confirmation.status
        }
    }


@router.get("/list", response_model=dict)
def list_confirmations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_no: Optional[str] = None,
    confirmation_no: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取确认单列表
    """
    # 构建基本查询
    query = db.query(DeliveryConfirmation).join(
        PurchaseOrder, DeliveryConfirmation.order_id == PurchaseOrder.id
    )

    # 应用过滤条件
    if order_no:
        query = query.filter(PurchaseOrder.order_no.ilike(f"%{order_no}%"))
    if confirmation_no:
        query = query.filter(DeliveryConfirmation.confirmation_no.ilike(f"%{confirmation_no}%"))

    # 处理状态参数
    if status:
        try:
            # 尝试将字符串转换为枚举值
            status_enum = ConfirmationStatus(status)
            query = query.filter(DeliveryConfirmation.status == status_enum)
        except ValueError:
            # 如果转换失败，尝试模糊搜索状态名称
            # 将枚举值转换为字符串进行模糊匹配
            status_values = [s.value for s in ConfirmationStatus]
            matching_statuses = [s for s in status_values if status.upper() in s.upper()]
            if matching_statuses:
                query = query.filter(DeliveryConfirmation.status.in_([ConfirmationStatus(s) for s in matching_statuses]))
            else:
                print(f"Invalid status value: {status}")

    # 处理日期参数
    if start_date:
        try:
            # 尝试将字符串转换为日期
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(DeliveryConfirmation.create_time >= start_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid start_date format: {start_date}")

    if end_date:
        try:
            # 尝试将字符串转换为日期
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(DeliveryConfirmation.create_time <= end_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid end_date format: {end_date}")

    # 计算总数
    total = query.count()

    # 分页
    query = query.order_by(DeliveryConfirmation.create_time.desc())
    query = query.offset((page - 1) * size).limit(size)

    # 获取结果
    confirmations = query.all()

    # 构建响应数据
    records = []
    for confirmation in confirmations:
        order = confirmation.order
        keeper = confirmation.keeper
        inspector = confirmation.inspector

        records.append({
            "id": confirmation.id,
            "confirmationNo": confirmation.confirmation_no,
            "orderNo": order.order_no,
            "supplierName": order.supplier_name,
            "category": order.category,
            "userUnit": order.user_unit,
            "status": confirmation.status,
            "keeper": keeper.full_name if keeper else None,
            "inspector": inspector.full_name if inspector else None,
            "createTime": confirmation.create_time,
            "printTime": confirmation.print_time
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


@router.get("/{id}/pdf", response_model=dict)
def get_confirmation_pdf(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取确认单PDF
    """
    # 查找确认单
    confirmation = db.query(DeliveryConfirmation).filter(DeliveryConfirmation.id == id).first()
    if not confirmation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"确认单 {id} 不存在"
        )

    # 在实际应用中，这里应该生成PDF文件并返回文件内容
    # 这里简化处理，只返回成功信息
    return {
        "success": True,
        "data": {
            "url": f"/api/confirmation/{id}/download-pdf"
        }
    }

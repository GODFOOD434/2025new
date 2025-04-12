from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import traceback
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.outbound import (
    OutboundOrder, 
    OutboundItem, 
    OutboundStatus,
    OutboundPDAOperation,
    OutboundPDAItem,
    PDAOperationStatus
)
from app.schemas.pda import (
    PDAOutboundAssignRequest,
    PDAOutboundListResponse,
    PDAOutboundDetailResponse,
    PDAOutboundCompleteRequest,
    PDAOutboundCompleteResponse,
    PDAOutboundItemComplete
)

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/outbound/list", response_model=PDAOutboundListResponse)
def list_pda_outbounds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    device_id: str = Query(..., description="PDA设备ID"),
    status: Optional[str] = Query(None, description="状态过滤")
) -> Any:
    """
    获取分配给PDA的出库单列表
    """
    logger.info(f"Getting PDA outbound list for device: {device_id}, user: {current_user.username}")
    
    try:
        # 构建查询
        query = db.query(OutboundPDAOperation).filter(
            OutboundPDAOperation.pda_device_id == device_id,
            OutboundPDAOperation.operator_id == current_user.id
        )
        
        # 应用状态过滤
        if status:
            try:
                status_enum = PDAOperationStatus(status)
                query = query.filter(OutboundPDAOperation.status == status_enum)
            except ValueError:
                logger.warning(f"Invalid status filter: {status}")
        
        # 执行查询
        operations = query.all()
        logger.info(f"Found {len(operations)} PDA operations")
        
        # 获取关联的出库单信息
        outbound_ids = [op.outbound_id for op in operations]
        outbounds = db.query(OutboundOrder).filter(OutboundOrder.id.in_(outbound_ids)).all()
        
        # 构建响应数据
        outbound_map = {outbound.id: outbound for outbound in outbounds}
        result = []
        
        for operation in operations:
            outbound = outbound_map.get(operation.outbound_id)
            if outbound:
                result.append({
                    "operation_id": operation.id,
                    "outbound_id": outbound.id,
                    "material_voucher": outbound.material_voucher,
                    "voucher_date": outbound.voucher_date,
                    "department": outbound.department,
                    "user_unit": outbound.user_unit,
                    "status": operation.status,
                    "assigned_time": operation.assigned_time,
                    "item_count": len(outbound.items) if outbound.items else 0
                })
        
        return {
            "success": True,
            "message": "获取PDA出库单列表成功",
            "data": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error getting PDA outbound list: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取PDA出库单列表失败: {str(e)}"
        )


@router.get("/outbound/{id}", response_model=PDAOutboundDetailResponse)
def get_pda_outbound(
    id: int = Path(..., description="出库单ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    device_id: str = Query(..., description="PDA设备ID")
) -> Any:
    """
    获取PDA出库单详情
    """
    logger.info(f"Getting PDA outbound detail for ID: {id}, device: {device_id}, user: {current_user.username}")
    
    try:
        # 查询出库单
        outbound = db.query(OutboundOrder).filter(OutboundOrder.id == id).first()
        if not outbound:
            logger.warning(f"Outbound order with ID {id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"出库单 {id} 不存在"
            )
        
        # 查询PDA操作记录
        operation = db.query(OutboundPDAOperation).filter(
            OutboundPDAOperation.outbound_id == id,
            OutboundPDAOperation.pda_device_id == device_id,
            OutboundPDAOperation.operator_id == current_user.id
        ).first()
        
        if not operation:
            logger.warning(f"PDA operation for outbound {id} and device {device_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到设备 {device_id} 对应的出库单 {id} 的PDA操作记录"
            )
        
        # 获取出库项
        items = []
        for item in outbound.items:
            # 查询PDA操作项
            pda_item = db.query(OutboundPDAItem).filter(
                OutboundPDAItem.pda_operation_id == operation.id,
                OutboundPDAItem.outbound_item_id == item.id
            ).first()
            
            items.append({
                "item_id": item.id,
                "material_code": item.material_code,
                "material_description": item.material_description,
                "unit": item.unit,
                "requested_quantity": item.requested_quantity,
                "actual_quantity": item.actual_quantity,
                "pda_quantity": pda_item.actual_quantity if pda_item else None,
                "location": pda_item.location if pda_item else None,
                "status": pda_item.status if pda_item else "PENDING",
                "scan_time": pda_item.scan_time if pda_item else None
            })
        
        # 构建响应数据
        result = {
            "operation_id": operation.id,
            "outbound_id": outbound.id,
            "material_voucher": outbound.material_voucher,
            "voucher_date": outbound.voucher_date,
            "department": outbound.department,
            "user_unit": outbound.user_unit,
            "document_type": outbound.document_type,
            "status": operation.status,
            "assigned_time": operation.assigned_time,
            "start_time": operation.start_time,
            "items": items
        }
        
        return {
            "success": True,
            "message": "获取PDA出库单详情成功",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting PDA outbound detail: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取PDA出库单详情失败: {str(e)}"
        )


@router.post("/outbound/assign", response_model=dict)
def assign_outbound_to_pda(
    request: PDAOutboundAssignRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    将出库单分配给PDA设备
    """
    logger.info(f"Assigning outbound {request.outbound_id} to PDA device {request.device_id}")
    
    try:
        # 查询出库单
        outbound = db.query(OutboundOrder).filter(OutboundOrder.id == request.outbound_id).first()
        if not outbound:
            logger.warning(f"Outbound order with ID {request.outbound_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"出库单 {request.outbound_id} 不存在"
            )
        
        # 检查出库单状态
        if outbound.status not in [OutboundStatus.PENDING, OutboundStatus.PROCESSING]:
            logger.warning(f"Outbound order {request.outbound_id} has invalid status: {outbound.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"出库单 {request.outbound_id} 状态不允许分配给PDA: {outbound.status}"
            )
        
        # 检查是否已经分配给PDA
        existing_operation = db.query(OutboundPDAOperation).filter(
            OutboundPDAOperation.outbound_id == request.outbound_id,
            OutboundPDAOperation.status.in_([
                PDAOperationStatus.ASSIGNED,
                PDAOperationStatus.PROCESSING
            ])
        ).first()
        
        if existing_operation:
            logger.warning(f"Outbound order {request.outbound_id} already assigned to PDA device {existing_operation.pda_device_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"出库单 {request.outbound_id} 已分配给PDA设备 {existing_operation.pda_device_id}"
            )
        
        # 创建PDA操作记录
        now = datetime.now(timezone.utc)
        operation = OutboundPDAOperation(
            outbound_id=request.outbound_id,
            pda_device_id=request.device_id,
            operator_id=current_user.id,
            status=PDAOperationStatus.ASSIGNED,
            assigned_time=now,
            remark=request.remark
        )
        
        db.add(operation)
        
        # 更新出库单状态
        outbound.status = OutboundStatus.PDA_ASSIGNED
        outbound.pda_assigned = 1
        outbound.pda_assigned_time = now
        
        # 提交事务
        db.commit()
        db.refresh(operation)
        
        logger.info(f"Successfully assigned outbound {request.outbound_id} to PDA device {request.device_id}, operation ID: {operation.id}")
        
        return {
            "success": True,
            "message": f"成功将出库单 {request.outbound_id} 分配给PDA设备 {request.device_id}",
            "data": {
                "operation_id": operation.id,
                "outbound_id": request.outbound_id,
                "device_id": request.device_id,
                "assigned_time": operation.assigned_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning outbound to PDA: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分配出库单到PDA失败: {str(e)}"
        )


@router.post("/outbound/start", response_model=dict)
def start_pda_outbound(
    operation_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    开始PDA出库操作
    """
    logger.info(f"Starting PDA outbound operation {operation_id}")
    
    try:
        # 查询PDA操作记录
        operation = db.query(OutboundPDAOperation).filter(OutboundPDAOperation.id == operation_id).first()
        if not operation:
            logger.warning(f"PDA operation with ID {operation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDA操作记录 {operation_id} 不存在"
            )
        
        # 检查操作人
        if operation.operator_id != current_user.id:
            logger.warning(f"User {current_user.username} is not authorized to start operation {operation_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权开始此PDA操作"
            )
        
        # 检查状态
        if operation.status != PDAOperationStatus.ASSIGNED:
            logger.warning(f"PDA operation {operation_id} has invalid status: {operation.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDA操作记录 {operation_id} 状态不允许开始: {operation.status}"
            )
        
        # 更新操作状态
        operation.status = PDAOperationStatus.PROCESSING
        operation.start_time = datetime.now(timezone.utc)
        
        # 更新出库单状态
        outbound = db.query(OutboundOrder).filter(OutboundOrder.id == operation.outbound_id).first()
        if outbound:
            outbound.status = OutboundStatus.PDA_PROCESSING
        
        # 提交事务
        db.commit()
        db.refresh(operation)
        
        logger.info(f"Successfully started PDA outbound operation {operation_id}")
        
        return {
            "success": True,
            "message": f"成功开始PDA出库操作 {operation_id}",
            "data": {
                "operation_id": operation.id,
                "outbound_id": operation.outbound_id,
                "status": operation.status,
                "start_time": operation.start_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting PDA outbound operation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始PDA出库操作失败: {str(e)}"
        )


@router.post("/outbound/complete", response_model=PDAOutboundCompleteResponse)
def complete_pda_outbound(
    request: PDAOutboundCompleteRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    完成PDA出库操作
    """
    logger.info(f"Completing PDA outbound operation {request.operation_id}")
    
    try:
        # 查询PDA操作记录
        operation = db.query(OutboundPDAOperation).filter(OutboundPDAOperation.id == request.operation_id).first()
        if not operation:
            logger.warning(f"PDA operation with ID {request.operation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDA操作记录 {request.operation_id} 不存在"
            )
        
        # 检查操作人
        if operation.operator_id != current_user.id:
            logger.warning(f"User {current_user.username} is not authorized to complete operation {request.operation_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权完成此PDA操作"
            )
        
        # 检查状态
        if operation.status != PDAOperationStatus.PROCESSING:
            logger.warning(f"PDA operation {request.operation_id} has invalid status: {operation.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDA操作记录 {request.operation_id} 状态不允许完成: {operation.status}"
            )
        
        # 查询出库单
        outbound = db.query(OutboundOrder).filter(OutboundOrder.id == operation.outbound_id).first()
        if not outbound:
            logger.warning(f"Outbound order with ID {operation.outbound_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"出库单 {operation.outbound_id} 不存在"
            )
        
        # 获取出库项
        outbound_items = {item.id: item for item in outbound.items}
        
        # 处理每个出库项
        now = datetime.now(timezone.utc)
        for item_data in request.items:
            outbound_item = outbound_items.get(item_data.item_id)
            if not outbound_item:
                logger.warning(f"Outbound item with ID {item_data.item_id} not found")
                continue
            
            # 查询或创建PDA操作项
            pda_item = db.query(OutboundPDAItem).filter(
                OutboundPDAItem.pda_operation_id == operation.id,
                OutboundPDAItem.outbound_item_id == item_data.item_id
            ).first()
            
            if pda_item:
                # 更新现有记录
                pda_item.actual_quantity = item_data.actual_quantity
                pda_item.location = item_data.location
                pda_item.scan_time = now
                pda_item.status = "COMPLETED"
                pda_item.remark = item_data.remark
            else:
                # 创建新记录
                pda_item = OutboundPDAItem(
                    pda_operation_id=operation.id,
                    outbound_item_id=item_data.item_id,
                    material_code=outbound_item.material_code,
                    actual_quantity=item_data.actual_quantity,
                    location=item_data.location,
                    scan_time=now,
                    status="COMPLETED",
                    remark=item_data.remark
                )
                db.add(pda_item)
        
        # 更新操作记录
        operation.status = PDAOperationStatus.COMPLETED
        operation.complete_time = now
        operation.sync_time = now
        operation.location_data = request.location_data
        operation.operation_data = request.operation_data
        operation.remark = request.remark
        
        # 更新出库单状态
        outbound.status = OutboundStatus.PDA_COMPLETED
        outbound.pda_complete_time = now
        
        # 提交事务
        db.commit()
        
        logger.info(f"Successfully completed PDA outbound operation {request.operation_id}")
        
        return {
            "success": True,
            "message": f"成功完成PDA出库操作 {request.operation_id}",
            "data": {
                "operation_id": operation.id,
                "outbound_id": operation.outbound_id,
                "status": operation.status,
                "complete_time": operation.complete_time,
                "sync_time": operation.sync_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing PDA outbound operation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完成PDA出库操作失败: {str(e)}"
        )


@router.post("/outbound/cancel", response_model=dict)
def cancel_pda_outbound(
    operation_id: int = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    取消PDA出库操作
    """
    logger.info(f"Cancelling PDA outbound operation {operation_id}")
    
    try:
        # 查询PDA操作记录
        operation = db.query(OutboundPDAOperation).filter(OutboundPDAOperation.id == operation_id).first()
        if not operation:
            logger.warning(f"PDA operation with ID {operation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDA操作记录 {operation_id} 不存在"
            )
        
        # 检查操作人
        if operation.operator_id != current_user.id:
            logger.warning(f"User {current_user.username} is not authorized to cancel operation {operation_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权取消此PDA操作"
            )
        
        # 检查状态
        if operation.status not in [PDAOperationStatus.ASSIGNED, PDAOperationStatus.PROCESSING]:
            logger.warning(f"PDA operation {operation_id} has invalid status: {operation.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDA操作记录 {operation_id} 状态不允许取消: {operation.status}"
            )
        
        # 更新操作状态
        operation.status = PDAOperationStatus.CANCELLED
        operation.remark = f"取消原因: {reason}"
        
        # 更新出库单状态
        outbound = db.query(OutboundOrder).filter(OutboundOrder.id == operation.outbound_id).first()
        if outbound:
            outbound.status = OutboundStatus.PENDING  # 恢复到待处理状态
            outbound.pda_assigned = 0
        
        # 提交事务
        db.commit()
        
        logger.info(f"Successfully cancelled PDA outbound operation {operation_id}")
        
        return {
            "success": True,
            "message": f"成功取消PDA出库操作 {operation_id}",
            "data": {
                "operation_id": operation.id,
                "outbound_id": operation.outbound_id,
                "status": operation.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling PDA outbound operation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消PDA出库操作失败: {str(e)}"
        )

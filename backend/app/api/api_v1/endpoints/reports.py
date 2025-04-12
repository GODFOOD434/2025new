from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from app.models.warehouse import Inventory, InventoryTransaction, InventoryTransactionType
from app.models.outbound import OutboundOrder, OutboundStatus
from app.models.workflow import WorkflowInstance, WorkflowTask, WorkflowStatus, TaskStatus
from app.schemas.report import (
    LeadershipDashboardResponse,
    OperationDashboardResponse
)

router = APIRouter()


@router.get("/dashboard/leadership", response_model=LeadershipDashboardResponse)
def get_leadership_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    time_range: str = "MONTH",  # TODAY, WEEK, MONTH
) -> Any:
    """
    获取领导层看板数据
    """
    # 根据时间范围确定起始日期
    today = date.today()
    if time_range == "TODAY":
        start_date = today
    elif time_range == "WEEK":
        start_date = today - timedelta(days=today.weekday())
    else:  # MONTH
        start_date = date(today.year, today.month, 1)
    
    # 采购订单统计
    order_count = db.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.order_date >= start_date
    ).scalar() or 0
    
    order_amount = db.query(func.sum(PurchaseOrder.total_amount)).filter(
        PurchaseOrder.order_date >= start_date
    ).scalar() or 0
    
    # 待处理工作流数量
    pending_workflow_count = db.query(func.count(WorkflowInstance.id)).filter(
        WorkflowInstance.status == WorkflowStatus.RUNNING,
        WorkflowInstance.create_time >= datetime.combine(start_date, datetime.min.time())
    ).scalar() or 0
    
    # 质检通过率
    total_tasks = db.query(func.count(WorkflowTask.id)).filter(
        WorkflowTask.task_name == "质检员确认",
        WorkflowTask.status == TaskStatus.COMPLETED,
        WorkflowTask.complete_time >= datetime.combine(start_date, datetime.min.time())
    ).scalar() or 0
    
    passed_tasks = db.query(func.count(WorkflowTask.id)).filter(
        WorkflowTask.task_name == "质检员确认",
        WorkflowTask.status == TaskStatus.COMPLETED,
        WorkflowTask.result == "APPROVED",
        WorkflowTask.complete_time >= datetime.combine(start_date, datetime.min.time())
    ).scalar() or 0
    
    quality_pass_rate = passed_tasks / total_tasks if total_tasks > 0 else 1.0
    
    # 库存价值
    inventory_value = db.query(func.sum(Inventory.total_value)).scalar() or 0
    
    # 订单趋势
    if time_range == "TODAY":
        # 按小时统计
        order_trend = []
        for hour in range(24):
            start_hour = datetime.combine(today, datetime.min.time()) + timedelta(hours=hour)
            end_hour = start_hour + timedelta(hours=1)
            
            count = db.query(func.count(PurchaseOrder.id)).filter(
                PurchaseOrder.create_time >= start_hour,
                PurchaseOrder.create_time < end_hour
            ).scalar() or 0
            
            amount = db.query(func.sum(PurchaseOrder.total_amount)).filter(
                PurchaseOrder.create_time >= start_hour,
                PurchaseOrder.create_time < end_hour
            ).scalar() or 0
            
            order_trend.append({
                "date": start_hour.strftime("%H:00"),
                "count": count,
                "amount": amount
            })
    elif time_range == "WEEK":
        # 按天统计
        order_trend = []
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            count = db.query(func.count(PurchaseOrder.id)).filter(
                PurchaseOrder.order_date == current_date
            ).scalar() or 0
            
            amount = db.query(func.sum(PurchaseOrder.total_amount)).filter(
                PurchaseOrder.order_date == current_date
            ).scalar() or 0
            
            order_trend.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": count,
                "amount": amount
            })
    else:  # MONTH
        # 按天统计
        order_trend = []
        days_in_month = (date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)) - date(today.year, today.month, 1)
        
        for day in range(days_in_month.days):
            current_date = start_date + timedelta(days=day)
            
            count = db.query(func.count(PurchaseOrder.id)).filter(
                PurchaseOrder.order_date == current_date
            ).scalar() or 0
            
            amount = db.query(func.sum(PurchaseOrder.total_amount)).filter(
                PurchaseOrder.order_date == current_date
            ).scalar() or 0
            
            order_trend.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": count,
                "amount": amount
            })
    
    # 大类分布
    category_distribution = []
    categories = db.query(PurchaseOrder.category, func.count(PurchaseOrder.id), func.sum(PurchaseOrder.total_amount)).filter(
        PurchaseOrder.order_date >= start_date
    ).group_by(PurchaseOrder.category).all()
    
    for category, count, amount in categories:
        if category:
            category_distribution.append({
                "category": category,
                "count": count,
                "amount": amount or 0,
                "percentage": count / order_count if order_count > 0 else 0
            })
    
    # 用户单位分布
    user_unit_distribution = []
    user_units = db.query(PurchaseOrder.user_unit, func.count(PurchaseOrder.id), func.sum(PurchaseOrder.total_amount)).filter(
        PurchaseOrder.order_date >= start_date
    ).group_by(PurchaseOrder.user_unit).all()
    
    for user_unit, count, amount in user_units:
        if user_unit:
            user_unit_distribution.append({
                "userUnit": user_unit,
                "count": count,
                "amount": amount or 0,
                "percentage": count / order_count if order_count > 0 else 0
            })
    
    # 警报信息
    alerts = []
    
    # 超时工作流
    timeout_threshold = datetime.now() - timedelta(hours=24)
    timeout_workflows = db.query(func.count(WorkflowInstance.id)).filter(
        WorkflowInstance.status == WorkflowStatus.RUNNING,
        WorkflowInstance.create_time < timeout_threshold
    ).scalar() or 0
    
    if timeout_workflows > 0:
        alerts.append({
            "type": "WORKFLOW_TIMEOUT",
            "message": f"{timeout_workflows}个工作流超过24小时未处理",
            "count": timeout_workflows,
            "level": "WARNING"
        })
    
    # 库存预警
    low_inventory_count = db.query(func.count(Inventory.id)).filter(
        Inventory.quantity <= 10  # 假设低于10为预警
    ).scalar() or 0
    
    if low_inventory_count > 0:
        alerts.append({
            "type": "LOW_INVENTORY",
            "message": f"{low_inventory_count}种物料库存不足",
            "count": low_inventory_count,
            "level": "WARNING"
        })
    
    return {
        "success": True,
        "data": {
            "orderCount": order_count,
            "orderAmount": order_amount,
            "pendingWorkflowCount": pending_workflow_count,
            "qualityPassRate": quality_pass_rate,
            "inventoryValue": inventory_value,
            "orderTrend": order_trend,
            "categoryDistribution": category_distribution,
            "userUnitDistribution": user_unit_distribution,
            "alerts": alerts
        }
    }


@router.get("/dashboard/operation", response_model=OperationDashboardResponse)
def get_operation_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取运营看板数据
    """
    # 工作流统计
    total_workflows = db.query(func.count(WorkflowInstance.id)).scalar() or 0
    running_workflows = db.query(func.count(WorkflowInstance.id)).filter(
        WorkflowInstance.status == WorkflowStatus.RUNNING
    ).scalar() or 0
    completed_workflows = db.query(func.count(WorkflowInstance.id)).filter(
        WorkflowInstance.status == WorkflowStatus.COMPLETED
    ).scalar() or 0
    
    # 平均处理时间（小时）
    avg_process_time_result = db.query(
        func.avg(
            func.extract('epoch', WorkflowInstance.update_time - WorkflowInstance.create_time) / 3600
        )
    ).filter(
        WorkflowInstance.status == WorkflowStatus.COMPLETED
    ).scalar()
    
    avg_process_time = float(avg_process_time_result) if avg_process_time_result else 0
    
    # 按工作流类型统计
    workflow_by_type = []
    workflow_types = db.query(
        WorkflowInstance.workflow_type,
        func.count(WorkflowInstance.id),
        func.avg(func.extract('epoch', WorkflowInstance.update_time - WorkflowInstance.create_time) / 3600)
    ).group_by(WorkflowInstance.workflow_type).all()
    
    for wf_type, count, avg_time in workflow_types:
        workflow_by_type.append({
            "type": wf_type,
            "count": count,
            "avgTime": float(avg_time) if avg_time else 0
        })
    
    # 仓储统计
    total_inventory_count = db.query(func.count(Inventory.id)).scalar() or 0
    total_inventory_value = db.query(func.sum(Inventory.total_value)).scalar() or 0
    
    # 库位使用率（假设）
    location_usage = 0.75
    
    # 入库和出库数量
    inbound_count = db.query(func.count(InventoryTransaction.id)).filter(
        InventoryTransaction.transaction_type == InventoryTransactionType.INBOUND
    ).scalar() or 0
    
    outbound_count = db.query(func.count(InventoryTransaction.id)).filter(
        InventoryTransaction.transaction_type == InventoryTransactionType.OUTBOUND
    ).scalar() or 0
    
    # 周转率
    turnover_rate = outbound_count / inbound_count if inbound_count > 0 else 0
    
    # 按大类统计库存
    inventory_by_category = []
    inventory_categories = db.query(
        Inventory.category,
        func.sum(Inventory.quantity),
        func.sum(Inventory.total_value)
    ).group_by(Inventory.category).all()
    
    for category, quantity, value in inventory_categories:
        if category:
            inventory_by_category.append({
                "category": category,
                "quantity": float(quantity) if quantity else 0,
                "value": float(value) if value else 0
            })
    
    # 质检统计
    inspection_count = db.query(func.count(WorkflowTask.id)).filter(
        WorkflowTask.task_name == "质检员确认",
        WorkflowTask.status == TaskStatus.COMPLETED
    ).scalar() or 0
    
    pass_count = db.query(func.count(WorkflowTask.id)).filter(
        WorkflowTask.task_name == "质检员确认",
        WorkflowTask.status == TaskStatus.COMPLETED,
        WorkflowTask.result == "APPROVED"
    ).scalar() or 0
    
    fail_count = inspection_count - pass_count
    pass_rate = pass_count / inspection_count if inspection_count > 0 else 1.0
    
    # 失败原因（假设数据）
    fail_reasons = [
        {
            "reason": "规格不符",
            "count": 5,
            "percentage": 0.56
        },
        {
            "reason": "质量问题",
            "count": 3,
            "percentage": 0.33
        },
        {
            "reason": "其他原因",
            "count": 1,
            "percentage": 0.11
        }
    ]
    
    return {
        "success": True,
        "data": {
            "workflowStats": {
                "total": total_workflows,
                "running": running_workflows,
                "completed": completed_workflows,
                "avgProcessTime": avg_process_time,
                "byType": workflow_by_type
            },
            "storageStats": {
                "locationUsage": location_usage,
                "inboundCount": inbound_count,
                "outboundCount": outbound_count,
                "turnoverRate": turnover_rate,
                "byCategory": inventory_by_category
            },
            "qualityStats": {
                "inspectionCount": inspection_count,
                "passCount": pass_count,
                "failCount": fail_count,
                "passRate": pass_rate,
                "failReasons": fail_reasons
            }
        }
    }

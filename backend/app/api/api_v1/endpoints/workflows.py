from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder, DeliveryType
from app.models.workflow import (
    WorkflowInstance, WorkflowTask, StaffAssignment,
    WorkflowType, WorkflowStatus, TaskStatus
)
from app.schemas.workflow import (
    WorkflowInstance as WorkflowInstanceSchema,
    WorkflowTask as WorkflowTaskSchema,
    WorkflowStart,
    TaskComplete
)

router = APIRouter()


@router.post("/start", response_model=dict)
def start_workflow(
    workflow_in: WorkflowStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    发起工作流
    """
    # 查找采购订单
    order = db.query(PurchaseOrder).filter(PurchaseOrder.order_no == workflow_in.order_no).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"采购订单 {workflow_in.order_no} 不存在"
        )
    
    # 检查是否已有工作流
    existing_workflow = db.query(WorkflowInstance).filter(
        WorkflowInstance.business_key == workflow_in.order_no,
        WorkflowInstance.workflow_type == workflow_in.workflow_type
    ).first()
    
    if existing_workflow and existing_workflow.status in [WorkflowStatus.CREATED, WorkflowStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"采购订单 {workflow_in.order_no} 已有进行中的工作流"
        )
    
    # 设置交付类型
    if workflow_in.delivery_type:
        order.delivery_type = DeliveryType(workflow_in.delivery_type)
    
    # 创建工作流实例
    workflow = WorkflowInstance(
        process_instance_id=f"WF{datetime.now().strftime('%Y%m%d%H%M%S')}",
        business_key=workflow_in.order_no,
        workflow_type=workflow_in.workflow_type,
        status=WorkflowStatus.RUNNING,
        initiator_id=current_user.id,
        purchase_order_id=order.id
    )
    db.add(workflow)
    db.flush()
    
    # 根据大类和用户单位分配任务
    tasks = []
    
    # 分配保管员任务
    keeper_assignment = db.query(StaffAssignment).filter(
        StaffAssignment.role_type == "keeper",
        StaffAssignment.category == order.category,
        StaffAssignment.user_unit == order.user_unit
    ).first()
    
    if not keeper_assignment:
        # 如果没有精确匹配，尝试只按大类匹配
        keeper_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "keeper",
            StaffAssignment.category == order.category
        ).first()
    
    if not keeper_assignment:
        # 如果仍然没有匹配，尝试只按用户单位匹配
        keeper_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "keeper",
            StaffAssignment.user_unit == order.user_unit
        ).first()
    
    if keeper_assignment:
        keeper_task = WorkflowTask(
            task_id=f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}1",
            workflow_instance_id=workflow.id,
            task_name="保管员确认",
            status=TaskStatus.PENDING,
            assignee_id=keeper_assignment.staff_id
        )
        db.add(keeper_task)
        tasks.append(keeper_task)
    else:
        # 如果没有找到匹配的保管员，可以分配给保管组长或系统管理员
        # 这里简化处理，实际应用中可能需要更复杂的逻辑
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法找到匹配的保管员处理该订单"
        )
    
    # 分配质检员任务
    inspector_assignment = db.query(StaffAssignment).filter(
        StaffAssignment.role_type == "inspector",
        StaffAssignment.category == order.category,
        StaffAssignment.user_unit == order.user_unit
    ).first()
    
    if not inspector_assignment:
        # 如果没有精确匹配，尝试只按大类匹配
        inspector_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "inspector",
            StaffAssignment.category == order.category
        ).first()
    
    if not inspector_assignment:
        # 如果仍然没有匹配，尝试只按用户单位匹配
        inspector_assignment = db.query(StaffAssignment).filter(
            StaffAssignment.role_type == "inspector",
            StaffAssignment.user_unit == order.user_unit
        ).first()
    
    if inspector_assignment:
        inspector_task = WorkflowTask(
            task_id=f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}2",
            workflow_instance_id=workflow.id,
            task_name="质检员确认",
            status=TaskStatus.PENDING,
            assignee_id=inspector_assignment.staff_id
        )
        db.add(inspector_task)
        tasks.append(inspector_task)
    else:
        # 如果没有找到匹配的质检员，可以分配给质检组长或系统管理员
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法找到匹配的质检员处理该订单"
        )
    
    # 提交事务
    db.commit()
    
    # 刷新对象以获取完整数据
    db.refresh(workflow)
    
    # 返回工作流信息
    return {
        "success": True,
        "data": {
            "workflowInstanceId": workflow.id,
            "processInstanceId": workflow.process_instance_id,
            "status": workflow.status,
            "tasks": tasks
        }
    }


@router.post("/task/{task_id}/complete", response_model=dict)
def complete_task(
    task_id: str,
    task_complete: TaskComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    完成任务
    """
    # 查找任务
    task = db.query(WorkflowTask).filter(WorkflowTask.task_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务 {task_id} 不是待处理状态"
        )
    
    # 检查任务是否分配给当前用户
    if task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"任务 {task_id} 不是分配给您的"
        )
    
    # 更新任务状态
    task.status = TaskStatus.COMPLETED
    task.complete_time = datetime.now()
    task.result = "APPROVED" if task_complete.approved else "REJECTED"
    task.comment = task_complete.comment
    
    # 获取工作流实例
    workflow = task.workflow_instance
    
    # 检查是否所有任务都已完成
    all_tasks = db.query(WorkflowTask).filter(WorkflowTask.workflow_instance_id == workflow.id).all()
    all_completed = all(t.status == TaskStatus.COMPLETED for t in all_tasks)
    
    # 如果所有任务都已完成，更新工作流状态
    if all_completed:
        workflow.status = WorkflowStatus.COMPLETED
    
    # 提交事务
    db.commit()
    
    # 刷新对象以获取完整数据
    db.refresh(task)
    
    # 返回任务完成信息
    return {
        "success": True,
        "data": {
            "taskId": task.id,
            "status": task.status,
            "completeTime": task.complete_time,
            "nextTasks": []  # 简化处理，实际应用中可能需要返回下一步任务
        }
    }


@router.get("/tasks/todo", response_model=dict)
def get_todo_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workflow_type: Optional[WorkflowType] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取待办任务
    """
    # 构建查询
    query = db.query(WorkflowTask).filter(
        WorkflowTask.assignee_id == current_user.id,
        WorkflowTask.status == TaskStatus.PENDING
    )
    
    # 如果指定了工作流类型，进一步过滤
    if workflow_type:
        query = query.join(WorkflowInstance).filter(WorkflowInstance.workflow_type == workflow_type)
    
    # 计算总数
    total = query.count()
    
    # 分页
    query = query.order_by(WorkflowTask.create_time.desc())
    query = query.offset((page - 1) * size).limit(size)
    
    # 获取结果
    tasks = query.all()
    
    # 构建响应数据
    records = []
    for task in tasks:
        workflow = task.workflow_instance
        order = workflow.purchase_order
        
        records.append({
            "id": task.id,
            "taskId": task.task_id,
            "taskName": task.task_name,
            "workflowInstanceId": workflow.id,
            "businessKey": workflow.business_key,
            "createTime": task.create_time,
            "dueDate": task.create_time,  # 简化处理，实际应用中可能需要计算截止日期
            "priority": "NORMAL",
            "orderInfo": {
                "orderNo": order.order_no if order else None,
                "supplierName": order.supplier_name if order else None,
                "category": order.category if order else None,
                "userUnit": order.user_unit if order else None
            }
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

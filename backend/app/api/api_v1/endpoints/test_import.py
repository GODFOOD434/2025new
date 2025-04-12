"""
测试导入功能
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import logging
import traceback
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.outbound import OutboundOrder, OutboundItem, OutboundStatus

router = APIRouter()

@router.post("/test-import")
async def test_import_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
) -> Any:
    """
    测试导入功能
    """
    # 设置日志
    logger = logging.getLogger("test_import")
    logger.setLevel(logging.DEBUG)

    # 创建一个新的数据库会话
    from app.db.session import SessionLocal
    new_db = SessionLocal()

    try:
        # 使用新的数据库会话
        db = new_db

        # 检查文件类型，支持大小写扩展名
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )

        # 转换为小写进行比较，支持大小写扩展名
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith('.xls') or filename_lower.endswith('.xlsx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持Excel文件(.xls, .xlsx, .XLS, .XLSX)"
            )

        # 读取文件
        contents = await file.read()
        await file.seek(0)

        # 读取Excel文件
        df = pd.read_excel(file.file)

        # 创建一个测试出库单
        test_order = OutboundOrder(
            material_voucher="TEST" + date.today().strftime("%Y%m%d"),
            voucher_date=date.today(),
            department="测试部门",
            user_unit="测试单位",
            document_type="测试类型",
            total_amount=100.0,
            status=OutboundStatus.PENDING,
            operator_id=current_user.id
        )

        # 添加到会话
        db.add(test_order)
        db.flush()

        # 创建一个测试出库项
        test_item = OutboundItem(
            outbound_id=test_order.id,
            material_code="M001",
            material_description="测试物料",
            unit="个",
            actual_quantity=10.0,
            outbound_price=10.0,
            outbound_amount=100.0,
            purchase_order_no="PO001",
            remark=""
        )

        # 添加到会话
        db.add(test_item)

        # 提交事务
        db.commit()

        return {
            "success": True,
            "message": "测试导入成功",
            "order_id": test_order.id
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Test import failed: {str(e)}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试导入失败: {str(e)}"
        )

    finally:
        # 关闭数据库会话
        new_db.close()

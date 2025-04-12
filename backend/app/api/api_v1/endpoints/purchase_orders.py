from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
import pandas as pd
from datetime import date, datetime
import traceback
import sys
import logging

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, DeliveryType
from app.schemas.purchase_order import (
    PurchaseOrder as PurchaseOrderSchema,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    ExcelImportResponse
)

router = APIRouter()


@router.get("/list", response_model=dict)
def list_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_no: Optional[str] = None,
    supplier_name: Optional[str] = None,
    material_code: Optional[str] = None,
    category: Optional[str] = None,
    user_unit: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取采购订单列表
    """
    query = db.query(PurchaseOrder)

    # 应用过滤条件
    if order_no:
        query = query.filter(PurchaseOrder.order_no.ilike(f"%{order_no}%"))
    if supplier_name:
        query = query.filter(PurchaseOrder.supplier_name.ilike(f"%{supplier_name}%"))
    if category:
        query = query.filter(PurchaseOrder.category.ilike(f"%{category}%"))
    if user_unit:
        query = query.filter(PurchaseOrder.user_unit.ilike(f"%{user_unit}%"))
    if start_date:
        try:
            # 尝试将字符串转换为日期
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(PurchaseOrder.order_date >= start_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid start_date format: {start_date}")
    if end_date:
        try:
            # 尝试将字符串转换为日期
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(PurchaseOrder.order_date <= end_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid end_date format: {end_date}")

    # 如果指定了物料编码，需要联合查询
    if material_code:
        query = query.join(PurchaseOrderItem).filter(
            PurchaseOrderItem.material_code.ilike(f"%{material_code}%")
        ).distinct()

    # 打印SQL查询
    print(f"SQL query: {query}")

    # 计算总数
    total = query.count()
    print(f"Total count: {total}")

    # 分页
    query = query.order_by(PurchaseOrder.id.desc())
    query = query.offset((page - 1) * size).limit(size)

    # 获取结果
    orders = query.all()
    print(f"Retrieved {len(orders)} orders")

    # 转换为响应格式
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "order_no": order.order_no,
            "plan_number": order.plan_number,
            "user_unit": order.user_unit,
            "category": order.category,
            "order_date": order.order_date,
            "supplier_name": order.supplier_name,
            "supplier_code": order.supplier_code,
            "material_group": order.material_group,
            "first_level_product": order.first_level_product,
            "factory": order.factory,
            "delivery_type": order.delivery_type,
            "total_amount": order.total_amount,
            "status": order.status,
            "create_time": order.create_time,
            "update_time": order.update_time
        })

    # 打印响应数据
    print(f"Response data: {result}")

    return {
        "data": result,
        "total": total,
        "page": page,
        "size": size,
        "debug": {
            "query_params": {
                "order_no": order_no,
                "supplier_name": supplier_name,
                "material_code": material_code,
                "category": category,
                "user_unit": user_unit,
                "start_date": start_date,
                "end_date": end_date
            },
            "result_count": len(result)
        }
    }


@router.post("/import", response_model=ExcelImportResponse)
async def import_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    导入采购订单Excel文件
    """
    # 设置详细的错误处理
    logger = logging.getLogger("purchase_import")
    logger.setLevel(logging.DEBUG)

    # 添加控制台处理程序
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f"Starting import process for file: {file.filename}")

    # 检查文件是否存在
    if not file.filename:
        logger.error("File name is empty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )

    # 检查文件类型，支持大小写扩展名
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.xls') or filename_lower.endswith('.xlsx')):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件(.xls, .xlsx, .XLS, .XLSX)"
        )

    try:
        # 读取Excel文件，增强异常处理
        try:
            # 尝试使用不同的引擎读取Excel文件
            try:
                # 首先尝试使用openpyxl引擎，它对新版Excel文件支持更好
                df = pd.read_excel(file.file, engine='openpyxl')
                logger.info("Successfully read Excel file using openpyxl engine")
            except Exception as openpyxl_error:
                logger.warning(f"Failed to read Excel with openpyxl: {str(openpyxl_error)}, trying xlrd engine")
                # 重置文件指针
                await file.seek(0)
                # 尝试使用xlrd引擎，它对旧版Excel文件支持更好
                df = pd.read_excel(file.file, engine='xlrd')
                logger.info("Successfully read Excel file using xlrd engine")
        except Exception as engine_error:
            logger.warning(f"Failed with specific engines: {str(engine_error)}, falling back to default engine")
            # 重置文件指针
            await file.seek(0)
            # 使用默认引擎
            df = pd.read_excel(file.file)
            logger.info("Successfully read Excel file using default engine")

        # 打印原始列名，帮助调试
        logger.info(f"Original Excel columns: {list(df.columns)}")

        # 清理数据前先处理数据
        # 1. 丢弃不需要的列（如“序号”列和无名列）
        unnecessary_columns = []
        for col in df.columns:
            # 检查是否是序号列或无名列
            if col in ["序号", "No.", "#", "Item"] or \
               (isinstance(col, str) and ("Unnamed" in col or col.strip() == "")):
                unnecessary_columns.append(col)

        if unnecessary_columns:
            logger.info(f"Dropping unnecessary columns: {unnecessary_columns}")
            df = df.drop(columns=unnecessary_columns)

        # 2. 处理空行（所有列都为空的行）
        rows_before_empty = len(df)
        df = df.dropna(how='all')
        logger.info(f"Dropped {rows_before_empty - len(df)} completely empty rows")

        # 3. 记录当前行数
        current_rows = len(df)
        logger.info(f"Current row count after dropping empty rows: {current_rows}")

        # 4. 丢弃采购订单号和行项目号为空的行
        if "采购订单号" in df.columns and "行项目号" in df.columns:
            # 先丢弃两个关键列都为空的行
            rows_before = len(df)
            df = df.dropna(subset=["采购订单号", "行项目号"], how='all')
            logger.info(f"Dropped {rows_before - len(df)} rows with both empty order number and line item")

            # 再丢弃采购订单号为空的行（可能是汇总行）
            rows_before = len(df)
            df = df.dropna(subset=["采购订单号"])
            logger.info(f"Dropped {rows_before - len(df)} rows with empty order number")

            # 再丢弃行项目号为空的行（可能是汇总行）
            rows_before = len(df)
            df = df.dropna(subset=["行项目号"])
            logger.info(f"Dropped {rows_before - len(df)} rows with empty line item")

            # 打印当前行数
            logger.info(f"Current row count after all cleaning: {len(df)} rows")

        # 5. 打印清理后的列名
        logger.info(f"Cleaned Excel columns: {list(df.columns)}")

        # 验证必要的列是否存在
        # 定义列名映射，允许使用替代列名
        column_mappings = {
            "采购订单号": ["采购订单号"],
            "行项目号": ["行项目号"],
            "物料编码": ["物料编码", "物资编码"]  # 允许物料编码或物资编码
        }

        # 检查每个必需列是否存在或有替代列
        missing_columns = []
        column_replacements = {}

        for required_col, alternatives in column_mappings.items():
            found = False
            for alt in alternatives:
                if alt in df.columns:
                    found = True
                    # 如果使用的是替代列名，记录下来
                    if alt != required_col:
                        column_replacements[required_col] = alt
                    break
            if not found:
                missing_columns.append(required_col)

        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
            )

        # 如果有替代列名，记录下来
        if column_replacements:
            logger.info(f"Using column replacements: {column_replacements}")

        # 处理数据
        total_count = len(df)
        success_count = 0
        error_count = 0
        error_details = []

        # 打印数据样本，帮助调试
        try:
            sample_data = df.head(2).to_dict(orient='records')
            logger.info(f"Sample data: {sample_data}")
        except Exception as e:
            logger.warning(f"Failed to print sample data: {str(e)}")

        # 检查是否有数据
        if len(df) == 0:
            logger.warning("Excel file is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel文件为空或没有有效数据"
            )

        # 检查采购订单号列是否有数据
        order_no_col = column_replacements.get("采购订单号", "采购订单号")
        if df[order_no_col].isna().all():
            logger.warning("No valid purchase order numbers found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有找到有效的采购订单号"
            )

        try:
            # 按采购订单号分组处理
            order_no_col = column_replacements.get("采购订单号", "采购订单号")
            grouped = df.groupby(order_no_col)
            logger.info(f"Grouped data by purchase order column '{order_no_col}', found {len(grouped)} groups")

            for order_no, group in grouped:
                logger.info(f"Processing order: {order_no} with {len(group)} items")

                # 检查订单是否已存在
                existing_order = db.query(PurchaseOrder).filter(PurchaseOrder.order_no == str(order_no)).first()
                if existing_order:
                    logger.warning(f"Order {order_no} already exists")
                    error_count += len(group)
                    for idx, row in group.iterrows():
                        error_details.append({
                            "rowIndex": idx + 2,  # Excel行号从1开始，标题占一行
                            "errorMessage": f"采购订单号 {order_no} 已存在"
                        })
                    continue

                try:
                    # 提取订单基本信息
                    first_row = group.iloc[0]

                    # 处理日期字段
                    order_date = first_row.get("订单生成日期", None)
                    if order_date is not None:
                        try:
                            # 如果是字符串，尝试转换为日期
                            if isinstance(order_date, str):
                                order_date = datetime.strptime(order_date, '%Y/%m/%d').date()
                            # 如果是时间戳，转换为日期
                            elif isinstance(order_date, (int, float)):
                                order_date = pd.to_datetime(order_date).date()
                        except Exception as e:
                            logger.warning(f"Failed to convert order date: {order_date}, error: {str(e)}")
                            order_date = None

                    logger.info(f"Creating order with date: {order_date}")

                    order = PurchaseOrder(
                        order_no=str(order_no),  # 确保转换为字符串
                        plan_number=str(first_row.get("计划编号", "")) if first_row.get("计划编号") is not None else None,
                        user_unit=str(first_row.get("用户单位", "")) if first_row.get("用户单位") is not None else None,
                        category=str(first_row.get("大类", "")) if first_row.get("大类") is not None else None,
                        order_date=order_date,
                        supplier_name=str(first_row.get("供应商名称", "")) if first_row.get("供应商名称") is not None else None,
                        supplier_code=str(first_row.get("供应商代码", "")) if first_row.get("供应商代码") is not None else None,
                        material_group=str(first_row.get("物料组", "")) if first_row.get("物料组") is not None else None,
                        first_level_product=str(first_row.get("一级目录产品", "")) if first_row.get("一级目录产品") is not None else None,
                        factory=str(first_row.get("工厂", "")) if first_row.get("工厂") is not None else None,
                        delivery_type=DeliveryType.WAREHOUSE,  # 默认为入库
                        status=PurchaseOrderStatus.PENDING
                    )
                    # 添加订单到数据库
                    db.add(order)
                    db.flush()  # 获取订单ID
                    logger.info(f"Created order with ID: {order.id}, order_no: {order.order_no}")

                    # 添加订单项
                    total_amount = 0
                    for idx, row in group.iterrows():
                        try:
                            # 使用正确的列名获取物料编码
                            material_code_col = column_replacements.get("物料编码", "物料编码")
                            material_code = row.get(material_code_col)

                            if not material_code:
                                error_count += 1
                                error_details.append({
                                    "rowIndex": idx + 2,
                                    "errorMessage": "物料编码不能为空"
                                })
                                continue

                            # 转换物料编码为字符串
                            try:
                                if isinstance(material_code, (int, float)):
                                    material_code = str(int(material_code))
                                else:
                                    material_code = str(material_code).strip()

                                logger.info(f"Converted material code: {material_code}")
                            except Exception as e:
                                logger.warning(f"Failed to convert material code: {material_code}, error: {str(e)}")

                            requested_quantity = row.get("申请数量", 0)
                            contract_price = row.get("签约单价", 0)
                            contract_amount = row.get("签约金额", 0)

                            # 如果没有签约金额，尝试计算
                            if not contract_amount and requested_quantity and contract_price:
                                contract_amount = requested_quantity * contract_price

                            item = PurchaseOrderItem(
                                order_id=order.id,
                                line_item_number=row.get("行项目号", None),
                                material_code=material_code,
                                material_description=row.get("物资描述", None),
                                unit=row.get("计量单位", None),
                                requested_quantity=requested_quantity,
                                contract_price=contract_price,
                                product_standard=row.get("产品标准", None),
                                contract_amount=contract_amount,
                                long_description=row.get("长描述", None),
                                price_flag=row.get("价格标志", None),
                                purchase_order_quantity=row.get("采购订单数", requested_quantity)
                            )
                            db.add(item)
                            logger.info(f"Added item with material_code: {material_code}, line_item_number: {row.get('行项目号', None)}")

                            # 累计总金额
                            total_amount += contract_amount if contract_amount else 0
                            success_count += 1
                        except Exception as e:
                            logger.error(f"Error adding item: {str(e)}")
                            logger.error(traceback.format_exc())
                            error_count += 1
                            error_details.append({
                                "rowIndex": idx + 2,
                                "errorMessage": str(e)
                            })

                    # 更新订单总金额
                    order.total_amount = total_amount
                    logger.info(f"Updated order {order.id} total amount to {total_amount}")
                except Exception as e:
                    logger.error(f"Error processing order {order_no}: {str(e)}")
                    logger.error(traceback.format_exc())
                    error_count += len(group)
                    for idx, row in group.iterrows():
                        error_details.append({
                            "rowIndex": idx + 2,
                            "errorMessage": str(e)
                        })
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            logger.error(traceback.format_exc())
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Excel文件处理错误: {str(e)}"
            )

        # 提交事务
        db.commit()
        logger.info(f"Transaction committed successfully. Total orders created: {success_count}")

        # 返回导入结果
        import_id = f"IMP{date.today().strftime('%Y%m%d')}{success_count:03d}"
        return {
            "success": True,
            "data": {
                "totalCount": total_count,
                "successCount": success_count,
                "errorCount": error_count,
                "errorDetails": error_details,
                "importId": import_id
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


@router.get("/{id}", response_model=PurchaseOrderSchema)
def get_purchase_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取采购订单详情
    """
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )
    return order


@router.put("/{id}", response_model=PurchaseOrderSchema)
def update_purchase_order(
    id: int,
    order_in: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新采购订单
    """
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )

    # 更新订单属性
    for field, value in order_in.model_dump(exclude_unset=True).items():
        setattr(order, field, value)

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/debug", response_model=dict)
def debug_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    调试用的API，显示所有采购订单的原始数据
    """
    # 直接查询所有采购订单
    orders = db.query(PurchaseOrder).all()

    # 转换为响应格式
    result = []
    for order in orders:
        order_data = {
            "id": order.id,
            "order_no": order.order_no,
            "plan_number": order.plan_number,
            "user_unit": order.user_unit,
            "category": order.category,
            "order_date": order.order_date,
            "supplier_name": order.supplier_name,
            "supplier_code": order.supplier_code,
            "material_group": order.material_group,
            "first_level_product": order.first_level_product,
            "factory": order.factory,
            "delivery_type": order.delivery_type,
            "total_amount": order.total_amount,
            "status": order.status,
            "create_time": order.create_time,
            "update_time": order.update_time,
            "items_count": db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order.id).count()
        }
        result.append(order_data)

    return {
        "data": result,
        "total": len(result),
        "message": "成功获取所有采购订单数据"
    }


@router.get("/user-units")
def get_user_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取所有用户单位
    """
    try:
        # 查询所有不同的用户单位
        user_units = db.query(PurchaseOrder.user_unit).distinct().filter(PurchaseOrder.user_unit.isnot(None)).all()

        # 转换为列表
        user_unit_list = [unit[0] for unit in user_units if unit[0]]

        # 排序
        user_unit_list.sort()

        print(f"Found {len(user_unit_list)} user units: {user_unit_list}")

        return {
            "data": user_unit_list,
            "total": len(user_unit_list),
            "message": "成功获取用户单位列表"
        }
    except Exception as e:
        print(f"Error getting user units: {str(e)}")
        # 返回空列表而不是错误
        return {
            "data": [],
            "total": 0,
            "message": "获取用户单位列表失败"
        }

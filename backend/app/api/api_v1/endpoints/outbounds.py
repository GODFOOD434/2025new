from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body, Query, Path, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from datetime import date, datetime, timedelta, timezone

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.outbound import OutboundOrder, OutboundItem, OutboundStatus, DeletedOutboundRecord
from app.models.warehouse import Inventory, InventoryTransaction, InventoryTransactionType
import json
import logging
import traceback
import math
import pandas as pd  # 确保已经导入pandas

# 设置日志记录器
logger = logging.getLogger(__name__)

# 通用日期解析函数
def parse_date(date_val, default_value=None, field_name="date"):
    """
    通用日期解析函数，支持多种格式的日期输入

    Args:
        date_val: 要解析的日期值（可以是数字、字符串或日期对象）
        default_value: 解析失败时的默认值
        field_name: 字段名称，用于日志记录

    Returns:
        解析后的日期对象或默认值
    """
    if date_val is None:
        return default_value

    try:
        # 如果是数字，假设是Excel日期格式
        if isinstance(date_val, (int, float)):
            # 处理Excel数字日期
            try:
                # 尝试使用pandas的to_datetime函数转换Excel日期
                excel_date = pd.to_datetime(date_val, unit='D', origin='1899-12-30')
                result_date = excel_date.date()
                logger.info(f"Converted Excel {field_name} {date_val} to {result_date} using pandas")
                return result_date
            except Exception as pd_error:
                logger.warning(f"Pandas conversion failed for {field_name}: {str(pd_error)}, trying manual conversion")
                try:
                    # 如果pandas转换失败，尝试手动转换
                    # Excel日期系统从1899-12-30开始计算，序列号1对应1900-01-01
                    base_date = date(1899, 12, 30)
                    days = int(date_val)
                    result_date = base_date + timedelta(days=days)
                    logger.info(f"Converted Excel {field_name} {date_val} to {result_date} manually")
                    return result_date
                except Exception as manual_error:
                    logger.error(f"Manual conversion failed for {field_name}: {str(manual_error)}")
                    # 如果数字很大，可能是年月日格式（如 20250216）
                    try:
                        date_str = str(int(date_val))
                        if len(date_str) == 8:  # YYYYMMDD
                            year = int(date_str[:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            result_date = date(year, month, day)
                            logger.info(f"Converted numeric {field_name} {date_val} to {result_date} as YYYYMMDD")
                            return result_date
                    except Exception as yyyymmdd_error:
                        logger.error(f"YYYYMMDD conversion failed for {field_name}: {str(yyyymmdd_error)}")

        # 如果是字符串，尝试多种格式解析
        elif isinstance(date_val, str):
            date_str = date_val.strip()
            # 尝试多种日期格式
            formats = [
                "%Y-%m-%d",       # YYYY-MM-DD
                "%Y/%m/%d",       # YYYY/MM/DD
                "%m/%d/%Y",       # MM/DD/YYYY
                "%d/%m/%Y",       # DD/MM/YYYY
                "%Y年%m月%d日",  # YYYY年MM月DD日
                "%Y.%m.%d"        # YYYY.MM.DD
            ]

            # 如果是中文日期格式，先转换为标准格式
            if '年' in date_str or '月' in date_str or '日' in date_str:
                date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')

            # 尝试所有格式
            for fmt in formats:
                try:
                    result_date = datetime.strptime(date_str, fmt).date()
                    logger.info(f"Parsed {field_name} string '{date_str}' to {result_date} using format {fmt}")
                    return result_date
                except ValueError:
                    continue

            logger.warning(f"Failed to parse {field_name} string: {date_str}, using default value")

        # 如果已经是日期对象
        elif hasattr(date_val, 'date'):
            return date_val.date()

    except Exception as e:
        logger.warning(f"Failed to parse {field_name}: {date_val}, using default value. Error: {str(e)}")

    return default_value
from app.schemas.outbound import (
    OutboundOrder as OutboundOrderSchema,
    OutboundOrderCreate,
    OutboundExcelImportResponse,
    BatchDeleteRequest
)

router = APIRouter()


@router.post("/import", response_model=OutboundExcelImportResponse)
async def import_outbound_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    purchase_order_no: str = Form("", description="采购订单号"),
) -> Any:
    # 创建一个新的数据库会话，避免使用依赖注入的会话
    from app.db.session import SessionLocal
    new_db = SessionLocal()
    # 打印请求信息
    print(f"Received file: {file.filename}, content_type: {file.content_type}")

    # 设置详细的错误处理
    import traceback
    import sys
    import logging

    logger = logging.getLogger("outbound_import")
    logger.setLevel(logging.DEBUG)

    # 添加控制台处理程序
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f"Starting import process for file: {file.filename}")
    """
    导入出库Excel文件
    """
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
        print(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件(.xls, .xlsx, .XLS, .XLSX)"
        )

    try:
        # 保存文件内容
        contents = await file.read()
        logger.info(f"File size: {len(contents)} bytes")

        # 重置文件指针
        await file.seek(0)

        # 读取Excel文件
        try:
            logger.info("Attempting to read Excel file...")

            # 定义日期列和转换函数
            date_columns = ["开单日期", "发料日期"]

            # 自定义日期转换函数，处理Excel数字日期
            def convert_excel_date(value):
                if pd.isna(value):
                    return None

                try:
                    # 如果是数字，尝试将其转换为日期
                    if isinstance(value, (int, float)):
                        # 使用pandas的to_datetime函数转换Excel日期
                        return pd.to_datetime(value, unit='D', origin='1899-12-30').date()
                    # 如果已经是日期对象，直接返回
                    elif isinstance(value, (pd.Timestamp, datetime, date)):
                        return value.date() if hasattr(value, 'date') else value
                    # 如果是字符串，尝试解析
                    elif isinstance(value, str):
                        return pd.to_datetime(value).date()
                    return value
                except Exception as e:
                    logger.warning(f"Failed to convert date value {value}: {str(e)}")
                    return value

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

            # 处理空值和特殊值
            # 替换NaN为Null，便于后续处理
            df = df.replace({pd.NA: None, float('nan'): None})

            # 处理列名中的空格和特殊字符
            df.columns = [str(col).strip() for col in df.columns]

            # 尝试处理可能的编码问题
            for col in df.columns:
                if '\ufffd' in col:  # 检测替换字符，表示编码问题
                    logger.warning(f"Detected encoding issue in column name: {col}")
                    # 尝试修复常见的列名
                    if '物料' in col or '凭证' in col:
                        new_col = '物料凭证'
                        df = df.rename(columns={col: new_col})
                        logger.info(f"Renamed column from {col} to {new_col}")
                    elif '开单' in col or '日期' in col:
                        new_col = '开单日期'
                        df = df.rename(columns={col: new_col})
                        logger.info(f"Renamed column from {col} to {new_col}")
                    # 可以根据需要添加更多的列名修复规则

            # 手动处理日期列，确保数字日期被正确转换
            for col in date_columns:
                if col in df.columns:
                    df[col] = df[col].apply(convert_excel_date)

            # 处理可能的编码问题和特殊字符
            for col in df.columns:
                # 检查列中的数据是否包含特殊字符
                if isinstance(col, str) and col.strip() != "":
                    # 处理列名中的特殊字符
                    if '\ufffd' in col or '\u0000' in col:
                        # 尝试修复常见的列名
                        if '物料' in col or '凭证' in col:
                            new_col = '物料凭证'
                            df = df.rename(columns={col: new_col})
                            logger.info(f"Renamed column from {col} to {new_col}")
                        elif '开单' in col or '日期' in col:
                            new_col = '开单日期'
                            df = df.rename(columns={col: new_col})
                            logger.info(f"Renamed column from {col} to {new_col}")

            # 处理列中的空值和特殊值
            for col in df.columns:
                # 检查是否是数值列
                if col in ["实拨数量", "出库单价", "出库金额", "应拨数量"]:
                    # 将空字符串、None、NaN等替换为0
                    df[col] = df[col].apply(lambda x: 0 if pd.isna(x) or (isinstance(x, str) and x.strip() == "") else x)
                    # 尝试将所有值转换为浮点数
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    except Exception as e:
                        logger.warning(f"Failed to convert column {col} to numeric: {str(e)}")

                # 检查是否是字符串列
                elif col in ["物料编码", "物资名称及规格型号", "计量单位", "具体用料部门"]:
                    # 将NaN替换为空字符串
                    df[col] = df[col].fillna("").astype(str)
                    # 去除前后空格
                    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

            logger.info(f"Successfully read Excel file with {len(df)} rows")

            # 打印列名以进行调试
            logger.info(f"Excel columns: {list(df.columns)}")

            # 打印前几行数据以进行调试
            logger.info(f"First few rows: \n{df.head().to_string()}")

            # 打印日期列的数据类型
            for col in date_columns:
                if col in df.columns:
                    logger.info(f"Column {col} data types: {df[col].apply(type).value_counts()}")
        except Exception as excel_error:
            logger.error(f"Error reading Excel file: {str(excel_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法读取Excel文件: {str(excel_error)}"
            )

        # 验证必要的列是否存在
        required_columns = ["物料凭证", "物料编码", "实拨数量", "具体用料部门"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        logger.info(f"Required columns: {required_columns}")
        logger.info(f"Missing columns: {missing_columns}")

        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
            )

        # 处理数据
        total_count = len(df)
        success_count = 0
        error_count = 0
        error_details = []

        # 打印数据库连接状态
        try:
            db_info = db.execute("SELECT version()").scalar()
            logger.info(f"Database connection successful. Version: {db_info}")
        except Exception as db_error:
            logger.error(f"Database connection error: {str(db_error)}")
            logger.error(traceback.format_exc())

        # 按物料凭证分组处理
        logger.info(f"Processing {len(df.groupby('物料凭证'))} unique vouchers")

        for voucher, group in df.groupby("物料凭证"):
            # 确保物料凭证是字符串类型
            voucher_str = str(voucher)
            logger.info(f"Processing voucher: {voucher_str} with {len(group)} items")

            # 检查凭证是否已存在
            try:
                existing_order = db.query(OutboundOrder).filter(OutboundOrder.material_voucher == voucher_str).first()
                if existing_order:
                    logger.warning(f"Voucher {voucher} already exists in database")
                    error_count += len(group)
                    for idx, row in group.iterrows():
                        error_details.append({
                            "rowIndex": idx + 2,  # Excel行号从1开始，标题占一行
                            "errorMessage": f"物料凭证 {voucher} 已存在"
                        })
                    continue

                # 提取出库单基本信息
                first_row = group.iloc[0]
                logger.info(f"First row data: {first_row.to_dict()}")
            except Exception as query_error:
                logger.error(f"Error processing voucher: {str(query_error)}")
                logger.error(traceback.format_exc())
                error_count += len(group)
                for idx, row in group.iterrows():
                    error_details.append({
                        "rowIndex": idx + 2,
                        "errorMessage": f"处理物料凭证 {voucher} 时出错: {str(query_error)}"
                    })
                continue

            # 创建新出库单
            try:

                # 获取日期字段，处理数字格式的日期
                voucher_date_val = first_row.get("开单日期")

                # 特别处理数字格式的日期
                if isinstance(voucher_date_val, (int, float)) and not pd.isna(voucher_date_val):
                    try:
                        # 尝试将数字转换为日期
                        base_date = date(1899, 12, 30)  # Excel日期系统的基准日期
                        days = int(voucher_date_val)
                        voucher_date = base_date + timedelta(days=days)
                        logger.info(f"Converted numeric voucher_date {voucher_date_val} to {voucher_date}")
                    except Exception as e:
                        logger.warning(f"Failed to convert numeric voucher_date {voucher_date_val}: {str(e)}")
                        voucher_date = date.today()
                elif voucher_date_val is None or pd.isna(voucher_date_val):
                    voucher_date = date.today()
                    logger.info(f"Using today's date for voucher_date as it was not provided")
                elif isinstance(voucher_date_val, (date, datetime, pd.Timestamp)):
                    # 如果已经是日期对象，直接使用
                    voucher_date = voucher_date_val.date() if hasattr(voucher_date_val, 'date') else voucher_date_val
                    logger.info(f"Using provided date object for voucher_date: {voucher_date}")
                else:
                    # 如果不是日期对象，使用通用解析函数
                    voucher_date = parse_date(voucher_date_val, default_value=date.today(), field_name="voucher_date")
                    logger.info(f"Parsed voucher_date from {voucher_date_val} to {voucher_date}")

                issue_date_val = first_row.get("发料日期")

                # 特别处理数字格式的日期
                if isinstance(issue_date_val, (int, float)) and not pd.isna(issue_date_val):
                    try:
                        # 尝试将数字转换为日期
                        base_date = date(1899, 12, 30)  # Excel日期系统的基准日期
                        days = int(issue_date_val)
                        issue_date = base_date + timedelta(days=days)
                        logger.info(f"Converted numeric issue_date {issue_date_val} to {issue_date}")
                    except Exception as e:
                        logger.warning(f"Failed to convert numeric issue_date {issue_date_val}: {str(e)}")
                        issue_date = None
                elif issue_date_val is None or pd.isna(issue_date_val):
                    issue_date = None
                    logger.info(f"Using None for issue_date as it was not provided")
                elif isinstance(issue_date_val, (date, datetime, pd.Timestamp)):
                    # 如果已经是日期对象，直接使用
                    issue_date = issue_date_val.date() if hasattr(issue_date_val, 'date') else issue_date_val
                    logger.info(f"Using provided date object for issue_date: {issue_date}")
                else:
                    # 如果不是日期对象，使用通用解析函数
                    issue_date = parse_date(issue_date_val, default_value=None, field_name="issue_date")
                    logger.info(f"Parsed issue_date from {issue_date_val} to {issue_date}")

                # 获取合计金额，如果有提供则使用，否则初始化为0后面计算
                total_amount_val = first_row.get("合计金额", 0)
                # 转换NumPy类型为Python原生类型
                total_amount = float(total_amount_val) if total_amount_val is not None else 0.0

                # 获取并转换字段值为Python原生类型
                department = str(first_row.get("具体用料部门", ""))
                user_unit = str(first_row.get("用料单位", first_row.get("具体用料部门", "")))
                document_type = str(first_row.get("单据类型", "正常出库"))

                sales_amount_val = first_row.get("销售金额", 0)
                sales_amount = float(sales_amount_val) if sales_amount_val is not None else 0.0

                transfer_order = str(first_row.get("转储订单/销售订单", ""))

                management_fee_rate_val = first_row.get("管理费率", 0)
                management_fee_rate = float(management_fee_rate_val) if management_fee_rate_val is not None else 0.0

                material_category = str(first_row.get("料单分属", ""))

                # 创建出库单
                order = OutboundOrder(
                    material_voucher=voucher_str,  # 使用字符串类型的物料凭证
                    voucher_date=voucher_date,
                    department=department,
                    user_unit=user_unit,
                    document_type=document_type,
                    total_amount=total_amount,  # 使用提供的合计金额或初始化为0
                    issue_date=issue_date,
                    sales_amount=sales_amount,
                    transfer_order=transfer_order,
                    management_fee_rate=management_fee_rate,
                    material_category=material_category,  # 添加料单分属字段
                    status=OutboundStatus.PENDING,
                    operator_id=current_user.id
                )
                db.add(order)
                db.flush()  # 获取订单ID

                # 添加出库项
                total_amount = 0
                for idx, row in group.iterrows():
                    try:
                        # 获取并转换物料编码，增强处理逻辑
                        material_code_val = row.get("物料编码")

                        # 检查物料编码是否为空
                        if material_code_val is None or pd.isna(material_code_val) or (isinstance(material_code_val, str) and material_code_val.strip() == ""):
                            error_count += 1
                            error_details.append({
                                "rowIndex": idx + 2,
                                "errorMessage": "物料编码不能为空"
                            })
                            continue

                        try:
                            # 处理不同类型的物料编码
                            if isinstance(material_code_val, (int, float)):
                                # 如果是数字，转换为整数字符串（去除小数点）
                                material_code = str(int(material_code_val))
                            else:
                                # 如果是字符串，去除前后空格
                                material_code = str(material_code_val).strip()

                                # 如果是科学计数法表示的数字（如"1.23e+10"），转换为整数
                                if 'e' in material_code.lower() and '+' in material_code:
                                    try:
                                        material_code = str(int(float(material_code)))
                                    except:
                                        pass  # 如果转换失败，保持原样

                            # 检查物料编码是否有效
                            if not material_code or material_code == 'nan' or material_code == 'None':
                                error_count += 1
                                error_details.append({
                                    "rowIndex": idx + 2,
                                    "errorMessage": f"无效的物料编码: {material_code}"
                                })
                                continue

                            logger.info(f"Converted material_code: {material_code_val} to {material_code}")
                        except Exception as e:
                            error_count += 1
                            error_details.append({
                                "rowIndex": idx + 2,
                                "errorMessage": f"物料编码格式错误: {str(e)}"
                            })
                            continue

                        # 获取并转换实拨数量
                        actual_quantity_val = row.get("实拨数量", 0)
                        try:
                            # 尝试转换为浮点数
                            actual_quantity_float = float(actual_quantity_val) if actual_quantity_val is not None else 0.0
                            if actual_quantity_float <= 0:
                                error_count += 1
                                error_details.append({
                                    "rowIndex": idx + 2,
                                    "errorMessage": "实拨数量必须大于0"
                                })
                                continue
                            actual_quantity = actual_quantity_float
                            logger.info(f"Converted actual_quantity: {actual_quantity_val} to {actual_quantity}")
                        except Exception as e:
                            error_count += 1
                            error_details.append({
                                "rowIndex": idx + 2,
                                "errorMessage": f"实拨数量格式错误: {str(e)}"
                            })
                            continue

                        # 获取并转换出库单价和金额
                        outbound_price_val = row.get("出库单价", 0)
                        try:
                            outbound_price = float(outbound_price_val) if outbound_price_val is not None else 0.0
                            logger.info(f"Converted outbound_price: {outbound_price_val} to {outbound_price}")
                        except Exception as e:
                            logger.warning(f"Error converting outbound_price {outbound_price_val}: {str(e)}, using 0.0")
                            outbound_price = 0.0

                        outbound_amount_val = row.get("出库金额", 0)
                        try:
                            outbound_amount = float(outbound_amount_val) if outbound_amount_val is not None else 0.0
                            logger.info(f"Converted outbound_amount: {outbound_amount_val} to {outbound_amount}")
                        except Exception as e:
                            logger.warning(f"Error converting outbound_amount {outbound_amount_val}: {str(e)}, using 0.0")
                            outbound_amount = 0.0

                        # 如果没有出库金额，但有数量和单价，则计算金额
                        if outbound_amount == 0 and actual_quantity > 0 and outbound_price > 0:
                            outbound_amount = float(actual_quantity) * float(outbound_price)

                        # 检查库存是否足够，仅作提示不阻止上传
                        inventory = db.query(Inventory).filter(Inventory.material_code == material_code).first()
                        if not inventory or inventory.quantity < actual_quantity:
                            # 添加警告信息，但不阻止上传
                            logger.warning(f"物料 {material_code} 库存不足，当前库存: {inventory.quantity if inventory else 0}, 需要: {actual_quantity}")
                            # 添加到错误详情，但不增加错误计数
                            error_details.append({
                                "rowIndex": idx + 2,
                                "errorMessage": f"警告: 物料 {material_code} 库存不足，当前库存: {inventory.quantity if inventory else 0}, 需要: {actual_quantity}"
                            })

                        try:
                            # 打印详细的行数据用于调试
                            logger.info(f"Row data: {row.to_dict()}")

                            # 获取并转换字段值，检查空字段并填充默认值

                            # 物资名称及规格型号
                            material_description_val = row.get("物资名称及规格型号", "")
                            if material_description_val is None or str(material_description_val).strip() == "":
                                logger.warning(f"Row {idx+2}: 物资名称及规格型号 is empty, using material code as description")
                                material_description = f"物料 {material_code}"
                            else:
                                material_description = str(material_description_val)

                            # 计量单位
                            unit_val = row.get("计量单位", "")
                            if unit_val is None or str(unit_val).strip() == "":
                                logger.warning(f"Row {idx+2}: 计量单位 is empty, using default value '件'")
                                unit = "件"
                            else:
                                unit = str(unit_val)

                            # 物资品种码
                            material_category_code_val = row.get("物资品种码", "")
                            if material_category_code_val is None or str(material_category_code_val).strip() == "":
                                logger.warning(f"Row {idx+2}: 物资品种码 is empty, using default value '未分类'")
                                material_category_code = "未分类"
                            else:
                                material_category_code = str(material_category_code_val)

                            # 工程编码
                            project_code_val = row.get("工程编码", "")
                            if project_code_val is None or str(project_code_val).strip() == "":
                                logger.warning(f"Row {idx+2}: 工程编码 is empty, using default value '无工程编码'")
                                project_code = "无工程编码"
                            else:
                                project_code = str(project_code_val)

                            # 应拨数量
                            requested_quantity_val = row.get("应拨数量", actual_quantity)
                            if requested_quantity_val is None or (isinstance(requested_quantity_val, str) and requested_quantity_val.strip() == ""):
                                logger.warning(f"Row {idx+2}: 应拨数量 is empty, using actual quantity {actual_quantity}")
                                requested_quantity = float(actual_quantity)
                            else:
                                try:
                                    requested_quantity = float(requested_quantity_val)
                                except (ValueError, TypeError):
                                    logger.warning(f"Row {idx+2}: 应拨数量 '{requested_quantity_val}' is not a valid number, using actual quantity {actual_quantity}")
                                    requested_quantity = float(actual_quantity)

                            # 采购订单号
                            # 优先使用页面上输入的采购订单号，如果没有则尝试使用Excel中的值
                            excel_po_val = row.get("采购订单号", "")

                            if purchase_order_no and purchase_order_no.strip():
                                # 使用页面上输入的采购订单号
                                po_no = purchase_order_no
                                logger.info(f"Using purchase order number from form: {po_no}")
                            elif excel_po_val and str(excel_po_val).strip():
                                # 使用Excel中的采购订单号
                                po_no = str(excel_po_val).strip()
                                logger.info(f"Using purchase order number from Excel: {po_no}")
                            else:
                                # 使用默认值
                                po_no = "无采购订单号"
                                logger.warning(f"Row {idx+2}: No purchase order number provided, using default value '无采购订单号'")

                            # 打印字段类型信息
                            logger.info(f"Field types: material_code={type(material_code)}, actual_quantity={type(actual_quantity)}, outbound_price={type(outbound_price)}")

                            # 创建出库项
                            try:
                                item = OutboundItem(
                                    outbound_id=order.id,
                                    material_code=material_code,
                                    material_description=material_description,
                                    unit=unit,
                                    actual_quantity=actual_quantity,
                                    outbound_price=outbound_price,
                                    material_category_code=material_category_code,
                                    project_code=project_code,
                                    requested_quantity=requested_quantity,
                                    outbound_amount=outbound_amount,
                                    purchase_order_no=po_no,
                                    remark=""
                                )
                                logger.info(f"OutboundItem created: {item}")
                            except Exception as create_error:
                                logger.error(f"Error creating OutboundItem: {str(create_error)}")
                                logger.error(traceback.format_exc())
                                raise
                            db.add(item)

                            # 打印成功添加的项目
                            logger.info(f"Successfully added item: {material_code}, quantity: {actual_quantity}")
                        except Exception as item_error:
                            logger.error(f"Error adding item: {str(item_error)}")
                            logger.error(traceback.format_exc())
                            raise

                        # 累计总金额
                        total_amount += outbound_amount if outbound_amount else 0
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        error_details.append({
                            "rowIndex": idx + 2,
                            "errorMessage": str(e)
                        })

                # 更新订单总金额
                order.total_amount = total_amount
            except Exception as e:
                error_count += len(group)
                for idx, row in group.iterrows():
                    error_details.append({
                        "rowIndex": idx + 2,
                        "errorMessage": str(e)
                    })

        # 在提交事务前打印汇总信息
        logger.info(f"Import summary: total={total_count}, success={success_count}, error={error_count}")

        try:
            # 提交事务
            db.commit()
            logger.info("Database transaction committed successfully")
        except Exception as commit_error:
            logger.error(f"Error committing transaction: {str(commit_error)}")
            logger.error(traceback.format_exc())
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"提交数据库事务失败: {str(commit_error)}"
            )

        # 返回导入结果
        import_id = f"OUT{date.today().strftime('%Y%m%d')}{success_count:03d}"
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
    except Exception as e:
        db.rollback()
        logger.error(f"Import failed with exception: {str(e)}")
        logger.error(traceback.format_exc())

        # 检查是否是数据库错误
        if "psycopg2" in str(e) or "sqlalchemy" in str(e).lower():
            error_message = f"数据库错误: {str(e)}"
        else:
            error_message = f"导入失败: {str(e)}"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )
    finally:
        # 关闭数据库会话
        new_db.close()


@router.post("/complete/{id}", response_model=dict)
def complete_outbound(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    完成出库操作
    """
    # 查找出库单
    order = db.query(OutboundOrder).filter(OutboundOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"出库单 {id} 不存在"
        )

    # 检查状态
    if order.status != OutboundStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"出库单 {id} 不是待处理状态"
        )

    # 获取出库项
    items = db.query(OutboundItem).filter(OutboundItem.outbound_id == id).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"出库单 {id} 没有出库项"
        )

    # 处理每个出库项
    for item in items:
        # 查找库存
        inventory = db.query(Inventory).filter(Inventory.material_code == item.material_code).first()
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"物料 {item.material_code} 不存在库存记录"
            )

        # 检查库存是否足够
        if inventory.quantity < item.actual_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"物料 {item.material_code} 库存不足，当前库存: {inventory.quantity}"
            )

        # 更新库存
        inventory.quantity -= item.actual_quantity
        inventory.total_value = inventory.quantity * inventory.unit_price if inventory.unit_price else 0
        db.add(inventory)

        # 创建库存事务记录
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=InventoryTransactionType.OUTBOUND,
            quantity=item.actual_quantity,
            reference_no=order.material_voucher,
            reference_type="出库单",
            operator_id=current_user.id,
            remark=f"出库操作，物料凭证: {order.material_voucher}"
        )
        db.add(transaction)

    # 更新出库单状态
    order.status = OutboundStatus.COMPLETED
    db.add(order)

    # 提交事务
    db.commit()

    return {
        "success": True,
        "data": {
            "id": order.id,
            "material_voucher": order.material_voucher,
            "status": order.status,
            "message": "出库操作已完成"
        }
    }


@router.get("/list", response_model=dict)
def list_outbounds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    material_voucher: Optional[str] = None,
    material_code: Optional[str] = None,
    department: Optional[str] = None,
    user_unit: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Any:
    """
    获取出库单列表
    """
    # 构建基本查询
    query = db.query(OutboundOrder)

    # 应用过滤条件
    if material_voucher:
        # 确保物料凭证是字符串类型
        material_voucher_str = str(material_voucher)
        query = query.filter(OutboundOrder.material_voucher.ilike(f"%{material_voucher_str}%"))
    if department:
        query = query.filter(OutboundOrder.department.ilike(f"%{department}%"))
    if user_unit:
        query = query.filter(OutboundOrder.user_unit.ilike(f"%{user_unit}%"))

    # 处理状态参数
    if status:
        try:
            # 尝试将字符串转换为枚举值
            status_enum = OutboundStatus(status)
            query = query.filter(OutboundOrder.status == status_enum)
        except ValueError:
            # 如果转换失败，尝试模糊搜索状态名称
            # 将枚举值转换为字符串进行模糊匹配
            status_values = [s.value for s in OutboundStatus]
            matching_statuses = [s for s in status_values if status.upper() in s.upper()]
            if matching_statuses:
                query = query.filter(OutboundOrder.status.in_([OutboundStatus(s) for s in matching_statuses]))
            else:
                print(f"Invalid status value: {status}")

    # 处理日期参数
    if start_date:
        try:
            # 尝试将字符串转换为日期
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(OutboundOrder.voucher_date >= start_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid start_date format: {start_date}")

    if end_date:
        try:
            # 尝试将字符串转换为日期
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(OutboundOrder.voucher_date <= end_date_obj)
        except ValueError:
            # 如果转换失败，忽略该过滤条件
            print(f"Invalid end_date format: {end_date}")

    # 如果指定了物料编码，需要联合查询
    if material_code:
        query = query.join(OutboundItem).filter(
            OutboundItem.material_code.ilike(f"%{material_code}%")
        ).distinct()

    # 计算总数
    total = query.count()

    # 分页
    # 确保分页参数是有效的
    if page < 1:
        page = 1
    if size < 1:
        size = 20

    print(f"Pagination: page={page}, size={size}, total={total}")

    # 如果总数小于等于5，则返回所有记录，不进行分页
    # 这样可以确保在数据量少的情况下显示所有记录
    if total <= 5:
        print(f"Total count is <= 5 ({total}), returning all records without pagination")
        # 只排序，不分页
        query = query.order_by(OutboundOrder.create_time.desc())
    else:
        # 排序并应用分页
        print(f"Total count is > 5 ({total}), applying pagination: page={page}, size={size}")
        query = query.order_by(OutboundOrder.create_time.desc())
        query = query.offset((page - 1) * size).limit(size)

    # 获取结果
    orders = query.all()
    print(f"Retrieved {len(orders)} orders")

    # 构建响应数据
    records = []
    for order in orders:
        # 获取出库项
        items = db.query(OutboundItem).filter(OutboundItem.outbound_id == order.id).all()

        # 处理出库项中的特殊浮点数值
        for item in items:
            for column in item.__table__.columns:
                value = getattr(item, column.name)
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    if math.isnan(value):
                        setattr(item, column.name, 0.0)  # 将NaN替换为0
                    elif math.isinf(value):
                        # 将无穷大替换为非常大的数
                        setattr(item, column.name, float("1e100") if value > 0 else float("-1e100"))

        # 将出库项转换为字典
        items_data = []
        for item in items:
            item_dict = {
                "id": item.id,
                "material_code": item.material_code,
                "material_description": item.material_description,
                "unit": item.unit,
                "requested_quantity": item.requested_quantity,
                "actual_quantity": item.actual_quantity,
                "outbound_price": item.outbound_price,
                "outbound_amount": item.outbound_amount,
                "material_category_code": item.material_category_code,
                "project_code": item.project_code,
                "purchase_order_no": item.purchase_order_no,
                "remark": item.remark
            }
            items_data.append(item_dict)

        record = {
            "id": order.id,
            "material_voucher": order.material_voucher,
            "voucher_date": order.voucher_date,
            "department": order.department,
            "user_unit": order.user_unit,
            "document_type": order.document_type,
            "total_amount": order.total_amount,
            "status": order.status,
            "create_time": order.create_time,
            "material_category": order.material_category,  # 添加料单分属字段
            "operator": order.operator.full_name if order.operator else None,
            "items": items_data  # 添加出库项信息
        }
        records.append(record)
        print(f"Added record: {record['material_voucher']}")

    # 构建响应数据
    response_data = {
        "success": True,
        "data": {
            "total": total,
            "pages": (total + size - 1) // size if size > 0 else 1,
            "current": page,
            "records": records
        }
    }

    # 打印响应数据的摘要
    print(f"Response summary: success={response_data['success']}, total={response_data['data']['total']}, records_count={len(response_data['data']['records'])}")

    return response_data


@router.get("/audit/records", response_model=dict)
def list_audit_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    material_voucher: Optional[str] = Query(None),
    user_unit: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1),
    size: int = Query(100),
) -> Any:
    """
    获取已删除的出库单审计记录
    """
    # 构建查询
    query = db.query(DeletedOutboundRecord)

    # 应用过滤条件
    if material_voucher:
        query = query.filter(DeletedOutboundRecord.material_voucher.ilike(f"%{material_voucher}%"))
    if user_unit:
        query = query.filter(DeletedOutboundRecord.user_unit.ilike(f"%{user_unit}%"))
    if status:
        query = query.filter(DeletedOutboundRecord.status.ilike(f"%{status}%"))
    if start_date and start_date.strip():
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(DeletedOutboundRecord.voucher_date >= start_date_obj)
        except ValueError:
            print(f"Invalid start_date format: {start_date}")

    if end_date and end_date.strip():
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(DeletedOutboundRecord.voucher_date <= end_date_obj)
        except ValueError:
            print(f"Invalid end_date format: {end_date}")

    # 计算总数
    total = query.count()

    # 分页
    records = query.order_by(DeletedOutboundRecord.delete_time.desc()).\
        offset((page - 1) * size).limit(size).all()

    # 计算总页数
    pages = (total + size - 1) // size

    # 构建响应
    result = {
        "total": total,
        "pages": pages,
        "current": page,
        "records": [
            {
                "id": record.id,
                "original_id": record.original_id,
                "material_voucher": record.material_voucher,
                "voucher_date": record.voucher_date,
                "department": record.department,
                "user_unit": record.user_unit,
                "document_type": record.document_type,
                "total_amount": record.total_amount,
                "material_category": record.material_category,
                "status": record.status,
                "delete_time": record.delete_time,
                "delete_reason": record.delete_reason,
                "operator": record.operator.full_name if record.operator else None,
                "items_count": len(record.items_data) if record.items_data else 0
            } for record in records
        ]
    }

    return {"success": True, "data": result}


@router.get("/{id}", response_model=OutboundOrderSchema)
def get_outbound(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取出库单详情
    """
    try:
        logger.info(f"Getting outbound details for ID: {id}")

        # 打印请求信息
        logger.info(f"Request info - ID: {id}, User: {current_user.username if current_user else 'None'}")

        # 检查数据库连接
        try:
            db_info = db.execute(text("SELECT 1")).scalar()
            logger.info(f"Database connection check: {db_info}")
        except Exception as db_error:
            logger.error(f"Database connection error: {str(db_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"数据库连接错误: {str(db_error)}"
            )

        # 查询出库单
        try:
            order = db.query(OutboundOrder).filter(OutboundOrder.id == id).first()
            logger.info(f"Query result for ID {id}: {order is not None}")

            if not order:
                logger.warning(f"Outbound order with ID {id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"出库单 {id} 不存在"
                )

            # 打印出库单信息
            logger.info(f"Outbound order found: ID={order.id}, Voucher={order.material_voucher}, Status={order.status}")

            # 检查并处理特殊浮点数值
            for column in order.__table__.columns:
                value = getattr(order, column.name)
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    logger.warning(f"Found special float value in column {column.name}: {value}")
                    if math.isnan(value):
                        setattr(order, column.name, 0.0)  # 将NaN替换为0
                    elif math.isinf(value):
                        # 将无穷大替换为非常大的数
                        setattr(order, column.name, float("1e100") if value > 0 else float("-1e100"))
        except Exception as query_error:
            logger.error(f"Error querying outbound order: {str(query_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询出库单时发生错误: {str(query_error)}"
            )

        # 检查关联的出库项
        try:
            items = db.query(OutboundItem).filter(OutboundItem.outbound_id == id).all()
            logger.info(f"Found {len(items)} items for outbound ID {id}")

            # 打印出库项信息
            if items:
                for i, item in enumerate(items[:3]):  # 只打印前3个项目
                    logger.info(f"Item {i+1}: Code={item.material_code}, Desc={item.material_description[:20]}...")
                if len(items) > 3:
                    logger.info(f"... and {len(items) - 3} more items")

                # 处理出库项中的特殊浮点数值
                for item in items:
                    for column in item.__table__.columns:
                        value = getattr(item, column.name)
                        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                            logger.warning(f"Found special float value in item column {column.name}: {value}")
                            if math.isnan(value):
                                setattr(item, column.name, 0.0)  # 将NaN替换为0
                            elif math.isinf(value):
                                # 将无穷大替换为非常大的数
                                setattr(item, column.name, float("1e100") if value > 0 else float("-1e100"))
        except Exception as items_error:
            logger.error(f"Error querying outbound items: {str(items_error)}")
            logger.error(traceback.format_exc())
            # 不抛出异常，继续返回出库单

        return order
    except Exception as e:
        logger.error(f"Error getting outbound details for ID {id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取出库单详情时发生错误: {str(e)}"
        )


@router.get("/audit/records/{id}", response_model=dict)
def get_audit_record(
    id: int = Path(..., description="审计记录ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取审计记录详情
    """
    # 查找记录
    record = db.query(DeletedOutboundRecord).filter(DeletedOutboundRecord.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"审计记录 {id} 不存在"
        )

    # 构建响应
    result = {
        "id": record.id,
        "original_id": record.original_id,
        "material_voucher": record.material_voucher,
        "voucher_date": record.voucher_date,
        "department": record.department,
        "user_unit": record.user_unit,
        "document_type": record.document_type,
        "total_amount": record.total_amount,
        "material_category": record.material_category,
        "status": record.status,
        "delete_time": record.delete_time,
        "delete_reason": record.delete_reason,
        "operator": record.operator.full_name if record.operator else None,
        "items": record.items_data
    }

    return {"success": True, "data": result}


@router.delete("/{id}", response_model=dict)
def delete_outbound(
    id: int,
    reason: str = Query("", description="删除原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除出库单
    """
    try:
        logger.info(f"Deleting outbound with ID: {id}, reason: {reason}")

        # 查找出库单
        order = db.query(OutboundOrder).filter(OutboundOrder.id == id).first()
        if not order:
            logger.warning(f"Outbound order with ID {id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"出库单 {id} 不存在"
            )

        # 获取出库项
        items = db.query(OutboundItem).filter(OutboundItem.outbound_id == id).all()
        logger.info(f"Found {len(items)} items for outbound ID {id}")

        # 创建删除记录
        items_data = []
        for item in items:
            items_data.append({
                "material_code": item.material_code,
                "material_description": item.material_description,
                "unit": item.unit,
                "requested_quantity": item.requested_quantity,
                "actual_quantity": item.actual_quantity,
                "outbound_price": item.outbound_price,
                "outbound_amount": item.outbound_amount,
                "material_category_code": item.material_category_code,
                "project_code": item.project_code,
                "purchase_order_no": item.purchase_order_no,
                "remark": item.remark
            })

        # 创建删除记录
        deleted_record = DeletedOutboundRecord(
            original_id=order.id,
            material_voucher=order.material_voucher,
            voucher_date=order.voucher_date,
            department=order.department,
            user_unit=order.user_unit,
            document_type=order.document_type,
            total_amount=order.total_amount,
            material_category=order.material_category,
            status=order.status.value,
            delete_time=datetime.now(timezone.utc),
            delete_reason=reason,
            items_data=items_data,
            operator_id=current_user.id
        )
        db.add(deleted_record)

        # 删除出库项
        for item in items:
            db.delete(item)

        # 删除出库单
        db.delete(order)

        # 提交事务
        db.commit()

        return {
            "success": True,
            "data": {
                "id": id,
                "message": f"出库单 {id} 已成功删除"
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting outbound with ID {id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除出库单时发生错误: {str(e)}"
        )


@router.post("/batch-delete", response_model=dict)
def batch_delete_outbounds(
    request: BatchDeleteRequest,
    reason: str = Query("", description="删除原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    批量删除出库单
    """
    try:
        logger.info(f"Batch deleting outbounds with IDs: {request.ids}, reason: {reason}")

        if not request.ids:
            return {
                "success": True,
                "data": {
                    "message": "没有选择要删除的出库单"
                }
            }

        success_count = 0
        failed_ids = []

        for id in request.ids:
            try:
                # 查找出库单
                order = db.query(OutboundOrder).filter(OutboundOrder.id == id).first()
                if not order:
                    logger.warning(f"Outbound order with ID {id} not found")
                    failed_ids.append(id)
                    continue

                # 获取出库项
                items = db.query(OutboundItem).filter(OutboundItem.outbound_id == id).all()
                logger.info(f"Found {len(items)} items for outbound ID {id}")

                # 创建删除记录
                items_data = []
                for item in items:
                    items_data.append({
                        "material_code": item.material_code,
                        "material_description": item.material_description,
                        "unit": item.unit,
                        "requested_quantity": item.requested_quantity,
                        "actual_quantity": item.actual_quantity,
                        "outbound_price": item.outbound_price,
                        "outbound_amount": item.outbound_amount,
                        "material_category_code": item.material_category_code,
                        "project_code": item.project_code,
                        "purchase_order_no": item.purchase_order_no,
                        "remark": item.remark
                    })

                # 创建删除记录
                deleted_record = DeletedOutboundRecord(
                    original_id=order.id,
                    material_voucher=order.material_voucher,
                    voucher_date=order.voucher_date,
                    department=order.department,
                    user_unit=order.user_unit,
                    document_type=order.document_type,
                    total_amount=order.total_amount,
                    material_category=order.material_category,
                    status=order.status.value,
                    delete_time=datetime.now(timezone.utc),
                    delete_reason=reason,
                    items_data=items_data,
                    operator_id=current_user.id
                )
                db.add(deleted_record)

                # 删除出库项
                for item in items:
                    db.delete(item)

                # 删除出库单
                db.delete(order)

                success_count += 1

            except Exception as e:
                logger.error(f"Error deleting outbound with ID {id}: {str(e)}")
                failed_ids.append(id)

        # 提交事务
        db.commit()

        return {
            "success": True,
            "data": {
                "success_count": success_count,
                "failed_ids": failed_ids,
                "message": f"成功删除 {success_count} 个出库单" + (f", {len(failed_ids)} 个失败" if failed_ids else "")
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting outbounds: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除出库单时发生错误: {str(e)}"
        )
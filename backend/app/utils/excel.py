import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
import io


def validate_excel_columns(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    """
    验证Excel文件是否包含所需列
    
    Args:
        df: pandas DataFrame对象
        required_columns: 必需的列名列表
    
    Returns:
        缺失的列名列表
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns


def process_purchase_order_excel(file_content: bytes) -> pd.DataFrame:
    """
    处理采购订单Excel文件
    
    Args:
        file_content: Excel文件内容
    
    Returns:
        处理后的DataFrame
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        
        # 验证必要的列是否存在
        required_columns = ["采购订单号", "行项目号", "物料编码"]
        missing_columns = validate_excel_columns(df, required_columns)
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
            )
        
        # 数据清洗和转换
        # 1. 去除空行
        df = df.dropna(subset=["采购订单号", "物料编码"], how="all")
        
        # 2. 处理日期列
        if "订单生成日期" in df.columns:
            df["订单生成日期"] = pd.to_datetime(df["订单生成日期"], errors="coerce").dt.date
        
        # 3. 处理数值列
        numeric_columns = ["申请数量", "签约单价", "签约金额", "采购订单数"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
        return df
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"处理Excel文件失败: {str(e)}"
        )


def process_outbound_excel(file_content: bytes) -> pd.DataFrame:
    """
    处理出库Excel文件
    
    Args:
        file_content: Excel文件内容
    
    Returns:
        处理后的DataFrame
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        
        # 验证必要的列是否存在
        required_columns = ["物料凭证", "物料编码", "实拨数量", "具体用料部门"]
        missing_columns = validate_excel_columns(df, required_columns)
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
            )
        
        # 数据清洗和转换
        # 1. 去除空行
        df = df.dropna(subset=["物料凭证", "物料编码"], how="all")
        
        # 2. 处理日期列
        date_columns = ["开单日期", "发料日期"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        
        # 3. 处理数值列
        numeric_columns = ["实拨数量", "出库单价", "出库金额", "应拨数量", "合计金额", "销售金额", "管理费率"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
        return df
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"处理Excel文件失败: {str(e)}"
        )

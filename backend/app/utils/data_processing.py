"""
数据处理工具模块

根据 Python 版本使用不同的数据处理库：
- Python < 3.13: 使用 pandas
- Python >= 3.13: 使用 polars
"""

import sys
import os
from typing import List, Dict, Any, Union, Optional

# 根据 Python 版本选择数据处理库
if sys.version_info >= (3, 13):
    import polars as pl
    USE_POLARS = True
else:
    import pandas as pd
    USE_POLARS = False


def read_excel(file_path: str, sheet_name: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    读取 Excel 文件
    
    Args:
        file_path: Excel 文件路径
        sheet_name: 工作表名称，如果为 None，则读取所有工作表
        
    Returns:
        如果 sheet_name 为 None，返回包含所有工作表的字典
        否则返回指定工作表的数据
    """
    if USE_POLARS:
        if sheet_name is None:
            # 获取所有工作表名称
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = wb.sheetnames
            wb.close()
            
            # 读取所有工作表
            result = {}
            for name in sheet_names:
                result[name] = pl.read_excel(file_path, sheet_name=name)
            return result
        else:
            return pl.read_excel(file_path, sheet_name=sheet_name)
    else:
        return pd.read_excel(file_path, sheet_name=sheet_name)


def to_dict(data: Any) -> List[Dict[str, Any]]:
    """
    将数据转换为字典列表
    
    Args:
        data: pandas DataFrame 或 polars DataFrame
        
    Returns:
        字典列表
    """
    if USE_POLARS:
        return data.to_dicts()
    else:
        return data.to_dict(orient="records")


def filter_data(data: Any, condition: Dict[str, Any]) -> Any:
    """
    根据条件筛选数据
    
    Args:
        data: pandas DataFrame 或 polars DataFrame
        condition: 筛选条件，键为列名，值为筛选值
        
    Returns:
        筛选后的数据
    """
    if USE_POLARS:
        filtered_data = data
        for col, value in condition.items():
            filtered_data = filtered_data.filter(pl.col(col) == value)
        return filtered_data
    else:
        filtered_data = data
        for col, value in condition.items():
            filtered_data = filtered_data[filtered_data[col] == value]
        return filtered_data


def group_by(data: Any, columns: List[str], agg_dict: Dict[str, str]) -> Any:
    """
    分组聚合数据
    
    Args:
        data: pandas DataFrame 或 polars DataFrame
        columns: 分组列
        agg_dict: 聚合字典，键为列名，值为聚合函数
        
    Returns:
        聚合后的数据
    """
    if USE_POLARS:
        agg_exprs = []
        for col, agg_func in agg_dict.items():
            if agg_func == "sum":
                agg_exprs.append(pl.sum(col).alias(f"{col}_sum"))
            elif agg_func == "mean":
                agg_exprs.append(pl.mean(col).alias(f"{col}_mean"))
            elif agg_func == "count":
                agg_exprs.append(pl.count(col).alias(f"{col}_count"))
            elif agg_func == "min":
                agg_exprs.append(pl.min(col).alias(f"{col}_min"))
            elif agg_func == "max":
                agg_exprs.append(pl.max(col).alias(f"{col}_max"))
        
        return data.group_by(columns).agg(agg_exprs)
    else:
        return data.groupby(columns).agg(agg_dict).reset_index()


def merge_data(left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
    """
    合并数据
    
    Args:
        left: 左侧数据
        right: 右侧数据
        on: 连接列
        how: 连接方式，可选值为 "inner", "left", "right", "outer"
        
    Returns:
        合并后的数据
    """
    if USE_POLARS:
        return left.join(right, on=on, how=how)
    else:
        return pd.merge(left, right, on=on, how=how)


def to_excel(data: Any, file_path: str, sheet_name: str = "Sheet1") -> None:
    """
    将数据保存为 Excel 文件
    
    Args:
        data: pandas DataFrame 或 polars DataFrame
        file_path: 保存路径
        sheet_name: 工作表名称
    """
    if USE_POLARS:
        # polars 没有直接保存为 Excel 的方法，需要先转换为 pandas
        import pandas as pd
        pd_data = pd.DataFrame(data.to_dicts())
        pd_data.to_excel(file_path, sheet_name=sheet_name, index=False)
    else:
        data.to_excel(file_path, sheet_name=sheet_name, index=False)

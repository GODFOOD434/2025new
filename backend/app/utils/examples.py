"""
数据处理示例
"""

from app.utils.data_processing import (
    read_excel,
    to_dict,
    filter_data,
    group_by,
    merge_data,
    to_excel,
    USE_POLARS
)


def process_purchase_orders_example(file_path: str):
    """
    处理采购订单示例
    
    Args:
        file_path: Excel 文件路径
    """
    # 读取 Excel 文件
    data = read_excel(file_path, sheet_name="采购订单")
    
    # 转换为字典列表
    records = to_dict(data)
    print(f"读取到 {len(records)} 条采购订单记录")
    
    # 筛选数据
    filtered_data = filter_data(data, {"供应商": "供应商A"})
    filtered_records = to_dict(filtered_data)
    print(f"供应商A的订单有 {len(filtered_records)} 条")
    
    # 分组聚合
    if USE_POLARS:
        # polars 版本
        import polars as pl
        grouped_data = data.group_by("供应商").agg([
            pl.sum("金额").alias("总金额"),
            pl.count("订单号").alias("订单数量")
        ])
    else:
        # pandas 版本
        grouped_data = group_by(
            data,
            ["供应商"],
            {"金额": "sum", "订单号": "count"}
        )
    
    grouped_records = to_dict(grouped_data)
    print("按供应商分组统计结果:")
    for record in grouped_records:
        print(record)
    
    # 保存结果
    to_excel(grouped_data, "供应商统计.xlsx", "供应商统计")
    print("结果已保存到 供应商统计.xlsx")


if __name__ == "__main__":
    # 示例用法
    print(f"使用 {'Polars' if USE_POLARS else 'Pandas'} 进行数据处理")
    
    # 这里需要一个实际的 Excel 文件路径
    # process_purchase_orders_example("采购订单.xlsx")

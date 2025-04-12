"""
创建一个最小的测试 Excel 文件，用于测试出库单导入功能
"""
import pandas as pd
import os

# 创建一个简单的 DataFrame，只包含必要的列
data = {
    "物料凭证": ["TEST001"],
    "开单日期": ["2023-01-01"],
    "物料编码": ["M001"],
    "物资名称及规格型号": ["测试物料"],
    "计量单位": ["个"],
    "实拨数量": [10],
    "出库单价": [10.0],
    "出库金额": [100.0],
    "具体用料部门": ["测试部门"]
}

df = pd.DataFrame(data)

# 保存为 Excel 文件
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minimal_test.xlsx")
df.to_excel(output_path, index=False)

print(f"最小测试文件已创建: {output_path}")

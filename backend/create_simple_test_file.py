"""
创建一个简单的测试 Excel 文件，用于测试出库单导入功能
"""
import pandas as pd
import os

# 创建一个简单的 DataFrame，只包含必要的列
data = {
    "物料凭证": ["MV001", "MV001"],
    "物料编码": ["M001", "M002"],
    "实拨数量": [10, 20],
    "具体用料部门": ["生产部", "生产部"]
}

df = pd.DataFrame(data)

# 保存为 Excel 文件
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple_test.xlsx")
df.to_excel(output_path, index=False)

print(f"简单测试文件已创建: {output_path}")

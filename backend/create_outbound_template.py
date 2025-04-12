import pandas as pd
import os

# 设置表头 - 按照用户指定的格式
headers = ["物料凭证", "开单日期", "物料编码", "物资名称及规格型号", "计量单位", "实拨数量", "出库单价", 
           "具体用料部门", "料单分属", "物资品种码", "工程编码", "应拨数量", "出库金额", "用料单位", 
           "单据类型", "合计金额", "发料日期", "销售金额", "转储订单/销售订单", "管理费率"]

# 创建数据
data = [
    # 第一行数据
    ["MV20240501001", "2024-05-01", "M001", "钢板 10mm", "kg", 100, 10.5, 
     "生产部", "生产", "A001", "P001", 100, 1050, "生产一组", 
     "正常出库", 1050, "2024-05-02", 1102.5, "TO001", 0.05],
    
    # 第二行数据（同一物料凭证下的另一个物料）
    ["MV20240501001", "2024-05-01", "M002", "螺丝 M8", "个", 200, 0.5, 
     "生产部", "生产", "B001", "P001", 200, 100, "生产一组", 
     "正常出库", 100, "2024-05-02", 105, "TO001", 0.05]
]

# 创建DataFrame
df = pd.DataFrame(data, columns=headers)

# 保存为Excel文件
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outbound_template_custom.xlsx")
df.to_excel(output_path, index=False)

print(f"Excel模板文件已创建: {output_path}")

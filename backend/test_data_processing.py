"""
测试数据处理模块
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.data_processing import USE_POLARS

def main():
    """
    测试数据处理模块
    """
    print(f"Python 版本: {sys.version}")
    print(f"使用 Polars: {USE_POLARS}")
    
    if USE_POLARS:
        print("成功导入 polars 库")
        import polars as pl
        # 创建一个简单的 DataFrame
        df = pl.DataFrame({
            "A": [1, 2, 3, 4, 5],
            "B": ["a", "b", "c", "d", "e"]
        })
        print("\nPolars DataFrame:")
        print(df)
    else:
        print("成功导入 pandas 库")
        import pandas as pd
        # 创建一个简单的 DataFrame
        df = pd.DataFrame({
            "A": [1, 2, 3, 4, 5],
            "B": ["a", "b", "c", "d", "e"]
        })
        print("\nPandas DataFrame:")
        print(df)
    
    print("\n测试成功!")

if __name__ == "__main__":
    main()

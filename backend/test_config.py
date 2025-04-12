"""
测试配置模块
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    测试配置模块
    """
    print(f"Python 版本: {sys.version}")
    
    try:
        from app.core.config import settings
        print("成功导入配置模块")
        print(f"项目名称: {settings.PROJECT_NAME}")
        print(f"数据库 URI: {settings.SQLALCHEMY_DATABASE_URI}")
        print(f"API 前缀: {settings.API_V1_STR}")
        print("\n测试成功!")
    except Exception as e:
        print(f"导入配置模块失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

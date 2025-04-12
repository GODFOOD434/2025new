"""
测试出库单导入功能
"""
import os
import sys
import logging
import traceback
from fastapi import UploadFile
from tempfile import NamedTemporaryFile
from sqlalchemy.orm import Session

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test_outbound_import")

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用模块
from app.db.session import SessionLocal
from app.models.user import User
from app.api.api_v1.endpoints.outbounds import import_outbound_excel

async def test_import():
    """测试导入功能"""
    try:
        # 创建数据库会话
        db = SessionLocal()

        # 获取一个管理员用户
        admin_user = db.query(User).filter(User.is_superuser == True).first()
        if not admin_user:
            logger.error("No admin user found in database")
            return

        # 测试文件路径
        test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outbound_template_custom.xlsx")
        if not os.path.exists(test_file_path):
            test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outbound_template_custom.xlsx")

        if not os.path.exists(test_file_path):
            logger.error(f"Test file not found: {test_file_path}")
            return

        logger.info(f"Using test file: {test_file_path}")

        # 创建临时文件对象
        with open(test_file_path, "rb") as f:
            content = f.read()

        # 创建 UploadFile 对象
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(content)
        temp_file.close()

        # 创建 UploadFile 对象
        file_obj = open(temp_file.name, "rb")
        upload_file = UploadFile(filename="outbound_template_custom.xlsx")
        upload_file.file = file_obj
        upload_file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # 调用导入函数
        try:
            result = await import_outbound_excel(db=db, current_user=admin_user, file=upload_file)
            logger.info(f"Import result: {result}")
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            # 关闭文件
            upload_file.file.close()
            os.unlink(temp_file.name)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # 关闭数据库会话
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_import())

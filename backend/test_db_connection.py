"""
测试数据库连接和模型
"""
import os
import sys
import logging
from datetime import date

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_db_connection")

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用模块
from app.db.session import SessionLocal
from app.models.outbound import OutboundOrder, OutboundStatus, OutboundItem
from app.models.user import User

def test_db_connection():
    """测试数据库连接"""
    try:
        # 创建数据库会话
        db = SessionLocal()

        # 测试连接
        from sqlalchemy import text
        result = db.execute(text("SELECT version()")).scalar()
        logger.info(f"Database connection successful. Version: {result}")

        # 获取一个管理员用户
        admin_user = db.query(User).filter(User.is_superuser == True).first()
        if not admin_user:
            logger.error("No admin user found in database")
            return

        logger.info(f"Found admin user: {admin_user.username}")

        # 测试创建出库单
        try:
            # 创建一个测试出库单
            test_order = OutboundOrder(
                material_voucher="TEST123456",
                voucher_date=date.today(),
                department="测试部门",
                user_unit="测试单位",
                document_type="测试类型",
                total_amount=100.0,
                status=OutboundStatus.PENDING,
                operator_id=admin_user.id
            )

            # 添加到会话
            db.add(test_order)
            db.flush()

            logger.info(f"Created test order with ID: {test_order.id}")

            # 创建一个测试出库项
            test_item = OutboundItem(
                outbound_id=test_order.id,
                material_code="M001",
                material_description="测试物料",
                unit="个",
                actual_quantity=10.0,
                outbound_price=10.0,
                outbound_amount=100.0,
                purchase_order_no="PO001"
            )

            # 添加到会话
            db.add(test_item)

            # 提交事务
            db.commit()
            logger.info("Test order and item created successfully")

            # 查询刚刚创建的出库单
            created_order = db.query(OutboundOrder).filter(OutboundOrder.material_voucher == "TEST123456").first()
            if created_order:
                logger.info(f"Retrieved test order: {created_order.material_voucher}")

                # 删除测试数据
                db.delete(created_order)
                db.commit()
                logger.info("Test data cleaned up")
            else:
                logger.error("Failed to retrieve test order")

        except Exception as e:
            db.rollback()
            logger.error(f"Error testing models: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # 关闭数据库会话
        db.close()

if __name__ == "__main__":
    test_db_connection()

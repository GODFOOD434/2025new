"""
创建测试出库单数据
"""
import os
import sys
import logging
from datetime import date, datetime, timedelta
import random

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_test_outbounds")

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用模块
from app.db.session import SessionLocal
from app.models.user import User
from app.models.outbound import OutboundOrder, OutboundItem, OutboundStatus

def create_test_data():
    """创建测试数据"""
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 获取一个管理员用户
        admin_user = db.query(User).filter(User.is_superuser == True).first()
        if not admin_user:
            logger.error("No admin user found in database")
            return
        
        logger.info(f"Found admin user: {admin_user.username}")
        
        # 创建10个测试出库单
        for i in range(1, 11):
            # 创建出库单
            voucher_date = date.today() - timedelta(days=i)
            material_voucher = f"TEST{date.today().strftime('%Y%m%d')}{i:03d}"
            
            # 检查是否已存在
            existing = db.query(OutboundOrder).filter(OutboundOrder.material_voucher == material_voucher).first()
            if existing:
                logger.info(f"Outbound order {material_voucher} already exists, skipping")
                continue
            
            # 随机选择状态
            status_choices = [OutboundStatus.PENDING, OutboundStatus.COMPLETED]
            status = random.choice(status_choices)
            
            # 创建出库单
            order = OutboundOrder(
                material_voucher=material_voucher,
                voucher_date=voucher_date,
                department=f"测试部门{i}",
                user_unit=f"测试单位{i}",
                document_type="正常出库",
                total_amount=i * 1000.0,
                status=status,
                material_category="测试分类",
                operator_id=admin_user.id
            )
            
            db.add(order)
            db.flush()
            
            logger.info(f"Created test order: {material_voucher}")
            
            # 为每个出库单创建2个出库项
            for j in range(1, 3):
                item = OutboundItem(
                    outbound_id=order.id,
                    material_code=f"M{i:03d}{j:02d}",
                    material_description=f"测试物料{i}-{j}",
                    unit="个",
                    actual_quantity=j * 10.0,
                    outbound_price=j * 50.0,
                    outbound_amount=j * 10.0 * j * 50.0,
                    material_category_code="TEST",
                    project_code="",
                    requested_quantity=j * 10.0,
                    purchase_order_no=f"PO{i:03d}{j:02d}",
                    remark=""
                )
                db.add(item)
            
            logger.info(f"Created 2 items for order: {material_voucher}")
        
        # 提交事务
        db.commit()
        logger.info("Test data created successfully")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating test data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # 关闭数据库会话
        db.close()

if __name__ == "__main__":
    create_test_data()

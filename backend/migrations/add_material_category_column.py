"""
数据库迁移脚本：添加 material_category 列到 wh_outboundorder 表
"""
import os
import sys
import logging

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入应用模块
from app.db.session import engine
from sqlalchemy import text

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_migration")

def run_migration():
    """执行迁移"""
    try:
        # 创建连接
        with engine.connect() as connection:
            # 开始事务
            with connection.begin():
                # 检查列是否已存在
                check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'wh_outboundorder' 
                AND column_name = 'material_category'
                """)
                
                result = connection.execute(check_query)
                if result.fetchone():
                    logger.info("列 'material_category' 已存在，无需迁移")
                    return
                
                # 添加列
                logger.info("添加 'material_category' 列到 wh_outboundorder 表")
                add_column_query = text("""
                ALTER TABLE wh_outboundorder 
                ADD COLUMN material_category VARCHAR(100)
                """)
                
                connection.execute(add_column_query)
                logger.info("迁移成功完成")
    
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()

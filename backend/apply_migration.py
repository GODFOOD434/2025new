import os
import sys

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接使用 SQL 脚本创建表
print("正在创建审计记录表...")

# 获取数据库连接
from app.db.session import engine

# 检测数据库类型
from app.core.config import settings
db_url = settings.SQLALCHEMY_DATABASE_URI.lower()

# 根据数据库类型选择不同的 SQL
if 'sqlite' in db_url:
    # SQLite 版本
    sql = """
    CREATE TABLE IF NOT EXISTS wh_deletedoutboundrecord (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_id INTEGER,
        material_voucher VARCHAR(32) NOT NULL,
        voucher_date DATE NOT NULL,
        department VARCHAR(100) NOT NULL,
        user_unit VARCHAR(100) NOT NULL,
        document_type VARCHAR(20),
        total_amount FLOAT,
        material_category VARCHAR(100),
        status VARCHAR(20),
        delete_time TIMESTAMP,
        delete_reason VARCHAR(255),
        items_data TEXT,
        operator_id INTEGER REFERENCES wh_user(id),
        create_time TIMESTAMP,
        update_time TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS ix_wh_deletedoutboundrecord_material_voucher ON wh_deletedoutboundrecord (material_voucher);
    """
else:
    # PostgreSQL 版本
    sql = """
    CREATE TABLE IF NOT EXISTS wh_deletedoutboundrecord (
        id SERIAL PRIMARY KEY,
        original_id INTEGER,
        material_voucher VARCHAR(32) NOT NULL,
        voucher_date DATE NOT NULL,
        department VARCHAR(100) NOT NULL,
        user_unit VARCHAR(100) NOT NULL,
        document_type VARCHAR(20),
        total_amount FLOAT,
        material_category VARCHAR(100),
        status VARCHAR(20),
        delete_time TIMESTAMP,
        delete_reason VARCHAR(255),
        items_data JSONB,
        operator_id INTEGER REFERENCES wh_user(id),
        create_time TIMESTAMP,
        update_time TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS ix_wh_deletedoutboundrecord_material_voucher ON wh_deletedoutboundrecord (material_voucher);
    """

try:
    # 执行 SQL
    with engine.connect() as connection:
        # 对于 SQLAlchemy 2.0
        from sqlalchemy import text
        connection.execute(text(sql))
        connection.commit()
    print("审计记录表创建成功！")
except Exception as e:
    print(f"创建表失败: {e}")

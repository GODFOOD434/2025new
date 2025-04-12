"""Add PDA tables

Revision ID: 20250413_add_pda_tables
Revises: None
Create Date: 2025-04-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250413_add_pda_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 添加出库单状态枚举值
    # 使用更安全的方式添加枚举值
    try:
        op.execute("ALTER TYPE outboundstatus ADD VALUE 'PDA_ASSIGNED'")
    except Exception as e:
        print(f"Warning: Could not add PDA_ASSIGNED to outboundstatus: {e}")

    try:
        op.execute("ALTER TYPE outboundstatus ADD VALUE 'PDA_PROCESSING'")
    except Exception as e:
        print(f"Warning: Could not add PDA_PROCESSING to outboundstatus: {e}")

    try:
        op.execute("ALTER TYPE outboundstatus ADD VALUE 'PDA_COMPLETED'")
    except Exception as e:
        print(f"Warning: Could not add PDA_COMPLETED to outboundstatus: {e}")

    # 添加PDA相关字段到出库单表
    op.add_column('wh_outboundorder', sa.Column('pda_assigned', sa.Integer(), nullable=True, default=0))
    op.add_column('wh_outboundorder', sa.Column('pda_assigned_time', sa.DateTime(), nullable=True))
    op.add_column('wh_outboundorder', sa.Column('pda_complete_time', sa.DateTime(), nullable=True))

    # 创建PDA操作状态枚举类型
    op.execute("CREATE TYPE pdaoperationstatus AS ENUM ('ASSIGNED', 'PROCESSING', 'COMPLETED', 'CANCELLED', 'FAILED')")

    # 创建PDA操作表
    op.create_table('wh_outboundpdaoperation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('outbound_id', sa.Integer(), nullable=False),
        sa.Column('pda_device_id', sa.String(100), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ASSIGNED', 'PROCESSING', 'COMPLETED', 'CANCELLED', 'FAILED', name='pdaoperationstatus'), nullable=True),
        sa.Column('assigned_time', sa.DateTime(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('complete_time', sa.DateTime(), nullable=True),
        sa.Column('sync_time', sa.DateTime(), nullable=True),
        sa.Column('location_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('operation_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['outbound_id'], ['wh_outboundorder.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['wh_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wh_outboundpdaoperation_id'), 'wh_outboundpdaoperation', ['id'], unique=False)

    # 创建PDA操作项表
    op.create_table('wh_outboundpdaitem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pda_operation_id', sa.Integer(), nullable=False),
        sa.Column('outbound_item_id', sa.Integer(), nullable=False),
        sa.Column('material_code', sa.String(32), nullable=False),
        sa.Column('actual_quantity', sa.Float(), nullable=False),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('scan_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pda_operation_id'], ['wh_outboundpdaoperation.id'], ),
        sa.ForeignKeyConstraint(['outbound_item_id'], ['wh_outbounditem.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wh_outboundpdaitem_id'), 'wh_outboundpdaitem', ['id'], unique=False)
    op.create_index(op.f('ix_wh_outboundpdaitem_material_code'), 'wh_outboundpdaitem', ['material_code'], unique=False)


def downgrade():
    # 删除PDA操作项表
    op.drop_index(op.f('ix_wh_outboundpdaitem_material_code'), table_name='wh_outboundpdaitem')
    op.drop_index(op.f('ix_wh_outboundpdaitem_id'), table_name='wh_outboundpdaitem')
    op.drop_table('wh_outboundpdaitem')

    # 删除PDA操作表
    op.drop_index(op.f('ix_wh_outboundpdaoperation_id'), table_name='wh_outboundpdaoperation')
    op.drop_table('wh_outboundpdaoperation')

    # 删除PDA操作状态枚举类型
    op.execute("DROP TYPE pdaoperationstatus")

    # 删除出库单表中的PDA相关字段
    op.drop_column('wh_outboundorder', 'pda_complete_time')
    op.drop_column('wh_outboundorder', 'pda_assigned_time')
    op.drop_column('wh_outboundorder', 'pda_assigned')

    # 注意：无法从枚举类型中删除值，所以这里不需要操作

"""Add deleted outbound record model

Revision ID: add_deleted_outbound_record
Revises:
Create Date: 2025-04-12 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import json
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableDict

# revision identifiers, used by Alembic.
revision = 'add_deleted_outbound_record'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建已删除出库单审计记录表
    op.create_table(
        'wh_deletedoutboundrecord',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_id', sa.Integer(), nullable=True),
        sa.Column('material_voucher', sa.String(length=32), nullable=False),
        sa.Column('voucher_date', sa.Date(), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('user_unit', sa.String(length=100), nullable=False),
        sa.Column('document_type', sa.String(length=20), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('material_category', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('delete_time', sa.DateTime(), nullable=True),
        sa.Column('delete_reason', sa.String(length=255), nullable=True),
        sa.Column('items_data', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['wh_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wh_deletedoutboundrecord_material_voucher'), 'wh_deletedoutboundrecord', ['material_voucher'], unique=False)


def downgrade():
    # 删除已删除出库单审计记录表
    op.drop_index(op.f('ix_wh_deletedoutboundrecord_material_voucher'), table_name='wh_deletedoutboundrecord')
    op.drop_table('wh_deletedoutboundrecord')

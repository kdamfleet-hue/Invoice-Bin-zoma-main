"""Add Yard and CustodyItem

Revision ID: b089400cc9e6
Revises: b7f3db79753a
Create Date: 2026-07-21 23:43:58.431004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b089400cc9e6'
down_revision = 'b7f3db79753a'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    
    if dialect == 'postgresql':
        op.execute("ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS yard_status VARCHAR(50) DEFAULT 'خارج الساحة';")
        op.execute("ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS yard_condition VARCHAR(50);")
    else:
        try:
            with op.batch_alter_table('erp_vehicles', schema=None) as batch_op:
                batch_op.add_column(sa.Column('yard_status', sa.String(length=50), nullable=True))
                batch_op.add_column(sa.Column('yard_condition', sa.String(length=50), nullable=True))
        except Exception:
            pass


def downgrade():
    try:
        with op.batch_alter_table('erp_vehicles', schema=None) as batch_op:
            batch_op.drop_column('yard_condition')
            batch_op.drop_column('yard_status')
    except Exception:
        pass

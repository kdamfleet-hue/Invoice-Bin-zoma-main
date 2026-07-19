"""Add branch_id to models

Revision ID: 294abbd5fdc1
Revises: 0f5d2a6ffc52
Create Date: 2026-07-19 12:56:18.428657

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '294abbd5fdc1'
down_revision = '0f5d2a6ffc52'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    
    tables_with_fk = [
        'erp_users', 'erp_drivers', 'erp_vehicles', 'erp_documents', 
        'erp_spare_parts', 'erp_maintenance_requests', 'erp_suppliers', 
        'erp_oil_changes', 'erp_audit_logs', 'erp_purchase_orders', 
        'erp_branch_accounts'
    ]
    
    if dialect == 'postgresql':
        for t in tables_with_fk:
            op.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES erp_branches(id);")
        op.execute("ALTER TABLE erp_settings ADD COLUMN IF NOT EXISTS branch_id INTEGER;")
    else:
        for t in tables_with_fk:
            try:
                with op.batch_alter_table(t, schema=None) as batch_op:
                    batch_op.add_column(sa.Column('branch_id', sa.Integer(), sa.ForeignKey('erp_branches.id'), nullable=True))
            except Exception:
                pass
        try:
            with op.batch_alter_table('erp_settings', schema=None) as batch_op:
                batch_op.add_column(sa.Column('branch_id', sa.Integer(), nullable=True))
        except Exception:
            pass


def downgrade():
    pass

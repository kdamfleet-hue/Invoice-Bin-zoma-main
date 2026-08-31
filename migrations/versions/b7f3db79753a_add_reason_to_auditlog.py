"""Add reason to AuditLog

Revision ID: b7f3db79753a
Revises: 294abbd5fdc1
Create Date: 2026-07-21 23:43:15.838853

"""
from alembic import op
import sqlalchemy as sa


revision = 'b7f3db79753a'
down_revision = '294abbd5fdc1'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns("erp_audit_logs")]
    if "reason" in cols:
        return
    with op.batch_alter_table("erp_audit_logs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reason", sa.Text(), nullable=True))


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns("erp_audit_logs")]
    if "reason" not in cols:
        return
    with op.batch_alter_table("erp_audit_logs", schema=None) as batch_op:
        batch_op.drop_column("reason")

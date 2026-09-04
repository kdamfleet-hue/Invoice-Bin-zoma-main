"""add email to erp_users

Revision ID: 9a2f6c1d4e11
Revises: 7c4e1a9b2d10
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa

revision = "9a2f6c1d4e11"
down_revision = "7c4e1a9b2d10"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.drop_column("email")

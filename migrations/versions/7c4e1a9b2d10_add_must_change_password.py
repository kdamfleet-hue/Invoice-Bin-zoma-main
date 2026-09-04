"""add must_change_password to erp_users

Revision ID: 7c4e1a9b2d10
Revises: 0f5d2a6ffc52
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa

revision = "7c4e1a9b2d10"
down_revision = "0f5d2a6ffc52"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "must_change_password",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            )
        )


def downgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.drop_column("must_change_password")

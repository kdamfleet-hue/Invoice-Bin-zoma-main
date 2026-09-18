"""add login OTP records

Revision ID: 7a8b9c0d1e2f
Revises: f2a1b3c4d5e6
"""
from alembic import op
import sqlalchemy as sa

revision = "7a8b9c0d1e2f"
down_revision = "f2a1b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "erp_login_otps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("erp_users.id"), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=30), nullable=False, server_default="login"),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_erp_login_otps_user_purpose",
        "erp_login_otps",
        ["user_id", "purpose", "created_at"],
    )


def downgrade():
    op.drop_index("ix_erp_login_otps_user_purpose", table_name="erp_login_otps")
    op.drop_table("erp_login_otps")

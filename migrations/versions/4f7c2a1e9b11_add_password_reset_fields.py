"""add password reset fields to erp_users

Revision ID: 4f7c2a1e9b11
Revises: c1d4e8f7a902
Create Date: 2026-09-05
"""
from alembic import op
import sqlalchemy as sa

revision = "4f7c2a1e9b11"
down_revision = "c1d4e8f7a902"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("erp_users")}
    unique_names = {constraint.get("name") for constraint in inspector.get_unique_constraints("erp_users")}
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        if "password_reset_token_hash" not in columns:
            batch_op.add_column(sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True))
        if "password_reset_expires_at" not in columns:
            batch_op.add_column(sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True))
        if "uq_erp_users_password_reset_token_hash" not in unique_names:
            batch_op.create_unique_constraint("uq_erp_users_password_reset_token_hash", ["password_reset_token_hash"])


def downgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_erp_users_password_reset_token_hash", type_="unique")
        batch_op.drop_column("password_reset_expires_at")
        batch_op.drop_column("password_reset_token_hash")

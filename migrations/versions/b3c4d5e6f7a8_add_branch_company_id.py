"""add company_id to erp_branches (one isolated branch per SaaS company)

Revision ID: b3c4d5e6f7a8
Revises: 7a8b9c0d1e2f
"""
from alembic import op
import sqlalchemy as sa

revision = "b3c4d5e6f7a8"
down_revision = "7a8b9c0d1e2f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("erp_branches") as batch_op:
        batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_erp_branches_company_id", "erp_companies", ["company_id"], ["id"]
        )
    op.create_index(
        "ix_erp_branches_company_id", "erp_branches", ["company_id"]
    )


def downgrade():
    op.drop_index("ix_erp_branches_company_id", table_name="erp_branches")
    with op.batch_alter_table("erp_branches") as batch_op:
        batch_op.drop_constraint("fk_erp_branches_company_id", type_="foreignkey")
        batch_op.drop_column("company_id")

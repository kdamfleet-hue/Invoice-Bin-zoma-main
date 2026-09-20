"""add phone to erp_users

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-20

Idempotent migration for production and fresh databases. models/schema.py
User.phone has been used for a while by the SaaS company lookup
(routes/saas.py company_login()) and the mobile-number/OTP login paths
(routes/auth.py), but unlike every sibling column added around the same
time (email: 9a2f6c1d4e11, must_change_password: 7c4e1a9b2d10, company_id:
a91c3e7b5d02), no migration ever added it. app.py ensure_db_columns() also
attempts this at every startup as a best-effort fallback, but that
mechanism wraps its entire body (multiple tables) in one try/except and
runs all statements in a single transaction, so one failing statement
anywhere before erp_users aborts every statement after it on Postgres --
and it evidently has, leaving real production databases still missing
this column and failing every User.query lookup (all login paths) with
psycopg2.errors.UndefinedColumn.
"""
from alembic import op
import sqlalchemy as sa

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("erp_users")}
    if "phone" not in cols:
        with op.batch_alter_table("erp_users", schema=None) as batch_op:
            batch_op.add_column(sa.Column("phone", sa.String(length=30), nullable=True))


def downgrade():
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        batch_op.drop_column("phone")

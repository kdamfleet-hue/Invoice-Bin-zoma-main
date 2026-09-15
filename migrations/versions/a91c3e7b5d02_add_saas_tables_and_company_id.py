"""add SaaS tables and erp_users.company_id

Revision ID: a91c3e7b5d02
Revises: 4f7c2a1e9b11
Create Date: 2026-09-15

Idempotent official migration for production and fresh databases.
Covers:
- erp_companies
- erp_subscription_plans
- erp_subscriptions
- erp_payments
- erp_users.company_id + FK + index
- remaining User columns used by models/schema.py if missing
"""
from alembic import op
import sqlalchemy as sa

revision = "a91c3e7b5d02"
down_revision = "4f7c2a1e9b11"
branch_labels = None
depends_on = None

FK_USERS_COMPANY = "fk_erp_users_company_id"
IX_USERS_COMPANY = "ix_erp_users_company_id"
UQ_COMPANY_EMAIL = "uq_erp_companies_email"
UQ_PLAN_NAME = "uq_erp_subscription_plans_name"
IX_USERS_ACTIVE_ROLE = "ix_erp_users_active_role"

def _tables(inspector):
    return set(inspector.get_table_names())

def _columns(inspector, table):
    if table not in _tables(inspector):
        return set()
    return {col["name"] for col in inspector.get_columns(table)}

def _fk_names(inspector, table):
    if table not in _tables(inspector):
        return set()
    names = set()
    for fk in inspector.get_foreign_keys(table):
        if fk.get("name"):
            names.add(fk["name"])
        referred = fk.get("referred_table")
        constrained = tuple(fk.get("constrained_columns") or ())
        names.add((referred, constrained))
    return names

def _index_names(inspector, table):
    if table not in _tables(inspector):
        return set()
    return {idx.get("name") for idx in inspector.get_indexes(table) if idx.get("name")}

def _unique_names(inspector, table):
    if table not in _tables(inspector):
        return set()
    return {c.get("name") for c in inspector.get_unique_constraints(table) if c.get("name")}

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = _tables(inspector)
    if "erp_companies" not in tables:
        op.create_table("erp_companies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(length=180), nullable=False), sa.Column("owner_name", sa.String(length=150), nullable=False), sa.Column("phone", sa.String(length=30), nullable=False), sa.Column("email", sa.String(length=255), nullable=False), sa.Column("status", sa.String(length=30), nullable=False, server_default="trial"), sa.Column("trial_started_at", sa.DateTime(), nullable=False), sa.Column("trial_ends_at", sa.DateTime(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.UniqueConstraint("email", name=UQ_COMPANY_EMAIL))
    else:
        inspector = sa.inspect(bind)
        uniques = _unique_names(inspector, "erp_companies")
        cols = _columns(inspector, "erp_companies")
        if "email" in cols and UQ_COMPANY_EMAIL not in uniques:
            existing_email_unique = any(c.get("column_names") == ["email"] for c in inspector.get_unique_constraints("erp_companies"))
            if not existing_email_unique:
                op.create_unique_constraint(UQ_COMPANY_EMAIL, "erp_companies", ["email"])
    inspector = sa.inspect(bind); tables = _tables(inspector)
    if "erp_subscription_plans" not in tables:
        op.create_table("erp_subscription_plans", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("monthly_price", sa.Numeric(10, 2), nullable=False, server_default="99"), sa.Column("annual_price", sa.Numeric(10, 2), nullable=False, server_default="990"), sa.Column("description", sa.Text(), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")), sa.UniqueConstraint("name", name=UQ_PLAN_NAME))
    inspector = sa.inspect(bind); tables = _tables(inspector)
    if "erp_subscriptions" not in tables:
        op.create_table("erp_subscriptions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("company_id", sa.Integer(), nullable=False), sa.Column("plan_id", sa.Integer(), nullable=False), sa.Column("status", sa.String(length=30), nullable=False, server_default="trial"), sa.Column("billing_cycle", sa.String(length=20), nullable=False, server_default="monthly"), sa.Column("started_at", sa.DateTime(), nullable=False), sa.Column("current_period_end", sa.DateTime(), nullable=False), sa.Column("provider", sa.String(length=50), nullable=True), sa.Column("provider_reference", sa.String(length=180), nullable=True), sa.ForeignKeyConstraint(["company_id"], ["erp_companies.id"], name="fk_erp_subscriptions_company_id"), sa.ForeignKeyConstraint(["plan_id"], ["erp_subscription_plans.id"], name="fk_erp_subscriptions_plan_id"))
    inspector = sa.inspect(bind); tables = _tables(inspector)
    if "erp_payments" not in tables:
        op.create_table("erp_payments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("company_id", sa.Integer(), nullable=False), sa.Column("subscription_id", sa.Integer(), nullable=True), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("currency", sa.String(length=3), nullable=False, server_default="SAR"), sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"), sa.Column("provider", sa.String(length=50), nullable=True), sa.Column("provider_reference", sa.String(length=180), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["company_id"], ["erp_companies.id"], name="fk_erp_payments_company_id"), sa.ForeignKeyConstraint(["subscription_id"], ["erp_subscriptions.id"], name="fk_erp_payments_subscription_id") )
    inspector = sa.inspect(bind)
    user_cols = _columns(inspector, "erp_users")
    user_fks = _fk_names(inspector, "erp_users")
    user_indexes = _index_names(inspector, "erp_users")
    with op.batch_alter_table("erp_users", schema=None) as batch_op:
        if "company_id" not in user_cols: batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
        if "display_name" not in user_cols: batch_op.add_column(sa.Column("display_name", sa.String(length=150), nullable=True))
        if "email" not in user_cols: batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        if "must_change_password" not in user_cols: batch_op.add_column(sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.text("0")))
        if "authz_version" not in user_cols: batch_op.add_column(sa.Column("authz_version", sa.Integer(), nullable=False, server_default="1"))
        if "last_login" not in user_cols: batch_op.add_column(sa.Column("last_login", sa.DateTime(), nullable=True))
        if "password_reset_token_hash" not in user_cols: batch_op.add_column(sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True))
        if "password_reset_expires_at" not in user_cols: batch_op.add_column(sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True))
        has_company_fk = FK_USERS_COMPANY in user_fks or ("erp_companies", ("company_id",)) in user_fks
        if not has_company_fk: batch_op.create_foreign_key(FK_USERS_COMPANY, "erp_companies", ["company_id"], ["id"])
        if IX_USERS_COMPANY not in user_indexes: batch_op.create_index(IX_USERS_COMPANY, ["company_id"])
        if IX_USERS_ACTIVE_ROLE not in user_indexes and {"is_active", "role"}.issubset(user_cols):
            batch_op.create_index(IX_USERS_ACTIVE_ROLE, ["is_active", "role"])
    plans = sa.table("erp_subscription_plans", sa.column("id", sa.Integer), sa.column("name", sa.String), sa.column("monthly_price", sa.Numeric), sa.column("annual_price", sa.Numeric), sa.column("description", sa.Text), sa.column("is_active", sa.Boolean))
    arabic_plan = bind.execute(sa.text("SELECT id FROM erp_subscription_plans WHERE name = 'الأساسية' LIMIT 1")).scalar()
    basic_plan = bind.execute(sa.text("SELECT id FROM erp_subscription_plans WHERE name = 'Basic' LIMIT 1")).scalar()
    if arabic_plan is None and basic_plan is not None:
        bind.execute(sa.text("UPDATE erp_subscription_plans SET name = 'الأساسية', description = :description WHERE id = :id"), {
            "description": "إدارة الأسطول والتشغيل والمستندات للمؤسسات الصغيرة والمتوسطة.",
            "id": basic_plan,
        })
    count = bind.execute(sa.text("SELECT COUNT(*) FROM erp_subscription_plans")).scalar()
    if not count:
        op.bulk_insert(plans, [{"name": "الأساسية", "monthly_price": 99, "annual_price": 990, "description": "إدارة الأسطول والتشغيل والمستندات للمؤسسات الصغيرة والمتوسطة.", "is_active": True}])

def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = _columns(inspector, "erp_users")
    user_fks = _fk_names(inspector, "erp_users")
    user_indexes = _index_names(inspector, "erp_users")

    if "erp_users" in _tables(inspector):
        with op.batch_alter_table("erp_users", schema=None) as batch_op:
            if IX_USERS_COMPANY in user_indexes:
                batch_op.drop_index(IX_USERS_COMPANY)
            if FK_USERS_COMPANY in user_fks or ("erp_companies", ("company_id",)) in user_fks:
                batch_op.drop_constraint(FK_USERS_COMPANY, type="foreignkey")
            if "company_id" in user_cols:
                batch_op.drop_column("company_id")

    for table in ("erp_payments", "erp_subscriptions", "erp_subscription_plans", "erp_companies"):
        if table in _tables(sa.inspect(bind)):
            op.drop_table(table)

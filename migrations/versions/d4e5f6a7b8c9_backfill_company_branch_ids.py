"""backfill a dedicated Branch + erp_users.branch_id for companies missing one

Revision ID: d4e5f6a7b8c9
Revises: b3c4d5e6f7a8
Create Date: 2026-09-20

Idempotent data migration for production and fresh databases.

Companies registered between the SaaS tables migration (a91c3e7b5d02,
2026-09-15) and the per-company Branch provisioning added to
routes/saas.py register_company() (commit 164d207, 2026-09-18) have users
with company_id set but branch_id NULL. helpers.py/app.py current_branch_id()
previously treated a missing branch_id as "branch 1" (البن زومة's real
Dammam branch), so such a legacy company session could read/write real
branch-1 data. This migration gives every such company its own dedicated
Branch (matching what register_company() does today) and points its users
at it — the same self-heal routes/saas.py _enter_isolated_site() and
routes/auth.py _establish_user_session() now also perform on login.
"""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "b3c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    orphaned_company_ids = [
        row[0] for row in bind.execute(sa.text(
            "SELECT DISTINCT u.company_id FROM erp_users u "
            "WHERE u.company_id IS NOT NULL AND u.branch_id IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM erp_branches b WHERE b.company_id = u.company_id)"
        )).fetchall()
    ]
    for company_id in orphaned_company_ids:
        name = bind.execute(
            sa.text("SELECT name FROM erp_companies WHERE id = :id"), {"id": company_id}
        ).scalar() or "شركة"
        bind.execute(
            sa.text("INSERT INTO erp_branches (name, company_id) VALUES (:name, :company_id)"),
            {"name": f"مساحة {name}", "company_id": company_id},
        )
    # Point every company user with no branch_id at their (now guaranteed to
    # exist) company's own dedicated branch. Correlated subquery so multiple
    # users of the same company all land on the SAME branch.
    bind.execute(sa.text(
        "UPDATE erp_users SET branch_id = ("
        "  SELECT b.id FROM erp_branches b WHERE b.company_id = erp_users.company_id"
        ") WHERE company_id IS NOT NULL AND branch_id IS NULL "
        "AND EXISTS (SELECT 1 FROM erp_branches b WHERE b.company_id = erp_users.company_id)"
    ))


def downgrade():
    # Data backfill only; no schema change to reverse. Leaving users pointed
    # at their company's branch on downgrade is safe and avoids resurrecting
    # the vulnerability this migration fixes.
    pass

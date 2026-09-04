"""merge migration heads

Revision ID: c1d4e8f7a902
Revises: 72becfe50723, 9a2f6c1d4e11
Create Date: 2026-09-04

This is a graph-only merge revision. The two parent branches already contain
all schema operations; this revision intentionally performs no additional DDL.
"""

revision = "c1d4e8f7a902"
down_revision = ("72becfe50723", "9a2f6c1d4e11")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

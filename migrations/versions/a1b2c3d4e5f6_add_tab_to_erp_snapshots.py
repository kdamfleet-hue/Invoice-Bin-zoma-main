"""Add tab column to erp_snapshots

Revision ID: a1b2c3d4e5f6
Revises: 9dfded86b804
Create Date: 2026-09-02 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9dfded86b804'  # تأكد أن هذا هو آخر revision عندك
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    columns = [col['name'] for col in inspector.get_columns('erp_snapshots')]
    
    with op.batch_alter_table('erp_snapshots', schema=None) as batch_op:
        if 'tab' not in columns:
            batch_op.add_column(sa.Column('tab', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('erp_snapshots', schema=None) as batch_op:
        batch_op.drop_column('tab')

"""add read-only inbound email tasks

Revision ID: f2a1b3c4d5e6
Revises: a91c3e7b5d02
"""
from alembic import op
import sqlalchemy as sa

revision = 'f2a1b3c4d5e6'
down_revision = 'a91c3e7b5d02'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'erp_inbound_email_tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('erp_branches.id'), nullable=True),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=True),
        sa.Column('sender', sa.String(length=255), nullable=True),
        sa.Column('recipients', sa.String(length=1000), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('body_preview', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='وارد'),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='inbound_read_only'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('message_id', name='uq_inbound_email_message_id'),
    )
    op.create_index('ix_erp_inbound_email_tasks_message_id', 'erp_inbound_email_tasks', ['message_id'], unique=True)


def downgrade():
    op.drop_index('ix_erp_inbound_email_tasks_message_id', table_name='erp_inbound_email_tasks')
    op.drop_table('erp_inbound_email_tasks')

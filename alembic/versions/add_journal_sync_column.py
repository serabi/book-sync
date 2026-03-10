"""add journal_sync column to hardcover_details

Revision ID: j1s2y3n4c5o6
Revises:
Create Date: 2026-03-08
"""
import sqlalchemy as sa

from alembic import op

revision = 'j1s2y3n4c5o6'
down_revision = 'add_hardcover_sync_log_table'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('hardcover_details')]
    if 'journal_sync' not in columns:
        with op.batch_alter_table('hardcover_details') as batch_op:
            batch_op.add_column(sa.Column('journal_sync', sa.String(10), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('hardcover_details')]
    if 'journal_sync' in columns:
        with op.batch_alter_table('hardcover_details') as batch_op:
            batch_op.drop_column('journal_sync')

"""add source column to book_alignments

Revision ID: i0j1k2l3m4n5
Revises: h9i0j1k2l3m4
Create Date: 2026-03-15
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'i0j1k2l3m4n5'
down_revision: str | Sequence[str] | None = 'h9i0j1k2l3m4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'book_alignments' not in inspector.get_table_names():
        return

    columns = {c['name'] for c in inspector.get_columns('book_alignments')}

    if 'source' not in columns:
        op.add_column('book_alignments', sa.Column('source', sa.String(20), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'book_alignments' not in inspector.get_table_names():
        return

    columns = {c['name'] for c in inspector.get_columns('book_alignments')}

    if 'source' in columns:
        op.drop_column('book_alignments', 'source')

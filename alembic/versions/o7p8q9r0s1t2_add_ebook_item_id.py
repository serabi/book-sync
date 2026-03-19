"""add ebook_item_id column — additive rename of abs_ebook_item_id

Adds ebook_item_id as source-agnostic name for the ebook library item ID.
Backfills from abs_ebook_item_id. Does NOT drop the old column — that
happens in a future cleanup release.

Revision ID: o7p8q9r0s1t2
Revises: n6o7p8q9r0s1
Create Date: 2026-03-18
"""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'o7p8q9r0s1t2'
down_revision: str | Sequence[str] | None = 'n6o7p8q9r0s1'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('books', sa.Column('ebook_item_id', sa.String(255), nullable=True))
    op.execute("UPDATE books SET ebook_item_id = abs_ebook_item_id WHERE abs_ebook_item_id IS NOT NULL")


def downgrade() -> None:
    op.drop_column('books', 'ebook_item_id')

"""rename abs_title to title — source-agnostic book model

The abs_title column stores the display title for ALL books regardless of
source (ABS, Storyteller, Booklore, KOSync). The abs_ prefix is misleading
now that the model is source-agnostic. This is a simple in-place rename.

Revision ID: n6o7p8q9r0s1
Revises: m5n6o7p8q9r0
Create Date: 2026-03-17
"""

from typing import Sequence

from alembic import op

revision: str = 'n6o7p8q9r0s1'
down_revision: str | Sequence[str] | None = 'm5n6o7p8q9r0'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('books', 'abs_title', new_column_name='title')


def downgrade() -> None:
    op.alter_column('books', 'title', new_column_name='abs_title')

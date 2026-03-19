"""add ondelete CASCADE to states and jobs foreign keys

Revision ID: j2k3l4m5n6o7
Revises: i0j1k2l3m4n5
Create Date: 2026-03-17
"""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'j2k3l4m5n6o7'
down_revision: str | Sequence[str] | None = 'i0j1k2l3m4n5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Superseded by Phase 2 migration (l4m5n6o7p8q9) which recreates
    # these tables with book_id FK + CASCADE.  Kept as no-op for
    # migration chain continuity.
    pass


def downgrade() -> None:
    with op.batch_alter_table('states', schema=None) as batch_op:
        batch_op.drop_constraint('fk_states_abs_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_states_abs_id', 'books', ['abs_id'], ['abs_id']
        )

    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_jobs_abs_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_jobs_abs_id', 'books', ['abs_id'], ['abs_id']
        )

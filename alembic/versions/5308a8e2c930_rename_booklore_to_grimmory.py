"""rename booklore to grimmory

Revision ID: 5308a8e2c930
Revises: p6q7r8s9t0u1
Create Date: 2026-03-27
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

revision: str = "5308a8e2c930"
down_revision: str | Sequence[str] | None = "p6q7r8s9t0u1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Rename table booklore_books -> grimmory_books
    op.rename_table("booklore_books", "grimmory_books")

    # Rename column kosync_documents.booklore_id -> grimmory_id
    with op.batch_alter_table("kosync_documents") as batch_op:
        batch_op.alter_column("booklore_id", new_column_name="grimmory_id")

    # Rename constraint and index on grimmory_books
    with op.batch_alter_table("grimmory_books") as batch_op:
        batch_op.drop_constraint("uq_booklore_server_filename", type_="unique")
        batch_op.create_unique_constraint("uq_grimmory_server_filename", ["server_id", "filename"])

    # Update client_name values in states table
    conn = op.get_bind()
    conn.execute(text("UPDATE states SET client_name = 'Grimmory' WHERE client_name = 'BookLore'"))
    conn.execute(text("UPDATE states SET client_name = 'Grimmory2' WHERE client_name = 'BookLore2'"))
    conn.execute(text("UPDATE states SET client_name = 'grimmory' WHERE client_name = 'booklore'"))

    # Update source values in kosync_documents
    conn.execute(text("UPDATE kosync_documents SET source = 'grimmory' WHERE source = 'booklore'"))

    # Rename settings keys from BOOKLORE_* to GRIMMORY_*
    conn.execute(text("UPDATE settings SET key = REPLACE(key, 'BOOKLORE', 'GRIMMORY') WHERE key LIKE 'BOOKLORE%'"))


def downgrade() -> None:
    conn = op.get_bind()

    # Revert settings keys
    conn.execute(text("UPDATE settings SET key = REPLACE(key, 'GRIMMORY', 'BOOKLORE') WHERE key LIKE 'GRIMMORY%'"))

    # Revert source values in kosync_documents
    conn.execute(text("UPDATE kosync_documents SET source = 'booklore' WHERE source = 'grimmory'"))

    # Revert client_name values in states table
    conn.execute(text("UPDATE states SET client_name = 'BookLore' WHERE client_name = 'Grimmory'"))
    conn.execute(text("UPDATE states SET client_name = 'BookLore2' WHERE client_name = 'Grimmory2'"))
    conn.execute(text("UPDATE states SET client_name = 'booklore' WHERE client_name = 'grimmory'"))

    # Revert constraint rename
    with op.batch_alter_table("grimmory_books") as batch_op:
        batch_op.drop_constraint("uq_grimmory_server_filename", type_="unique")
        batch_op.create_unique_constraint("uq_booklore_server_filename", ["server_id", "filename"])

    # Revert column rename
    with op.batch_alter_table("kosync_documents") as batch_op:
        batch_op.alter_column("grimmory_id", new_column_name="booklore_id")

    # Revert table rename
    op.rename_table("grimmory_books", "booklore_books")

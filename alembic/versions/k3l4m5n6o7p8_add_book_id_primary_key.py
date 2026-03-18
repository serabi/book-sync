"""add integer id as primary key to books table

Phase 1 of abs_id decoupling: adds auto-increment id as the new PK,
demotes abs_id to a unique non-null regular column.  Child table FKs
still reference books.abs_id via its UNIQUE constraint.

Uses explicit SQL table recreation for reliability on production
SQLite databases — batch_alter_table cannot reliably swap PKs.

Revision ID: k3l4m5n6o7p8
Revises: j2k3l4m5n6o7
Create Date: 2026-03-17
"""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'k3l4m5n6o7p8'
down_revision: str | Sequence[str] | None = 'j2k3l4m5n6o7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Every column from the current books table (order must match)
_BOOK_COLS = (
    'abs_id', 'abs_title', 'ebook_filename', 'original_ebook_filename',
    'kosync_doc_id', 'transcript_file', 'status', 'activity_flag',
    'duration', 'sync_mode', 'storyteller_uuid', 'abs_ebook_item_id',
    'custom_cover_url', 'started_at', 'finished_at', 'rating', 'read_count',
)


def upgrade() -> None:
    conn = op.get_bind()

    # Safety: clean up from a previously interrupted attempt
    conn.execute(sa.text("DROP TABLE IF EXISTS _books_new"))

    # 1. Create new table with id as INTEGER PRIMARY KEY AUTOINCREMENT
    conn.execute(sa.text("""
        CREATE TABLE _books_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abs_id VARCHAR(255) NOT NULL,
            abs_title VARCHAR(500),
            ebook_filename VARCHAR(500),
            original_ebook_filename VARCHAR(500),
            kosync_doc_id VARCHAR(255),
            transcript_file VARCHAR(500),
            status VARCHAR(50) DEFAULT 'not_started',
            activity_flag BOOLEAN DEFAULT 0,
            duration FLOAT,
            sync_mode VARCHAR(20) DEFAULT 'audiobook',
            storyteller_uuid VARCHAR(36),
            abs_ebook_item_id VARCHAR(255),
            custom_cover_url VARCHAR(500),
            started_at VARCHAR(10),
            finished_at VARCHAR(10),
            rating FLOAT,
            read_count INTEGER DEFAULT 1,
            UNIQUE (abs_id)
        )
    """))

    # 2. Copy all existing rows — id auto-populates via AUTOINCREMENT
    cols = ', '.join(_BOOK_COLS)
    conn.execute(sa.text(f"INSERT INTO _books_new ({cols}) SELECT {cols} FROM books"))

    # 3. Drop old table, rename new
    conn.execute(sa.text("DROP TABLE books"))
    conn.execute(sa.text("ALTER TABLE _books_new RENAME TO books"))

    # 4. Recreate indexes
    conn.execute(sa.text(
        "CREATE UNIQUE INDEX ix_books_abs_id ON books (abs_id)"))
    conn.execute(sa.text(
        "CREATE INDEX ix_books_kosync_doc_id ON books (kosync_doc_id)"))
    conn.execute(sa.text(
        "CREATE INDEX ix_books_storyteller_uuid ON books (storyteller_uuid)"))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DROP TABLE IF EXISTS _books_old"))

    # Recreate original table with abs_id as PK
    conn.execute(sa.text("""
        CREATE TABLE _books_old (
            abs_id VARCHAR(255) PRIMARY KEY,
            abs_title VARCHAR(500),
            ebook_filename VARCHAR(500),
            original_ebook_filename VARCHAR(500),
            kosync_doc_id VARCHAR(255),
            transcript_file VARCHAR(500),
            status VARCHAR(50) DEFAULT 'not_started',
            activity_flag BOOLEAN DEFAULT 0,
            duration FLOAT,
            sync_mode VARCHAR(20) DEFAULT 'audiobook',
            storyteller_uuid VARCHAR(36),
            abs_ebook_item_id VARCHAR(255),
            custom_cover_url VARCHAR(500),
            started_at VARCHAR(10),
            finished_at VARCHAR(10),
            rating FLOAT,
            read_count INTEGER DEFAULT 1
        )
    """))

    cols = ', '.join(_BOOK_COLS)
    conn.execute(sa.text(f"INSERT INTO _books_old ({cols}) SELECT {cols} FROM books"))
    conn.execute(sa.text("DROP TABLE books"))
    conn.execute(sa.text("ALTER TABLE _books_old RENAME TO books"))

    conn.execute(sa.text(
        "CREATE INDEX ix_books_kosync_doc_id ON books (kosync_doc_id)"))
    conn.execute(sa.text(
        "CREATE INDEX ix_books_storyteller_uuid ON books (storyteller_uuid)"))

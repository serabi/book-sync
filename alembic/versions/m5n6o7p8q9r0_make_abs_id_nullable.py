"""make books.abs_id nullable — books can exist without ABS

Phase 4 of abs_id decoupling: abs_id is now optional on the books
table, enabling standalone reading tracker use without ABS.

Child table abs_id columns are kept for backward compatibility.

Revision ID: m5n6o7p8q9r0
Revises: l4m5n6o7p8q9
Create Date: 2026-03-17
"""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'm5n6o7p8q9r0'
down_revision: str | Sequence[str] | None = 'l4m5n6o7p8q9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS _books_new"))
    conn.execute(sa.text("""
        CREATE TABLE _books_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abs_id VARCHAR(255),
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
    conn.execute(sa.text("""
        INSERT INTO _books_new (
            id, abs_id, abs_title, ebook_filename, original_ebook_filename,
            kosync_doc_id, transcript_file, status, activity_flag, duration,
            sync_mode, storyteller_uuid, abs_ebook_item_id, custom_cover_url,
            started_at, finished_at, rating, read_count
        )
        SELECT id, abs_id, abs_title, ebook_filename, original_ebook_filename,
            kosync_doc_id, transcript_file, status, activity_flag, duration,
            sync_mode, storyteller_uuid, abs_ebook_item_id, custom_cover_url,
            started_at, finished_at, rating, read_count
        FROM books
    """))
    conn.execute(sa.text("DROP TABLE books"))
    conn.execute(sa.text("ALTER TABLE _books_new RENAME TO books"))
    conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_books_abs_id ON books (abs_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_books_kosync_doc_id ON books (kosync_doc_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_books_storyteller_uuid ON books (storyteller_uuid)"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS _books_old"))
    conn.execute(sa.text("""
        CREATE TABLE _books_old (
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
    conn.execute(sa.text("INSERT INTO _books_old SELECT * FROM books WHERE abs_id IS NOT NULL"))
    conn.execute(sa.text("DROP TABLE books"))
    conn.execute(sa.text("ALTER TABLE _books_old RENAME TO books"))
    conn.execute(sa.text("CREATE UNIQUE INDEX ix_books_abs_id ON books (abs_id)"))
    conn.execute(sa.text("CREATE INDEX ix_books_kosync_doc_id ON books (kosync_doc_id)"))
    conn.execute(sa.text("CREATE INDEX ix_books_storyteller_uuid ON books (storyteller_uuid)"))

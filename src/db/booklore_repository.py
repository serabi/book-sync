"""Repository for Booklore integration: book metadata cache."""

import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .base_repository import BaseRepository
from .models import BookloreBook

logger = logging.getLogger(__name__)


class BookloreRepository(BaseRepository):

    def get_booklore_book(self, filename, server_id='default'):
        return self._get_one(
            BookloreBook,
            BookloreBook.filename == filename,
            BookloreBook.server_id == server_id,
        )

    def get_all_booklore_books(self, server_id=None):
        if server_id is None:
            return self._get_all(BookloreBook)
        with self.get_session() as session:
            rows = session.query(BookloreBook).filter(BookloreBook.server_id == server_id).all()
            for r in rows:
                session.expunge(r)
            return rows

    def save_booklore_book(self, booklore_book):
        with self.get_session() as session:
            existing = (
                session.query(BookloreBook)
                .filter(
                    BookloreBook.server_id == booklore_book.server_id,
                    BookloreBook.filename == booklore_book.filename,
                )
                .first()
            )

            if existing:
                for attr in ["title", "authors", "raw_metadata"]:
                    if hasattr(booklore_book, attr):
                        setattr(existing, attr, getattr(booklore_book, attr))
                session.flush()
                session.refresh(existing)
                session.expunge(existing)
                return existing
            else:
                try:
                    session.add(booklore_book)
                    session.flush()
                except IntegrityError:
                    session.rollback()
                    existing = (
                        session.query(BookloreBook)
                        .filter(
                            BookloreBook.server_id == booklore_book.server_id,
                            BookloreBook.filename == booklore_book.filename,
                        )
                        .first()
                    )
                    if existing:
                        for attr in ["title", "authors", "raw_metadata"]:
                            if hasattr(booklore_book, attr):
                                setattr(existing, attr, getattr(booklore_book, attr))
                        session.flush()
                        session.refresh(existing)
                        session.expunge(existing)
                        return existing
                    raise
                session.refresh(booklore_book)
                session.expunge(booklore_book)
                return booklore_book

    def delete_booklore_book(self, filename, server_id='default'):
        try:
            with self.get_session() as session:
                deleted = (
                    session.query(BookloreBook)
                    .filter(
                        BookloreBook.server_id == server_id,
                        BookloreBook.filename == filename,
                    )
                    .delete(synchronize_session=False)
                )
                return deleted > 0
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete Booklore book '{filename}': {e}")
            return False

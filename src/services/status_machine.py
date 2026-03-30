"""Centralized status transition logic for books.

All status transitions flow through StatusMachine.transition() to ensure
consistent side effects (journal entries, date filling, HC push, etc.).
"""

import logging
from datetime import date

from src.utils.logging_utils import sanitize_log_data

logger = logging.getLogger(__name__)

# Valid book statuses
VALID_STATUSES = {"active", "completed", "paused", "dnf", "not_started"}

# Status → journal event mapping
EVENT_MAP = {
    "completed": "finished",
    "paused": "paused",
    "dnf": "dnf",
}


class StatusMachine:
    """Single entry point for all book status transitions.

    The `source` parameter controls which side effects fire:
    - 'local': journal + HC push + Grimmory push + TBR cleanup + date fill
    - 'auto_complete': journal + date fill + HC push + TBR cleanup
    """

    def __init__(self, database_service):
        self.database_service = database_service

    def transition(self, book, new_status, source, *, container=None, dates=None, allowed_from=None):
        """Transition a book to a new status with appropriate side effects.

        Args:
            book: Book model instance (will be mutated).
            new_status: Target status string.
            source: 'local' or 'auto_complete'.
            container: DI container (needed for HC push, Grimmory push, date pull).
            dates: Optional dict with 'started_at'/'finished_at' to use instead of pulling.
            allowed_from: If set, only allow transition from these statuses.

        Returns:
            dict with 'success', 'status', 'previous_status', and optionally 'error'.
        """
        if new_status not in VALID_STATUSES:
            return {"success": False, "error": f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}"}

        old_status = book.status

        if allowed_from is not None and old_status not in allowed_from:
            return {"success": False, "error": f"Cannot change to '{new_status}' from status '{old_status}'"}

        if old_status == new_status:
            return {"success": True, "status": new_status, "previous_status": old_status}

        # Apply status change
        book.status = new_status
        if new_status == "active":
            book.activity_flag = False
        self.database_service.save_book(book)

        # Journal entry
        self._record_journal(book, new_status, old_status, source, container)

        # Date filling
        self._fill_dates(book, new_status, old_status, source, container, dates)

        if new_status in ("active", "paused", "dnf", "completed"):
            logger.info(f"Book status changed to '{new_status}': '{sanitize_log_data(book.title or book.abs_id)}'")

        # HC push
        if source in ("local", "auto_complete") and container:
            self._push_to_hardcover(book, new_status, container)

        # TBR cleanup — remove from Want to Read when book becomes active/finished
        if new_status in ("active", "completed", "paused", "dnf") and source in ("local", "auto_complete"):
            self._cleanup_tbr(book)

        # Grimmory push (local only)
        if source == "local" and book.ebook_filename and container:
            self._push_to_grimmory(book, new_status, old_status, container)

        return {"success": True, "status": new_status, "previous_status": old_status}

    def _cleanup_tbr(self, book):
        """Remove any TBR item for this book, falling back to HC book ID lookup."""
        deleted = self.database_service.delete_tbr_by_book_id(book.id)
        if not deleted:
            hc = self.database_service.get_hardcover_details(book.id)
            if hc and hc.hardcover_book_id:
                tbr = self.database_service.find_tbr_by_hardcover_id(int(hc.hardcover_book_id))
                if tbr:
                    self.database_service.delete_tbr_item(tbr.id)

    def _record_journal(self, book, new_status, old_status, source, container):
        """Create journal entry for the transition."""
        if new_status == "active":
            # Use old_status to decide: unread→started, anything else→resumed
            if old_status in ("not_started", "unread"):
                self.database_service.add_reading_journal(book.id, event="started", abs_id=book.abs_id)
            else:
                self.database_service.add_reading_journal(book.id, event="resumed", abs_id=book.abs_id)
            return

        event = EVENT_MAP.get(new_status)
        if event:
            pct = 1.0 if event == "finished" else None
            self.database_service.add_reading_journal(book.id, event=event, percentage=pct, abs_id=book.abs_id)

    def _fill_dates(self, book, new_status, old_status, source, container, dates):
        """Fill in started_at/finished_at based on the transition."""
        updates = {}

        if new_status == "active":
            if not book.started_at:
                updates["started_at"] = self._resolve_started_at(book.id, container, dates)
        elif new_status == "completed":
            if not book.finished_at:
                updates["finished_at"] = (dates or {}).get("finished_at") or date.today().isoformat()
                if not book.started_at:
                    updates["started_at"] = self._resolve_started_at(book.id, container, dates)
            else:
                # Re-read — increment read count
                updates["read_count"] = (book.read_count or 1) + 1

        if updates:
            self.database_service.update_book_reading_fields(book.id, **updates)

    def _resolve_started_at(self, book_id, container, dates):
        """Get started_at from provided dates, external pull, or today."""
        if dates and dates.get("started_at"):
            return dates["started_at"]
        if container:
            try:
                pulled = container.reading_date_service().pull_reading_dates(book_id)
                return pulled.get("started_at", date.today().isoformat())
            except Exception as e:
                logger.debug("Could not pull started_at for book_id=%s: %s", book_id, e)
        return date.today().isoformat()

    def _push_to_hardcover(self, book, new_status, container):
        """Push status change to Hardcover."""
        try:
            hc_service = container.hardcover_service()
            if hc_service.is_configured():
                hc_service.push_local_status(book, new_status)
        except Exception as e:
            logger.debug(f"Could not push status to Hardcover: {e}")

    def _push_to_grimmory(self, book, new_status, old_status, container):
        """Push read status to Grimmory for relevant transitions."""
        from src.services.reading_date_service import push_grimmory_read_status

        if new_status == "active" and old_status in ("dnf", "paused", "not_started", "completed"):
            push_grimmory_read_status(book, container, "READING")
        elif new_status == "completed":
            push_grimmory_read_status(book, container, "READ")

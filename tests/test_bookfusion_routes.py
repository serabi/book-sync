"""Tests for BookFusion blueprint routes."""

from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest
from tests.conftest import MockContainer


def _make_mock_book(
    abs_id="test-abs-id",
    title="Test Book",
    book_id=1,
    status="active",
    ebook_filename="book.epub",
    original_ebook_filename=None,
    author="Test Author",
):
    """Return a Mock that behaves like a Book ORM instance."""
    book = Mock()
    book.id = book_id
    book.abs_id = abs_id
    book.title = title
    book.status = status
    book.started_at = None
    book.finished_at = None
    book.sync_mode = "audiobook"
    book.ebook_filename = ebook_filename
    book.original_ebook_filename = original_ebook_filename
    book.author = author
    return book


def _make_bf_book(
    bookfusion_id="bf-123",
    title="BF Book",
    authors="Author",
    filename="book.epub",
    highlight_count=3,
    matched_book_id=None,
    hidden=False,
    series=None,
    tags=None,
):
    """Return a Mock that behaves like a BookfusionBook ORM instance."""
    bf = Mock()
    bf.bookfusion_id = bookfusion_id
    bf.title = title
    bf.authors = authors
    bf.filename = filename
    bf.highlight_count = highlight_count
    bf.matched_book_id = matched_book_id
    bf.hidden = hidden
    bf.series = series
    bf.tags = tags
    bf.frontmatter = None
    return bf


def _make_bf_highlight(
    hl_id=1,
    highlight_id="hl-1",
    bookfusion_book_id="bf-123",
    book_title="BF Book",
    content="Some highlight text",
    quote_text=None,
    chapter_heading=None,
    matched_book_id=None,
    highlighted_at=None,
):
    """Return a Mock that behaves like a BookfusionHighlight ORM instance."""
    hl = Mock()
    hl.id = hl_id
    hl.highlight_id = highlight_id
    hl.bookfusion_book_id = bookfusion_book_id
    hl.book_title = book_title
    hl.content = content
    hl.quote_text = quote_text
    hl.chapter_heading = chapter_heading
    hl.matched_book_id = matched_book_id
    hl.highlighted_at = highlighted_at
    return hl


# ── Upload ───────────────────────────────────────────────────────────────


def test_upload_requires_abs_id(client, mock_container):
    resp = client.post(
        "/api/bookfusion/upload",
        json={},
    )
    assert resp.status_code == 400
    assert "abs_id required" in resp.get_json()["error"]


def test_upload_book_not_found(client, mock_container):
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = None
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/upload",
        json={"abs_id": "nonexistent"},
    )
    assert resp.status_code == 404


def test_upload_requires_ebook_file(client, mock_container):
    book = _make_mock_book(ebook_filename=None, original_ebook_filename=None)
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/upload",
        json={"abs_id": "test-abs-id"},
    )
    assert resp.status_code == 400
    assert "No ebook file" in resp.get_json()["error"]


def test_upload_requires_upload_api_key(client, mock_container):
    book = _make_mock_book()
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_container._database = mock_db

    mock_bf = Mock()
    mock_bf.upload_api_key = None
    mock_container.mock_bookfusion_client.upload_api_key = None

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post(
            "/api/bookfusion/upload",
            json={"abs_id": "test-abs-id"},
        )
    assert resp.status_code == 400
    assert "not configured" in resp.get_json()["error"]


def test_upload_success(client, mock_container, tmp_path):
    book = _make_mock_book(ebook_filename="test.epub")
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_container._database = mock_db

    mock_bf = Mock()
    mock_bf.upload_api_key = "test-key"
    mock_bf.upload_book.return_value = {"id": "bf-123", "title": "Test"}

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        with patch("src.utils.epub_resolver.get_local_epub") as mock_resolve:
            mock_resolve.return_value = None

            resp = client.post(
                "/api/bookfusion/upload",
                json={"abs_id": "test-abs-id"},
            )

    assert resp.status_code == 500
    assert "Could not locate" in resp.get_json()["error"]


def test_upload_saves_bookfusion_link(client, mock_container, tmp_path):
    book = _make_mock_book(ebook_filename="test.epub", book_id=42)
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_container._database = mock_db

    mock_bf = Mock()
    mock_bf.upload_api_key = "test-key"
    mock_bf.upload_book.return_value = {"id": "bf-123", "title": "Test Book", "authors": "Author"}

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        with patch("src.utils.epub_resolver.get_local_epub") as mock_resolve:
            test_file = tmp_path / "test.epub"
            test_file.write_bytes(b"fake epub content")
            mock_resolve.return_value = test_file

            resp = client.post(
                "/api/bookfusion/upload",
                json={"abs_id": "test-abs-id"},
            )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert mock_db.save_bookfusion_book.called


# ── Sync Highlights (Full) ─────────────────────────────────────────────


def test_sync_highlights_requires_api_key(client, mock_container):
    mock_bf = Mock()
    mock_bf.highlights_api_key = None
    mock_container.mock_bookfusion_client.highlights_api_key = None

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post("/api/bookfusion/sync-highlights")

    assert resp.status_code == 400
    assert "not configured" in resp.get_json()["error"]


def test_sync_highlights_success(client, mock_container):
    mock_bf = Mock()
    mock_bf.highlights_api_key = "test-key"
    mock_bf.sync_all_highlights.return_value = {
        "new_highlights": 5,
        "books_saved": 2,
        "new_ids": ["hl-1", "hl-2"],
    }

    mock_db = Mock()
    mock_db.get_bookfusion_sync_cursor.return_value = None
    mock_container._database = mock_db

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post("/api/bookfusion/sync-highlights")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["new_highlights"] == 5
    assert data["books_saved"] == 2


def test_sync_highlights_full_resync(client, mock_container):
    mock_bf = Mock()
    mock_bf.highlights_api_key = "test-key"
    mock_bf.sync_all_highlights.return_value = {
        "new_highlights": 10,
        "books_saved": 3,
        "new_ids": [],
    }

    mock_db = Mock()
    mock_container._database = mock_db

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post(
            "/api/bookfusion/sync-highlights",
            json={"full_resync": True},
        )

    assert resp.status_code == 200
    mock_db.set_bookfusion_sync_cursor.assert_called_with(None)


# ── Sync Book (Per-Book) ─────────────────────────────────────────────


def test_sync_book_requires_abs_id(client, mock_container):
    resp = client.post("/api/bookfusion/sync-book", json={})
    assert resp.status_code == 400
    assert "abs_id required" in resp.get_json()["error"]


def test_sync_book_book_not_found(client, mock_container):
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = None
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/sync-book",
        json={"abs_id": "nonexistent"},
    )
    assert resp.status_code == 404


def test_sync_book_not_linked(client, mock_container):
    book = _make_mock_book()
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_books_by_book_id.return_value = []
    mock_container._database = mock_db

    mock_bf = Mock()
    mock_bf.highlights_api_key = "test-key"

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post(
            "/api/bookfusion/sync-book",
            json={"abs_id": "test-abs-id"},
        )

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"]


def test_sync_book_success(client, mock_container):
    book = _make_mock_book(book_id=42)
    bf_book = _make_bf_book(bookfusion_id="bf-123", matched_book_id=42)

    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_books_by_book_id.return_value = [bf_book]
    mock_container._database = mock_db

    mock_bf = Mock()
    mock_bf.highlights_api_key = "test-key"
    mock_bf.sync_all_highlights.return_value = {
        "new_highlights": 3,
        "books_saved": 1,
    }

    with patch.object(mock_container, "bookfusion_client", return_value=mock_bf):
        resp = client.post(
            "/api/bookfusion/sync-book",
            json={"abs_id": "test-abs-id"},
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["linked_books"] == 1


# ── Save Journal (With Deduplication) ─────────────────────────────────


def test_save_journal_requires_abs_id(client, mock_container):
    resp = client.post("/api/bookfusion/save-journal", json={})
    assert resp.status_code == 400
    assert "abs_id required" in resp.get_json()["error"]


def test_save_journal_book_not_found(client, mock_container):
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = None
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/save-journal",
        json={"abs_id": "nonexistent"},
    )
    assert resp.status_code == 404


def test_save_journal_no_highlights(client, mock_container):
    book = _make_mock_book()
    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_highlights_for_book_by_book_id.return_value = []
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/save-journal",
        json={"abs_id": "test-abs-id"},
    )
    assert resp.status_code == 400
    assert "No highlights" in resp.get_json()["error"]


def test_save_journal_success(client, mock_container):
    book = _make_mock_book(book_id=42)
    highlight = _make_bf_highlight(
        quote_text="Test quote",
        chapter_heading="Chapter 1",
        highlighted_at=datetime(2026, 1, 15),
        matched_book_id=42,
    )

    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_highlights_for_book_by_book_id.return_value = [highlight]
    mock_db.get_reading_journal_entries_for_book.return_value = []
    mock_db.cleanup_bookfusion_import_notes.return_value = {
        "entries_cleaned": 0,
        "timestamps_backfilled": 0,
    }
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/save-journal",
        json={"abs_id": "test-abs-id"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["saved"] == 1
    mock_db.add_reading_journal.assert_called_once()


def test_save_journal_deduplication(client, mock_container):
    book = _make_mock_book(book_id=42)
    highlight = _make_bf_highlight(
        quote_text="Duplicate quote",
        chapter_heading="Chapter 1",
        highlighted_at=datetime(2026, 1, 15),
        matched_book_id=42,
    )

    existing_journal = Mock()
    existing_journal.entry = "Duplicate quote\n— Chapter 1"

    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_highlights_for_book_by_book_id.return_value = [highlight]
    mock_db.get_reading_journal_entries_for_book.return_value = [existing_journal]
    mock_db.cleanup_bookfusion_import_notes.return_value = {"entries_cleaned": 0, "timestamps_backfilled": 0}
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/save-journal",
        json={"abs_id": "test-abs-id"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["saved"] == 0
    assert data["skipped"] == 1
    mock_db.add_reading_journal.assert_not_called()


def test_save_journal_with_existing_entries(client, mock_container):
    book = _make_mock_book(book_id=42)
    highlight = _make_bf_highlight(
        quote_text="New quote",
        chapter_heading="Chapter 2",
        highlighted_at=datetime(2026, 2, 1),
        matched_book_id=42,
    )

    existing_journal = Mock()
    existing_journal.entry = "Old quote"

    mock_db = Mock()
    mock_db.get_book_by_ref.return_value = book
    mock_db.get_bookfusion_highlights_for_book_by_book_id.return_value = [highlight]
    mock_db.get_reading_journal_entries_for_book.return_value = [existing_journal]
    mock_db.cleanup_bookfusion_import_notes.return_value = {"entries_cleaned": 0, "timestamps_backfilled": 0}
    mock_container._database = mock_db

    resp = client.post(
        "/api/bookfusion/save-journal",
        json={"abs_id": "test-abs-id"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["saved"] == 1
    mock_db.add_reading_journal.assert_called_once()

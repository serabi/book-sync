"""Shared title normalization utilities used by BookFusion and database layers."""

import re

STRIP_EXTENSIONS = re.compile(r"\.(epub|mobi|azw3?|pdf|fb2|cbz|cbr|md)$", re.IGNORECASE)


def normalize_title(title: str) -> str:
    """Normalize a title for matching: strip extensions, lowercase, collapse whitespace."""
    t = STRIP_EXTENSIONS.sub("", title)
    return " ".join(t.lower().split())


def clean_book_title(title: str) -> str:
    """Strip .md suffix and wiki-link artifacts from book titles."""
    if title.endswith(".md"):
        title = title[:-3]
    return title.strip()

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup


def _is_hidden(tag) -> bool:
    """Identify HTML elements that should not become document text."""

    if tag.has_attr("hidden"):
        return True

    if tag.get("aria-hidden") == "true":
        return True

    style = (tag.get("style") or "").replace(" ", "").lower()

    return (
        "display:none" in style
        or "visibility:hidden" in style
    )


def _is_page_marker(line: str) -> bool:
    """
    Identify recurring SEC page header/footer markers.

    Example:
        Apple Inc. | 2025 Form 10-K | 5
    """

    normalized = " ".join(line.split())

    pattern = re.compile(
        r"^.+\|\s*\d{4}\s+Form\s+10-K\s*\|\s*\d+$",
        flags=re.IGNORECASE,
    )

    return bool(pattern.fullmatch(normalized))


def parse_html_to_text(file_path: str | Path) -> str:
    """Convert an SEC HTML filing into cleaned human-readable text."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Filing not found: {file_path}"
        )

    html = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # Remove non-document elements.
    for element in soup(
        [
            "script",
            "style",
            "noscript",
        ]
    ):
        element.decompose()

    # Remove Inline XBRL metadata containers.
    for tag_name in [
        "ix:header",
        "ix:hidden",
        "ix:resources",
        "ix:references",
    ]:
        for element in soup.find_all(tag_name):
            element.decompose()

    # Remove elements explicitly marked as hidden.
    for element in soup.find_all(_is_hidden):
        element.decompose()

    # Prefer document body when available.
    document = soup.body or soup

    text = document.get_text(
        separator="\n",
        strip=True,
    )

    cleaned_lines = []

    for line in text.splitlines():

        cleaned = re.sub(
            r"[ \t]+",
            " ",
            line,
        ).strip()

        if not cleaned:
            continue

        # Remove recurring SEC page headers/footers.
        if _is_page_marker(cleaned):
            continue

        cleaned_lines.append(cleaned)

    return "\n".join(cleaned_lines)
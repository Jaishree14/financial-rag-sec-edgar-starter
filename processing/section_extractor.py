from __future__ import annotations

import re


MIN_SECTION_CHARS = 1000


def _normalize_heading(line: str) -> str:
    """
    Normalize whitespace and typographic apostrophes.
    """
    normalized = " ".join(line.split()).strip()

    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("‘", "'")

    return normalized


def find_heading_indices(
    lines: list[str],
    heading_pattern: str,
) -> list[int]:
    """
    Find all occurrences of a section heading.

    Handles both common SEC filing formats:

    Format 1 - heading on one line:
        Item 1.    Business

    Format 2 - heading split across lines:
        ITEM 1. B
        USINESS

    Also ignores Table-of-Contents occurrences when the
    matched heading is immediately followed by a page number.
    """

    pattern = re.compile(
        heading_pattern,
        flags=re.IGNORECASE,
    )

    # ---------------------------------------------------------
    # Build a second regex for whitespace-insensitive matching.
    #
    # Example:
    #
    # Item 1.\s*Business
    #
    # becomes approximately:
    #
    # Item1\.Business
    #
    # This lets us match:
    #
    # ITEM 1. B
    # USINESS
    # ---------------------------------------------------------

    compact_pattern_text = heading_pattern

    # Remove regex whitespace operators used in our patterns.
    compact_pattern_text = compact_pattern_text.replace(
        r"\s*",
        "",
    )
    compact_pattern_text = compact_pattern_text.replace(
        r"\s+",
        "",
    )

    # Remove literal whitespace.
    compact_pattern_text = re.sub(
        r"\s+",
        "",
        compact_pattern_text,
    )

    compact_pattern = re.compile(
        compact_pattern_text,
        flags=re.IGNORECASE,
    )

    matches: list[int] = []

    for index in range(len(lines)):

        current = _normalize_heading(lines[index])

        if not current:
            continue

        # =====================================================
        # CASE 1: Normal one-line heading
        # =====================================================

        if pattern.fullmatch(current):

            # Check whether this is probably a TOC entry.
            # Example:
            #
            # Item 1.
            # Business
            # 3
            #
            # In that case, ignore it.
            toc_match = False

            next_index = index + 1

            while next_index < len(lines):
                next_line = _normalize_heading(
                    lines[next_index]
                )

                if next_line:
                    if re.fullmatch(
                        r"\d+",
                        next_line,
                    ):
                        toc_match = True
                    break

                next_index += 1

            if not toc_match:
                matches.append(index)

            continue

        # =====================================================
        # CASE 2: Heading split across multiple lines
        # =====================================================

        combined_parts = [current]

        # Five lines is enough for the SEC headings we have
        # observed so far, while still limiting false matches.
        for offset in range(1, 6):

            next_index = index + offset

            if next_index >= len(lines):
                break

            next_line = _normalize_heading(
                lines[next_index]
            )

            if not next_line:
                continue

            combined_parts.append(next_line)

            # -------------------------------------------------
            # Normal comparison
            #
            # ITEM 1.
            # Business
            #
            # becomes:
            #
            # ITEM 1. Business
            # -------------------------------------------------

            candidate = " ".join(
                combined_parts
            )

            if pattern.fullmatch(candidate):

                toc_match = False

                page_index = next_index + 1

                while page_index < len(lines):
                    page_line = _normalize_heading(
                        lines[page_index]
                    )

                    if page_line:
                        if re.fullmatch(
                            r"\d+",
                            page_line,
                        ):
                            toc_match = True
                        break

                    page_index += 1

                if not toc_match:
                    matches.append(index)

                break

            # -------------------------------------------------
            # COMPACT comparison
            #
            # This handles:
            #
            # ITEM 1. B
            # USINESS
            #
            # candidate:
            # ITEM 1. B USINESS
            #
            # compact:
            # ITEM1.BUSINESS
            # -------------------------------------------------

            compact_candidate = re.sub(
                r"\s+",
                "",
                candidate,
            )

            if compact_pattern.fullmatch(
                compact_candidate
            ):

                toc_match = False

                page_index = next_index + 1

                while page_index < len(lines):
                    page_line = _normalize_heading(
                        lines[page_index]
                    )

                    if page_line:
                        if re.fullmatch(
                            r"\d+",
                            page_line,
                        ):
                            toc_match = True
                        break

                    page_index += 1

                if not toc_match:
                    matches.append(index)

                break

    return matches

def find_section_bounds(
    lines: list[str],
    start_heading_pattern: str,
    end_heading_pattern: str,
) -> tuple[int, int] | None:
    """
    Find the first credible section boundary pair.

    SEC filings often contain headings in:
      - Table of Contents
      - cross-references
      - the actual section

    We therefore:
      1. Find every start-heading occurrence.
      2. For each occurrence, find the nearest end heading.
      3. Reject suspiciously short sections.
      4. Return the first credible pair.
    """

    start_matches = find_heading_indices(
        lines,
        start_heading_pattern,
    )

    end_matches = find_heading_indices(
        lines,
        end_heading_pattern,
    )

    if not start_matches or not end_matches:
        return None

    for start_index in start_matches:

        # Find the nearest end heading after this start.
        candidate_end = None

        for end_index in end_matches:
            if end_index > start_index:
                candidate_end = end_index
                break

        if candidate_end is None:
            continue

        section_text = "\n".join(
            lines[start_index:candidate_end]
        ).strip()

        # Reject Table-of-Contents fragments and other
        # tiny references.
        if len(section_text) < MIN_SECTION_CHARS:
            continue

        return start_index, candidate_end

    return None


def extract_section(
    text: str,
    start_heading_pattern: str,
    end_heading_pattern: str,
) -> str:
    """
    Extract the first credible section between two headings.
    """

    lines = text.splitlines()

    bounds = find_section_bounds(
        lines=lines,
        start_heading_pattern=start_heading_pattern,
        end_heading_pattern=end_heading_pattern,
    )

    if bounds is None:
        raise ValueError(
            "Could not find a credible section boundary pair:\n"
            f"Start: {start_heading_pattern}\n"
            f"End: {end_heading_pattern}"
        )

    start_index, end_index = bounds

    return "\n".join(
        lines[start_index:end_index]
    ).strip()


def extract_major_sections(text: str) -> dict[str, str]:
    """
    Extract the four major sections used by the RAG pipeline.
    """

    return {
        "business": extract_section(
            text=text,
            start_heading_pattern=r"Item 1\.\s*Business",
            end_heading_pattern=r"Item 1A\.\s*Risk Factors",
        ),

        "risk_factors": extract_section(
            text=text,
            start_heading_pattern=r"Item 1A\.\s*Risk Factors",
            end_heading_pattern=r"Item 1B\.\s*Unresolved Staff Comments",
        ),

        "cybersecurity": extract_section(
            text=text,
            start_heading_pattern=r"Item 1C\.\s*Cybersecurity",
            end_heading_pattern=r"Item 2\.\s*Properties",
        ),

        "management_discussion": extract_section(
            text=text,
            start_heading_pattern=(
                r"Item 7\.\s*Management's Discussion and Analysis "
                r"of Financial Condition and Results of Operations"
            ),
            end_heading_pattern=(
                r"Item 7A\.\s*Quantitative and Qualitative Disclosures "
                r"About Market Risk"
            ),
        ),
    }
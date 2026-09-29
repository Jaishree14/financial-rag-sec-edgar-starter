from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """
    Represents one processed document chunk together with
    the metadata needed for traceability and retrieval.
    """

    chunk_id: str
    text: str
    ticker: str
    company_name: str
    accession_number: str
    filing_date: str
    form_type: str
    section: str
    chunk_index: int
    total_chunks: int
    word_count: int
    source_path: str


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 75,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()

    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


def create_chunks(
    text: str,
    ticker: str,
    company_name: str,
    accession_number: str,
    filing_date: str,
    form_type: str,
    section: str,
    source_path: str,
    chunk_size: int = 500,
    overlap: int = 75,
) -> list[Chunk]:
    """
    Create text chunks and attach filing metadata to each chunk.
    """

    texts = chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    total_chunks = len(texts)

    chunks: list[Chunk] = []

    for index, chunk in enumerate(texts):
        chunk_id = (
            f"{ticker}-"
            f"{accession_number}-"
            f"{section}-"
            f"{index:04d}"
        )

        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                text=chunk,
                ticker=ticker,
                company_name=company_name,
                accession_number=accession_number,
                filing_date=filing_date,
                form_type=form_type,
                section=section,
                chunk_index=index,
                total_chunks=total_chunks,
                word_count=len(chunk.split()),
                source_path=source_path,
            )
        )

    return chunks
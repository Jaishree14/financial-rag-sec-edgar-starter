from __future__ import annotations

import uuid
from pathlib import Path

from qdrant_client.models import PointStruct
from sqlalchemy import select

from embeddings.embedder import embed_text
from processing.chunker import create_chunks
from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections
from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)
from storage.database import SessionLocal
from storage.models import Filing


CHUNK_SIZE = 500
CHUNK_OVERLAP = 75


def index_filing(filing: Filing) -> int:
    """
    Process and index one downloaded SEC filing.

    Returns:
        Number of chunks indexed.
    """

    if not filing.local_path:
        raise ValueError(
            f"No local path found for {filing.ticker}"
        )

    file_path = Path(filing.local_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Filing file does not exist: {file_path}"
        )

    print(f"Processing {filing.ticker} - {filing.company_name}")
    print(f"File: {file_path}")

    # ---------------------------------------------------------
    # 1. Parse HTML
    # ---------------------------------------------------------

    text = parse_html_to_text(file_path)

    print(f"Parsed characters: {len(text):,}")

    # ---------------------------------------------------------
    # 2. Extract major sections
    # ---------------------------------------------------------

    sections = extract_major_sections(text)

    client = get_qdrant_client()

    total_chunks = 0

    # ---------------------------------------------------------
    # 3. Process each section
    # ---------------------------------------------------------

    for section_name, section_text in sections.items():

        chunks = create_chunks(
            text=section_text,
            ticker=filing.ticker,
            company_name=filing.company_name,
            accession_number=filing.accession_number,
            filing_date=str(filing.filing_date),
            form_type=filing.form_type,
            section=section_name,
            source_path=str(file_path),
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )

        print(
            f"  {section_name}: "
            f"{len(chunks)} chunks"
        )

        points: list[PointStruct] = []

        # -----------------------------------------------------
        # 4. Generate embeddings
        # -----------------------------------------------------

        for chunk in chunks:

            vector = embed_text(chunk.text)

            qdrant_point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    chunk.chunk_id,
                )
            )

            points.append(
                PointStruct(
                    id=qdrant_point_id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "ticker": chunk.ticker,
                        "company_name": chunk.company_name,
                        "accession_number": chunk.accession_number,
                        "filing_date": chunk.filing_date,
                        "form_type": chunk.form_type,
                        "section": chunk.section,
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks,
                        "word_count": chunk.word_count,
                        "source_path": chunk.source_path,
                    },
                )
            )

        # -----------------------------------------------------
        # 5. Store vectors + metadata in Qdrant
        # -----------------------------------------------------

        if points:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )

        total_chunks += len(points)

    print(
        f"Indexed {total_chunks} chunks for {filing.ticker}"
    )

    return total_chunks


def main() -> None:
    """
    Index every downloaded filing registered in PostgreSQL.
    """

    session = SessionLocal()

    try:
        statement = (
            select(Filing)
            .where(Filing.status == "downloaded")
            .order_by(Filing.ticker)
        )

        filings = session.scalars(statement).all()

        print(
            f"Found {len(filings)} downloaded filings."
        )
        print()

        total_indexed = 0

        for filing in filings:

            print("=" * 80)

            indexed = index_filing(filing)

            total_indexed += indexed

            print()

        print("=" * 80)
        print("BULK INDEXING COMPLETE")
        print("=" * 80)
        print(
            f"Total chunks indexed: {total_indexed}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()
from __future__ import annotations

import uuid

from qdrant_client.models import PointStruct

from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections
from processing.chunker import create_chunks
from embeddings.embedder import embed_text
from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)


FILE_PATH = "data/raw/Apple_Inc./2025-10-31_10-K.html"


def main():
    # 1. Parse the filing
    text = parse_html_to_text(FILE_PATH)

    # 2. Extract the major sections
    sections = extract_major_sections(text)

    # 3. Select Risk Factors
    risk_factors = sections["risk_factors"]

    # 4. Create chunks
    chunks = create_chunks(
        text=risk_factors,
        ticker="AAPL",
        company_name="Apple Inc.",
        accession_number="0000320193-25-000079",
        filing_date="2025-10-31",
        form_type="10-K",
        section="risk_factors",
        source_path=FILE_PATH,
        chunk_size=500,
        overlap=75,
    )

    # 5. Take the first chunk
    first_chunk = chunks[0]

    # 6. Generate its embedding
    vector = embed_text(first_chunk.text)

    # 7. Create a deterministic UUID for Qdrant
    qdrant_point_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            first_chunk.chunk_id,
        )
    )

    print("Application chunk ID:")
    print(first_chunk.chunk_id)
    print()

    print("Qdrant point ID:")
    print(qdrant_point_id)
    print()

    # 8. Connect to Qdrant
    client = get_qdrant_client()

    # 9. Create the Qdrant point
    point = PointStruct(
        id=qdrant_point_id,
        vector=vector,
        payload={
            "chunk_id": first_chunk.chunk_id,
            "text": first_chunk.text,
            "ticker": first_chunk.ticker,
            "company_name": first_chunk.company_name,
            "accession_number": first_chunk.accession_number,
            "filing_date": first_chunk.filing_date,
            "form_type": first_chunk.form_type,
            "section": first_chunk.section,
            "chunk_index": first_chunk.chunk_index,
            "total_chunks": first_chunk.total_chunks,
            "word_count": first_chunk.word_count,
            "source_path": first_chunk.source_path,
        },
    )

    # 10. Insert into Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )

    print("Qdrant insertion successful.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Vector dimensions: {len(vector)}")


if __name__ == "__main__":
    main()
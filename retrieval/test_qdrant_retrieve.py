from __future__ import annotations

import uuid

from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)


CHUNK_ID = "AAPL-0000320193-25-000079-risk_factors-0000"


def main():
    # Generate the same deterministic Qdrant UUID
    point_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            CHUNK_ID,
        )
    )

    client = get_qdrant_client()

    points = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[point_id],
        with_payload=True,
        with_vectors=False,
    )

    if not points:
        raise RuntimeError("Chunk was not found in Qdrant.")

    point = points[0]
    payload = point.payload or {}

    print("Qdrant retrieval successful.")
    print()
    print(f"Qdrant point ID: {point.id}")
    print(f"Chunk ID: {payload.get('chunk_id')}")
    print(f"Ticker: {payload.get('ticker')}")
    print(f"Company: {payload.get('company_name')}")
    print(f"Section: {payload.get('section')}")
    print(f"Chunk index: {payload.get('chunk_index')}")
    print(f"Word count: {payload.get('word_count')}")
    print()
    print("Text preview:")
    print(payload.get("text", "")[:500])


if __name__ == "__main__":
    main()
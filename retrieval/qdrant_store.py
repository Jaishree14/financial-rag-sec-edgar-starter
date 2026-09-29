from __future__ import annotations

import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

COLLECTION_NAME = "financial_documents"
VECTOR_SIZE = 768


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )


def create_collection() -> None:
    client = get_qdrant_client()

    existing_collections = client.get_collections().collections

    existing_names = {
        collection.name for collection in existing_collections
    }

    if COLLECTION_NAME in existing_names:
        print(f"Collection already exists: {COLLECTION_NAME}")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(f"Collection created: {COLLECTION_NAME}")


if __name__ == "__main__":
    create_collection()
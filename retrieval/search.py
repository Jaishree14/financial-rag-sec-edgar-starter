from __future__ import annotations

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)

from embeddings.embedder import embed_text
from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)


def search(
    query: str,
    limit: int = 5,
    ticker: str | None = None,
    section: str | None = None,
) -> list[dict]:
    """
    Perform semantic search over indexed SEC filing chunks.

    Args:
        query: Natural-language question.
        limit: Maximum number of results.
        ticker: Optional ticker such as AAPL, MSFT, or TSLA.
        section: Optional section such as risk_factors,
                 business, cybersecurity, or management_discussion.
    """

    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    if limit <= 0:
        raise ValueError("Limit must be greater than 0.")

    if ticker is not None:
        ticker = ticker.strip().upper()

        if not ticker:
            raise ValueError("Ticker must not be empty.")

    if section is not None:
        section = section.strip().lower()

        if not section:
            raise ValueError("Section must not be empty.")

    # ---------------------------------------------------------
    # Generate query embedding
    # ---------------------------------------------------------

    query_vector = embed_text(query)

    client = get_qdrant_client()

    # ---------------------------------------------------------
    # Build metadata filters
    # ---------------------------------------------------------

    conditions = []

    if ticker is not None:
        conditions.append(
            FieldCondition(
                key="ticker",
                match=MatchValue(value=ticker),
            )
        )

    if section is not None:
        conditions.append(
            FieldCondition(
                key="section",
                match=MatchValue(value=section),
            )
        )

    query_filter = None

    if conditions:
        query_filter = Filter(
            must=conditions
        )

    # ---------------------------------------------------------
    # Semantic search
    # ---------------------------------------------------------

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    ).points

    matches = []

    for result in results:
        payload = result.payload or {}

        matches.append(
            {
                "score": result.score,
                "chunk_id": payload.get("chunk_id"),
                "ticker": payload.get("ticker"),
                "company_name": payload.get("company_name"),
                "section": payload.get("section"),
                "filing_date": payload.get("filing_date"),
                "text": payload.get("text"),
            }
        )

    return matches
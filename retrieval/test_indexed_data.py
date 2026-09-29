from __future__ import annotations

from collections import Counter

from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)


def main():
    client = get_qdrant_client()

    # ---------------------------------------------------------
    # 1. Collection information
    # ---------------------------------------------------------

    collection = client.get_collection(
        collection_name=COLLECTION_NAME
    )

    print("Qdrant collection:")
    print(f"  Name: {COLLECTION_NAME}")
    print(f"  Points: {collection.points_count}")
    print()

    # ---------------------------------------------------------
    # 2. Read all payloads
    # ---------------------------------------------------------

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False,
    )

    ticker_counts = Counter()

    for point in points:
        payload = point.payload or {}

        ticker = payload.get("ticker")

        if ticker:
            ticker_counts[ticker] += 1

    print("Points by ticker:")

    for ticker, count in sorted(ticker_counts.items()):
        print(f"  {ticker}: {count}")

    print()

    # ---------------------------------------------------------
    # 3. Validation
    # ---------------------------------------------------------

    if collection.points_count != 168:
        raise AssertionError(
            f"Expected 168 points, "
            f"found {collection.points_count}"
        )

    expected_tickers = {
        "AAPL": 37,
        "MSFT": 63,
        "TSLA": 68,
    }

    if dict(ticker_counts) != expected_tickers:
        raise AssertionError(
            f"Unexpected ticker distribution: "
            f"{dict(ticker_counts)}"
        )

    print("Index verification PASSED.")


if __name__ == "__main__":
    main()
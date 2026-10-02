from retrieval.search import (
    build_search_query,
    search,
)


def main():
    query = "What are Apple's security risks?"

    enriched_query = build_search_query(
        query=query,
        section="cybersecurity",
    )

    print("=" * 80)
    print("QUERY ENRICHMENT TEST")
    print("=" * 80)

    print("Original query:")
    print(query)

    print()
    print("Enriched query:")
    print(enriched_query)

    print()
    print("Searching with production threshold: 0.65")

    results = search(
        query=query,
        ticker="AAPL",
        section="cybersecurity",
        limit=3,
        score_threshold=0.65,
    )

    print()
    print(f"Results returned: {len(results)}")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print()
        print(f"RESULT {index}")
        print(f"Score: {result['score']}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Section: {result['section']}")


if __name__ == "__main__":
    main()
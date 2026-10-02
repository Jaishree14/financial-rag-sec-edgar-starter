from retrieval.search import search


def main():
    query = "What are Apple's security risks?"

    print("=" * 80)
    print("CYBERSECURITY SEARCH TEST")
    print("=" * 80)
    print(f"Query: {query}")
    print("Ticker: AAPL")
    print("Section: cybersecurity")
    print()

    results = search(
        query=query,
        ticker="AAPL",
        section="cybersecurity",
        limit=3,
        score_threshold=0.0,
    )

    print(f"Results returned: {len(results)}")
    print()

    for index, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"RESULT {index}")
        print("=" * 80)
        print(f"Score: {result['score']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Ticker: {result['ticker']}")
        print(f"Section: {result['section']}")
        print()
        print(result["text"][:1000])
        print()


if __name__ == "__main__":
    main()
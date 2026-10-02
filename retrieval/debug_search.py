from retrieval.search import search


def main():
    query = "What are Microsoft's business strategies?"

    results = search(
        query=query,
        ticker="MSFT",
        section="business",
        limit=5,
        score_threshold=0.50,
    )

    print("=" * 80)
    print("RETRIEVAL DEBUG")
    print("=" * 80)
    print(f"Query: {query}")
    print("Ticker: MSFT")
    print("Section: business")
    print(f"Results returned: {len(results)}")
    print()

    for index, result in enumerate(results, start=1):

        print("=" * 80)
        print(f"RESULT {index}")
        print("=" * 80)

        print(f"Score: {result['score']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Section: {result['section']}")
        print()
        print(result["text"])
        print()


if __name__ == "__main__":
    main()
from retrieval.search import search


def main():
    query = "What are Apple's major business risks?"

    results = search(
    query=query,
    ticker="AAPL",
    section="risk_factors",
    limit=5,
    )

    print("=" * 80)
    print("TICKER + SECTION FILTERED SEARCH TEST")
    print("Section filter: risk_factors")
    print("=" * 80)
    print(f"Query: {query}")
    print("Ticker filter: AAPL")
    print(f"Results returned: {len(results)}")
    print()

    if not results:
        raise RuntimeError("No search results returned.")

    for index, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"RESULT {index}")
        print("=" * 80)

        print(f"Score: {result['score']}")
        print(f"Ticker: {result['ticker']}")
        print(f"Company: {result['company_name']}")
        print(f"Section: {result['section']}")
        print(f"Filing date: {result['filing_date']}")
        print(f"Chunk ID: {result['chunk_id']}")

        print()
        print("Text:")
        print(result["text"][:500])
        print()


if __name__ == "__main__":
    main()
from retrieval.search import search
from retrieval.reranker import rerank


def main():
    query = "What are Microsoft's business strategies?"

    # Retrieve a larger candidate pool.
    results = search(
        query=query,
        ticker="MSFT",
        section="business",
        limit=10,
        score_threshold=0.50,
    )

    print("=" * 80)
    print("RERANKING TEST")
    print("=" * 80)
    print(f"Query: {query}")
    print(f"Candidates retrieved: {len(results)}")
    print()

    reranked = rerank(
        query=query,
        results=results,
        limit=5,
    )

    for index, result in enumerate(
        reranked,
        start=1,
    ):
        print("=" * 80)
        print(f"RERANKED RESULT {index}")
        print("=" * 80)

        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Original score: {result['semantic_score']:.6f}")
        print(
            f"Keyword overlap: "
            f"{result['keyword_overlap']:.6f}"
        )
        print(
            f"Rerank score: "
            f"{result['rerank_score']:.6f}"
        )

        print()
        print(result["text"][:600])
        print()

    print("=" * 80)


if __name__ == "__main__":
    main()
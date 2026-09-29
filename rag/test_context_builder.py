from retrieval.search import search
from rag.context_builder import build_context


def main():
    query = "What are Apple's major business risks?"

    results = search(
        query=query,
        ticker="AAPL",
        section="risk_factors",
        limit=3,
        score_threshold=0.65,
    )

    if not results:
        raise RuntimeError(
            "No retrieval results were returned."
        )

    context = build_context(results)

    print("=" * 80)
    print("RAG CONTEXT TEST")
    print("=" * 80)

    print(f"Query: {query}")
    print(f"Retrieved chunks: {len(results)}")

    print()
    print(context)


if __name__ == "__main__":
    main()
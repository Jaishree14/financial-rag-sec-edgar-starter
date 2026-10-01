from retrieval.search import search
from rag.context_builder import build_context
from rag.llm import generate_answer


def main():
    question = "What are Apple's major business risks?"

    # 1. Retrieve relevant evidence
    results = search(
        query=question,
        ticker="AAPL",
        section="risk_factors",
        limit=3,
        score_threshold=0.65,
    )

    if not results:
        raise RuntimeError(
            "No relevant filing chunks were retrieved."
        )

    # 2. Build LLM context
    context = build_context(results)

    # 3. Generate grounded answer
    answer = generate_answer(
        question=question,
        context=context,
    )

    print("=" * 80)
    print("FIRST RAG ANSWER")
    print("=" * 80)
    print()
    print(f"Question: {question}")
    print()
    print("Answer:")
    print(answer)
    print()
    print("=" * 80)
    print("Retrieved sources")
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        print(
            f"[Source {index}] "
            f"{result['company_name']} | "
            f"{result['section']} | "
            f"{result['filing_date']} | "
            f"{result['chunk_id']}"
        )


if __name__ == "__main__":
    main()
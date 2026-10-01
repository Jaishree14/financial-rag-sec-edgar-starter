from retrieval.search import search
from rag.context_builder import build_context
from rag.llm import generate_answer


TEST_CASES = [
    {
        "name": "Apple Risk Factors",
        "ticker": "AAPL",
        "section": "risk_factors",
        "question": "What are Apple's major business risks?",
    },
    {
        "name": "Microsoft Risk Factors",
        "ticker": "MSFT",
        "section": "risk_factors",
        "question": "What are Microsoft's major business risks?",
    },
    {
        "name": "Tesla Cybersecurity",
        "ticker": "TSLA",
        "section": "cybersecurity",
        "question": "What cybersecurity risks and controls does Tesla discuss?",
    },
    {
        "name": "Unsupported Question",
        "ticker": "AAPL",
        "section": "cybersecurity",
        "question": "What was Apple's total revenue in 2025?",
    },
]


def run_case(case):
    print("=" * 80)
    print(case["name"])
    print("=" * 80)

    results = search(
        query=case["question"],
        ticker=case["ticker"],
        section=case["section"],
        limit=3,
        score_threshold=0.65,
    )

    print(f"Question: {case['question']}")
    print(f"Ticker: {case['ticker']}")
    print(f"Section: {case['section']}")
    print(f"Retrieved chunks: {len(results)}")
    print()

    if not results:
        print("No sufficiently relevant chunks found.")
        print()
        return

    context = build_context(results)

    answer = generate_answer(
        question=case["question"],
        context=context,
    )

    print("ANSWER:")
    print(answer)

    print()
    print("SOURCES:")
    for index, result in enumerate(results, start=1):
        print(
            f"[Source {index}] "
            f"{result['ticker']} | "
            f"{result['section']} | "
            f"{result['chunk_id']}"
        )

    print()


def main():
    for case in TEST_CASES:
        run_case(case)


if __name__ == "__main__":
    main()
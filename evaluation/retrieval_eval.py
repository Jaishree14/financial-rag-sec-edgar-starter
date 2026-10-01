from __future__ import annotations

from retrieval.search import search


TEST_CASES = [
    {
        "question": "What are Apple's major business risks?",
        "ticker": "AAPL",
        "section": "risk_factors",
    },
    {
        "question": "What are Microsoft's major business risks?",
        "ticker": "MSFT",
        "section": "risk_factors",
    },
    {
        "question": "What cybersecurity risks does Tesla discuss?",
        "ticker": "TSLA",
        "section": "cybersecurity",
    },
    {
        "question": "How does Microsoft describe its business?",
        "ticker": "MSFT",
        "section": "business",
    },
    {
        "question": "What financial risks does Tesla discuss?",
        "ticker": "TSLA",
        "section": "risk_factors",
    },
]


def evaluate_case(case: dict) -> dict:
    results = search(
        query=case["question"],
        ticker=case["ticker"],
        section=case["section"],
        limit=5,
        score_threshold=0.65,
    )

    correct_scope = all(
        result.get("ticker") == case["ticker"]
        and result.get("section") == case["section"]
        for result in results
    )

    return {
        "question": case["question"],
        "expected_ticker": case["ticker"],
        "expected_section": case["section"],
        "results": len(results),
        "correct_scope": correct_scope,
        "top_score": (
            results[0]["score"]
            if results
            else None
        ),
    }


def main():
    print("=" * 80)
    print("RETRIEVAL EVALUATION")
    print("=" * 80)
    print()

    evaluations = []

    for case in TEST_CASES:
        result = evaluate_case(case)
        evaluations.append(result)

        print(f"Question: {result['question']}")
        print(f"Expected ticker: {result['expected_ticker']}")
        print(f"Expected section: {result['expected_section']}")
        print(f"Results returned: {result['results']}")
        print(f"Top score: {result['top_score']}")
        print(f"Correct scope: {result['correct_scope']}")
        print("-" * 80)

    passed = sum(
        result["correct_scope"]
        for result in evaluations
    )

    total = len(evaluations)

    print()
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Cases passed: {passed}/{total}")
    print(
        f"Scope accuracy: "
        f"{(passed / total) * 100:.1f}%"
    )


if __name__ == "__main__":
    main()
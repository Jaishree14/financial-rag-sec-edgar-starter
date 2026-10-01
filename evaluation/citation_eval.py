from __future__ import annotations

import re

from rag.pipeline import run_rag


TEST_CASES = [
    {
        "name": "Apple Risk Factors",
        "question": "What are Apple's major business risks?",
        "ticker": "AAPL",
        "section": "risk_factors",
    },
    {
        "name": "Microsoft Risk Factors",
        "question": "What are Microsoft's major business risks?",
        "ticker": "MSFT",
        "section": "risk_factors",
    },
    {
        "name": "Tesla Cybersecurity",
        "question": "What cybersecurity risks and controls does Tesla discuss?",
        "ticker": "TSLA",
        "section": "cybersecurity",
    },
]


def extract_citations(answer: str) -> set[int]:
    """
    Extract citations such as:

        [Source 1]
        [Source 2, Source 3]

    Returns the source numbers found in the answer.
    """

    matches = re.findall(
        r"\[Source\s+(\d+)\]",
        answer,
        flags=re.IGNORECASE,
    )

    return {int(match) for match in matches}


def evaluate_case(case: dict) -> dict:
    answer, results = run_rag(
        question=case["question"],
        ticker=case["ticker"],
        section=case["section"],
        limit=3,
        score_threshold=0.65,
    )

    citations = extract_citations(answer)

    available_sources = set(
        range(1, len(results) + 1)
    )

    invalid_citations = citations - available_sources

    has_citation = bool(citations)

    citations_valid = (
        has_citation
        and not invalid_citations
    )

    return {
        "name": case["name"],
        "retrieved_sources": len(results),
        "citations_found": sorted(citations),
        "invalid_citations": sorted(invalid_citations),
        "citations_valid": citations_valid,
    }


def main():
    print("=" * 80)
    print("RAG CITATION EVALUATION")
    print("=" * 80)
    print()

    evaluations = []

    for case in TEST_CASES:
        result = evaluate_case(case)
        evaluations.append(result)

        print(f"Case: {result['name']}")
        print(
            f"Retrieved sources: "
            f"{result['retrieved_sources']}"
        )
        print(
            f"Citations found: "
            f"{result['citations_found']}"
        )
        print(
            f"Invalid citations: "
            f"{result['invalid_citations']}"
        )
        print(
            f"Citation validation: "
            f"{result['citations_valid']}"
        )
        print("-" * 80)

    passed = sum(
        result["citations_valid"]
        for result in evaluations
    )

    total = len(evaluations)

    print()
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Cases passed: {passed}/{total}")
    print(
        f"Citation validity: "
        f"{(passed / total) * 100:.1f}%"
    )


if __name__ == "__main__":
    main()
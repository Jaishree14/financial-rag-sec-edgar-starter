from rag.pipeline import run_rag


def main():
    print("=" * 80)
    print("RAG PIPELINE TEST")
    print("=" * 80)

    question = "What are Apple's major business risks?"

    answer, results = run_rag(
        question=question,
        ticker="AAPL",
        section="risk_factors",
        limit=3,
        score_threshold=0.65,
    )

    # ---------------------------------------------------------
    # Validate answer
    # ---------------------------------------------------------

    if not answer:
        raise AssertionError(
            "RAG pipeline returned an empty answer."
        )

    # ---------------------------------------------------------
    # Validate retrieved sources
    # ---------------------------------------------------------

    if not results:
        raise AssertionError(
            "RAG pipeline returned no sources."
        )

    # ---------------------------------------------------------
    # Validate source metadata
    # ---------------------------------------------------------

    for result in results:
        if result.get("ticker") != "AAPL":
            raise AssertionError(
                "Unexpected ticker in retrieved result."
            )

        if result.get("section") != "risk_factors":
            raise AssertionError(
                "Unexpected section in retrieved result."
            )

    print("Pipeline execution successful.")
    print(f"Question: {question}")
    print(f"Retrieved sources: {len(results)}")
    print()
    print("ANSWER:")
    print(answer)
    print()
    print("SOURCES:")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"[Source {index}] "
            f"{result['ticker']} | "
            f"{result['section']} | "
            f"{result['chunk_id']}"
        )

    print()
    print("RAG PIPELINE TEST PASSED.")


if __name__ == "__main__":
    main()
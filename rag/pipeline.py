from __future__ import annotations

from rag.context_builder import build_context
from rag.llm import generate_answer
from retrieval.search import search


def run_rag(
    question: str,
    ticker: str | None = None,
    section: str | None = None,
    limit: int = 3,
    score_threshold: float | None = 0.65,
) -> tuple[str, list[dict]]:
    """
    Execute the complete RAG pipeline.

    Returns:
        answer, retrieved source records
    """

    results = search(
        query=question,
        ticker=ticker,
        section=section,
        limit=limit,
        score_threshold=score_threshold,
    )

    if not results:
        return (
            "The available filing context is insufficient "
            "to answer this question.",
            [],
        )

    context = build_context(results)

    answer = generate_answer(
        question=question,
        context=context,
    )

    return answer, results
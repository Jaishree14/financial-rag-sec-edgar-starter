from __future__ import annotations

import re


STOP_WORDS = {
    "what",
    "are",
    "the",
    "a",
    "an",
    "is",
    "of",
    "to",
    "and",
    "or",
    "for",
    "in",
    "on",
    "does",
    "do",
    "how",
    "their",
    "its",
    "about",
}


def _tokenize(text: str) -> set[str]:
    """
    Convert text into normalized keyword tokens.
    """

    tokens = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower(),
    )

    return {
        token
        for token in tokens
        if token not in STOP_WORDS
    }


def rerank(
    query: str,
    results: list[dict],
    limit: int = 3,
) -> list[dict]:
    """
    Rerank retrieved results using a combination of:

    1. Original semantic similarity score.
    2. Keyword overlap between the query and chunk.

    This is a lightweight second-stage reranker.
    """

    if not results:
        return []

    if limit <= 0:
        raise ValueError(
            "limit must be greater than 0."
        )

    query_terms = _tokenize(query)

    scored_results = []

    for result in results:

        text = result.get("text") or ""

        chunk_terms = _tokenize(text)

        if query_terms:
            overlap = (
                len(query_terms & chunk_terms)
                / len(query_terms)
            )
        else:
            overlap = 0.0

        semantic_score = float(
            result.get("score") or 0.0
        )

        # Semantic similarity remains the dominant signal.
        # Keyword overlap provides a secondary signal.
        combined_score = (
            0.80 * semantic_score
            + 0.20 * overlap
        )

        reranked = dict(result)

        reranked["semantic_score"] = semantic_score
        reranked["keyword_overlap"] = overlap
        reranked["rerank_score"] = combined_score

        scored_results.append(reranked)

    scored_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return scored_results[:limit]
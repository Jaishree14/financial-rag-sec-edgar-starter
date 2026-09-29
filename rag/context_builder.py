from __future__ import annotations


def build_context(
    results: list[dict],
) -> str:
    """
    Build a structured context block from retrieved chunks.

    Each retrieved chunk keeps its source information so the
    eventual LLM response can be traced back to the filing.
    """

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""SOURCE {index}
Company: {result.get("company_name")}
Ticker: {result.get("ticker")}
Form: 10-K
Filing Date: {result.get("filing_date")}
Section: {result.get("section")}
Chunk ID: {result.get("chunk_id")}
Similarity Score: {result.get("score")}

CONTENT:
{result.get("text", "")}
"""
        )

    return "\n" + "\n".join(context_parts)
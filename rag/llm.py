from __future__ import annotations

import json
import os

import requests


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://ollama:11434",
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama3.1:8b",
)

LLM_TIMEOUT_SECONDS = int(
    os.getenv(
        "LLM_TIMEOUT_SECONDS",
        "600",
    )
)

LLM_CONTEXT_SIZE = int(
    os.getenv(
        "LLM_CONTEXT_SIZE",
        "4096",
    )
)

LLM_MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "LLM_MAX_OUTPUT_TOKENS",
        "400",
    )
)


SYSTEM_PROMPT = """
You are a financial document question-answering assistant.

Answer the user's question using ONLY the SEC filing
context provided to you.

Rules:

1. Use only information explicitly supported by the
   provided filing context.

2. Do not invent facts, numbers, risks, dates, causes,
   or conclusions.

3. Treat each SOURCE as evidence from the filing.
   A source may begin or end in the middle of a sentence
   because the filing was chunked.

4. Do not interpret a sentence fragment as a standalone
   risk or standalone fact.

5. Combine information from multiple sources when necessary.

6. Every factual statement must have an inline citation
   such as [Source 1], [Source 2], or [Source 3].

7. Place the citation immediately after the statement
   it supports.

8. Do not cite a source unless that source actually
   supports the statement.

9. If the supplied context does not contain enough
   information to answer the question, say:
   "The available filing context is insufficient to answer
   this question."

10. Do not use outside knowledge.

11. Prefer a concise answer with clear categories rather
    than repeating long passages from the filing.

12. Answer only the question that was asked.
    Do not introduce additional topics, categories, or
    sections unless they are necessary to directly answer
    the question.

13. If the retrieved context contains related but
    unrequested information, ignore it.
    For example, when asked about business strategies,
    do not add a separate discussion of risks unless
    the question explicitly asks about risks.
"""


def generate_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate a grounded answer using Ollama.

    Streaming is used so the client can receive partial
    output instead of waiting for the complete response.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question must not be empty."
        )

    if not context or not context.strip():
        raise ValueError(
            "Context must not be empty."
        )

    payload = {
        "model": LLM_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": (
            f"SEC FILING CONTEXT:\n\n"
            f"{context}\n\n"
            f"USER QUESTION:\n"
            f"{question}\n\n"
            "Answer the user's specific question directly and concisely.\n"
            "Ignore information in the context that is not relevant to "
            "the question.\n\n"
            "Every factual statement must include an inline citation "
            "such as [Source 1], [Source 2], or [Source 3].\n\n"
            "For example:\n"
            "- Relevant point: explanation [Source 1]\n"
            "- Relevant point: explanation [Source 2]\n\n"
            "ANSWER:"
        ),
        "stream": True,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.1,
            "num_ctx": LLM_CONTEXT_SIZE,
            "num_predict": LLM_MAX_OUTPUT_TOKENS,
        },
    }

    url = f"{OLLAMA_BASE_URL}/api/generate"

    try:
        with requests.post(
            url,
            json=payload,
            stream=True,
            timeout=(
                10,
                LLM_TIMEOUT_SECONDS,
            ),
        ) as response:

            response.raise_for_status()

            output_parts: list[str] = []

            for line in response.iter_lines(
                decode_unicode=True
            ):
                if not line:
                    continue

                data = json.loads(line)

                response_text = data.get(
                    "response",
                    "",
                )

                if response_text:
                    output_parts.append(
                        response_text
                    )

                if data.get("done"):
                    break

            answer = "".join(
                output_parts
            ).strip()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Ollama generation request failed: {exc}"
        ) from exc

    if not answer:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return answer
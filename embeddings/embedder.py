from __future__ import annotations

import os

import requests


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://ollama:11434",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text",
)


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding vector for a single text string.
    """

    if not text or not text.strip():
        raise ValueError("Text must not be empty.")

    url = f"{OLLAMA_BASE_URL}/api/embed"

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise ValueError("Ollama returned no embeddings.")

    return embeddings[0]
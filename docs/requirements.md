# Requirements

## Problem statement
Build a financial document intelligence system that lets users ask natural-language questions about SEC EDGAR 10-K filings and receive grounded answers with source attribution.

## Goals
1. Automate SEC filing acquisition.
2. Parse, clean, section-aware chunk, and enrich filings with metadata.
3. Generate embeddings and store them in Qdrant.
4. Retrieve relevant evidence for user questions.
5. Generate grounded answers with a local Ollama model by default, with optional OpenAI support.
6. Provide a FastAPI interface.
7. Add evaluation, testing, logging, and Docker-based reproducibility.

## Functional requirements
- FR-01 Filing acquisition from SEC EDGAR.
- FR-02 Document parsing and cleaning.
- FR-03 Section-aware chunking with metadata.
- FR-04 Embedding generation.
- FR-05 Vector indexing and semantic retrieval.
- FR-06 RAG answer generation.
- FR-07 Source attribution.
- FR-08 API endpoint for question answering.
- FR-09 Evaluation dataset and metrics.

## Non-functional requirements
- Configurable provider/model selection.
- SEC-compliant User-Agent and request throttling.
- Resilient handling of transient external-service failures.
- No hard-coded secrets.
- Reproducible local execution with Docker Compose.
- Tests for core components.

## Initial scope
Companies: AAPL, MSFT, TSLA
Filing type: 10-K
GenAI default: Ollama/local model
Vector store: Qdrant
API: FastAPI

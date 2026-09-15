# Financial RAG — SEC EDGAR

A production-oriented Retrieval-Augmented Generation (RAG) system for querying SEC EDGAR 10-K filings with source-grounded answers.

## Planned stack
- Python
- FastAPI
- Qdrant
- Ollama (local GenAI)
- Optional OpenAI provider
- Docker / Docker Compose

## Repository status
Scaffold created. Implementation will be added incrementally, starting with SEC EDGAR ingestion.

## Quick start
```bash
docker compose up --build
```

See `docs/` for project requirements and architecture.

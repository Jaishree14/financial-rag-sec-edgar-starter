# Architecture

## High-level flow

```text
SEC EDGAR
   |
   v
Ingestion -> Raw HTML + Metadata
   |
   v
Processing -> Clean text -> Sections -> Chunks
   |
   v
Embeddings
   |
   v
Qdrant Vector Database
   ^
   |
User -> FastAPI -> Query Embedding -> Retrieval -> Prompt -> Ollama/OpenAI -> Answer + Sources
```

## Containers
- `api`: FastAPI application and RAG orchestration.
- `qdrant`: vector database.
- `ollama`: local LLM runtime.

## Future components
Add PostgreSQL, background workers, orchestration, monitoring, or a frontend only when an actual requirement justifies them.

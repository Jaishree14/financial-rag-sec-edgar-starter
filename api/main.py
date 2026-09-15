from fastapi import FastAPI

app = FastAPI(title="Financial RAG - SEC EDGAR", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

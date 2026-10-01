from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="Financial RAG API",
    description=(
        "SEC EDGAR financial document RAG system."
    ),
    version="1.0.0",
)

app.include_router(router)
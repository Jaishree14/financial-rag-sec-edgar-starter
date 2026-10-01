from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


app = FastAPI(
    title="Financial RAG API",
    description="SEC EDGAR financial document RAG system.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------
# Allow the local frontend (opened from the filesystem)
# to communicate with the FastAPI backend.
#
# This is suitable for local development.
# For production, restrict this to the actual frontend
# origin instead of using "*".
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
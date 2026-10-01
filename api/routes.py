from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from rag.pipeline import run_rag
from sqlalchemy import select
from api.schemas import (
    FilingInfo,
    QueryRequest,
    QueryResponse,
    Source,
)
from storage.database import SessionLocal
from storage.models import Filing

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def root():
    return {
        "name": "Financial RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "filings": "/filings",
        "query": "/query",
    }

@router.get("/health")
def health():
    return {
        "status": "ok"
    }

@router.get(
    "/filings",
    response_model=list[FilingInfo],
)
def filings():
    """
    Return the filings currently available to the RAG system.
    """

    session = SessionLocal()

    try:
        statement = (
            select(Filing)
            .where(Filing.status == "downloaded")
            .order_by(Filing.ticker)
        )

        records = session.scalars(statement).all()

        response = []

        for filing in records:
            response.append(
                FilingInfo(
                    ticker=filing.ticker,
                    company_name=filing.company_name,
                    filing_date=str(filing.filing_date),
                    form_type=filing.form_type,
                    sections=[
                        "business",
                        "risk_factors",
                        "cybersecurity",
                        "management_discussion",
                    ],
                )
            )

        return response

    finally:
        session.close()

@router.post(
    "/query",
    response_model=QueryResponse,
)
def query(request: QueryRequest):
    """
    Execute the complete RAG pipeline.
    """

    try:
        answer, results = run_rag(
            question=request.question,
            ticker=request.ticker,
            section=request.section,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

        sources = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            sources.append(
                Source(
                    source_number=index,
                    ticker=result.get("ticker"),
                    company_name=result.get("company_name"),
                    section=result.get("section"),
                    filing_date=result.get("filing_date"),
                    chunk_id=result.get("chunk_id"),
                    score=result.get("score"),
                )
            )

        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources,
        )

    except RuntimeError as exc:
        # Log the technical error internally.
        logger.exception(
            "RAG service failure: %s",
            exc,
        )

        # Return a safe message to the API client.
        raise HTTPException(
            status_code=503,
            detail=(
                "The RAG generation service is temporarily "
                "unavailable. Please try again."
            ),
        ) from exc

    except Exception as exc:
        # Log unexpected errors internally.
        logger.exception(
            "Unexpected error while processing query: %s",
            exc,
        )

        # Do not expose internal implementation details.
        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred while processing "
                "the request."
            ),
        ) from exc
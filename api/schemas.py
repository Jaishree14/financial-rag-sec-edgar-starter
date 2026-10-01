from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SectionName = Literal[
    "business",
    "risk_factors",
    "cybersecurity",
    "management_discussion",
]


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural-language question.",
    )

    ticker: str | None = Field(
        default=None,
        min_length=1,
        description="Optional ticker such as AAPL, MSFT, or TSLA.",
    )

    section: SectionName | None = Field(
        default=None,
        description=(
            "Optional section: business, risk_factors, "
            "cybersecurity, or management_discussion."
        ),
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of retrieved chunks.",
    )

    score_threshold: float | None = Field(
        default=0.65,
        ge=-1.0,
        le=1.0,
        description="Minimum semantic similarity score.",
    )


class Source(BaseModel):
    source_number: int
    ticker: str | None
    company_name: str | None
    section: str | None
    filing_date: str | None
    chunk_id: str | None
    score: float | None


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]

class FilingInfo(BaseModel):
    ticker: str
    company_name: str
    filing_date: str
    form_type: str
    sections: list[str]
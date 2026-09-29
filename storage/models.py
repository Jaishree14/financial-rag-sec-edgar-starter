from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


class Filing(Base):
    __tablename__ = "filings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    cik: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    form_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    filing_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    accession_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    filing_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    local_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="discovered",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
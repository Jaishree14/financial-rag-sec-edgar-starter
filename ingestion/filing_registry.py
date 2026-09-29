from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ingestion.edgar_downloader import Filing
from storage.models import Filing as FilingModel


class FilingRegistry:
    """Manage SEC filing records in PostgreSQL."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_accession(
        self,
        accession_number: str,
    ) -> FilingModel | None:
        statement = select(FilingModel).where(
            FilingModel.accession_number == accession_number
        )

        return self.session.scalar(statement)

    def register(
        self,
        filing: Filing,
    ) -> FilingModel:

        existing = self.get_by_accession(
            filing.accession_number
        )

        if existing is not None:
            return existing

        db_filing = FilingModel(
            ticker=filing.ticker,
            company_name=filing.company,
            cik=filing.cik,
            form_type=filing.form_type,
            filing_date=date.fromisoformat(filing.filing_date),
            accession_number=filing.accession_number,
            filename=filing.filename,
            filing_url=filing.filing_url,
            status="discovered",
        )

        self.session.add(db_filing)
        self.session.commit()
        self.session.refresh(db_filing)

        return db_filing

    def update_status(
            self,
            accession_number: str,
            status: str,
            local_path: str | None = None,
        ) -> FilingModel | None:

        filing = self.get_by_accession(accession_number)

        if filing is None:
            return None

        filing.status = status

        if local_path is not None:
            filing.local_path = local_path

        self.session.commit()
        self.session.refresh(filing)

        return filing
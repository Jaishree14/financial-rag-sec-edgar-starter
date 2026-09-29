"""Entry point for Stage 1 SEC ingestion."""

from __future__ import annotations

import logging

from ingestion.edgar_downloader import (
    download_filing,
    get_latest_10k,
)
from ingestion.filing_registry import FilingRegistry
from storage.database import SessionLocal


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


TARGETS = [
    "AAPL",
    "MSFT",
    "TSLA",
]


def ingest_ticker(ticker: str) -> None:
    """Discover, register, download, and update one company's latest 10-K."""

    logger.info("Starting ingestion for %s", ticker)

    filing = get_latest_10k(ticker)

    if filing is None:
        logger.warning("No 10-K found for %s", ticker)
        return

    session = SessionLocal()

    try:
        registry = FilingRegistry(session)

        # Register the filing if it does not already exist.
        db_filing = registry.register(filing)

        logger.info(
            "Filing registered: id=%s accession=%s",
            db_filing.id,
            db_filing.accession_number,
        )

        # Download the filing.
        local_path = download_filing(filing)

        # Update PostgreSQL after successful download.
        registry.update_status(
            accession_number=filing.accession_number,
            status="downloaded",
            local_path=str(local_path),
        )

        logger.info(
            "Ingestion completed: ticker=%s status=downloaded",
            ticker,
        )

    except Exception:
        session.rollback()

        logger.exception(
            "Ingestion failed for %s",
            ticker,
        )

        raise

    finally:
        session.close()


def main() -> None:
    """Run the ingestion pipeline."""

    for ticker in TARGETS:
        ingest_ticker(ticker)


if __name__ == "__main__":
    main()
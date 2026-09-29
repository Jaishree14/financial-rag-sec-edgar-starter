from sqlalchemy import select

from ingestion.edgar_downloader import get_latest_10k
from ingestion.filing_registry import FilingRegistry
from storage.database import SessionLocal
from storage.models import Filing


def main() -> None:
    filing = get_latest_10k("AAPL")

    if filing is None:
        raise RuntimeError("No AAPL 10-K found.")

    session = SessionLocal()

    try:
        registry = FilingRegistry(session)

        db_filing = registry.register(filing)

        print("Filing registered successfully:")
        print(f"ID:                 {db_filing.id}")
        print(f"Ticker:              {db_filing.ticker}")
        print(f"Company:             {db_filing.company_name}")
        print(f"Form:                {db_filing.form_type}")
        print(f"Filing date:         {db_filing.filing_date}")
        print(f"Accession number:    {db_filing.accession_number}")
        print(f"Status:              {db_filing.status}")

        # Verify it can be read back from PostgreSQL.
        saved = session.scalar(
            select(Filing).where(
                Filing.accession_number
                == filing.accession_number
            )
        )

        if saved is None:
            raise RuntimeError(
                "Filing was not found after insertion."
            )

        print("\nPostgreSQL verification successful.")

    finally:
        session.close()


if __name__ == "__main__":
    main()
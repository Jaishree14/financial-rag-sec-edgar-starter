from ingestion.edgar_downloader import (
    download_filing,
    get_latest_10k,
)
from ingestion.filing_registry import FilingRegistry
from storage.database import SessionLocal


def main() -> None:
    filing = get_latest_10k("AAPL")

    if filing is None:
        raise RuntimeError("No AAPL 10-K found.")

    session = SessionLocal()

    try:
        registry = FilingRegistry(session)

        # Make sure the filing exists in PostgreSQL.
        db_filing = registry.get_by_accession(
            filing.accession_number
        )

        if db_filing is None:
            raise RuntimeError(
                "Filing does not exist in PostgreSQL."
            )

        # Download the filing.
        local_path = download_filing(filing)

        # Update PostgreSQL.
        updated = registry.update_status(
            accession_number=filing.accession_number,
            status="downloaded",
            local_path=str(local_path),
        )

        if updated is None:
            raise RuntimeError(
                "Could not update filing status."
            )

        print("Filing download + database update successful:")
        print(f"ID:          {updated.id}")
        print(f"Ticker:      {updated.ticker}")
        print(f"Status:      {updated.status}")
        print(f"Local path:  {updated.local_path}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
from sqlalchemy import select

from storage.database import SessionLocal
from storage.models import Filing


def main():
    session = SessionLocal()

    try:
        statement = (
            select(Filing)
            .where(Filing.status == "downloaded")
            .order_by(Filing.ticker)
        )

        filings = session.scalars(statement).all()

        print("Downloaded filings found:", len(filings))
        print()

        for filing in filings:
            print("=" * 80)
            print(f"Ticker: {filing.ticker}")
            print(f"Company: {filing.company_name}")
            print(f"Form: {filing.form_type}")
            print(f"Filing date: {filing.filing_date}")
            print(f"Accession: {filing.accession_number}")
            print(f"Local path: {filing.local_path}")
            print(f"Status: {filing.status}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
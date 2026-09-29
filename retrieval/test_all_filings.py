from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from storage.database import SessionLocal
from storage.models import Filing

from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections
from processing.chunker import create_chunks


def main():
    session = SessionLocal()

    try:
        statement = (
            select(Filing)
            .where(Filing.status == "downloaded")
            .order_by(Filing.ticker)
        )

        filings = session.scalars(statement).all()

        print(f"Found {len(filings)} downloaded filings.")
        print()

        for filing in filings:
            print("=" * 80)
            print(f"{filing.ticker} - {filing.company_name}")
            print("=" * 80)

            if not filing.local_path:
                raise ValueError(
                    f"No local_path found for {filing.ticker}"
                )

            file_path = Path(filing.local_path)

            if not file_path.exists():
                raise FileNotFoundError(
                    f"File does not exist: {file_path}"
                )

            print(f"Reading: {file_path}")

            # Parse HTML
            text = parse_html_to_text(file_path)

            print(f"Parsed characters: {len(text):,}")

            # Extract sections
            sections = extract_major_sections(text)

            total_chunks = 0

            for section_name, section_text in sections.items():
                chunks = create_chunks(
                    text=section_text,
                    ticker=filing.ticker,
                    company_name=filing.company_name,
                    accession_number=filing.accession_number,
                    filing_date=str(filing.filing_date),
                    form_type=filing.form_type,
                    section=section_name,
                    source_path=str(file_path),
                    chunk_size=500,
                    overlap=75,
                )

                print(
                    f"{section_name:22} "
                    f"{len(section_text):>8,} chars  "
                    f"{len(chunks):>4} chunks"
                )

                total_chunks += len(chunks)

            print("-" * 80)
            print(f"Total chunks: {total_chunks}")
            print()

    finally:
        session.close()


if __name__ == "__main__":
    main()
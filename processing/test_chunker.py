from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections
from processing.chunker import create_chunks


FILE_PATH = "data/raw/Apple_Inc./2025-10-31_10-K.html"


def main():
    text = parse_html_to_text(FILE_PATH)

    sections = extract_major_sections(text)

    risk_factors = sections["risk_factors"]

    chunks = create_chunks(
        text=risk_factors,
        ticker="AAPL",
        company_name="Apple Inc.",
        accession_number="0000320193-25-000079",
        filing_date="2025-10-31",
        form_type="10-K",
        section="risk_factors",
        source_path=FILE_PATH,
        chunk_size=500,
        overlap=75,
    )

    print("Chunk metadata creation successful.")
    print(f"Total chunks: {len(chunks)}")
    print()

    first = chunks[0]

    print("=" * 80)
    print("FIRST CHUNK METADATA")
    print("=" * 80)

    print(f"chunk_id: {first.chunk_id}")
    print(f"ticker: {first.ticker}")
    print(f"company_name: {first.company_name}")
    print(f"accession_number: {first.accession_number}")
    print(f"filing_date: {first.filing_date}")
    print(f"form_type: {first.form_type}")
    print(f"section: {first.section}")
    print(f"chunk_index: {first.chunk_index}")
    print(f"total_chunks: {first.total_chunks}")
    print(f"word_count: {first.word_count}")
    print(f"source_path: {first.source_path}")

    print()
    print("TEXT PREVIEW")
    print("=" * 80)
    print(first.text[:500])


if __name__ == "__main__":
    main()
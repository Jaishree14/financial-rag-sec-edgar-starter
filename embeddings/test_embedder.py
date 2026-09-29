from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections
from processing.chunker import create_chunks
from embeddings.embedder import embed_text


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

    first_chunk = chunks[0]

    vector = embed_text(first_chunk.text)

    print("Embedding generation successful.")
    print()
    print(f"Chunk ID: {first_chunk.chunk_id}")
    print(f"Chunk word count: {first_chunk.word_count}")
    print(f"Embedding dimensions: {len(vector)}")
    print()
    print("First 10 embedding values:")
    print(vector[:10])


if __name__ == "__main__":
    main()
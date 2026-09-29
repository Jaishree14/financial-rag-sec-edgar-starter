from ingestion.edgar_downloader import (
    download_filing,
    get_latest_10k,
)


def main() -> None:
    filing = get_latest_10k("AAPL")

    if filing is None:
        raise RuntimeError("No AAPL 10-K found.")

    print("Downloading filing:")
    print(f"Company: {filing.company}")
    print(f"Form: {filing.form_type}")
    print(f"Date: {filing.filing_date}")
    print(f"Accession: {filing.accession_number}")

    path = download_filing(filing)

    print("\nDownload successful:")
    print(path)


if __name__ == "__main__":
    main()
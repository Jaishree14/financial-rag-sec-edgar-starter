from ingestion.edgar_downloader import get_latest_10k


def main() -> None:
    filing = get_latest_10k("AAPL")

    if filing is None:
        print("No 10-K filing found.")
        return

    print("\nSEC filing discovered:")
    print(f"Company:           {filing.company}")
    print(f"Ticker:            {filing.ticker}")
    print(f"CIK:               {filing.cik}")
    print(f"Form:              {filing.form_type}")
    print(f"Filing date:       {filing.filing_date}")
    print(f"Accession number:  {filing.accession_number}")
    print(f"Filename:          {filing.filename}")
    print(f"SEC URL:           {filing.filing_url}")


if __name__ == "__main__":
    main()
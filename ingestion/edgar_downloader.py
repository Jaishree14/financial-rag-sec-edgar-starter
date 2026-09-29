"""SEC EDGAR filing downloader.

Stage 1 of the Financial RAG ingestion pipeline.

Responsibilities:
- Resolve ticker symbols to SEC CIKs.
- Search EDGAR Full-Text Search for filings.
- Build archive URLs.
- Download filing HTML.
- Save filing metadata.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions"

DATA_DIR = Path(os.getenv("DATA_DIR", "data/raw"))

REQUEST_DELAY_SECONDS = float(
    os.getenv("SEC_REQUEST_DELAY_SECONDS", "0.3")
)

REQUEST_TIMEOUT_SECONDS = int(
    os.getenv("SEC_REQUEST_TIMEOUT_SECONDS", "30")
)

MAX_RETRIES = int(
    os.getenv("SEC_MAX_RETRIES", "3")
)

SEC_USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "Financial RAG Project contact@example.com",
)

HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Filing:
    """Metadata representing one SEC filing."""

    company: str
    ticker: str
    cik: str
    form_type: str
    filing_date: str
    accession_number: str
    filename: str
    filing_url: str


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(
    url: str,
    params: dict[str, Any] | None = None,
) -> requests.Response:
    """GET a URL with retry and basic backoff handling."""

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            # Retry transient server/rate-limit responses.
            if response.status_code in {429, 500, 502, 503, 504}:
                retry_delay = 2 ** (attempt - 1)

                logger.warning(
                    "SEC request returned %s. Retrying in %ss...",
                    response.status_code,
                    retry_delay,
                )

                time.sleep(retry_delay)
                continue

            response.raise_for_status()
            return response

        except requests.RequestException as exc:
            last_error = exc

            if attempt == MAX_RETRIES:
                break

            retry_delay = 2 ** (attempt - 1)

            logger.warning(
                "SEC request failed (%s). Retrying in %ss...",
                exc,
                retry_delay,
            )

            time.sleep(retry_delay)

    raise RuntimeError(
        f"SEC request failed after {MAX_RETRIES} attempts: {url}"
    ) from last_error


def _respect_rate_limit() -> None:
    """Pause between SEC requests."""

    time.sleep(REQUEST_DELAY_SECONDS)


# ---------------------------------------------------------------------------
# Ticker / CIK resolution
# ---------------------------------------------------------------------------

def resolve_ticker(ticker: str) -> tuple[str, str]:
    """Resolve ticker to (CIK, company name) using SEC's ticker mapping."""

    ticker = ticker.upper().strip()

    response = _get(SEC_COMPANY_TICKERS_URL)
    data = response.json()

    _respect_rate_limit()

    for record in data.values():
        if str(record.get("ticker", "")).upper() == ticker:
            cik = str(record["cik_str"]).zfill(10)
            company = record["title"]

            logger.info(
                "Resolved %s -> CIK %s (%s)",
                ticker,
                cik,
                company,
            )

            return cik, company

    raise ValueError(f"Ticker not found in SEC company mapping: {ticker}")


# ---------------------------------------------------------------------------
# Filing History
# ---------------------------------------------------------------------------
def get_latest_10k(ticker: str) -> Filing | None:
    """Get the latest 10-K filing for a company."""

    cik, company = resolve_ticker(ticker)

    url = f"{SEC_SUBMISSIONS_URL}/CIK{cik}.json"

    logger.info(
        "Fetching filing history for %s (CIK %s)",
        ticker,
        cik,
    )

    response = _get(url)
    _respect_rate_limit()

    data = response.json()
    recent = data.get("filings", {}).get("recent", {})

    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_documents = recent.get("primaryDocument", [])

    for i, form in enumerate(forms):

        if form != "10-K":
            continue

        accession_number = accession_numbers[i]
        filename = primary_documents[i]
        filing_date = filing_dates[i]

        filing_url = build_filing_url(
            cik=cik,
            accession_number=accession_number,
            filename=filename,
        )

        return Filing(
            company=company,
            ticker=ticker,
            cik=cik,
            form_type=form,
            filing_date=filing_date,
            accession_number=accession_number,
            filename=filename,
            filing_url=filing_url,
        )

    return None


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_filings(
    ticker: str,
    forms: str = "10-K",
    date_from: str | None = None,
    date_to: str | None = None,
    max_results: int = 2,
) -> list[Filing]:
    """Search SEC EDGAR Full-Text Search for filings."""

    cik, company = resolve_ticker(ticker)

    results: list[Filing] = []
    start = 0

    while len(results) < max_results:

        params: dict[str, Any] = {
            "q": "*",
            "forms": forms,
            "ciks": cik,
            "from": start,
        }

        if date_from and date_to:
            params.update(
                {
                    "dateRange": "custom",
                    "startdt": date_from,
                    "enddt": date_to,
                }
            )

        logger.info(
            "Searching EDGAR: ticker=%s, form=%s, from=%s",
            ticker,
            forms,
            start,
        )

        response = _get(
            SEC_SEARCH_URL,
            params=params,
        )

        _respect_rate_limit()

        data = response.json()

        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            break

        for hit in hits:
            source = hit.get("_source", {})

            accession_and_file = hit.get("_id")

            if not accession_and_file:
                logger.warning("Skipping result without filing ID.")
                continue

            try:
                accession_number, filename = accession_and_file.split(":", 1)
            except ValueError:
                logger.warning(
                    "Skipping malformed filing ID: %s",
                    accession_and_file,
                )
                continue

            filing_cik = str(
                source.get("ciks", [cik])[0]
            ).zfill(10)

            form_type = source.get(
                "root_forms",
                [forms],
            )[0]

            filing_date = source.get(
                "file_date",
                "unknown",
            )

            filing_url = build_filing_url(
                cik=filing_cik,
                accession_number=accession_number,
                filename=filename,
            )

            results.append(
                Filing(
                    company=company,
                    ticker=ticker,
                    cik=filing_cik,
                    form_type=form_type,
                    filing_date=filing_date,
                    accession_number=accession_number,
                    filename=filename,
                    filing_url=filing_url,
                )
            )

            if len(results) >= max_results:
                break

        start += len(hits)

        if len(hits) < 10:
            break

    return results[:max_results]


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

def build_filing_url(
    cik: str,
    accession_number: str,
    filename: str,
) -> str:
    """Build the SEC archive URL for a filing."""

    cik_path = str(int(cik))
    accession_path = accession_number.replace("-", "")

    return (
        f"{SEC_ARCHIVES_BASE}/"
        f"{cik_path}/"
        f"{accession_path}/"
        f"{filename}"
    )


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def _safe_company_name(company: str) -> str:
    """Convert company name into a filesystem-friendly directory name."""

    cleaned = company.replace(",", "").replace("/", "_")
    return "_".join(cleaned.split())


def download_filing(filing: Filing) -> Path:
    """Download one filing and save HTML + metadata."""

    company_dir = DATA_DIR / _safe_company_name(filing.company)
    company_dir.mkdir(parents=True, exist_ok=True)

    html_path = (
        company_dir
        / f"{filing.filing_date}_{filing.form_type}.html"
    )

    metadata_path = (
        company_dir
        / f"{filing.filing_date}_{filing.form_type}.json"
    )

    # Idempotency: don't redownload an existing filing.
    if html_path.exists() and metadata_path.exists():
        logger.info(
            "Filing already exists. Skipping: %s",
            html_path,
        )
        return html_path

    logger.info(
        "Downloading %s",
        filing.filing_url,
    )

    response = _get(filing.filing_url)

    html_path.write_text(
        response.text,
        encoding="utf-8",
    )

    metadata_path.write_text(
        json.dumps(
            asdict(filing),
            indent=2,
        ),
        encoding="utf-8",
    )

    _respect_rate_limit()

    logger.info(
        "Saved filing: %s",
        html_path,
    )

    return html_path

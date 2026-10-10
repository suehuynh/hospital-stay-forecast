"""Download the SPARCS 2024 inpatient discharges from the NY Health Data API.

Usage:
    python -m src.download           # download (resumes if interrupted)
    python -m src.download --force   # delete saved parts and start over

The ~2.2M rows are fetched PAGE_SIZE rows at a time, ordered by the built-in
row id ``:id`` so pages are stable and never overlap or skip rows. Each page
is saved as its own parquet file (``data/raw/sparcs_2024/part-00000.parquet``,
...), so a crash only loses the page in progress. A ``_SUCCESS`` marker is
written once the last page has been fetched.

If ``APP_TOKEN`` is set in the ``.env`` file at the repo root, it is sent as
the ``X-App-Token`` header to avoid throttling. Without it the requests still
work, just more slowly.
"""

import argparse
import os
import shutil

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import BASE_URL, PAGE_SIZE, RAW_COLUMNS, RAW_DIR, ROOT

load_dotenv(ROOT / ".env")
_app_token = os.environ.get("APP_TOKEN")
HEADERS = {"X-App-Token": _app_token} if _app_token else {}

SUCCESS_MARKER = RAW_DIR / "_SUCCESS"


def fetch_page(offset):
    payload = {"$limit": PAGE_SIZE, "$offset": offset, "$order": ":id"}
    resp = requests.get(BASE_URL, params=payload, timeout=120, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def fetch_row_count():
    """Total number of rows according to the API."""
    resp = requests.get(BASE_URL, params={"$select": "count(*)"}, timeout=60, headers=HEADERS)
    resp.raise_for_status()
    return int(resp.json()[0]["count"])


def part_path(page_number):
    return RAW_DIR / f"part-{page_number:05d}.parquet"


def download(force=False):
    """Fetch every page from the API into RAW_DIR, skipping pages already saved."""
    if force and RAW_DIR.exists():
        shutil.rmtree(RAW_DIR)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if SUCCESS_MARKER.exists():
        print(f"Raw data already complete in {RAW_DIR}")
        return

    page_number = 0
    while True:
        path = part_path(page_number)
        if path.exists():
            page_number += 1
            continue

        offset = page_number * PAGE_SIZE
        page = fetch_page(offset)
        if not page:  # an empty page means we have gone past the last row
            break

        # Keep every field as a string here; type conversion happens in src.clean.
        df = pd.DataFrame(page).reindex(columns=RAW_COLUMNS).astype("string")
        df.to_parquet(path, index=False)
        print(f"saved rows {offset:,} to {offset + len(df):,} -> {path.name}")

        if len(page) < PAGE_SIZE:  # a short page is the last one
            break
        page_number += 1

    SUCCESS_MARKER.touch()
    print(f"Download complete: {RAW_DIR}")


def load_raw(columns=None):
    """Read the raw parts as one DataFrame (all columns are strings)."""
    if not SUCCESS_MARKER.exists():
        raise FileNotFoundError(
            f"Raw data not found or incomplete in {RAW_DIR}. Run `python -m src.download` first."
        )
    return pd.read_parquet(RAW_DIR, columns=columns)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="delete saved parts and re-download")
    args = parser.parse_args()

    download(force=args.force)

    n_local = len(load_raw(columns=["length_of_stay"]))
    n_api = fetch_row_count()
    if n_local == n_api:
        print(f"Row count matches the API: {n_local:,} rows")
    else:
        print(f"WARNING: row count mismatch. API has {n_api:,} rows, local copy has {n_local:,}")


if __name__ == "__main__":
    main()

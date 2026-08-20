"""CSV Ingestion Helper Script for Earnings Estimates.

Usage:
  python scripts/ingest_earnings_estimates.py path/to/estimates.csv

Expected CSV Header:
  symbol,fiscal_period,estimate_type,estimate_value,as_of_date,source,revision_of
"""

import sys
import csv
import argparse
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.services.monitoring.earnings_revision import RevisionTracker


def ingest_csv(csv_filepath: str) -> int:
    path = Path(csv_filepath)
    if not path.exists():
        print(f"[ERROR] File not found: {csv_filepath}")
        return 0

    tracker = RevisionTracker()
    inserted_count = 0

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            symbol = row.get("symbol")
            fiscal_period = row.get("fiscal_period")
            estimate_value = row.get("estimate_value")

            if not symbol or not fiscal_period or estimate_value is None:
                print(f"[WARN] Row {row_num}: Missing required fields (symbol, fiscal_period, estimate_value). Skipping.")
                continue

            try:
                val = float(estimate_value)
                est_type = row.get("estimate_type", "consensus_eps") or "consensus_eps"
                as_of = row.get("as_of_date")
                source = row.get("source", "CSV_INGESTION") or "CSV_INGESTION"
                rev_of = int(row["revision_of"]) if row.get("revision_of") and row["revision_of"].isdigit() else None

                est_id = tracker.add_estimate(
                    symbol=symbol,
                    fiscal_period=fiscal_period,
                    estimate_value=val,
                    estimate_type=est_type,
                    as_of_date=as_of,
                    source=source,
                    revision_of=rev_of
                )
                inserted_count += 1
                print(f"[OK] Row {row_num}: Ingested estimate ID {est_id} for {symbol} ({fiscal_period}): {val}")
            except Exception as e:
                print(f"[ERROR] Row {row_num}: Failed to parse or insert row: {e}")

    print(f"=== Successfully ingested {inserted_count} earnings estimate(s) into database ===")
    return inserted_count


def main():
    parser = argparse.ArgumentParser(description="Ingest earnings estimates from CSV into IERL DB.")
    parser.add_argument("csv_path", nargs="?", help="Path to CSV file containing earnings estimates.")
    args = parser.parse_args()

    if not args.csv_path:
        print("Usage: python scripts/ingest_earnings_estimates.py <path_to_csv>")
        sys.exit(1)

    ingest_csv(args.csv_path)


if __name__ == "__main__":
    main()

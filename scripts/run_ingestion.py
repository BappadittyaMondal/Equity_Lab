"""Run Ingestion Job — Tier 0 Data Pipeline Orchestration.

Usage:
    python scripts/run_ingestion.py

Sequentially ingests watchlist symbols:
1. Checks watchlist table in ResearchDataStore (seeds default set if empty via seed_watchlist logic)
2. Runs FinancialIngester for every symbol
3. Runs DailyPriceIngester for every symbol
4. Logs success/failure per symbol
"""

import logging
import sys
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.research_data import ResearchDataStore
from app.services.ingestion.financial_ingester import FinancialIngester
from app.services.ingestion.daily_price_ingester import DailyPriceIngester
from app.services.ingestion.seed_watchlist import run_seed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("run_ingestion")


def main() -> None:
    store = ResearchDataStore()
    watchlist = store.get_watchlist()

    # Step 1: Seed watchlist if empty
    if not watchlist:
        logger.info("Watchlist table empty — running seed_watchlist logic...")
        run_seed()
        watchlist = store.get_watchlist()

    symbols = [item["symbol"].replace(".NS", "") for item in watchlist]
    logger.info("Starting ingestion job for %d symbols: %s", len(symbols), symbols)

    fin_ingester = FinancialIngester(store)
    price_ingester = DailyPriceIngester(store)

    success_count = 0
    failure_count = 0
    per_symbol_results = {}

    for i, symbol in enumerate(symbols, 1):
        logger.info("[%d/%d] Ingesting data for symbol: %s", i, len(symbols), symbol)
        symbol_errors = []

        # Financial ingestion
        try:
            fin_res = fin_ingester.ingest_symbol(symbol)
            fin_count = fin_res.get("financials_ingested", 0)
            symbol_errors.extend(fin_res.get("errors", []))
        except Exception as e:
            fin_count = 0
            symbol_errors.append(f"FinancialIngester exception: {e}")

        # Daily price ingestion
        try:
            price_res = price_ingester.ingest_symbol(symbol, period="2y")
            price_count = price_res.get("snapshots_ingested", 0)
            symbol_errors.extend(price_res.get("errors", []))
        except Exception as e:
            price_count = 0
            symbol_errors.append(f"DailyPriceIngester exception: {e}")

        if symbol_errors:
            failure_count += 1
            logger.warning("  ❌ %s: Ingested %d financials, %d prices with errors: %s",
                           symbol, fin_count, price_count, symbol_errors)
        else:
            success_count += 1
            logger.info("  ✅ %s: Ingested %d financials, %d price snapshots",
                        symbol, fin_count, price_count)

        per_symbol_results[symbol] = {
            "financials_ingested": fin_count,
            "prices_ingested": price_count,
            "status": "SUCCESS" if not symbol_errors else "FAILED_WITH_ERRORS",
            "errors": symbol_errors,
        }

    logger.info("=" * 60)
    logger.info("INGESTION JOB COMPLETE")
    logger.info("  Processed: %d symbols", len(symbols))
    logger.info("  Successes: %d", success_count)
    logger.info("  Failures:  %d", failure_count)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

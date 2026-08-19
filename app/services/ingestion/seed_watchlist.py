"""Watchlist Seed Command — Bulk data ingestion for all watchlist symbols.

Usage:
    python -m app.services.ingestion.seed_watchlist

Iterates over every symbol on the watchlist and runs:
1. FinancialIngester — quarterly income, balance sheet, cash flow
2. DailyPriceIngester — 2 years of daily OHLCV data

After running, the ResearchDataStore will have real data for every
watchlist symbol, enabling all strategy engines to operate on real
observations instead of synthetic defaults.
"""

import sys
import logging
from datetime import datetime, timezone

from app.services.research_data import ResearchDataStore
from app.services.ingestion.financial_ingester import FinancialIngester
from app.services.ingestion.daily_price_ingester import DailyPriceIngester

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("seed_watchlist")

# Default seed symbols covering Nifty-50 sectors: Banking, Pharma, Defence, Manufacturing, Power, IT, FMCG, Energy
DEFAULT_SEED_SYMBOLS = [
    # Energy / Oil & Gas
    "RELIANCE", "ONGC", "BPCL",
    # IT & Technology
    "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM",
    # Banking & Financial Services
    "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "BAJFINANCE",
    # Pharma & Healthcare
    "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB",
    # Defence & Aerospace
    "HAL", "BEL", "BDL",
    # Manufacturing, Industrials & Auto
    "LT", "MARUTI", "TATAMOTORS", "BHARATFORG",
    # Power & Utilities
    "NTPC", "POWERGRID", "TATAPOWER",
    # Consumer & FMCG
    "HINDUNILVR", "ITC", "TITAN"
]


def run_seed(symbols: list[str] | None = None, price_period: str = "2y") -> dict:
    """Execute the full seed pipeline for given symbols.

    Args:
        symbols: List of ticker symbols. If None, uses watchlist or defaults.
        price_period: Historical price period to ingest (default "2y").

    Returns:
        Summary dict with per-symbol results.
    """
    store = ResearchDataStore()
    fin_ingester = FinancialIngester(store)
    price_ingester = DailyPriceIngester(store)

    # Determine symbols to seed
    if symbols is None:
        watchlist = store.get_watchlist()
        symbols = [item["symbol"].replace(".NS", "") for item in watchlist]
        if len(symbols) < 20:
            logger.info("Watchlist has only %d symbols — seeding representative 30-symbol universe into watchlist table", len(symbols))
            for sym in DEFAULT_SEED_SYMBOLS:
                store.add_to_watchlist(sym, company_name=f"{sym} Ltd", target_price=0.0, notes="Seed universe")
            watchlist = store.get_watchlist()
            symbols = [item["symbol"].replace(".NS", "") for item in watchlist]

    logger.info("=" * 60)
    logger.info("IERL Watchlist Seed — %d symbols", len(symbols))
    logger.info("=" * 60)

    results = {}
    total_financials = 0
    total_prices = 0
    total_errors = 0

    for i, symbol in enumerate(symbols, 1):
        logger.info("[%d/%d] Ingesting %s...", i, len(symbols), symbol)

        # Financial data
        fin_result = fin_ingester.ingest_symbol(symbol)
        total_financials += fin_result["financials_ingested"]

        # Daily price data
        price_result = price_ingester.ingest_symbol(symbol, period=price_period)
        total_prices += price_result["snapshots_ingested"]

        errors = fin_result.get("errors", []) + price_result.get("errors", [])
        total_errors += len(errors)

        results[symbol] = {
            "financials": fin_result["financials_ingested"],
            "ownership": fin_result.get("ownership_ingested", 0),
            "daily_prices": price_result["snapshots_ingested"],
            "errors": errors,
        }

        logger.info(
            "  → %d financials, %d prices, %d errors",
            fin_result["financials_ingested"],
            price_result["snapshots_ingested"],
            len(errors),
        )

    logger.info("=" * 60)
    logger.info("SEED COMPLETE")
    logger.info("  Total financial observations: %d", total_financials)
    logger.info("  Total daily price snapshots:  %d", total_prices)
    logger.info("  Total errors:                 %d", total_errors)
    logger.info("=" * 60)

    return {
        "symbols_processed": len(symbols),
        "total_financials": total_financials,
        "total_prices": total_prices,
        "total_errors": total_errors,
        "per_symbol": results,
    }


if __name__ == "__main__":
    # Allow passing symbols as command-line arguments
    cli_symbols = sys.argv[1:] if len(sys.argv) > 1 else None
    run_seed(symbols=cli_symbols)

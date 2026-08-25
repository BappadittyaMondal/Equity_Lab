import os
import json
import asyncio
from datetime import datetime, timezone

import sys
# Ensure the project root is on PYTHONPATH for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.orchestration.orchestrator import Orchestrator
from app.services.market_data import AutoRefreshMarketDataService


def main() -> None:
    """Iterate the watchlist, auto-refresh market data (<72h gap), refresh conviction calls, and persist a JSON digest."""
    print("Executing automated nightly market data refresh...")
    refresh_result = asyncio.run(AutoRefreshMarketDataService.auto_refresh_universe(max_age_hours=72))
    print(f"Auto-refresh complete: {refresh_result['refreshed_count']} refreshed out of {refresh_result['stale_count']} stale symbols.")

    orchestrator = Orchestrator()
    symbols = orchestrator._watchlist_symbols()

    digest: dict[str, dict] = {}
    for symbol in symbols:
        conviction = orchestrator.get_conviction(symbol)
        digest[symbol] = conviction.dict() if hasattr(conviction, "dict") else conviction.model_dump()

    # Ensure the output directory exists.
    out_dir = os.path.join(os.path.dirname(__file__), "..", "frontend_deploy", "data", "digests")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "watchlist_digest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "auto_refresh_summary": refresh_result, "data": digest}, f, indent=2)
    print(f"Watchlist digest successfully written to {out_path}")


if __name__ == "__main__":
    main()


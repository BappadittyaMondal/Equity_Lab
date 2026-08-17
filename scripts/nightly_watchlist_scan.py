import os
import json
from datetime import datetime, timezone

import os
import sys
# Ensure the project root is on PYTHONPATH for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.orchestration.orchestrator import Orchestrator


def main() -> None:
    """Iterate the watch‑list, refresh conviction calls, and persist a JSON digest.

    The digest is written to `data/digests/watchlist_digest.json` and contains a
    mapping of symbol → conviction call payload (as a plain dict).  This script is
    intended to be executed by a nightly cron job.
    """
    orchestrator = Orchestrator()
    # Resolve all symbols that the watch‑list service knows about.
    symbols = orchestrator._watchlist_symbols()

    digest: dict[str, dict] = {}
    for symbol in symbols:
        # `get_conviction` handles caching, drift logging and persistence.
        conviction = orchestrator.get_conviction(symbol)
        digest[symbol] = conviction.dict()

    # Ensure the output directory exists.
    out_dir = os.path.join(os.path.dirname(__file__), "..", "frontend_deploy", "data", "digests")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "watchlist_digest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "data": digest}, f, indent=2)
    print(f"Watchlist digest written to {out_path}")


if __name__ == "__main__":
    main()

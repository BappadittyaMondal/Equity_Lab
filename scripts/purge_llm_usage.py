"""Purge LLM Usage Logs Older Than 90 Days.

Triggered via cron (same mechanism as nightly watchlist scan).
"""

import sys
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Adjust Python path to allow app imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def purge_old_llm_logs(retention_days: int = 90) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    cutoff_iso = cutoff.isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM llm_usage WHERE timestamp < ?", (cutoff_iso,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    logger.info("Purged %d LLM usage log records older than %d days (cutoff: %s).", deleted_count, retention_days, cutoff_iso)
    return deleted_count


def main():
    logger.info("Starting 90-day LLM usage log purge script...")
    purged = purge_old_llm_logs(90)
    print(f"Purge complete: {purged} records deleted.")


if __name__ == "__main__":
    main()

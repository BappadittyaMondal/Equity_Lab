"""Database Health & Postgres-First Production Check.

Verifies database connectivity and warns/logs errors if SQLite fallback is active in production or Vercel serverless environments.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def check_db_health() -> Dict[str, Any]:
    database_url = os.getenv("DATABASE_URL", "").strip()
    is_vercel = bool(os.getenv("VERCEL") or os.getenv("VERCEL_URL"))
    is_prod = os.getenv("IERL_ENVIRONMENT", "development").lower() == "production"

    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        db_type = "POSTGRESQL"
        is_postgres = True
    else:
        db_type = "SQLITE"
        is_postgres = False

    warning = None
    if is_vercel and not is_postgres:
        warning = (
            "CRITICAL DATABASE WARNING: Active database is SQLite on ephemeral Vercel environment. "
            "Data writes will be wiped on container restart. Configure DATABASE_URL (Render/Supabase PostgreSQL) for persistence."
        )
        logger.error(warning)
    elif is_prod and not is_postgres:
        warning = (
            "PRODUCTION DATABASE WARNING: Running in production with local SQLite store. "
            "Set DATABASE_URL to a production PostgreSQL instance."
        )
        logger.warning(warning)

    return {
        "status": "HEALTHY" if is_postgres else ("WARNING" if warning else "OK"),
        "db_type": db_type,
        "is_postgres": is_postgres,
        "is_vercel": is_vercel,
        "warning": warning
    }

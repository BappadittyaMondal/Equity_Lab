"""Centralized Production Boot Guards & Integrity Invariants.

Enforces zero-trust deployment gates across all application entrypoints:
1. FastAPI web server (lifespan)
2. ARQ asynchronous worker (startup)
3. Background CLI daemons

Invariants Enforced:
- Prohibits OFFLINE_TEST_MODE in production deployments.
- Enforces PostgreSQL when STRICT_PRODUCTION_POSTGRES_GATE is active on Render/Vercel/Cloud.
"""

import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


def enforce_production_boot_invariants() -> Dict[str, Any]:
    """Verify runtime environment and database health before accepting traffic or worker tasks."""
    try:
        from app.core.db_health import check_db_health
    except ImportError:
        from core.db_health import check_db_health

    health_status = check_db_health()
    is_cloud_prod = health_status.get("is_vercel") or health_status.get("is_prod")
    is_prod_env = is_cloud_prod or os.getenv("IERL_ENVIRONMENT", "").lower() == "production"

    if is_prod_env and os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true":
        logger.critical("BOOT ABORTED: OFFLINE_TEST_MODE is enabled in production environment! Live deployment requires real data feeds.")
        raise RuntimeError("CRITICAL_CONFIGURATION_ERROR: OFFLINE_TEST_MODE=true is prohibited in production deployments.")

    if is_cloud_prod and not health_status.get("is_postgres"):
        gate_active = os.getenv("STRICT_PRODUCTION_POSTGRES_GATE", os.getenv("STRICT_VERCEL_POSTGRES_GATE", "1")) == "1"
        if gate_active:
            env_name = "Render" if health_status.get("is_render") else ("Vercel" if health_status.get("is_vercel") else "Production")
            logger.critical(f"BOOT ABORTED: {env_name} production environment detected without PostgreSQL DATABASE_URL. Set DATABASE_URL or STRICT_PRODUCTION_POSTGRES_GATE=0.")
            raise RuntimeError(f"Deployment aborted: {env_name} environment requires PostgreSQL DATABASE_URL to prevent silent data loss.")

    return health_status

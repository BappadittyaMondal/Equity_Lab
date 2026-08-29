"""IERL OS Configuration Management.

Loads environment settings safely from environment variables and dotenv files.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Local dotenv files are a developer convenience only. Production deployments must
# supply secrets through their host's environment-variable/secret-store facility.
root_dir = Path(__file__).resolve().parents[2]
if os.getenv("IERL_ENVIRONMENT", "development").lower() == "development":
    load_dotenv(dotenv_path=root_dir / ".env")
    # Legacy key files can contain pasted notes or stale credentials. Loading one
    # is deliberately opt-in during local migration and is never done in prod.
    if os.getenv("IERL_LOAD_LEGACY_API_KEYS_FILE", "false").lower() == "true":
        load_dotenv(dotenv_path=root_dir / "API_KEYS_CONFIG.env")


class Settings:
    PROJECT_NAME: str = "Equity Lab"
    VERSION: str = "0.0.9"
    DESCRIPTION: str = "Institutional Indian Equity Research, Options Arbitrage, and Return Probability Engine"

    # Infrastructure & Distributed Cache/Limiter Settings
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text").lower()

    # Active LLM Provider
    ACTIVE_LLM_PROVIDER: str = os.getenv("ACTIVE_LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    # Security & CORS
    # In production, an explicit allow list is required; wildcard is prohibited.
    ALLOWED_ORIGINS_RAW: str = os.getenv("ALLOWED_ORIGIN", "")

    @staticmethod
    def _validate_cors_settings():
        """Validate CORS configuration for production.
        Fallback safely if running tests or local development.
        """
        env = os.getenv("IERL_ENVIRONMENT", "development").lower()
        if env == "production":
            raw = os.getenv("ALLOWED_ORIGIN", "")
            if not raw:
                vercel_url = os.getenv("VERCEL_URL")
                if vercel_url:
                    raw = f"https://{vercel_url}"
                    os.environ["ALLOWED_ORIGIN"] = raw
                elif "PYTEST_CURRENT_TEST" in os.environ or os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true":
                    os.environ["ALLOWED_ORIGIN"] = "http://localhost:3000,http://127.0.0.1:8000"
                else:
                    # Provide a local development fallback default instead of crashing startup
                    import logging
                    logging.getLogger("app.core.config").warning(
                        "SECURITY WARNING: Running with IERL_ENVIRONMENT=production but ALLOWED_ORIGIN is not set. "
                        "Falling back to localhost origins (http://localhost:3000, http://127.0.0.1:8000)."
                    )
                    os.environ["ALLOWED_ORIGIN"] = "http://localhost:3000,http://127.0.0.1:8000"
            elif "*" in [o.strip() for o in raw.split(",")]:
                vercel_url = os.getenv("VERCEL_URL")
                if vercel_url:
                    os.environ["ALLOWED_ORIGIN"] = f"https://{vercel_url}"
                else:
                    raise RuntimeError("Wildcard '*' is not allowed for ALLOWED_ORIGIN in production.")

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]
        if not origins and os.getenv("IERL_ENVIRONMENT", "development").lower() == "development":
            return ["http://localhost:3000", "http://127.0.0.1:8000", "http://localhost:8000"]
        return origins

    # Security Limits
    MAX_REQUEST_SIZE_BYTES: int = 1_000_000  # 1 MB max payload
    RATE_LIMIT_PUBLIC_RPM: int = 60
    RATE_LIMIT_LLM_RPM: int = 10
    TRUST_PROXY_HEADERS: bool = os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true"
    
    # Optional Auth Key
    API_KEY_SECRET: str = os.getenv("API_KEY_SECRET", "")
    # In production, authentication is required by default.
    REQUIRE_AUTH: bool = (
        os.getenv("IERL_ENVIRONMENT", "development").lower() == "production"
        or os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    )

    # Options A2 remains suspended until it has validated live option-chain data,
    # exchange-calibrated margin data, and a documented backtest.
    ENABLE_OPTIONS_A2: bool = os.getenv("ENABLE_OPTIONS_A2", "false").lower() == "true"

    # Research data is append-only and local by default. Writes always require
    # this separate key, even when public read-only endpoints are enabled.
    DATA_STORE_PATH: str = os.getenv("DATA_STORE_PATH", str(root_dir / "data" / "ierl_equity.sqlite3"))
    DATA_WRITE_API_KEY: str = os.getenv("DATA_WRITE_API_KEY", "")

    # Observability & Cost Control
    # Observability \u0026 Cost Control
    LLM_DAILY_CALL_LIMIT: int = int(os.getenv("LLM_DAILY_CALL_LIMIT", "150"))
    LLM_COST_PER_1K_TOKENS: float = float(os.getenv("LLM_COST_PER_1K_TOKENS", "0"))
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")
    
    @property
    def SKILL_LIBRARY_VERSION(self) -> str:
        env_ver = os.getenv("SKILL_LIBRARY_VERSION")
        if env_ver:
            return env_ver
        # Compute SHA-256 content hash of docs master corpus if present
        docs_dir = root_dir / "docs"
        if not docs_dir.exists():
            return "v1.2-sha256-default"
        hasher = hashlib.sha256()
        for filepath in sorted(docs_dir.rglob("*.md")):
            try:
                hasher.update(filepath.read_bytes())
            except Exception:
                pass
        return f"sha256:{hasher.hexdigest()[:16]}"

    # Market Data Settings
    MARKET_DATA_PRIMARY_PROVIDER: str = "yfinance"
    # Cache TTLs for different data types (seconds)
    CACHE_TTL_QUOTE_SEC: int = int(os.getenv("CACHE_TTL_QUOTE_SEC", "60"))  # default 60s
    CACHE_TTL_FUNDAMENTALS_SEC: int = int(os.getenv("CACHE_TTL_FUNDAMENTALS_SEC", "300"))  # default 5min
    # Price conflict tolerance for synthesis (percentage)
    PRICE_CONFLICT_TOLERANCE_PCT: float = float(os.getenv("PRICE_CONFLICT_TOLERANCE_PCT", "5.0"))


settings = Settings()

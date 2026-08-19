"""IERL OS Configuration Management.

Loads environment settings safely from environment variables and dotenv files.
"""

import os
import hashlib
from pathlib import Path
from typing import List
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
    PROJECT_NAME: str = "IERL AI Equity Intelligence OS Engine"
    VERSION: str = "0.4.0"
    DESCRIPTION: str = "Institutional Indian Equity Research, Options Arbitrage, and Return Probability Engine"

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
        Raises RuntimeError if ALLOWED_ORIGIN is empty or contains a wildcard.
        """
        if os.getenv("IERL_ENVIRONMENT", "development").lower() == "production":
            raw = os.getenv("ALLOWED_ORIGIN", "")
            if not raw:
                raise RuntimeError("ALLOWED_ORIGIN must be set in production.")
            if "*" in [o.strip() for o in raw.split(",")]:
                raise RuntimeError("Wildcard '*' is not allowed for ALLOWED_ORIGIN in production.")

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]

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
        # Compute SHA-256 content hash of Canonical_Source_84 master corpus
        canonical_dir = root_dir / "Not_Required_Upload" / "Canonical_Source_84"
        if not canonical_dir.exists():
            return "v1.2-sha256-default"
        hasher = hashlib.sha256()
        for filepath in sorted(canonical_dir.rglob("*.md")):
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

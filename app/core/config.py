"""IERL OS Configuration Management.

Loads environment settings safely from environment variables and dotenv files.
"""

import os
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
    VERSION: str = "0.3-Production"
    DESCRIPTION: str = "Institutional Indian Equity Research, Options Arbitrage, and Return Probability Engine"

    # Active LLM Provider
    ACTIVE_LLM_PROVIDER: str = os.getenv("ACTIVE_LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    # Security & CORS
    ALLOWED_ORIGINS_RAW: str = os.getenv(
        "ALLOWED_ORIGIN", 
        "https://sovereignmind.in,http://localhost:8000,http://127.0.0.1:8000"
    )
    
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
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

    # Options A2 remains suspended until it has validated live option-chain data,
    # exchange-calibrated margin data, and a documented backtest.
    ENABLE_OPTIONS_A2: bool = os.getenv("ENABLE_OPTIONS_A2", "false").lower() == "true"

    # Research data is append-only and local by default. Writes always require
    # this separate key, even when public read-only endpoints are enabled.
    DATA_STORE_PATH: str = os.getenv("DATA_STORE_PATH", str(root_dir / "data" / "ierl_equity.sqlite3"))
    DATA_WRITE_API_KEY: str = os.getenv("DATA_WRITE_API_KEY", "")

    # Market Data Settings
    MARKET_DATA_PRIMARY_PROVIDER: str = "yfinance"
    CACHE_TTL_SECONDS: int = 60


settings = Settings()

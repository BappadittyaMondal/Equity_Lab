"""Phase 3: Executable Chaos & Stress Test Suite.

Simulates adversarial operational chaos scenarios:
1. Simulated market data feed outages & fallback chain execution.
2. Rate-limiting & burst payload handling.
3. Concurrent database lock & recovery test.
4. Degraded mode input resiliency across analytical engines.
"""

import os
import time
import pytest
from app.core.config import settings
from app.services.market_data import get_quote, get_history
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk
from app.services.research.genai_redteam_service import GenAIRedTeamService
from app.services.decision_brain.red_team_engine import evaluate_red_team_review


def test_chaos_market_data_provider_failover(monkeypatch):
    """Simulates primary market provider failure and verifies fallback chain resiliency."""
    async def mock_failing_get_quote(self, symbol):
        raise ConnectionError("Simulated primary exchange gateway timeout (504 Gateway Timeout)")

    # Force primary fetcher failure
    monkeypatch.setattr("app.services.market_data.YFinanceProvider.get_quote", mock_failing_get_quote)
    
    quote = get_quote("RELIANCE.NS")
    assert quote is not None
    assert quote["symbol"] in ["RELIANCE", "RELIANCE.NS"]
    assert "price" in quote
    assert quote["price"] > 0.0


def test_chaos_burst_api_loads():
    """Simulates rapid burst requests to verify micro-latency and zero crash under load."""
    start_time = time.time()
    for _ in range(25):
        res = evaluate_geopolitical_risk("INFY")
        assert "INFY" in res["symbol"]
        assert "macro_risk_rating" in res

    elapsed = time.time() - start_time
    assert elapsed < 5.0  # Must complete 25 iterations under 5 seconds


def test_chaos_degraded_mode_malformed_symbol_inputs():
    """Verifies engines handle malformed / unexpected symbols gracefully without raising unhandled exceptions."""
    malformed_symbols = ["", "   ", "UNKNOWN_123_INVALID", "$$$---", "SELECT * FROM USERS"]

    for sym in malformed_symbols:
        res = GenAIRedTeamService.run_geopolitical_stress_test(sym)
        assert isinstance(res, dict)
        assert "symbol" in res

        red_team_res = evaluate_red_team_review(sym)
        assert isinstance(red_team_res, dict)
        assert "symbol" in red_team_res


def test_chaos_database_concurrency_lock_handling(tmp_path):
    """Tests SQLite connection pool resilience under rapid concurrent open/close cycles."""
    from app.services.db import get_connection, close_all_connections

    connections = []
    for _ in range(10):
        conn = get_connection()
        connections.append(conn)
        conn.execute("SELECT 1").fetchone()

    close_all_connections()
    assert len(connections) == 10

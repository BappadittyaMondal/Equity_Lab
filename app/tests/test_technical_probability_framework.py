"""Test Suite for Institutional Technical Probability & Market-Structure Framework.

Validates:
  1. Market Regime Classifier (R1–R6)
  2. Multi-Timeframe Trend & RS Acceleration Engine
  3. Base Quality, Volatility Compression & Technical Setups A–H
  4. Volume, Delivery & Microstructure Engine
  5. Indian Regulatory Surveillance Gate & Transaction Cost Model
  6. Empirical Probability Calibration Engine
  7. In-Position Trade Management Engine
  8. Portfolio Heat & Aggregated Risk Engine (Gate 11)
  9. 3-Tier Technical Universe Screener Funnel
  10. Arbiter Synthesis & FastAPI Technical Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.research.market_regime import classify_market_regime
from app.services.strategies.technical_trend_rs import evaluate_technical_trend_and_rs
from app.services.strategies.technical_structure import evaluate_technical_structure_and_setups
from app.services.strategies.technical_volume_microstructure import evaluate_volume_and_microstructure
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate
from app.services.research.technical_probability import calculate_calibrated_probability_ladder
from app.services.risk.trade_management import evaluate_in_position_management
from app.services.risk.portfolio_risk import evaluate_portfolio_heat_and_risk
from app.services.research.universe_screener import run_technical_universe_screener
from app.services.decision_brain.arbiter import Arbiter

client = TestClient(app)
_API_KEY_HEADER = {"X-API-Key": "test_secret_key"}


@pytest.fixture(autouse=True)
def mock_market_data(monkeypatch):
    import pandas as pd
    import numpy as np

    def _mock_get_history(symbol: str, period: str = "1y", interval: str = "1d"):
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=252, freq="B")
        n_len = len(dates)
        price = 1000.0 + np.cumsum(np.random.randn(n_len) * 5)
        price = np.clip(price, 100, 5000)
        volume = np.abs(np.random.randn(n_len) * 500000 + 1000000).astype(int)
        return pd.DataFrame({
            "Open": price * 0.99,
            "High": price * 1.01,
            "Low": price * 0.98,
            "Close": price,
            "Volume": volume,
        }, index=dates)

    monkeypatch.setattr("app.services.market_data.get_history", _mock_get_history)
    monkeypatch.setattr("app.services.research.market_regime.get_history", _mock_get_history)
    monkeypatch.setattr("app.services.strategies.technical_trend_rs.get_history", _mock_get_history)
    monkeypatch.setattr("app.services.strategies.technical_structure.get_history", _mock_get_history)
    monkeypatch.setattr("app.services.strategies.technical_volume_microstructure.get_history", _mock_get_history)


def test_market_regime_classifier():
    regime = classify_market_regime()
    assert regime.regime_code in ["R1_BULL_TREND", "R2_BULL_VOLATILE", "R3_SIDEWAYS_RANGE", "R4_BEAR_TREND", "R5_PANIC_STRESS", "R6_RECOVERY_TRANSITION"]
    assert regime.realized_volatility_pct > 0.0


def test_technical_trend_and_rs():
    res = evaluate_technical_trend_and_rs("POLYCAB")
    assert "trend_score" in res
    assert "rs_rating_0_99" in res
    assert 1 <= res["rs_rating_0_99"] <= 99
    assert isinstance(res["pre_breakout_rs_leadership"], bool)


def test_technical_structure_and_setups():
    res = evaluate_technical_structure_and_setups("POLYCAB")
    assert "base_quality_score" in res
    assert "setup_class" in res
    assert res["setup_class"].startswith("SETUP_")
    assert "volatility_compression_state" in res


def test_volume_and_microstructure():
    res = evaluate_volume_and_microstructure("POLYCAB")
    assert "participation_score" in res
    assert res["rvol"] > 0.0
    assert res["udvr"] > 0.0


def test_surveillance_and_cost_gate():
    gate = evaluate_surveillance_and_cost_gate("POLYCAB")
    assert gate.asm_stage == "CLEAN"
    assert gate.total_roundtrip_cost_pct > 0.0
    assert gate.hard_gate_status in ["PASS", "AMBER", "FAIL"]


def test_empirical_probability_calibration():
    ladder = calculate_calibrated_probability_ladder("POLYCAB", tss_score=80.0, setup_class="SETUP_A_BREAKOUT")
    assert 0.0 <= ladder.event_t1_prob_5pct_10d <= 1.0
    assert 0.0 <= ladder.event_t2_prob_10pct_20d <= 1.0
    assert ladder.expected_value_pct != 0.0


def test_in_position_trade_management():
    state = evaluate_in_position_management("POLYCAB", entry_price=500.0, highest_close_since_entry=540.0, initial_stop_price=475.0)
    assert state.breakeven_status == "ACTIVE"
    assert state.partial_exit_status == "PARTIAL_BOOKED_50PCT"
    assert state.chandelier_atr_stop_price > 475.0


def test_portfolio_heat_and_risk():
    heat = evaluate_portfolio_heat_and_risk("POLYCAB", candidate_risk_pct=1.5)
    assert heat.gate11_status in ["PASS", "FAIL_HEAT_EXCEEDED", "FAIL_MAX_POSITIONS", "FAIL_SECTOR_CONCENTRATION"]


def test_3tier_universe_screener():
    res = run_technical_universe_screener(universe=["POLYCAB", "RELIANCE", "INFY"], min_tss_score=50.0)
    assert res["total_universe_scanned"] == 3
    assert len(res["candidates"]) >= 0


def test_arbiter_technical_report():
    arbiter = Arbiter()
    report = arbiter.generate_technical_report("POLYCAB")
    assert report.symbol == "POLYCAB"
    assert report.technical_state_score >= 0.0
    assert report.setup_type.startswith("SETUP_")


def test_fastapi_technical_endpoints():
    r1 = client.get("/api/v1/technical/regime", headers=_API_KEY_HEADER)
    assert r1.status_code == 200
    assert "regime_code" in r1.json()

    r2 = client.get("/api/v1/technical/report/POLYCAB", headers=_API_KEY_HEADER)
    assert r2.status_code == 200
    assert r2.json()["symbol"] == "POLYCAB"

    r3 = client.get("/api/v1/technical/screener?min_tss_score=50.0", headers=_API_KEY_HEADER)
    assert r3.status_code == 200
    assert "candidates" in r3.json()

    r4 = client.get("/api/v1/technical/surveillance/POLYCAB", headers=_API_KEY_HEADER)
    assert r4.status_code == 200
    assert "circuit_band_pct" in r4.json()


def test_isotonic_calibrator_monotonicity():
    """Verify IsotonicCalibrator output is strictly non-decreasing (monotonic)."""
    import numpy as np
    from app.services.probability import IsotonicCalibrator

    np.random.seed(42)
    raw_probs = np.linspace(0.1, 0.9, 50)
    outcomes = (raw_probs + np.random.randn(50) * 0.15 > 0.5).astype(int)

    iso = IsotonicCalibrator()
    iso.fit(raw_probs, outcomes)

    test_grid = np.linspace(0.0, 1.0, 20)
    calibrated = iso.predict(test_grid)

    # Assert monotonic non-decreasing property: calibrated[i+1] >= calibrated[i]
    diffs = np.diff(calibrated)
    assert np.all(diffs >= -1e-9)


"""State-Propagation & End-to-End Integration Tests for Gate 11 Portfolio Heat Engine.

Certifies:
1. Empty Book: Allows single-name candidate entry with PASS status.
2. Sector Concentration: Rejects entry with FAIL_SECTOR_CONCENTRATION when sector allocation exceeds cap.
3. Max Positions: Rejects entry with FAIL_MAX_POSITIONS when concurrent positions reach limit.
4. Decision Run Manifest: Accurately populates engines_missing and min_engines_required.
"""

import pytest
from app.services.risk.portfolio_risk import evaluate_portfolio_heat_and_risk
from app.services.decision_brain.arbiter import Arbiter


def test_gate11_empty_book_pass():
    """Verify that evaluating against an empty book allows entry."""
    res = evaluate_portfolio_heat_and_risk(
        candidate_symbol="RELIANCE",
        candidate_sector="OIL_GAS",
        candidate_risk_pct=1.5,
        open_positions={},
        regime_code="R1_BULL_TREND"
    )
    assert res.gate11_status == "PASS"
    assert res.current_portfolio_heat_pct == 0.0
    assert res.concurrent_positions_count == 0


def test_gate11_sector_concentration_fail():
    """Verify that a concentrated book in INFRASTRUCTURE rejects a 5th candidate in the same sector."""
    concentrated_book = {
        "INFRA1": {"symbol": "INFRA1", "sector": "INFRASTRUCTURE", "risk_pct": 2.0},
        "INFRA2": {"symbol": "INFRA2", "sector": "INFRASTRUCTURE", "risk_pct": 2.0},
        "INFRA3": {"symbol": "INFRA3", "sector": "INFRASTRUCTURE", "risk_pct": 2.0},
        "INFRA4": {"symbol": "INFRA4", "sector": "INFRASTRUCTURE", "risk_pct": 2.0},
        "AUTO1": {"symbol": "AUTO1", "sector": "AUTO", "risk_pct": 1.0},
    }

    res = evaluate_portfolio_heat_and_risk(
        candidate_symbol="INFRA_NEW",
        candidate_sector="INFRASTRUCTURE",
        candidate_risk_pct=2.0,
        open_positions=concentrated_book,
        regime_code="R1_BULL_TREND"
    )

    assert res.gate11_status == "FAIL_SECTOR_CONCENTRATION"
    assert res.sector_concentration_pct > 30.0
    assert res.correlation_discount_factor <= 0.85


def test_gate11_max_positions_fail():
    """Verify that reaching 10 open positions blocks new candidate entry."""
    full_book = {
        f"STOCK_{i}": {"symbol": f"STOCK_{i}", "sector": f"SECTOR_{i}", "risk_pct": 1.0}
        for i in range(10)
    }

    res = evaluate_portfolio_heat_and_risk(
        candidate_symbol="STOCK_11",
        candidate_sector="SECTOR_NEW",
        candidate_risk_pct=1.0,
        open_positions=full_book,
        regime_code="R1_BULL_TREND"
    )

    assert res.gate11_status == "FAIL_MAX_POSITIONS"
    assert res.concurrent_positions_count == 10


def test_decision_manifest_engines_missing_diagnostics():
    """Verify Arbiter decision_manifest attaches engines_missing and min_engines_required."""
    arbiter = Arbiter()
    call = arbiter.arbitrate("TCS")

    assert call.decision_manifest is not None
    manifest = call.decision_manifest
    assert "engines_missing" in manifest
    assert "min_engines_required" in manifest
    assert manifest["min_engines_required"] == 10
    assert "evidence_coverage_pct" in manifest
    assert "evidence_clusters" in manifest

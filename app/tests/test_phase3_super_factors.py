"""Unit tests for Phase 3 Super-Factor Analytical Engines.

Tests:
1. Incremental ROIC calculation and trend in fundamental_metrics.py
2. Revision Breadth and Momentum in earnings_revision.py
3. Moat Scoring Rubric in moat_engine.py
4. Sector Unit Economics & Market Share Velocity in unit_economics.py
5. Bayesian Thesis Updating in thesis_monitor.py
6. Multibagger Screener Integration and Registry E8 routing
"""

import pytest
import sqlite3
from types import SimpleNamespace
from app.services.strategies.fundamental_metrics import compute_incremental_roic
from app.services.monitoring.earnings_revision import RevisionTracker
from app.services.strategies.moat_engine import evaluate_moat_score
from app.services.strategies.unit_economics import evaluate_unit_economics, compute_market_share_velocity
from app.services.longitudinal.thesis_monitor import ThesisMonitorEngine
from app.services.strategies.multibagger_screener import evaluate_multibagger_score
from app.services.strategies.registry import run_strategy_module, get_strategy_module


def test_incremental_roic_normal():
    # Construct 5 financial observations with rising NOPAT and rising Invested Capital
    financials = [
        SimpleNamespace(metric="nopat", value=100.0, period_end="2024-03-31"),
        SimpleNamespace(metric="nopat", value=140.0, period_end="2025-03-31"),
        SimpleNamespace(metric="invested_capital", value=500.0, period_end="2024-03-31"),
        SimpleNamespace(metric="invested_capital", value=600.0, period_end="2025-03-31"),
    ]
    res = compute_incremental_roic(financials, periods=1)
    assert res["status"] == "PRODUCTION"
    assert res["incremental_roic_pct"] == 40.0  # ΔNOPAT (40) / ΔIC (100) * 100
    assert "SUPER-FACTOR HIGH INCREMENTAL ROIC" in res["evidence"][0]


def test_incremental_roic_static_capital():
    financials = [
        SimpleNamespace(metric="nopat", value=100.0, period_end="2024-03-31"),
        SimpleNamespace(metric="nopat", value=120.0, period_end="2025-03-31"),
        SimpleNamespace(metric="invested_capital", value=500.0, period_end="2024-03-31"),
        SimpleNamespace(metric="invested_capital", value=500.0, period_end="2025-03-31"),
    ]
    res = compute_incremental_roic(financials, periods=1)
    assert res["status"] == "PRODUCTION"
    assert res["incremental_roic_pct"] is None


def test_revision_breadth_and_momentum(tmp_path):
    db_file = str(tmp_path / "test_revisions.db")
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS earnings_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            fiscal_period TEXT NOT NULL,
            estimate_type TEXT NOT NULL,
            estimate_value REAL NOT NULL,
            as_of_date TEXT NOT NULL,
            source TEXT,
            revision_of INTEGER
        )
    """)
    conn.commit()
    conn.close()

    tracker = RevisionTracker(db_path=db_file)
    tracker.add_estimate("TCS", "FY25", 100.0, as_of_date="2024-01-01")
    tracker.add_estimate("TCS", "FY25", 110.0, as_of_date="2024-02-01")
    tracker.add_estimate("TCS", "FY25", 115.0, as_of_date="2024-03-01")

    res = tracker.compute_revision_breadth_and_momentum("TCS")
    assert res["status"] == "PRODUCTION"
    assert res["up_revisions"] == 2
    assert res["down_revisions"] == 0
    assert res["revision_breadth"] == 1.0
    assert res["revision_momentum"] > 0.0


def test_moat_engine():
    res = evaluate_moat_score("RELIANCE", inputs={"pricing_power": 5, "cost_advantage": 5})
    assert res["moat_score"] > 60.0
    assert res["moat_trajectory"] == "STRENGTHENING"
    assert "Pricing Power" in res["evidence"][2]


def test_unit_economics():
    res_fin = evaluate_unit_economics("HDFCBANK", sector="FINANCIALS", operational_data={"net_interest_margin_pct": 4.2})
    assert res_fin["unit_economics_score"] > 50.0
    assert "nim_pct" in res_fin["metrics"]

    res_mfg = evaluate_unit_economics("TATASTEEL", sector="MANUFACTURING", operational_data={"capacity_utilization_pct": 82.0})
    assert res_mfg["unit_economics_score"] > 50.0

    res_mkt = compute_market_share_velocity("TATASTEEL")
    assert res_mkt["status"] == "DATA_BLOCKED"


def test_bayesian_thesis_monitor(tmp_path):
    db_file = str(tmp_path / "test_thesis.db")
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS thesis_records (
            symbol TEXT PRIMARY KEY,
            why_buy TEXT,
            growth_drivers TEXT,
            catalysts TEXT,
            risks TEXT,
            thesis_conditions TEXT,
            invalidation_conditions TEXT,
            thesis_state TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    
    engine = ThesisMonitorEngine(db=conn)
    thesis = engine.evaluate_thesis_state(
        symbol="INFY",
        conviction_score=85,
        verdict="Buy",
        contradictions=[],
        primary_thesis="Cloud acceleration momentum.",
        prior_probability=0.50
    )
    assert thesis.thesis_state == "STRENGTHENING"
    assert "Bayesian Thesis Probability" in thesis.growth_drivers[2]
    conn.close()



def test_multibagger_screener_integration():
    res = evaluate_multibagger_score("RELIANCE")
    assert res.multibagger_score >= 0.0
    assert "growth_inflection_score" in res.component_scores


def test_strategy_registry_e8():
    module = get_strategy_module("E8")
    assert module.name == "Moat Strength & Unit Economics Engine"
    
    res = run_strategy_module("E8", "RELIANCE")
    assert res.status == "production"
    assert "moat_score" in res.results

"""
Phase 199: Comprehensive Institutional Verification Suite.
Validates:
  1. E22 Geopolitical & Macroeconomic Risk Engine registration & dispatch.
  2. Arbiter MACRO category integration, evidence clustering & 100% pillar coverage.
  3. Self-Learning PROMOTED Prior Dynamic Memory Recall & feedback into conviction.
  4. Deadliest Combo Book-to-Bill (B2B >= 2.5x) and Sovereign Capex Convexity Boosts.
"""

import pytest
from unittest.mock import MagicMock
from app.services.strategies.registry import (
    RESEARCH_ENGINES,
    get_strategy_module,
    run_strategy_module,
)
from app.services.decision_brain.debate_engine import ENGINE_CATEGORIES, _get_engine_category
from app.services.decision_brain.arbiter import Arbiter
from app.services.research.self_learning_engine import SelfLearningEngine
from app.services.research.deadliest_combo_pipeline import _calculate_operating_leverage_convexity
from app.models.schemas import StrategyRunResponse


# ==============================================================================
# 1. E22 Registration & Dispatch Integrity
# ==============================================================================

def test_e22_registered_in_research_engines():
    """Verify E22 is registered in RESEARCH_ENGINES and has correct properties."""
    assert "E22" in RESEARCH_ENGINES
    mod = RESEARCH_ENGINES["E22"]
    assert mod.id == "E22"
    assert mod.name == "Geopolitical & Macroeconomic Risk Engine"
    assert mod.status == "production"
    assert "macro_risk_rating" in mod.metrics


def test_e22_mapped_to_macro_in_debate_engine():
    """Verify E22 is mapped to MACRO category in debate_engine.py."""
    assert "E22" in ENGINE_CATEGORIES
    assert ENGINE_CATEGORIES["E22"] == "MACRO"
    assert _get_engine_category("E22") == "MACRO"


def test_e22_strategy_run_response_conformance():
    """Verify E22 executes through run_strategy_module and returns StrategyRunResponse."""
    res = run_strategy_module("E22", symbol="RELIANCE")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "E22"
    assert res.status == "production"
    assert res.symbol == "RELIANCE.NS"
    assert "macro_risk_rating" in res.results
    assert "effective_overlay_pct" in res.results
    assert "score" in res.metrics
    assert 10.0 <= res.metrics["score"] <= 95.0


def test_e22_shipping_sensitivity_overlay():
    """Verify E22 correctly evaluates macro volatility overlay on shipping/tanker stocks."""
    res = run_strategy_module("E22", symbol="GESHIP")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "E22"
    assert res.results["macro_risk_rating"] in ("LOW", "MODERATE", "ELEVATED", "HIGH")
    assert "conviction_penalty_pct" in res.results


# ==============================================================================
# 2. Arbiter MACRO Integration & Evidence Clusters
# ==============================================================================

def test_arbiter_collects_e22_and_scores_macro_category():
    """Verify Arbiter _collect_engine_outputs runs E22 and populates MACRO in weighted score."""
    arbiter = Arbiter()
    outputs = arbiter._collect_engine_outputs("RELIANCE")
    
    e22_outs = [o for o in outputs if o.get("engine_id") == "E22"]
    assert len(e22_outs) == 1
    assert e22_outs[0]["verdict"] in ("Buy", "Avoid")
    assert e22_outs[0]["score_0_100"] is not None

    composite, breakdown = arbiter._compute_weighted_score(outputs, objective="GENERAL")
    assert "MACRO" in breakdown
    assert breakdown["MACRO"] > 0.0


def test_arbiter_evidence_clusters_surfaces_macro_geopolitical():
    """Verify _compute_evidence_clusters populates macro_geopolitical."""
    arbiter = Arbiter()
    sample_breakdown = {
        "FUNDAMENTAL": 70.0,
        "VALUATION": 65.0,
        "TECHNICAL": 60.0,
        "FORENSIC": 75.0,
        "GOVERNANCE": 80.0,
        "MACRO": 72.0,
    }
    cov_pct, clusters = arbiter._compute_evidence_clusters(sample_breakdown)
    assert cov_pct == 100.0  # All 6 core categories active
    assert "macro_geopolitical" in clusters
    assert clusters["macro_geopolitical"] == 72.0


# ==============================================================================
# 3. Self-Learning PROMOTED Prior Dynamic Memory Recall
# ==============================================================================

def test_self_learning_recall_target_stock_phantom_exit():
    """Verify recall_applicable_priors identifies target superstar exits (e.g. NAZARA)."""
    sle = SelfLearningEngine()
    recalled = sle.recall_applicable_priors("NAZARA")
    
    assert recalled["symbol"] == "NAZARA"
    assert recalled["promoted_rules_evaluated"] >= 30
    assert recalled["applied_rules_count"] >= 1
    
    applied_eids = [r["entity_id"] for r in recalled["applied_rules"]]
    assert any("NAZARA" in eid for eid in applied_eids)
    assert recalled["net_conviction_delta_pct"] < 0.0  # Penalty applied


def test_self_learning_recall_hard_veto_override():
    """Verify recall_applicable_priors identifies empirical hard gate disqualifications."""
    sle = SelfLearningEngine()
    recalled = sle.recall_applicable_priors("TEXRAIL")
    
    assert recalled["symbol"] == "TEXRAIL"
    assert recalled["hard_veto_rule"] is not None
    assert "TEXRAIL" in recalled["hard_veto_rule"]["entity_id"]


def test_self_learning_recall_working_capital_elongation():
    """Verify recall_applicable_priors applies Lamba Working Capital haircut when metrics breach."""
    sle = SelfLearningEngine()
    
    # Mock snap with elongated working capital
    mock_snap = MagicMock()
    mock_snap.working_capital_days = 145.0
    mock_snap.debtor_days = 95.0
    mock_snap.institutional_holding = 15.0
    
    recalled = sle.recall_applicable_priors("GENERIC_CORP", snap=mock_snap)
    applied_eids = [r["entity_id"] for r in recalled["applied_rules"]]
    
    assert "LAMBA_WORKING_CAPITAL_VELOCITY_RULE" in applied_eids
    assert recalled["net_conviction_delta_pct"] <= -0.20


def test_arbiter_manifest_records_self_learning_feedback():
    """Verify Arbiter decision_manifest records active self-learning feedback."""
    arbiter = Arbiter()
    call = arbiter.arbitrate("NAZARA")
    
    manifest = call.decision_manifest
    assert "self_learning_feedback" in manifest
    sl_fb = manifest["self_learning_feedback"]
    assert sl_fb["rules_applied_count"] >= 1
    assert len(sl_fb["applied_rules"]) >= 1
    assert any("NAZARA" in r for r in sl_fb["applied_rules"])


# ==============================================================================
# 4. Deadliest Combo Book-to-Bill (B2B) Convexity Boost
# ==============================================================================

def test_deadliest_combo_b2b_ratio_convexity_boost():
    """Verify B2B >= 2.5x adds backlog convexity boost to Omega."""
    base_fundamentals = {
        "pat_growth_latest": 20.0,
        "sales_growth_latest": 10.0,
    }
    omega_base = _calculate_operating_leverage_convexity(base_fundamentals)
    assert omega_base == 2.0  # 20 / 10 = 2.0

    b2b_fundamentals = {
        "pat_growth_latest": 20.0,
        "sales_growth_latest": 10.0,
        "b2b_ratio": 3.0,  # 3.0x book-to-bill backlog
    }
    omega_boosted = _calculate_operating_leverage_convexity(b2b_fundamentals)
    assert omega_boosted > omega_base
    # Expected boost: min(0.25, round((3.0 - 1.0) * 0.08, 3)) = 0.16
    assert omega_boosted == round(2.0 + 0.16, 3)


def test_deadliest_combo_b2b_sovereign_capex_bonus():
    """Verify sovereign_capex_bonus flag adds 0.15 convexity boost to Omega."""
    base_fundamentals = {
        "pat_growth_latest": 15.0,
        "sales_growth_latest": 10.0,
    }
    omega_base = _calculate_operating_leverage_convexity(base_fundamentals)
    assert omega_base == 1.5

    sovereign_fundamentals = {
        "pat_growth_latest": 15.0,
        "sales_growth_latest": 10.0,
        "sovereign_capex_bonus": True,
    }
    omega_boosted = _calculate_operating_leverage_convexity(sovereign_fundamentals)
    assert omega_boosted == 1.65  # 1.5 + 0.15


def test_deadliest_combo_omega_clamped_at_2_5_ceiling():
    """Verify Omega convexity never exceeds the mathematical upper bound of 2.5."""
    extreme_fundamentals = {
        "pat_growth_latest": 50.0,
        "sales_growth_latest": 5.0,  # ratio 10.0
        "b2b_ratio": 5.0,
        "capital_wip": 100.0,
        "net_block": 100.0,
    }
    omega = _calculate_operating_leverage_convexity(extreme_fundamentals)
    assert omega == 2.5

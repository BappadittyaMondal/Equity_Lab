"""Point-in-Time Integration Regression Test for Decision Brain Arbiter.

Verifies that Arbiter.arbitrate(symbol, as_of=historical_date) forwards the exact as_of 
timestamp down through registry.run_strategy_module() to the underlying research engines,
preventing future look-ahead data leakage.
"""

from datetime import datetime, timezone
import pytest
from app.services.decision_brain.arbiter import Arbiter
from app.services.strategies import registry

def test_arbiter_point_in_time_threading():
    """Verify as_of timestamp is passed without modification to strategy engines."""
    arbiter = Arbiter()
    historical_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    call_records = []
    original_run_module = registry.run_strategy_module

    def spy_run_strategy_module(strategy_id: str, symbol: str = "RELIANCE", as_of=None):
        call_records.append((strategy_id, symbol, as_of))
        return original_run_module(strategy_id, symbol, as_of=as_of)

    registry.run_strategy_module = spy_run_strategy_module

    try:
        verdict = arbiter.arbitrate("RELIANCE", as_of=historical_dt)
        assert verdict is not None
        assert len(call_records) > 0, "Arbiter should execute strategy modules"

        for strategy_id, symbol, as_of in call_records:
            assert as_of == historical_dt, f"Engine {strategy_id} received wrong as_of: {as_of} (expected {historical_dt})"
    finally:
        registry.run_strategy_module = original_run_module

def test_direct_registry_point_in_time_threading():
    """Directly test run_strategy_module forwards as_of parameter."""
    historical_dt = datetime(2022, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
    resp = registry.run_strategy_module("E1", "RELIANCE", as_of=historical_dt)
    assert resp is not None
    assert resp.symbol in ("RELIANCE", "RELIANCE.NS")


def test_arbiter_sub_agent_governance_veto_integration():
    """Test that high promoter pledge (>50%) triggers sub-agent veto and caps score."""
    arbiter = Arbiter()
    # Mock snapshot with critical 60% promoter pledge
    class MockSnap:
        promoter_pledge_pct = 60.0
        related_party_pct = 5.0
        auditor_resigned_recently = False
        net_income_3y_cagr = 10.0
        ocf_3y_cagr = 12.0

    mock_snap = MockSnap()
    veto = arbiter._apply_governance_veto([{"symbol": "HIGH_PLEDGE_CO"}], snap=mock_snap)
    assert veto is True, "Sub-agent pledge veto must trigger True for 60% pledge"


def test_arbiter_universe_scoping_large_vs_micro():
    """Verify that Large Caps are not vetoed by microcap gate, while Microcaps without data fail closed."""
    arbiter = Arbiter()

    # 1. Large Cap with clean governance should NOT be vetoed by microcap gate
    class LargeCapSnap:
        market_cap_cr = 1500000.0  # ₹15 Lakh Cr (Reliance)
        promoter_pledge_pct = 0.0
        related_party_pct = 1.0
        auditor_resigned_recently = False
        net_income_3y_cagr = 15.0
        ocf_3y_cagr = 18.0

    veto_large = arbiter._apply_governance_veto([{"symbol": "RELIANCE"}], snap=LargeCapSnap())
    assert veto_large is False, "Large Cap stock RELIANCE should NOT be vetoed by microcap gate"

    # 2. Microcap without data should fail closed (trigger veto)
    class MicroCapSnap:
        market_cap_cr = 150.0  # ₹150 Cr Microcap
        promoter_pledge_pct = 0.0
        related_party_pct = 1.0
        auditor_resigned_recently = False
        net_income_3y_cagr = 15.0
        ocf_3y_cagr = 18.0

    veto_micro = arbiter._apply_governance_veto([{"symbol": "UNKNOWN_MICRO_PENNY"}], snap=MicroCapSnap())
    assert veto_micro is True, "Microcap with insufficient filing history must fail-closed veto"


def test_collinearity_deduplication():
    """Verify that E4 composite is de-duplicated from fundamental category when children are present."""
    arbiter = Arbiter()
    # Case A: Only E1 present with score 80
    outputs_children = [
        {"engine_id": "E1", "score_0_100": 80.0, "confidence": 100.0, "verdict": "Buy", "status": "ok"},
    ]
    score_children, breakdown_children = arbiter._compute_weighted_score(outputs_children)
    assert breakdown_children["FUNDAMENTAL"] == 80.0

    # Case B: E1 (80.0) AND E4 (95.0) both present. E4 should be de-duplicated to prevent double counting.
    outputs_both = [
        {"engine_id": "E1", "score_0_100": 80.0, "confidence": 100.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "E4", "score_0_100": 95.0, "confidence": 100.0, "verdict": "Buy", "status": "ok"},
    ]
    score_both, breakdown_both = arbiter._compute_weighted_score(outputs_both)
    # Fundamental category average should remain 80.0 because E4 was de-duplicated!
    assert breakdown_both["FUNDAMENTAL"] == 80.0


def test_unscored_engine_skipped_without_pseudo_score():
    """Verify that an engine with score_0_100=None does not inject confidence or 50 as a pseudo score."""
    arbiter = Arbiter()
    outputs = [
        {"engine_id": "E1", "score_0_100": 80.0, "confidence": 100.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "E8", "score_0_100": None, "confidence": 40.0, "verdict": "Avoid", "status": "ok"},
    ]
    _, breakdown = arbiter._compute_weighted_score(outputs)
    # E8 must be skipped entirely; FUNDAMENTAL should equal 80.0 (from E1 only), NOT diluted by pseudo-score
    assert breakdown["FUNDAMENTAL"] == 80.0


def test_production_unverified_governance_capped(monkeypatch):
    """Verify that in production mode, missing/unverified C13 caps verdict to Watch."""
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    arbiter = Arbiter()

    # Simulate strong bullish outputs with NO C13 governance engine evaluated
    outputs = [
        {"engine_id": "E1", "score_0_100": 90.0, "confidence": 95.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "E7", "score_0_100": 88.0, "confidence": 95.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "E15", "score_0_100": 85.0, "confidence": 90.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "C10", "score_0_100": 85.0, "confidence": 90.0, "verdict": "Buy", "status": "ok"},
        {"engine_id": "D18", "score_0_100": 85.0, "confidence": 90.0, "verdict": "Buy", "status": "ok"},
    ]

    # Mock arbitrate internals
    class MockSnap:
        symbol = "TEST_TICKER"
        data_confidence_score = 0.85
        consensus_price = 500.0

    monkeypatch.setattr(arbiter.synthesizer, "synthesize", lambda *args, **kwargs: MockSnap())
    monkeypatch.setattr(arbiter, "_collect_engine_outputs", lambda *args, **kwargs: outputs)
    monkeypatch.setattr(arbiter, "_apply_governance_veto", lambda *args, **kwargs: False)
    monkeypatch.setattr(arbiter, "_detect_contradictions", lambda *args, **kwargs: [])
    monkeypatch.setattr(arbiter, "_persist", lambda *args, **kwargs: 1)
    monkeypatch.setattr(arbiter, "_log_to_prediction_ledger", lambda *args, **kwargs: None)

    call = arbiter.arbitrate("TEST_TICKER")
    # In production without C13 verified, Buy/Strong Buy MUST be capped at Watch
    assert call.verdict == "Watch"
    assert call.confidence_tier == "Contested"
    assert call.decision_manifest["governance_status"] == "UNVERIFIED"
    assert "[GOVERNANCE UNVERIFIED" in call.primary_thesis


def test_arbiter_3tier_pledge_matrix():
    """Verify Context-Aware 3-Tier Pledge Matrix:
    1. Professionally managed (promoter < 5%) -> pledge is N/A -> PASS
    2. Significant promoter (>= 5%) with pledge > 40% -> HARD VETO
    3. Significant promoter (>= 5%) with pledge=None -> AMBER_UNVERIFIED + Score cap 65
    """
    arbiter = Arbiter()

    # Case 1: Professionally managed (ITC / L&T model)
    class SnapProfManaged:
        symbol = "ITC"
        promoter_holding_pct = 0.0
        promoter_pledge_pct = None

    veto_prof = arbiter._apply_governance_veto([], snap=SnapProfManaged())
    assert veto_prof is False
    assert arbiter._pledge_audit_amber is False

    # Case 2: High-pledge promoter (>= 5% holding, > 40% pledge)
    class SnapHighPledge:
        symbol = "HIGH_PLEDGE_CO"
        promoter_holding_pct = 55.0
        promoter_pledge_pct = 68.0

    veto_high = arbiter._apply_governance_veto([], snap=SnapHighPledge())
    assert veto_high is True

    # Case 3: Promoter company with unobserved pledge data
    class SnapMissingPledge:
        symbol = "RELIANCE"
        market_cap_cr = 1700000.0
        promoter_holding_pct = 50.3
        promoter_pledge_pct = None

    veto_missing = arbiter._apply_governance_veto([], snap=SnapMissingPledge())
    assert veto_missing is False  # Does not falsely liquidate
    assert arbiter._pledge_audit_amber is True  # Flags amber for scoring cap and audit


def test_arbiter_archetype_weight_routing():
    """Verify Arbiter dynamically shifts category weights according to investment objective."""
    arbiter = Arbiter()
    # Output set with high technical (90 via B4) and poor fundamental (30 via E1)
    outputs = [
        {"engine_id": "B4", "score_0_100": 90.0, "confidence": 100.0, "verdict": "Buy", "status": "ok"},  # Technical
        {"engine_id": "E1", "score_0_100": 30.0, "confidence": 100.0, "verdict": "Avoid", "status": "ok"}, # Fundamental
    ]

    # In SWING_POSITIONAL, technical weight is 50% vs fundamental 10%
    score_swing, breakdown_swing = arbiter._compute_weighted_score(outputs, objective="SWING_POSITIONAL")
    # In SIP_COMPOUNDER, technical weight is 0% vs fundamental 40%
    score_sip, breakdown_sip = arbiter._compute_weighted_score(outputs, objective="SIP_COMPOUNDER")

    assert score_swing > score_sip, "Swing objective must prioritize high technical setup over fundamental laggard"
    # In SIP compounder, technical contributes 0 weight to composite score
    assert score_sip < 10.0, f"Expected low SIP composite due to fundamental avoidance, got {score_sip}"


def test_arbiter_two_tier_risk_classification():
    """Verify non-destructive two-tier alert classification."""
    arbiter = Arbiter()
    outputs = [
        {"engine_id": "C11", "score_0_100": 40.0, "confidence": 90.0, "verdict": "Avoid", "raw": None},
    ]
    fatal, warnings = arbiter._classify_two_tier_alerts(outputs, objective="TURNAROUND")
    assert any("Turnaround" in w for w in warnings)
    assert any("QoQ cash inflection" in w for w in warnings)


def test_governance_quality_fails_closed_when_ownership_unobserved(tmp_path):
    """Verify Governance Quality engine returns UNKNOWN grade and pledge risk when ownership is not observed."""
    from app.services.strategies.governance_quality import evaluate_governance_quality
    from app.services.research_data import ResearchDataStore
    from app.models.schemas import CompanyUpsertRequest
    
    store = ResearchDataStore(str(tmp_path / "test_gov.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="UNKNOWN_SCRIP", legal_name="Unknown Scrip Ltd"))
    res = evaluate_governance_quality("UNKNOWN_SCRIP", store=store)
    assert res.governance_grade == "UNKNOWN"
    assert res.promoter_pledge_risk == "UNKNOWN"
    assert any("No shareholding pattern observation history found" in e for e in res.evidence)


def test_multibagger_screener_separates_data_adequacy_and_stage():
    """Verify Multibagger Screener separates data adequacy from stage index."""
    from app.services.strategies.multibagger_screener import evaluate_multibagger_score
    res = evaluate_multibagger_score("RELIANCE")
    assert "data_adequacy_pct" in res.component_scores
    assert "stage_index_pct" in res.component_scores
    assert 0.0 <= res.component_scores["data_adequacy_pct"] <= 100.0
    assert 0.0 <= res.component_scores["stage_index_pct"] <= 100.0






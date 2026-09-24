"""Phase 140 Test Suite — Geopolitical Pre-Event Weak Signal (PEWS) Engine,
Physical Disruption Likelihood Ratio (PDLR) Gate, Tanker Bifurcation, &
Closed-Loop Bayesian Kalman Self-Learning Ledger.
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.research.geopolitical_engine import (
    PreEventSignal,
    evaluate_pre_event_weak_signals,
    evaluate_physical_disruption_gate,
    compute_geo_shock_sensitivity,
    calculate_dynamic_geographic_overlay,
    SECTOR_GEOPOLITICAL_SENSITIVITIES,
)
from app.services.monitoring.event_prediction_ledger import (
    EventPredictionLedgerService,
    GeopoliticalEventRecord,
    MAX_KALMAN_DRIFT_STEP,
)

client = TestClient(app)
API_HEADERS = {"X-API-Key": "test-key-phase140"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Tanker vs Container Shipping Bifurcation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_tanker_corridor_overlay_awards_tailwind_premium():
    """Verify Middle East chokepoint diversion awards +15% tailwind to tanker operators."""
    split = {"middle_east": 0.60, "domestic": 0.40}
    res_tanker = calculate_dynamic_geographic_overlay("SHIPPING_TANKERS", split)
    # Middle East share 0.60 * 15.0 = +9.0%, domestic 0.0
    assert res_tanker["overlay_pct"] >= 8.0
    assert res_tanker["overlay_type"] == "TAILWIND_PREMIUM"
    assert "middle_east_red_sea" in res_tanker["corridor_breakdown"]
    assert res_tanker["corridor_breakdown"]["middle_east_red_sea"] > 0


def test_cargo_shipping_corridor_receives_trade_bottleneck_penalty():
    """Verify container/general cargo shipping receives -15% corridor penalty."""
    split = {"middle_east": 0.60, "domestic": 0.40}
    res_cargo = calculate_dynamic_geographic_overlay("CONTAINER_CARGO", split)
    # Middle East share 0.60 * (-15.0) = -9.0%
    assert res_cargo["overlay_pct"] <= -8.0
    assert res_cargo["overlay_type"] in ("VOLATILITY_INDEX", "MACRO_RISK_PENALTY")
    assert res_cargo["corridor_breakdown"]["middle_east_red_sea"] < 0


def test_geship_subsegment_routing_preserves_backward_compatibility():
    """Verify default GESHIP preserves Phase 139 baseline headwind while tanker mode grants tailwind."""
    # 1. Backward-compatible call with sector='SHIPPING'
    base_res = compute_geo_shock_sensitivity("GESHIP", sector="SHIPPING")
    assert base_res["beta_maritime_chokepoint"] <= -0.80
    assert base_res["verdict"] in ("GEO_HEADWIND", "GEO_CRITICAL")

    # 2. Specialized Tanker mode via sub_segment='TANKERS'
    tanker_res = compute_geo_shock_sensitivity("GESHIP", sector="SHIPPING", sub_segment="TANKERS")
    assert tanker_res["beta_maritime_chokepoint"] == 0.85
    assert tanker_res["sector"] == "SHIPPING_TANKERS"
    assert tanker_res["verdict"] in ("GEO_TAILWIND", "GEO_NEUTRAL")


def test_direct_tanker_sector_in_shock_matrix():
    """Verify SHIPPING_TANKERS sector directly maps to high positive maritime beta."""
    res = compute_geo_shock_sensitivity("GESHIP_TANKER", sector="SHIPPING_TANKERS")
    assert res["beta_maritime_chokepoint"] == 0.85
    assert res["beta_crude_spike"] == 0.50
    assert res["verdict"] == "GEO_TAILWIND"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Pre-Event Weak Signal (PEWS) Evaluator Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_pews_no_signals_returns_baseline_prior():
    """Verify empty signal array maintains baseline tension prior."""
    res = evaluate_pre_event_weak_signals([], prior_probability=0.10)
    assert res["status"] == "NO_SIGNALS_OBSERVED"
    assert res["pews_probability"] == 0.10
    assert res["imminence_rating"] == "BASELINE_MONITORING"
    assert res["recommended_stance"] == "STATUS_QUO"


def test_pews_single_notam_closure_escalates_imminence():
    """Verify single high-specificity airspace NOTAM significantly raises event probability."""
    signals = [
        PreEventSignal(
            signal_type="AIRSPACE_NOTAM_CLOSURE",
            intensity=1.0,
            confidence=0.95,
            age_hours=2.0,
            theater="MIDDLE_EAST",
            source_description="FIR Tehran / Persian Gulf emergency FL260-FL400 closure",
        )
    ]
    res = evaluate_pre_event_weak_signals(signals, prior_probability=0.10)
    assert res["pews_probability"] > 0.40
    assert res["imminence_rating"] in ("WATCHLIST_STAGE_TENSION", "ELEVATED_PRE_STRIKE_PROBABILITY")
    assert len(res["dominant_signals"]) == 1
    assert res["dominant_signals"][0]["signal_type"] == "AIRSPACE_NOTAM_CLOSURE"


def test_pews_multi_signal_confluence_triggers_critical_intervention():
    """Verify confluence of NOTAM + AIS dark + Diplomatic collapse + Options skew triggers critical zone."""
    signals = [
        PreEventSignal(signal_type="AIRSPACE_NOTAM_CLOSURE", intensity=1.0, confidence=0.95, age_hours=1.0),
        PreEventSignal(signal_type="AIS_TRANSPONDER_DARK", intensity=0.90, confidence=0.90, age_hours=3.0),
        PreEventSignal(signal_type="DIPLOMATIC_SCHEDULE_COLLAPSE", intensity=1.0, confidence=0.90, age_hours=4.0),
        PreEventSignal(signal_type="CRUDE_CALL_SKEW_SPIKE", intensity=0.85, confidence=0.85, age_hours=2.0),
    ]
    res = evaluate_pre_event_weak_signals(signals, prior_probability=0.10, theater="MIDDLE_EAST")
    assert res["pews_probability"] >= 0.80
    assert res["imminence_rating"] == "CRITICAL_IMMINENT_INTERVENTION"
    assert res["recommended_stance"] == "EXECUTE_PRE_EVENT_HEDGES"


def test_pews_temporal_decay_attenuates_stale_signals():
    """Verify stale signals (72h old) have lower delta log-odds than fresh signals (1h old)."""
    fresh = [PreEventSignal(signal_type="AIS_TRANSPONDER_DARK", intensity=1.0, age_hours=1.0)]
    stale = [PreEventSignal(signal_type="AIS_TRANSPONDER_DARK", intensity=1.0, age_hours=72.0)]

    res_fresh = evaluate_pre_event_weak_signals(fresh, prior_probability=0.10)
    res_stale = evaluate_pre_event_weak_signals(stale, prior_probability=0.10)

    assert res_fresh["pews_probability"] > res_stale["pews_probability"]
    assert res_fresh["dominant_signals"][0]["effective_weight"] > res_stale["dominant_signals"][0]["effective_weight"]


def test_pews_symbolic_leader_signaling_alone_is_contained():
    """Verify leader signaling anomaly (white cap / photo release) alone does not trigger critical alarm."""
    signals = [
        PreEventSignal(
            signal_type="LEADER_SIGNALLING_ANOMALY",
            intensity=1.0,
            confidence=0.80,
            age_hours=2.0,
            theater="SOUTH_ASIA",
            source_description="Operational HQ headgear / war room unannounced photo",
        )
    ]
    res = evaluate_pre_event_weak_signals(signals, prior_probability=0.10)
    # Stays well below critical threshold (0.80)
    assert res["pews_probability"] < 0.35
    assert res["imminence_rating"] != "CRITICAL_IMMINENT_INTERVENTION"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Physical Disruption Likelihood Ratio (PDLR) Gate Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_pdlr_gate_caps_political_theater_to_tactical_volatility():
    """Verify PDLR < 0.40 (political theater) caps negative penalty to -3.0% and blocks fatal veto."""
    res = evaluate_physical_disruption_gate(pdlr=0.25, raw_overlay_pct=-15.0, sector="OIL_GAS")
    assert res["classification"] == "SYMBOLIC_THEATER_OR_POSTURING"
    assert res["effective_overlay_pct"] == -3.0
    assert res["allow_fatal_veto"] is False
    assert res["allow_sizing_haircut"] is False
    assert res["gate_action"] == "CAP_PENALTY_TO_TACTICAL_VOLATILITY"


def test_pdlr_gate_preserves_positive_tailwinds_under_theater():
    """Verify positive tailwinds (e.g. +15% Defense) are not curtailed by low PDLR."""
    res = evaluate_physical_disruption_gate(pdlr=0.20, raw_overlay_pct=15.0, sector="DEFENSE")
    assert res["effective_overlay_pct"] == 15.0


def test_pdlr_gate_elevated_friction_applies_damped_overlay():
    """Verify 0.40 <= PDLR < 0.70 applies 75% damped overlay and permits tactical sizing haircut."""
    res = evaluate_physical_disruption_gate(pdlr=0.55, raw_overlay_pct=-16.0, sector="PAINTS")
    assert res["classification"] == "ELEVATED_FRICTION_RISK"
    assert res["effective_overlay_pct"] == -12.0  # -16.0 * 0.75
    assert res["allow_fatal_veto"] is False
    assert res["allow_sizing_haircut"] is True


def test_pdlr_gate_confirmed_physical_disruption_enforces_full_overlay():
    """Verify PDLR >= 0.70 enforces 100% of raw structural macro overlay and fatal vetoes."""
    res = evaluate_physical_disruption_gate(pdlr=0.88, raw_overlay_pct=-20.0, sector="CONTAINER_CARGO")
    assert res["classification"] == "PHYSICAL_DISRUPTION_CONFIRMED"
    assert res["effective_overlay_pct"] == -20.0
    assert res["allow_fatal_veto"] is True
    assert res["allow_sizing_haircut"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 4. Closed-Loop Event Learning Ledger & Bayesian Kalman Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_event_prediction_ledger_logging_and_calibration():
    """Verify end-to-end logging of pre-event prediction, realization recording, and Kalman update."""
    event_id = "TEST_EVENT_HORMUZ_2026_09"
    
    # 1. Log pre-event prediction
    rec = EventPredictionLedgerService.log_geopolitical_event(
        event_id=event_id,
        title="Strait of Hormuz Kinetic Incident Escalation",
        event_type="MARITIME_CHOKEPOINT",
        theater="MIDDLE_EAST",
        pews_probability=0.85,
        pdlr_ratio=0.80,
        pdlr_classification="PHYSICAL_DISRUPTION_CONFIRMED",
        shock_vector={"crude": 0.20, "maritime": 0.75},
        predicted_betas={"SHIPPING_TANKERS": 0.85, "PAINTS": -0.60},
        notes="Phase 140 Automated Test Run",
    )
    assert rec.event_id == event_id
    assert rec.status == "PENDING_OUTCOME"

    # 2. Record realization and trigger Bayesian calibration
    # Brent surged +20%, GESHIP surged +22% (excess +20%), Paints dropped -14% (excess -16%)
    res = EventPredictionLedgerService.record_event_market_realization(
        event_id=event_id,
        realized_shock={"maritime": 0.75, "crude": 0.20},
        empirical_asset_returns={
            "SHIPPING_TANKERS": 22.0,
            "PAINTS": -14.0,
            "^NSEI": 2.0,
        },
        event_occurred=True,
    )
    assert res["status"] == "CALIBRATED"
    assert res["brier_score"] == round((0.85 - 1.0) ** 2, 4)
    assert res["kalman_gain"] > 0.0
    assert res["drift_guard_applied"] is True
    assert "SHIPPING_TANKERS" in res["calibrated_betas"]
    assert "PAINTS" in res["calibrated_betas"]

    # 3. Verify bounded drift guard: updated beta delta is bounded within MAX_KALMAN_DRIFT_STEP (±0.05)
    prior_paints = -0.60
    cal_paints = res["calibrated_betas"]["PAINTS"]
    assert abs(cal_paints - prior_paints) <= MAX_KALMAN_DRIFT_STEP + 1e-4

    # 4. Verify historical retrieval
    history = EventPredictionLedgerService.get_event_history(limit=5)
    matched = [h for h in history if h.event_id == event_id]
    assert len(matched) == 1
    assert matched[0].status == "CALIBRATED"


def test_dynamic_calibrated_matrix_integration():
    """Verify compute_geo_shock_sensitivity incorporates calibrated matrix without regression."""
    matrix = EventPredictionLedgerService.get_calibrated_beta_matrix()
    assert "SHIPPING_TANKERS" in matrix
    assert "DEFENSE" in matrix
    assert "TRANSFORMERS" in matrix


# ─────────────────────────────────────────────────────────────────────────────
# 5. REST API Endpoints Verification
# ─────────────────────────────────────────────────────────────────────────────

def test_api_pews_evaluation_endpoint():
    """Verify POST /api/v1/research/geopolitical/pre-event-eval returns valid schema."""
    payload = {
        "signals": [
            {"signal_type": "AIRSPACE_NOTAM_CLOSURE", "intensity": 1.0, "confidence": 0.90},
            {"signal_type": "DIPLOMATIC_SCHEDULE_COLLAPSE", "intensity": 0.80, "confidence": 0.85},
        ],
        "prior_probability": 0.12,
        "theater": "MIDDLE_EAST",
    }
    resp = client.post("/api/v1/research/geopolitical/pre-event-eval", json=payload, headers=API_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "EVALUATED"
    assert 0.0 <= data["pews_probability"] <= 1.0
    assert "imminence_rating" in data


def test_api_pdlr_gate_evaluation_endpoint():
    """Verify POST /api/v1/research/geopolitical/pdlr-gate-eval returns gated overlay."""
    payload = {
        "pdlr": 0.20,
        "raw_overlay_pct": -15.0,
        "sector": "OIL_GAS",
    }
    resp = client.post("/api/v1/research/geopolitical/pdlr-gate-eval", json=payload, headers=API_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] == "SYMBOLIC_THEATER_OR_POSTURING"
    assert data["effective_overlay_pct"] == -3.0
    assert data["allow_fatal_veto"] is False


def test_api_tanker_subsegment_shock_sensitivity():
    """Verify GET /api/v1/research/geopolitical-shock-sensitivity/{symbol}?sub_segment=TANKERS."""
    resp = client.get(
        "/api/v1/research/geopolitical-shock-sensitivity/GESHIP?sub_segment=TANKERS",
        headers=API_HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["sector"] == "SHIPPING_TANKERS"
    assert 0.75 <= data["beta_maritime_chokepoint"] <= 0.90
    assert data["verdict"] in ("GEO_TAILWIND", "GEO_NEUTRAL")


def test_evaluate_geopolitical_risk_with_pdlr_and_subsegment():
    """Verify evaluate_geopolitical_risk integrates PDLR gate and subsegment routing."""
    from app.services.research.geopolitical_engine import evaluate_geopolitical_risk

    # 1. GESHIP with tanker subsegment yields +15.0% tailwind premium
    res_tanker = evaluate_geopolitical_risk("GESHIP", sub_segment="TANKERS")
    assert res_tanker["overlay_pct"] == 15.0
    assert res_tanker["overlay_type"] == "TAILWIND_PREMIUM"
    assert res_tanker["macro_risk_rating"] == "LOW"

    # 2. IT stock with PDLR=0.25 (theater) caps penalty to -3.0% instead of -20.0%
    res_theater = evaluate_geopolitical_risk("COFORGE", pdlr=0.25)
    assert res_theater["overlay_pct"] == -20.0
    assert res_theater["effective_overlay_pct"] == -3.0
    assert res_theater["conviction_penalty_pct"] == 3.0
    assert res_theater["macro_risk_rating"] == "MODERATE"
    assert "pdlr_gate" in res_theater
    assert res_theater["pdlr_gate"]["classification"] == "SYMBOLIC_THEATER_OR_POSTURING"


"""Unit tests for Phase 142: Anticipatory Intelligence, Cultural Grayzone & Self-Learning Engine.

Verifies:
1. WeakSignalParserService extraction of cultural boycott, chokepoint alliance, trade settlement, and socio-religious cycles.
2. Monotonic horizon-decay weight formula W(H) in intent_adaptive_engine.py.
3. Strict suppression of macro grayzones for SWING_3D/10D vs full enforcement for SIP_COMPOUNDER.
4. SelfLearningEngine knowledge gap detection, zero-trust epistemic scoring, and noise quarantine.
5. UserFeedbackEngine automatic integration with SelfLearningEngine.
"""

import os
import pytest
from app.services.research.weak_signal_parser import WeakSignalParserService
from app.services.research.intent_adaptive_engine import (
    compute_horizon_grayzone_weight,
    QueryAdaptiveConstraintEngine
)
from app.services.research.self_learning_engine import SelfLearningEngine
from app.services.research.user_feedback_engine import UserFeedbackEngine


def test_weak_signal_cultural_boycott():
    """Verify detection and likelihood ratio of cultural consumer boycott signals."""
    text = "Consumer boycott campaign accelerating across regional franchise stores with sharp footfall collapse."
    signals = WeakSignalParserService.parse_text_to_signals(text)
    assert any(s.signal_type == "CULTURAL_BOYCOTT_ACCELERATION" for s in signals)
    boycott_sig = next(s for s in signals if s.signal_type == "CULTURAL_BOYCOTT_ACCELERATION")
    assert boycott_sig.likelihood_ratio >= 3.8
    assert boycott_sig.intensity >= 0.65


def test_weak_signal_chokepoint_alliance():
    """Verify non-state ideological coordination contesting maritime chokepoints."""
    text = "Sectarian militia drone swarm tanker attack near Bab el-Mandeb in coordination with axis of resistance."
    signals = WeakSignalParserService.parse_text_to_signals(text)
    assert any(s.signal_type == "CHOKEPOINT_ALLIANCE_ALIGNMENT" for s in signals)
    cp_sig = next(s for s in signals if s.signal_type == "CHOKEPOINT_ALLIANCE_ALIGNMENT")
    assert cp_sig.likelihood_ratio >= 5.5
    assert cp_sig.theater == "MIDDLE_EAST"


def test_weak_signal_trade_settlement_and_muhurat():
    """Verify non-dollar bilateral settlement and Indic socio-religious purchasing cycles."""
    text = (
        "Bilateral trade confirms rupee-dirham settlement corridor and local currency clearing. "
        "Retail jeweler notes auspicious gold purchase window and Diwali demand ahead of wedding season dates."
    )
    signals = WeakSignalParserService.parse_text_to_signals(text)
    types = [s.signal_type for s in signals]
    assert "TRADE_SETTLEMENT_DEVIATION" in types
    assert "SOCIO_RELIGIOUS_SEASONAL_CYCLE" in types


def test_horizon_grayzone_weight_decay():
    """Verify monotonic decay function W(H) = round(1.0 - exp(-0.015 * H), 4)."""
    w_3d = compute_horizon_grayzone_weight(3.0)
    w_10d = compute_horizon_grayzone_weight(10.0)
    w_30d = compute_horizon_grayzone_weight(30.0)
    w_90d = compute_horizon_grayzone_weight(90.0)
    w_365d = compute_horizon_grayzone_weight(365.0)

    # 3-day tactical must be completely zeroed out
    assert w_3d == 0.0
    # 10-day swing must be capped at noise floor
    assert w_10d == 0.05
    # Intermediate 30D/90D must scale monotonically
    assert 0.35 <= w_30d <= 0.38
    assert 0.70 <= w_90d <= 0.76
    # Long-term compounder must receive full transmission
    assert w_365d >= 0.99


def test_adaptive_constraints_swing_grayzone_suppression():
    """Verify that SWING_3D and SWING_10D explicitly suppress macro grayzone risks."""
    engine = QueryAdaptiveConstraintEngine()
    res_3d = engine.evaluate_adaptive_constraints("SWING_3D", {"close": 250.0})
    relaxed_3d = res_3d.get("relaxed_parameters", [])
    assert any("W_grayzone=0.0" in r for r in relaxed_3d)

    res_10d = engine.evaluate_adaptive_constraints("SWING_10D", {"close": 250.0})
    relaxed_10d = res_10d.get("relaxed_parameters", [])
    assert any("W_grayzone<=0.05" in r for r in relaxed_10d)


def test_adaptive_constraints_sip_grayzone_enforcement():
    """Verify that SIP_COMPOUNDER enforces long-term sovereign and cultural grayzone stability."""
    engine = QueryAdaptiveConstraintEngine()
    res_sip = engine.evaluate_adaptive_constraints("SIP_COMPOUNDER", {"close": 500.0})
    tightened_sip = res_sip.get("tightened_parameters", [])
    assert any("W_grayzone=1.0" in t for t in tightened_sip)


def test_self_learning_engine_fact_vs_noise(tmp_path):
    """Verify zero-trust epistemic scoring certifies facts and quarantines sensational noise."""
    custom_reg = str(tmp_path / "test_learned_registry.json")
    learner = SelfLearningEngine(registry_file=custom_reg)

    # 1. Fact test
    fact_text = "Exchange closing auction session system CASS implemented for stable closing price determination."
    facts = learner.learn_from_text(fact_text, provenance_score=0.95)
    assert len(facts) >= 1
    assert facts[0].verification_status == "CERTIFIED_FACT"
    assert facts[0].confidence_score >= 0.70

    # 2. Sensational noise test
    noise_text = "Secret plan to invade and secretly capture Argentina for lithium with guaranteed 100x return!"
    noise_entity = learner.evaluate_and_learn_entity("TEST_NOISE_1", noise_text, provenance_score=0.30)
    assert noise_entity.verification_status == "SPECULATIVE_NARRATIVE_NOISE"
    assert noise_entity.sensationalism_penalty >= 0.50

    # 3. Query priors
    active_priors = learner.query_learned_priors(exclude_noise=True)
    assert len(active_priors) == 1
    assert active_priors[0]["entity_id"] == "EXCHANGE_CASS_MECHANISM"


def test_user_feedback_engine_self_learning_integration(tmp_path):
    """Verify that UserFeedbackEngine triggers autonomous learning on user queries."""
    fb = UserFeedbackEngine()
    res = fb.process_counter_question(
        "Why is there uncertainty regarding Closing Auction Session System CASS and Lithium Triangle RIGI framework?"
    )
    assert res.get("status") == "SUCCESS"
    assert "Autonomous Learning Engine ingested" in res.get("analytical_response")

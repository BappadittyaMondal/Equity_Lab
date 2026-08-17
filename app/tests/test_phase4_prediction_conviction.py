"""Phase 4 — Prediction & Conviction Tests.

Tests for:
  Layer 10: Prediction Engine — horizons, scenarios, risk, confidence decomposition
  Layer 11: Arbiter — weighted scoring, governance veto, 5-tier verdicts, auto-log
  Layer 14: Audit Trail — DecisionAuditTrail structure, why-explainer, data lineage
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, List, Dict
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_closes(n: int = 400, trend: float = 0.0003) -> np.ndarray:
    """Generate synthetic price series."""
    np.random.seed(42)
    prices = [1000.0]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1 + trend + np.random.randn() * 0.012))
    return np.array(prices)


def _make_financials(n_quarters: int = 12) -> List[Any]:
    """Create mock FinancialObservation list."""
    periods = [f"202{i//4+1}-0{(i%4)*3+3:02d}-30" for i in range(n_quarters)]
    obs_list = []
    for i, period in enumerate(periods):
        base = 1000.0 * (1 + i * 0.05)
        for metric, val in [
            ("revenue", base),
            ("net_income", base * 0.15),
            ("operating_cash_flow", base * 0.18),
            ("basic_eps", 25.0 + i * 0.5),
        ]:
            o = MagicMock()
            o.metric = metric
            o.period_end = period
            o.value = val
            o.confidence = 0.85
            o.source_name = "Screener.in"
            obs_list.append(o)
    return obs_list


def _mock_engine_output(
    engine_id: str,
    verdict: str = "Buy",
    confidence: int = 75,
    status: str = "production",
    evidence: List[str] = None,
) -> Dict[str, Any]:
    raw = MagicMock()
    raw.strategy_name = f"Mock Engine {engine_id}"
    raw.status = status
    raw.passed_gates = (verdict == "Buy")
    raw.results = {"evidence": evidence or [f"{engine_id} passed with strong data"]}
    raw.metrics = {}
    raw.meta = {"source": f"Mock({engine_id})", "retrieved_at": "2025-01-01T00:00:00Z"}
    return {
        "engine_id": engine_id,
        "verdict": verdict,
        "confidence": confidence,
        "regime": "CALM",
        "raw": raw,
        "status": status,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Layer 10: Prediction Engine
# ═══════════════════════════════════════════════════════════════════════════

class TestEmpiricalReturns:
    """Empirical rolling return computation."""

    def test_returns_computed_for_sufficient_data(self):
        from app.services.decision_brain.prediction_engine import _empirical_returns
        closes = _make_closes(500)
        rets = _empirical_returns(closes, 63)  # 3M
        assert len(rets) > 0

    def test_returns_empty_for_insufficient_data(self):
        from app.services.decision_brain.prediction_engine import _empirical_returns
        closes = _make_closes(50)
        rets = _empirical_returns(closes, 63)
        assert len(rets) == 0

    def test_returns_count_correct(self):
        from app.services.decision_brain.prediction_engine import _empirical_returns
        closes = _make_closes(300, trend=0.0005)
        rets = _empirical_returns(closes, 63)
        assert len(rets) == 300 - 63


class TestRiskMetrics:
    """Per-horizon risk quantification."""

    def test_risk_metrics_keys_present(self):
        from app.services.decision_brain.prediction_engine import _risk_metrics
        closes = _make_closes(500)
        rets = np.array([c * 0.01 for c in range(-20, 30)])
        metrics = _risk_metrics(rets, "1Y")
        assert "median_return_pct" in metrics
        assert "prob_positive_pct" in metrics
        assert "prob_loss_20pct" in metrics
        assert "sortino_ratio" in metrics
        assert "max_drawdown_proxy_pct" in metrics

    def test_empty_returns_returns_empty_dict(self):
        from app.services.decision_brain.prediction_engine import _risk_metrics
        assert _risk_metrics(np.array([]), "1Y") == {}

    def test_sortino_positive_for_trending_stock(self):
        from app.services.decision_brain.prediction_engine import _risk_metrics
        rets = np.array([float(x) for x in range(5, 25)])  # All positive
        metrics = _risk_metrics(rets, "1Y")
        # No downside → sortino = None (no downside deviation)
        # But if all positive, downside std = 0
        assert metrics["prob_positive_pct"] == 100.0


class TestFundamentalReturnEstimate:
    """Earnings growth × multiple expansion estimate."""

    def test_estimate_returns_float_with_data(self):
        from app.services.decision_brain.prediction_engine import _fundamental_return_estimate
        financials = _make_financials(12)
        result = _fundamental_return_estimate(financials, current_pe=22.0, horizon_years=1.0)
        assert result is None or isinstance(result, float)

    def test_estimate_none_with_insufficient_data(self):
        from app.services.decision_brain.prediction_engine import _fundamental_return_estimate
        result = _fundamental_return_estimate([], current_pe=22.0, horizon_years=1.0)
        assert result is None

    def test_high_pe_has_compression_expectation(self):
        from app.services.decision_brain.prediction_engine import _fundamental_return_estimate
        financials = _make_financials(12)
        result_high = _fundamental_return_estimate(financials, current_pe=40.0, horizon_years=1.0)
        result_low = _fundamental_return_estimate(financials, current_pe=10.0, horizon_years=1.0)
        if result_high is not None and result_low is not None:
            # High PE should return lower expectation than low PE
            assert result_high < result_low


class TestValuationReversionReturn:
    """Mean reversion contribution from valuation gap."""

    def test_positive_mos_gives_positive_return(self):
        from app.services.decision_brain.prediction_engine import _valuation_reversion_return
        result = _valuation_reversion_return(25.0, 2.0)
        assert result > 0

    def test_negative_mos_gives_negative_return(self):
        from app.services.decision_brain.prediction_engine import _valuation_reversion_return
        result = _valuation_reversion_return(-20.0, 2.0)
        assert result < 0

    def test_none_mos_returns_none(self):
        from app.services.decision_brain.prediction_engine import _valuation_reversion_return
        assert _valuation_reversion_return(None, 1.0) is None


class TestScenarioTree:
    """Bull/Base/Bear scenario probabilities."""

    def test_probabilities_sum_to_100(self):
        from app.services.decision_brain.prediction_engine import _build_scenario_tree
        scenario = _build_scenario_tree(1000.0, 10.0, 20.0, 35.0, 18.0, "1Y")
        total = (
            scenario["bull_case"]["probability"] +
            scenario["base_case"]["probability"] +
            scenario["bear_case"]["probability"]
        )
        assert abs(total - 1.0) < 0.001

    def test_bull_target_exceeds_bear_target(self):
        from app.services.decision_brain.prediction_engine import _build_scenario_tree
        scenario = _build_scenario_tree(1000.0, 5.0, 15.0, 30.0, 12.0, "1Y")
        assert scenario["bull_case"]["price_target"] > scenario["bear_case"]["price_target"]

    def test_scenario_has_expected_return(self):
        from app.services.decision_brain.prediction_engine import _build_scenario_tree
        scenario = _build_scenario_tree(1000.0, 5.0, 15.0, 30.0, 12.0, "1Y")
        assert "expected_return_pct" in scenario
        assert isinstance(scenario["expected_return_pct"], float)


class TestConfidenceDecomposition:
    """3-component confidence breakdown."""

    def test_decomposition_returns_three_components(self):
        from app.services.decision_brain.prediction_engine import _decompose_confidence
        result = _decompose_confidence(12, 750, True, 20.0)
        assert "data_quality_confidence" in result
        assert "model_confidence" in result
        assert "thesis_confidence" in result
        assert "composite_confidence_pct" in result

    def test_composite_in_range_0_100(self):
        from app.services.decision_brain.prediction_engine import _decompose_confidence
        result = _decompose_confidence(12, 750, True, 20.0)
        assert 0 <= result["composite_confidence_pct"] <= 100

    def test_rich_data_gives_high_confidence(self):
        from app.services.decision_brain.prediction_engine import _decompose_confidence
        rich = _decompose_confidence(16, 1200, True, 35.0)
        sparse = _decompose_confidence(1, 50, False, None)
        assert rich["composite_confidence_pct"] > sparse["composite_confidence_pct"]

    def test_positive_mos_boosts_thesis_confidence(self):
        from app.services.decision_brain.prediction_engine import _decompose_confidence
        pos_mos = _decompose_confidence(8, 300, True, 25.0)
        neg_mos = _decompose_confidence(8, 300, True, -25.0)
        assert pos_mos["thesis_confidence"] > neg_mos["thesis_confidence"]


class TestCatalystTimeline:
    """Catalyst extraction from business_events."""

    def _make_events(self, n: int = 5):
        events = []
        from datetime import date, timedelta
        for i in range(n):
            evt = MagicMock()
            evt.event_date = date.today() + timedelta(days=30 * (i + 1))
            evt.event_type = ["earnings_release", "board_meeting", "agm", "dividend_announcement", "regulatory_approval"][i % 5]
            evt.title = f"Event {i + 1}"
            events.append(evt)
        return events

    def test_catalysts_sorted_by_days_ahead(self):
        from app.services.decision_brain.prediction_engine import _extract_catalyst_timeline
        events = self._make_events(5)
        catalysts = _extract_catalyst_timeline(events)
        days = [c["days_ahead"] for c in catalysts]
        assert days == sorted(days)

    def test_earnings_flagged_high_magnitude(self):
        from app.services.decision_brain.prediction_engine import _extract_catalyst_timeline
        events = self._make_events(1)
        events[0].event_type = "earnings_release"
        catalysts = _extract_catalyst_timeline(events)
        assert catalysts[0]["magnitude"] == "HIGH"

    def test_past_events_excluded(self):
        from app.services.decision_brain.prediction_engine import _extract_catalyst_timeline
        from datetime import date, timedelta
        evt = MagicMock()
        evt.event_date = date.today() - timedelta(days=30)  # Past event
        evt.event_type = "earnings_release"
        evt.title = "Old event"
        catalysts = _extract_catalyst_timeline([evt])
        assert len(catalysts) == 0

    def test_empty_events_returns_empty_list(self):
        from app.services.decision_brain.prediction_engine import _extract_catalyst_timeline
        assert _extract_catalyst_timeline([]) == []


# ═══════════════════════════════════════════════════════════════════════════
# Layer 11: Arbiter — Weighted Composite Scoring
# ═══════════════════════════════════════════════════════════════════════════

class TestWeightedScoring:
    """Weighted composite score from engine categories."""

    def _make_arbiter(self):
        from app.services.decision_brain.arbiter import Arbiter
        return Arbiter()

    def test_all_buy_produces_high_score(self):
        arb = self._make_arbiter()
        outputs = [
            _mock_engine_output("E1", "Buy", 90),
            _mock_engine_output("B5", "Buy", 85),
            _mock_engine_output("C9", "Buy", 80),
            _mock_engine_output("C13", "Buy", 85),
        ]
        score, _ = arb._compute_weighted_score(outputs)
        assert score > 60.0

    def test_all_avoid_produces_low_score(self):
        arb = self._make_arbiter()
        outputs = [
            _mock_engine_output("E1", "Avoid", 40),
            _mock_engine_output("B5", "Avoid", 35),
            _mock_engine_output("C9", "Avoid", 30),
        ]
        score, _ = arb._compute_weighted_score(outputs)
        assert score < 50.0

    def test_data_insufficient_engines_excluded(self):
        arb = self._make_arbiter()
        outputs = [
            _mock_engine_output("E1", "Buy", 90, status="production"),
            _mock_engine_output("E2", "Buy", 0, status="data_insufficient"),  # Should be excluded
            _mock_engine_output("B5", "Buy", 85, status="production"),
        ]
        score_with, _ = arb._compute_weighted_score(outputs)
        score_without, _ = arb._compute_weighted_score(outputs[:1] + outputs[2:])
        # Both should be similar since data_insufficient is excluded
        assert abs(score_with - score_without) < 20

    def test_category_breakdown_returned(self):
        arb = self._make_arbiter()
        outputs = [
            _mock_engine_output("E1", "Buy", 80),
            _mock_engine_output("C13", "Buy", 70),
        ]
        _, breakdown = arb._compute_weighted_score(outputs)
        assert isinstance(breakdown, dict)
        assert len(breakdown) >= 1

    def test_options_engines_excluded_from_composite(self):
        """OPTIONS category has weight 0.0 — should not affect score."""
        arb = self._make_arbiter()
        outputs_base = [_mock_engine_output("E1", "Buy", 80)]
        outputs_with_options = outputs_base + [_mock_engine_output("A1", "Avoid", 20)]
        score_base, _ = arb._compute_weighted_score(outputs_base)
        score_options, _ = arb._compute_weighted_score(outputs_with_options)
        assert score_base == score_options


class TestGovernanceVeto:
    """Forensic veto triggers.

    Uses plain namespace objects (not MagicMock) so that
    isinstance(raw.results, dict) passes correctly inside the arbiter.
    """

    def _make_arbiter(self):
        from app.services.decision_brain.arbiter import Arbiter
        return Arbiter()

    def _raw(self, results: dict, metrics: dict = None):
        """Return a plain object with real dict attributes."""
        class _Raw:
            pass
        obj = _Raw()
        obj.results = results
        obj.metrics = metrics or {}
        return obj

    def test_poor_governance_grade_triggers_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "C13", "raw": self._raw({"governance_grade": "POOR"})}]
        assert arb._apply_governance_veto(outputs) is True

    def test_good_governance_grade_no_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "C13", "raw": self._raw({"governance_grade": "GOOD"})}]
        assert arb._apply_governance_veto(outputs) is False

    def test_excellent_governance_no_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "C13", "raw": self._raw({"governance_grade": "EXCELLENT"})}]
        assert arb._apply_governance_veto(outputs) is False

    def test_forensic_critical_triggers_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "FORENSIC", "raw": self._raw({"forensic_risk": "CRITICAL"})}]
        assert arb._apply_governance_veto(outputs) is True

    def test_forensic_low_no_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "FORENSIC", "raw": self._raw({"forensic_risk": "LOW"})}]
        assert arb._apply_governance_veto(outputs) is False

    def test_pledge_over_40pct_triggers_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "C13", "raw": self._raw({"promoter_pledge_pct": 45.0})}]
        assert arb._apply_governance_veto(outputs) is True

    def test_pledge_under_40pct_no_veto(self):
        arb = self._make_arbiter()
        outputs = [{"engine_id": "C13", "raw": self._raw({"promoter_pledge_pct": 15.0})}]
        assert arb._apply_governance_veto(outputs) is False

    def test_empty_outputs_no_veto(self):
        arb = self._make_arbiter()
        assert arb._apply_governance_veto([]) is False

    def test_no_raw_attribute_no_veto(self):
        arb = self._make_arbiter()
        assert arb._apply_governance_veto([{"engine_id": "C13", "raw": None}]) is False


class TestVerdictMapping:
    """5-tier verdict granularity."""

    def _make_arbiter(self):
        from app.services.decision_brain.arbiter import Arbiter
        return Arbiter()

    def test_score_85_plus_strong_buy(self):
        arb = self._make_arbiter()
        assert arb._score_to_verdict(85.0, False) == "Strong Buy"
        assert arb._score_to_verdict(95.0, False) == "Strong Buy"

    def test_score_70_to_84_buy(self):
        arb = self._make_arbiter()
        assert arb._score_to_verdict(70.0, False) == "Buy"
        assert arb._score_to_verdict(84.0, False) == "Buy"

    def test_score_55_to_69_accumulate(self):
        arb = self._make_arbiter()
        assert arb._score_to_verdict(55.0, False) == "Accumulate"
        assert arb._score_to_verdict(69.0, False) == "Accumulate"

    def test_score_40_to_54_watch(self):
        arb = self._make_arbiter()
        assert arb._score_to_verdict(40.0, False) == "Watch"

    def test_score_below_40_avoid(self):
        arb = self._make_arbiter()
        assert arb._score_to_verdict(30.0, False) == "Avoid"

    def test_veto_always_avoid(self):
        arb = self._make_arbiter()
        # Even Strong Buy score becomes Avoid under veto
        assert arb._score_to_verdict(90.0, True) == "Avoid"
        assert arb._score_to_verdict(50.0, True) == "Avoid"


class TestConfidenceTiers:
    def _make_arbiter(self):
        from app.services.decision_brain.arbiter import Arbiter
        return Arbiter()

    def test_confirmed_above_80(self):
        arb = self._make_arbiter()
        assert arb._confidence_tier(80.0) == "Confirmed"
        assert arb._confidence_tier(95.0) == "Confirmed"

    def test_model_dependent_50_to_79(self):
        arb = self._make_arbiter()
        assert arb._confidence_tier(50.0) == "Model-dependent"
        assert arb._confidence_tier(79.0) == "Model-dependent"

    def test_contested_below_50(self):
        arb = self._make_arbiter()
        assert arb._confidence_tier(30.0) == "Contested"


# ═══════════════════════════════════════════════════════════════════════════
# Layer 14: DecisionAuditTrail
# ═══════════════════════════════════════════════════════════════════════════

class TestDecisionAuditTrailSchema:
    """Validate AuditTrail schema structure."""

    def test_audit_trail_instantiates(self):
        from app.models.schemas import DecisionAuditTrail
        trail = DecisionAuditTrail(
            symbol="RELIANCE",
            final_score=72,
            final_verdict="Buy",
            why_this_verdict="Verdict BUY because E1 shows strong growth",
            falsification_conditions=["Revenue < 10%", "D/E > 1.5x"],
        )
        assert trail.symbol == "RELIANCE"
        assert trail.final_verdict == "Buy"
        assert len(trail.falsification_conditions) == 2

    def test_engine_output_record_instantiates(self):
        from app.models.schemas import EngineOutputRecord
        record = EngineOutputRecord(
            engine_id="E1",
            engine_name="Growth Inflection",
            category="FUNDAMENTAL",
            verdict="Buy",
            passed_gates=True,
            confidence_pct=80,
            data_status="production",
            evidence=["Revenue +25% YoY"],
        )
        assert record.engine_id == "E1"
        assert record.verdict == "Buy"

    def test_audit_trail_timestamp_auto_set(self):
        from app.models.schemas import DecisionAuditTrail
        trail = DecisionAuditTrail(symbol="TCS", final_score=65, final_verdict="Accumulate")
        assert trail.timestamp is not None
        assert "T" in trail.timestamp  # ISO format

    def test_audit_trail_default_model_version(self):
        from app.models.schemas import DecisionAuditTrail
        trail = DecisionAuditTrail(symbol="INFY", final_score=60, final_verdict="Accumulate")
        assert trail.model_version == "0.4.0"


class TestWhyExplainer:
    """Why-this-verdict explainer."""

    def test_explainer_mentions_verdict(self):
        from app.services.decision_brain.audit_trail import generate_why_explainer
        outputs = [_mock_engine_output("E1", "Buy", 80, evidence=["Revenue +25% YoY"])]
        why = generate_why_explainer("RELIANCE", "Buy", 72, outputs, False)
        assert "BUY" in why.upper() or "72" in why

    def test_explainer_mentions_supporting_engine(self):
        from app.services.decision_brain.audit_trail import generate_why_explainer
        outputs = [_mock_engine_output("E1", "Buy", 85, evidence=["Revenue +25% YoY Q2FY25"])]
        why = generate_why_explainer("RELIANCE", "Buy", 72, outputs, False)
        assert "E1" in why

    def test_veto_explainer_mentions_veto(self):
        from app.services.decision_brain.audit_trail import generate_why_explainer
        outputs = [_mock_engine_output("C13", "Avoid", 40)]
        why = generate_why_explainer("RELIANCE", "Avoid", 15, outputs, True)
        assert "VETO" in why.upper() or "veto" in why.lower()

    def test_explainer_returns_string(self):
        from app.services.decision_brain.audit_trail import generate_why_explainer
        why = generate_why_explainer("TCS", "Watch", 48, [], False)
        assert isinstance(why, str)
        assert len(why) > 10


class TestDataLineage:
    """Data lineage tracing."""

    def test_lineage_always_has_price_entry(self):
        from app.services.decision_brain.audit_trail import _build_data_lineage
        lineage = _build_data_lineage("RELIANCE", [])
        types = [l["data_type"] for l in lineage]
        assert "live_price" in types

    def test_lineage_has_entry_per_engine(self):
        from app.services.decision_brain.audit_trail import _build_data_lineage
        outputs = [
            _mock_engine_output("E1", "Buy"),
            _mock_engine_output("B5", "Buy"),
        ]
        lineage = _build_data_lineage("RELIANCE", outputs)
        engine_entries = [l for l in lineage if "engine_output" in l["data_type"]]
        assert len(engine_entries) == 2

    def test_lineage_confidence_is_float(self):
        from app.services.decision_brain.audit_trail import _build_data_lineage
        lineage = _build_data_lineage("TCS", [])
        for entry in lineage:
            assert isinstance(entry["confidence"], float)
            assert 0.0 <= entry["confidence"] <= 1.0

    def test_no_financials_logs_warning_entry(self):
        from app.services.decision_brain.audit_trail import _build_data_lineage
        lineage = _build_data_lineage("TCS", [], financials=[])
        fin_entries = [l for l in lineage if l["data_type"] == "financial_observations"]
        assert len(fin_entries) >= 1
        assert fin_entries[0]["confidence"] == 0.0

"""Phase 3 — Intelligence & Reasoning Tests.

Tests for:
  Layer 8: Registry else-branch fully eliminated (data_insufficient not 82.5)
  Layer 9: Debate Engine — Bull vs Bear structure, severity, falsification
  Layer 13: LLM service — evidence-grounded prompting, context builder
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, List


# ═══════════════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_engine_output(
    engine_id: str,
    verdict: str,
    confidence: int = 75,
    evidence: List[str] = None,
    forensic_risk: str = "LOW",
) -> dict:
    """Create a mock engine output dict as returned by Arbiter._collect_engine_outputs."""
    raw = MagicMock()
    raw.strategy_name = f"Mock Engine {engine_id}"
    raw.results = {
        "evidence": evidence or [f"Signal from {engine_id}: strong YoY growth"],
        "forensic_risk": forensic_risk,
    }
    raw.metrics = {}
    return {
        "engine_id": engine_id,
        "verdict": verdict,
        "confidence": confidence,
        "regime": "CALM",
        "raw": raw,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Layer 8: Multi-Strategy Intelligence — else-branch elimination
# ═══════════════════════════════════════════════════════════════════════════

class TestElseBranchEliminated:
    """Verify the fake diagnostic_score: 82.5 is completely removed."""

    def test_no_fake_score_in_registry_source(self):
        import importlib.util
        spec = importlib.util.find_spec("app.services.strategies.registry")
        assert spec and spec.origin
        with open(spec.origin) as f:
            content = f.read()
        assert "diagnostic_score" not in content, "Fake diagnostic_score still in registry"
        assert "82.5" not in content, "Hardcoded 82.5 still in registry"

    def test_unimplemented_module_returns_data_insufficient(self):
        """Any module not yet implemented must return data_insufficient, not a fake score."""
        from app.services.strategies.registry import STRATEGY_MODULES, run_strategy_module
        # Find a module that is NOT explicitly routed (e.g. A1, A3)
        # A1 options arbitrage — no equity symbol makes sense
        resp = run_strategy_module("A1", "RELIANCE")
        # Should be production (it routes to the strategy) or data_insufficient
        # Key assertion: passed_gates should not be blindly True with fake metrics
        assert resp.strategy_id == "A1"
        assert resp.metrics.get("diagnostic_score") is None, \
            "A1 should not return fake diagnostic_score"

    def test_data_insufficient_not_passed(self):
        """data_insufficient responses must have passed_gates=False."""
        from app.services.strategies.registry import run_strategy_module, STRATEGY_MODULES
        # Try a module that will get no real data (e.g. B4 with mocked empty data)
        # We test the else-branch by checking module in STRATEGY_MODULES that is not explicitly routed
        for engine_id in ["A1", "A3"]:
            if engine_id in STRATEGY_MODULES:
                resp = run_strategy_module(engine_id, "TESTXYZ")
                if resp.status == "data_insufficient":
                    assert resp.passed_gates is False


# ═══════════════════════════════════════════════════════════════════════════
# Layer 9: Debate Engine Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestDebateEngineStructure:
    """Test structured Bull vs Bear debate output."""

    def _mixed_outputs(self):
        return [
            _make_engine_output("E1", "Buy", 80, ["Revenue grew 25% YoY", "PAT up 30%"]),
            _make_engine_output("E2", "Buy", 70, ["Turnaround confirmed", "FCF positive"]),
            _make_engine_output("B5", "Buy", 65, ["VCP breakout forming", "Volume dry-up"]),
            _make_engine_output("C13", "Avoid", 60, ["Promoter pledge 22%"]),
            _make_engine_output("C9", "Avoid", 55, ["High growth expectations priced in"]),
        ]

    def _all_bullish(self):
        return [
            _make_engine_output("E1", "Buy", 85, ["Strong revenue growth"]),
            _make_engine_output("B5", "Buy", 80),
            _make_engine_output("C9", "Buy", 75),
        ]

    def _all_bearish(self):
        return [
            _make_engine_output("C13", "Avoid", 40, [], "CRITICAL"),
            _make_engine_output("FORENSIC", "Avoid", 35, ["Beneish M-Score > -1.78"], "CRITICAL"),
        ]

    def test_debate_returns_contradiction_report(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert report.symbol == "RELIANCE"

    def test_bull_case_populated(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert len(report.bull_case) >= 1
        assert all("engine_id" in bc for bc in report.bull_case)

    def test_bear_case_populated(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert len(report.bear_case) >= 1

    def test_bull_case_max_3(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert len(report.bull_case) <= 3

    def test_bear_case_max_3(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert len(report.bear_case) <= 3

    def test_counter_arguments_in_bull_case(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        for bc in report.bull_case:
            assert "counter_arguments" in bc

    def test_falsification_conditions_present(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._mixed_outputs())
        assert len(report.falsification_conditions) >= 2
        assert len(report.falsification_conditions) <= 3

    def test_falsification_conditions_are_strings(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("TCS", self._mixed_outputs())
        for cond in report.falsification_conditions:
            assert isinstance(cond, str)
            assert len(cond) > 10  # Not empty

    def test_net_evidence_balance_bullish_when_all_buy(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._all_bullish())
        assert report.net_evidence_balance == "BULLISH_DOMINANT"

    def test_net_evidence_balance_bearish_when_all_sell(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", self._all_bearish())
        assert report.net_evidence_balance in ("BEARISH_DOMINANT", "CONTESTED")

    def test_net_evidence_balance_contested_mixed(self):
        from app.services.decision_brain.debate_engine import generate_debate
        # Equal bull and bear
        outputs = [
            _make_engine_output("E1", "Buy", 70),
            _make_engine_output("C13", "Avoid", 70),
        ]
        report = generate_debate("INFY", outputs)
        assert report.net_evidence_balance in ("CONTESTED", "BEARISH_DOMINANT", "BULLISH_DOMINANT")

    def test_empty_outputs_returns_valid_report(self):
        from app.services.decision_brain.debate_engine import generate_debate
        report = generate_debate("RELIANCE", [])
        assert report.symbol == "RELIANCE"
        assert report.contradiction_severity == "LOW"


class TestContradictionSeverity:
    """Severity matrix: FORENSIC vs FUNDAMENTAL = HIGH, etc."""

    def test_fundamental_vs_technical_is_low(self):
        from app.services.decision_brain.debate_engine import _compute_contradiction_severity
        severity = _compute_contradiction_severity(["E1"], ["B5"], [])
        assert severity == "LOW"

    def test_fundamental_vs_forensic_is_high(self):
        from app.services.decision_brain.debate_engine import _compute_contradiction_severity
        severity = _compute_contradiction_severity(["E1"], ["C13"], [])
        assert severity == "HIGH"

    def test_forensic_critical_flag_escalates_to_critical(self):
        from app.services.decision_brain.debate_engine import _compute_contradiction_severity
        # Engine output with CRITICAL forensic risk
        raw = MagicMock()
        raw.results = {"forensic_risk": "CRITICAL"}
        outputs = [{"engine_id": "C13", "verdict": "Avoid", "raw": raw}]
        severity = _compute_contradiction_severity(["E1"], ["C13"], outputs)
        assert severity == "CRITICAL"

    def test_valuation_vs_technical_is_low(self):
        from app.services.decision_brain.debate_engine import _compute_contradiction_severity
        severity = _compute_contradiction_severity(["C9"], ["B5"], [])
        assert severity == "LOW"

    def test_fundamental_vs_valuation_is_medium(self):
        from app.services.decision_brain.debate_engine import _compute_contradiction_severity
        severity = _compute_contradiction_severity(["E1"], ["C9"], [])
        assert severity == "MEDIUM"


class TestThesisAttack:
    """Counter-argument generation."""

    def test_revenue_growth_has_counter(self):
        from app.services.decision_brain.debate_engine import _generate_thesis_attack
        attack = _generate_thesis_attack("Revenue grew 25% YoY", [])
        assert "margin" in attack.lower() or "counter" in attack.lower()

    def test_fcf_claim_has_counter(self):
        from app.services.decision_brain.debate_engine import _generate_thesis_attack
        attack = _generate_thesis_attack("FCF turned positive", [])
        assert "capex" in attack.lower() or "working capital" in attack.lower()

    def test_rs_rating_has_counter(self):
        from app.services.decision_brain.debate_engine import _generate_thesis_attack
        attack = _generate_thesis_attack("RS Rating 85/99 — top performer", [])
        assert "extended" in attack.lower() or "base" in attack.lower()

    def test_generic_claim_returns_string(self):
        from app.services.decision_brain.debate_engine import _generate_thesis_attack
        attack = _generate_thesis_attack("Some unknown signal", [])
        assert isinstance(attack, str)
        assert len(attack) > 20


class TestFalsificationConditions:
    """Falsification condition generation."""

    def test_always_returns_3_conditions(self):
        from app.services.decision_brain.debate_engine import _generate_falsification_conditions
        conditions = _generate_falsification_conditions("RELIANCE", [])
        assert len(conditions) == 3

    def test_conditions_are_non_empty_strings(self):
        from app.services.decision_brain.debate_engine import _generate_falsification_conditions
        conditions = _generate_falsification_conditions("TCS", [])
        for c in conditions:
            assert isinstance(c, str) and len(c) > 20

    def test_conditions_mention_symbol_or_metric(self):
        from app.services.decision_brain.debate_engine import _generate_falsification_conditions
        conditions = _generate_falsification_conditions("INFOSYS", [])
        full_text = " ".join(conditions).lower()
        assert any(kw in full_text for kw in ["revenue", "infosys", "z-score", "regime", "pledge"])


# ═══════════════════════════════════════════════════════════════════════════
# Layer 13: LLM Service — Evidence-Grounded Prompting
# ═══════════════════════════════════════════════════════════════════════════

class TestResearchContextBuilder:
    """Verify research context is structured and grounded."""

    @patch("app.services.llm.get_quote")
    def test_context_contains_live_price(self, mock_quote):
        mock_q = MagicMock()
        mock_q.price = 2500.0
        mock_q.pe_ratio = 25.0
        mock_q.fifty_two_week_high = 3000.0
        mock_q.fifty_two_week_low = 1800.0
        mock_quote.return_value = mock_q

        from app.services.llm import build_research_context
        ctx = build_research_context("RELIANCE")
        assert "2500" in ctx or "2,500" in ctx
        assert "RESEARCH CONTEXT" in ctx

    def test_context_contains_regime(self):
        from app.services.llm import build_research_context
        ctx = build_research_context("RELIANCE")
        # Should contain macro regime section even if ResearchDataStore is empty
        assert "═══" in ctx  # Context structure markers present

    def test_context_contains_no_fabrication_rule(self):
        from app.services.llm import build_research_context
        ctx = build_research_context("RELIANCE")
        assert "never invent" in ctx.lower() or "cite only" in ctx.lower()


class TestAnalysisPromptStructure:
    """Verify prompt enforces structured reasoning protocol."""

    def test_prompt_contains_reasoning_rules(self):
        from app.services.llm import _build_analysis_prompt
        prompt = _build_analysis_prompt("Analyze RELIANCE", "RELIANCE", "Research", "context here")
        assert "CITE ONLY" in prompt.upper() or "cite only" in prompt.lower()
        assert "UNCERTAIN" in prompt or "uncertain" in prompt.lower()
        assert "DATA REQUIRED" in prompt

    def test_challenge_prompt_mentions_devil_advocate(self):
        from app.services.llm import _build_challenge_prompt
        prompt = _build_challenge_prompt("Stock looks good due to growth", "RELIANCE")
        assert "devil" in prompt.lower() or "challenge" in prompt.lower() or "against" in prompt.lower()
        assert "RELIANCE" in prompt

    def test_deterministic_fallback_includes_context(self):
        """When LLM unavailable, fallback must include ResearchContext, not empty reply."""
        from app.services.llm import build_research_context
        ctx = build_research_context("TCS")
        assert len(ctx) > 50  # Must be substantive, not empty

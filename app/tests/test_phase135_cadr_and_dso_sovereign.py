"""Phase 135 Test Suite: CADR Dilution Velocity Gate & DSO Sovereign Client-Type Contextualisation.

Verified without hallucination against:
1. compute_cadr() in forensic_auditor.py — warrant vs rights/QIP threshold branching
2. _classify_three_tier_alerts() DSO block in arbiter.py — sovereign vs commercial client-type routing

Evidence base:
- Apollo Micro: 20.7 Cr → 37.16 Cr shares (+80% total, CADR ≈ 21.5%/yr via warrants) — extraction
- HBL Power:  DSO > 150d due to Railway/Defence clients — sovereign, NOT collection failure
- Uni Abex Alloy: DSO elevated due to RDSO/Railway castings — sovereign structure
"""

import pytest
from app.services.research.forensic_auditor import compute_cadr, ForensicAuditor


# ─────────────────────────────────────────────────────────────────────────────
# 1. compute_cadr(): Core CADR formula tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCADRFormula:
    """Verify mathematical correctness of CADR computation."""

    def test_cadr_zero_dilution_clean(self):
        """No dilution in 3 years → CLEAN."""
        result = compute_cadr(shares_latest=100.0, shares_3y_ago=100.0, archetype="EARLY_MICROCAP")
        assert result.severity == "CLEAN"
        assert result.cadr == pytest.approx(0.0, abs=1e-4)
        assert result.flag_message is None

    def test_cadr_buyback_clean(self):
        """Net buyback (shares decreased) → CLEAN."""
        result = compute_cadr(shares_latest=80.0, shares_3y_ago=100.0, archetype="EARLY_MICROCAP")
        assert result.severity == "CLEAN"
        assert result.cadr < 0.0

    def test_cadr_data_absent(self):
        """Missing share data → DATA_ABSENT, no crash."""
        result = compute_cadr(shares_latest=None, shares_3y_ago=None, archetype="EARLY_MICROCAP")
        assert result.severity == "DATA_ABSENT"
        assert result.cadr is None

    def test_cadr_apollo_micro_warrant_block(self):
        """Apollo Micro: 20.7 Cr → 37.16 Cr shares via warrants = ~21.5% CADR → TIER2_OBJECTIVE_BLOCK."""
        result = compute_cadr(
            shares_latest=37_160_000,
            shares_3y_ago=20_700_000,
            dilution_instrument_hint="preferential warrants to promoters and investors",
            archetype="EARLY_MICROCAP",
            years=3.0,
        )
        assert result.severity == "TIER2_OBJECTIVE_BLOCK"
        assert result.cadr > 0.05   # > 5% threshold
        assert result.dilution_type == "WARRANT_EXTRACTION"
        assert result.flag_message is not None
        assert "TIER 2 OBJECTIVE BLOCK" in result.flag_message.upper() or "CADR DILUTION VELOCITY BLOCK" in result.flag_message.upper()

    def test_cadr_moderate_warrant_below_threshold_clean(self):
        """4% CADR via warrants (below 5% threshold) → CLEAN."""
        # shares_t1 = shares_t0 * (1.04)^3 ≈ 1.125x
        result = compute_cadr(
            shares_latest=112_500,
            shares_3y_ago=100_000,
            dilution_instrument_hint="preferential warrants",
            archetype="EARLY_MICROCAP",
        )
        assert result.severity == "CLEAN"
        assert result.cadr == pytest.approx(0.04, abs=0.006)

    def test_cadr_qip_expansion_below_12pct_clean(self):
        """10% CADR via QIP (below 12% expansion threshold) → CLEAN."""
        result = compute_cadr(
            shares_latest=133_100,
            shares_3y_ago=100_000,
            dilution_instrument_hint="qualified institutional placement for capex",
            archetype="MULTIBAGGER",
        )
        assert result.severity == "CLEAN"
        assert result.dilution_type == "EXPANSION_CAPITAL"

    def test_cadr_qip_above_12pct_tier3_caution(self):
        """15% CADR via QIP (above 12% expansion threshold) → TIER3_CONTEXTUAL_CAUTION, no Tier 2."""
        # shares_t1 = shares_t0 * (1.15)^3 ≈ 1.521x
        result = compute_cadr(
            shares_latest=152_100,
            shares_3y_ago=100_000,
            dilution_instrument_hint="rights issue for greenfield capacity",
            archetype="MULTIBAGGER",
        )
        assert result.severity == "TIER3_CONTEXTUAL_CAUTION"
        assert result.dilution_type == "EXPANSION_CAPITAL"
        assert result.flag_message is not None
        assert "[CAUTION]" in result.flag_message or "CADR DILUTION CAUTION" in result.flag_message

    def test_cadr_no_hint_early_microcap_uses_strict_threshold(self):
        """Unknown hint with EARLY_MICROCAP archetype uses strict 5% warrant threshold."""
        # 7% CADR, no instrument hint → should trigger TIER2_OBJECTIVE_BLOCK for EARLY_MICROCAP
        result = compute_cadr(
            shares_latest=122_500,  # ~(1.07)^3 ≈ 1.225x
            shares_3y_ago=100_000,
            dilution_instrument_hint=None,
            archetype="EARLY_MICROCAP",
        )
        assert result.severity == "TIER2_OBJECTIVE_BLOCK"
        assert result.dilution_type == "UNKNOWN"

    def test_cadr_no_hint_general_archetype_uses_lenient_threshold(self):
        """Unknown hint with GENERAL archetype uses lenient 12% expansion threshold."""
        # 7% CADR, no instrument hint → CLEAN for GENERAL archetype
        result = compute_cadr(
            shares_latest=122_500,
            shares_3y_ago=100_000,
            dilution_instrument_hint=None,
            archetype="GENERAL",
        )
        assert result.severity == "CLEAN"


# ─────────────────────────────────────────────────────────────────────────────
# 2. ForensicAuditor.audit_equity(): Integration of CADR into full audit
# ─────────────────────────────────────────────────────────────────────────────

class TestForensicAuditorCADRIntegration:
    """Verify CADR is correctly integrated into ForensicAuditResult."""

    def test_cadr_result_field_present(self):
        """cadr_result field exists in ForensicAuditResult."""
        auditor = ForensicAuditor()
        res = auditor.audit_equity("UNKNOWN_TEST_STOCK")
        assert hasattr(res, "cadr_result")
        assert res.cadr_result is not None

    def test_clean_stock_no_cadr_penalty(self):
        """Stock with no dilution: cadr_result CLEAN, forensic_score not penalised by CADR."""
        auditor = ForensicAuditor()
        res = auditor.audit_equity(
            "CLEAN_TEST",
            related_party_pct=2.0,
            auditor_resigned_recently=False,
            net_income_3y_cagr=18.0,
            ocf_3y_cagr=15.0,
            shares_latest=100_000,
            shares_3y_ago=100_000,
            dilution_instrument_hint=None,
            archetype="MULTIBAGGER",
        )
        assert res.cadr_result.severity == "CLEAN"
        assert res.forensic_score == pytest.approx(100.0, abs=0.1)

    def test_warrant_heavy_dilution_reduces_score(self):
        """Warrant CADR > 5% for EARLY_MICROCAP reduces forensic_score by 20pts."""
        auditor = ForensicAuditor()
        res = auditor.audit_equity(
            "DILUTED_TEST",
            related_party_pct=2.0,
            auditor_resigned_recently=False,
            net_income_3y_cagr=18.0,
            ocf_3y_cagr=15.0,
            shares_latest=200_000,   # 2x shares = ~26% CADR
            shares_3y_ago=100_000,
            dilution_instrument_hint="preferential warrants to promoters",
            archetype="EARLY_MICROCAP",
        )
        assert res.cadr_result.severity == "TIER2_OBJECTIVE_BLOCK"
        assert res.forensic_score == pytest.approx(80.0, abs=0.1)  # 100 - 20
        assert any("CADR" in flag for flag in res.red_flags)

    def test_data_modes_and_fields_backward_compat(self):
        """Existing test: ForensicAuditor includes m_score, z_score, data_mode — backward compat."""
        auditor = ForensicAuditor()
        res = auditor.audit_equity("UNKNOWN_TEST_STOCK")
        assert hasattr(res, "m_score")
        assert hasattr(res, "z_score")
        assert res.data_mode in ["INSUFFICIENT_DATA", "PARTIAL_DATA", "OBSERVED"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. DSO Sovereign Context in Arbiter (integration via _classify_three_tier_alerts)
# ─────────────────────────────────────────────────────────────────────────────

class TestArbiterDSOSovereignContext:
    """Verify Arbiter DSO check correctly branches on sovereign vs commercial client type."""

    def _make_snap(self, dso: float, sector: str = "", industry: str = ""):
        """Build a minimal snap-like object with dso, sector, industry fields."""
        class _Snap:
            pass
        s = _Snap()
        s.debtor_days = dso
        s.dso = 0.0
        s.debt_to_equity = 0.3
        s.interest_coverage = 5.0
        s.related_party_pct = 2.0
        s.sector = sector
        s.industry = industry
        return s

    def test_sovereign_defence_dso_is_tier3_caution_only(self):
        """Defence/Aerospace sector with DSO > 150d → Tier 3 Caution, NO Tier 2 haircut."""
        from app.services.decision_brain.arbiter import Arbiter
        arb = Arbiter()
        snap = self._make_snap(dso=210.0, sector="Capital Goods", industry="Aerospace & Defence")
        result = arb._classify_three_tier_alerts([], snap=snap, objective="MULTIBAGGER")
        warnings = result["tier_2_critical_warnings"]
        cautions = result["tier_3_contextual_cautions"]
        # Must NOT appear in Tier 2 critical warnings
        assert not any("dso" in str(w.get("metric", "")).lower() for w in warnings), \
            "Sovereign defence DSO should NOT trigger Tier 2 haircut"
        # MUST appear in Tier 3 contextual cautions
        assert any("dso" in c.lower() or "sovereign" in c.lower() or "150d" in c.lower()
                   for c in cautions), \
            "Sovereign defence DSO must appear in Tier 3 contextual cautions"

    def test_railway_sector_dso_is_tier3_caution_only(self):
        """Railway infrastructure sector with DSO > 150d → Tier 3, no Tier 2."""
        from app.services.decision_brain.arbiter import Arbiter
        arb = Arbiter()
        snap = self._make_snap(dso=185.0, sector="Capital Goods", industry="Railway Infrastructure")
        result = arb._classify_three_tier_alerts([], snap=snap, objective="MULTIBAGGER")
        warnings = result["tier_2_critical_warnings"]
        assert not any("dso" in str(w.get("metric", "")).lower() for w in warnings), \
            "Railway DSO should NOT trigger Tier 2 haircut"

    def test_private_commercial_dso_is_tier2_haircut(self):
        """Private FMCG/IT sector with DSO > 150d → Tier 2 Critical Warning with haircut."""
        from app.services.decision_brain.arbiter import Arbiter
        arb = Arbiter()
        snap = self._make_snap(dso=180.0, sector="FMCG", industry="Consumer Goods")
        result = arb._classify_three_tier_alerts([], snap=snap, objective="GENERAL")
        warnings = result["tier_2_critical_warnings"]
        assert any("dso" in str(w.get("metric", "")).lower() for w in warnings), \
            "Private commercial DSO must trigger Tier 2 Critical Warning"
        # Confirm sizing haircut present
        dso_warning = next(w for w in warnings if "dso" in str(w.get("metric", "")).lower())
        assert dso_warning["sizing_haircut_pct"] == pytest.approx(15.0)

    def test_normal_dso_below_150_no_flag(self):
        """DSO <= 150d → neither Tier 2 nor sovereign caution."""
        from app.services.decision_brain.arbiter import Arbiter
        arb = Arbiter()
        snap = self._make_snap(dso=90.0, sector="Capital Goods", industry="Aerospace & Defence")
        result = arb._classify_three_tier_alerts([], snap=snap, objective="GENERAL")
        warnings = result["tier_2_critical_warnings"]
        cautions = result["tier_3_contextual_cautions"]
        assert not any("dso" in str(w.get("metric", "")).lower() for w in warnings)
        assert not any("sovereign" in c.lower() for c in cautions)

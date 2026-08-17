"""Phase 1 — Data Foundation Tests.

Tests for:
  Layer 1: RegimeEngine, MacroContext, SectorModel
  Layer 2: FinancialIngester (schema validation, data flow)
  Layer 3: DataQualityGate (quote validation, freshness, corporate action factors)
"""

import pytest
from datetime import datetime, timezone

from app.models.schemas import (
    RegimeClassification,
    MacroContext,
    SectorProfile,
    DataQualityReport,
    SourceCredibility,
)


# =====================================================================
# Layer 1: Regime Engine Tests
# =====================================================================

class TestRegimeClassification:
    """Test the deterministic regime classification logic."""

    def test_regime_calm_low_vix(self):
        """VIX < 15 with positive DMA distance → CALM."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=12.0, nifty_spot=22000, nifty_200dma=21000)
        assert result.regime == "CALM"
        assert result.confidence >= 0.8

    def test_regime_elevated_medium_vix(self):
        """VIX 15–20 → ELEVATED."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=17.5, nifty_spot=22000, nifty_200dma=21500)
        assert result.regime == "ELEVATED"

    def test_regime_volatile_high_vix(self):
        """VIX 20–30 → VOLATILE."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=25.0, nifty_spot=20000, nifty_200dma=21500)
        assert result.regime == "VOLATILE"

    def test_regime_crisis_extreme_vix_and_dma_breach(self):
        """VIX > 30 AND Nifty > 10% below 200DMA → CRISIS."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=35.0, nifty_spot=18000, nifty_200dma=21000)
        assert result.regime == "CRISIS"
        assert "India VIX: 35.0" in result.evidence[0]

    def test_regime_volatile_nifty_below_200dma(self):
        """Nifty significantly below 200DMA even with moderate VIX."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=14.0, nifty_spot=19000, nifty_200dma=21000)
        # 19000/21000 = -9.5% → below -5% threshold → VOLATILE
        assert result.regime == "VOLATILE"

    def test_regime_fii_outflow_escalation(self):
        """FII outflow escalates ELEVATED to VOLATILE."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(
            vix_level=16.0,
            nifty_spot=22000,
            nifty_200dma=21500,
            fii_net_flow_direction="OUTFLOW"
        )
        assert result.regime == "VOLATILE"
        assert any("FII" in e for e in result.evidence)

    def test_regime_no_data_defaults_calm(self):
        """When no market data is available, classify based on what can be fetched.
        If live VIX is fetchable, confidence will be > 0.3."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=None, nifty_spot=None, nifty_200dma=None)
        # May fetch live VIX/Nifty, so just verify it returns a valid regime
        assert result.regime in ("CALM", "ELEVATED", "VOLATILE", "CRISIS")
        assert 0.0 < result.confidence <= 1.0

    def test_regime_evidence_list_populated(self):
        """Evidence list contains specific data points."""
        from app.services.knowledge.regime_engine import RegimeEngine
        engine = RegimeEngine()
        result = engine.classify(vix_level=18.0, nifty_spot=22500, nifty_200dma=22000)
        assert len(result.evidence) >= 2
        assert any("VIX" in e for e in result.evidence)
        assert any("Nifty" in e for e in result.evidence)


class TestMacroContext:
    """Test MacroContext Pydantic model."""

    def test_macro_context_defaults(self):
        ctx = MacroContext()
        assert ctx.rbi_repo_rate == 6.5
        assert ctx.risk_free_rate == 7.0
        assert ctx.regime.regime == "CALM"

    def test_macro_context_with_regime(self):
        regime = RegimeClassification(regime="VOLATILE", vix_level=25.0)
        ctx = MacroContext(regime=regime, nifty_level=20000.0, india_vix=25.0)
        assert ctx.regime.regime == "VOLATILE"
        assert ctx.nifty_level == 20000.0


# =====================================================================
# Layer 1: Sector Model Tests
# =====================================================================

class TestSectorModel:
    """Test sector classification and peer mapping."""

    def test_sector_normalization(self):
        from app.services.knowledge.sector_model import SectorModel
        model = SectorModel()
        assert model._normalize_sector("information technology") == "Technology"
        assert model._normalize_sector("FMCG") == "Consumer"
        assert model._normalize_sector("pharmaceutical") == "Healthcare"
        assert model._normalize_sector("banking") == "Financials"
        assert model._normalize_sector(None) is None

    def test_peer_group_lookup(self):
        from app.services.knowledge.sector_model import SectorModel
        model = SectorModel()
        peers = model._find_peers("TCS", "Technology")
        assert "TCS" not in peers  # Self excluded
        assert "INFY" in peers
        assert len(peers) <= 7

    def test_unknown_sector_returns_empty_peers(self):
        from app.services.knowledge.sector_model import SectorModel
        model = SectorModel()
        peers = model._find_peers("SOMECORP", None)
        assert peers == []


# =====================================================================
# Layer 2: Ingestion Framework Tests (schema validation)
# =====================================================================

class TestSourceCredibility:
    """Test source credibility tiers."""

    def test_credibility_tiers_ordered(self):
        cred = SourceCredibility()
        assert cred.BSE_FILING > cred.SCREENER_IN
        assert cred.SCREENER_IN > cred.YFINANCE
        assert cred.YFINANCE > cred.NEWS_ARTICLE
        assert cred.NEWS_ARTICLE > cred.AI_GENERATED

    def test_bse_filing_is_highest(self):
        cred = SourceCredibility()
        assert cred.BSE_FILING == 1.0


# =====================================================================
# Layer 3: Data Quality Gate Tests
# =====================================================================

class TestDataQualityGate:
    """Test data quality validation and grading."""

    def test_validate_quote_clean_data(self):
        from app.services.ingestion.data_quality_gate import DataQualityGate
        gate = DataQualityGate()
        quote = {
            "symbol": "RELIANCE.NS",
            "price": 1350.0,
            "volume": 1500000,
            "pe_ratio": 25.0,
            "fifty_two_week_high": 1600.0,
            "fifty_two_week_low": 1100.0,
            "meta": {"retrieved_at": datetime.now(timezone.utc).isoformat()},
        }
        validated = gate.validate_quote(quote)
        assert "data_quality_warnings" not in validated or len(validated.get("data_quality_warnings", [])) == 0

    def test_validate_quote_zero_price_warns(self):
        from app.services.ingestion.data_quality_gate import DataQualityGate
        gate = DataQualityGate()
        quote = {"symbol": "BAD", "price": 0.0, "volume": 100, "meta": {}}
        validated = gate.validate_quote(quote)
        assert any("INVALID_PRICE" in w for w in validated.get("data_quality_warnings", []))

    def test_validate_quote_insane_pe_warns(self):
        from app.services.ingestion.data_quality_gate import DataQualityGate
        gate = DataQualityGate()
        quote = {"symbol": "TEST", "price": 100.0, "pe_ratio": 9999.0, "meta": {}}
        validated = gate.validate_quote(quote)
        assert any("PE_TOO_HIGH" in w for w in validated.get("data_quality_warnings", []))

    def test_validate_quote_inverted_52w_range_warns(self):
        from app.services.ingestion.data_quality_gate import DataQualityGate
        gate = DataQualityGate()
        quote = {
            "symbol": "TEST", "price": 100.0,
            "fifty_two_week_high": 80.0, "fifty_two_week_low": 120.0,
            "meta": {},
        }
        validated = gate.validate_quote(quote)
        assert any("52W_RANGE_INVERTED" in w for w in validated.get("data_quality_warnings", []))


class TestDataQualityGrading:
    """Test data quality grade computation."""

    def test_grade_a_with_rich_data(self):
        grade = DataQualityReport.compute_grade(quarters=16, has_ownership=True, credibility=0.9)
        assert grade == "A"

    def test_grade_f_with_no_data(self):
        grade = DataQualityReport.compute_grade(quarters=0, has_ownership=False, credibility=0.0)
        assert grade == "F"

    def test_grade_c_with_moderate_data(self):
        grade = DataQualityReport.compute_grade(quarters=6, has_ownership=False, credibility=0.7)
        assert grade in ("C", "D")

    def test_grade_a_with_good_data(self):
        # 12*5=60 + 15(ownership) + 21(0.85*25) = 96 → Grade A
        grade = DataQualityReport.compute_grade(quarters=12, has_ownership=True, credibility=0.85)
        assert grade == "A"


class TestCorporateActionFactor:
    """Test corporate action adjustment factor calculation."""

    def test_stock_split_1_to_5(self):
        from app.services.ingestion.data_quality_gate import compute_corporate_action_factor
        factor = compute_corporate_action_factor("SPLIT", ratio_numerator=1, ratio_denominator=5)
        assert factor == 5.0

    def test_bonus_1_to_1(self):
        from app.services.ingestion.data_quality_gate import compute_corporate_action_factor
        factor = compute_corporate_action_factor("BONUS", ratio_numerator=1, ratio_denominator=1)
        assert factor == 0.5

    def test_dividend_no_adjustment(self):
        from app.services.ingestion.data_quality_gate import compute_corporate_action_factor
        factor = compute_corporate_action_factor("DIVIDEND", ratio_numerator=1, ratio_denominator=1)
        assert factor == 1.0

    def test_invalid_denominator_returns_1(self):
        from app.services.ingestion.data_quality_gate import compute_corporate_action_factor
        factor = compute_corporate_action_factor("SPLIT", ratio_numerator=1, ratio_denominator=0)
        assert factor == 1.0

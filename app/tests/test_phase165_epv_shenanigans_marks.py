"""Phase 165 Unit Tests — Institutional Valuation Frontiers & Forensic Shenanigans Engine.

Verifies:
1. Bruce Greenwald EPV Engine:
   - Asset Reproduction Cost (AV), Zero-Growth EPV, and Franchise Moat Multiple.
   - Classification of Durable Franchise Moat vs Capital Destroying Asset Trap.
2. Howard Schilit 7 Financial Shenanigans Forensic Detector:
   - CWIP expense capitalization, premature revenue/receivables divergence, and other income masking.
   - CFO vs PAT cash flow divergence detection.
3. Howard Marks Market & Credit Cycle Pendulum Scorer:
   - Cyclical sentiment positioning: Extreme Greed vs Distress.
   - Recommended risk posture and cash allocation guide.
4. McKinsey / Tim Koller Invested Capital & Economic Profit Calculator:
   - Economic Profit = Invested Capital * (ROIC - WACC).
   - Blume mean-reverting Beta adjustment.
5. Epistemic Self-Learning Integration:
   - Dynamic pattern recognition and certified facts in registry.
"""

import pytest
from app.services.research.epv_and_shenanigans import (
    GreenwaldEPVEngine,
    SchilitShenanigansDetector,
    MarksCreditCyclePendulum,
    McKinseyInvestedCapitalNormalizer,
)
from app.services.research.self_learning_engine import SelfLearningEngine


# ----------------------------------------------------------------------
# 1. Bruce Greenwald EPV Engine Tests
# ----------------------------------------------------------------------

def test_greenwald_epv_durable_franchise():
    """Verify high EPV relative to Asset Reproduction Cost signals a durable moat."""
    res = GreenwaldEPVEngine.calculate_epv(
        ebit_cr=266.67,
        wacc_pct=13.5,
        tax_rate_pct=25.0,
        net_debt_cr=100.0,
        asset_reproduction_cost_cr=750.0,
        current_mcap_cr=2500.0,
    )
    # NOPAT = 266.67 * 0.75 = 200.0
    # EPV_firm = 200.0 / 0.135 = 1481.48
    # EPV_equity = 1481.48 - 100 = 1381.48
    # Moat Multiple = 1381.48 / 750 = 1.84 (>= 1.40)
    assert res["moat_multiple"] >= 1.40
    assert res["moat_classification"] == "DURABLE_FRANCHISE_MOAT"
    assert res["franchise_value_cr"] > 0
    assert res["price_to_epv"] is not None


def test_greenwald_epv_capital_destroying_trap():
    """Verify low earnings power relative to massive balance sheet assets is flagged as a trap."""
    res = GreenwaldEPVEngine.calculate_epv(
        ebit_cr=60.0,
        wacc_pct=13.5,
        tax_rate_pct=25.0,
        net_debt_cr=150.0,
        asset_reproduction_cost_cr=800.0,
    )
    # NOPAT = 45.0
    # EPV_firm = 45 / 0.135 = 333.33
    # EPV_equity = 333.33 - 150 = 183.33
    # Moat Multiple = 183.33 / 800 = 0.23 (< 0.90)
    assert res["moat_multiple"] < 0.90
    assert res["moat_classification"] == "CAPITAL_DESTROYING_ASSET_TRAP"
    assert res["franchise_value_cr"] == 0.0


def test_greenwald_growth_premium_calculation():
    """Verify market growth premium indicates what percentage of market cap reflects future growth."""
    res = GreenwaldEPVEngine.calculate_epv(
        ebit_cr=180.0,
        wacc_pct=13.5,
        tax_rate_pct=25.0,
        net_debt_cr=0.0,
        current_mcap_cr=2000.0,
    )
    # NOPAT = 135 -> EPV_firm = 135 / 0.135 = 1000.0
    # EPV_equity = 1000.0
    # Growth premium = (2000 - 1000) / 2000 = 50.0%
    assert res["epv_equity_cr"] == 1000.0
    assert res["price_to_epv"] == 2.0
    assert res["market_growth_premium_pct"] == 50.0


# ----------------------------------------------------------------------
# 2. Howard Schilit Financial Shenanigans Forensic Tests
# ----------------------------------------------------------------------

def test_schilit_clean_accounting():
    """Verify conservative company receives high hygiene score with zero flags."""
    res = SchilitShenanigansDetector.detect_shenanigans(
        cwip_cr=10.0,
        gross_block_cr=200.0,
        ebit_cr=80.0,
        delta_cwip_cr=5.0,
        sales_growth_yoy_pct=18.0,
        receivables_growth_yoy_pct=16.0,
        dso_latest_days=45.0,
        dso_previous_days=44.0,
        other_income_cr=5.0,
        pbt_cr=75.0,
        cfo_cr=70.0,
        pat_cr=60.0,
    )
    assert res["forensic_hygiene_score"] >= 85.0
    assert res["hygiene_rating"] == "CLEAN_ACCOUNTING_CONSERVATIVE"
    assert res["detected_shenanigans_count"] == 0


def test_schilit_cwip_and_revenue_shenanigans():
    """Verify excessive CWIP capitalization and premature revenue recognition are flagged."""
    res = SchilitShenanigansDetector.detect_shenanigans(
        cwip_cr=150.0,
        gross_block_cr=250.0,  # 60% of gross block
        ebit_cr=50.0,
        delta_cwip_cr=40.0,    # 80% of EBIT
        sales_growth_yoy_pct=10.0,
        receivables_growth_yoy_pct=35.0, # 25% higher than sales
        dso_latest_days=95.0,
        dso_previous_days=65.0, # Jump of 30 days
        cfo_cr=-10.0,
        pat_cr=40.0,           # Positive PAT, negative CFO
    )
    assert res["cwip_anomaly_detected"] is True
    assert res["revenue_anomaly_detected"] is True
    assert res["cfo_divergence_detected"] is True
    assert res["forensic_hygiene_score"] < 65.0
    assert res["hygiene_rating"] == "AGGRESSIVE_ACCOUNTING_RED_FLAG"
    assert res["detected_shenanigans_count"] >= 3


# ----------------------------------------------------------------------
# 3. Howard Marks Credit & Market Cycle Pendulum Tests
# ----------------------------------------------------------------------

def test_marks_pendulum_extreme_greed():
    """Verify high valuation multiple and tight credit spreads trigger defensive posture."""
    res = MarksCreditCyclePendulum.assess_pendulum(
        nifty_trailing_pe=27.0,
        historical_median_pe=20.0,
        credit_spread_bps=80.0,
        speculative_ipo_frenzy=True,
    )
    assert res["pendulum_state"] == "EXTREME_GREED_TIGHT_SPREAD_RISK"
    assert res["recommended_risk_posture"] == "DEFENSIVE_RISK_CONTROL"
    assert "ELEVATED_CASH" in res["cash_allocation_guide"]


def test_marks_pendulum_distress_opportunity():
    """Verify depressed valuations and wide spreads trigger aggressive deployment signal."""
    res = MarksCreditCyclePendulum.assess_pendulum(
        nifty_trailing_pe=16.0,
        historical_median_pe=20.0,
        credit_spread_bps=280.0,
    )
    assert res["pendulum_state"] == "DISTRESS_LIQUIDITY_CONTRACTION"
    assert res["recommended_risk_posture"] == "AGGRESSIVE_CAPITAL_DEPLOYMENT"


# ----------------------------------------------------------------------
# 4. McKinsey / Tim Koller Invested Capital & Economic Profit Tests
# ----------------------------------------------------------------------

def test_mckinsey_economic_profit_creation():
    """Verify ROIC > WACC creates positive economic profit."""
    res = McKinseyInvestedCapitalNormalizer.calculate_economic_profit(
        invested_capital_cr=1000.0,
        nopat_cr=220.0,
        wacc_pct=13.5,
        raw_beta=1.4,
    )
    # ROIC = 22.0%
    # Spread = 22.0 - 13.5 = +8.5%
    # Economic Profit = 1000 * 0.085 = 85.0 Cr
    assert res["roic_pct"] == 22.0
    assert res["roic_wacc_spread_pct"] == 8.5
    assert res["economic_profit_cr"] == 85.0
    assert res["value_creation_status"] == "VALUE_CREATING"
    # Blume beta = 0.67 * 1.4 + 0.33 * 1.0 = 0.938 + 0.33 = 1.27
    assert 1.20 <= res["blume_adjusted_beta"] <= 1.30


def test_mckinsey_economic_profit_destruction():
    """Verify ROIC < WACC flags value destruction even if company is profitable."""
    res = McKinseyInvestedCapitalNormalizer.calculate_economic_profit(
        invested_capital_cr=1200.0,
        nopat_cr=96.0,
        wacc_pct=13.5,
    )
    # ROIC = 8.0% < 13.5% WACC
    # Spread = -5.5%
    # Economic Profit = 1200 * -0.055 = -66.0 Cr
    assert res["roic_pct"] == 8.0
    assert res["roic_wacc_spread_pct"] < 0
    assert res["economic_profit_cr"] < 0
    assert res["value_creation_status"] == "VALUE_DESTROYING"


# ----------------------------------------------------------------------
# 5. Epistemic Self-Learning Integration Tests
# ----------------------------------------------------------------------

def test_self_learning_phase165_patterns_and_facts():
    """Verify pattern matching and registry persistence for Phase 165 concepts."""
    engine = SelfLearningEngine()
    
    # 1. Greenwald EPV detection
    text_epv = "Bruce Greenwald Earnings Power Value EPV and Asset Reproduction Cost analysis."
    gaps_epv = engine.detect_knowledge_gaps(text_epv)
    assert any(g["entity_id"] == "GREENWALD_EARNINGS_POWER_VALUE" for g in gaps_epv)

    # 2. Schilit Shenanigans detection
    text_schilit = "Howard Schilit Financial Shenanigans regarding CWIP capitalization and premature revenue."
    gaps_schilit = engine.detect_knowledge_gaps(text_schilit)
    assert any(g["entity_id"] == "SCHILIT_FORENSIC_SHENANIGANS" for g in gaps_schilit)

    # 3. Marks Credit Cycle detection
    text_marks = "Howard Marks credit cycle pendulum indicates tight credit spread and market euphoria."
    gaps_marks = engine.detect_knowledge_gaps(text_marks)
    assert any(g["entity_id"] == "MARKS_CREDIT_CYCLE_PENDULUM" for g in gaps_marks)

    # 4. McKinsey Economic Profit detection
    text_mckinsey = "McKinsey Valuation Tim Koller economic profit with invested capital and Blume adjusted beta."
    gaps_mckinsey = engine.detect_knowledge_gaps(text_mckinsey)
    assert any(g["entity_id"] == "MCKINSEY_ECONOMIC_PROFIT" for g in gaps_mckinsey)

    # 5. Verify registered facts in registry
    reg = engine._read_registry()
    entities = reg.get("entities", {})
    for expected_id in [
        "GREENWALD_EARNINGS_POWER_VALUE",
        "SCHILIT_FORENSIC_SHENANIGANS",
        "MARKS_CREDIT_CYCLE_PENDULUM",
        "MCKINSEY_ECONOMIC_PROFIT",
    ]:
        assert expected_id in entities, f"Missing entity {expected_id} in registry"
        assert entities[expected_id]["verification_status"] == "CERTIFIED_FACT"

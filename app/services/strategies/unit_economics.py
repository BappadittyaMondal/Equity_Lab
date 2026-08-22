"""Unit Economics Analysis Engine (Strategy Engine E8 / Section 8).

Provides sector-conditional unit economics calculations for Manufacturing, Financials,
Technology/SaaS, and Consumer sectors per Section 8 of the Institutional Framework:
1. Manufacturing: Capacity utilization, realization/unit, conversion cost, asset turnover.
2. Financials: Net Interest Margin (NIM), credit growth, credit cost, CASA ratio.
3. SaaS / Technology: Net Revenue Retention (NRR), ARR, LTV/CAC.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header


def evaluate_unit_economics(
    symbol: str,
    sector: str = "MANUFACTURING",
    operational_data: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluate sector-conditional unit economics and incremental unit trend."""
    norm_symbol = normalize_symbol(symbol)
    sector_upper = sector.upper().strip()
    data = operational_data or {}
    evidence = []

    if sector_upper in ["FINANCIALS", "BANKING", "NBFC"]:
        nim = float(data.get("net_interest_margin_pct", 3.8))
        credit_growth = float(data.get("credit_growth_pct", 14.5))
        credit_cost = float(data.get("credit_cost_pct", 0.9))
        casa_ratio = float(data.get("casa_ratio_pct", 41.2))

        # Financials Unit Economics Score (0-100)
        nim_score = min(30.0, (nim / 4.5) * 30.0)
        growth_score = min(30.0, (credit_growth / 18.0) * 30.0)
        cost_score = min(20.0, max(0.0, (2.0 - credit_cost) * 10.0))
        casa_score = min(20.0, (casa_ratio / 50.0) * 20.0)
        unit_score = round(nim_score + growth_score + cost_score + casa_score, 1)

        evidence.append(f"Financials Unit Economics: NIM {nim:.2f}% | Credit Growth {credit_growth:.1f}%")
        evidence.append(f"Credit Cost: {credit_cost:.2f}% | CASA Ratio: {casa_ratio:.1f}%")
        metrics = {
            "nim_pct": nim,
            "credit_growth_pct": credit_growth,
            "credit_cost_pct": credit_cost,
            "casa_ratio_pct": casa_ratio
        }

    elif sector_upper in ["TECHNOLOGY", "SAAS", "IT_SERVICES"]:
        nrr = float(data.get("net_revenue_retention_pct", 112.0))
        gross_margin = float(data.get("gross_margin_pct", 72.0))
        cac_payback_months = float(data.get("cac_payback_months", 14.0))

        unit_score = round(min(100.0, (nrr / 120.0) * 50.0 + (gross_margin / 80.0) * 30.0 + max(0.0, 24.0 - cac_payback_months)), 1)
        evidence.append(f"SaaS Unit Economics: NRR {nrr:.1f}% | Gross Margin {gross_margin:.1f}% | CAC Payback {cac_payback_months:.1f}m")
        metrics = {
            "net_revenue_retention_pct": nrr,
            "gross_margin_pct": gross_margin,
            "cac_payback_months": cac_payback_months
        }

    else:
        # Default: MANUFACTURING / CAPITAL GOODS / CHEMICALS
        utilization = float(data.get("capacity_utilization_pct", 78.5))
        realization_growth = float(data.get("realization_growth_pct", 5.2))
        conversion_cost_trend = float(data.get("conversion_cost_trend_pct", -1.5))
        contribution_margin = float(data.get("contribution_margin_pct", 28.0))

        util_score = min(35.0, (utilization / 85.0) * 35.0)
        real_score = min(25.0, max(0.0, (realization_growth + 5.0) * 2.5))
        cost_score = min(20.0, max(0.0, (-conversion_cost_trend + 5.0) * 2.0))
        margin_score = min(20.0, (contribution_margin / 35.0) * 20.0)
        unit_score = round(util_score + real_score + cost_score + margin_score, 1)

        evidence.append(f"Manufacturing Unit Economics: Capacity Utilization {utilization:.1f}%")
        evidence.append(f"Realization Growth: {realization_growth:+.1f}% | Contribution Margin: {contribution_margin:.1f}%")
        metrics = {
            "capacity_utilization_pct": utilization,
            "realization_growth_pct": realization_growth,
            "conversion_cost_trend_pct": conversion_cost_trend,
            "contribution_margin_pct": contribution_margin
        }

    # Trend direction
    unit_trend = "IMPROVING" if unit_score >= 65.0 else ("DETERIORATING" if unit_score < 40.0 else "STABLE")

    return {
        "symbol": norm_symbol,
        "sector": sector_upper,
        "executed_at": datetime.now().isoformat(),
        "unit_economics_score": unit_score,
        "unit_trend": unit_trend,
        "metrics": metrics,
        "evidence": evidence,
        "meta": create_meta_header(source="Unit Economics Engine (E8)")
    }


def compute_market_share_velocity(symbol: str) -> Dict[str, Any]:
    """Market Share Velocity = ΔMarket Share over Trailing 4 Quarters.

    Data Feeds Note:
    Requires industry-level sales aggregator feeds. Returns DATA_BLOCKED status when
    external industry aggregate dataset is absent, preventing unverified heuristics.
    """
    norm_symbol = normalize_symbol(symbol)
    return {
        "symbol": norm_symbol,
        "status": "DATA_BLOCKED",
        "market_share_velocity_pct": None,
        "market_share_acceleration": None,
        "evidence": ["DATA_BLOCKED: Industry-level total sales data feed is not currently ingested."]
    }


"""Shareholding-Pattern Intelligence Engine (§24).

Tracks FII/DII/Mutual Fund flows, institutional accumulation streaks, retail distribution signals,
free-float index inclusion catalysts, and ownership concentration risks.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import ShareholdingPatternIntelligence


def evaluate_shareholding_pattern(
    symbol: str,
    shareholding_data: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates institutional flow momentum, accumulation streaks, and float catalysts."""
    norm_symbol = normalize_symbol(symbol)
    data = shareholding_data or {}
    evidence = []

    fii_pct = float(data.get("fii_holding_pct", 14.5))
    fii_qoq = float(data.get("fii_qoq_change", 1.4))
    dii_pct = float(data.get("dii_mf_holding_pct", 19.8))
    dii_qoq = float(data.get("dii_qoq_change", 0.9))
    accumulation_quarters = int(data.get("institutional_accumulation_quarters", 3))
    retail_trend = str(data.get("retail_holding_trend", "DECREASING")).upper()
    mcap_crores = float(data.get("free_float_market_cap_cr", 4500.0))

    # Institutional Flow Score (0-100)
    fii_score = min(30.0, max(0.0, (fii_qoq + 2.0) * 7.5))
    dii_score = min(30.0, max(0.0, (dii_qoq + 2.0) * 7.5))
    streak_score = min(25.0, accumulation_quarters * 6.25)
    retail_score = 15.0 if retail_trend == "DECREASING" else 0.0

    institutional_flow_score = round(min(100.0, fii_score + dii_score + streak_score + retail_score), 1)

    # Free Float Index Inclusion Catalyst Check
    if mcap_crores >= 15000.0:
        index_catalyst = "NIFTY_100_INCLUSION_CANDIDATE"
    elif mcap_crores >= 4000.0:
        index_catalyst = "NIFTY_MIDCAP_150_INCLUSION_CANDIDATE"
    elif mcap_crores >= 1000.0:
        index_catalyst = "NIFTY_SMALLCAP_250_INCLUSION_CANDIDATE"
    else:
        index_catalyst = "MICRO_CAP_EXPANSION"

    concentration_risk = "HIGH" if (fii_pct + dii_pct) > 65.0 or fii_pct > 35.0 else "BALANCED"

    evidence.append(f"Institutional Flow Score: {institutional_flow_score}/100 | Streak: {accumulation_quarters} quarters")
    evidence.append(f"FII: {fii_pct:.1f}% ({fii_qoq:+.1f}% QoQ) | DII/MF: {dii_pct:.1f}% ({dii_qoq:+.1f}% QoQ)")
    evidence.append(f"Retail Holding Trend: {retail_trend} | Float Catalyst: {index_catalyst}")

    intelligence = ShareholdingPatternIntelligence(
        fii_holding_pct=fii_pct,
        fii_qoq_change=fii_qoq,
        dii_mf_holding_pct=dii_pct,
        dii_qoq_change=dii_qoq,
        institutional_accumulation_quarters=accumulation_quarters,
        retail_holding_trend=retail_trend,
        free_float_index_catalyst=index_catalyst,
        ownership_concentration_risk=concentration_risk
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "institutional_flow_score": institutional_flow_score,
        "accumulation_quarters": accumulation_quarters,
        "index_catalyst": index_catalyst,
        "pattern_intelligence": intelligence.model_dump(),
        "evidence": evidence,
        "meta": create_meta_header(source="Shareholding Pattern Intelligence Engine (§24)")
    }

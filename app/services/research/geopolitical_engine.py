"""Geopolitical & Macro Risk Assessment Engine — Phase 8.

Monitors macro-economic policy shocks, crude oil volatility, trade tariff changes,
geopolitical alerts, and sector sensitivity metrics from ResearchDataStore.

Pipeline Law: No synthetic default risk scores. If no macro/geopolitical events
are found in the point-in-time observation store, emits explicit DATA_UNAVAILABLE.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research_data import ResearchDataStore

logger = logging.getLogger(__name__)


SECTOR_GEOPOLITICAL_SENSITIVITIES: Dict[str, Dict[str, str]] = {
    "IT": {"primary_risk": "USD_INR_VOLATILITY", "sensitivity": "HIGH"},
    "SOFTWARE": {"primary_risk": "USD_INR_VOLATILITY", "sensitivity": "HIGH"},
    "OIL_GAS": {"primary_risk": "CRUDE_OIL_SHOCK", "sensitivity": "CRITICAL"},
    "PAINTS": {"primary_risk": "CRUDE_OIL_SHOCK", "sensitivity": "HIGH"},
    "METALS": {"primary_risk": "TARIFF_DUTY_SHOCK", "sensitivity": "HIGH"},
    "BANKING": {"primary_risk": "RBI_RATE_POLICY", "sensitivity": "MODERATE"},
    "FINANCE": {"primary_risk": "RBI_RATE_POLICY", "sensitivity": "MODERATE"},
    "AUTO": {"primary_risk": "SUPPLY_CHAIN_DISRUPTION", "sensitivity": "MODERATE"},
}


def evaluate_geopolitical_risk(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None,
) -> Dict[str, Any]:
    """Evaluate geopolitical and macro-economic event risks.

    Args:
        symbol: Equity ticker symbol.
        as_of: Optional cutoff datetime.
        store: Optional ResearchDataStore.

    Returns:
        Dict with status, macro_risk_rating, sector_sensitivity, active_triggers, conviction_penalty_pct, evidence, meta.
    """
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()

    events = []
    company = None
    try:
        timeline = data_store.get_timeline(norm_symbol, as_of=as_of)
        company = timeline[0] if isinstance(timeline, tuple) and len(timeline) > 0 else None
        events = timeline[2] if isinstance(timeline, tuple) and len(timeline) > 2 else []
    except Exception as e:
        logger.warning("Geopolitical engine error accessing ResearchDataStore for %s: %s", norm_symbol, e)

    sector = getattr(company, "sector", "UNKNOWN").upper() if company else "UNKNOWN"
    sector_profile = SECTOR_GEOPOLITICAL_SENSITIVITIES.get(sector, {"primary_risk": "GENERAL_MACRO", "sensitivity": "LOW"})

    # Filter macro and geopolitical events
    macro_event_types = {
        "geopolitical_alert",
        "macro_economic_policy",
        "rbi_monetary_policy",
        "crude_oil_shock",
        "tariff_duty_change",
        "sanctions_export_control",
        "fx_volatility",
    }

    active_triggers: List[Dict[str, Any]] = []
    evidence: List[str] = []

    for evt in events:
        e_type = str(getattr(evt, "event_type", "")).lower()
        if e_type in macro_event_types or "macro" in e_type or "geopolitical" in e_type:
            severity = getattr(evt, "severity", "MODERATE").upper()
            title = getattr(evt, "title", "Macro Event")
            e_date = str(getattr(evt, "event_date", ""))[:10]

            active_triggers.append({
                "event_type": e_type,
                "title": title,
                "event_date": e_date,
                "severity": severity,
            })
            evidence.append(f"Geopolitical/Macro Event [{e_date}]: {title} (Severity: {severity})")

    if not active_triggers:
        return {
            "symbol": norm_symbol,
            "status": "DATA_UNAVAILABLE",
            "executed_at": get_ist_now_str(),
            "sector": sector,
            "sector_sensitivity": sector_profile,
            "macro_risk_rating": "LOW",
            "active_triggers": [],
            "conviction_penalty_pct": 0.0,
            "evidence": ["DATA_UNAVAILABLE: No macro or geopolitical event triggers observed in ResearchDataStore."],
            "meta": create_meta_header(source=f"Geopolitical Risk Engine ({norm_symbol})")
        }

    # Calculate conviction penalty based on severity count
    critical_count = sum(1 for t in active_triggers if t["severity"] in ("CRITICAL", "HIGH"))
    moderate_count = sum(1 for t in active_triggers if t["severity"] == "MODERATE")

    penalty_pct = round(min(25.0, (critical_count * 8.0) + (moderate_count * 3.0)), 1)
    if penalty_pct >= 15.0:
        risk_rating = "HIGH"
    elif penalty_pct >= 8.0:
        risk_rating = "MODERATE"
    else:
        risk_rating = "LOW"

    return {
        "symbol": norm_symbol,
        "status": "PRODUCTION",
        "executed_at": get_ist_now_str(),
        "sector": sector,
        "sector_sensitivity": sector_profile,
        "macro_risk_rating": risk_rating,
        "active_triggers": active_triggers,
        "conviction_penalty_pct": penalty_pct,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Geopolitical Risk Engine ({norm_symbol})")
    }

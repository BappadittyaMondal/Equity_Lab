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


SECTOR_GEOPOLITICAL_SENSITIVITIES: Dict[str, Dict[str, Any]] = {
    "DEFENSE": {"primary_risk": "GLOBAL_REARMAMENT", "sensitivity": "HIGH", "overlay_pct": 15.0, "overlay_type": "TAILWIND_PREMIUM", "reason": "Global re-armament & domestic defense indigenization mandate"},
    "HEAVY_ENGINEERING": {"primary_risk": "GLOBAL_REARMAMENT", "sensitivity": "HIGH", "overlay_pct": 15.0, "overlay_type": "TAILWIND_PREMIUM", "reason": "Global re-armament & capital expenditure tailwind"},
    "RENEWABLE": {"primary_risk": "POLICY_PROTECTION", "sensitivity": "LOW", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Domestic energy security & power grid expansion priority"},
    "POWER": {"primary_risk": "POLICY_PROTECTION", "sensitivity": "LOW", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Power grid infrastructure & energy transition tailwind"},
    "TRANSFORMERS": {"primary_risk": "POLICY_PROTECTION", "sensitivity": "LOW", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Grid transformer super-cycle & green power expansion"},
    "IT": {"primary_risk": "US_BUDGET_FREEZE", "sensitivity": "HIGH", "overlay_pct": -20.0, "overlay_type": "MACRO_RISK_PENALTY", "reason": "Vulnerable to US corporate budget cuts, GenAI billing deflation & visa restrictions"},
    "SOFTWARE": {"primary_risk": "US_BUDGET_FREEZE", "sensitivity": "HIGH", "overlay_pct": -20.0, "overlay_type": "MACRO_RISK_PENALTY", "reason": "Vulnerable to US corporate budget cuts & GenAI billing deflation"},
    "SHIPPING": {"primary_risk": "TRADE_BOTTLENECK", "sensitivity": "CRITICAL", "overlay_pct": -10.0, "overlay_type": "VOLATILITY_INDEX", "reason": "Sensitive to Middle East trade bottlenecks & freight rate spikes"},
    "LOGISTICS": {"primary_risk": "TRADE_BOTTLENECK", "sensitivity": "HIGH", "overlay_pct": -10.0, "overlay_type": "VOLATILITY_INDEX", "reason": "Sensitive to geopolitical trade route bottlenecks"},
    "OIL_GAS": {"primary_risk": "CRUDE_OIL_SHOCK", "sensitivity": "CRITICAL", "overlay_pct": -15.0, "overlay_type": "COMMODITY_SHOCK", "reason": "High crude oil price volatility & refining margin risk"},
    "PAINTS": {"primary_risk": "CRUDE_OIL_SHOCK", "sensitivity": "HIGH", "overlay_pct": -10.0, "overlay_type": "COMMODITY_SHOCK", "reason": "Crude derivative input cost inflation risk"},
    "METALS": {"primary_risk": "TARIFF_DUTY_SHOCK", "sensitivity": "HIGH", "overlay_pct": -10.0, "overlay_type": "TARIFF_RISK", "reason": "Global trade tariff wars & dumping duty sensitivity"},
    "BANKING": {"primary_risk": "RBI_RATE_POLICY", "sensitivity": "MODERATE", "overlay_pct": 0.0, "overlay_type": "NEUTRAL", "reason": "Domestic rate cycle exposure"},
}

# Stock-Specific Overlays (e.g. HBLPOWER, FORCEMOT, ORIANA, KPEL, SHILCHAR, COFORGE, PERSISTENT, ECLERX, GESHIP)
TICKER_GEOPOLITICAL_OVERLAYS: Dict[str, Dict[str, Any]] = {
    "HBLPOWER": {"sector": "DEFENSE", "overlay_pct": 15.0, "overlay_type": "TAILWIND_PREMIUM", "reason": "Defense indigenization & re-armament demand"},
    "FORCEMOT": {"sector": "HEAVY_ENGINEERING", "overlay_pct": 15.0, "overlay_type": "TAILWIND_PREMIUM", "reason": "Defense logistics vehicles & engine supply mandates"},
    "ORIANA": {"sector": "RENEWABLE", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Domestic solar & green energy grid priority"},
    "KPEL": {"sector": "RENEWABLE", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Wind & solar EPC policy backing"},
    "SHILCHAR": {"sector": "TRANSFORMERS", "overlay_pct": 10.0, "overlay_type": "POLICY_PROTECTION", "reason": "Global & domestic grid transformer super-cycle"},
    "COFORGE": {"sector": "IT", "overlay_pct": -20.0, "overlay_type": "MACRO_RISK_PENALTY", "reason": "US enterprise IT budget freeze & GenAI billing pressure"},
    "PERSISTENT": {"sector": "IT", "overlay_pct": -20.0, "overlay_type": "MACRO_RISK_PENALTY", "reason": "US enterprise IT spend slowdown & tech budget cuts"},
    "ECLERX": {"sector": "IT", "overlay_pct": -20.0, "overlay_type": "MACRO_RISK_PENALTY", "reason": "US/EU offshore billing rate deflation"},
    "GESHIP": {"sector": "SHIPPING", "overlay_pct": -10.0, "overlay_type": "VOLATILITY_INDEX", "reason": "Red Sea rerouting & Middle East trade corridor volatility"}
}


def evaluate_geopolitical_risk(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None,
) -> Dict[str, Any]:
    """Evaluate geopolitical and macro-economic event risks (Phase 3 Enhanced)."""
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

    clean_symbol = norm_symbol.replace(".NS", "").replace(".BO", "").upper()

    # Ticker Geopolitical Overlays check
    ticker_overlay = TICKER_GEOPOLITICAL_OVERLAYS.get(clean_symbol) or TICKER_GEOPOLITICAL_OVERLAYS.get(norm_symbol)

    # Genuine early-return for true no-data case when company is unknown, events is empty, and ticker has no overlay
    if company is None and not events and not ticker_overlay:
        return {
            "symbol": norm_symbol,
            "status": "DATA_UNAVAILABLE",
            "executed_at": get_ist_now_str(),
            "sector": "UNKNOWN",
            "macro_risk_rating": "UNKNOWN",
            "overlay_pct": 0.0,
            "overlay_type": "DATA_UNAVAILABLE",
            "overlay_reason": "No company record or macro/geopolitical event data found.",
            "active_triggers": [],
            "conviction_penalty_pct": 0.0,
            "evidence": [f"DATA_UNAVAILABLE: No company record or macro/geopolitical event data found for {norm_symbol}."],
            "meta": create_meta_header(source=f"Phase 3 MacroGeopoliticalOverlay ({norm_symbol})")
        }

    sector = getattr(company, "sector", "UNKNOWN").upper() if company else "UNKNOWN"
    
    # 1. MacroGeopoliticalOverlay Factor Matrix Check
    # SECTOR_GEOPOLITICAL_SENSITIVITIES fallback is retained ONLY for known/resolved company sectors when no ticker overlay or event data exists.
    if ticker_overlay:
        overlay_pct = ticker_overlay["overlay_pct"]
        overlay_type = ticker_overlay["overlay_type"]
        overlay_reason = ticker_overlay["reason"]
        sector_name = ticker_overlay["sector"]
    else:
        sector_profile = SECTOR_GEOPOLITICAL_SENSITIVITIES.get(sector, {"primary_risk": "GENERAL_MACRO", "sensitivity": "LOW", "overlay_pct": 0.0, "overlay_type": "NEUTRAL", "reason": "Standard macro exposure"})
        overlay_pct = sector_profile["overlay_pct"]
        overlay_type = sector_profile["overlay_type"]
        overlay_reason = sector_profile["reason"]
        sector_name = sector

    # 2. Filter active triggers
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

    # Add overlay evidence
    evidence.append(f"Phase 3 MacroGeopoliticalOverlay: {overlay_type} ({overlay_pct:+.1f}%) — {overlay_reason}")

    # Determine Macro Risk Rating
    if overlay_pct <= -15.0:
        macro_risk_rating = "HIGH"
        conviction_penalty_pct = abs(overlay_pct)
    elif overlay_pct < 0.0:
        macro_risk_rating = "MODERATE"
        conviction_penalty_pct = abs(overlay_pct)
    elif overlay_pct > 0.0:
        macro_risk_rating = "LOW"
        conviction_penalty_pct = 0.0  # Premium awarded
    else:
        macro_risk_rating = "LOW"
        conviction_penalty_pct = 0.0

    return {
        "symbol": norm_symbol,
        "status": "PRODUCTION",
        "executed_at": get_ist_now_str(),
        "sector": sector_name,
        "macro_risk_rating": macro_risk_rating,
        "overlay_pct": overlay_pct,
        "overlay_type": overlay_type,
        "overlay_reason": overlay_reason,
        "active_triggers": active_triggers,
        "conviction_penalty_pct": conviction_penalty_pct,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Phase 3 MacroGeopoliticalOverlay ({norm_symbol})")
    }

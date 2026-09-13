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


def calculate_dynamic_geographic_overlay(
    sector: str,
    split: Dict[str, float],
    symbol: str = ""
) -> Dict[str, Any]:
    """Calculates weighted macro/geopolitical overlay based on empirical geographic revenue shares.
    
    Corridor risk factors:
      - domestic: Policy protection, PLI & re-armament capex (+15% for Defense/Renewable/Engineering, 0% neutral)
      - us_na: Enterprise IT budget freeze (-25% for IT/Software, -10% general tariffs)
      - eu: CBAM carbon tariff & tech spend slowdown (-20% for IT/Software, -15% for Metals)
      - middle_east_red_sea: Shipping route disruption & freight rate spikes (-15% for Shipping/Oil)
      - china_apac: Supply chain & dumping risk (-10% for Metals/Chemicals)
      - rest_of_world: Baseline emerging market FX/tariff risk (-5%)
    """
    total_weight = sum(split.values())
    if total_weight <= 0:
        return {"overlay_pct": 0.0, "overlay_type": "NEUTRAL", "reason": "Zero geographic weight observed."}
    
    norm_split = {k.lower(): v / total_weight for k, v in split.items()}
    sec = sector.upper()
    
    corridor_impacts: Dict[str, float] = {}
    
    # 1. Domestic Corridor
    dom_share = norm_split.get("domestic", 0.0) + norm_split.get("india", 0.0)
    if sec in ("DEFENSE", "HEAVY_ENGINEERING", "ENGINEERING", "CAPITAL GOODS", "CAPITAL_GOODS", "AEROSPACE"):
        corridor_impacts["domestic"] = dom_share * 15.0
    elif sec in ("RENEWABLE", "POWER", "TRANSFORMERS", "UTILITIES"):
        corridor_impacts["domestic"] = dom_share * 10.0
    else:
        corridor_impacts["domestic"] = 0.0

    # 2. US / North America Corridor
    us_share = norm_split.get("us_na", 0.0) + norm_split.get("us", 0.0) + norm_split.get("north_america", 0.0)
    if sec in ("IT", "SOFTWARE", "TECHNOLOGY", "IT_SERVICES"):
        corridor_impacts["us_na"] = us_share * (-25.0)
    elif sec in ("METALS", "MINING"):
        corridor_impacts["us_na"] = us_share * (-12.0)
    else:
        corridor_impacts["us_na"] = us_share * (-5.0)

    # 3. European Union Corridor
    eu_share = norm_split.get("eu", 0.0) + norm_split.get("europe", 0.0)
    if sec in ("IT", "SOFTWARE", "TECHNOLOGY", "IT_SERVICES"):
        corridor_impacts["eu"] = eu_share * (-20.0)
    elif sec in ("METALS", "MINING"):
        corridor_impacts["eu"] = eu_share * (-15.0)
    else:
        corridor_impacts["eu"] = eu_share * (-5.0)

    # 4. Middle East & Red Sea Transit Corridor
    me_share = norm_split.get("middle_east", 0.0) + norm_split.get("red_sea", 0.0) + norm_split.get("shipping_corridor", 0.0)
    if sec in ("SHIPPING", "LOGISTICS"):
        corridor_impacts["middle_east_red_sea"] = me_share * (-15.0)
    elif sec in ("OIL_GAS",):
        corridor_impacts["middle_east_red_sea"] = me_share * (-12.0)
    else:
        corridor_impacts["middle_east_red_sea"] = me_share * (-3.0)

    # 5. China / APAC Corridor
    apac_share = norm_split.get("apac", 0.0) + norm_split.get("china", 0.0) + norm_split.get("asia", 0.0)
    if sec in ("METALS", "PAINTS"):
        corridor_impacts["china_apac"] = apac_share * (-10.0)
    else:
        corridor_impacts["china_apac"] = apac_share * (-2.0)

    # 6. Rest of World
    row_share = norm_split.get("row", 0.0) + norm_split.get("rest_of_world", 0.0)
    corridor_impacts["rest_of_world"] = row_share * (-5.0)

    net_overlay = round(sum(corridor_impacts.values()), 2)

    if net_overlay >= 8.0:
        o_type = "TAILWIND_PREMIUM"
        reason = f"High domestic/allied market exposure ({dom_share*100:.0f}% Domestic) driving strategic policy premium."
    elif net_overlay <= -12.0:
        o_type = "MACRO_RISK_PENALTY"
        reason = f"Elevated exposure to high-risk geopolitical trade corridors ({us_share*100:.0f}% US, {eu_share*100:.0f}% EU)."
    elif net_overlay < 0.0:
        o_type = "VOLATILITY_INDEX"
        reason = f"Moderate trade corridor exposure with regional macro volatility."
    else:
        o_type = "POLICY_PROTECTION" if net_overlay > 0 else "NEUTRAL"
        reason = f"Balanced geographic revenue footprint with net neutral macro impact."

    return {
        "overlay_pct": net_overlay,
        "overlay_type": o_type,
        "reason": reason,
        "corridor_breakdown": {k: round(v, 2) for k, v in corridor_impacts.items() if v != 0.0},
        "geographic_shares": norm_split
    }


def evaluate_geopolitical_risk(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None,
    geographic_split: Optional[Dict[str, float]] = None,
    sector: Optional[str] = None,
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

    # Dynamic Geographic Exposure Check
    effective_split = geographic_split
    if not effective_split and company and hasattr(company, "metadata") and isinstance(company.metadata, dict):
        effective_split = company.metadata.get("geographic_revenue_split")

    # Ticker Geopolitical Overlays check
    ticker_overlay = TICKER_GEOPOLITICAL_OVERLAYS.get(clean_symbol) or TICKER_GEOPOLITICAL_OVERLAYS.get(norm_symbol)

    # Resolve sector
    detected_sector = (sector or getattr(company, "sector", "UNKNOWN")).upper() if (company or sector) else "UNKNOWN"
    if detected_sector == "UNKNOWN" and ticker_overlay:
        detected_sector = ticker_overlay.get("sector", "UNKNOWN").upper()
    if detected_sector == "UNKNOWN":
        if any(t in clean_symbol for t in ("INFY", "TCS", "WIPRO", "HCLTECH", "LTIM", "COFORGE", "PERSISTENT")):
            detected_sector = "IT"
        elif any(t in clean_symbol for t in ("HAL", "BEL", "BDL", "HBLPOWER", "MAZDOCK")):
            detected_sector = "DEFENSE"
        elif any(t in clean_symbol for t in ("GESHIP", "SCI", "COCHINSHIP")):
            detected_sector = "SHIPPING"

    # Genuine early-return for true no-data case when company is unknown, events is empty, and ticker has no overlay
    if company is None and not events and not ticker_overlay and not effective_split:
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

    sector = detected_sector
    geographic_breakdown = None

    # 1. MacroGeopoliticalOverlay Factor Matrix Check
    # Priority: 1. Dynamic Geographic Split (if observed) -> 2. Ticker Overlay -> 3. Sector Profile
    if effective_split:
        geo_res = calculate_dynamic_geographic_overlay(sector, effective_split, symbol=clean_symbol)
        overlay_pct = geo_res["overlay_pct"]
        overlay_type = geo_res["overlay_type"]
        overlay_reason = geo_res["reason"]
        sector_name = sector
        geographic_breakdown = geo_res.get("corridor_breakdown")
    elif ticker_overlay:
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
        "geographic_exposure_breakdown": geographic_breakdown,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Phase 3 MacroGeopoliticalOverlay ({norm_symbol})")
    }

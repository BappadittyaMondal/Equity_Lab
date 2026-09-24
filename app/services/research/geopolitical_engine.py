"""Geopolitical & Macro Risk Assessment Engine — Phase 8.

Monitors macro-economic policy shocks, crude oil volatility, trade tariff changes,
geopolitical alerts, and sector sensitivity metrics from ResearchDataStore.

Pipeline Law: No synthetic default risk scores. If no macro/geopolitical events
are found in the point-in-time observation store, emits explicit DATA_UNAVAILABLE.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

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
    "SHIPPING_TANKERS": {"primary_risk": "TON_MILE_EXPANSION", "sensitivity": "HIGH", "overlay_pct": 15.0, "overlay_type": "TAILWIND_PREMIUM", "reason": "Crude/product tanker day-charter rate surge from Cape of Good Hope rerouting & ton-mile demand expansion"},
    "CONTAINER_CARGO": {"primary_risk": "TRADE_BOTTLENECK", "sensitivity": "CRITICAL", "overlay_pct": -10.0, "overlay_type": "VOLATILITY_INDEX", "reason": "Sensitive to Middle East trade bottlenecks & unhedged demurrage risk"},
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
    if sec in ("SHIPPING_TANKERS", "TANKERS"):
        corridor_impacts["middle_east_red_sea"] = me_share * (+15.0)
    elif sec in ("SHIPPING", "LOGISTICS", "CONTAINER_CARGO"):
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
    sub_segment: Optional[str] = None,
    pdlr: Optional[float] = None,
) -> Dict[str, Any]:
    """Evaluate geopolitical and macro-economic event risks (Phase 3 & Phase 140 Enhanced)."""
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
    if sub_segment and str(sub_segment).upper() in ("TANKERS", "SHIPPING_TANKERS", "CRUDE_TANKER", "PRODUCT_TANKER"):
        detected_sector = "SHIPPING_TANKERS"
    elif detected_sector == "UNKNOWN" and ticker_overlay:
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
    elif sub_segment and str(sub_segment).upper() in ("TANKERS", "SHIPPING_TANKERS", "CRUDE_TANKER", "PRODUCT_TANKER"):
        sec_prof = SECTOR_GEOPOLITICAL_SENSITIVITIES["SHIPPING_TANKERS"]
        overlay_pct = sec_prof["overlay_pct"]
        overlay_type = sec_prof["overlay_type"]
        overlay_reason = sec_prof["reason"]
        sector_name = "SHIPPING_TANKERS"
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

    # Determine Macro Risk Rating & Apply PDLR Gate if supplied
    pdlr_gate_data = None
    if pdlr is not None:
        pdlr_res = evaluate_physical_disruption_gate(pdlr=pdlr, raw_overlay_pct=overlay_pct, sector=sector_name)
        effective_pct = pdlr_res["effective_overlay_pct"]
        pdlr_gate_data = pdlr_res
        evidence.append(f"Phase 140 PDLR Gate: {pdlr_res['classification']} (PDLR={pdlr:.2f}) → Effective Overlay {effective_pct:+.1f}%")
    else:
        effective_pct = overlay_pct

    if effective_pct <= -15.0:
        macro_risk_rating = "HIGH"
        conviction_penalty_pct = abs(effective_pct)
    elif effective_pct < 0.0:
        macro_risk_rating = "MODERATE"
        conviction_penalty_pct = abs(effective_pct)
    elif effective_pct > 0.0:
        macro_risk_rating = "LOW"
        conviction_penalty_pct = 0.0  # Premium awarded
    else:
        macro_risk_rating = "LOW"
        conviction_penalty_pct = 0.0

    res_dict = {
        "symbol": norm_symbol,
        "status": "PRODUCTION",
        "executed_at": get_ist_now_str(),
        "sector": sector_name,
        "macro_risk_rating": macro_risk_rating,
        "overlay_pct": overlay_pct,
        "effective_overlay_pct": effective_pct,
        "overlay_type": overlay_type,
        "overlay_reason": overlay_reason,
        "active_triggers": active_triggers,
        "conviction_penalty_pct": conviction_penalty_pct,
        "geographic_exposure_breakdown": geographic_breakdown,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Phase 3 MacroGeopoliticalOverlay ({norm_symbol})")
    }
    if pdlr_gate_data:
        res_dict["pdlr_gate"] = pdlr_gate_data

    return res_dict



# ── Phase 139: β_geo Vectorized Geopolitical Shock Sensitivity Matrix ──────────
# Asset-level sensitivity vectors across 5 global shock scenarios.
# Beta convention: +1.0 = full tailwind, -1.0 = full headwind per unit shock magnitude.

# Sector-level β_geo matrix [Crude Spike, Maritime Chokepoint, China Dumping, Grid Hardware Deficit, US Rate Hike]
# Values are β multipliers: positive = tailwind, negative = headwind (scaled -1.0 to +1.0)
_GEO_SHOCK_BETA_MATRIX: Dict[str, Dict[str, float]] = {
    # (Crude Spike +30%, Maritime Chokepoint, China Dumping, Grid HW Deficit, US +100bps)
    "OIL_GAS":          {"crude": +0.80, "maritime": -0.60, "china_dump": +0.10, "grid_hw": -0.10, "us_rate": -0.20},
    "REFINING":         {"crude": -0.50, "maritime": -0.30, "china_dump": +0.05, "grid_hw": -0.05, "us_rate": -0.15},
    "SHIPPING":         {"crude": -0.30, "maritime": -0.90, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.10},
    "SHIPPING_TANKERS": {"crude": +0.50, "maritime": +0.85, "china_dump": -0.05, "grid_hw": -0.05, "us_rate": -0.10},
    "CONTAINER_CARGO":  {"crude": -0.40, "maritime": -0.90, "china_dump": -0.15, "grid_hw": -0.05, "us_rate": -0.10},
    "LOGISTICS":        {"crude": -0.20, "maritime": -0.50, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.05},
    "PAINTS":           {"crude": -0.60, "maritime": -0.10, "china_dump": -0.15, "grid_hw": -0.05, "us_rate": -0.10},
    "CHEMICALS":        {"crude": -0.40, "maritime": -0.15, "china_dump": -0.20, "grid_hw": -0.05, "us_rate": -0.10},
    "METALS":           {"crude": -0.15, "maritime": -0.20, "china_dump": -0.70, "grid_hw": +0.20, "us_rate": -0.25},
    "MINING":           {"crude": -0.10, "maritime": -0.15, "china_dump": -0.50, "grid_hw": +0.25, "us_rate": -0.20},
    "IT":               {"crude": +0.05, "maritime": +0.00, "china_dump": +0.10, "grid_hw": -0.05, "us_rate": -0.40},
    "SOFTWARE":         {"crude": +0.05, "maritime": +0.00, "china_dump": +0.10, "grid_hw": -0.05, "us_rate": -0.40},
    "BANKING":          {"crude": -0.20, "maritime": -0.05, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.55},
    "NBFC":             {"crude": -0.15, "maritime": -0.05, "china_dump": -0.05, "grid_hw": -0.05, "us_rate": -0.50},
    "DEFENSE":          {"crude": -0.05, "maritime": +0.10, "china_dump": +0.10, "grid_hw": +0.30, "us_rate": -0.05},
    "HEAVY_ENGINEERING":{"crude": -0.10, "maritime": +0.05, "china_dump": -0.20, "grid_hw": +0.50, "us_rate": -0.10},
    "CAPITAL_GOODS":    {"crude": -0.10, "maritime": +0.05, "china_dump": -0.15, "grid_hw": +0.45, "us_rate": -0.10},
    "RENEWABLE":        {"crude": +0.30, "maritime": -0.05, "china_dump": -0.20, "grid_hw": +0.70, "us_rate": -0.10},
    "POWER":            {"crude": -0.10, "maritime": -0.05, "china_dump": -0.10, "grid_hw": +0.40, "us_rate": -0.10},
    "TRANSFORMERS":     {"crude": -0.05, "maritime": -0.05, "china_dump": -0.15, "grid_hw": +0.85, "us_rate": -0.05},
    "PHARMA":           {"crude": -0.10, "maritime": -0.10, "china_dump": -0.15, "grid_hw": -0.05, "us_rate": -0.15},
    "FMCG":             {"crude": -0.20, "maritime": -0.05, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.15},
    "CONSUMER":         {"crude": -0.15, "maritime": -0.05, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.20},
    "AUTO":             {"crude": -0.30, "maritime": -0.10, "china_dump": -0.20, "grid_hw": -0.10, "us_rate": -0.20},
    "AUTO_ANCILLARY":   {"crude": -0.20, "maritime": -0.10, "china_dump": -0.25, "grid_hw": -0.10, "us_rate": -0.15},
    "CEMENT":           {"crude": -0.15, "maritime": -0.05, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.20},
    "REAL_ESTATE":      {"crude": -0.15, "maritime": -0.05, "china_dump": -0.05, "grid_hw": -0.05, "us_rate": -0.40},
    "TEXTILES":         {"crude": -0.10, "maritime": -0.15, "china_dump": -0.30, "grid_hw": -0.05, "us_rate": -0.10},
    "AGRI":             {"crude": -0.15, "maritime": -0.10, "china_dump": -0.10, "grid_hw": -0.05, "us_rate": -0.10},
    "DIVERSIFIED":      {"crude": -0.10, "maritime": -0.05, "china_dump": -0.10, "grid_hw": +0.05, "us_rate": -0.20},
}

_DEFAULT_GEO_BETA: Dict[str, float] = {
    "crude": -0.10, "maritime": -0.05, "china_dump": -0.10, "grid_hw": +0.05, "us_rate": -0.20
}


def compute_geo_shock_sensitivity(
    symbol: str,
    sector: Optional[str] = None,
    sub_segment: Optional[str] = None,
    use_calibrated_matrix: bool = True,
) -> Dict[str, Any]:
    """Compute vectorized β_geo geopolitical shock sensitivity for a single asset.

    Returns 5 scenario betas and aggregate geo-beta verdict.
    Beta convention: positive = tailwind, negative = headwind.
    Magnitude: |β| in [0.0, 1.0]. Equal-weighted aggregate over 5 shocks.

    Shock scenarios:
      1. Crude Oil Spike +30% (Brent from $85 → $110)
      2. Maritime Chokepoint (Strait of Hormuz / Red Sea blockade)
      3. China Export Dumping (steel, chemicals, solar panels)
      4. Grid Hardware Deficit (transformer / semiconductor shortages)
      5. US Interest Rate Hike +100bps (Fed funds target increase)
    """
    norm_symbol = normalize_symbol(symbol)
    sector_key = str(sector or "DIVERSIFIED").upper().replace(" ", "_")

    # Tanker sub-segment routing
    if sub_segment and str(sub_segment).upper() in ("TANKERS", "SHIPPING_TANKERS", "CRUDE_TANKER", "PRODUCT_TANKER"):
        sector_key = "SHIPPING_TANKERS"
    elif norm_symbol in TICKER_GEOPOLITICAL_OVERLAYS and not sector:
        sector_key = TICKER_GEOPOLITICAL_OVERLAYS[norm_symbol].get("sector", sector_key).upper()

    active_matrix = _GEO_SHOCK_BETA_MATRIX
    if use_calibrated_matrix:
        try:
            from app.services.monitoring.event_prediction_ledger import EventPredictionLedgerService
            active_matrix = EventPredictionLedgerService.get_calibrated_beta_matrix()
        except Exception:
            active_matrix = _GEO_SHOCK_BETA_MATRIX

    betas = active_matrix.get(sector_key, _DEFAULT_GEO_BETA)

    b_crude = betas["crude"]
    b_maritime = betas["maritime"]
    b_china = betas["china_dump"]
    b_grid = betas["grid_hw"]
    b_us_rate = betas["us_rate"]

    aggregate = round((b_crude + b_maritime + b_china + b_grid + b_us_rate) / 5.0, 4)

    # Dominant shock: scenario with maximum absolute impact
    shock_map = {
        "CRUDE_SPIKE_30PCT": b_crude,
        "MARITIME_CHOKEPOINT": b_maritime,
        "CHINA_DUMPING": b_china,
        "GRID_HARDWARE_DEFICIT": b_grid,
        "US_RATE_HIKE_100BPS": b_us_rate,
    }
    dominant_shock = max(shock_map, key=lambda k: abs(shock_map[k]))

    # Verdict classification
    if aggregate >= 0.15:
        verdict = "GEO_TAILWIND"
    elif aggregate >= -0.05:
        verdict = "GEO_NEUTRAL"
    elif aggregate >= -0.25:
        verdict = "GEO_HEADWIND"
    else:
        verdict = "GEO_CRITICAL"

    evidence: List[str] = [
        f"β_crude_spike = {b_crude:+.2f} | β_maritime = {b_maritime:+.2f} | β_china_dumping = {b_china:+.2f}",
        f"β_grid_hw_deficit = {b_grid:+.2f} | β_us_rate_hike = {b_us_rate:+.2f}",
        f"Aggregate β_geo = {aggregate:+.4f} → {verdict}",
        f"Dominant shock scenario: {dominant_shock} (β = {shock_map[dominant_shock]:+.2f})",
        f"Sector key used: {sector_key}",
    ]

    return {
        "symbol": norm_symbol,
        "sector": sector_key,
        "beta_crude_spike": b_crude,
        "beta_maritime_chokepoint": b_maritime,
        "beta_china_dumping": b_china,
        "beta_grid_hardware_deficit": b_grid,
        "beta_us_rate_hike": b_us_rate,
        "aggregate_geo_beta": aggregate,
        "dominant_shock": dominant_shock,
        "verdict": verdict,
        "evidence": evidence,
        "executed_at": get_ist_now_str(),
        "meta": create_meta_header(source=f"Phase 139 β_geo ShockMatrix ({norm_symbol})")
    }


# ── Phase 140: Pre-Event Weak Signal (PEWS) & Physical Disruption Gate (PDLR) ──

class PreEventSignal(BaseModel):
    """Container for an observed geopolitical leading indicator / weak signal."""
    signal_type: str  # AIRSPACE_NOTAM_CLOSURE, AIS_TRANSPONDER_DARK, DIPLOMATIC_SCHEDULE_COLLAPSE, CRUDE_CALL_SKEW_SPIKE, SOVEREIGN_FX_SWAP_EMERGENCY, LEADER_SIGNALLING_ANOMALY
    intensity: float = 1.0  # Normalized intensity [0.0, 1.0]
    likelihood_ratio: Optional[float] = None  # Likelihood ratio P(S|Event)/P(S|¬Event)
    confidence: float = 1.0  # Observation confidence [0.0, 1.0]
    age_hours: float = 0.0  # Elapsed hours since detection
    theater: str = "GLOBAL"  # MIDDLE_EAST, SOUTH_ASIA, TAIWAN_STRAIT, EASTERN_EUROPE, GLOBAL
    source_description: str = ""


PEWS_SIGNAL_PROFILES: Dict[str, Dict[str, float]] = {
    "AIRSPACE_NOTAM_CLOSURE": {"lr": 8.5, "half_life_hours": 36.0},
    "AIS_TRANSPONDER_DARK": {"lr": 6.0, "half_life_hours": 24.0},
    "DIPLOMATIC_SCHEDULE_COLLAPSE": {"lr": 4.5, "half_life_hours": 48.0},
    "CRUDE_CALL_SKEW_SPIKE": {"lr": 5.2, "half_life_hours": 24.0},
    "SOVEREIGN_FX_SWAP_EMERGENCY": {"lr": 3.5, "half_life_hours": 72.0},
    "LEADER_SIGNALLING_ANOMALY": {"lr": 2.8, "half_life_hours": 48.0},
}


def evaluate_pre_event_weak_signals(
    signals: List[PreEventSignal],
    prior_probability: float = 0.10,
    theater: str = "GLOBAL",
) -> Dict[str, Any]:
    """Evaluates heterogeneous weak signals via Bayesian log-odds updating.

    Calculates the posterior strike/shock probability P(Event | S_1, ..., S_n)
    before kinetic or market open reality unfolds.
    """
    if not signals:
        return {
            "status": "NO_SIGNALS_OBSERVED",
            "pews_probability": prior_probability,
            "imminence_rating": "BASELINE_MONITORING",
            "log_odds_delta": 0.0,
            "dominant_signals": [],
            "theaters_at_risk": [theater],
            "recommended_stance": "STATUS_QUO",
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source="Phase 140 PEWS Evaluator")
        }

    # Clamped prior probability [0.01, 0.99]
    p0 = max(0.01, min(0.99, prior_probability))
    prior_logit = math.log(p0 / (1.0 - p0))

    total_delta_logit = 0.0
    signal_contributions = []

    for s in signals:
        stype = s.signal_type.upper()
        prof = PEWS_SIGNAL_PROFILES.get(stype, {"lr": 2.5, "half_life_hours": 48.0})
        lr = s.likelihood_ratio if s.likelihood_ratio is not None and s.likelihood_ratio > 0 else prof["lr"]
        half_life = prof["half_life_hours"]

        # Temporal decay: weight = 0.5^(age / half_life)
        decay = 0.5 ** (max(0.0, s.age_hours) / max(1.0, half_life))
        eff_weight = max(0.0, min(1.0, s.intensity)) * max(0.0, min(1.0, s.confidence)) * decay
        delta_logit = eff_weight * math.log(max(0.1, lr))

        total_delta_logit += delta_logit
        signal_contributions.append({
            "signal_type": stype,
            "raw_lr": round(lr, 2),
            "effective_weight": round(eff_weight, 3),
            "delta_logit": round(delta_logit, 3),
            "theater": s.theater,
            "source_description": s.source_description,
        })

    posterior_logit = prior_logit + total_delta_logit
    # Sigmoid posterior probability
    try:
        posterior_prob = 1.0 / (1.0 + math.exp(-posterior_logit))
    except OverflowError:
        posterior_prob = 1.0 if posterior_logit > 0 else 0.0
    posterior_prob = round(max(0.0, min(1.0, posterior_prob)), 4)

    # Imminence classification
    if posterior_prob >= 0.80:
        imminence = "CRITICAL_IMMINENT_INTERVENTION"
        stance = "EXECUTE_PRE_EVENT_HEDGES"
    elif posterior_prob >= 0.55:
        imminence = "ELEVATED_PRE_STRIKE_PROBABILITY"
        stance = "RAISE_CASH_AND_TACTICAL_VOLATILITY_STOPS"
    elif posterior_prob >= 0.25:
        imminence = "WATCHLIST_STAGE_TENSION"
        stance = "SURVEILLANCE_ACTIVE"
    else:
        imminence = "BASELINE_NOISE"
        stance = "STATUS_QUO"

    # Sort dominant signals by delta_logit descending
    dominant_signals = sorted(signal_contributions, key=lambda x: x["delta_logit"], reverse=True)
    theaters = list(set([s.theater for s in signals if s.theater] + [theater]))

    return {
        "status": "EVALUATED",
        "pews_probability": posterior_prob,
        "imminence_rating": imminence,
        "prior_probability": p0,
        "posterior_logit": round(posterior_logit, 4),
        "dominant_signals": dominant_signals,
        "theaters_at_risk": theaters,
        "recommended_stance": stance,
        "executed_at": get_ist_now_str(),
        "meta": create_meta_header(source="Phase 140 PEWS Evaluator")
    }


def evaluate_physical_disruption_gate(
    pdlr: float,
    raw_overlay_pct: float,
    sector: Optional[str] = None,
) -> Dict[str, Any]:
    """Physical Disruption Likelihood Ratio (PDLR) Gate.

    Distinguishes symbolic political rhetoric / posturing (PDLR < 0.40) from
    actual physical supply destruction / chokepoint blockades (PDLR >= 0.40).

    Rules:
      - PDLR < 0.40 (Symbolic Theater):
          Caps negative macro penalties to tactical volatility limit (max -3.0%).
          Blocks Tier 1 fatal vetoes and structural portfolio liquidations.
      - 0.40 <= PDLR < 0.70 (Elevated Friction):
          Applies 75% damped macro overlay. Allows tactical sizing haircuts (max 15%).
      - PDLR >= 0.70 (Physical Disruption Confirmed):
          Enforces full structural overlay and conviction rating downgrades.
    """
    ratio = round(max(0.0, float(pdlr)), 4)
    raw_pct = float(raw_overlay_pct)

    if ratio < 0.40:
        classification = "SYMBOLIC_THEATER_OR_POSTURING"
        # Cap negative penalty to max -3.0% tactical volatility hedge; preserve positive tailwinds
        effective_pct = max(raw_pct, -3.0) if raw_pct < 0.0 else raw_pct
        allow_fatal_veto = False
        allow_sizing_haircut = False
        gate_action = "CAP_PENALTY_TO_TACTICAL_VOLATILITY"
        thesis = (
            f"PDLR ({ratio:.2f} < 0.40) flags political posturing/theater without verified physical "
            f"supply destruction. Macro penalty capped at {effective_pct:+.1f}% (vs raw {raw_pct:+.1f}%). "
            f"Fatal portfolio liquidation blocked."
        )
    elif ratio < 0.70:
        classification = "ELEVATED_FRICTION_RISK"
        effective_pct = round(raw_pct * 0.75, 2)
        allow_fatal_veto = False
        allow_sizing_haircut = True
        gate_action = "DAMPED_MACRO_OVERLAY"
        thesis = (
            f"PDLR ({ratio:.2f}) indicates elevated friction and diplomatic tension. "
            f"Applying 75% damped macro overlay ({effective_pct:+.1f}%). Fatal vetoes withheld."
        )
    else:
        classification = "PHYSICAL_DISRUPTION_CONFIRMED"
        effective_pct = raw_pct
        allow_fatal_veto = True
        allow_sizing_haircut = True
        gate_action = "FULL_STRUCTURAL_MACRO_OVERLAY"
        thesis = (
            f"PDLR ({ratio:.2f} >= 0.70) confirms kinetic infrastructure strike / physical chokepoint blockade. "
            f"Full structural macro overlay enforced ({effective_pct:+.1f}%)."
        )

    return {
        "status": "GATED",
        "pdlr_ratio": ratio,
        "classification": classification,
        "gate_action": gate_action,
        "raw_overlay_pct": raw_pct,
        "effective_overlay_pct": effective_pct,
        "allow_fatal_veto": allow_fatal_veto,
        "allow_sizing_haircut": allow_sizing_haircut,
        "sector": sector or "UNKNOWN",
        "thesis": thesis,
        "executed_at": get_ist_now_str(),
        "meta": create_meta_header(source="Phase 140 PDLR Gate")
    }



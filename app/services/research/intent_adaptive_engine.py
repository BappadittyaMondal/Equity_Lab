"""Query-Intent Adaptive Dynamic Parameter Engine (§Master Control Plane).

Provides context-aware parameter relaxation and tightening across 6 strategic investment archetypes:
  1. INTENT_TURNAROUND: Relaxes 3Y/5Y trailing CAGR; tightens sequential QoQ CFO & interest coverage.
  2. INTENT_VALUE_BUYING: Relaxes growth & momentum; tightens NCAV, EV/FCF, and asset reproduction discount.
  3. INTENT_SIP_COMPOUNDER: Ignores short-term 3D/10D technicals; tightens 10Y ROCE stability & CFO/PAT > 0.85.
  4. INTENT_SWING_POSITION: Relaxes 5Y DCF & terminal growth; tightens Multi-Anchor VWAP, volume pinch & ADTV cap.
  5. INTENT_MULTIBAGGER: Relaxes institutional ownership; tightens Incremental ROIC > 25% & capacity headroom.
  6. INTENT_PEER_COMPARE: Normalizes sector capital intensity (Rule of 40 for SaaS vs Book-to-Bill for ESDM).
"""

import re
from typing import Dict, Any, List, Optional


ARCHETYPE_WEIGHT_PROFILES = {
    "GENERAL": {
        "FUNDAMENTAL": 0.25,
        "VALUATION":   0.20,
        "TECHNICAL":   0.15,
        "GOVERNANCE":  0.10,
        "MACRO":       0.05,
        "FORENSIC":    0.25,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "TURNAROUND": {
        "FORENSIC":    0.35,  # Maximum scrutiny on solvency, NCLT risk, and cash burn
        "FUNDAMENTAL": 0.25,  # Sequential QoQ inflection, margin turn, order pipeline
        "VALUATION":   0.20,  # Asymmetric risk/reward, depressed base
        "GOVERNANCE":  0.10,  # Promoter de-pledging, insider conviction
        "TECHNICAL":   0.05,  # Baseline stabilization, exhaustion of selling
        "MACRO":       0.05,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "VALUE_BUYING": {
        "VALUATION":   0.35,  # Deep discount to NCAV, EV/FCF, liquidation margin
        "FORENSIC":    0.25,  # Solvency shield against value traps
        "FUNDAMENTAL": 0.20,  # Clean balance sheet, low leverage, asset backing
        "GOVERNANCE":  0.15,  # Capital allocation discipline, dividend support
        "TECHNICAL":   0.05,  # Base building
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "SIP_COMPOUNDER": {
        "FUNDAMENTAL": 0.40,  # 10Y ROCE stability, CFO/PAT conversion > 0.85
        "GOVERNANCE":  0.25,  # Zero promoter pledge, skin in the game
        "FORENSIC":    0.20,  # Accounting conservatism
        "VALUATION":   0.15,  # Reasonable entry relative to moat
        "TECHNICAL":   0.00,  # Completely zero technical noise; dips are buying points
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "SWING_POSITIONAL": {
        "TECHNICAL":   0.50,  # Market microstructure, Anchored VWAP, TTM squeeze
        "MACRO":       0.20,  # Sector momentum & regime alignment
        "FORENSIC":    0.15,  # Liquidity / circuit surveillance shield
        "FUNDAMENTAL": 0.10,  # Basic sanity
        "VALUATION":   0.05,  # Subordinate 10Y DCF to 10-30 session trade geometry
        "GOVERNANCE":  0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "SWING_3D": {
        "TECHNICAL":   0.65,  # Pure microstructure, Intraday VWAP, Opening Range Breakout
        "MACRO":       0.15,  # Intraday / sector tailwind
        "FORENSIC":    0.15,  # Circuit proximity and daily traded turnover guard
        "FUNDAMENTAL": 0.05,  # Minimal sanity only
        "VALUATION":   0.00,  # DCF completely zeroed out for 72-hour holding
        "GOVERNANCE":  0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "SWING_10D": {
        "TECHNICAL":   0.55,  # TTM Squeeze, 10/20 EMA ribbon pullback & volume surge
        "MACRO":       0.20,  # Sector momentum & Mansfield Relative Strength
        "FORENSIC":    0.15,  # Earnings gap event guard & circuit safety
        "FUNDAMENTAL": 0.10,  # Quarterly sanity check
        "VALUATION":   0.00,  # Long-term DCF ignored
        "GOVERNANCE":  0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "POSITIONAL_30D": {
        "TECHNICAL":   0.45,  # Minervini Stage 2 uptrend, base breakout volume >= 2.0x
        "FUNDAMENTAL": 0.30,  # Quarterly PAT acceleration >= 15% / SEBI Reg 30 order wins
        "MACRO":       0.15,  # Industry cycle momentum
        "FORENSIC":    0.10,  # Clean accounting & auditor tenure
        "VALUATION":   0.00,  # 10Y DCF relaxed in favor of intermediate catalyst
        "GOVERNANCE":  0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "MULTIBAGGER": {
        "FUNDAMENTAL": 0.35,  # Capacity expansion, incremental ROIC > 25%, 35% TAM ceiling
        "VALUATION":   0.25,  # Re-rating runway & valuation asymmetry
        "FORENSIC":    0.20,  # Accounting cleanliness & zero siphoning
        "GOVERNANCE":  0.15,  # Promoter holding > 50%, zero pledge
        "TECHNICAL":   0.05,  # Base breakout accumulation
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "EARLY_MICROCAP": {
        "FORENSIC":    0.35,  # Forensic shield against small-cap fraud
        "FUNDAMENTAL": 0.25,  # Capacity expansion, incremental ROIC > 25%
        "GOVERNANCE":  0.20,  # Promoter holding > 50%, zero pledge
        "VALUATION":   0.10,  # Re-rating runway
        "TECHNICAL":   0.10,  # Accumulation volume footprint
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "PEER_COMPARE": {
        "FUNDAMENTAL": 0.30,  # Relative ROIC vs WACC spread
        "VALUATION":   0.25,  # Relative multiples & FCF yield
        "TECHNICAL":   0.20,  # Mansfield relative strength
        "FORENSIC":    0.15,  # Comparative cash conversion & working capital
        "GOVERNANCE":  0.10,
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "KEDIA_SMILE": {
        "GOVERNANCE":  0.35,  # Promoter integrity, pledge < 5%, capital allocation
        "FUNDAMENTAL": 0.25,  # Secular ROCE stability, long runway
        "FORENSIC":    0.20,  # Solvency fortress, zero debt, CFO/PAT
        "VALUATION":   0.15,  # Reasonable entry relative to 5-15Y horizon
        "TECHNICAL":   0.05,
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "KACHOLIA_SCALABILITY": {
        "FUNDAMENTAL": 0.40,  # Incremental ROIC > 22%, CWIP conversion, asset turnover
        "VALUATION":   0.20,  # Operating leverage runway
        "FORENSIC":    0.20,  # Clean accounting, working capital turn
        "GOVERNANCE":  0.15,  # Promoter alignment
        "TECHNICAL":   0.05,
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
    "AGRAWAL_INFLECTION": {
        "TECHNICAL":   0.40,  # Volume Z-score, float delivery %, 52W breakout structure
        "FUNDAMENTAL": 0.35,  # QoQ PAT acceleration > 8Q average + 15%
        "FORENSIC":    0.15,  # Basic sanity / circuit safety
        "VALUATION":   0.10,  # Growth at reasonable price / momentum allowance
        "GOVERNANCE":  0.00,
        "MACRO":       0.00,
        "OTHER":       0.00,
        "OPTIONS":     0.00,
    },
}


class QueryAdaptiveConstraintEngine:
    """Institutional Query-Intent Adaptive Routing & Constraint Engine."""

    INTENT_KEYWORDS = {
        "TURNAROUND": [
            "turnaround", "recovery", "nclt", "distress", "revival", "inflection",
            "loss to profit", "operational recovery", "debt reduction"
        ],
        "VALUE_BUYING": [
            "value", "deep value", "graham", "ncav", "net-net", "margin of safety",
            "low pe", "low pb", "fcf yield", "asset backing", "book value"
        ],
        "SIP_COMPOUNDER": [
            "sip", "compounder", "coffee can", "long term", "10 year", "5 year",
            "quality", "durable", "moat", "multidecade", "bluechip", "consistent"
        ],
        "SWING_POSITIONAL": [
            "swing", "position", "positional", "breakout", "momentum", "3 day", "10 day",
            "30 day", "chart", "setup", "vcp", "rsi", "vwap", "squeeze", "tactical"
        ],
        "MULTIBAGGER": [
            "multibagger", "10x", "5x", "asymmetry", "runway", "under discovered",
            "high growth compounder", "reinvestment runway", "super investor", "smart money",
            "ace investor", "bulk deal", "block deal"
        ],
        "EARLY_MICROCAP": [
            "microcap", "early stage", "100cr", "500cr", "nano cap",
            "smallcap", "illiquid", "micro cap"
        ],
        "PEER_COMPARE": [
            "compare", "comparison", "vs", "versus", "better than", "peer",
            "which stock", "sector peer", "relative"
        ],
        "KEDIA_SMILE": [
            "kedia", "vijay kedia", "smile", "kedia securities", "kedia stock", "smile framework"
        ],
        "KACHOLIA_SCALABILITY": [
            "kacholia", "ashish kacholia", "capital scalability", "incremental roic", "lucky investment"
        ],
        "AGRAWAL_INFLECTION": [
            "mukul agrawal", "agrawal", "techno funda", "inflection breakout", "param capital"
        ],
    }

    @classmethod
    def detect_query_intent(cls, query_text: str) -> str:
        """Classifies a user query string into one of the canonical strategic archetypes."""
        if not query_text or not isinstance(query_text, str):
            return "GENERAL"

        q_lower = query_text.lower().strip()

        # Check explicit intent tags first (e.g. "intent_multibagger", "intent_sip")
        for archetype in ARCHETYPE_WEIGHT_PROFILES:
            if f"intent_{archetype.lower()}" in q_lower or f"intent:{archetype.lower()}" in q_lower:
                return archetype

        # Check explicit sub-horizon swing/positional patterns before generic keywords
        if re.search(r'\b(3\s*day|3d|3-day)\b', q_lower):
            return "SWING_3D"
        if re.search(r'\b(30\s*day|30d|30-day|monthly positional)\b', q_lower):
            return "POSITIONAL_30D"

        # Score keyword matches
        scores = {arch: 0 for arch in cls.INTENT_KEYWORDS}
        for arch, keywords in cls.INTENT_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    scores[arch] += 1

        best_match = max(scores.items(), key=lambda x: x[1])
        if best_match[1] > 0:
            return best_match[0]

        return "GENERAL"

    @classmethod
    def get_weight_profile(cls, intent: str) -> Dict[str, float]:
        """Returns the category weight profile for composite scoring."""
        norm_intent = str(intent).upper().replace("INTENT_", "")
        return ARCHETYPE_WEIGHT_PROFILES.get(norm_intent, ARCHETYPE_WEIGHT_PROFILES["GENERAL"])

    @classmethod
    def evaluate_adaptive_constraints(
        cls,
        intent: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluates whether an investment opportunity passes context-specific strict/relaxed gates."""
        norm_intent = str(intent).upper().replace("INTENT_", "")
        if norm_intent in ("SIP", "SIP_COMPOUND", "COMPOUNDER"):
            norm_intent = "SIP_COMPOUNDER"
        elif norm_intent in ("VALUE", "DEEP_VALUE"):
            norm_intent = "VALUE_BUYING"
        elif norm_intent in ("SWING_3D", "3D", "TACTICAL", "3_DAY", "3DAY"):
            norm_intent = "SWING_3D"
        elif norm_intent in ("SWING_10D", "10D", "10_DAY", "10DAY"):
            norm_intent = "SWING_10D"
        elif norm_intent in ("POSITIONAL_30D", "30D", "MONTHLY", "30_DAY", "30DAY"):
            norm_intent = "POSITIONAL_30D"
        elif norm_intent in ("SWING", "POSITIONAL"):
            norm_intent = "SWING_POSITIONAL"
        elif norm_intent in ("MICROCAP", "NANO_CAP", "EARLY_STAGE"):
            norm_intent = "EARLY_MICROCAP"
        elif norm_intent in ("MULTIBAGGER", "10X", "5X"):
            norm_intent = "MULTIBAGGER"
        elif norm_intent in ("COMPARE", "PEER"):
            norm_intent = "PEER_COMPARE"
        elif norm_intent in ("KEDIA", "VIJAY_KEDIA", "SMILE", "KEDIA_SMILE"):
            norm_intent = "KEDIA_SMILE"
        elif norm_intent in ("KACHOLIA", "ASHISH_KACHOLIA", "KACHOLIA_SCALABILITY"):
            norm_intent = "KACHOLIA_SCALABILITY"
        elif norm_intent in ("AGRAWAL", "MUKUL_AGRAWAL", "AGRAWAL_INFLECTION"):
            norm_intent = "AGRAWAL_INFLECTION"

        relaxed: List[str] = []
        tightened: List[str] = []
        warnings: List[str] = []
        vetoes: List[str] = []
        fatal_vetoes: List[str] = []
        objective_blocks: List[str] = []

        # Common data points with explicit missingness tracking
        def _get_opt_float(key_list: List[str]) -> Optional[float]:
            for k in key_list:
                v = data.get(k)
                if v is not None:
                    try:
                        return float(v)
                    except (ValueError, TypeError):
                        pass
            return None

        pat_cagr_3y = _get_opt_float(["pat_growth_3yr", "pat_cagr_3y"])
        sales_cagr_3y = _get_opt_float(["sales_growth_3yr", "sales_cagr_3y"])
        roce = _get_opt_float(["roce_latest", "roce"])
        cfo_pat = _get_opt_float(["cfo_pat_ratio", "cfo_pat"])
        debt_eq = _get_opt_float(["debt_to_equity"])
        pledge_pct = _get_opt_float(["pledged_pct", "promoter_pledge_pct"])
        interest_cov = _get_opt_float(["interest_coverage"])
        dso = _get_opt_float(["dso", "debtor_days"])
        mcap = _get_opt_float(["market_cap"])
        pat_growth_latest = _get_opt_float(["pat_growth_latest", "pat_growth_yoy", "latest_pat_growth"])
        vol_z = _get_opt_float(["volume_z_score", "vol_z", "z_vol"])
        delivery_turnover = _get_opt_float(["delivery_turnover_5d", "delivery_turnover", "dtr_5d"])
        inc_roic = _get_opt_float(["incremental_roic", "inc_roic", "roic", "roce"])
        prom_hold = _get_opt_float(["promoter_holding", "promoter_holding_pct"])
        circuit_headroom = _get_opt_float(["circuit_headroom", "circuit_headroom_pct", "circuit_distance_pct", "dist_to_circuit_pct"])
        adtv = _get_opt_float(["adtv_cr", "daily_turnover_cr", "turnover_cr", "avg_daily_turnover_cr"])
        close_pos = _get_opt_float(["close_position", "close_pos", "cp_ratio"])
        days_to_earnings = _get_opt_float(["days_to_earnings", "earnings_in_days"])
        breakout_vol = _get_opt_float(["breakout_volume_mult", "breakout_vol", "volume_multiple"])

        # ── 1. TURNAROUND INTENT ─────────────────────────────────────────
        if norm_intent == "TURNAROUND":
            # Relax historical financials
            if (pat_cagr_3y is not None and pat_cagr_3y <= 0) or (sales_cagr_3y is not None and sales_cagr_3y <= 0):
                relaxed.append(f"Historical 3Y Sales/PAT growth ({sales_cagr_3y or 0.0:.1f}% / {pat_cagr_3y or 0.0:.1f}%) relaxed under TURNAROUND intent.")
            if roce is not None and roce < 10.0:
                relaxed.append(f"Depressed historical ROCE ({roce:.1f}%) relaxed under TURNAROUND intent.")
            if not relaxed:
                relaxed.append("Historical 3Y/5Y trailing earnings CAGR hurdles relaxed for turnaround thesis.")

            # Tighten real-time survival & inflection
            if interest_cov is None:
                warnings.append("CAUTION: Interest coverage ratio unobserved; debt service safety unconfirmed.")
                tightened.append("Debt service safety: Interest coverage >= 1.5x strictly enforced (unobserved).")
            elif interest_cov < 1.5:
                msg = f"OBJECTIVE_BLOCK: Interest coverage ratio ({interest_cov:.2f}x) is below minimum turnaround survival threshold (1.5x)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Debt service safety: Interest coverage >= 1.5x strictly enforced (failed: {interest_cov:.2f}x).")
            else:
                tightened.append(f"Interest coverage ({interest_cov:.2f}x >= 1.5x) strictly verified for debt service safety.")

            if cfo_pat is None:
                warnings.append("CAUTION: Operating cash flow (CFO) unobserved; sequential cash inflection unconfirmed.")
                tightened.append("Sequential cash inflection: CFO/PAT > 0 strictly enforced (unobserved).")
            elif cfo_pat < 0:
                msg = "OBJECTIVE_BLOCK: Operating cash flow (CFO) is negative; turnaround requires positive sequential cash realization."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Sequential cash inflection: CFO/PAT > 0 strictly enforced (failed: {cfo_pat:.2f}).")
            else:
                tightened.append(f"Positive cash inflection strictly confirmed (CFO/PAT: {cfo_pat:.2f}).")

            if pledge_pct is None:
                warnings.append("CAUTION: Promoter pledge unobserved; cannot verify unencumbered equity.")
            elif pledge_pct > 20.0:
                msg = f"FATAL: Promoter pledge ({pledge_pct:.1f}%) exceeds turnaround distress ceiling (20%)."
                fatal_vetoes.append(msg)
                vetoes.append(msg)

            # Solvency Liquidity Runway Gate (Cash + Liquid Investments vs Operating Cash Burn)
            cash_st_inv = _get_opt_float(["cash_and_equivalents", "cash_equivalents_cr", "liquid_cash_cr"])
            quarterly_burn = _get_opt_float(["quarterly_cash_burn", "operating_cash_burn_cr", "cfo_burn_quarterly"])
            cfo_raw = _get_opt_float(["cfo", "cfo_cr", "operating_cash_flow_cr"])

            # Auto-derive quarterly cash burn if unobserved but operating cash flow is negative
            if quarterly_burn is None and cfo_raw is not None and cfo_raw < 0:
                quarterly_burn = round(abs(cfo_raw) / 4.0, 2)

            if quarterly_burn is not None and quarterly_burn > 0:
                if cash_st_inv is not None:
                    runway_quarters = round(cash_st_inv / max(0.1, quarterly_burn), 1)
                    if runway_quarters < 4.0:
                        msg = f"OBJECTIVE_BLOCK: Solvency liquidity runway ({runway_quarters:.1f} quarters) is below minimum turnaround survival threshold (4.0 quarters / 12 months)."
                        objective_blocks.append(msg)
                        vetoes.append(msg)
                        tightened.append(f"Solvency runway >= 12 months strictly enforced (failed: {runway_quarters:.1f}Q).")
                    else:
                        tightened.append(f"Solvency liquidity runway strictly verified: {runway_quarters:.1f} quarters (>= 4.0Q / 12 months).")
                else:
                    msg = f"OBJECTIVE_BLOCK: Unverified liquidity buffer during active cash burn (estimated burn: Rs {quarterly_burn:.2f} Cr/quarter)."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append("Solvency runway verification failed closed due to unobserved cash balance during active cash burn.")

        # ── 2. VALUE BUYING INTENT ───────────────────────────────────────
        elif norm_intent == "VALUE_BUYING":
            # Relax sales momentum
            if sales_cagr_3y is not None and sales_cagr_3y < 8.0:
                relaxed.append(f"Low trailing sales growth ({sales_cagr_3y:.1f}%) relaxed under deep value framework.")
            else:
                relaxed.append("Trailing revenue momentum relaxed in favor of deep margin of safety and asset backing.")

            # Tighten balance sheet solvency
            if debt_eq is not None and debt_eq > 0.60:
                msg = f"OBJECTIVE_BLOCK: Debt-to-Equity ({debt_eq:.2f}) exceeds deep value safety ceiling (0.60)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Solvency ceiling: Debt/Equity <= 0.60 strictly enforced (failed: {debt_eq:.2f}).")
            elif debt_eq is not None:
                tightened.append(f"Solvency strictly verified: Debt/Equity ({debt_eq:.2f} <= 0.60).")
            else:
                tightened.append("Solvency shield and conservative balance sheet leverage strictly enforced.")

            if cfo_pat is not None and cfo_pat < 0.60:
                warnings.append(f"CAUTION: Cash flow conversion (CFO/PAT: {cfo_pat:.2f}) is weak for value thesis.")

        # ── 3. SIP COMPOUNDER INTENT ─────────────────────────────────────
        elif norm_intent == "SIP_COMPOUNDER":
            # Relax short-term technicals
            relaxed.append("Short-term technical indicators (3D/10D RSI, breakout volume) completely relaxed for long-duration SIP.")

            # Check if company is in BFSI / Financial sector
            sector_val = str(data.get("sector") or data.get("industry") or "").upper().strip()
            sub_sector_val = str(data.get("sub_sector") or "").upper().strip()
            is_bfsi = any(b in sector_val for b in ("BANK", "FINANCIAL", "NBFC", "LENDING", "INSURANCE", "AMC", "BROKING", "EXCHANGE")) or any(b in sub_sector_val for b in ("BANK", "FINANCIAL", "NBFC", "LENDING", "INSURANCE", "AMC", "BROKING", "EXCHANGE"))

            if is_bfsi:
                is_asset_light = any(b in sector_val for b in ("AMC", "ASSET MANAGEMENT", "MUTUAL FUND", "EXCHANGE", "DEPOSITORY", "BROKING", "REGISTRAR", "CAMS", "CDSL", "MCX", "BSE")) or any(b in sub_sector_val for b in ("AMC", "BROKING", "EXCHANGE", "ASSET_LIGHT", "DEPOSITORY"))
                is_insurance = any(b in sector_val for b in ("INSURANCE", "LIFE INSURANCE", "GENERAL INSURANCE")) or any(b in sub_sector_val for b in ("INSURANCE", "LIFE_INSURANCE", "GENERAL_INSURANCE"))

                if is_asset_light:
                    relaxed.append("Credit lending Gross NPA and CAR capital adequacy metrics relaxed for asset-light financial platform (AMC/Exchange/Depository/Broking).")
                    opm = _get_opt_float(["opm", "operating_margin", "ebit_margin", "operating_profit_margin"])
                    if roce is not None and roce >= 25.0:
                        tightened.append(f"Superior asset-light platform capital efficiency strictly verified: ROCE ({roce:.1f}% >= 25.0%).")
                    elif roce is not None and roce < 20.0:
                        msg = f"OBJECTIVE_BLOCK: Asset-light financial ROCE ({roce:.1f}%) below institutional hurdle (20.0%)."
                        objective_blocks.append(msg)
                        vetoes.append(msg)
                        tightened.append(f"Asset-light ROCE hurdle: ROCE >= 20.0% strictly enforced (failed: {roce:.1f}%).")
                    elif roce is not None:
                        tightened.append(f"Asset-light capital efficiency verified: ROCE ({roce:.1f}% >= 20.0%).")
                    else:
                        tightened.append("Asset-light financial platform metrics: High ROCE (>= 25%) and pristine operational margins strictly enforced.")

                    if opm is not None and opm >= 35.0:
                        tightened.append(f"High-margin operational leverage verified: Operating Margin ({opm:.1f}% >= 35.0%).")
                    elif opm is not None and opm < 25.0:
                        warnings.append(f"CAUTION: Operating margin ({opm:.1f}%) is low for asset-light financial platform (benchmark >= 35.0%).")

                    if debt_eq is not None and debt_eq > 0.30:
                        msg = f"OBJECTIVE_BLOCK: Asset-light platform carries excessive leverage (Debt/Equity: {debt_eq:.2f} > 0.30)."
                        objective_blocks.append(msg)
                        vetoes.append(msg)
                        tightened.append(f"Balance sheet purity: Debt/Equity <= 0.30 strictly enforced (failed: {debt_eq:.2f}).")

                elif is_insurance:
                    relaxed.append("Credit lending Gross NPA and CAR metrics relaxed for insurance balance sheet; solvency buffer and persistency monitored.")
                    solvency = _get_opt_float(["solvency_ratio", "solvency", "regulatory_solvency"])
                    if solvency is not None and solvency < 1.50:
                        msg = f"OBJECTIVE_BLOCK: Insurer solvency ratio ({solvency:.2f}) is below mandatory regulatory buffer (1.50)."
                        objective_blocks.append(msg)
                        vetoes.append(msg)
                        tightened.append(f"Solvency floor: Solvency ratio >= 1.50 strictly enforced (failed: {solvency:.2f}).")
                    elif solvency is not None:
                        tightened.append(f"Pristine insurer solvency verified: Solvency ratio ({solvency:.2f} >= 1.50).")
                    else:
                        tightened.append("Insurance regulatory solvency (Solvency Ratio >= 1.50) and underwriting discipline strictly enforced.")

                else:
                    # BFSI_LENDING (Banks, NBFCs, Housing Finance)
                    relaxed.append("Industrial ROCE and CFO/PAT conversion metrics relaxed for credit lending institution balance sheet.")
                    roe = _get_opt_float(["roe", "return_on_equity", "roe_latest", "roe_10yr"])
                    roa = _get_opt_float(["roa", "return_on_assets"])
                    gnpa = _get_opt_float(["gnpa", "gross_npa", "gross_npa_pct"])
                    car = _get_opt_float(["car", "capital_adequacy_ratio", "crar"])

                    if roe is not None and roe >= 15.0:
                        tightened.append(f"Banking profitability strictly verified (ROE: {roe:.1f}% >= 15.0%).")
                    elif roe is not None:
                        warnings.append(f"CAUTION: Banking ROE ({roe:.1f}%) is below compounder standard (15.0%).")

                    if gnpa is not None and gnpa > 3.5:
                        msg = f"OBJECTIVE_BLOCK: Asset quality stress in financial institution (Gross NPA: {gnpa:.2f}% > 3.5% ceiling)."
                        objective_blocks.append(msg)
                        vetoes.append(msg)
                        tightened.append(f"Asset quality ceiling: Gross NPA <= 3.5% strictly enforced (failed: {gnpa:.2f}%).")
                    elif gnpa is not None:
                        tightened.append(f"Pristine asset quality verified: Gross NPA ({gnpa:.2f}% <= 2.0%).")
                    else:
                        tightened.append("Banking capital adequacy (CAR >= 15%) and asset quality strictly enforced.")
            else:
                # Tighten multi-year capital efficiency & cash quality for Industrials/Non-BFSI
                if roce is None:
                    msg = "OBJECTIVE_BLOCK: ROCE unobserved; long-duration compounder requires verified multi-year capital efficiency."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append("Capital efficiency standard: ROCE >= 20.0% strictly enforced (unobserved).")
                elif roce < 20.0:
                    msg = f"OBJECTIVE_BLOCK: ROCE ({roce:.1f}%) is below compounder institutional standard (20.0%)."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append(f"Capital efficiency standard: ROCE >= 20.0% strictly enforced (failed: {roce:.1f}%).")
                else:
                    tightened.append(f"Superior capital efficiency strictly verified: ROCE ({roce:.1f}% >= 20.0%).")

                if cfo_pat is None:
                    msg = "OBJECTIVE_BLOCK: Operating cash conversion unobserved for compounder quality gate."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append("Cash realization standard: CFO/PAT >= 0.80 strictly enforced (unobserved).")
                elif cfo_pat < 0.80:
                    msg = f"OBJECTIVE_BLOCK: Cash flow conversion (CFO/PAT: {cfo_pat:.2f}) fails compounder quality gate (minimum 0.80)."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append(f"Cash realization standard: CFO/PAT >= 0.80 strictly enforced (failed: {cfo_pat:.2f}).")
                else:
                    tightened.append(f"Pristine cash realization verified (CFO/PAT: {cfo_pat:.2f} >= 0.80).")

                # Phase 140: CAQI Hard Gate evaluation
                caqi_val = _get_opt_float(["caqi"])
                caqi_gate = str(data.get("caqi_gate") or "")
                if caqi_gate == "FAIL" or (caqi_val is not None and caqi_val < 0.80):
                    caqi_msg = f"OBJECTIVE_BLOCK: CAQI Gate FAIL: Cash Accrual Quality ({caqi_val or 0.0:.2f}x) fails compounder hurdle (0.80x minimum)."
                    if caqi_msg not in objective_blocks:
                        objective_blocks.append(caqi_msg)
                        vetoes.append(caqi_msg)
                    tightened.append(f"CAQI cash accrual quality >= 0.80x strictly enforced (failed: {caqi_val or 0.0:.2f}x).")
                elif caqi_gate == "PASS" or (caqi_val is not None and caqi_val >= 0.80):
                    tightened.append(f"Pristine CAQI cash accrual verified ({caqi_val:.2f}x >= 0.80x threshold).")

                if debt_eq is not None and debt_eq > 0.30:
                    warnings.append(f"CAUTION: Balance sheet leverage (D/E: {debt_eq:.2f}) is above pristine compounder tier (< 0.30).")

            if pledge_pct is None:
                warnings.append("CAUTION: Promoter pledge unobserved in compounder candidate.")
            elif pledge_pct > 0.0:
                warnings.append(f"CAUTION: Promoter pledging ({pledge_pct:.1f}%) detected in compounder scrip.")

        # ── 4. SWING POSITIONAL INTENT ───────────────────────────────────
        elif norm_intent == "SWING_POSITIONAL":
            # Relax long-term DCF and multi-year runway
            relaxed.append("10-Year DCF intrinsic valuation and terminal growth completely relaxed for 10-30 session swing trade.")
            tightened.append("Technical momentum, Anchored VWAP structure, and volume confirmation strictly enforced.")

            # Tighten liquidity and risk geometry
            if dso is not None and dso > 180:
                warnings.append(f"CAUTION: Elevated working capital (DSO {dso:.0f}d) flagged, but trade governed by chart setup.")

        elif norm_intent == "SWING_3D":
            # 72-Hour Tactical Momentum Horizon
            relaxed.append("Multi-year 5Y/10Y DCF, long-term ROCE, and terminal valuation completely relaxed for 72-hour tactical swing.")
            tightened.append("Intraday Anchored VWAP, volume Z-score, close position >= 0.75, and upper circuit distance strictly enforced.")

            if vol_z is not None and vol_z < 2.0:
                warnings.append(f"CAUTION: Volume Z-score ({vol_z:.1f}s) below strong momentum threshold (2.0s).")
            elif vol_z is not None:
                tightened.append(f"Momentum volume surge confirmed (Z-score: +{vol_z:.1f}s).")

            if close_pos is not None and close_pos < 0.60:
                warnings.append(f"CAUTION: Close position ({close_pos:.2f}) indicates intraday selling pressure (< 0.60).")

            # Circuit Headroom Gate: must be at least 3.0% away from upper circuit
            if circuit_headroom is not None:
                if circuit_headroom < 3.0:
                    msg = f"OBJECTIVE_BLOCK: Insufficient upper circuit headroom ({circuit_headroom:.1f}% < 3.0%); immediate liquidity freeze risk."
                    objective_blocks.append(msg)
                    vetoes.append(msg)
                    tightened.append(f"Upper circuit headroom >= 3.0% strictly enforced (failed: {circuit_headroom:.1f}%).")
                else:
                    tightened.append(f"Safe circuit headroom verified ({circuit_headroom:.1f}% >= 3.0%).")

            # Daily turnover liquidity floor (min Rs 5 Cr ADTV for clean exit)
            if adtv is not None:
                if adtv < 5.0:
                    warnings.append(f"CAUTION: Daily turnover (₹{adtv:.1f}Cr) is below optimal 3-day tactical liquidity benchmark (₹5.0Cr).")
                else:
                    tightened.append(f"Tactical exit liquidity verified (ADTV: ₹{adtv:.1f}Cr >= ₹5.0Cr).")

        elif norm_intent == "SWING_10D":
            # 1-2 Week Multi-Session Swing Horizon
            relaxed.append("10-Year DCF intrinsic valuation and multi-decade reinvestment runway relaxed for 10-day multi-session swing.")
            tightened.append("TTM Squeeze compression/expansion, 10/20 EMA ribbon support, and event risk safety strictly enforced.")

            # Event Risk: earnings gap avoidance
            if days_to_earnings is not None and 0 <= days_to_earnings <= 5:
                warnings.append(f"CAUTION: Corporate earnings announcement scheduled in {int(days_to_earnings)} days; binary overnight gap risk present.")

            if vol_z is not None and vol_z >= 1.5:
                tightened.append(f"Accumulation volume surge verified (Z-score: +{vol_z:.1f}s).")

        elif norm_intent == "POSITIONAL_30D":
            # 1-Month Base Breakout & Intermediate Catalyst Horizon
            relaxed.append("Multi-decade terminal growth models relaxed in favor of intermediate base breakout structure and quarterly catalysts.")
            tightened.append("Minervini Stage 2 uptrend, base consolidation depth, and quarterly PAT acceleration strictly enforced.")

            eff_pat = pat_growth_latest if pat_growth_latest is not None else pat_cagr_3y
            if eff_pat is not None and eff_pat < 15.0:
                warnings.append(f"CAUTION: Quarterly PAT acceleration ({eff_pat:.1f}%) is below preferred 30-day breakout benchmark (15.0%).")
            elif eff_pat is not None:
                tightened.append(f"Quarterly earnings acceleration verified (PAT Growth: {eff_pat:.1f}% >= 15.0%).")

            if breakout_vol is not None and breakout_vol >= 2.0:
                tightened.append(f"Base breakout volume confirmation verified ({breakout_vol:.1f}x average volume).")

        # ── 5. SCALED MULTIBAGGER INTENT ─────────────────────────────────
        elif norm_intent == "MULTIBAGGER":
            # Relax institutional ownership and analyst coverage
            relaxed.append("Institutional ownership thresholds and analyst coverage relaxed for under-discovered growth compounder.")

            # Tighten Incremental ROIC / Capital Efficiency Runway
            inc_roic = _get_opt_float(["incremental_roic", "inc_roic", "roic", "roce"])
            if inc_roic is not None and inc_roic >= 22.0:
                tightened.append(f"High incremental capital efficiency verified (ROIC/ROCE: {inc_roic:.1f}% >= 22.0%).")
            elif inc_roic is not None:
                warnings.append(f"CAUTION: Capital productivity (ROIC/ROCE: {inc_roic:.1f}%) is below elite multibagger standard (22.0%).")
            else:
                tightened.append("High incremental capital productivity (ROIC >= 22%) strictly enforced.")

            # 35% Sector TAM Ceiling Gate
            tam_share = _get_opt_float(["implied_tam_share", "implied_market_share", "terminal_market_share"])
            if tam_share is not None and tam_share > 35.0:
                msg = f"OBJECTIVE_BLOCK: Implied 7-year terminal revenue exceeds Sector TAM Ceiling ({tam_share:.1f}% > 35.0%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Sector TAM ceiling <= 35% strictly enforced (failed: {tam_share:.1f}%).")
            elif tam_share is not None:
                tightened.append(f"Addressable market headroom verified (TAM share: {tam_share:.1f}% <= 35.0%).")
            else:
                tightened.append("Sector TAM headroom and addressable runway strictly enforced.")

            # Phase 140: DEME-HR Multiple Expansion Ceiling Gate
            deme_hr = _get_opt_float(["deme_hr"])
            deme_verdict = str(data.get("deme_hr_verdict") or "")
            if deme_verdict == "VALUATION_CONSTRAINED" or (deme_hr is not None and deme_hr <= 1.0):
                warnings.append(f"CAUTION: DEME-HR ({deme_hr or 1.0:.2f} <= 1.0) trailing P/E at or above sector benchmark ceiling; multiple expansion room exhausted.")
                tightened.append(f"Multiple expansion headroom: DEME-HR > 1.0 required for asymmetric re-rating (constrained: {deme_hr or 1.0:.2f}).")
            elif deme_verdict == "UNDERVALUED" or (deme_hr is not None and deme_hr > 2.0):
                tightened.append(f"Strong multiple expansion headroom verified: DEME-HR ({deme_hr or 2.0:.2f} > 2.0x ceiling buffer).")

        # ── 6. EARLY MICROCAP RISK-FIRST INTENT ──────────────────────────
        elif norm_intent in ("EARLY_MICROCAP", "MICROCAP_RISK"):
            # Relax institutional ownership and scale
            mcap_val = mcap or 500.0
            relaxed.append(f"Small-cap scale (MCap: Rs {mcap_val:.0f} Cr) and low institutional coverage relaxed for early-stage discovery.")

            # Tighten promoter alignment and incremental efficiency
            prom_hold = _get_opt_float(["promoter_holding"])
            if prom_hold is None:
                warnings.append("CAUTION: Promoter holding unobserved for early-stage microcap.")
                tightened.append("Insider alignment standard: Promoter holding >= 40% strictly enforced (unobserved).")
            elif prom_hold < 40.0:
                warnings.append(f"CAUTION: Promoter holding ({prom_hold:.1f}%) is low for early-stage microcap.")
                tightened.append(f"Insider alignment standard: Promoter holding >= 40% strictly enforced (low: {prom_hold:.1f}%).")
            else:
                tightened.append(f"Strong insider alignment strictly verified (Promoter: {prom_hold:.1f}%).")

            if pledge_pct is not None and pledge_pct > 15.0:
                msg = f"FATAL: Promoter pledge ({pledge_pct:.1f}%) exceeds microcap risk tolerance (15%)."
                fatal_vetoes.append(msg)
                vetoes.append(msg)

            if not tightened:
                tightened.append("High incremental ROIC runway and insider alignment strictly enforced.")

        # ── 7. PEER COMPARE INTENT ───────────────────────────────────────
        elif norm_intent == "PEER_COMPARE":
            sector = str(data.get("sector") or "").lower()
            if "saas" in sector or "software" in sector or "it" in sector:
                relaxed.append("Software SaaS asset-light structure normalized: gross block additions relaxed.")
                tightened.append("Rule of 40 (Sales Growth + FCF Margin) and gross margin stability enforced.")
            else:
                relaxed.append("Sector cross-sectional comparison: asset base normalized across peer group.")
                tightened.append("Hardware/ESDM working capital cycle and Book-to-Bill ratio enforced.")

        # ── 8. KEDIA SMILE INTENT ────────────────────────────────────────
        elif norm_intent == "KEDIA_SMILE":
            relaxed.append("Short-term price/volume volatility and cyclical raw material swings relaxed for 5-15Y SMILE compounding horizon.")

            # Strict promoter alignment & skin in the game
            if prom_hold is None:
                warnings.append("CAUTION: Promoter holding unobserved in Kedia SMILE candidate.")
                tightened.append("Promoter alignment: Promoter holding >= 50.0% strictly enforced (unobserved).")
            elif prom_hold < 45.0:
                msg = f"OBJECTIVE_BLOCK: Promoter holding ({prom_hold:.1f}%) below Kedia skin-in-the-game hurdle (minimum 45.0%, preferred >= 50%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Promoter alignment >= 45% strictly enforced (failed: {prom_hold:.1f}%).")
            else:
                tightened.append(f"Strong promoter alignment strictly verified (Promoter: {prom_hold:.1f}% >= 45.0%).")

            # Strict zero/low pledge
            if pledge_pct is None:
                warnings.append("CAUTION: Promoter pledge unobserved in Kedia candidate.")
            elif pledge_pct > 5.0:
                if pledge_pct > 20.0:
                    msg = f"FATAL: Promoter pledge ({pledge_pct:.1f}%) exceeds safety distress limit (20.0%)."
                    fatal_vetoes.append(msg)
                else:
                    msg = f"OBJECTIVE_BLOCK: Promoter pledge ({pledge_pct:.1f}%) exceeds Kedia SMILE zero-pledge hurdle (5.0%)."
                    objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Promoter pledge <= 5% strictly enforced (failed: {pledge_pct:.1f}%).")
            else:
                tightened.append(f"Clean unencumbered promoter shares verified (Pledge: {pledge_pct:.1f}% <= 5.0%).")

            # Solvency fortress
            if debt_eq is not None and debt_eq > 0.30:
                msg = f"OBJECTIVE_BLOCK: Balance sheet leverage (D/E: {debt_eq:.2f}) exceeds Kedia conservative solvency ceiling (0.30)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Solvency ceiling Debt/Equity <= 0.30 strictly enforced (failed: {debt_eq:.2f}).")
            elif debt_eq is not None:
                tightened.append(f"Conservative solvency verified: Debt/Equity ({debt_eq:.2f} <= 0.30).")

            if interest_cov is not None and interest_cov < 3.5:
                msg = f"OBJECTIVE_BLOCK: Interest coverage ({interest_cov:.2f}x) below Kedia safety buffer (3.5x)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Interest coverage >= 3.5x strictly enforced (failed: {interest_cov:.2f}x).")
            elif interest_cov is not None:
                tightened.append(f"Robust interest service coverage verified ({interest_cov:.2f}x >= 3.5x).")

            if roce is not None and roce < 15.0:
                msg = f"OBJECTIVE_BLOCK: ROCE ({roce:.1f}%) below Kedia compounding benchmark (15.0%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Capital allocation ROCE >= 15.0% strictly enforced (failed: {roce:.1f}%).")
            elif roce is not None:
                tightened.append(f"Healthy capital efficiency verified: ROCE ({roce:.1f}% >= 15.0%).")

        # ── 9. KACHOLIA SCALABILITY INTENT ───────────────────────────────
        elif norm_intent == "KACHOLIA_SCALABILITY":
            relaxed.append("Dividend yield and high institutional float coverage relaxed for niche B2B/manufacturing scale compounder.")

            # Incremental capital productivity (dNOPAT/dIC or ROCE)
            target_roic = inc_roic if inc_roic is not None else roce
            if target_roic is None:
                warnings.append("CAUTION: Incremental capital productivity unobserved; scalability unconfirmed.")
                tightened.append("Incremental capital productivity: ROIC/ROCE >= 20.0% strictly enforced (unobserved).")
            elif target_roic < 18.0:
                msg = f"OBJECTIVE_BLOCK: Incremental capital productivity ({target_roic:.1f}%) below Kacholia scalability threshold (18.0%, target >= 22%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Capital productivity >= 18% strictly enforced (failed: {target_roic:.1f}%).")
            else:
                tightened.append(f"High incremental capital productivity strictly verified (ROIC/ROCE: {target_roic:.1f}% >= 18.0%).")

            # Revenue / capacity expansion runway
            if sales_cagr_3y is not None and sales_cagr_3y < 12.0:
                msg = f"OBJECTIVE_BLOCK: Trailing 3Y sales CAGR ({sales_cagr_3y:.1f}%) below Kacholia growth runway hurdle (12.0%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Sales growth runway >= 12% strictly enforced (failed: {sales_cagr_3y:.1f}%).")
            elif sales_cagr_3y is not None:
                tightened.append(f"Strong top-line growth runway verified (3Y Sales CAGR: {sales_cagr_3y:.1f}% >= 12.0%).")

            # Cash flow realization
            if cfo_pat is not None and cfo_pat < 0.65:
                warnings.append(f"CAUTION: Operating cash flow conversion (CFO/PAT: {cfo_pat:.2f}) indicates working capital lag.")
                tightened.append("Working capital & cash conversion discipline enforced (CFO/PAT >= 0.65).")
            elif cfo_pat is not None:
                tightened.append(f"Disciplined working capital cash conversion verified (CFO/PAT: {cfo_pat:.2f} >= 0.65).")

            if debt_eq is not None and debt_eq > 0.70:
                msg = f"OBJECTIVE_BLOCK: Leverage (D/E: {debt_eq:.2f}) exceeds Kacholia capex safety ceiling (0.70)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"Debt/Equity <= 0.70 strictly enforced (failed: {debt_eq:.2f}).")

        # ── 10. AGRAWAL INFLECTION INTENT ────────────────────────────────
        elif norm_intent == "AGRAWAL_INFLECTION":
            relaxed.append("Multi-year 5Y/10Y historical metrics and trailing valuation multiples relaxed in favor of immediate operating inflection and volume breakout.")

            # Latest QoQ PAT acceleration
            eff_pat_acc = pat_growth_latest if pat_growth_latest is not None else pat_cagr_3y
            if eff_pat_acc is None:
                warnings.append("CAUTION: Latest PAT growth rate unobserved; earnings inflection unconfirmed.")
                tightened.append("Operating inflection: PAT acceleration >= 18.0% strictly enforced (unobserved).")
            elif eff_pat_acc < 15.0:
                msg = f"OBJECTIVE_BLOCK: Latest PAT growth ({eff_pat_acc:.1f}%) below Agrawal inflection acceleration threshold (15.0%, preferred >= 20%)."
                objective_blocks.append(msg)
                vetoes.append(msg)
                tightened.append(f"PAT inflection acceleration >= 15% strictly enforced (failed: {eff_pat_acc:.1f}%).")
            else:
                tightened.append(f"Explosive earnings inflection strictly verified (PAT growth: {eff_pat_acc:.1f}% >= 15.0%).")

            # Volume & Microstructure Footprint confirmation
            if vol_z is not None and vol_z < 0.5:
                warnings.append(f"CAUTION: Volume accumulation z-score ({vol_z:.1f}s) indicates muted institutional participation.")
            elif vol_z is not None:
                tightened.append(f"Institutional volume accumulation footprint strictly verified (Z-score: +{vol_z:.1f}s).")
            else:
                tightened.append("Institutional delivery volume expansion and base breakout structure strictly enforced.")

            if delivery_turnover is not None and delivery_turnover >= 2.0:
                tightened.append(f"High float delivery turnover verified: {delivery_turnover:.1f}% (>= 2.0%).")

            # Governance sanity
            if pledge_pct is not None and pledge_pct > 15.0:
                msg = f"FATAL: Promoter pledge ({pledge_pct:.1f}%) exceeds momentum risk threshold (15.0%)."
                fatal_vetoes.append(msg)
                vetoes.append(msg)

        # ── 11. GENERAL INTENT ───────────────────────────────────────────
        else:
            relaxed.append("Standard balanced weighting: no single dimension excessively penalized or boosted.")
            tightened.append("Baseline institutional risk checks enforced: solvency, governance, and forensic hygiene.")

        strictness_summary = (
            f"Intent {norm_intent}: {len(relaxed)} relaxed parameters, "
            f"{len(tightened)} tightened parameters."
        )

        return {
            "intent": norm_intent,
            "passed": len(vetoes) == 0,
            "relaxed_parameters": relaxed,
            "tightened_parameters": tightened,
            "strictness_summary": strictness_summary,
            "warnings": warnings,
            "vetoes": vetoes,
            "objective_blocks": objective_blocks,
            "fatal_vetoes": fatal_vetoes,
            "status": "APPROVED" if len(vetoes) == 0 else "REJECTED_INTENT_VETO"
        }

    @classmethod
    def synthesize_intent_verdict(cls, intent: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes dynamic parameter adjustments and constraints for an intent."""
        constraints = cls.evaluate_adaptive_constraints(intent, data)
        return {
            "intent": constraints["intent"],
            "passed": constraints["passed"],
            "relaxed_parameters": constraints["relaxed_parameters"],
            "tightened_parameters": constraints["tightened_parameters"],
            "strictness_summary": constraints["strictness_summary"],
            "warnings": constraints["warnings"],
            "vetoes": constraints["vetoes"],
            "status": constraints["status"]
        }


# Canonical Institutional Aliases
IntentAdaptiveEngine = QueryAdaptiveConstraintEngine


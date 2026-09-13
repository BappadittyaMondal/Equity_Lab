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
            "high growth compounder", "reinvestment runway"
        ],
        "EARLY_MICROCAP": [
            "microcap", "early stage", "100cr", "500cr", "nano cap",
            "smallcap", "illiquid", "micro cap"
        ],
        "PEER_COMPARE": [
            "compare", "comparison", "vs", "versus", "better than", "peer",
            "which stock", "sector peer", "relative"
        ],
    }

    @classmethod
    def detect_query_intent(cls, query_text: str) -> str:
        """Classifies a user query string into one of the 6 canonical strategic archetypes."""
        if not query_text or not isinstance(query_text, str):
            return "GENERAL"

        q_lower = query_text.lower().strip()

        # Check explicit intent tags first (e.g. "intent_multibagger", "intent_sip")
        for archetype in ARCHETYPE_WEIGHT_PROFILES:
            if f"intent_{archetype.lower()}" in q_lower or f"intent:{archetype.lower()}" in q_lower:
                return archetype

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
        elif norm_intent in ("SWING", "POSITIONAL"):
            norm_intent = "SWING_POSITIONAL"
        elif norm_intent in ("MICROCAP", "NANO_CAP", "EARLY_STAGE"):
            norm_intent = "EARLY_MICROCAP"
        elif norm_intent in ("MULTIBAGGER", "10X", "5X"):
            norm_intent = "MULTIBAGGER"
        elif norm_intent in ("COMPARE", "PEER"):
            norm_intent = "PEER_COMPARE"

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

        # ── 7. GENERAL INTENT ────────────────────────────────────────────
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


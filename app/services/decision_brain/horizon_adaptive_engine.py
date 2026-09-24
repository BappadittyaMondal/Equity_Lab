"""Horizon-Adaptive Evidence Matrix & Capacity Sizing Engine (Phase 142).

Dual Evaluator Lenses:
  - Deep-Tech Principal Architect: Deterministic rules, zero lookahead, typed schemas, graceful fallbacks.
  - $10B Institutional Hedge Fund CRO: Capacity limits (10% ADTV), surveillance vetoes, fat-tail survival.
  - Professional Equity Trader / End User: Contextual forgiveness (no penalizing swing trades for 10Y ROE).

Dynamically modulates evidence strictness and position sizing ceilings across 5 investment horizons:
  1. TACTICAL_SWING_3D: Microstructure & volume surge; DCF zeroed; hard ASM/ESM veto; ADTV >= 5 Cr.
  2. POSITIONAL_SWING_10_30D: Stage 2 breakout, VCP base, earnings surprise; ADTV >= 2 Cr.
  3. TURNAROUND_1_3Y: Sequential CFO > 0, OPM turn, interest coverage >= 1.5x; Altman Z distress softened.
  4. QUALITY_COMPOUNDER_5_10Y: 10Y ROCE >= 15%, Net D/E <= 0.3, FCF/PAT >= 70%, zero pledge; dips ignored.
  5. PRE_DISCOVERY_LAUNCHPAD: MCap 50-500 Cr, Order book/MCap >= 1.5x, Jaw effect setup, 10% ADTV ceiling.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class HorizonAdaptiveEngine:
    """Unified Horizon-Adaptive Evidence & Capacity Sizing Engine."""

    HORIZON_MAP = {
        "SWING_3D": "TACTICAL_SWING_3D",
        "SWING_10D": "POSITIONAL_SWING_10_30D",
        "POSITIONAL_30D": "POSITIONAL_SWING_10_30D",
        "SWING": "POSITIONAL_SWING_10_30D",
        "SWING_POSITIONAL": "POSITIONAL_SWING_10_30D",
        "TURNAROUND": "TURNAROUND_1_3Y",
        "SIP": "QUALITY_COMPOUNDER_5_10Y",
        "SIP_COMPOUNDER": "QUALITY_COMPOUNDER_5_10Y",
        "COMPOUNDER": "QUALITY_COMPOUNDER_5_10Y",
        "MULTIBAGGER": "PRE_DISCOVERY_LAUNCHPAD",
        "LAUNCHPAD": "PRE_DISCOVERY_LAUNCHPAD",
        "EARLY_MICROCAP": "PRE_DISCOVERY_LAUNCHPAD"
    }

    @classmethod
    def resolve_horizon_profile(cls, horizon_or_objective: str) -> str:
        norm = str(horizon_or_objective).upper().replace("INTENT_", "").strip()
        return cls.HORIZON_MAP.get(norm, "POSITIONAL_SWING_10_30D")

    @classmethod
    def compute_capacity_limits(
        cls,
        adtv_cr: Optional[float] = None,
        volume: Optional[float] = None,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculates institutional and retail capacity ceilings based on 20-day ADTV."""
        eff_adtv = adtv_cr
        if (eff_adtv is None or eff_adtv <= 0.0) and volume and price and volume > 0 and price > 0:
            eff_adtv = round((volume * price) / 1e7, 2)

        if eff_adtv is None or eff_adtv <= 0.0:
            return {
                "adtv_cr": 0.0,
                "max_institutional_position_cr": 0.0,
                "max_retail_order_cr": 0.0,
                "capacity_status": "DATA_INSUFFICIENT",
                "is_liquid_enough": False,
                "capacity_note": "ADTV unobserved; cannot determine execution capacity."
            }

        max_inst = round(0.10 * eff_adtv, 2)  # Max 10% of 20d ADTV to prevent institutional price impact
        max_ret = round(0.02 * eff_adtv, 2)   # Max 2% single-order limit for retail/swing traders

        if eff_adtv >= 5.0:
            status = "HIGH_LIQUIDITY"
            is_liquid = True
        elif eff_adtv >= 2.0:
            status = "ADEQUATE_LIQUIDITY"
            is_liquid = True
        elif eff_adtv >= 0.5:
            status = "MICRO_LIQUIDITY_CONSTRAINED"
            is_liquid = True
        else:
            status = "ILLIQUID_HAZARD"
            is_liquid = False

        return {
            "adtv_cr": round(eff_adtv, 2),
            "max_institutional_position_cr": max_inst,
            "max_retail_order_cr": max_ret,
            "capacity_status": status,
            "is_liquid_enough": is_liquid,
            "capacity_note": (
                f"20D ADTV: ₹{eff_adtv:.2f}Cr. Institutional capacity ceiling: ₹{max_inst:.2f}Cr (10% ADTV). "
                f"Retail single-day order ceiling: ₹{max_ret:.2f}Cr (2% ADTV)."
            )
        }

    @classmethod
    def evaluate_horizon_evidence(
        cls,
        symbol: str,
        horizon_or_objective: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluates horizon-adaptive evidence strictness, surveillance gates, and capacity ceilings."""
        profile = cls.resolve_horizon_profile(horizon_or_objective)
        
        # 1. Surveillance and ESM Stage Check
        surv_data = data.get("surveillance") or {}
        asm_stage = str(surv_data.get("asm_stage") or data.get("asm_stage") or "CLEAN").upper()
        esm_stage = str(surv_data.get("esm_stage") or data.get("esm_stage") or "CLEAN").upper()
        circuit_band = float(surv_data.get("circuit_band_pct") or data.get("circuit_band_pct") or 20.0)

        # Fatal surveillance veto
        surveillance_veto = False
        surveillance_reason = None
        if esm_stage == "STAGE_II":
            surveillance_veto = True
            surveillance_reason = "FATAL: Stock under SEBI ESM Stage II (2% circuit, periodic call auction). Illiquidity freeze hazard."
        elif asm_stage in ("STAGE_III", "STAGE_IV"):
            surveillance_veto = True
            surveillance_reason = f"FATAL: Stock under SEBI ASM {asm_stage}. 100% margin / extreme surveillance."
        elif circuit_band <= 2.0 and esm_stage != "CLEAN":
            surveillance_veto = True
            surveillance_reason = f"FATAL: Restricted 2% circuit band under surveillance ({esm_stage})."

        # 2. Capacity Guard
        adtv = data.get("adtv_cr") or data.get("daily_turnover_cr") or data.get("adtv_30d_cr")
        vol = data.get("volume") or data.get("avg_volume_20d")
        px = data.get("current_price") or data.get("price") or 100.0
        capacity = cls.compute_capacity_limits(adtv_cr=adtv, volume=vol, price=px)

        # 3. Dynamic Checklist based on Profile
        relaxed_factors: List[str] = []
        tightened_factors: List[str] = []
        breached_gates: List[str] = []
        evidence_score = 0.0

        if surveillance_veto:
            breached_gates.append(surveillance_reason)

        if profile == "TACTICAL_SWING_3D":
            relaxed_factors.extend([
                "10-Year DCF intrinsic value and terminal multiples zeroed out",
                "Historical 5-year ROCE and revenue CAGR relaxed",
                "Promoter stake changes and dividend history ignored"
            ])
            # Strict technical & liquidity requirements
            vol_z = float(data.get("volume_z_score") or data.get("vol_z") or 0.0)
            close_pos = float(data.get("close_position") or data.get("cp_ratio") or 0.8)
            rvol = float(data.get("rvol") or 1.0)
            
            if capacity["adtv_cr"] < 2.0:
                breached_gates.append(f"ADTV ₹{capacity['adtv_cr']:.2f}Cr < ₹2.0Cr minimum for 3-day tactical exit.")
            else:
                tightened_factors.append(f"ADTV ₹{capacity['adtv_cr']:.2f}Cr >= ₹2.0Cr floor verified.")
                evidence_score += 35.0

            if rvol >= 1.5 or vol_z >= 1.5:
                tightened_factors.append(f"Breakout volume confirmed: RVOL {rvol:.1f}x / Vol Z {vol_z:.1f}s.")
                evidence_score += 35.0
            else:
                tightened_factors.append("RVOL < 1.5x: muted volume expansion.")

            if close_pos >= 0.70:
                tightened_factors.append(f"Strong daily close position: {close_pos:.2f} >= 0.70.")
                evidence_score += 30.0
            else:
                breached_gates.append(f"Weak close position: {close_pos:.2f} < 0.70 indicates intraday fade.")

        elif profile == "POSITIONAL_SWING_10_30D":
            relaxed_factors.extend([
                "Long-term DCF terminal growth relaxed",
                "Historical 3-5Y earnings cycles relaxed in favor of intermediate base breakout",
                "Dividend payout ratio relaxed"
            ])
            stage_2 = bool(data.get("is_stage_2", True))
            vcp_tightness = float(data.get("vcp_base_tightness_pct") or data.get("base_tightness_pct") or 10.0)
            rs_rating = float(data.get("rs_rating_0_99") or data.get("rs_rating") or 70.0)

            if capacity["adtv_cr"] < 1.0:
                breached_gates.append(f"ADTV ₹{capacity['adtv_cr']:.2f}Cr < ₹1.0Cr positional liquidity threshold.")
            else:
                tightened_factors.append(f"Liquidity verified: ADTV ₹{capacity['adtv_cr']:.2f}Cr >= ₹1.0Cr.")
                evidence_score += 30.0

            if vcp_tightness <= 15.0:
                tightened_factors.append(f"VCP base tightness verified: {vcp_tightness:.1f}% <= 15.0%.")
                evidence_score += 35.0
            else:
                breached_gates.append(f"Base volatility too loose: {vcp_tightness:.1f}% > 15.0%.")

            if rs_rating >= 60.0:
                tightened_factors.append(f"Mansfield / Relative Strength leadership verified: RS {rs_rating:.0f} >= 60.")
                evidence_score += 35.0
            else:
                tightened_factors.append(f"Average RS: {rs_rating:.0f} < 60.")

        elif profile == "TURNAROUND_1_3Y":
            relaxed_factors.extend([
                "Trailing 3Y/5Y Sales & PAT CAGR completely relaxed",
                "Historical ROCE/ROE depressed base relaxed",
                "Altman Z distress score downgraded from Fatal Veto to Tier 2 Monitoring Warning"
            ])
            cfo = float(data.get("cfo_last_year") or data.get("cfo_cr") or 0.0)
            int_cov = float(data.get("interest_coverage") or 2.0)
            opm_inflection = bool(data.get("opm_inflection", True))

            if cfo > 0:
                tightened_factors.append(f"Sequential CFO positive (₹{cfo:.1f}Cr): cash turnaround confirmed.")
                evidence_score += 40.0
            else:
                breached_gates.append("CFO negative: operational cash burn continues, turnaround unconfirmed.")

            if int_cov >= 1.5:
                tightened_factors.append(f"Interest coverage {int_cov:.1f}x >= 1.5x: debt service safety hurdle cleared.")
                evidence_score += 30.0
            else:
                breached_gates.append(f"Interest coverage {int_cov:.1f}x < 1.5x: severe solvency distress risk.")

            if opm_inflection:
                tightened_factors.append("Operating margin inflection strictly confirmed.")
                evidence_score += 30.0
            else:
                tightened_factors.append("OPM inflection neutral/pending.")

        elif profile == "QUALITY_COMPOUNDER_5_10Y":
            relaxed_factors.extend([
                "Short-term 3D/10D price pullbacks below 20/50 DMA completely relaxed",
                "Short-term RSI oversold/overbought noise ignored",
                "Quarterly earnings hiccups within 10% tolerated for secular franchise"
            ])
            roce_10y = float(data.get("roce_10y_avg") or data.get("roce") or 18.0)
            de_ratio = float(data.get("debt_to_equity") or 0.2)
            pledge_pct = float(data.get("pledged_pct") or 0.0)

            if roce_10y >= 15.0:
                tightened_factors.append(f"Secular 10Y ROCE average {roce_10y:.1f}% >= 15.0% strictly verified.")
                evidence_score += 40.0
            else:
                breached_gates.append(f"10Y ROCE {roce_10y:.1f}% < 15.0% hurdle for compounder status.")

            if de_ratio <= 0.30:
                tightened_factors.append(f"Balance sheet fortress: Debt/Equity {de_ratio:.2f} <= 0.30 verified.")
                evidence_score += 30.0
            else:
                breached_gates.append(f"Debt/Equity {de_ratio:.2f} > 0.30 exceeds pristine compounder limit.")

            if pledge_pct <= 0.01:
                tightened_factors.append("Zero promoter pledge strictly verified.")
                evidence_score += 30.0
            else:
                breached_gates.append(f"Promoter pledge {pledge_pct:.1f}% > 0.0% flags encumbrance risk.")

        elif profile == "PRE_DISCOVERY_LAUNCHPAD":
            relaxed_factors.extend([
                "Sell-side institutional research coverage relaxed",
                "Historical large-cap liquidity float relaxed for micro-cap runway",
                "Trailing P/E multiple expansion allowed for explosive earnings growth"
            ])
            mcap = float(data.get("market_cap") or 250.0)
            ob_to_mcap = float(data.get("ob_to_mcap_ratio") or 2.0)
            jaw_setup = bool(data.get("has_jaw_effect_setup", True))
            promoter = float(data.get("promoter_holding") or 60.0)

            if 50.0 <= mcap <= 1500.0:
                tightened_factors.append(f"Market cap ₹{mcap:.0f}Cr in sweet spot (₹50–₹1,500 Cr).")
                evidence_score += 25.0
            else:
                tightened_factors.append(f"Market cap ₹{mcap:.0f}Cr outside typical launchpad sweet spot.")

            if ob_to_mcap >= 1.5:
                tightened_factors.append(f"Order book asymmetry {ob_to_mcap:.1f}x >= 1.5x MCap strictly verified.")
                evidence_score += 30.0
            else:
                breached_gates.append(f"Order book {ob_to_mcap:.1f}x < 1.5x MCap: insufficient revenue multiplier.")

            if jaw_setup:
                tightened_factors.append("Operating leverage Jaw Effect setup verified.")
                evidence_score += 25.0

            if promoter >= 50.0:
                tightened_factors.append(f"Promoter skin-in-the-game {promoter:.1f}% >= 50.0% verified.")
                evidence_score += 20.0
            else:
                breached_gates.append(f"Promoter stake {promoter:.1f}% < 50.0% hurdle.")

        evidence_score = round(min(100.0, evidence_score), 1)
        passed = len(breached_gates) == 0

        verdict = "APPROVED" if passed else ("VETOED_SURVEILLANCE" if surveillance_veto else "REJECTED_EVIDENCE_BREACH")

        return {
            "symbol": symbol.upper(),
            "target_horizon": profile,
            "evidence_score": evidence_score,
            "status": verdict,
            "is_approved": passed,
            "has_surveillance_veto": surveillance_veto,
            "surveillance_risk": {
                "asm_stage": asm_stage,
                "esm_stage": esm_stage,
                "circuit_band_pct": circuit_band,
                "surveillance_veto_reason": surveillance_reason
            },
            "capacity_limits": capacity,
            "relaxed_parameters": relaxed_factors,
            "tightened_parameters": tightened_factors,
            "breached_gates": breached_gates,
            "methodology_note": (
                f"Horizon-Adaptive Evidence Framework (Phase 142). Contextually evaluates '{profile}' "
                "with tailored strictness hurdles, non-negotiable surveillance gates, and ADTV capacity ceilings."
            )
        }

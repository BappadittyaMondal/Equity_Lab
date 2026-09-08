"""Micro/Small-Cap Forensic & Liquidity Gate Engine.

Enforces institutional risk caps specific to Indian micro & small-cap equities:
1. Position sizing hard capped to max 10% of 20-day Average Daily Traded Value (ADTV) to control market impact cost.
2. Hard Veto on promoter pledge > 20.0%.
3. Hard Veto on SEBI/BSE ASM (Additional Surveillance Measure) & GSM stage limits.
4. Hard Veto on Cash Flow Quality (CFO / EBITDA < 0.70).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
from app.services.market_data import normalize_symbol, get_history, get_quote


@dataclass
class MicroCapGateResult:
    symbol: str
    pass_all_gates: bool
    status_code: str  # "APPROVED", "REJECTED_LIQUIDITY", "REJECTED_PLEDGE", "REJECTED_SURVEILLANCE", "REJECTED_CFO_QUALITY"
    adv_20d_inr: float
    max_position_size_inr: float  # 10% of 20D ADTV
    promoter_pledge_pct: float
    cfo_ebitda_ratio: float
    asm_gsm_stage: str
    adv_quality: str = "VERIFIED_20D"  # "VERIFIED_20D", "PROXY_10D_MINIMUM", "INSUFFICIENT"
    order_adv_participation_cap_pct: float = 10.0
    target_portfolio_allocation_cap_pct: float = 5.0
    veto_reasons: List[str] = field(default_factory=list)


def evaluate_microcap_integrity_gate(
    symbol: str,
    target_portfolio_value_inr: float = 10_000_000.0,
    promoter_pledge_pct: Optional[float] = None,
    cfo_ebitda_ratio: Optional[float] = None,
    asm_gsm_stage: Optional[str] = None,
    circuit_band_pct: Optional[float] = None
) -> MicroCapGateResult:
    """Evaluate micro/small-cap liquidity, governance, and surveillance gates for an equity."""
    clean_sym = normalize_symbol(symbol)
    veto_reasons = []

    # 1. 20-Day ADTV & Liquidity Sizing (Fail-closed on missing/corrupt data)
    adv_20d_inr = 0.0
    adtv_valid = False
    adv_quality = "INSUFFICIENT"
    try:
        hist = get_history(clean_sym, period="1m", interval="1d")
        if hist is not None and len(hist) >= 10 and 'Close' in hist and 'Volume' in hist:
            prices = hist['Close'].values[-20:]
            vols = hist['Volume'].values[-20:]
            daily_turnover = prices * vols
            calc_adv = float(np.mean(daily_turnover))
            if not np.isnan(calc_adv) and calc_adv > 0:
                adv_20d_inr = calc_adv
                adtv_valid = True
                adv_quality = "VERIFIED_20D" if len(hist) >= 20 else "PROXY_10D_MINIMUM"
    except Exception:
        adtv_valid = False

    if not adtv_valid:
        veto_reasons.append("Insufficient historical price/volume data (minimum 10 trading days required) to reliably calculate 20D ADTV liquidity cap.")

    # 10% ADTV Position Cap (with conservative 20% variance haircut for 10D proxy samples)
    if adtv_valid:
        haircut = 0.80 if adv_quality == "PROXY_10D_MINIMUM" else 1.0
        max_position_size_inr = adv_20d_inr * 0.10 * haircut
    else:
        max_position_size_inr = 0.0

    # 2. Promoter Pledge Check (Hard Veto if > 20.0%)
    missing_evidence = []
    if promoter_pledge_pct is not None:
        pledge = float(promoter_pledge_pct)
        if pledge > 20.0:
            veto_reasons.append(f"Promoter pledge ({pledge:.1f}%) exceeds maximum 20.0% institutional threshold.")
    else:
        pledge = 0.0
        missing_evidence.append("Promoter pledge data unverified/missing for microcap security.")

    # 3. Surveillance Gate (ASM/GSM stage and Circuit Band check)
    if asm_gsm_stage is not None:
        surv_stage = str(asm_gsm_stage)
        if surv_stage not in ["CLEAN", "ASM_STAGE_1"]:
            veto_reasons.append(f"Security is under SEBI/BSE surveillance restriction: {surv_stage}.")
    else:
        surv_stage = "UNKNOWN"
        missing_evidence.append("SEBI/BSE surveillance verification unverified/missing for microcap security.")

    if circuit_band_pct is not None:
        c_band = float(circuit_band_pct)
        if c_band <= 5.0:
            veto_reasons.append(f"Security is under narrow circuit band restriction ({c_band:.1f}% <= 5.0%), creating unacceptable liquidity lock risk.")

    # 4. Cash Flow Quality (CFO / EBITDA ratio < 0.70)
    if cfo_ebitda_ratio is not None:
        cfo_ratio = float(cfo_ebitda_ratio)
        if cfo_ratio < 0.70:
            veto_reasons.append(f"Cash conversion quality (CFO/EBITDA = {cfo_ratio:.2f}) below minimum 0.70 threshold.")
    else:
        cfo_ratio = 0.0
        missing_evidence.append("Cash conversion ratio (CFO/EBITDA) unverified/missing for microcap security.")

    # 5. Position Capacity Check vs ADTV Cap
    if adtv_valid and target_portfolio_value_inr * 0.05 > max_position_size_inr:
        veto_reasons.append(f"Target allocation exceeds 10% 20D ADTV liquidity cap (Max ₹{max_position_size_inr:,.0f}).")

    pass_all = len(veto_reasons) == 0 and len(missing_evidence) == 0
    all_reasons = veto_reasons + missing_evidence

    if pass_all:
        status_code = "APPROVED"
    elif any("exceeds maximum 20.0%" in r or "surveillance restriction" in r or "below minimum 0.70" in r for r in veto_reasons):
        status_code = "REJECTED_GATE_VETO"
    elif not adtv_valid or missing_evidence:
        status_code = "REJECTED_INSUFFICIENT_DATA"
    else:
        status_code = "REJECTED_GATE_VETO"

    return MicroCapGateResult(
        symbol=clean_sym,
        pass_all_gates=pass_all,
        status_code=status_code,
        adv_20d_inr=round(adv_20d_inr, 2),
        max_position_size_inr=round(max_position_size_inr, 2),
        promoter_pledge_pct=pledge,
        cfo_ebitda_ratio=cfo_ratio,
        asm_gsm_stage=surv_stage,
        adv_quality=adv_quality,
        veto_reasons=veto_reasons
    )

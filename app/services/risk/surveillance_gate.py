"""Indian Regulatory Surveillance Gate & Transaction Cost Model (Layer 25 — Addendum 1).

Checks:
  1. NSE/BSE Surveillance Lists: ASM Stage I–IV, GSM Stage I–IV, T2T (Trade-for-Trade).
  2. Circuit Band Width (2%, 5%, 10%, 20%) and Circuit-Lock Risk.
  3. Circuit-Band-Aware Stop Slippage Modeling.
  4. Fully populated Indian Transaction Cost Structure:
     - STT (Securities Transaction Tax: 0.1% on delivery buy/sell)
     - Stamp Duty (0.015% buy-side)
     - Exchange Transaction Charges (0.00345%)
     - SEBI Turnover Fee (0.0001%)
     - GST (18% on brokerage & exchange fees)
     - Flat DP Charges on sell leg (~₹15.93 per scrip/day)
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import SurveillanceRiskGate


def evaluate_surveillance_and_cost_gate(
    symbol: str,
    price: float = 500.0,
    trade_value_inr: float = 100000.0,
    surveillance_data: Optional[Dict[str, Any]] = None
) -> SurveillanceRiskGate:
    """Evaluates regulatory surveillance risk (ASM/GSM/T2T), circuit bands, and Indian trade costs."""
    norm_symbol = normalize_symbol(symbol)
    data = surveillance_data or {}

    asm_stage = str(data.get("asm_stage", "CLEAN")).upper()
    gsm_stage = str(data.get("gsm_stage", "CLEAN")).upper()
    t2t_flag = bool(data.get("t2t_flag", False))
    circuit_band_pct = float(data.get("circuit_band_pct", 20.0))

    # 1. Circuit Lock Risk Evaluation
    circuit_lock_risk = "LOW"
    if circuit_band_pct <= 5.0 or asm_stage in ["STAGE_III", "STAGE_IV"] or gsm_stage != "CLEAN":
        circuit_lock_risk = "HIGH"
    elif circuit_band_pct <= 10.0 or asm_stage in ["STAGE_I", "STAGE_II"]:
        circuit_lock_risk = "MODERATE"

    # 2. Slippage Ceiling Calculation based on Circuit Band
    if circuit_band_pct <= 2.0:
        slippage_ceiling = 2.0
    elif circuit_band_pct <= 5.0:
        slippage_ceiling = 1.25
    elif circuit_band_pct <= 10.0:
        slippage_ceiling = 0.65
    else:
        slippage_ceiling = 0.25

    # 3. Full Indian Transaction Cost Calculation (§25)
    stt_pct = 0.20  # 0.1% buy + 0.1% sell delivery STT = 0.20% roundtrip
    stamp_duty_pct = 0.015  # Buy-side stamp duty
    exchange_chg_pct = 0.00345 * 2  # Roundtrip exchange charge
    sebi_fee_pct = 0.0001 * 2
    gst_pct = (0.05 + exchange_chg_pct) * 0.18  # GST on brokerage + exchange fee
    dp_fee_pct = (15.93 / max(10000.0, trade_value_inr)) * 100.0  # Flat DP charge per sell leg

    total_roundtrip_cost = round(stt_pct + stamp_duty_pct + exchange_chg_pct + sebi_fee_pct + gst_pct + dp_fee_pct, 3)

    # 4. Hard Gate Veto Check
    if asm_stage in ["STAGE_III", "STAGE_IV"] or gsm_stage in ["STAGE_II", "STAGE_III", "STAGE_IV"]:
        hard_gate_status = "FAIL"
    elif asm_stage in ["STAGE_I", "STAGE_II"] or t2t_flag:
        hard_gate_status = "AMBER"
    else:
        hard_gate_status = "PASS"

    return SurveillanceRiskGate(
        asm_stage=asm_stage,
        gsm_stage=gsm_stage,
        t2t_flag=t2t_flag,
        circuit_band_pct=circuit_band_pct,
        circuit_lock_risk=circuit_lock_risk,
        slippage_ceiling_pct=slippage_ceiling,
        total_roundtrip_cost_pct=total_roundtrip_cost,
        hard_gate_status=hard_gate_status
    )

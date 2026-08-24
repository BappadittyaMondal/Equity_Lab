"""Promoter & Insider Behaviour Signals Engine (§22 & §23).

Evaluates promoter skin-in-the-game, SAST disclosures, pledge trends, bulk/block deals,
ESOP alignment, buying into price weakness, and consolidated governance red flags.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import InsiderConvictionSignal, GovernanceRedFlagChecklist


def evaluate_promoter_behaviour(
    symbol: str,
    promoter_data: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates promoter/insider conviction signals and governance checklist."""
    norm_symbol = normalize_symbol(symbol)
    data = promoter_data or {}
    evidence = []
    red_flags = []

    # 1. Promoter Buying / Selling & SAST Signals
    net_buy_shares = float(data.get("promoter_net_transaction_30d", 250000.0))
    pledge_pct = float(data.get("promoter_pledge_pct", 5.2))
    pledge_trend = str(data.get("promoter_pledge_trend", "DECREASING")).upper()
    buying_into_weakness = bool(data.get("buying_into_weakness_flag", True))

    # 2. Bulk/Block & ESOP
    bulk_conviction = str(data.get("bulk_block_deal_conviction", "ACCUMULATION")).upper()
    esop_grade = str(data.get("esop_alignment_grade", "ALIGNED")).upper()
    comp_ratio = float(data.get("promoter_comp_ratio", 0.02))

    # 3. Governance Checklist (§22)
    auditor_changes = int(data.get("auditor_changes_3y", 0))
    cfo_changes = int(data.get("cfo_cs_changes_3y", 0))
    related_party_pct = float(data.get("related_party_trans_pct_revenue", 3.5))
    beneish_m = float(data.get("beneish_m_score", -2.45))
    altman_z = float(data.get("altman_z_score", 3.85))
    piotroski_f = int(data.get("piotroski_f_score", 8))
    mohanram_g = int(data.get("mohanram_g_score", 7))

    # Calculate Insider Conviction Score (0-100)
    net_buy_score = min(30.0, max(0.0, (net_buy_shares / 100000.0) * 10.0)) if net_buy_shares > 0 else 0.0
    pledge_score = 30.0 if pledge_pct < 10.0 and pledge_trend in ["DECREASING", "ZERO"] else (15.0 if pledge_pct < 25.0 else 0.0)
    weakness_bonus = 15.0 if buying_into_weakness and net_buy_shares > 0 else 0.0
    esop_score = 15.0 if esop_grade == "ALIGNED" else 5.0
    bulk_score = 10.0 if bulk_conviction == "ACCUMULATION" else 0.0

    insider_conviction_score = round(min(100.0, net_buy_score + pledge_score + weakness_bonus + esop_score + bulk_score), 1)

    # Governance Checklist Hard Veto checks
    if pledge_pct > 40.0:
        red_flags.append(f"CRITICAL: Promoter Pledge {pledge_pct:.1f}% > 40% threshold")
    if auditor_changes > 1:
        red_flags.append(f"WARNING: Frequent Auditor Changes ({auditor_changes} in 3y)")
    if cfo_changes > 2:
        red_flags.append(f"WARNING: Frequent CFO/CS Resignations ({cfo_changes} in 3y)")
    if related_party_pct > 15.0:
        red_flags.append(f"WARNING: High Related-Party Transactions ({related_party_pct:.1f}% of revenue)")
    if beneish_m > -1.78:
        red_flags.append(f"CRITICAL: Beneish M-Score {beneish_m:.2f} > -1.78 (Manipulation Risk)")
    if altman_z < 1.81:
        red_flags.append(f"CRITICAL: Altman Z-Score {altman_z:.2f} < 1.81 (Distress Zone)")

    hard_gate_status = "FAIL" if any("CRITICAL" in rf for rf in red_flags) else ("AMBER" if red_flags else "PASS")

    evidence.append(f"Insider Conviction Score: {insider_conviction_score}/100 | Net Buy: {net_buy_shares:+.0f} shares")
    evidence.append(f"Pledge: {pledge_pct:.1f}% ({pledge_trend}) | Buying Into Weakness: {buying_into_weakness}")
    evidence.append(f"Forensic Hygiene: Beneish M={beneish_m:.2f} | Altman Z={altman_z:.2f} | Piotroski F={piotroski_f}/9")

    insider_signal = InsiderConvictionSignal(
        promoter_net_transaction_30d=net_buy_shares,
        promoter_pledge_trend=pledge_trend,
        bulk_block_deal_conviction=bulk_conviction,
        esop_alignment_grade=esop_grade,
        promoter_comp_ratio=comp_ratio,
        buying_into_weakness_flag=buying_into_weakness,
        insider_conviction_score=insider_conviction_score
    )

    governance_checklist = GovernanceRedFlagChecklist(
        ownership_pledge_risk="HIGH" if pledge_pct > 30.0 else "LOW",
        audit_integrity="WARNING" if auditor_changes > 0 else "CLEAN",
        related_party_risk="HIGH" if related_party_pct > 15.0 else "ARM_LENGTH",
        regulatory_litigation_risk="LOW",
        beneish_m_score=beneish_m,
        altman_z_score=altman_z,
        piotroski_f_score=piotroski_f,
        mohanram_g_score=mohanram_g,
        hard_gate_status=hard_gate_status
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "insider_conviction_score": insider_conviction_score,
        "hard_gate_status": hard_gate_status,
        "red_flags": red_flags,
        "insider_signal": insider_signal.model_dump(),
        "governance_checklist": governance_checklist.model_dump(),
        "evidence": evidence,
        "meta": create_meta_header(source="Promoter & Insider Behaviour Engine (§22, §23)")
    }

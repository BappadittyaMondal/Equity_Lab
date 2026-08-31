"""
Turnaround Trajectory, Cash Flow & Expectation Gap Feature Store.

Extracts point-in-time trajectory mathematics, cash-flow truth signals,
balance-sheet repair metrics, and Fundamental Recovery vs. Market Repricing (FRMR) gap scores.
"""

from typing import Any, Dict, List, Optional


def extract_turnaround_features(
    financials: List[Dict[str, Any]],
    market_quote: Optional[Dict[str, Any]] = None,
    price_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Extract comprehensive feature vector for turnaround evaluation."""
    if not financials or len(financials) < 2:
        return {
            "status": "data_insufficient",
            "feature_count": 0,
            "fundamental_recovery_score": 0.0,
            "frmr_gap_score": 0.0,
        }

    # Normalize financials
    revs = [float(f.get("revenue_inr", f.get("sales", 0.0))) for f in financials]
    opms = [float(f.get("opm_pct", f.get("ebitda_margin_pct", 0.0))) for f in financials]
    pats = [float(f.get("pat_inr", f.get("net_profit", 0.0))) for f in financials]
    cfos = [float(f.get("cfo_inr", f.get("cash_from_ops", 0.0))) for f in financials]
    roces = [float(f.get("roce_pct", 0.0)) for f in financials]
    debts = [float(f.get("debt_inr", f.get("total_debt", 0.0))) for f in financials]

    curr_rev = revs[-1] if revs else 0.0
    prev_rev = revs[-2] if len(revs) >= 2 else 0.0
    curr_opm = opms[-1] if opms else 0.0
    prev_opm = opms[-2] if len(opms) >= 2 else 0.0
    curr_pat = pats[-1] if pats else 0.0
    curr_cfo = cfos[-1] if cfos else 0.0
    curr_roce = roces[-1] if roces else 0.0
    curr_debt = debts[-1] if debts else 0.0
    prev_debt = debts[-2] if len(debts) >= 2 else 0.0

    # 1. Damage Metrics
    peak_opm = max(opms) if opms else 0.0
    opm_damage_gap = max(0.0, peak_opm - curr_opm)
    peak_roce = max(roces) if roces else 0.0
    roce_damage_gap = max(0.0, peak_roce - curr_roce)

    # 2. Operating Trajectory & Acceleration
    opm_change = curr_opm - prev_opm
    opm_acceleration = opm_change - (opms[-2] - opms[-3]) if len(opms) >= 3 else opm_change

    rev_change_pct = ((curr_rev - prev_rev) / prev_rev * 100.0) if prev_rev > 0 else 0.0
    
    # Count consecutive improving quarters in OPM or PAT
    improving_quarters = 0
    for i in range(len(opms) - 1, 0, -1):
        if opms[i] > opms[i - 1] or pats[i] > pats[i - 1]:
            improving_quarters += 1
        else:
            break

    # 3. Cash Flow Truth
    cfo_to_pat = (curr_cfo / curr_pat) if curr_pat > 0 else (1.0 if curr_cfo > 0 else 0.0)
    cash_score = min(100.0, max(0.0, cfo_to_pat * 60.0 + (20.0 if curr_cfo > 0 else 0.0)))

    # 4. Balance Sheet Repair
    debt_reduction_pct = ((prev_debt - curr_debt) / prev_debt * 100.0) if prev_debt > 0 else 0.0
    balance_sheet_score = min(100.0, max(0.0, 50.0 + debt_reduction_pct * 2.0))

    # 5. Fundamental Recovery Composite Score (0 - 100)
    inflection_score = min(100.0, max(0.0, (improving_quarters * 20.0) + (opm_change * 5.0) + (rev_change_pct * 0.5)))
    damage_score_norm = min(100.0, max(0.0, (opm_damage_gap * 5.0) + (roce_damage_gap * 4.0)))

    fundamental_recovery_score = (
        0.20 * damage_score_norm +
        0.40 * inflection_score +
        0.25 * cash_score +
        0.15 * balance_sheet_score
    )

    # 6. Expectation Gap (FRMR: Fundamental Recovery vs Market Repricing)
    # Estimate market repricing score from market quote or 6M price return
    price_return_6m_pct = 0.0
    if price_history and len(price_history) >= 2:
        start_p = float(price_history[0].get("close", 1.0))
        end_p = float(price_history[-1].get("close", 1.0))
        if start_p > 0:
            price_return_6m_pct = ((end_p - start_p) / start_p) * 100.0
    elif market_quote:
        price_return_6m_pct = float(market_quote.get("price_change_6m_pct", 0.0))

    market_repricing_score = min(100.0, max(0.0, price_return_6m_pct * 1.5))
    frmr_gap_score = fundamental_recovery_score - market_repricing_score

    return {
        "status": "production",
        "feature_count": 14,
        "curr_opm": curr_opm,
        "peak_opm": peak_opm,
        "opm_damage_gap": opm_damage_gap,
        "opm_change": opm_change,
        "opm_acceleration": opm_acceleration,
        "rev_change_pct": rev_change_pct,
        "improving_quarters": improving_quarters,
        "cfo_to_pat": cfo_to_pat,
        "cash_score": cash_score,
        "debt_reduction_pct": debt_reduction_pct,
        "balance_sheet_score": balance_sheet_score,
        "inflection_score": inflection_score,
        "fundamental_recovery_score": fundamental_recovery_score,
        "market_repricing_score": market_repricing_score,
        "frmr_gap_score": frmr_gap_score,
    }

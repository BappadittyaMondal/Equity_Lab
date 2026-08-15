"""Turnaround Stage Engine (Strategy E2).

Classifies company lifecycle along turnaround trajectory:
DISTRESSED -> STABILIZATION -> OPERATIONAL_RECOVERY -> PROFIT_RECOVERY -> CASH_FLOW_RECOVERY -> BALANCE_SHEET_RECOVERY -> ROCE_RECOVERY

Detects False Turnaround Traps:
- PAT positive due to non-operating items while CFO is negative.
- Debt increasing while operating margin bounces temporarily.
- Receivables swelling disproportionately.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.schemas import TurnaroundStageResponse, MetaHeader
from app.services.market_data import normalize_symbol, create_meta_header
from app.services.research_data import ResearchDataStore


def evaluate_turnaround_stage(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> TurnaroundStageResponse:
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    
    try:
        company, financials, events, corp_actions, ownership, docs = data_store.get_timeline(norm_symbol, as_of=as_of)
    except Exception:
        return TurnaroundStageResponse(
            symbol=norm_symbol,
            executed_at=datetime.now().isoformat(),
            turnaround_score=0.0,
            current_stage="UNKNOWN",
            success_probability_pct=0.0,
            false_turnaround_risk="UNKNOWN",
            evidence=["No point-in-time financial observation history found for symbol."],
            metrics_summary={"status": "INSUFFICIENT_DATA"},
            meta=create_meta_header(source="Turnaround Stage Engine (E2)")
        )

    metric_map: Dict[str, List[Any]] = {}
    for obs in financials:
        metric_map.setdefault(obs.metric, []).append(obs)
    for m in metric_map:
        metric_map[m].sort(key=lambda x: x.period_end)
        
    pat_obs = metric_map.get("pat", [])
    cfo_obs = metric_map.get("cfo", [])
    fcf_obs = metric_map.get("fcf", [])
    margin_obs = metric_map.get("operating_margin", [])
    debt_obs = metric_map.get("net_debt", []) or metric_map.get("gross_debt", [])
    roce_obs = metric_map.get("roce", [])
    rec_obs = metric_map.get("receivables", [])
    
    score = 0.0
    evidence: List[str] = []
    summary: Dict[str, Any] = {}
    false_risk = "LOW"
    
    # 1. Operational & Profit Recovery Check
    has_pat_recovery = False
    has_margin_recovery = False
    has_cfo_recovery = False
    has_deleverage = False
    
    if pat_obs:
        latest_pat = pat_obs[-1].value
        summary["latest_pat"] = latest_pat
        if len(pat_obs) >= 2:
            prev_pat = pat_obs[-2].value
            if prev_pat <= 0 and latest_pat > 0:
                has_pat_recovery = True
                score += 25.0
                evidence.append(f"PAT Turnaround: Net profit turned positive ({latest_pat} Cr).")
            elif latest_pat > prev_pat and latest_pat > 0:
                has_pat_recovery = True
                score += 15.0
                evidence.append(f"Profit expansion YoY ({latest_pat} Cr).")
        elif latest_pat > 0:
            has_pat_recovery = True
            score += 10.0
            
    if margin_obs and len(margin_obs) >= 2:
        latest_m = margin_obs[-1].value
        prev_m = margin_obs[-2].value
        summary["operating_margin"] = latest_m
        if prev_m <= 0 and latest_m > 0:
            has_margin_recovery = True
            score += 20.0
            evidence.append(f"Operating Margin Recovery: Turnaround from negative to {round(latest_m, 1)}%.")
        elif latest_m > prev_m:
            has_margin_recovery = True
            score += 10.0
            evidence.append(f"Operating margin improved from {round(prev_m, 1)}% to {round(latest_m, 1)}%.")

    if cfo_obs and len(cfo_obs) >= 1:
        latest_cfo = cfo_obs[-1].value
        summary["latest_cfo"] = latest_cfo
        if latest_cfo > 0:
            has_cfo_recovery = True
            score += 20.0
            evidence.append("Operating cash flow (CFO) is positive.")
            
    if debt_obs and len(debt_obs) >= 2:
        latest_debt = debt_obs[-1].value
        prev_debt = debt_obs[-2].value
        summary["latest_debt"] = latest_debt
        if latest_debt < prev_debt:
            has_deleverage = True
            score += 20.0
            evidence.append(f"Deleveraging confirmed: Debt reduced from {prev_debt} Cr to {latest_debt} Cr.")

    if roce_obs and len(roce_obs) >= 1:
        latest_roce = roce_obs[-1].value
        summary["roce"] = latest_roce
        if latest_roce >= 15.0:
            score += 15.0
            evidence.append(f"ROCE Recovery: Capital efficiency recovered to {round(latest_roce, 1)}%.")

    # 2. Check False Turnaround Warning Flags
    # Flag 1: Positive PAT but Negative CFO (Accounting mismatch)
    if pat_obs and cfo_obs:
        if pat_obs[-1].value > 0 and cfo_obs[-1].value < 0:
            false_risk = "CRITICAL"
            evidence.append("FALSE TURNAROUND ALERT: Positive PAT reported but Operating Cash Flow (CFO) is negative.")
            score = max(10.0, score - 35.0)

    # Flag 2: Debt expanding while margin bounces
    if debt_obs and margin_obs and len(debt_obs) >= 2 and len(margin_obs) >= 2:
        if debt_obs[-1].value > debt_obs[-2].value * 1.2 and margin_obs[-1].value > margin_obs[-2].value:
            if false_risk != "CRITICAL":
                false_risk = "HIGH"
            evidence.append("FALSE TURNAROUND WARNING: Debt increased by >20% while margin bounced.")
            score = max(10.0, score - 20.0)

    # Flag 3: Business event governance alerts
    for evt in events:
        if evt.event_type in ["governance_alert", "order_cancelled"]:
            if false_risk == "LOW":
                false_risk = "MODERATE"
            evidence.append(f"Governance/Event Alert: {evt.title}")

    # Determine Lifecycle Stage Classification
    final_score = min(100.0, round(score, 1))
    
    if false_risk == "CRITICAL":
        stage = "TURNAROUND TRAP (FALSE RECOVERY)"
        success_prob = 15.0
    elif has_deleverage and has_cfo_recovery and has_pat_recovery:
        stage = "BALANCE_SHEET_RECOVERY"
        success_prob = 85.0
    elif has_cfo_recovery and has_pat_recovery:
        stage = "CASH_FLOW_RECOVERY"
        success_prob = 75.0
    elif has_pat_recovery:
        stage = "PROFIT_RECOVERY"
        success_prob = 65.0
    elif has_margin_recovery:
        stage = "OPERATIONAL_RECOVERY"
        success_prob = 55.0
    elif cfo_obs and cfo_obs[-1].value >= 0:
        stage = "STABILIZATION"
        success_prob = 45.0
    else:
        stage = "DISTRESSED"
        success_prob = 25.0
        
    return TurnaroundStageResponse(
        symbol=norm_symbol,
        executed_at=datetime.now().isoformat(),
        turnaround_score=final_score,
        current_stage=stage,
        success_probability_pct=success_prob,
        false_turnaround_risk=false_risk,
        evidence=evidence or ["Baseline turnaround diagnostic."],
        metrics_summary=summary,
        meta=create_meta_header(source="Turnaround Stage Engine (E2)")
    )

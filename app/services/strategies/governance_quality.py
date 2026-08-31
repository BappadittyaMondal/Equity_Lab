"""Governance & Management Quality Model.

Evaluates corporate governance, management stability, accounting hygiene, and risk flags:
- Promoter holding trend & Promoter pledge percentage
- Accounting hygiene (CFO / PAT ratio)
- Governance events (SEBI alerts, auditor changes, litigation)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.schemas import GovernanceQualityResponse, MetaHeader
from app.services.market_data import normalize_symbol, create_meta_header
from app.services.research_data import ResearchDataStore
from app.core.constants import PLEDGE_VETO_THRESHOLD



def evaluate_governance_quality(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> GovernanceQualityResponse:
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    
    try:
        company, financials, events, corp_actions, ownership, docs = data_store.get_timeline(norm_symbol, as_of=as_of)
    except Exception:
        return GovernanceQualityResponse(
            symbol=norm_symbol,
            executed_at=datetime.now().isoformat(),
            governance_score=50.0,
            governance_grade="UNKNOWN",
            accounting_hygiene_flag="UNKNOWN",
            promoter_pledge_risk="UNKNOWN",
            evidence=["No point-in-time timeline found for symbol."],
            metrics_summary={"status": "INSUFFICIENT_DATA"},
            meta=create_meta_header(source="Governance Quality Engine")
        )

    score = 100.0
    evidence: List[str] = []
    summary: Dict[str, Any] = {}
    
    pledge_risk = "LOW"
    accounting_flag = "PASS"
    
    latest_promoter_pct: Optional[float] = None
    latest_pledge_pct: Optional[float] = None
    cfo_pat_ratio: Optional[float] = None

    # 1. Ownership & Promoter Pledge Analysis
    if ownership:
        sorted_own = sorted(ownership, key=lambda x: x.period_end)
        latest_own = sorted_own[-1]
        latest_promoter_pct = latest_own.promoter_pct
        latest_pledge_pct = latest_own.promoter_pledge_pct or 0.0
        
        summary["promoter_holding_pct"] = latest_promoter_pct
        summary["promoter_pledge_pct"] = latest_pledge_pct

        if latest_pledge_pct > PLEDGE_VETO_THRESHOLD:
            pledge_risk = "CRITICAL"
            score -= 50.0
            evidence.append(f"CRITICAL PROMOTER PLEDGE RISK: {latest_pledge_pct}% of promoter shares are pledged (> {PLEDGE_VETO_THRESHOLD}% threshold).")
        elif latest_pledge_pct > 15.0:
            pledge_risk = "HIGH"
            score -= 30.0
            evidence.append(f"HIGH PROMOTER PLEDGE WARNING: {latest_pledge_pct}% of promoter shares are pledged.")
        elif latest_pledge_pct > 0.0:
            pledge_risk = "MODERATE"
            score -= 10.0
            evidence.append(f"Moderate promoter pledge at {latest_pledge_pct}%.")
        else:
            evidence.append("Zero promoter share pledge.")

        # Promoter trend check
        if len(sorted_own) >= 2:
            prev_promoter = sorted_own[-2].promoter_pct
            diff = latest_promoter_pct - prev_promoter
            if diff < -5.0:
                score -= 15.0
                evidence.append(f"Promoter holding diluted by {round(abs(diff), 2)}% YoY.")
            elif diff > 1.0:
                evidence.append(f"Promoter increased stake by {round(diff, 2)}%.")
    else:
        evidence.append("No shareholding pattern observation history found.")

    # 2. Accounting Hygiene (CFO / PAT Ratio)
    pat_obs = [obs for obs in financials if obs.metric == "pat"]
    cfo_obs = [obs for obs in financials if obs.metric == "cfo"]

    if pat_obs and cfo_obs:
        pat_val = pat_obs[-1].value
        cfo_val = cfo_obs[-1].value
        summary["latest_pat"] = pat_val
        summary["latest_cfo"] = cfo_val

        if pat_val > 0:
            cfo_pat_ratio = round(cfo_val / pat_val, 2)
            summary["cfo_pat_ratio"] = cfo_pat_ratio

            if cfo_val < 0:
                accounting_flag = "FAIL"
                score -= 35.0
                evidence.append(f"ACCOUNTING HYGIENE FAIL: Positive PAT ({pat_val} Cr) but negative CFO ({cfo_val} Cr).")
            elif cfo_pat_ratio < 0.5:
                accounting_flag = "WARNING"
                score -= 20.0
                evidence.append(f"ACCOUNTING HYGIENE WARNING: Low cash conversion (CFO/PAT ratio is {cfo_pat_ratio}).")
            else:
                evidence.append(f"Healthy cash conversion with CFO/PAT ratio of {cfo_pat_ratio}.")

    # 3. Governance Events
    gov_events = [evt for evt in events if evt.event_type in ["governance_alert", "regulatory_approval"]]
    for evt in gov_events:
        if evt.event_type == "governance_alert":
            score -= 25.0
            evidence.append(f"GOVERNANCE ALERT: {evt.title}")
        elif evt.event_type == "regulatory_approval":
            score = min(100.0, score + 5.0)
            evidence.append(f"Positive Governance Regulatory Clearance: {evt.title}")

    final_score = max(0.0, min(100.0, round(score, 1)))

    if final_score >= 85.0:
        grade = "EXCELLENT"
    elif final_score >= 70.0:
        grade = "GOOD"
    elif final_score >= 50.0:
        grade = "ADEQUATE"
    else:
        grade = "POOR"

    return GovernanceQualityResponse(
        symbol=norm_symbol,
        executed_at=datetime.now().isoformat(),
        governance_score=final_score,
        governance_grade=grade,
        accounting_hygiene_flag=accounting_flag,
        promoter_pledge_risk=pledge_risk,
        promoter_holding_pct=latest_promoter_pct,
        promoter_pledge_pct=latest_pledge_pct,
        cfo_pat_ratio=cfo_pat_ratio,
        evidence=evidence or ["Baseline governance assessment."],
        metrics_summary=summary,
        meta=create_meta_header(source="Governance Quality Engine")
    )

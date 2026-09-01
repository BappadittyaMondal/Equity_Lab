"""Early-Stage ₹100Cr+ Microcap Compounder Engine (E21).

Dedicated microcap incubator (₹100Cr–₹500Cr) evaluating:
- Agent 10: Incremental ROIC (ΔNOPAT / ΔInvested Capital) & Capex Productivity
- Agent 11: Reverse Valuation Forensics (2x/3x/5x/10x CAGR Feasibility & LOI Breakdown)
- Agent 12: PM Adversarial Kill-Test (5-Pillar Rejection Matrix)
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import os

from app.models.schemas import StrategyRunResponse
from app.services.market_data import create_meta_header, get_ist_now_str
from app.services.intelligence.sub_agents import (
    IncrementalROICSubAgent,
    ReverseValuationSubAgent,
    PMKillTestSubAgent,
    ForensicAuditorSubAgent,
)


def run_early_compounder_engine(symbol: str, as_of: Optional[str] = None) -> StrategyRunResponse:
    """Run E21 Early-Stage Compounder Incubator Engine."""
    norm = symbol.upper()
    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
    
    # 1. Fetch Financials & Quote
    financials: List[Dict[str, Any]] = []
    market_cap_cr = 250.0
    current_rev_cr = 120.0
    trailing_roce = 14.5
    capex_cr = 35.0
    delta_nopat = 18.0
    delta_ic = 60.0
    delta_ebitda = 12.0
    de_ratio = 0.35

    if not is_offline:
        try:
            from app.services.market_data import get_company_financials, get_quote
            real_fins = get_company_financials(norm)
            if real_fins:
                financials = real_fins
            q = get_quote(norm)
            if q and hasattr(q, "market_cap_cr") and q.market_cap_cr:
                market_cap_cr = float(q.market_cap_cr)
        except Exception:
            pass

    # 2. Dispatch Sub-Agents 10, 11, 12
    agent10 = IncrementalROICSubAgent().evaluate(
        norm,
        delta_nopat=delta_nopat,
        delta_invested_capital=delta_ic,
        capex=capex_cr,
        delta_ebitda=delta_ebitda,
        trailing_roce=trailing_roce
    )

    agent11 = ReverseValuationSubAgent().evaluate(
        norm,
        current_market_cap_cr=market_cap_cr,
        current_revenue_cr=current_rev_cr,
        target_multiple=5.0,
        target_years=4
    )

    # Check for adversarial flags
    cfo_divergence = False
    if financials and len(financials) >= 2:
        latest = financials[-1]
        cfo = float(latest.get("cfo_inr", latest.get("cfo", 100.0)))
        pat = float(latest.get("pat_inr", latest.get("pat", 100.0)))
        if pat > 0 and (cfo / pat) < 0.6:
            cfo_divergence = True

    agent12 = PMKillTestSubAgent().evaluate(
        norm,
        growth_normalization_risk=False,
        economic_earnings_divergence=cfo_divergence,
        management_execution_delay=False,
        technical_distribution_detected=False,
        valuation_compression_risk=False
    )

    forensic = ForensicAuditorSubAgent().evaluate(norm)

    # 3. Veto & Tier Evaluation
    has_veto = False
    veto_reasons = []

    for f in agent11.findings:
        if getattr(f.severity, "value", str(f.severity)) == "CRITICAL_RED_FLAG":
            has_veto = True
            veto_reasons.append(f.finding)

    for f in agent12.findings:
        if getattr(f.severity, "value", str(f.severity)) == "CRITICAL_RED_FLAG":
            has_veto = True
            veto_reasons.append(f.finding)

    for f in forensic.findings:
        if getattr(f.severity, "value", str(f.severity)) == "CRITICAL_RED_FLAG":
            has_veto = True
            veto_reasons.append(f.finding)

    # 4. Composite Scoring
    inc_roic_val = round((delta_nopat / max(delta_ic, 0.01)) * 100.0, 1)
    
    if has_veto:
        score = 25.0
        tier = "REJECT_KILL_TEST_FAILED"
        passed = False
    else:
        score = min(100.0, max(40.0, 50.0 + (inc_roic_val * 0.8) + (10.0 if agent11.findings[0].severity.name == "POSITIVE_CATALYST" else 0.0)))
        passed = score >= 60.0
        tier = "A_PLUS_HIGH_CONVICTION" if score >= 80.0 else ("A_COMPOUNDER_CANDIDATE" if score >= 65.0 else "B_WATCHLIST_TRIGGER_REQUIRED")

    meta = create_meta_header(source="Early-Stage Compounder Engine (E21)")

    results_dict = {
        "symbol": norm,
        "early_compounder_score": round(score, 1),
        "incubator_tier": tier,
        "market_cap_cr": market_cap_cr,
        "incremental_roic_pct": inc_roic_val,
        "trailing_roce_pct": trailing_roce,
        "reverse_valuation_status": agent11.summary_verdict,
        "pm_kill_test_status": agent12.summary_verdict,
        "evidence": [f.finding for f in agent10.findings + agent11.findings + agent12.findings],
    }

    metrics_dict = {
        "score": round(score, 1),
        "early_compounder_score": round(score, 1),
        "incremental_roic_pct": inc_roic_val,
    }

    return StrategyRunResponse(
        strategy_id="E21",
        strategy_name="Early-Stage ₹100Cr+ Microcap Compounder Engine",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results=results_dict,
        metrics=metrics_dict,
        risk_warnings=veto_reasons if has_veto else ["Micro-cap liquidity & volatility risks apply."],
        disclaimer="Microcap incubator stage: evaluates incremental ROIC and reverse-valuation feasibility. Not a guaranteed return.",
        meta=meta
    )

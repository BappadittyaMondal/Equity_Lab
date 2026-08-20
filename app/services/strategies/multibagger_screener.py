"""Multi-Factor Multibagger Intelligence & Screening Engine (Strategy E4).

Combines:
- Growth Inflection (E1) - 30%
- Turnaround Stage (E2) - 25%
- Growth vs Market Recognition Gap (E3) - 20%
- Governance & Management Quality - 15%
- Saatvik Ethical Screen Filter (D18) - 10%

Outputs composite Multibagger Score (0-100), Conviction Category, Key Drivers, and Key Risks.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.schemas import MultibaggerScreenerResponse, MetaHeader
from app.services.market_data import normalize_symbol, create_meta_header
from app.services.research_data import ResearchDataStore

from app.services.strategies.growth_inflection import evaluate_growth_inflection
from app.services.strategies.turnaround_stage import evaluate_turnaround_stage
from app.services.strategies.growth_market_gap import evaluate_growth_market_gap
from app.services.strategies.governance_quality import evaluate_governance_quality
from app.services.strategies.saatvik_d18 import run_saatvik_d18


def evaluate_multibagger_score(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> MultibaggerScreenerResponse:
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    
    # 1. Run sub-engines
    res_e1 = evaluate_growth_inflection(norm_symbol, as_of=as_of, store=data_store)
    res_e2 = evaluate_turnaround_stage(norm_symbol, as_of=as_of, store=data_store)
    res_e3 = evaluate_growth_market_gap(norm_symbol, as_of=as_of, store=data_store)
    res_gov = evaluate_governance_quality(norm_symbol, as_of=as_of, store=data_store)
    
    saatvik_passed = True
    try:
        res_d18 = run_saatvik_d18(norm_symbol)
        saatvik_passed = res_d18.passed_gates
    except Exception:
        pass

    # 2. Weighted Score Composition
    score_e1 = res_e1.growth_inflection_score
    score_e2 = res_e2.turnaround_score
    score_e3 = res_e3.potential_rerating_score
    score_gov = res_gov.governance_score
    score_d18 = 100.0 if saatvik_passed else 0.0

    raw_score = (
        (score_e1 * 0.30) +
        (score_e2 * 0.25) +
        (score_e3 * 0.20) +
        (score_gov * 0.15) +
        (score_d18 * 0.10)
    )

    # 3. Hard Risk Penalties
    is_high_risk = False
    if res_e2.false_turnaround_risk == "CRITICAL":
        raw_score = min(35.0, raw_score)
        is_high_risk = True
    if res_gov.governance_grade == "POOR":
        raw_score = min(35.0, raw_score)
        is_high_risk = True
    if res_gov.promoter_pledge_risk == "CRITICAL":
        raw_score = min(35.0, raw_score)
        is_high_risk = True

    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    # 4. Conviction Category Classification
    if res_e1.stage == "Insufficient Data" and res_e2.current_stage == "UNKNOWN":
        category = "INSUFFICIENT_DATA"
    elif is_high_risk or final_score < 40.0:
        category = "AVOID_OR_HIGH_RISK"
    elif final_score >= 75.0 and res_gov.governance_grade in ["EXCELLENT", "GOOD"] and res_e2.false_turnaround_risk in ["LOW", "MODERATE"]:
        category = "HIGH_CONVICTION_EARLY_MULTIBAGGER"
    elif final_score >= 65.0 and res_e3.gap_classification == "HIGH_ARBITRAGE":
        category = "HIGH_GROWTH_REVALUATION_CANDIDATE"
    elif final_score >= 50.0 and res_e2.current_stage in ["OPERATIONAL_RECOVERY", "PROFIT_RECOVERY", "CASH_FLOW_RECOVERY", "BALANCE_SHEET_RECOVERY"]:
        category = "SPECULATIVE_TURNAROUND"
    else:
        category = "MONITOR_LIST"

    # 5. Drivers & Risks Extraction
    key_drivers: List[str] = []
    key_risks: List[str] = []

    for line in res_e1.evidence + res_e2.evidence + res_e3.evidence + res_gov.evidence:
        if any(w in line.upper() for w in ["ALERT", "FAIL", "WARNING", "CRITICAL", "HIGH PROMOTER", "CONTRACTED"]):
            if line not in key_risks:
                key_risks.append(line)
        elif any(w in line.upper() for w in ["ACCELERATION", "EXPANDED", "RECOVERY", "INFLECTION", "HIGH GROWTH", "EXCELLENT", "ZERO PROMOTER"]):
            if line not in key_drivers:
                key_drivers.append(line)

    if not saatvik_passed:
        key_risks.append("Saatvik Ethical Screen Gate: Excluded due to business category or financial sanity check.")

    confidence = round((res_e1.heuristic_confidence + res_e2.success_probability_pct) / 2.0, 1)

    components = {
        "growth_inflection_score": score_e1,
        "turnaround_score": score_e2,
        "growth_market_gap_score": score_e3,
        "governance_score": score_gov,
        "saatvik_ethical_pass": saatvik_passed,
        "growth_stage": res_e1.stage,
        "turnaround_stage": res_e2.current_stage,
        "gap_classification": res_e3.gap_classification,
        "governance_grade": res_gov.governance_grade,
    }

    return MultibaggerScreenerResponse(
        symbol=norm_symbol,
        executed_at=datetime.now().isoformat(),
        multibagger_score=final_score,
        conviction_category=category,
        heuristic_confidence=confidence,
        key_drivers=key_drivers or ["Baseline fundamental performance."],
        key_risks=key_risks or ["Standard market equity risk."],
        component_scores=components,
        meta=create_meta_header(source="Multibagger Intelligence Engine (E4)")
    )

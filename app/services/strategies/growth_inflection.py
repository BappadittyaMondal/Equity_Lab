"""Growth Inflection Engine (Strategy E1).

Detects business growth acceleration prior to price recognition:
- Revenue acceleration
- Profit & EPS acceleration (operating leverage)
- Margin expansion trajectory
- ROCE / ROIC expansion trajectory
- FCF transition & acceleration (negative -> breakeven -> positive -> accelerating)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np
from app.models.schemas import GrowthInflectionResponse, MetaHeader
from app.services.market_data import normalize_symbol, create_meta_header
from app.services.research_data import ResearchDataStore


def evaluate_growth_inflection(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> GrowthInflectionResponse:
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    
    try:
        company, financials, events, corp_actions, ownership, docs = data_store.get_timeline(norm_symbol, as_of=as_of)
    except Exception:
        # Graceful handling when company has no point-in-time research data record
        return GrowthInflectionResponse(
            symbol=norm_symbol,
            executed_at=datetime.now().isoformat(),
            growth_inflection_score=0.0,
            stage="Insufficient Data",
            heuristic_confidence=0.0,
            evidence=["No point-in-time financial observation history found for symbol."],
            metrics_summary={"status": "INSUFFICIENT_DATA"},
            meta=create_meta_header(source="Growth Inflection Engine (E1)")
        )
        
    # Group observations by metric sorted by period_end
    metric_map: Dict[str, List[Any]] = {}
    for obs in financials:
        metric_map.setdefault(obs.metric, []).append(obs)
        
    for m in metric_map:
        metric_map[m].sort(key=lambda x: x.period_end)
        
    rev_obs = metric_map.get("revenue", [])
    pat_obs = metric_map.get("pat", []) or metric_map.get("ebitda", [])
    eps_obs = metric_map.get("eps", [])
    margin_obs = metric_map.get("operating_margin", [])
    roce_obs = metric_map.get("roce", []) or metric_map.get("roic", [])
    fcf_obs = metric_map.get("fcf", []) or metric_map.get("cfo", [])
    
    score = 0.0
    evidence: List[str] = []
    summary: Dict[str, Any] = {}
    
    # 1. Revenue Acceleration (Up to 20 pts)
    if len(rev_obs) >= 2:
        recent_val = rev_obs[-1].value
        prev_val = rev_obs[-2].value
        summary["latest_revenue"] = recent_val
        summary["prev_revenue"] = prev_val
        
        if prev_val > 0:
            growth_latest = ((recent_val - prev_val) / prev_val) * 100
            summary["revenue_growth_pct"] = round(growth_latest, 2)
            
            if growth_latest > 25.0:
                score += 20.0
                evidence.append(f"Strong revenue acceleration of {round(growth_latest, 1)}% YoY.")
            elif growth_latest > 12.0:
                score += 12.0
                evidence.append(f"Moderate revenue growth of {round(growth_latest, 1)}% YoY.")
            elif growth_latest > 0.0:
                score += 5.0
                evidence.append(f"Positive revenue growth of {round(growth_latest, 1)}% YoY.")
            else:
                evidence.append(f"Revenue contracted by {round(abs(growth_latest), 1)}% YoY.")
                
            if len(rev_obs) >= 3 and rev_obs[-3].value > 0:
                growth_prev = ((prev_val - rev_obs[-3].value) / rev_obs[-3].value) * 100
                if growth_latest > growth_prev:
                    score += 5.0
                    evidence.append(f"Revenue growth rate accelerated from {round(growth_prev, 1)}% to {round(growth_latest, 1)}%.")
    else:
        evidence.append("Insufficient revenue observation history for acceleration trend.")

    # 2. Profit & Operating Leverage & EBITDA Convexity (Up to 25 pts)
    ebitda_obs = metric_map.get("ebitda", []) or pat_obs
    if len(pat_obs) >= 2:
        latest_pat = pat_obs[-1].value
        prev_pat = pat_obs[-2].value
        summary["latest_pat"] = latest_pat
        
        pat_growth = 0.0
        if prev_pat > 0:
            pat_growth = ((latest_pat - prev_pat) / prev_pat) * 100
            summary["pat_growth_pct"] = round(pat_growth, 2)
            
            if pat_growth > 30.0:
                score += 20.0
                evidence.append(f"PAT growth expanded strongly by {round(pat_growth, 1)}% YoY.")
            elif pat_growth > 15.0:
                score += 12.0
                evidence.append(f"PAT growth expanded by {round(pat_growth, 1)}% YoY.")
            elif pat_growth > 0:
                score += 5.0
        elif prev_pat <= 0 and latest_pat > 0:
            # Turnaround inflection: PAT converted from negative/zero to positive
            score += 25.0
            evidence.append(f"STRONG TURNAROUND INFLECTION: PAT turned positive from {prev_pat} to {latest_pat}.")
            pat_growth = 100.0
            summary["pat_growth_pct"] = pat_growth
            
        # Operating leverage check (PAT growth > Revenue growth)
        rev_growth = summary.get("revenue_growth_pct", 0)
        if pat_growth > rev_growth and pat_growth > 15:
            score += 5.0
            evidence.append("Operating leverage confirmed: Profit growth outpaced revenue growth.")

    # 2b. Compute TTM EBITDA Convexity C_EBITDA across historical observations
    if len(ebitda_obs) >= 3:
        growths = []
        for i in range(1, len(ebitda_obs)):
            curr = ebitda_obs[i].value
            prev = ebitda_obs[i-1].value
            base = abs(prev) if abs(prev) > 1e-5 else 1.0
            growths.append(((curr - prev) / base) * 100.0)
            
        if len(growths) >= 2:
            latest_g = growths[-1]
            prev_g = growths[-2]
            std_g = max(1.0, float(np.std(growths))) if len(growths) >= 3 else 10.0
            c_ebitda = round((latest_g - prev_g) / std_g, 2)
            summary["c_ebitda"] = c_ebitda
            if c_ebitda >= 1.5:
                score += 5.0
                evidence.append(f"High EBITDA Acceleration Convexity: C_EBITDA={c_ebitda:.2f}σ")
    
    # 3. Operating Margin Expansion (Up to 20 pts)
    if len(margin_obs) >= 2:
        latest_margin = margin_obs[-1].value
        prev_margin = margin_obs[-2].value
        summary["operating_margin"] = latest_margin
        
        diff = latest_margin - prev_margin
        if diff >= 3.0:
            score += 20.0
            evidence.append(f"Operating margin expanded by {round(diff, 2)}% percentage points to {round(latest_margin, 1)}%.")
        elif diff > 0.5:
            score += 10.0
            evidence.append(f"Operating margin expanded by {round(diff, 2)}% percentage points.")
        elif diff < -2.0:
            evidence.append(f"Operating margin contracted by {round(abs(diff), 2)}% percentage points.")

    # 4. ROCE / ROIC Expansion (Up to 20 pts)
    if len(roce_obs) >= 2:
        latest_roce = roce_obs[-1].value
        prev_roce = roce_obs[-2].value
        summary["roce"] = latest_roce
        
        if latest_roce >= 20.0:
            score += 12.0
            evidence.append(f"High capital efficiency with ROCE at {round(latest_roce, 1)}%.")
        elif latest_roce >= 15.0:
            score += 8.0
            
        if latest_roce > prev_roce:
            score += 8.0
            evidence.append(f"ROCE expanded from {round(prev_roce, 1)}% to {round(latest_roce, 1)}%.")
            
    # 5. FCF Cash Flow Inflection (Up to 15 pts)
    if len(fcf_obs) >= 2:
        latest_fcf = fcf_obs[-1].value
        prev_fcf = fcf_obs[-2].value
        summary["fcf"] = latest_fcf
        
        if prev_fcf <= 0 and latest_fcf > 0:
            score += 15.0
            evidence.append(f"FCF Inflection: Free Cash Flow turned positive ({latest_fcf} Cr).")
        elif latest_fcf > prev_fcf and latest_fcf > 0:
            score += 10.0
            evidence.append("Free Cash Flow expanding YoY.")
            
    final_score = min(100.0, round(score, 1))
    
    # Stage Classification
    total_data_points = len(rev_obs) + len(pat_obs) + len(margin_obs) + len(roce_obs)
    if total_data_points < 3:
        stage = "Insufficient Data"
        confidence = 30.0
    elif final_score >= 75.0:
        stage = "Early"
        confidence = 85.0
    elif final_score >= 55.0:
        stage = "Developing"
        confidence = 80.0
    elif final_score >= 40.0:
        stage = "Confirmed"
        confidence = 75.0
    else:
        stage = "Exhausting"
        confidence = 70.0
        
    return GrowthInflectionResponse(
        symbol=norm_symbol,
        executed_at=datetime.now().isoformat(),
        growth_inflection_score=final_score,
        stage=stage,
        heuristic_confidence=confidence,
        evidence=evidence or ["Baseline growth performance."],
        metrics_summary=summary,
        meta=create_meta_header(source="Growth Inflection Engine (E1)")
    )

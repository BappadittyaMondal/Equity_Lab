"""Scorecard Matrix Service — Gap Closure Feature 1.

Consolidates Arbiter pillar scores, Multibagger optionality metrics,
and Empirical Horizon Probabilities into a unified Scorecard presentation payload.
"""

import logging
from typing import List, Optional
from datetime import datetime

from app.models.schemas import (
    ScorecardItemResponse,
    ScorecardMatrixResponse,
    ScorecardScores,
    ScorecardProbabilities,
    ReturnProbabilityRequest,
)
from app.services.decision_brain.arbiter import Arbiter
from app.services.strategies.multibagger_screener import evaluate_multibagger_score
from app.services.probability import calculate_return_probability
from app.services.market_data import normalize_symbol, get_ist_now_str, create_meta_header

logger = logging.getLogger(__name__)

# Standard qualitative view tag mapping based on overall score & conviction
_TAG_MAP = [
    (85, "🚀 Highest asymmetric bet"),
    (75, "⭐ Dark horse / High growth compounder"),
    (65, "⭐ Best structural bet"),
    (55, "AI & Tech compounder"),
    (45, "Risk-adjusted leader"),
    (0,  "Watchlist candidate / High risk"),
]


def generate_scorecard_for_symbol(symbol: str, rank: Optional[int] = None) -> ScorecardItemResponse:
    """Generate consolidated ScorecardItemResponse for a single ticker."""
    norm = normalize_symbol(symbol)
    
    # 1. Arbiter arbitration
    arb = Arbiter()
    call = arb.arbitrate(norm)
    
    # 2. Multibagger evaluation
    try:
        mb = evaluate_multibagger_score(norm)
        mb_score = mb.multibagger_score
    except Exception as e:
        logger.warning("Multibagger score fallback for %s: %s", norm, e)
        mb_score = call.conviction_score * 0.9

    # 3. Independent Empirical Probability Matrix (No heuristic offset formulas)
    prob_1y = "N/A"
    prob_2y = "N/A"
    prob_3y = "N/A"
    prob_3y_2x = "N/A"
    prob_5y_15x = "N/A"
    prob_res = None
    try:
        req_1y = ReturnProbabilityRequest(symbol=norm, horizon_days=252, return_threshold_pct=10.0)
        prob_res = calculate_return_probability(req_1y)
        prob_1y = f"{round(prob_res.probability_above_threshold_pct)}%"

        try:
            req_2y = ReturnProbabilityRequest(symbol=norm, horizon_days=504, return_threshold_pct=20.0)
            res_2y = calculate_return_probability(req_2y)
            prob_2y = f"{round(res_2y.probability_above_threshold_pct)}%"
        except Exception:
            prob_2y = "N/A"

        try:
            req_3y = ReturnProbabilityRequest(symbol=norm, horizon_days=756, return_threshold_pct=30.0)
            res_3y = calculate_return_probability(req_3y)
            prob_3y = f"{round(res_3y.probability_above_threshold_pct)}%"
        except Exception:
            prob_3y = "N/A"

        try:
            req_2x = ReturnProbabilityRequest(symbol=norm, horizon_days=756, return_threshold_pct=100.0)
            res_2x = calculate_return_probability(req_2x)
            prob_3y_2x = f"{round(res_2x.probability_above_threshold_pct)}%"
        except Exception:
            prob_3y_2x = "N/A"

        try:
            req_15x = ReturnProbabilityRequest(symbol=norm, horizon_days=1260, return_threshold_pct=1400.0)
            res_15x = calculate_return_probability(req_15x)
            prob_5y_15x = f"{round(res_15x.probability_above_threshold_pct)}%"
        except Exception:
            prob_5y_15x = "N/A"
    except Exception as e:
        logger.warning("Probability calculation unavailable for %s: %s", norm, e)

    # Convert scores to /10 ratings
    bq_val = min(10.0, round(call.conviction_score * 0.1, 1))
    gp_val = min(10.0, round((call.conviction_score * 0.5 + mb_score * 0.5) * 0.1, 1))
    op_val = min(10.0, round(mb_score * 0.1, 1))

    # Empirical Risk Calculation (Independent from conviction score)
    downside_risk_pts = 2.0
    if prob_res and hasattr(prob_res, "probability_negative_return_pct"):
        downside_risk_pts = min(4.0, (prob_res.probability_negative_return_pct / 100.0) * 4.0)

    contradict_count = len(call.contradicting_engines) if call.contradicting_engines else 0
    contradict_pts = min(3.0, contradict_count * 0.75)
    verdict_penalty = 3.0 if call.verdict in ("Avoid", "ABSTAIN") else (1.5 if call.verdict == "Watch" else 0.5)

    rk_val = min(10.0, max(0.5, round(downside_risk_pts + contradict_pts + verdict_penalty, 1)))

    # Pick qualitative tag
    q_tag = "Risk-adjusted leader"
    for threshold, tag in _TAG_MAP:
        if call.conviction_score >= threshold:
            q_tag = tag
            break

    # Determine risk tier
    if call.verdict == "Avoid" or call.conviction_score < 40:
        r_tier = "Critical"
    elif call.conviction_score < 60:
        r_tier = "High"
    elif call.conviction_score < 80:
        r_tier = "Medium"
    else:
        r_tier = "Low"

    return ScorecardItemResponse(
        rank=rank,
        symbol=norm,
        company_name=norm,
        scores=ScorecardScores(
            business_quality=f"{bq_val}/10",
            growth_potential=f"{gp_val}/10",
            optionality_15x=f"{op_val}/10",
            risk_score=f"{rk_val}/10",
            overall_score=call.conviction_score,
        ),
        horizon_probabilities=ScorecardProbabilities(
            prob_1y=prob_1y,
            prob_2y=prob_2y,
            prob_3y=prob_3y,
            prob_3y_2x_plus=prob_3y_2x,
            prob_5y_15x=prob_5y_15x,
        ),
        qualitative_view=q_tag,
        risk_tier=r_tier,
        meta=create_meta_header(source=f"IERL Scorecard Engine ({norm})"),
    )


def generate_scorecard_matrix(symbols: List[str]) -> ScorecardMatrixResponse:
    """Generate side-by-side ScorecardMatrixResponse for a list of tickers sorted by score."""
    items: List[ScorecardItemResponse] = []
    for s in symbols:
        try:
            item = generate_scorecard_for_symbol(s)
            items.append(item)
        except Exception as e:
            logger.error("Failed to generate scorecard item for %s: %s", s, e)

    # Sort descending by overall score and assign ranks
    items.sort(key=lambda x: x.scores.overall_score, reverse=True)
    for idx, item in enumerate(items, 1):
        item.rank = idx

    return ScorecardMatrixResponse(
        items=items,
        count=len(items),
        executed_at=get_ist_now_str(),
        meta=create_meta_header(source="IERL Scorecard Matrix Engine"),
    )

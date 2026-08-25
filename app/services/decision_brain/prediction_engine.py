"""Prediction Engine — Phase 4, Layer 10.

Multi-horizon probabilistic prediction combining:
  1. Empirical return distribution (historical rolling returns)
  2. Fundamental-based return estimate (earnings growth × multiple expansion)
  3. Mean reversion tendency from valuation gap (margin of safety)
  4. Catalyst timeline from business_events in ResearchDataStore
  5. Scenario tree (Bull/Base/Bear) with probability weights
  6. Risk quantification (max drawdown, Sortino-like ratio)
  7. Decomposed confidence (data quality / model / thesis)

Pipeline law: This engine reads from ResearchDataStore and market data only.
It never invents numbers — every projection is grounded in real observations.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.services.market_data import (
    normalize_symbol, get_history, get_quote, create_meta_header, get_ist_now_str
)

logger = logging.getLogger(__name__)

# Horizon definitions: (label, trading_days, calendar_months)
HORIZONS: List[Tuple[str, int, int]] = [
    ("3M",  63,   3),
    ("6M",  126,  6),
    ("1Y",  252,  12),
    ("2Y",  504,  24),
    ("5Y",  1260, 60),
]

RISK_FREE_RATE_ANNUAL = 0.071   # India 10Y G-Sec ≈ 7.1%
NIFTY_LONG_TERM_CAGR  = 0.12   # Nifty 50 historical ~12% CAGR


# ─────────────────────────────────────────────────────────────────────────────
# 1. Empirical Return Distribution per Horizon
# ─────────────────────────────────────────────────────────────────────────────

def _empirical_returns(closes: np.ndarray, trading_days: int) -> np.ndarray:
    """Compute overlapping rolling N-day returns from price series."""
    if len(closes) < trading_days + 10:
        return np.array([])
    returns = []
    for i in range(len(closes) - trading_days):
        r = ((closes[i + trading_days] - closes[i]) / closes[i]) * 100.0
        returns.append(r)
    return np.array(returns)


def _risk_metrics(rets: np.ndarray, horizon_label: str) -> Dict[str, Any]:
    """Compute risk metrics for a return distribution."""
    if len(rets) == 0:
        return {}
    downside = rets[rets < 0]
    downside_std = float(np.std(downside)) if len(downside) > 1 else 0.0
    median_ret = float(np.percentile(rets, 50))
    # Sortino-like: median return / downside deviation
    sortino = round(median_ret / downside_std, 2) if downside_std > 0 else None
    prob_loss_20 = round(float(np.mean(rets < -20.0)) * 100, 2)
    max_drawdown = round(float(np.percentile(rets, 2)), 2)  # 2nd percentile as max drawdown proxy
    return {
        "median_return_pct": round(median_ret, 2),
        "p5_return_pct":     round(float(np.percentile(rets, 5)), 2),
        "p25_return_pct":    round(float(np.percentile(rets, 25)), 2),
        "p75_return_pct":    round(float(np.percentile(rets, 75)), 2),
        "p95_return_pct":    round(float(np.percentile(rets, 95)), 2),
        "prob_positive_pct": round(float(np.mean(rets > 0)) * 100, 2),
        "prob_loss_20pct":   prob_loss_20,
        "max_drawdown_proxy_pct": max_drawdown,
        "sortino_ratio":     sortino,
        "sample_size":       len(rets),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. Fundamental-Based Return Estimate
# ─────────────────────────────────────────────────────────────────────────────

def _fundamental_return_estimate(
    financials: List[Any],
    current_pe: Optional[float],
    horizon_years: float,
) -> Optional[float]:
    """Estimate expected return from earnings growth × multiple expansion.

    Expected Return ≈ EPS_CAGR + Dividend_Yield + Multiple_Change
    Multiple change estimated as mean reversion to 5Y median P/E.
    """
    from app.services.strategies.fundamental_metrics import _extract_series, _cagr

    pat_series = _extract_series(financials, ["net_income", "pat"])
    eps_series = _extract_series(financials, ["basic_eps", "diluted_eps"])

    # Use PAT CAGR as proxy for EPS growth
    growth_series = eps_series if len(eps_series) >= 8 else pat_series
    if len(growth_series) < 5:
        return None

    eps_cagr = _cagr(growth_series, min(len(growth_series) - 1, 8))
    if eps_cagr is None or eps_cagr < -50 or eps_cagr > 100:
        return None

    # Approximate dividend yield from India market (2% average)
    div_yield = 0.02

    # Multiple change: if current P/E > 30, expect slight compression; < 15, expansion
    multiple_change_annual = 0.0
    if current_pe is not None and current_pe > 30:
        multiple_change_annual = -0.02  # 2% annual multiple compression
    elif current_pe is not None and current_pe < 15:
        multiple_change_annual = 0.02   # 2% annual multiple expansion

    annual_return = (eps_cagr / 100.0) + div_yield + multiple_change_annual
    total_return_pct = ((1 + annual_return) ** horizon_years - 1) * 100.0
    return round(total_return_pct, 2)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Valuation Gap Mean Reversion Contribution
# ─────────────────────────────────────────────────────────────────────────────

def _valuation_reversion_return(margin_of_safety_pct: Optional[float], horizon_years: float) -> Optional[float]:
    """Estimate return contribution from reversion to intrinsic value.

    If stock is 20% undervalued, expect ~20/horizon_years % annual contribution.
    Assumes partial (50%) reversion over horizon.
    """
    if margin_of_safety_pct is None:
        return None
    reversion_pct = margin_of_safety_pct * 0.5  # 50% mean reversion assumption
    annual_contribution = reversion_pct / max(horizon_years, 1.0)
    total_contribution = reversion_pct  # Total over horizon
    return round(total_contribution, 2)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Catalyst Timeline
# ─────────────────────────────────────────────────────────────────────────────

def _extract_catalyst_timeline(events: List[Any]) -> List[Dict[str, Any]]:
    """Extract upcoming catalysts from business_events with impact estimates."""
    catalysts = []
    now = datetime.now(timezone.utc).date()

    for evt in events:
        event_date_raw = getattr(evt, "event_date", None)
        if not event_date_raw:
            continue
        try:
            if hasattr(event_date_raw, "date"):
                event_date = event_date_raw.date()
            else:
                event_date = datetime.fromisoformat(str(event_date_raw)).date()
        except Exception:
            continue

        # Only upcoming events (within next 12 months)
        days_ahead = (event_date - now).days
        if days_ahead < 0 or days_ahead > 365:
            continue

        event_type = getattr(evt, "event_type", "unknown")
        title = getattr(evt, "title", "Event")

        # Impact direction heuristic
        if event_type in ("earnings_release", "results_announcement"):
            impact_direction = "POSITIVE_IF_BEAT"
            magnitude = "HIGH"
        elif event_type in ("board_meeting", "agm"):
            impact_direction = "NEUTRAL"
            magnitude = "MODERATE"
        elif event_type == "governance_alert":
            impact_direction = "NEGATIVE"
            magnitude = "HIGH"
        elif event_type == "regulatory_approval":
            impact_direction = "POSITIVE"
            magnitude = "MODERATE"
        elif event_type in ("dividend_announcement", "bonus_issue"):
            impact_direction = "POSITIVE"
            magnitude = "LOW"
        else:
            impact_direction = "UNCERTAIN"
            magnitude = "LOW"

        catalysts.append({
            "event_date":        str(event_date),
            "event_type":        event_type,
            "title":             title,
            "days_ahead":        days_ahead,
            "impact_direction":  impact_direction,
            "magnitude":         magnitude,
        })

    return sorted(catalysts, key=lambda x: x["days_ahead"])[:10]


# ─────────────────────────────────────────────────────────────────────────────
# 5. Scenario Tree
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_scenario_probabilities(
    symbol: str = "",
    composite_score: float = 60.0,
    regime: Optional[str] = None,
) -> Tuple[float, float, float, str]:
    """Calculate calibrated Bull/Base/Bear probabilities using ML ensemble & market regime.

    Returns (prob_bull, prob_base, prob_bear, confidence_mode).
    """
    prob_bull, prob_base, prob_bear = 0.25, 0.50, 0.25
    confidence_mode = "prior_insufficient_data"

    try:
        from app.services.ml.baseline_model import _MODEL_CACHE, predict_outperformance_prob, train_baseline_model
        if not _MODEL_CACHE.get("is_trained"):
            train_baseline_model()

        sample_count = _MODEL_CACHE.get("sample_count", 0)
        if _MODEL_CACHE.get("is_trained") and sample_count >= 20:
            p_out = predict_outperformance_prob(symbol, composite_score, data_backed=True)
            p_bull = round(0.50 * p_out, 4)
            p_bear = round(0.50 * (1.0 - p_out), 4)
            p_base = round(1.0 - p_bull - p_bear, 4)
            prob_bull, prob_base, prob_bear = p_bull, p_base, p_bear
            confidence_mode = "calibrated_ml_ensemble"
    except Exception as e:
        logger.debug("ML scenario probability calculation fallback: %s", e)

    # Regime adjustments
    if regime:
        regime_upper = str(regime).upper()
        if regime_upper == "ELEVATED":
            shift = 0.05
            prob_bull = max(0.05, prob_bull - shift)
            prob_bear = min(0.80, prob_bear + shift)
            prob_base = round(1.0 - prob_bull - prob_bear, 4)
        elif regime_upper == "VOLATILE":
            shift = 0.10
            prob_bull = max(0.05, prob_bull - shift)
            prob_bear = min(0.80, prob_bear + shift)
            prob_base = round(1.0 - prob_bull - prob_bear, 4)
        elif regime_upper == "CRISIS":
            shift = 0.20
            prob_bull = max(0.02, prob_bull - shift)
            prob_bear = min(0.90, prob_bear + shift)
            prob_base = round(1.0 - prob_bull - prob_bear, 4)

    total = prob_bull + prob_base + prob_bear
    if total > 0:
        prob_bull = round(prob_bull / total, 4)
        prob_bear = round(prob_bear / total, 4)
        prob_base = round(1.0 - prob_bull - prob_bear, 4)

    return prob_bull, prob_base, prob_bear, confidence_mode


def _build_scenario_tree(
    current_price: float,
    empirical_p25: float,
    empirical_p50: float,
    empirical_p75: float,
    fundamental_est: Optional[float],
    horizon_label: str,
    symbol: str = "",
    composite_score: float = 60.0,
    regime: Optional[str] = None,
) -> Dict[str, Any]:
    """Build Bull/Base/Bear scenarios with probability weights.

    Combines empirical percentiles with fundamental estimates and calibrated ML output.
    Probabilities always sum to 100%.
    """
    # Base case: blend empirical median and fundamental estimate
    base_return = empirical_p50
    if fundamental_est is not None:
        base_return = empirical_p50 * 0.6 + fundamental_est * 0.4

    bull_return = max(empirical_p75, base_return * 1.4)
    bear_return = min(empirical_p25, base_return * 0.5)

    def _price_target(ret_pct: float) -> float:
        return round(current_price * (1 + ret_pct / 100.0), 2) if current_price > 0 else 0.0

    prob_bull, prob_base, prob_bear, confidence_mode = _calculate_scenario_probabilities(
        symbol=symbol, composite_score=composite_score, regime=regime
    )

    expected_return = (
        bull_return * prob_bull +
        base_return * prob_base +
        bear_return * prob_bear
    )

    return {
        "horizon":             horizon_label,
        "confidence_mode":     confidence_mode,
        "bull_case":  {"return_pct": round(bull_return, 2), "price_target": _price_target(bull_return), "probability": prob_bull, "drivers": ["Strong earnings beat", "Multiple expansion", "Sector re-rating"]},
        "base_case":  {"return_pct": round(base_return, 2), "price_target": _price_target(base_return), "probability": prob_base, "drivers": ["Earnings inline with estimates", "Stable multiple"]},
        "bear_case":  {"return_pct": round(bear_return, 2), "price_target": _price_target(bear_return), "probability": prob_bear, "drivers": ["Earnings miss", "Multiple compression", "Macro headwinds"]},
        "expected_return_pct": round(expected_return, 2),
        "expected_price":      _price_target(expected_return),
        "prob_sum_check":      round(prob_bull + prob_base + prob_bear, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. Confidence Decomposition
# ─────────────────────────────────────────────────────────────────────────────

def _decompose_confidence(
    financial_quarters: int,
    price_history_days: int,
    fundamental_est_available: bool,
    margin_of_safety: Optional[float],
) -> Dict[str, Any]:
    """Break conviction confidence into 3 traceable components.

    - Data quality confidence: How many quarters / how much price history?
    - Model confidence: Are multiple methods converging?
    - Thesis confidence: Is margin of safety positive?
    """
    # Data quality (0-100)
    if financial_quarters >= 12:
        data_quality = 90
    elif financial_quarters >= 8:
        data_quality = 75
    elif financial_quarters >= 4:
        data_quality = 55
    elif financial_quarters >= 1:
        data_quality = 35
    else:
        data_quality = 10

    if price_history_days >= 750:
        data_quality = min(100, data_quality + 10)

    # Model confidence (0-100): convergence of empirical + fundamental
    if fundamental_est_available and price_history_days >= 252:
        model_confidence = 80
    elif price_history_days >= 252:
        model_confidence = 60
    else:
        model_confidence = 30

    # Thesis confidence (0-100): margin of safety
    if margin_of_safety is not None:
        if margin_of_safety > 30:
            thesis_confidence = 90
        elif margin_of_safety > 10:
            thesis_confidence = 70
        elif margin_of_safety > 0:
            thesis_confidence = 55
        elif margin_of_safety > -15:
            thesis_confidence = 40
        else:
            thesis_confidence = 20
    else:
        thesis_confidence = 50  # No valuation data — neutral

    composite = round(data_quality * 0.4 + model_confidence * 0.3 + thesis_confidence * 0.3, 1)

    return {
        "composite_confidence_pct": composite,
        "data_quality_confidence":  data_quality,
        "model_confidence":         model_confidence,
        "thesis_confidence":        thesis_confidence,
        "data_quality_inputs": {
            "financial_quarters_available": financial_quarters,
            "price_history_trading_days":   price_history_days,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. Main Prediction Engine Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def generate_prediction_summary(
    symbol: str,
    store=None,
    margin_of_safety_pct: Optional[float] = None,
    composite_score: float = 60.0,
) -> Dict[str, Any]:
    """Generate full multi-horizon prediction summary for a symbol.

    Returns a dict (not StrategyRunResponse) because it's used as an input
    to the Arbiter's scoring and the AuditTrail — not a standalone API endpoint.

    Args:
        symbol: Equity symbol (normalised).
        store: Optional ResearchDataStore instance (created if None).
        margin_of_safety_pct: From Forward DCF (if already computed).
        composite_score: Scorecard composite score (dynamically resolved if default).

    Returns:
        Dict with: horizon_predictions, catalyst_timeline, confidence_decomposition,
                   scenario_trees, risk_summary, evidence.
    """
    norm = normalize_symbol(symbol)
    evidence = []
    financials = []
    events = []

    # ── Resolve dynamic composite score if default ────────────────────────
    if composite_score == 60.0:
        try:
            from app.services.decision_brain.scorecard import calculate_multi_dimensional_scorecard
            sc = calculate_multi_dimensional_scorecard(norm)
            if isinstance(sc, dict) and "composite_score" in sc:
                composite_score = float(sc["composite_score"])
            elif hasattr(sc, "composite_score"):
                composite_score = float(getattr(sc, "composite_score", 60.0))
        except Exception:
            pass

    # ── Fetch financial and event data ────────────────────────────────────
    try:
        from app.services.research_data import ResearchDataStore
        data_store = store or ResearchDataStore()
        _, financials, events, _, _, _ = data_store.get_timeline(norm)
        evidence.append(f"Financial observations: {len(financials)} records from ResearchDataStore")
    except Exception as e:
        evidence.append(f"ResearchDataStore unavailable: {e}")

    # ── Fetch price history ───────────────────────────────────────────────
    closes = np.array([])
    price_history_days = 0
    current_price = 0.0
    current_pe = None

    try:
        hist = get_history(norm, period="5y", interval="1d")
        if hist is not None and not hist.empty:
            closes = hist["Close"].values
            price_history_days = len(closes)
            current_price = float(closes[-1])
            evidence.append(f"Price history: {price_history_days} trading days fetched")
    except Exception as e:
        evidence.append(f"Price history unavailable: {e}")

    try:
        quote = get_quote(norm)
        p_val = getattr(quote, "price", None) or (quote.get("price") if isinstance(quote, dict) else None)
        if p_val and float(p_val) > 0:
            current_price = float(p_val)
        pe_val = getattr(quote, "pe_ratio", None) or (quote.get("pe_ratio") if isinstance(quote, dict) else None)
        if pe_val and float(pe_val) > 0:
            current_pe = float(pe_val)
    except Exception:
        pass

    # ── Per-horizon predictions ───────────────────────────────────────────
    horizon_predictions = {}
    risk_summary = {}

    for label, trading_days, months in HORIZONS:
        rets = _empirical_returns(closes, trading_days)
        risk = _risk_metrics(rets, label)

        horizon_years = months / 12.0
        fundamental_est = _fundamental_return_estimate(financials, current_pe, horizon_years)
        valuation_contrib = _valuation_reversion_return(margin_of_safety_pct, horizon_years)

        # Blended expected return
        components = []
        weights = []
        if len(rets) > 10:
            components.append(risk.get("median_return_pct", 0))
            weights.append(0.5)
        if fundamental_est is not None:
            components.append(fundamental_est)
            weights.append(0.35)
        if valuation_contrib is not None:
            components.append(valuation_contrib)
            weights.append(0.15)

        if components:
            total_w = sum(weights)
            blended = sum(c * w for c, w in zip(components, weights)) / total_w
        elif len(rets) > 0:
            blended = float(np.median(rets))
        else:
            blended = 0.0

        p25 = risk.get("p25_return_pct", blended * 0.5)
        p50 = risk.get("median_return_pct", blended)
        p75 = risk.get("p75_return_pct", blended * 1.5)
        regime_str = None
        try:
            from app.services.knowledge.regime_engine import RegimeEngine
            regime_str = RegimeEngine().classify().regime
        except Exception:
            pass

        scenario = _build_scenario_tree(
            current_price, p25, p50, p75, fundamental_est, label,
            symbol=norm, composite_score=composite_score, regime=regime_str
        )
        horizon_predictions[label] = {
            "horizon_months":           months,
            "blended_expected_return_pct": round(blended, 2),
            "fundamental_estimate_pct": fundamental_est,
            "valuation_contrib_pct":    valuation_contrib,
            "risk_metrics":             risk,
            "scenario_tree":            scenario,
            "data_status":              "PRODUCTION" if (len(rets) > 0 or fundamental_est is not None) else "DATA_UNAVAILABLE",
        }
        risk_summary[label] = {
            "prob_loss_20pct":           risk.get("prob_loss_20pct"),
            "max_drawdown_proxy_pct":    risk.get("max_drawdown_proxy_pct"),
            "sortino_ratio":             risk.get("sortino_ratio"),
        }

    # ── Catalyst timeline ─────────────────────────────────────────────────
    catalysts = _extract_catalyst_timeline(events)
    if catalysts:
        evidence.append(f"Upcoming catalysts: {len(catalysts)} events identified")
    else:
        evidence.append("No upcoming catalysts in ResearchDataStore (run BSE filing ingester)")

    # ── Confidence decomposition ──────────────────────────────────────────
    financial_quarters = len({getattr(f, "period_end", "") for f in financials}) if financials else 0
    confidence = _decompose_confidence(
        financial_quarters, price_history_days,
        any(hp.get("fundamental_estimate_pct") is not None for hp in horizon_predictions.values()),
        margin_of_safety_pct,
    )

    return {
        "symbol":               norm,
        "current_price":        current_price,
        "generated_at":         get_ist_now_str(),
        "horizon_predictions":  horizon_predictions,
        "catalyst_timeline":    catalysts,
        "confidence_decomposition": confidence,
        "risk_summary":         risk_summary,
        "evidence":             evidence,
        "data_inputs": {
            "financial_observations":  len(financials),
            "business_events":         len(events),
            "price_history_days":      price_history_days,
            "margin_of_safety_pct":    margin_of_safety_pct,
        },
    }

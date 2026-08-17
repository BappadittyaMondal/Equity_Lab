"""Fundamental Metrics Library — Phase 2, Layer 4.

Provides deterministic calculation functions for all institutional-grade
fundamental metrics. Used by E1/E2/E3/E4 engines and the Arbiter.

All functions accept lists of financial observations from ResearchDataStore
and return computed metrics with evidence strings. No synthetic fallbacks.
"""

from typing import Any, Dict, List, Optional, Tuple
import statistics


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def _extract_series(
    observations: List[Any], metric_names: List[str]
) -> List[Tuple[str, float]]:
    """Extract (period_end, value) pairs for a list of metric name aliases."""
    obs = [o for o in observations if o.metric in metric_names]
    obs.sort(key=lambda x: str(x.period_end))
    return [(str(o.period_end), float(o.value)) for o in obs]


def _pct_change(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100.0


def _yoy_growth(series: List[Tuple[str, float]], lag: int = 4) -> Optional[float]:
    """Compute YoY % change comparing latest to 4-quarters-ago."""
    if len(series) < lag + 1:
        return None
    return _pct_change(series[-1][1], series[-lag - 1][1])


def _cagr(series: List[Tuple[str, float]], periods: int) -> Optional[float]:
    """Compound annual growth rate over `periods` quarters (n/4 years)."""
    if len(series) < periods + 1:
        return None
    start = series[-(periods + 1)][1]
    end = series[-1][1]
    if start <= 0 or end <= 0:
        return None
    years = periods / 4.0
    return ((end / start) ** (1.0 / years) - 1.0) * 100.0


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 Metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_revenue_metrics(financials: List[Any]) -> Dict[str, Any]:
    """Revenue growth: QoQ, YoY, 3Y CAGR, acceleration flag."""
    series = _extract_series(financials, ["revenue", "total_revenue", "operating_revenue"])
    if not series:
        return {"status": "no_data", "evidence": []}

    evidence = []
    result: Dict[str, Any] = {}

    if len(series) >= 2:
        qoq = _pct_change(series[-1][1], series[-2][1])
        result["revenue_qoq_pct"] = round(qoq, 2) if qoq is not None else None

    yoy = _yoy_growth(series)
    if yoy is not None:
        result["revenue_yoy_pct"] = round(yoy, 2)
        label = f"Revenue YoY: {yoy:+.1f}%  [{series[-5][0] if len(series)>4 else '?'} → {series[-1][0]}]"
        evidence.append(label)

    cagr_12q = _cagr(series, 12)
    if cagr_12q is not None:
        result["revenue_3y_cagr_pct"] = round(cagr_12q, 2)
        evidence.append(f"Revenue 3Y CAGR: {cagr_12q:.1f}%")

    # Acceleration: latest YoY > prior YoY
    if len(series) >= 6:
        prior_yoy = _pct_change(series[-5][1], series[-6][1]) if len(series) >= 6 else None
        if prior_yoy is not None and yoy is not None:
            result["revenue_accelerating"] = yoy > prior_yoy
            if yoy > prior_yoy:
                evidence.append(
                    f"Revenue growth ACCELERATING: {prior_yoy:.1f}% → {yoy:.1f}%"
                )

    result["evidence"] = evidence
    result["latest_revenue"] = series[-1][1]
    result["latest_period"] = series[-1][0]
    return result


def compute_profitability_metrics(financials: List[Any]) -> Dict[str, Any]:
    """PAT, operating margin, EBITDA margin, earnings quality."""
    result: Dict[str, Any] = {}
    evidence = []

    # Net income / PAT
    pat_series = _extract_series(financials, ["net_income", "pat", "net_income_common_stockholders"])
    if len(pat_series) >= 2:
        yoy = _yoy_growth(pat_series)
        if yoy is not None:
            result["pat_yoy_pct"] = round(yoy, 2)
            evidence.append(f"PAT YoY: {yoy:+.1f}%")
        cagr = _cagr(pat_series, 12)
        if cagr is not None:
            result["pat_3y_cagr_pct"] = round(cagr, 2)

    # Operating margin (if stored as ratio)
    margin_series = _extract_series(financials, ["operating_margin", "operating_income"])
    rev_series = _extract_series(financials, ["revenue", "total_revenue"])
    if margin_series and rev_series and len(margin_series) >= 2:
        # If operating_income, compute margin
        if margin_series[-1][1] > 5.0:  # likely operating income value, not %
            if rev_series and rev_series[-1][1] > 0:
                margin_pct = (margin_series[-1][1] / rev_series[-1][1]) * 100.0
                prev_margin_pct = (margin_series[-2][1] / rev_series[-2][1]) * 100.0 if rev_series[-2][1] > 0 else margin_pct
                result["operating_margin_pct"] = round(margin_pct, 2)
                diff = margin_pct - prev_margin_pct
                result["margin_expansion_pct"] = round(diff, 2)
                if diff > 1.0:
                    evidence.append(f"Operating margin expanding: {prev_margin_pct:.1f}% → {margin_pct:.1f}% (+{diff:.1f}bps)")
                elif diff < -1.0:
                    evidence.append(f"Operating margin contracting: {prev_margin_pct:.1f}% → {margin_pct:.1f}% ({diff:.1f}bps)")

    # Margin stability (std dev over last 8 quarters)
    if len(margin_series) >= 4:
        recent_margins = [v for _, v in margin_series[-8:]]
        if all(v > 5.0 for v in recent_margins) and rev_series:
            # Compute as pct if values are absolute
            pass  # already handled above
        stability = statistics.stdev(recent_margins) if len(recent_margins) >= 2 else 0.0
        result["margin_stability_stddev"] = round(stability, 2)

    result["evidence"] = evidence
    return result


def compute_balance_sheet_metrics(financials: List[Any]) -> Dict[str, Any]:
    """D/E ratio, working capital trend, net debt."""
    result: Dict[str, Any] = {}
    evidence = []

    debt_series = _extract_series(financials, ["total_debt", "net_debt"])
    equity_series = _extract_series(financials, ["total_equity", "stockholders_equity"])
    wc_series = _extract_series(financials, ["working_capital"])

    if debt_series and equity_series:
        latest_debt = debt_series[-1][1]
        latest_equity = equity_series[-1][1]
        if latest_equity > 0:
            de_ratio = round(latest_debt / latest_equity, 2)
            result["de_ratio"] = de_ratio
            if de_ratio < 0.3:
                evidence.append(f"Strong balance sheet: D/E = {de_ratio}x (debt-free / low debt)")
            elif de_ratio < 1.0:
                evidence.append(f"Moderate leverage: D/E = {de_ratio}x")
            else:
                evidence.append(f"High leverage: D/E = {de_ratio}x — monitor carefully")

        # Trend: is debt declining?
        if len(debt_series) >= 4:
            debt_trend = _pct_change(debt_series[-1][1], debt_series[-4][1])
            if debt_trend is not None:
                result["debt_change_4q_pct"] = round(debt_trend, 2)
                if debt_trend < -10.0:
                    evidence.append(f"Debt declining: {debt_trend:.1f}% over past year (deleveraging)")
                elif debt_trend > 20.0:
                    evidence.append(f"Debt rising sharply: +{debt_trend:.1f}% — flag for investigation")

    if wc_series and len(wc_series) >= 2:
        wc_change = _pct_change(wc_series[-1][1], wc_series[-2][1])
        if wc_change is not None:
            result["working_capital_change_pct"] = round(wc_change, 2)

    result["evidence"] = evidence
    return result


def compute_cashflow_metrics(financials: List[Any]) -> Dict[str, Any]:
    """FCF, CFO/PAT earnings quality, capital expenditure."""
    result: Dict[str, Any] = {}
    evidence = []

    cfo_series = _extract_series(financials, ["operating_cash_flow", "cfo"])
    fcf_series = _extract_series(financials, ["free_cash_flow", "fcf"])
    pat_series = _extract_series(financials, ["net_income", "pat"])
    capex_series = _extract_series(financials, ["capital_expenditure"])

    # Earnings quality: CFO / PAT
    if cfo_series and pat_series:
        cfo = cfo_series[-1][1]
        pat = pat_series[-1][1]
        if pat > 0 and cfo != 0:
            quality_ratio = round(cfo / pat, 2)
            result["earnings_quality_ratio"] = quality_ratio
            if quality_ratio >= 1.0:
                evidence.append(f"High earnings quality: CFO/PAT = {quality_ratio}x (cash-backed profit)")
            elif quality_ratio >= 0.7:
                evidence.append(f"Adequate earnings quality: CFO/PAT = {quality_ratio}x")
            elif quality_ratio < 0:
                evidence.append(f"EARNINGS QUALITY RISK: Positive PAT but negative CFO (ratio={quality_ratio}x)")
            else:
                evidence.append(f"Low earnings quality: CFO/PAT = {quality_ratio}x")

    # FCF trend
    if fcf_series and len(fcf_series) >= 2:
        latest_fcf = fcf_series[-1][1]
        prev_fcf = fcf_series[-2][1]
        result["latest_fcf"] = latest_fcf
        if prev_fcf <= 0 < latest_fcf:
            evidence.append("FCF INFLECTION: Free Cash Flow turned positive")
        elif latest_fcf > prev_fcf > 0:
            growth = _pct_change(latest_fcf, prev_fcf)
            evidence.append(f"FCF growing: {growth:.1f}% QoQ")
        elif latest_fcf < 0:
            evidence.append(f"Negative FCF: {latest_fcf:,.0f} — company is cash-consuming")

    result["evidence"] = evidence
    return result


def compute_dupont_roe(financials: List[Any]) -> Dict[str, Any]:
    """DuPont ROE decomposition: Net Margin × Asset Turnover × Equity Multiplier."""
    result: Dict[str, Any] = {}
    evidence = []

    pat_series = _extract_series(financials, ["net_income", "pat"])
    rev_series = _extract_series(financials, ["revenue", "total_revenue"])
    asset_series = _extract_series(financials, ["total_assets"])
    equity_series = _extract_series(financials, ["total_equity"])

    if not (pat_series and rev_series and asset_series and equity_series):
        return {"status": "insufficient_data", "evidence": []}

    pat = pat_series[-1][1]
    rev = rev_series[-1][1]
    assets = asset_series[-1][1]
    equity = equity_series[-1][1]

    if rev > 0 and assets > 0 and equity > 0:
        net_margin = pat / rev
        asset_turnover = rev / assets
        equity_multiplier = assets / equity
        roe = net_margin * asset_turnover * equity_multiplier * 100.0

        result["roe_pct"] = round(roe, 2)
        result["net_margin_pct"] = round(net_margin * 100, 2)
        result["asset_turnover"] = round(asset_turnover, 2)
        result["equity_multiplier"] = round(equity_multiplier, 2)

        evidence.append(
            f"DuPont ROE: {roe:.1f}% = "
            f"Margin {net_margin*100:.1f}% × Turnover {asset_turnover:.2f}x × Leverage {equity_multiplier:.2f}x"
        )

    result["evidence"] = evidence
    return result


def compute_fundamental_quality_score(financials: List[Any]) -> Dict[str, Any]:
    """
    Composite FundamentalQualityScore (0–100) from 4 pillars:
      1. Earnings quality (CFO/PAT)      — 30 pts
      2. Growth trajectory               — 30 pts
      3. Balance sheet strength (D/E)    — 20 pts
      4. Capital efficiency (ROCE trend) — 20 pts
    """
    score = 0.0
    evidence = []

    # --- Pillar 1: Earnings quality ---
    cf_metrics = compute_cashflow_metrics(financials)
    eq = cf_metrics.get("earnings_quality_ratio")
    if eq is not None:
        if eq >= 1.2:
            score += 30
            evidence.append(f"P1 Earnings quality: EXCELLENT (CFO/PAT={eq}x) → 30/30")
        elif eq >= 0.8:
            score += 20
            evidence.append(f"P1 Earnings quality: GOOD (CFO/PAT={eq}x) → 20/30")
        elif eq >= 0.5:
            score += 10
            evidence.append(f"P1 Earnings quality: MODERATE (CFO/PAT={eq}x) → 10/30")
        else:
            evidence.append(f"P1 Earnings quality: POOR (CFO/PAT={eq}x) → 0/30")
    else:
        evidence.append("P1 Earnings quality: no CFO data → 0/30")

    # --- Pillar 2: Revenue growth ---
    rev_metrics = compute_revenue_metrics(financials)
    yoy = rev_metrics.get("revenue_yoy_pct")
    if yoy is not None:
        if yoy > 25:
            score += 30
            evidence.append(f"P2 Revenue growth: {yoy:.1f}% YoY → 30/30")
        elif yoy > 15:
            score += 22
            evidence.append(f"P2 Revenue growth: {yoy:.1f}% YoY → 22/30")
        elif yoy > 8:
            score += 15
            evidence.append(f"P2 Revenue growth: {yoy:.1f}% YoY → 15/30")
        elif yoy > 0:
            score += 8
            evidence.append(f"P2 Revenue growth: {yoy:.1f}% YoY → 8/30")
        else:
            evidence.append(f"P2 Revenue declining: {yoy:.1f}% YoY → 0/30")
    else:
        evidence.append("P2 Revenue: insufficient quarters → 0/30")

    # --- Pillar 3: Balance sheet ---
    bs_metrics = compute_balance_sheet_metrics(financials)
    de = bs_metrics.get("de_ratio")
    if de is not None:
        if de < 0.3:
            score += 20
            evidence.append(f"P3 Balance sheet: STRONG (D/E={de}x) → 20/20")
        elif de < 0.7:
            score += 14
            evidence.append(f"P3 Balance sheet: MODERATE (D/E={de}x) → 14/20")
        elif de < 1.5:
            score += 8
            evidence.append(f"P3 Balance sheet: HIGH DEBT (D/E={de}x) → 8/20")
        else:
            evidence.append(f"P3 Balance sheet: LEVERAGED (D/E={de}x) → 0/20")
    else:
        evidence.append("P3 Balance sheet: no data → 0/20")

    # --- Pillar 4: ROCE trend ---
    roce_series = _extract_series(financials, ["roce", "roic", "return_on_assets"])
    if len(roce_series) >= 2:
        latest_roce = roce_series[-1][1]
        prev_roce = roce_series[-2][1]
        if latest_roce >= 20 and latest_roce > prev_roce:
            score += 20
            evidence.append(f"P4 ROCE: HIGH & IMPROVING ({prev_roce:.1f}% → {latest_roce:.1f}%) → 20/20")
        elif latest_roce >= 15:
            score += 14
            evidence.append(f"P4 ROCE: ADEQUATE ({latest_roce:.1f}%) → 14/20")
        elif latest_roce > 0:
            score += 7
            evidence.append(f"P4 ROCE: LOW ({latest_roce:.1f}%) → 7/20")
        else:
            evidence.append(f"P4 ROCE: NEGATIVE ({latest_roce:.1f}%) → 0/20")
    else:
        evidence.append("P4 ROCE: no data → 0/20")

    return {
        "fundamental_quality_score": round(min(100.0, score), 1),
        "evidence": evidence,
        "pillars": {
            "earnings_quality_score": min(30, score) if eq else 0,
            "data_quality": "real" if (yoy is not None or de is not None) else "none",
        }
    }

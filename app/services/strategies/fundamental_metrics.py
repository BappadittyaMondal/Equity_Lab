"""Fundamental Metrics Library — Phase 2 & 6, Layer 4.

Provides deterministic calculation functions for all institutional-grade
fundamental metrics. Used by E1/E2/E3/E4/E6 engines and the Arbiter.

All functions accept lists of financial observations from ResearchDataStore
and return computed metrics with evidence strings. No synthetic fallbacks.
"""

from typing import Any, Dict, List, Optional, Tuple
import statistics
from app.services.utils.math import calculate_cagr


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def _extract_series(
    observations: List[Any], metric_names: List[str]
) -> List[Tuple[str, float]]:
    """Extract (period_end, value) pairs for a list of metric name aliases."""
    obs = [o for o in observations if getattr(o, "metric", "").lower() in [m.lower() for m in metric_names]]
    obs.sort(key=lambda x: str(getattr(x, "period_end", "")))
    return [(str(getattr(o, "period_end", "")), float(getattr(o, "value", 0.0))) for o in obs]


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
    years = periods / 4.0
    return calculate_cagr(start, end, years)


# ─────────────────────────────────────────────────────────────────────────────
# Core Layer 4 Metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_revenue_metrics(financials: List[Any]) -> Dict[str, Any]:
    """Revenue growth: QoQ, YoY, 3Y CAGR, acceleration flag."""
    series = _extract_series(financials, ["revenue", "total_revenue", "operating_revenue"])
    if not series:
        return {"status": "DATA_UNAVAILABLE", "evidence": ["DATA_UNAVAILABLE: No revenue series found."]}

    evidence = []
    result: Dict[str, Any] = {"status": "PRODUCTION"}

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
    result: Dict[str, Any] = {"status": "PRODUCTION"}
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

    # Operating margin
    margin_series = _extract_series(financials, ["operating_margin", "operating_income"])
    rev_series = _extract_series(financials, ["revenue", "total_revenue"])
    if margin_series and rev_series and len(margin_series) >= 2:
        if margin_series[-1][1] > 5.0:
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

    if len(margin_series) >= 4:
        recent_margins = [v for _, v in margin_series[-8:]]
        stability = statistics.stdev(recent_margins) if len(recent_margins) >= 2 else 0.0
        result["margin_stability_stddev"] = round(stability, 2)

    if not pat_series and not margin_series:
        return {"status": "DATA_UNAVAILABLE", "evidence": ["DATA_UNAVAILABLE: Insufficient profitability observation data."]}

    result["evidence"] = evidence
    return result


def compute_balance_sheet_metrics(financials: List[Any]) -> Dict[str, Any]:
    """D/E ratio, working capital trend, net debt."""
    result: Dict[str, Any] = {"status": "PRODUCTION"}
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

    if not debt_series and not equity_series and not wc_series:
        return {"status": "DATA_UNAVAILABLE", "evidence": ["DATA_UNAVAILABLE: Balance sheet observations unavailable."]}

    result["evidence"] = evidence
    return result


def compute_cashflow_metrics(financials: List[Any]) -> Dict[str, Any]:
    """FCF, CFO/PAT earnings quality, capital expenditure."""
    result: Dict[str, Any] = {"status": "PRODUCTION"}
    evidence = []

    cfo_series = _extract_series(financials, ["operating_cash_flow", "cfo"])
    fcf_series = _extract_series(financials, ["free_cash_flow", "fcf"])
    pat_series = _extract_series(financials, ["net_income", "pat"])

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

    if not cfo_series and not fcf_series:
        return {"status": "DATA_UNAVAILABLE", "evidence": ["DATA_UNAVAILABLE: Cash flow observations unavailable."]}

    result["evidence"] = evidence
    return result


def compute_working_capital_turnover(financials: List[Any]) -> Dict[str, Any]:
    """Working Capital Turnover = Revenue / Working Capital."""
    rev_series = _extract_series(financials, ["revenue", "total_revenue", "operating_revenue"])
    wc_series = _extract_series(financials, ["working_capital"])

    if not rev_series or not wc_series:
        return {"status": "DATA_UNAVAILABLE", "working_capital_turnover": None, "evidence": ["DATA_UNAVAILABLE: Revenue or Working Capital missing."]}

    rev = rev_series[-1][1]
    wc = wc_series[-1][1]

    if wc <= 0:
        return {
            "status": "PRODUCTION",
            "working_capital_turnover": None,
            "evidence": [f"Working Capital is non-positive ({wc:,.2f}); turnover ratio not defined."]
        }

    turnover = round(rev / wc, 2)
    return {
        "status": "PRODUCTION",
        "working_capital_turnover": turnover,
        "evidence": [f"Working Capital Turnover: {turnover:.2f}x (Revenue ₹{rev:,.0f} / WC ₹{wc:,.0f})"]
    }


def compute_roic_wacc_spread(financials: List[Any], wacc: float = 11.5) -> Dict[str, Any]:
    """ROIC vs Cost of Capital (WACC) Spread = ROIC (%) - WACC (%)."""
    roic_series = _extract_series(financials, ["roic", "roce", "return_on_capital_employed"])

    if not roic_series:
        return {"status": "DATA_UNAVAILABLE", "spread_pct": None, "evidence": ["DATA_UNAVAILABLE: ROIC/ROCE observations missing."]}

    roic = roic_series[-1][1]
    spread = round(roic - wacc, 2)

    return {
        "status": "PRODUCTION",
        "roic_pct": round(roic, 2),
        "wacc_pct": round(wacc, 2),
        "spread_pct": spread,
        "value_creating": spread > 0,
        "evidence": [f"ROIC vs WACC Spread: {spread:+.2f}% points (ROIC {roic:.1f}% vs Cost of Capital {wacc:.1f}%)"]
    }


def compute_incremental_roic(financials: List[Any], periods: int = 4) -> Dict[str, Any]:
    """Incremental ROIC = ΔNOPAT / ΔInvested Capital over `periods` quarters.

    Answers the institutional super-factor question:
    What return is the company generating on the NEW capital it is investing today?
    """
    nopat_series = _extract_series(financials, ["nopat", "operating_income", "ebit", "net_income"])
    ic_series = _extract_series(financials, ["invested_capital", "total_equity", "total_assets"])

    if len(nopat_series) < 2 or len(ic_series) < 2:
        return {
            "status": "DATA_UNAVAILABLE",
            "incremental_roic_pct": None,
            "reinvestment_rate_pct": None,
            "evidence": ["DATA_UNAVAILABLE: Insufficient observations to compute ΔNOPAT and ΔInvested Capital."]
        }

    # Match latest and comparison periods
    latest_nopat = nopat_series[-1][1]
    prev_nopat = nopat_series[-min(periods + 1, len(nopat_series))][1]
    delta_nopat = latest_nopat - prev_nopat

    latest_ic = ic_series[-1][1]
    prev_ic = ic_series[-min(periods + 1, len(ic_series))][1]
    delta_ic = latest_ic - prev_ic

    evidence = []
    if delta_ic <= 0:
        evidence.append(f"Invested capital static or contracting (ΔIC = ₹{delta_ic:,.0f}). Incremental ROIC not defined.")
        return {
            "status": "PRODUCTION",
            "incremental_roic_pct": None,
            "delta_nopat": round(delta_nopat, 2),
            "delta_invested_capital": round(delta_ic, 2),
            "reinvestment_rate_pct": 0.0,
            "evidence": evidence
        }

    inc_roic = round((delta_nopat / delta_ic) * 100.0, 2)
    reinvestment_rate = round((delta_ic / max(1.0, prev_nopat)) * 100.0, 2) if prev_nopat > 0 else 0.0

    if inc_roic > 25.0:
        evidence.append(f"SUPER-FACTOR HIGH INCREMENTAL ROIC: {inc_roic:+.1f}% (ΔNOPAT ₹{delta_nopat:,.0f} / ΔIC ₹{delta_ic:,.0f})")
    elif inc_roic > 15.0:
        evidence.append(f"Adequate Incremental ROIC: {inc_roic:+.1f}%")
    elif inc_roic < 0:
        evidence.append(f"DESTRUCTIVE REINVESTMENT: Negative Incremental ROIC ({inc_roic:+.1f}%)")
    else:
        evidence.append(f"Low Incremental ROIC: {inc_roic:+.1f}%")

    return {
        "status": "PRODUCTION",
        "incremental_roic_pct": inc_roic,
        "delta_nopat": round(delta_nopat, 2),
        "delta_invested_capital": round(delta_ic, 2),
        "reinvestment_rate_pct": reinvestment_rate,
        "evidence": evidence
    }



def compute_debt_ebitda(financials: List[Any]) -> Dict[str, Any]:
    """Debt / EBITDA Ratio."""
    debt_series = _extract_series(financials, ["total_debt", "net_debt"])
    ebitda_series = _extract_series(financials, ["ebitda", "operating_income"])

    if not debt_series or not ebitda_series:
        return {"status": "DATA_UNAVAILABLE", "debt_ebitda_ratio": None, "evidence": ["DATA_UNAVAILABLE: Debt or EBITDA observations missing."]}

    debt = debt_series[-1][1]
    ebitda = ebitda_series[-1][1]

    if ebitda <= 0:
        return {
            "status": "PRODUCTION",
            "debt_ebitda_ratio": None,
            "evidence": [f"EBITDA is non-positive ({ebitda:,.2f}); Debt/EBITDA not defined."]
        }

    ratio = round(debt / ebitda, 2)
    return {
        "status": "PRODUCTION",
        "debt_ebitda_ratio": ratio,
        "evidence": [f"Debt / EBITDA: {ratio:.2f}x (Total Debt ₹{debt:,.0f} / EBITDA ₹{ebitda:,.0f})"]
    }


def compute_ocf_yield(financials: List[Any], market_cap: Optional[float] = None) -> Dict[str, Any]:
    """Operating Cash Flow Yield = CFO / Market Capitalization."""
    cfo_series = _extract_series(financials, ["operating_cash_flow", "cfo"])

    if not cfo_series or market_cap is None or market_cap <= 0:
        return {"status": "DATA_UNAVAILABLE", "ocf_yield_pct": None, "evidence": ["DATA_UNAVAILABLE: CFO observations or Market Cap missing."]}

    cfo = cfo_series[-1][1]
    ocf_yield = round((cfo / market_cap) * 100.0, 2)

    return {
        "status": "PRODUCTION",
        "ocf_yield_pct": ocf_yield,
        "evidence": [f"Operating Cash Flow Yield: {ocf_yield:.2f}% (CFO ₹{cfo:,.0f} / Market Cap ₹{market_cap:,.0f})"]
    }


def compute_dupont_roe(financials: List[Any]) -> Dict[str, Any]:
    """DuPont ROE decomposition: 5-Stage (Tax Effect × Interest Burden × EBIT Margin × Asset Turnover × Financial Leverage) + DOL."""
    result: Dict[str, Any] = {"status": "PRODUCTION"}
    evidence = []

    pat_series = _extract_series(financials, ["net_income", "pat"])
    rev_series = _extract_series(financials, ["revenue", "total_revenue"])
    asset_series = _extract_series(financials, ["total_assets"])
    equity_series = _extract_series(financials, ["total_equity"])
    ebit_series = _extract_series(financials, ["ebit", "operating_income"])
    ebt_series = _extract_series(financials, ["ebt", "income_before_tax"])

    if not (pat_series and rev_series and asset_series and equity_series):
        return {"status": "DATA_UNAVAILABLE", "evidence": ["DATA_UNAVAILABLE: Insufficient observations for DuPont ROE."]}

    pat = pat_series[-1][1]
    rev = rev_series[-1][1]
    assets = asset_series[-1][1]
    equity = equity_series[-1][1]
    ebit = ebit_series[-1][1] if ebit_series else (ebt_series[-1][1] if ebt_series else pat)
    ebt = ebt_series[-1][1] if ebt_series else pat

    if rev > 0 and assets > 0 and equity > 0:
        net_margin = pat / rev
        asset_turnover = rev / assets
        equity_multiplier = assets / equity
        roe = net_margin * asset_turnover * equity_multiplier * 100.0

        # 5-Stage DuPont components
        from app.services.research.peer_normalization import compute_5_stage_dupont_and_dol
        prev_ebit = ebit_series[-2][1] if ebit_series and len(ebit_series) >= 2 else None
        prev_rev = rev_series[-2][1] if len(rev_series) >= 2 else None

        dupont_5stage = compute_5_stage_dupont_and_dol(
            net_income=pat,
            ebt=ebt,
            ebit=ebit,
            revenue=rev,
            total_assets=assets,
            equity=equity,
            prev_ebit=prev_ebit,
            prev_revenue=prev_rev
        )

        headline_roe = dupont_5stage.get("dupont_roe_pct", round(roe, 2))
        result["roe_pct"] = headline_roe
        result["net_margin_pct"] = round(net_margin * 100, 2)
        result["asset_turnover"] = round(asset_turnover, 2)
        result["equity_multiplier"] = round(equity_multiplier, 2)

        # 5-Stage & Operating Leverage Additions
        result["tax_effect"] = dupont_5stage.get("tax_effect", 1.0)
        result["interest_burden"] = dupont_5stage.get("interest_burden", 1.0)
        result["ebit_margin_pct"] = dupont_5stage.get("ebit_margin_pct", round((ebit / rev) * 100, 2) if rev > 0 else 0.0)
        result["degree_of_operating_leverage"] = dupont_5stage.get("degree_of_operating_leverage", 0.0)
        result["operating_leverage_tier"] = dupont_5stage.get("operating_leverage_tier", "LOW")

        evidence.append(
            f"DuPont ROE (5-Stage): {headline_roe:.1f}% = "
            f"Tax {result['tax_effect']} × IntBurden {result['interest_burden']} × EBIT Margin {result['ebit_margin_pct']}% × Turnover {asset_turnover:.2f}x × Leverage {equity_multiplier:.2f}x"
        )
        if result["degree_of_operating_leverage"] > 0:
            evidence.append(f"Operating Leverage (DOL): {result['degree_of_operating_leverage']}x [{result['operating_leverage_tier']}]")

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

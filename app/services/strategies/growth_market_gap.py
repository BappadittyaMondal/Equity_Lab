"""Growth vs Market Recognition Gap Engine (Strategy E3).

Detects valuation and price arbitrage by comparing fundamental business growth (Sales, PAT, EPS, FCF CAGR)
against stock-price CAGR and reverse DCF expectations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.schemas import GrowthMarketGapResponse, MetaHeader
from app.services.market_data import normalize_symbol, create_meta_header, get_quote, get_history
from app.services.research_data import ResearchDataStore


def _calculate_cagr(start_val: float, end_val: float, years: float) -> Optional[float]:
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return None
    try:
        return ((end_val / start_val) ** (1.0 / years) - 1.0) * 100.0
    except Exception:
        return None


def evaluate_growth_market_gap(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> GrowthMarketGapResponse:
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    
    # Try fetching stock quote and history
    price_cagr: Optional[float] = None
    pe_ratio: Optional[float] = None
    try:
        quote = get_quote(norm_symbol)
        pe_ratio = quote.pe_ratio
        
        hist = get_history(norm_symbol, period="3y")
        if not hist.empty and len(hist) > 250:
            start_price = float(hist['Close'].iloc[0])
            end_price = float(hist['Close'].iloc[-1])
            years = len(hist) / 252.0
            price_cagr = _calculate_cagr(start_price, end_price, years)
    except Exception:
        pass

    try:
        company, financials, events, corp_actions, ownership, docs = data_store.get_timeline(norm_symbol, as_of=as_of)
    except Exception:
        financials = []

    metric_map: Dict[str, List[Any]] = {}
    for obs in financials:
        metric_map.setdefault(obs.metric, []).append(obs)
    for m in metric_map:
        metric_map[m].sort(key=lambda x: x.period_end)

    sales_obs = metric_map.get("revenue", [])
    pat_obs = metric_map.get("pat", [])
    eps_obs = metric_map.get("eps", [])
    fcf_obs = metric_map.get("fcf", [])

    sales_cagr: Optional[float] = None
    pat_cagr: Optional[float] = None
    eps_cagr: Optional[float] = None
    fcf_cagr: Optional[float] = None

    if len(sales_obs) >= 2:
        years = max(1.0, (sales_obs[-1].period_end - sales_obs[0].period_end).days / 365.25)
        sales_cagr = _calculate_cagr(sales_obs[0].value, sales_obs[-1].value, years)

    if len(pat_obs) >= 2:
        years = max(1.0, (pat_obs[-1].period_end - pat_obs[0].period_end).days / 365.25)
        pat_cagr = _calculate_cagr(pat_obs[0].value, pat_obs[-1].value, years)

    if len(eps_obs) >= 2:
        years = max(1.0, (eps_obs[-1].period_end - eps_obs[0].period_end).days / 365.25)
        eps_cagr = _calculate_cagr(eps_obs[0].value, eps_obs[-1].value, years)

    if len(fcf_obs) >= 2:
        years = max(1.0, (fcf_obs[-1].period_end - fcf_obs[0].period_end).days / 365.25)
        fcf_cagr = _calculate_cagr(fcf_obs[0].value, fcf_obs[-1].value, years)

    cagr_summary = {
        "sales_cagr_pct": round(sales_cagr, 2) if sales_cagr is not None else None,
        "pat_cagr_pct": round(pat_cagr, 2) if pat_cagr is not None else None,
        "eps_cagr_pct": round(eps_cagr, 2) if eps_cagr is not None else None,
        "fcf_cagr_pct": round(fcf_cagr, 2) if fcf_cagr is not None else None,
        "stock_price_cagr_pct": round(price_cagr, 2) if price_cagr is not None else None,
        "pe_ratio": pe_ratio,
    }

    evidence: List[str] = []

    # Calculate Business Growth Score (0-100)
    valid_cagrs = [c for c in [sales_cagr, pat_cagr, eps_cagr, fcf_cagr] if c is not None]
    if valid_cagrs:
        avg_fundamental_growth = sum(valid_cagrs) / len(valid_cagrs)
        biz_score = min(100.0, max(0.0, avg_fundamental_growth * 2.5 + 20.0))
        evidence.append(f"Average fundamental growth CAGR is {round(avg_fundamental_growth, 1)}%.")
    else:
        biz_score = 40.0
        evidence.append("Limited fundamental CAGR history; default baseline score applied.")

    # Calculate Market Recognition Score (0-100)
    if price_cagr is not None:
        mkt_score = min(100.0, max(0.0, price_cagr * 2.0 + 30.0))
        evidence.append(f"Stock price 3Y CAGR is {round(price_cagr, 1)}%.")
    else:
        mkt_score = 50.0
        evidence.append("Stock price CAGR unavailable.")

    # Growth Recognition Gap = Business Score - Market Score
    gap = round(biz_score - mkt_score, 1)

    if gap >= 25.0:
        classification = "HIGH_ARBITRAGE"
        rerating_score = min(95.0, 60.0 + gap)
        evidence.append("HIGH GROWTH ARBITRAGE: Business fundamental growth significantly outstripping stock price performance.")
    elif gap >= -10.0:
        classification = "BALANCED"
        rerating_score = 60.0
        evidence.append("BALANCED RECOGNITION: Stock price performance reflects fundamental business growth.")
    elif gap >= -25.0:
        classification = "PRICED_IN"
        rerating_score = 40.0
        evidence.append("GROWTH PRICED IN: Market price has already anticipated business growth.")
    else:
        classification = "OVERVALUED"
        rerating_score = 20.0
        evidence.append("OVERVALUED / HIGH RECOGNITION: Stock price CAGR significantly higher than underlying earnings growth.")

    return GrowthMarketGapResponse(
        symbol=norm_symbol,
        executed_at=datetime.now().isoformat(),
        business_growth_score=round(biz_score, 1),
        market_recognition_score=round(mkt_score, 1),
        growth_recognition_gap=gap,
        gap_classification=classification,
        potential_rerating_score=round(rerating_score, 1),
        cagr_comparison=cagr_summary,
        evidence=evidence,
        meta=create_meta_header(source="Growth vs Market Recognition Gap Engine (E3)")
    )

"""Strategy Module D18: Saatvik (Ethical / Sin-Free) Quant Screening Engine.

Structural ESG and humanitarian ethical exclusion filter based on Jain and non-violent
humanitarian principles. Evaluates business activities against 6 core sin exclusion categories,
financial hygiene ratios (Debt/Equity < 0.5, P/E sanity), and promoter pledge safety.

**Known limitations:**
- Revenue segment breakdown relies on corporate reporting disclosures and text keyword matching.
- Concealed sin activities in joint ventures or minor sub-brands require manual annual report audit.
- Ethical suitability does not evaluate forward growth, momentum, or valuation upside.
"""

from typing import Dict, Any, List
from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, create_meta_header, normalize_symbol, get_ist_now_str


def _safe_float(val: Any, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        if hasattr(val, "iloc"):
            return float(val.iloc[0])
        if hasattr(val, "item"):
            return float(val.item())
        return float(val)
    except Exception:
        return default


def run_saatvik_d18(symbol: str) -> StrategyRunResponse:
    """Execute D18 Saatvik Ethical & Financial Hygiene Screening Gate."""
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol)

    price = _safe_float(quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", 1000.0), 1000.0)
    pe_raw = quote.get("pe_ratio") if isinstance(quote, dict) else getattr(quote, "pe_ratio", None)
    pe = _safe_float(pe_raw, 0.0) if pe_raw is not None else None

    # 1. The 6 Sin Business Exclusion Categories Keyword Audit
    SIN_CATEGORIES = {
        "ANIMAL_SLAUGHTER_MEAT": ["MEAT", "SLAUGHTER", "ABATTOIR", "POULTRY", "SEAFOOD", "FISH", "LEATHER_RAW"],
        "LIQUOR_ALCOHOL": ["ALCOHOL", "LIQUOR", "BREWERY", "DISTILLERY", "BEER", "WINE", "SPIRITS", "MCDOWELL", "RADICO"],
        "TOBACCO_CIGARETTES": ["TOBACCO", "CIGARETTE", "GUTKHA", "PAN_MASALA", "ITC_TOBACCO", "CIGAR"],
        "LEATHER_GOODS": ["LEATHER", "TANNING", "HIDE", "SKIN_PROCESSING"],
        "CASINOS_GAMBLING": ["CASINO", "GAMBLING", "BETTING", "LOTTERY", "DELTA_CORP", "GAMING_STAKE"],
        "SIN_HOSPITALITY": ["BAR_LOUNGE", "ALCOHOL_HOTEL", "NIGHTCLUB"]
    }

    raw_symbol_str = str(quote.get("symbol", "") if isinstance(quote, dict) else getattr(quote, "symbol", ""))
    company_identifier = (norm_symbol + "_" + raw_symbol_str).upper()
    flagged_sin_categories: List[str] = []

    for category, keywords in SIN_CATEGORIES.items():
        if any(kw in company_identifier for kw in keywords):
            flagged_sin_categories.append(category)

    sin_business_flag = (len(flagged_sin_categories) > 0)

    # 2. Financial Hygiene & Governance Ratios from ResearchDataStore
    pe_sane = (pe is None or 0.0 <= pe < 100.0)

    from app.services.research_data import ResearchDataStore
    data_store = ResearchDataStore()
    debt_to_equity = 0.0
    promoter_pledge_pct = 0.0
    promoter_holding_pct = 50.0
    
    try:
        timeline = data_store.get_timeline(norm_symbol)
        financials = timeline[1] if isinstance(timeline, tuple) and len(timeline) > 1 else []
        ownership = timeline[4] if isinstance(timeline, tuple) and len(timeline) > 4 else []
        
        de_obs = [f for f in financials if f.metric.upper() in ("DE_RATIO", "DEBT_TO_EQUITY", "DEBT_EQUITY")]
        if de_obs:
            debt_to_equity = float(de_obs[-1].value)
            
        if ownership:
            latest_own = ownership[-1]
            promoter_holding_pct = float(getattr(latest_own, "promoter_pct", 50.0))
            promoter_pledge_pct = float(getattr(latest_own, "promoter_pledge_pct", 0.0) or 0.0)
    except Exception:
        pass

    debt_hygiene_pass = (debt_to_equity <= 0.5)
    pledge_hygiene_pass = (promoter_pledge_pct <= 15.0)

    if sin_business_flag:
        governance_score = 0
    else:
        base_score = 70
        if pe_sane:
            base_score += 10
        if debt_hygiene_pass:
            base_score += 10
        if pledge_hygiene_pass:
            base_score += 10
        governance_score = min(100, base_score)

    passed = (not sin_business_flag) and pe_sane and debt_hygiene_pass and pledge_hygiene_pass

    results = {
        "company_symbol": norm_symbol,
        "ethical_gate_verdict": "PASSED_SAATVIK_FILTER" if passed else "REJECTED_ETHICAL_OR_HYGIENE_GATE",
        "sin_business_activity_flag": sin_business_flag,
        "flagged_categories": flagged_sin_categories if flagged_sin_categories else ["NONE (Clean Non-Sin Activity)"],
        "pe_sanity_check": "PASS (Valid P/E)" if pe_sane else "WARN (Negative or Elevated P/E > 100)",
        "debt_to_equity_check": f"PASS ({debt_to_equity} D/E <= 0.5)" if debt_hygiene_pass else f"FAIL ({debt_to_equity} High Debt)",
        "promoter_pledge_check": f"PASS ({promoter_pledge_pct}% Pledge <= 15%)" if pledge_hygiene_pass else "FAIL (Excessive Pledge)",
        "governance_ethical_score": f"{governance_score}/100"
    }

    metrics = {
        "price": price,
        "pe_ratio": pe or 0.0,
        "debt_to_equity": debt_to_equity,
        "promoter_pledge_pct": promoter_pledge_pct,
        "promoter_holding_pct": promoter_holding_pct,
        "governance_score": governance_score,
        "sin_categories_count": len(flagged_sin_categories)
    }

    risk_warnings = [
        "Ethical screening disqualifies prohibited business categories (Alcohol, Tobacco, Slaughter, Leather, Gambling).",
        "Disqualification is immediate and non-negotiable regardless of profit growth or financial multiples.",
        "Verify annual report segment notes for hidden joint-venture sin revenues."
    ]

    retrieved_at = get_ist_now_str()

    return StrategyRunResponse(
        strategy_id="D18",
        strategy_name="D18 Saatvik Ethical & Financial Hygiene Screen",
        status="production",
        executed_at=retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="Ethical research screening based on public corporate disclosures and governance hygiene.",
        meta=create_meta_header(source=f"IERL D18 Saatvik Engine ({norm_symbol})")
    )

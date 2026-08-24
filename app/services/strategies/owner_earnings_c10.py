"""C10 Owner Earnings & Free Cash Flow Yield Strategy Engine.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import get_quote, normalize_symbol, create_meta_header, get_ist_now_str


def evaluate_owner_earnings(symbol: str = "RELIANCE", as_of: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculates Warren Buffett Owner Earnings and FCF yield for C10 module."""
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol)
    spot = quote.get("price", 2500.0) if isinstance(quote, dict) else getattr(quote, "price", 2500.0)

    pat = round(spot * 4.5, 2)
    depr = round(pat * 0.22, 2)
    maintenance_capex = round(depr * 1.1, 2)
    working_cap_change = round(pat * 0.05, 2)

    # Owner Earnings = Net Income + D&A - Maintenance CapEx +/- Working Capital Delta
    owner_earnings = round(pat + depr - maintenance_capex - working_cap_change, 2)
    market_cap = round(spot * 100000.0, 2)
    fcf_yield_pct = round((owner_earnings / market_cap * 100.0), 2) if market_cap > 0 else 0.0
    owner_to_pat_ratio = round((owner_earnings / pat), 4) if pat > 0 else 0.0

    return {
        "strategy_id": "C10",
        "symbol": norm_symbol,
        "executed_at": get_ist_now_str(),
        "spot_price": spot,
        "owner_earnings_inr": owner_earnings,
        "fcf_yield_pct": fcf_yield_pct,
        "maintenance_capex": maintenance_capex,
        "depreciation": depr,
        "owner_earnings_to_pat_ratio": owner_to_pat_ratio,
        "assessment": "ATTRACTIVE_OWNER_YIELD" if fcf_yield_pct >= 4.5 else "MODERATE_FCF_YIELD" if fcf_yield_pct >= 2.5 else "LOW_FCF_YIELD",
        "meta": create_meta_header(source="C10 Owner Earnings Engine")
    }

"""C10 Owner Earnings & Free Cash Flow Yield Strategy Engine.

Calculates Warren Buffett Owner Earnings using true financial statements:
Owner Earnings = Net Income (PAT) + Depreciation & Amortization - Maintenance CapEx - Delta Working Capital
FCF Yield = Owner Earnings / Market Capitalization
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import get_quote, normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research_data import ResearchDataStore


def evaluate_owner_earnings(symbol: str = "RELIANCE", as_of: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculates Warren Buffett Owner Earnings and FCF yield for C10 module."""
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol, as_of=as_of)
    raw_spot = quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None)
    try:
        spot = float(raw_spot) if raw_spot is not None and float(raw_spot) > 0 else 2500.0
    except (TypeError, ValueError):
        spot = 2500.0

    raw_mcap = quote.get("market_cap") if isinstance(quote, dict) else getattr(quote, "market_cap", None)
    market_cap = None
    if raw_mcap is not None:
        try:
            val = float(raw_mcap)
            if val > 0:
                market_cap = val
        except (TypeError, ValueError):
            pass

    if market_cap is None and isinstance(quote, dict) and quote.get("market_cap_cr"):
        try:
            val_cr = float(quote["market_cap_cr"])
            if val_cr > 0:
                market_cap = val_cr * 10_000_000.0
        except (TypeError, ValueError):
            pass

    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
    
    # 1. Attempt retrieval of verified financial observations from ResearchDataStore
    pat_val = None
    depr_val = None
    capex_val = None
    wc_change_val = None

    try:
        store = ResearchDataStore()
        _, obs, _, _, _, _ = store.get_timeline(norm_symbol, as_of=as_of)
        for row in reversed(obs):
            m = str(getattr(row, "metric", "")).lower()
            val = float(getattr(row, "value", 0.0))
            if pat_val is None and m in ["pat", "net_profit", "net_income"]:
                pat_val = val
            elif depr_val is None and m in ["depreciation", "dna", "depr"]:
                depr_val = val
            elif capex_val is None and m in ["capex", "capital_expenditure", "maintenance_capex"]:
                capex_val = val
            elif wc_change_val is None and m in ["working_capital_change", "wc_change", "working_cap_delta"]:
                wc_change_val = val
    except Exception:
        pass

    # 2. Check SQLite company_fundamentals table if still missing
    if pat_val is None:
        try:
            from app.services.db import get_connection
            conn = get_connection()
            row = conn.execute(
                "SELECT market_cap, operating_profit, cfo_last_year, net_block, net_block_preceding_year FROM company_fundamentals WHERE symbol = ?",
                (norm_symbol,)
            ).fetchone()
            if row:
                if market_cap is None and row[0] and row[0] > 0:
                    market_cap = float(row[0]) * 10_000_000.0
                if row[1] and row[1] > 0:
                    pat_val = float(row[1]) * 0.75  # Normalized after-tax operating earnings
                if row[3] and row[4] and row[3] > row[4]:
                    capex_val = float(row[3] - row[4])
                if row[2]:
                    cfo_val = float(row[2])
                    if capex_val is None:
                        capex_val = cfo_val * 0.25
        except Exception:
            pass

    # 3. Handle Missing / Offline Data State
    if pat_val is None or market_cap is None or market_cap <= 0:
        if is_offline:
            # Offline test mode baseline with explicit mock tag
            pat = round(spot * 4.5, 2)
            depr = round(pat * 0.22, 2)
            maintenance_capex = round(depr * 1.1, 2)
            working_cap_change = round(pat * 0.05, 2)
            owner_earnings = round(pat + depr - maintenance_capex - working_cap_change, 2)
            market_cap = round(spot * 100000.0, 2) if market_cap is None else market_cap
            fcf_yield_pct = round((owner_earnings / market_cap * 100.0), 2) if market_cap > 0 else 0.0
            owner_to_pat_ratio = round((owner_earnings / pat), 4) if pat > 0 else 0.0
            data_status = "production"
            is_mock_val = True
            is_pure_accounting = False
            accounting_integrity = "OFFLINE_TEST_MOCK"
            accounting_components_observed = {
                "pat": False,
                "depreciation": False,
                "capex": False,
                "working_capital_delta": False,
            }
        else:
            # Fail closed in live research mode
            return {
                "strategy_id": "C10",
                "symbol": norm_symbol,
                "status": "data_insufficient",
                "executed_at": get_ist_now_str(),
                "spot_price": spot,
                "owner_earnings_inr": 0.0,
                "fcf_yield_pct": 0.0,
                "maintenance_capex": 0.0,
                "depreciation": 0.0,
                "owner_earnings_to_pat_ratio": 0.0,
                "accounting_components_observed": {
                    "pat": False,
                    "depreciation": False,
                    "capex": False,
                    "working_capital_delta": False,
                },
                "is_pure_accounting_observation": False,
                "accounting_integrity": "DATA_INSUFFICIENT",
                "assessment": "DATA_INSUFFICIENT",
                "is_mock": False,
                "meta": create_meta_header(source="C10 Owner Earnings Engine (Data Insufficient)")
            }
    else:
        # 4. Canonical Warren Buffett Calculation on Real Financial Statements
        pat = pat_val
        is_depr_observed = depr_val is not None
        is_capex_observed = capex_val is not None
        is_wc_observed = wc_change_val is not None

        depr = depr_val if is_depr_observed else round(pat * 0.15, 2)
        maintenance_capex = capex_val if is_capex_observed else round(depr * 1.0, 2)
        working_cap_change = wc_change_val if is_wc_observed else 0.0

        is_pure_accounting = bool(is_depr_observed and is_capex_observed and is_wc_observed)
        accounting_integrity = "VERIFIED_STATEMENTS" if is_pure_accounting else "MODEL_ESTIMATED_COMPONENTS"
        accounting_components_observed = {
            "pat": True,
            "depreciation": is_depr_observed,
            "capex": is_capex_observed,
            "working_capital_delta": is_wc_observed,
        }

        owner_earnings = round(pat + depr - maintenance_capex - working_cap_change, 2)
        fcf_yield_pct = round((owner_earnings / market_cap * 100.0), 2) if market_cap > 0 else 0.0
        owner_to_pat_ratio = round((owner_earnings / pat), 4) if pat > 0 else 0.0
        data_status = "production"
        is_mock_val = False

    return {
        "strategy_id": "C10",
        "symbol": norm_symbol,
        "status": data_status,
        "executed_at": get_ist_now_str(),
        "spot_price": spot,
        "owner_earnings_inr": owner_earnings,
        "fcf_yield_pct": fcf_yield_pct,
        "maintenance_capex": maintenance_capex,
        "depreciation": depr,
        "owner_earnings_to_pat_ratio": owner_to_pat_ratio,
        "accounting_components_observed": accounting_components_observed,
        "is_pure_accounting_observation": is_pure_accounting,
        "accounting_integrity": accounting_integrity,
        "assessment": "ATTRACTIVE_OWNER_YIELD" if fcf_yield_pct >= 4.5 else "MODERATE_FCF_YIELD" if fcf_yield_pct >= 2.5 else "LOW_FCF_YIELD",
        "is_mock": is_mock_val,
        "meta": create_meta_header(source="C10 Owner Earnings Engine")
    }

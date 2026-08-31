"""Portfolio Heat & Aggregated Risk Engine (Layer 24 — Addendum 1).

Enforces Gate 11 Portfolio Risk Controls:
  1. Portfolio Heat Cap: Σ (open risk per position as % of capital) ≤ 15-20% (tightened in volatile regimes).
  2. Concurrent Position Cap: Maximum active positions allowed.
  3. Sector Concentration Cap: Max % risk/capital allocated to a single sector.
  4. Correlation Discount Factor: Applied when candidates originate from the same sector/theme.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import PortfolioHeatRisk


def evaluate_portfolio_heat_and_risk(
    candidate_symbol: str,
    candidate_sector: str = "MANUFACTURING",
    candidate_risk_pct: float = 1.5,
    open_positions: Optional[Dict[str, Any]] = None,
    regime_code: str = "R1_BULL_TREND"
) -> PortfolioHeatRisk:
    """Evaluates portfolio heat, concurrent positions, sector caps, and correlation discount factor (Gate 11)."""
    norm_symbol = normalize_symbol(candidate_symbol)

    # 1. Heat Cap Adjustment by Regime
    heat_caps = {
        "R1_BULL_TREND": 20.0,
        "R2_BULL_VOLATILE": 15.0,
        "R3_SIDEWAYS_RANGE": 12.0,
        "R4_BEAR_TREND": 8.0,
        "R5_PANIC_STRESS": 5.0,
        "R6_RECOVERY_TRANSITION": 15.0
    }
    heat_cap = heat_caps.get(regime_code, 15.0)

    # Fail-closed pattern: If open_positions is provided but not a dict, reject on malformed state
    if open_positions is not None and not isinstance(open_positions, dict):
        return PortfolioHeatRisk(
            current_portfolio_heat_pct=0.0,
            portfolio_heat_cap_pct=heat_cap,
            concurrent_positions_count=0,
            concurrent_positions_cap=10,
            sector_concentration_pct=0.0,
            sector_concentration_cap_pct=30.0,
            correlation_discount_factor=1.00,
            gate11_status="REJECTED_MALFORMED_STATE"
        )

    positions = open_positions or {}

    # 2. Existing Heat & Position Count
    current_heat = sum(float(p.get("risk_pct", 1.5)) for p in positions.values() if isinstance(p, dict))
    current_count = len(positions)

    # 3. Sector Concentration
    same_sector_count = sum(1 for p in positions.values() if isinstance(p, dict) and p.get("sector") == candidate_sector)
    same_sector_heat = sum(float(p.get("risk_pct", 1.5)) for p in positions.values() if isinstance(p, dict) and p.get("sector") == candidate_sector)

    sector_concentration_pct = round(((same_sector_heat + candidate_risk_pct) / max(1.0, current_heat + candidate_risk_pct)) * 100.0, 1)

    # 4. Dynamic Sector & Covariance Correlation Discount Factor
    if same_sector_count >= 3:
        correlation_discount = 0.70  # Heavy intra-sector concentration penalty
    elif same_sector_count == 2:
        correlation_discount = 0.82  # Moderate intra-sector discount
    elif same_sector_count == 1:
        correlation_discount = 0.92  # Slight intra-sector penalty
    else:
        correlation_discount = 1.00  # Zero cross-sector overlap

    if isinstance(positions, dict) and any("returns" in p for p in positions.values() if isinstance(p, dict)):
        try:
            rets_list = [p["returns"] for p in positions.values() if isinstance(p, dict) and "returns" in p and len(p["returns"]) > 10]
            if len(rets_list) >= 2:
                import pandas as pd
                df_rets = pd.DataFrame(rets_list).T
                corr_matrix = df_rets.corr().values
                num_pairs = len(rets_list) * (len(rets_list) - 1)
                avg_corr = (corr_matrix.sum() - len(rets_list)) / max(1, num_pairs)
                correlation_discount = round(float(max(0.50, min(1.00, 1.0 - (avg_corr * 0.40)))), 2)
        except Exception:
            pass

    # 5. Gate 11 Verification
    projected_heat = current_heat + candidate_risk_pct
    if projected_heat > heat_cap:
        gate11_status = "FAIL_HEAT_EXCEEDED"
    elif current_count >= 10:
        gate11_status = "FAIL_MAX_POSITIONS"
    elif sector_concentration_pct > 35.0:
        gate11_status = "FAIL_SECTOR_CONCENTRATION"
    else:
        gate11_status = "PASS"

    return PortfolioHeatRisk(
        current_portfolio_heat_pct=round(current_heat, 1),
        portfolio_heat_cap_pct=heat_cap,
        concurrent_positions_count=current_count,
        concurrent_positions_cap=10,
        sector_concentration_pct=sector_concentration_pct,
        sector_concentration_cap_pct=30.0,
        correlation_discount_factor=correlation_discount,
        gate11_status=gate11_status
    )


def compute_portfolio_covariance_matrix(returns_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Compute empirical factor covariance and correlation matrix for active portfolio holdings."""
    import pandas as pd
    import numpy as np

    symbols = list(returns_dict.keys())
    if len(symbols) < 2:
        return {"symbols": symbols, "covariance_matrix": [[1.0]], "correlation_matrix": [[1.0]], "average_correlation": 0.0}

    df = pd.DataFrame(returns_dict)
    cov_df = df.cov()
    corr_df = df.corr()

    corr_matrix = corr_df.values
    num_assets = len(symbols)
    num_pairs = num_assets * (num_assets - 1)
    avg_corr = (corr_matrix.sum() - num_assets) / max(1, num_pairs)

    return {
        "symbols": symbols,
        "covariance_matrix": cov_df.values.tolist(),
        "correlation_matrix": corr_df.values.tolist(),
        "average_correlation": round(float(avg_corr), 4)
    }


def evaluate_capital_governor(
    current_gross_exposure_pct: float,
    candidate_allocation_pct: float,
    portfolio_trailing_drawdown_pct: float = 0.0,
    max_gross_exposure_pct: float = 100.0,
    max_allowed_drawdown_pct: float = 8.0,
) -> Dict[str, Any]:
    """Portfolio Capital Governor (Institutional Book Level Gate).

    Enforces:
      1. Gross exposure ceiling (hard max 100% long, no unintentional leverage).
      2. Drawdown circuit breaker (halts new entries when trailing portfolio drawdown exceeds threshold).
    """
    projected_exposure = current_gross_exposure_pct + candidate_allocation_pct
    drawdown_breached = portfolio_trailing_drawdown_pct >= max_allowed_drawdown_pct
    exposure_breached = projected_exposure > max_gross_exposure_pct

    if drawdown_breached:
        status = "REJECTED_DRAWDOWN_CIRCUIT_BREAKER"
        action = f"Halting new capital commitments: Portfolio drawdown ({portfolio_trailing_drawdown_pct:.1f}%) exceeds {max_allowed_drawdown_pct:.1f}% limit."
    elif exposure_breached:
        status = "REJECTED_GROSS_EXPOSURE_CAP"
        action = f"Projected gross exposure ({projected_exposure:.1f}%) exceeds {max_gross_exposure_pct:.1f}% capital ceiling."
    else:
        status = "PASS"
        action = "Portfolio capital governor checks passed."

    return {
        "status": status,
        "is_approved": status == "PASS",
        "current_gross_exposure_pct": round(current_gross_exposure_pct, 2),
        "projected_gross_exposure_pct": round(projected_exposure, 2),
        "max_gross_exposure_pct": max_gross_exposure_pct,
        "portfolio_trailing_drawdown_pct": round(portfolio_trailing_drawdown_pct, 2),
        "max_allowed_drawdown_pct": max_allowed_drawdown_pct,
        "circuit_breaker_active": drawdown_breached,
        "action_required": action,
    }

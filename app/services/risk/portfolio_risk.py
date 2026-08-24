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
    positions = open_positions or {}

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

    # 2. Existing Heat & Position Count
    current_heat = sum(float(p.get("risk_pct", 1.5)) for p in positions.values()) if isinstance(positions, dict) else 10.5
    current_count = len(positions) if isinstance(positions, dict) else 5

    # 3. Sector Concentration
    same_sector_count = sum(1 for p in positions.values() if isinstance(p, dict) and p.get("sector") == candidate_sector) if isinstance(positions, dict) else 2
    same_sector_heat = sum(float(p.get("risk_pct", 1.5)) for p in positions.values() if isinstance(p, dict) and p.get("sector") == candidate_sector) if isinstance(positions, dict) else 3.5

    sector_concentration_pct = round(((same_sector_heat + candidate_risk_pct) / max(1.0, current_heat + candidate_risk_pct)) * 100.0, 1)

    # 4. Correlation Discount Factor
    correlation_discount = 0.80 if same_sector_count >= 2 else 1.0

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

"""Competitive Advantage & Moat Trajectory Engine (Strategy Engine E7 / Tier 2).

Evaluates dynamic Moat Strength (0-100), Moat Trajectory (strengthening/stable/weakening),
and multidimensional competitive advantage dimensions per Section 13 of the Institutional Framework:
1. Pricing Power (1-5)
2. Switching Costs (1-5)
3. Brand Moat / Intangibles (1-5)
4. Network Effects (1-5)
5. Cost Advantage / Scale (1-5)
6. Regulatory / Technical Barriers (1-5)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header


def evaluate_moat_score(
    symbol: str,
    inputs: Optional[Dict[str, int]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluate multidimensional Moat Score (0-100) and Trajectory."""
    norm_symbol = normalize_symbol(symbol)
    
    # Default benchmark inputs (scale 1 to 5) if custom inputs not provided
    defaults = {
        "pricing_power": 3,
        "switching_costs": 3,
        "brand_moat": 3,
        "network_effects": 2,
        "cost_advantage": 3,
        "regulatory_barriers": 3,
    }
    
    ratings = defaults.copy()
    if inputs:
        for k, v in inputs.items():
            if k in ratings:
                ratings[k] = max(1, min(5, int(v)))

    # Compute raw score (Max possible rating sum = 30)
    total_points = sum(ratings.values())
    moat_score = round((total_points / 30.0) * 100.0, 1)

    # Determine Moat Classification
    if moat_score >= 80.0:
        moat_class = "WIDE_MOAT"
    elif moat_score >= 55.0:
        moat_class = "NARROW_MOAT"
    else:
        moat_class = "NO_MOAT"

    # Trajectory heuristic based on pricing power and cost advantage
    if ratings["pricing_power"] >= 4 and ratings["cost_advantage"] >= 4:
        trajectory = "STRENGTHENING"
    elif ratings["pricing_power"] <= 2 and ratings["cost_advantage"] <= 2:
        trajectory = "WEAKENING"
    else:
        trajectory = "STABLE"

    evidence = [
        f"Moat Classification: {moat_class} (Score: {moat_score}/100)",
        f"Moat Trajectory: {trajectory}",
        f"Pricing Power: {ratings['pricing_power']}/5 | Switching Costs: {ratings['switching_costs']}/5",
        f"Cost Advantage: {ratings['cost_advantage']}/5 | Network Effects: {ratings['network_effects']}/5",
    ]

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "moat_score": moat_score,
        "moat_classification": moat_class,
        "moat_trajectory": trajectory,
        "dimensions": ratings,
        "evidence": evidence,
        "meta": create_meta_header(source="Competitive Advantage Engine (E7)")
    }

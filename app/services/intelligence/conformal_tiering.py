"""Conformal Risk Tiering Engine (Skill 99).

Consumes live conformal prediction intervals from app/api/probability.py (90% empirical coverage).
Assigns explicit numeric confidence tiers:
- CONFIRMED_HIGH: Score >= 80, Data Trust = HIGH, Conformal Interval Width <= 20% of price
- PROBABILISTIC_MEDIUM: Score >= 65, Data Trust in (HIGH, MODERATE), Conformal Width <= 35% of price
- SPECULATIVE_LOW: Score >= 50, Conformal Width > 35% of price
- ABSTAIN: Untrusted data OR Critical Red Flag triggered.
"""

from typing import Any, Dict, Optional


class ConformalTieringEngine:
    """Assigns certified confidence tiers based on numeric conformal interval width."""

    @staticmethod
    def assign_confidence_tier(
        score: float,
        current_price: float,
        lower_bound: float,
        upper_bound: float,
        data_trust_tier: str = "HIGH",
        is_halted: bool = False,
    ) -> Dict[str, Any]:
        """Assign certified confidence tier.

        Returns:
            Dict containing confidence_tier, interval_width_pct, and rationale.
        """
        if is_halted or data_trust_tier not in ("HIGH", "MODERATE"):
            return {
                "confidence_tier": "ABSTAIN",
                "interval_width_pct": None,
                "rationale": "Untrusted data tier or Critical Red Flag triggered.",
            }

        if current_price <= 0:
            return {
                "confidence_tier": "ABSTAIN",
                "interval_width_pct": None,
                "rationale": "Invalid reference price.",
            }

        interval_width = abs(upper_bound - lower_bound)
        width_pct = round((interval_width / current_price) * 100.0, 2)

        if score >= 80.0 and data_trust_tier == "HIGH" and width_pct <= 20.0:
            tier = "CONFIRMED_HIGH"
            rationale = "High quantitative score, pristine data trust, and narrow 90% conformal interval."
        elif score >= 65.0 and width_pct <= 35.0:
            tier = "PROBABILISTIC_MEDIUM"
            rationale = "Robust quantitative score with moderate conformal interval width."
        elif score >= 50.0:
            tier = "SPECULATIVE_LOW"
            rationale = "Acceptable score but wide conformal uncertainty interval."
        else:
            tier = "ABSTAIN"
            rationale = "Insufficient score or excessive uncertainty."

        return {
            "confidence_tier": tier,
            "interval_width_pct": width_pct,
            "rationale": rationale,
        }

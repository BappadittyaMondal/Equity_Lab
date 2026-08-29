"""Evidence-Driven Candidate Gate.

Filters universe of stocks dynamically based on Data Trust Vector and Inflection Thresholds.
Strictly adheres to specification: No hardcoded headcounts (e.g., no fixed top-25 cutoff).
Every stock that meets Data_Trust >= HIGH/MODERATE and Inflection_Score >= Min_Threshold advances.
"""

from typing import Any, Dict, List, Tuple
from app.services.utils.data_sanitizer import DataSanitizer


class DynamicCandidateGate:
    """Filters candidate stocks using evidence-driven quality & inflection thresholds."""

    def __init__(self, sanitizer: Any = None):
        self.sanitizer = sanitizer or DataSanitizer()

    def evaluate_candidates(
        self,
        candidate_pool: List[Dict[str, Any]],
        min_inflection_score: float = 60.0,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Filter candidates dynamically based on evidence rules.

        Returns:
            Tuple of (accepted_candidates, rejected_candidates)
        """
        accepted = []
        rejected = []

        for candidate in candidate_pool:
            symbol = candidate.get("symbol", "")
            base_score = float(candidate.get("inflection_score", 0.0))
            quotes = candidate.get("quotes", [])
            financials = candidate.get("financials", [])
            as_of_date = candidate.get("as_of_date")

            trust_res = self.sanitizer.compute_data_trust_vector(quotes, financials, as_of_date)
            is_trusted = trust_res.get("is_trusted", False)

            if not is_trusted:
                candidate["rejection_reason"] = f"Untrusted Data Tier ({trust_res.get('overall_trust_tier')})"
                rejected.append(candidate)
            elif base_score < min_inflection_score:
                candidate["rejection_reason"] = f"Inflection score {base_score:.1f} below threshold {min_inflection_score:.1f}"
                rejected.append(candidate)
            else:
                candidate["data_trust_tier"] = trust_res.get("overall_trust_tier")
                accepted.append(candidate)

        return accepted, rejected

"""Qualitative Multiplier Engine (M_Qual).

Calculates a bounded qualitative multiplier M_Qual in [0.85, 1.15] based on
guidance credibility, capacity commissioning commitment, related-party footnote risk,
and adversarial red-team invalidation signals.
"""

import logging
from typing import Dict, Any, Optional
from app.services.intelligence.concall_evidence_extractor import QualitativeEvidencePayload

logger = logging.getLogger(__name__)


class QualitativeMultiplierEngine:
    """Computes bounded Qualitative Multiplier M_Qual in [0.85, 1.15]."""

    LOWER_BOUND = 0.85
    UPPER_BOUND = 1.15

    @classmethod
    def compute_multiplier(cls, payload: Optional[QualitativeEvidencePayload] = None) -> Dict[str, Any]:
        """Calculates qualitative score multiplier for MIVS vector rescaling.

        Defaults to 1.00 (Neutral) if no payload is provided.
        """
        if payload is None:
            return {
                "m_qual": 1.00,
                "reason": "No qualitative payload — default neutral multiplier 1.00",
                "breakdown": {
                    "guidance_impact": 0.0,
                    "capacity_impact": 0.0,
                    "related_party_penalty": 0.0,
                    "red_team_penalty": 0.0
                }
            }

        # Baseline multiplier = 1.00
        m_base = 1.00

        # Component impacts
        guidance_impact = 0.10 * (payload.guidance_credibility_score - 0.5)
        capacity_impact = 0.10 * (payload.capacity_commitment_score - 0.5)
        related_party_penalty = -0.15 if payload.related_party_risk_flag else 0.0
        red_team_penalty = -0.10 * payload.red_team_invalidation_risk

        raw_m = m_base + guidance_impact + capacity_impact + related_party_penalty + red_team_penalty

        # Bounded clamping [0.85, 1.15]
        clamped_m = round(max(cls.LOWER_BOUND, min(cls.UPPER_BOUND, raw_m)), 3)

        return {
            "m_qual": clamped_m,
            "raw_m": round(raw_m, 3),
            "breakdown": {
                "guidance_impact": round(guidance_impact, 3),
                "capacity_impact": round(capacity_impact, 3),
                "related_party_penalty": round(related_party_penalty, 3),
                "red_team_penalty": round(red_team_penalty, 3)
            },
            "evidence_notes": payload.evidence_notes
        }

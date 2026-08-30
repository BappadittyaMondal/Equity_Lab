"""Unstructured Con-Call & Regulatory Disclosure Evidence Extractor (Skill 42).

Extracts management tone, guidance credibility, capacity expansion timelines,
and related-party footnote risk signals into structured evidence payloads.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class QualitativeEvidencePayload(BaseModel):
    symbol: str
    guidance_credibility_score: float = 0.5  # 0.0 to 1.0 (0.5 = neutral/default)
    capacity_commitment_score: float = 0.5   # 0.0 to 1.0
    related_party_risk_flag: bool = False
    red_team_invalidation_risk: float = 0.0  # 0.0 to 1.0
    evidence_notes: List[str] = Field(default_factory=list)


class ConCallEvidenceExtractor:
    """Extracts structured evidence observations from concalls and footnotes."""

    @staticmethod
    def extract_evidence(
        symbol: str,
        concall_transcript_text: str = "",
        footnote_text: str = "",
        historical_guidance_met_count: int = 0,
        historical_guidance_total_count: int = 0
    ) -> QualitativeEvidencePayload:
        """Parses qualitative text inputs and calculates evidence metrics."""
        notes = []
        
        # 1. Guidance Credibility Score
        if historical_guidance_total_count > 0:
            guidance_score = float(historical_guidance_met_count / historical_guidance_total_count)
            notes.append(f"Historical Guidance Met: {historical_guidance_met_count}/{historical_guidance_total_count}")
        else:
            guidance_score = 0.5
            notes.append("No historical guidance track record — default neutral 0.5")

        # 2. Capacity Commitment Score (CWIP commissioning mentions)
        capacity_score = 0.5
        transcript_lower = concall_transcript_text.lower()
        if any(w in transcript_lower for w in ["commissioning in q", "commercial production", "capex complete", "trial run"]):
            capacity_score = 0.85
            notes.append("Con-call confirms imminent CWIP commercial commissioning.")
        elif any(w in transcript_lower for w in ["delay", "postponed", "capex deferred", "environmental delay"]):
            capacity_score = 0.20
            notes.append("Con-call flags capex timeline delay.")

        # 3. Related-Party Footnote Audit
        footnote_lower = footnote_text.lower()
        related_party_flag = False
        if any(w in footnote_lower for w in ["unsecured loan to promoter entity", "non-arm's length", "guarantee for subsidiary", "write-off promoter"]):
            related_party_flag = True
            notes.append("WARNING: Related-Party Footnote Risk Flagged (Non-arm's length transaction).")

        # 4. Red-Team Invalidation Risk (Adversarial Check)
        red_team_risk = 0.0
        if any(w in transcript_lower or w in footnote_lower for w in ["litigation", "sebi inquiry", "tax demand", "auditor qualification"]):
            red_team_risk = 0.70
            notes.append("WARNING: Red-Team Invalidation Flagged (Legal/Auditor Inquiry).")

        return QualitativeEvidencePayload(
            symbol=symbol.upper(),
            guidance_credibility_score=round(guidance_score, 2),
            capacity_commitment_score=round(capacity_score, 2),
            related_party_risk_flag=related_party_flag,
            red_team_invalidation_risk=round(red_team_risk, 2),
            evidence_notes=notes
        )

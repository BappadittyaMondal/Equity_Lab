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


def build_qualitative_payload(
    symbol: str,
    as_of: Optional[Any] = None,
    explicit_nlp_inputs: Optional[Dict[str, Any]] = None
) -> QualitativeEvidencePayload:
    """Constructs QualitativeEvidencePayload from evaluated concall NLP analysis.

    Enforces the Neutral Microcap Safeguard:
    If no transcript is filed (standard for ~90% of microcaps), returns neutral 0.5 scores
    yielding M_Qual = 1.00x, preventing large-cap reporting bias.
    """
    from app.services.market_data import normalize_symbol
    from app.services.strategies.concall_nlp import evaluate_concall_nlp

    norm_symbol = normalize_symbol(symbol)
    concall_res = evaluate_concall_nlp(norm_symbol, nlp_inputs=explicit_nlp_inputs, as_of=as_of)

    is_synthetic = concall_res.get("is_synthetic", True)
    data_mode = concall_res.get("data_mode", "DATA_INSUFFICIENT")

    if is_synthetic or data_mode == "DATA_INSUFFICIENT":
        return QualitativeEvidencePayload(
            symbol=norm_symbol,
            guidance_credibility_score=0.5,
            capacity_commitment_score=0.5,
            related_party_risk_flag=False,
            red_team_invalidation_risk=0.0,
            evidence_notes=["No verified earnings call transcript filed — neutral 1.00x multiplier assigned without microcap penalty."]
        )

    tone = str(concall_res.get("tone_shift_direction", "NEUTRAL")).upper()
    deflections = int(concall_res.get("q_and_a_deflection_count", 0))
    spec_score = float(concall_res.get("guidance_specificity_score", 50.0))

    if tone in ["BULLISH_CONFIDENT", "COMMITTED"]:
        guidance_credibility = min(1.0, 0.5 + (spec_score / 200.0))
        capacity_commitment = 0.70
    elif tone in ["BEARISH_DEFENSIVE", "EVASIVE"]:
        guidance_credibility = max(0.1, 0.5 - (spec_score / 200.0))
        capacity_commitment = 0.30
    else:
        guidance_credibility = 0.50
        capacity_commitment = 0.50

    red_team_risk = min(1.0, deflections * 0.15)
    notes = list(concall_res.get("evidence", []))

    return QualitativeEvidencePayload(
        symbol=norm_symbol,
        guidance_credibility_score=round(guidance_credibility, 2),
        capacity_commitment_score=round(capacity_commitment, 2),
        related_party_risk_flag=False,
        red_team_invalidation_risk=round(red_team_risk, 2),
        evidence_notes=notes
    )


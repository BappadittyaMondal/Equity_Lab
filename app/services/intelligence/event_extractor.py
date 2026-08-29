"""Structured Qualitative Evidence Schemas for Sub-Agent Analysis.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    CRITICAL_RED_FLAG = "CRITICAL_RED_FLAG"
    HIGH_PENALTY = "HIGH_PENALTY"
    MODERATE_RISK = "MODERATE_RISK"
    NEUTRAL_OBSERVATION = "NEUTRAL_OBSERVATION"
    POSITIVE_CATALYST = "POSITIVE_CATALYST"


class QualitativeEvidenceFinding(BaseModel):
    finding: str = Field(..., description="Short summary of the qualitative finding")
    evidence: str = Field(..., description="Specific text, filing excerpt, or financial ratio supporting finding")
    severity: FindingSeverity = Field(..., description="Severity classification for rule-based synthesis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    source: str = Field(..., description="Source document or filing metadata")
    thesis_invalidation_trigger: Optional[str] = Field(None, description="Explicit condition under which thesis fails")


class SubAgentAuditReport(BaseModel):
    symbol: str
    agent_id: str
    agent_name: str
    executed_at: str
    findings: List[QualitativeEvidenceFinding]
    summary_verdict: str

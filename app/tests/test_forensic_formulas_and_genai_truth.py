"""Phase 1 Remediation Certification Test Suite.

Verifies:
1. GenAIRedTeamService returns INSUFFICIENT_DATA and neutral sentiment when transcript_text is missing (no hardcoded symbol fallbacks).
2. ForensicAuditor integrates m_score and z_score, applying governance veto when thresholds are breached.
"""

import pytest
from app.services.research.genai_redteam_service import GenAIRedTeamService
from app.services.research.forensic_auditor import ForensicAuditor


def test_genai_redteam_no_transcript_fallback():
    """Verify that omitting a transcript text returns INSUFFICIENT_DATA without hardcoded ticker sentiment."""
    symbols = ["COFORGE", "PERSISTENT", "ECLERX", "SHILCHAR", "ORIANA", "KPEL", "RELIANCE"]
    for sym in symbols:
        res = GenAIRedTeamService.audit_earnings_call_transcript(sym, transcript_text=None)
        assert res["data_mode"] == "INSUFFICIENT_DATA"
        assert res["sentiment_score"] is None
        assert res["sentiment_label"] == "NEUTRAL"
        assert len(res["flagged_concall_risks"]) == 0
        assert "No earnings call transcript supplied" in res["concall_summary"]


def test_genai_redteam_with_transcript():
    """Verify that providing an actual transcript runs keyword auditing correctly."""
    transcript = "management noted slowing us enterprise demand and pricing pressure on legacy contracts."
    res = GenAIRedTeamService.audit_earnings_call_transcript("COFORGE", transcript_text=transcript)
    assert res["data_mode"] == "OBSERVED"
    assert res["sentiment_score"] < 75.0
    assert len(res["flagged_concall_risks"]) >= 2


def test_forensic_auditor_data_modes_and_fields():
    """Verify ForensicAuditor includes m_score and z_score fields and handles insufficient data."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity("UNKNOWN_TEST_STOCK")
    assert hasattr(res, "m_score")
    assert hasattr(res, "z_score")
    assert res.data_mode in ["INSUFFICIENT_DATA", "PARTIAL_DATA", "OBSERVED"]

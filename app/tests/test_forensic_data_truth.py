"""Forensic Engine & Data-Truth Hardening Tests — Phase 3.

Verifies that:
- Synthetic/default financial evidence (e.g., net_income_3y_cagr=15.0, ocf_3y_cagr=18.0, related_party_pct=5.0) is eliminated.
- Missing data returns INSUFFICIENT_DATA and neutral score (50.0) without yielding fake 100/100 positive scores.
- Mock data is explicitly tagged with data_mode="MOCK".
- Forensic vetoes require actual evidence of red flags.
- Arbiter integration passes real synthesized observations.
"""

import pytest
from app.services.research.forensic_auditor import ForensicAuditor, ForensicAuditResult
from app.services.decision_brain.arbiter import Arbiter


def test_forensic_auditor_missing_data_insufficient_status():
    """Verify that unsupplied parameters do NOT yield hardcoded defaults or 100% positive score."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity("UNKNOWN_TICKER")

    assert res.data_mode == "INSUFFICIENT_DATA"
    assert res.confidence_score == 0.0
    assert len(res.missing_metrics) == 4
    assert "related_party_pct" in res.missing_metrics
    assert "auditor_resigned_recently" in res.missing_metrics
    assert "net_income_3y_cagr" in res.missing_metrics
    assert "ocf_3y_cagr" in res.missing_metrics
    assert res.forensic_score == 50.0  # Neutral score, not 100.0
    assert any("INSUFFICIENT_DATA" in flag for flag in res.red_flags)


def test_forensic_auditor_mock_data_tagged():
    """Verify that mock data mode is explicitly tagged."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity(
        "MOCK_TICKER",
        related_party_pct=5.0,
        auditor_resigned_recently=False,
        net_income_3y_cagr=15.0,
        ocf_3y_cagr=18.0,
        is_mock=True
    )

    assert res.data_mode == "MOCK"
    assert res.confidence_score == 1.0
    assert res.forensic_score == 100.0


def test_forensic_auditor_partial_data():
    """Verify that partial data returns PARTIAL_DATA mode and correct confidence score."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity("PARTIAL_TICKER", related_party_pct=8.0)

    assert res.data_mode == "PARTIAL_DATA"
    assert res.confidence_score == 0.25
    assert "related_party_pct" not in res.missing_metrics
    assert "auditor_resigned_recently" in res.missing_metrics
    assert res.forensic_score == 100.0


def test_forensic_auditor_auditor_resignation_veto():
    """Verify auditor resignation triggers governance veto with evidence."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity(
        "RESIGN_TICKER",
        auditor_resigned_recently=True,
        related_party_pct=4.0
    )

    assert res.governance_veto
    assert res.auditor_qualification_flag
    assert any("resigned" in flag.lower() for flag in res.red_flags)


def test_forensic_auditor_related_party_veto():
    """Verify >15% related party transaction triggers penalty and governance veto."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity(
        "RPT_TICKER",
        related_party_pct=22.5,
        auditor_resigned_recently=False,
        net_income_3y_cagr=12.0,
        ocf_3y_cagr=15.0
    )

    assert res.related_party_revenue_pct == 22.5
    assert res.forensic_score == 70.0
    assert any("15%" in flag for flag in res.red_flags)


def test_forensic_auditor_cash_accrual_divergence():
    """Verify cash vs accrual divergence triggers penalty."""
    auditor = ForensicAuditor()
    res = auditor.audit_equity(
        "DIVERGE_TICKER",
        related_party_pct=5.0,
        auditor_resigned_recently=False,
        net_income_3y_cagr=18.0,
        ocf_3y_cagr=-4.0
    )

    assert res.cash_accrual_divergence_flag
    assert res.forensic_score == 65.0
    assert any("Cash-Accrual Divergence" in flag for flag in res.red_flags)


def test_arbiter_forensic_data_truth_integration():
    """Verify Arbiter passes synthesized data to ForensicAuditor cleanly."""
    arb = Arbiter()
    call = arb.arbitrate("RELIANCE")

    assert call.symbol == "RELIANCE"
    assert call.verdict in ("Strong Buy", "Buy", "Accumulate", "Watch", "Avoid", "ABSTAIN")

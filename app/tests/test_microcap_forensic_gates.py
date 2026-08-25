"""Test Suite for Micro/Small-Cap Forensic & Liquidity Gate Engines."""

import pytest
from app.services.research.microcap_integrity_gate import evaluate_microcap_integrity_gate
from app.services.research.forensic_auditor import ForensicAuditor


def test_microcap_integrity_gate_pass():
    res = evaluate_microcap_integrity_gate(
        symbol="POLYCAB",
        target_portfolio_value_inr=10_000_000.0,
        promoter_pledge_pct=5.0,
        cfo_ebitda_ratio=0.85,
        asm_gsm_stage="CLEAN"
    )
    assert res.pass_all_gates
    assert res.status_code == "APPROVED"
    assert res.max_position_size_inr > 0.0
    assert len(res.veto_reasons) == 0


def test_microcap_integrity_gate_pledge_veto():
    res = evaluate_microcap_integrity_gate(
        symbol="SUZLON",
        promoter_pledge_pct=35.0
    )
    assert not res.pass_all_gates
    assert any("Promoter pledge" in r for r in res.veto_reasons)


def test_forensic_auditor_clean():
    auditor = ForensicAuditor()
    res = auditor.audit_equity("POLYCAB", related_party_pct=4.2)
    assert not res.governance_veto
    assert res.forensic_score >= 80.0
    assert len(res.red_flags) == 0


def test_forensic_auditor_resignation_veto():
    auditor = ForensicAuditor()
    res = auditor.audit_equity("XYZ_MICRO", auditor_resigned_recently=True)
    assert res.governance_veto
    assert any("auditor" in r.lower() for r in res.red_flags)

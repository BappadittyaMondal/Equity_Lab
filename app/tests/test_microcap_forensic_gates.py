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


def test_microcap_integrity_gate_fail_closed_insufficient_data(monkeypatch):
    """Verify microcap gate fails closed on bad/missing historical market data instead of defaulting to 5 Cr."""
    from app.services.research import microcap_integrity_gate
    
    # Mock get_history to raise exception or return empty dataframe
    monkeypatch.setattr(microcap_integrity_gate, "get_history", lambda *args, **kwargs: None)
    
    res = evaluate_microcap_integrity_gate("UNKNOWN_MICRO")
    assert not res.pass_all_gates
    assert res.status_code == "REJECTED_INSUFFICIENT_DATA"
    assert any("minimum 10 trading days" in r for r in res.veto_reasons)
    assert res.adv_20d_inr == 0.0


def test_portfolio_risk_malformed_state_fail_closed():
    """Verify portfolio risk engine rejects malformed open_positions state."""
    from app.services.risk.portfolio_risk import evaluate_portfolio_heat_and_risk
    
    res = evaluate_portfolio_heat_and_risk("TCS", open_positions="INVALID_STRING_PAYLOAD")
    assert res.gate11_status == "REJECTED_MALFORMED_STATE"
    assert res.current_portfolio_heat_pct == 0.0


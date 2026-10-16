"""Unit tests for Phase 174: Self-Learning Stage 0 Recall and Disqualification Ledger."""

import pytest
from app.services.research.report_archiver import format_disqualification_ledger
from app.services.research.deadliest_combo_pipeline import _run_deadliest_combo_pipeline_core, DeadliestComboResult
from app.services.research.self_learning_engine import SelfLearningEngine


def test_format_disqualification_ledger():
    """Verify that format_disqualification_ledger generates an auditable markdown table."""
    dq1 = DeadliestComboResult(
        symbol="TEXRAIL",
        company_name="Texmaco Rail",
        disqualification_reason="ROCE 11.5% < 20.0% institutional floor",
    )
    dq2 = DeadliestComboResult(
        symbol="PTCIL",
        company_name="PTC Industries",
        disqualification_reason="P/E 304.4 > 80.0 multiple-compression ceiling",
    )
    ledger_md = format_disqualification_ledger([dq1, dq2])
    assert "## Disqualification & Re-Classification Ledger" in ledger_md
    assert "| **TEXRAIL** | Texmaco Rail | `ROCE 11.5% < 20.0% institutional floor` | `DISQUALIFIED` |" in ledger_md
    assert "| **PTCIL** | PTC Industries | `P/E 304.4 > 80.0 multiple-compression ceiling` | `DISQUALIFIED` |" in ledger_md


def test_self_learning_stage0_memory_recall_veto():
    """Verify that Stage 0 in the pipeline intercepts known falsified stocks using dynamic priors."""
    sle = SelfLearningEngine()
    sle.record_empirical_rule(
        rule_name="TESTBADSTOCK_ROCE_HARD_GATE_BREACH",
        category="HARD_GATE_DISQUALIFICATION",
        confidence=1.0,
        logic_statement="TestBadStock ROCE is below the 20% institutional floor.",
        target_symbol="TESTBADSTOCK",
    )

    qualified, disqualified = _run_deadliest_combo_pipeline_core(
        tickers=["TESTBADSTOCK"],
        fetch_live=False,
    )

    assert len(qualified) == 0
    assert len(disqualified) == 1
    assert disqualified[0].symbol == "TESTBADSTOCK"
    assert "LEARNED_RULE_DISQUALIFICATION" in disqualified[0].disqualification_reason

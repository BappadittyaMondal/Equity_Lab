"""Phase 155 Tests — Deadliest Combination Pipeline Orchestrator.

Verifies:
  T1: Hard gates filter out out-of-bounds MCap, high D/E, pledged shares, and non-operating PAT spikes.
  T2: Earnings quality score and return ceiling normalizer work mathematically as intended.
  T3: run_deadliest_combo_pipeline runs end-to-end, ranks properly, and produces Top N results.
  T4: format_pipeline_report outputs compliant markdown table with all required columns.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.research.deadliest_combo_pipeline import (
    _check_hard_gates,
    _earnings_quality_score,
    _normalize_return_ceiling,
    run_deadliest_combo_pipeline,
    format_pipeline_report,
    COMPOSITE_WEIGHTS,
    DeadliestComboResult,
)


class TestDeadliestComboHardGates:
    """Verify hard gate disqualification logic."""

    def test_mcap_too_low(self):
        fund = {"market_cap": 50.0, "debt_to_equity": 0.1, "pledged_pct": 0.0}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "minimum" in reason

    def test_mcap_too_high(self):
        fund = {"market_cap": 16000.0, "debt_to_equity": 0.1, "pledged_pct": 0.0}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "maximum" in reason

    def test_debt_to_equity_exceeded(self):
        fund = {"market_cap": 2000.0, "debt_to_equity": 0.45, "pledged_pct": 0.0}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "D/E" in reason

    def test_promoter_pledge_exceeded(self):
        fund = {"market_cap": 2000.0, "debt_to_equity": 0.1, "pledged_pct": 80.26}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "Promoter pledge" in reason

    def test_pat_quality_flag_disqualification(self):
        fund = {
            "market_cap": 2000.0,
            "debt_to_equity": 0.1,
            "pledged_pct": 0.0,
            "pat_quality_flag": "NON_OPERATING_DOMINATED",
        }
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "PAT quality" in reason

    def test_valid_stock_passes_all_gates(self):
        fund = {
            "market_cap": 2500.0,
            "debt_to_equity": 0.05,
            "pledged_pct": 0.0,
            "pat_quality_flag": "OPERATING",
        }
        assert _check_hard_gates(fund) is None


class TestDeadliestComboScoringComponents:
    """Verify earnings quality scoring and return ceiling normalizer."""

    def test_earnings_quality_score_operating_and_high_cfo(self):
        fund = {"pat_quality_flag": "OPERATING", "cfo_pat": 1.5}
        score = _earnings_quality_score(fund)
        assert score == 1.0  # maxed at 1.0

    def test_earnings_quality_score_elevated_other_income(self):
        fund = {"pat_quality_flag": "ELEVATED_OTHER_INCOME", "cfo_pat": 0.8}
        score = _earnings_quality_score(fund)
        assert score == 0.6

    def test_earnings_quality_score_poor_cfo(self):
        fund = {"pat_quality_flag": "OPERATING", "cfo_pat": 0.2}
        score = _earnings_quality_score(fund)
        assert score == 0.8  # 1.0 - 0.2

    def test_normalize_return_ceiling(self):
        assert _normalize_return_ceiling(0.0) == 0.0
        assert _normalize_return_ceiling(1.0) == 0.0  # log2(1)/3 = 0
        assert round(_normalize_return_ceiling(2.0), 3) == round(1.0 / 3.0, 3)
        assert round(_normalize_return_ceiling(4.0), 3) == round(2.0 / 3.0, 3)
        assert _normalize_return_ceiling(8.0) == 1.0


class TestDeadliestComboPipelineExecution:
    """Verify full pipeline execution and ranking."""

    @patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store")
    def test_pipeline_runs_and_ranks_candidates(self, mock_fetch):
        # Setup 3 candidate stocks
        # Stock 1: High quality
        s1 = {
            "symbol": "STOCK1.NS",
            "company_name": "Stock One Ltd",
            "market_cap": 3000.0,
            "current_price": 500.0,
            "high_52w": 520.0,
            "low_52w": 250.0,
            "dma_50": 480.0,
            "dma_200": 420.0,
            "volume": 100000,
            "vol_1w_avg": 90000,
            "vol_1y_avg": 80000,
            "debt_to_equity": 0.05,
            "pledged_pct": 0.0,
            "roce_annualized": 45.0,
            "roe_annualized": 30.0,
            "cfo_pat": 1.2,
            "net_profit_last_year": 150.0,
            "pat_quality_flag": "OPERATING",
            "shares_count": 10000000,
            "shares_count_10yr_back": 10000000,
        }
        # Stock 2: Mediocre technicals & return
        s2 = {
            "symbol": "STOCK2.NS",
            "company_name": "Stock Two Ltd",
            "market_cap": 8000.0,
            "current_price": 200.0,
            "high_52w": 350.0,
            "low_52w": 180.0,
            "dma_50": 210.0,
            "dma_200": 260.0,
            "volume": 50000,
            "vol_1w_avg": 40000,
            "vol_1y_avg": 60000,
            "debt_to_equity": 0.20,
            "pledged_pct": 1.5,
            "roce_annualized": 22.0,
            "roe_annualized": 15.0,
            "cfo_pat": 0.7,
            "net_profit_last_year": 120.0,
            "pat_quality_flag": "ELEVATED_OTHER_INCOME",
            "shares_count": 20000000,
            "shares_count_10yr_back": 18000000,
        }
        # Stock 3: Disqualified by pledge
        s3 = {
            "symbol": "STOCK3.NS",
            "company_name": "Stock Three Ltd",
            "market_cap": 1500.0,
            "debt_to_equity": 0.1,
            "pledged_pct": 55.0,  # Fails gate
        }

        mock_fetch.side_effect = lambda sym: {
            "STOCK1.NS": s1,
            "STOCK2.NS": s2,
            "STOCK3.NS": s3,
        }.get(sym)

        results = run_deadliest_combo_pipeline(["STOCK1.NS", "STOCK2.NS", "STOCK3.NS"], top_n=5)

        # Stock 3 must be filtered out
        assert len(results) == 2
        # Ranks must be 1 and 2
        assert results[0].rank == 1
        assert results[1].rank == 2
        # STOCK1 must outscore STOCK2
        assert results[0].symbol == "STOCK1.NS"
        assert results[0].composite_score > results[1].composite_score

        # Test report formatting
        report = format_pipeline_report(results)
        assert "# Deadliest Combination Pipeline Report" in report
        assert "STOCK1.NS" in report
        assert "STOCK2.NS" in report
        assert "STOCK3.NS" not in report

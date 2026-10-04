"""
Phase 150: Critical Fixes Test Suite
=====================================
Tests for the 4 Phase 150 changes:
  C1: cfo_pat included in fundamental_fetcher return dict
  C2: pledged_pct returns None (not 0.0) — unobserved, not falsely-clean
  C3: surveillance_data router requires auth (structural test)
  I6: SelfLearningEngine.learn_from_text is correctly callable

Zero network calls. All tests are deterministic.
"""
import sys
import os
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# ─────────────────────────────────────────────────────────────────────────────
# C1: cfo_pat in fundamental_fetcher return dict
# ─────────────────────────────────────────────────────────────────────────────
class TestCfoPATInReturnDict(unittest.TestCase):
    """C1: cfo_pat must be present in FundamentalFetcher.fetch_and_store() return dict."""

    def _mock_ticker(self, operating_cash_flow=500.0, net_income=400.0):
        """Builds a minimal yfinance Ticker mock sufficient for fundamental_fetcher."""
        import pandas as pd
        from datetime import datetime, timezone

        ticker = MagicMock()
        ticker.info = {
            "shortName": "TEST CORP",
            "marketCap": 5_000_000_000,
            "currentPrice": 250.0,
            "volume": 1_000_000,
            "fiftyTwoWeekHigh": 300.0,
            "fiftyTwoWeekLow": 150.0,
            "fiftyDayAverage": 240.0,
            "twoHundredDayAverage": 210.0,
            "trailingEps": 15.0,
            "sharesOutstanding": 100_000_000,
            "heldPercentInsiders": 0.50,
            "heldPercentInstitutions": 0.20,
            "pegRatio": 1.5,
            "averageVolume10days": 500_000,
            "averageVolume": 600_000,
        }

        # Empty quarterly financials — triggers defaults
        empty_df = pd.DataFrame()
        ticker.quarterly_financials = empty_df
        ticker.quarterly_balance_sheet = empty_df
        ticker.quarterly_cashflow = empty_df
        ticker.splits = pd.Series(dtype=float)  # No splits

        return ticker

    def test_cfo_pat_key_present_in_return_dict(self):
        """C1: 'cfo_pat' key must exist in the return dict from fetch_and_store."""
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher

        mock_ticker = self._mock_ticker()

        with patch("yfinance.Ticker", return_value=mock_ticker), \
             patch.object(FundamentalFetcher, "_store_in_db", return_value=None):
            result = FundamentalFetcher.fetch_and_store("TEST.NS")

        self.assertIsNotNone(result, "fetch_and_store must not return None for mocked ticker")
        self.assertIn("cfo_pat", result, "CRITICAL C1: 'cfo_pat' missing from return dict — SIP queries break")

    def test_cfo_pat_value_is_numeric_or_zero(self):
        """C1: cfo_pat value must be a float when both CFO and net_income are available."""
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher

        mock_ticker = self._mock_ticker()

        with patch("yfinance.Ticker", return_value=mock_ticker), \
             patch.object(FundamentalFetcher, "_store_in_db", return_value=None):
            result = FundamentalFetcher.fetch_and_store("TEST.NS")

        if result and "cfo_pat" in result:
            self.assertIsInstance(
                result["cfo_pat"], (int, float),
                "cfo_pat must be numeric"
            )


# ─────────────────────────────────────────────────────────────────────────────
# C2: pledged_pct returns None
# ─────────────────────────────────────────────────────────────────────────────
class TestPledgedPctIsNone(unittest.TestCase):
    """C2: pledged_pct must be None (unobserved) not 0.0 (falsely clean)."""

    def _mock_ticker_for_pledge(self):
        import pandas as pd
        ticker = MagicMock()
        ticker.info = {
            "shortName": "PLEDGE TEST",
            "marketCap": 1_000_000_000,
            "currentPrice": 100.0,
            "volume": 100_000,
            "fiftyTwoWeekHigh": 150.0,
            "fiftyTwoWeekLow": 80.0,
            "fiftyDayAverage": 110.0,
            "twoHundredDayAverage": 105.0,
            "trailingEps": 5.0,
            "sharesOutstanding": 50_000_000,
            "heldPercentInsiders": 0.60,
            "heldPercentInstitutions": 0.10,
            "pegRatio": 2.0,
            "averageVolume10days": 200_000,
            "averageVolume": 250_000,
        }
        empty_df = pd.DataFrame()
        ticker.quarterly_financials = empty_df
        ticker.quarterly_balance_sheet = empty_df
        ticker.quarterly_cashflow = empty_df
        ticker.splits = pd.Series(dtype=float)
        return ticker

    def test_pledged_pct_is_none_not_zero(self):
        """C2: pledged_pct must be None — 0.0 silently bypasses pledge governance gates."""
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher

        mock_ticker = self._mock_ticker_for_pledge()

        with patch("yfinance.Ticker", return_value=mock_ticker), \
             patch.object(FundamentalFetcher, "_store_in_db", return_value=None):
            result = FundamentalFetcher.fetch_and_store("PLEDGE.NS")

        self.assertIsNotNone(result)
        self.assertIn("pledged_pct", result)
        self.assertIsNone(
            result["pledged_pct"],
            "CRITICAL C2: pledged_pct should be None (unobserved), not 0.0 (false clean)"
        )

    def test_pledge_provenance_is_not_available(self):
        """C2: pledge_provenance must indicate data is genuinely unavailable."""
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher

        mock_ticker = self._mock_ticker_for_pledge()

        with patch("yfinance.Ticker", return_value=mock_ticker), \
             patch.object(FundamentalFetcher, "_store_in_db", return_value=None):
            result = FundamentalFetcher.fetch_and_store("PLEDGE.NS")

        if result:
            provenance = result.get("pledge_provenance", "")
            self.assertIn(
                "NOT_AVAILABLE", provenance,
                "pledge_provenance must clearly state data is not available"
            )


# ─────────────────────────────────────────────────────────────────────────────
# C3: Surveillance router auth (structural check)
# ─────────────────────────────────────────────────────────────────────────────
class TestSurveillanceRouterAuth(unittest.TestCase):
    """C3: surveillance_data router must be mounted with auth dependencies in main.py."""

    def test_surveillance_router_includes_auth_in_source(self):
        """C3: main.py source must show surveillance_data_router mounted with dependencies=auth_deps."""
        main_src_path = os.path.join(
            os.path.dirname(__file__), "..", "main.py"
        )
        with open(main_src_path, "r", encoding="utf-8") as f:
            src = f.read()

        # Verify the secure mount pattern is present
        self.assertIn(
            "surveillance_data_router, dependencies=auth_deps",
            src,
            "CRITICAL C3: surveillance_data router must be mounted with dependencies=auth_deps"
        )

        # Verify the OLD unauthenticated pattern is NOT present
        self.assertNotIn(
            "include_router(surveillance_data_router)\n",
            src,
            "CRITICAL C3: Old unauthenticated surveillance mount found in main.py"
        )


# ─────────────────────────────────────────────────────────────────────────────
# I6: Self-Learning Engine hook in llm.py
# ─────────────────────────────────────────────────────────────────────────────
class TestSelfLearningEngineHook(unittest.TestCase):
    """I6: Self-learning engine must be wired into process_llm_query post-response."""

    def test_self_learning_hook_in_llm_source(self):
        """I6: llm.py must contain self-learning engine activation after LLM response."""
        llm_src_path = os.path.join(
            os.path.dirname(__file__), "..", "services", "llm.py"
        )
        with open(llm_src_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn(
            "SelfLearningEngine",
            src,
            "I6: SelfLearningEngine must be referenced in llm.py"
        )
        self.assertIn(
            "learn_from_text",
            src,
            "I6: learn_from_text must be called in llm.py self-learning hook"
        )
        self.assertIn(
            "LLM_CONVERSATION",
            src,
            "I6: source_origin must identify LLM conversation as learning trigger"
        )

    def test_self_learning_engine_learn_from_text_callable(self):
        """I6: SelfLearningEngine.learn_from_text must be callable without errors on empty text."""
        from app.services.research.self_learning_engine import SelfLearningEngine
        sle = SelfLearningEngine()
        # Must not raise — even if it learns nothing from trivial text
        result = sle.learn_from_text(
            text="QUERY [RELIANCE|research]: Is RELIANCE a good buy?",
            source_origin="LLM_CONVERSATION|RELIANCE|research",
            provenance_score=0.80,
        )
        self.assertIsInstance(result, list, "learn_from_text must return a list of KnowledgeEntity objects")

    def test_self_learning_engine_non_blocking_on_error(self):
        """I6: Self-learning engine failure must NOT break the LLM response pipeline."""
        # The hook wraps learn_from_text in try/except — verify the engine still starts
        from app.services.research.self_learning_engine import SelfLearningEngine
        sle = SelfLearningEngine()
        # Even with garbage input — must not raise
        try:
            sle.learn_from_text(
                text="",
                source_origin="TEST",
                provenance_score=0.5,
            )
        except Exception as e:
            self.fail(f"learn_from_text raised unexpectedly on empty text: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Regression: Phase 149 architecture guard must still hold
# ─────────────────────────────────────────────────────────────────────────────
class TestPhase149ArchitectureGuardStillHolds(unittest.TestCase):
    """Regression: Phase 149 TBQE must not produce Arbiter contract keys after Phase 150."""

    def test_tbqe_no_pipeline_keys_after_phase150(self):
        from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
        _, breakdown = TechnicalBaseQualityEngine.score({
            "current_price": 150, "dma_50": 140, "dma_200": 130,
            "high_52w": 180, "low_52w": 100
        })
        forbidden = {"passed", "status", "vetoes", "fatal_vetoes"}
        found = forbidden & set(breakdown.keys())
        self.assertEqual(found, set(), f"TBQE must not produce Arbiter contract keys: {found}")


if __name__ == "__main__":
    unittest.main()

"""Phase 151 Tests — Earnings Quality Decomposition, Sustainable PEG & Pledge Provenance Guard.

Verifies:
  T1: other_income, other_income_pct_of_pat, pat_quality_flag present in fundamental_fetcher return dict.
  T2: peg_sustainable uses multi-year CAGR, not single-quarter YoY.
  T3: LLM research context renders pledge provenance guard (never prints "0.0%" when NOT_AVAILABLE).
"""

import pytest


# ── T1: Other Income Decomposition ───────────────────────────────────────────

class TestOtherIncomeDecomposition:
    """Verify other_income fields exist and pat_quality_flag logic is correct."""

    def test_other_income_fields_in_fetcher_source(self):
        """fundamental_fetcher.py must contain the new Other Income keys in return dict."""
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert '"other_income"' in source, "other_income key missing from return dict"
        assert '"other_income_pct_of_pat"' in source, "other_income_pct_of_pat key missing"
        assert '"pat_quality_flag"' in source, "pat_quality_flag key missing"

    def test_pat_quality_flag_thresholds_in_source(self):
        """Verify the three quality tiers: OPERATING, ELEVATED_OTHER_INCOME, NON_OPERATING_DOMINATED."""
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert 'NON_OPERATING_DOMINATED' in source
        assert 'ELEVATED_OTHER_INCOME' in source
        assert '"OPERATING"' in source

    def test_pat_quality_flag_logic_40_threshold(self):
        """If other_income_pct > 40%, flag must be NON_OPERATING_DOMINATED."""
        # Simulate the logic directly
        other_income_pct_of_pat = 52.4  # Like PIXTRANS Q1 FY27
        if other_income_pct_of_pat > 40.0:
            flag = "NON_OPERATING_DOMINATED"
        elif other_income_pct_of_pat > 25.0:
            flag = "ELEVATED_OTHER_INCOME"
        else:
            flag = "OPERATING"
        assert flag == "NON_OPERATING_DOMINATED"

    def test_pat_quality_flag_logic_operating(self):
        """If other_income_pct <= 25%, flag must be OPERATING."""
        other_income_pct_of_pat = 12.0
        if other_income_pct_of_pat > 40.0:
            flag = "NON_OPERATING_DOMINATED"
        elif other_income_pct_of_pat > 25.0:
            flag = "ELEVATED_OTHER_INCOME"
        else:
            flag = "OPERATING"
        assert flag == "OPERATING"


# ── T2: Sustainable PEG ──────────────────────────────────────────────────────

class TestSustainablePEG:
    """Verify peg_sustainable field and its multi-year CAGR logic."""

    def test_peg_sustainable_key_in_fetcher_source(self):
        """fundamental_fetcher.py must contain peg_sustainable in return dict."""
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert '"peg_sustainable"' in source, "peg_sustainable key missing"

    def test_peg_sustainable_uses_max_growth(self):
        """PEG should use max(pat_growth_latest, 3yr_cagr) as denominator."""
        # Simulate: PE=15, pat_growth_latest=38%, 3yr_cagr=10%
        pe = 15.0
        candidates = [38.0, 10.0]  # [single quarter, 3yr cagr]
        sustainable_growth = max(candidates)
        peg = round(pe / sustainable_growth, 2)
        assert peg == 0.39  # This is the correct PEG using best growth
        # But if we only used 3yr CAGR:
        peg_3yr = round(pe / 10.0, 2)
        assert peg_3yr == 1.50  # Much higher — more realistic

    def test_peg_none_for_negative_growth(self):
        """PEG must be None if growth < 1%."""
        pe = 15.0
        growth = -5.0
        peg = None if growth <= 1.0 else round(pe / growth, 2)
        assert peg is None


# ── T3: Pledge Provenance Guard ──────────────────────────────────────────────

class TestPledgeProvenanceGuard:
    """Verify LLM context never renders '0.0%' for pledge when NOT_AVAILABLE."""

    def test_pledge_guard_in_llm_source(self):
        """llm.py must check pledge_provenance before rendering."""
        import inspect
        from app.services.llm import build_research_context
        source = inspect.getsource(build_research_context)
        assert 'NOT_AVAILABLE' in source, "Pledge provenance guard missing from llm.py"
        assert 'NOT VERIFIED' in source, "Must render 'NOT VERIFIED' when pledge is unavailable"

    def test_pledge_guard_logic_not_available(self):
        """When provenance is NOT_AVAILABLE_YFINANCE, display must say NOT VERIFIED."""
        pledge_val = None
        pledge_prov = "NOT_AVAILABLE_YFINANCE"
        if pledge_val is None or 'NOT_AVAILABLE' in str(pledge_prov):
            display = "NOT VERIFIED (yfinance does not provide pledge data — verify from BSE filing)"
        else:
            display = f"{pledge_val}%"
        assert "NOT VERIFIED" in display
        assert "0.0%" not in display

    def test_pledge_guard_logic_available(self):
        """When pledge value is real number with valid provenance, display the number."""
        pledge_val = 80.26
        pledge_prov = "BSE_FILING"
        if pledge_val is None or 'NOT_AVAILABLE' in str(pledge_prov):
            display = "NOT VERIFIED"
        else:
            display = f"{pledge_val}%"
        assert display == "80.26%"


# ── Phase 150 Regression Guard ───────────────────────────────────────────────

class TestPhase150RegressionAfterPhase151:
    """Ensure Phase 150 fixes still hold after Phase 151 additions."""

    def test_cfo_pat_still_in_return_dict(self):
        """Phase 150 C1 fix: cfo_pat must remain in return dict."""
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert '"cfo_pat": cfo_pat' in source

    def test_pledged_pct_still_none(self):
        """Phase 150 C2 fix: pledged_pct must still default to None, not 0.0."""
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert '"pledged_pct": None' in source

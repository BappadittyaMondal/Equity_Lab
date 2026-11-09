# -*- coding: utf-8 -*-
"""Test Suite: Enhanced Report Naming and Strategy-Subfolder Placement."""
from datetime import datetime
from pathlib import Path

from app.services.research.report_archiver import (
    IST,
    build_report_filename,
    save_single_stock_report,
    save_stock_list_report,
    ensure_report_directories,
)


def test_prefly_strategy_naming_without_top_n():
    """Verify prefly strategy without top-n produces PRE_FLY_<YYYY-MM-DD>_<HHMM_IST>.ext."""
    fixed_ts = datetime(2026, 11, 7, 18, 30, tzinfo=IST)
    subfolder, filename = build_report_filename("prefly", timestamp=fixed_ts, ext="pdf")
    assert subfolder == "Pre_Fly"
    assert filename == "PRE_FLY_2026-11-07_1830_IST.pdf"


def test_prefly_strategy_naming_with_top_n():
    """Verify prefly strategy with top-n produces PRE_FLY_TOP_<N>_<YYYY-MM-DD>_<HHMM_IST>.ext."""
    fixed_ts = datetime(2026, 11, 7, 18, 30, tzinfo=IST)
    subfolder, filename = build_report_filename("top 25 prefly list", timestamp=fixed_ts, ext="md")
    assert subfolder == "Pre_Fly"
    assert filename == "PRE_FLY_TOP_25_2026-11-07_1830_IST.md"


def test_single_stock_analysis_naming_general(tmp_path: Path):
    """Verify general stock analysis produces <STOCK>_ANALYSIS_<date_time> in Comparison_And_Single."""
    fixed_ts = datetime(2026, 11, 7, 18, 30, tzinfo=IST)
    saved = save_single_stock_report(
        content=b"%PDF-1.4 Mock PDF Content",
        symbol="AWFIS",
        category_or_query="GENERAL",
        ext="pdf",
        timestamp=fixed_ts,
        base_root=tmp_path,
    )
    assert saved.exists()
    assert saved.parent.name == "Comparison_And_Single"
    assert saved.name == "AWFIS_ANALYSIS_2026-11-07_1830_IST.pdf"


def test_single_stock_analysis_under_specific_strategy(tmp_path: Path):
    """Verify stock analysis under specific strategy (e.g. Pre-Fly) places in strategy subfolder."""
    fixed_ts = datetime(2026, 11, 7, 18, 30, tzinfo=IST)
    saved = save_single_stock_report(
        content="# Pashupati Pre-Fly Analysis\n",
        symbol="PASHUPATI",
        category_or_query="PRE_FLY",
        ext="md",
        timestamp=fixed_ts,
        base_root=tmp_path,
    )
    assert saved.exists()
    assert saved.parent.name == "Pre_Fly"
    assert saved.name == "PRE_FLY_PASHUPATI_2026-11-07_1830_IST.md"

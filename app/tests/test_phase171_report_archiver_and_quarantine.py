"""Phase 171 Test Suite — Automated Stock List Report Archiver & Quarantine Manager."""

from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.services.research.report_archiver import (
    CANONICAL_REPORT_SUBFOLDERS,
    IST,
    build_report_filename,
    ensure_report_directories,
    extract_top_n,
    quarantine_unnecessary_files,
    resolve_report_subfolder,
    save_stock_list_report,
)


def test_canonical_report_directories_exist():
    """Verify all 9 canonical strategy subfolders exist under Stocks_Analysis_Report/."""
    rep_root = ensure_report_directories()
    assert rep_root.is_dir()
    for sub in CANONICAL_REPORT_SUBFOLDERS:
        assert (rep_root / sub).is_dir(), f"Missing subfolder: {sub}"


def test_resolve_report_subfolder_across_all_8_user_categories():
    """Verify every user-requested category routes to its exact matching subfolder."""
    assert resolve_report_subfolder("give me top 25 prefly list") == ("Pre_Fly", "PRE_FLY")
    assert resolve_report_subfolder("top 10 deadliest combo stocks") == ("Deadliest_Combo", "DEADLIEST_COMBO")
    assert resolve_report_subfolder("dedlistcombo top 15") == ("Deadliest_Combo", "DEADLIEST_COMBO")
    assert resolve_report_subfolder("top 25 multibagger list") == ("Multibagger", "MULTIBAGGER")
    assert resolve_report_subfolder("top 15 micromultibagger stocks") == ("Micro_Multibagger", "MICRO_MULTIBAGGER")
    assert resolve_report_subfolder("top 10 sip stocks for 10 years") == ("SIP", "SIP")
    assert resolve_report_subfolder("top 10 swing 3 days") == ("Swing", "SWING_3D")
    assert resolve_report_subfolder("top 15 swing 10 days") == ("Swing", "SWING_10D")
    assert resolve_report_subfolder("top 25 swing 30 days") == ("Swing", "SWING_30D")
    assert resolve_report_subfolder("top 10 turnarround stocks") == ("Turnaround", "TURNAROUND")
    assert resolve_report_subfolder("top 15 value buying stocks") == ("Value_Buying", "VALUE_BUYING")


def test_extract_top_n_parsing():
    """Verify Top-N number extraction from user queries."""
    assert extract_top_n("give me top 25 prefly list") == 25
    assert extract_top_n("find Top-15 turnaround stocks") == 15
    assert extract_top_n("TOP_10 deadliest combo") == 10
    assert extract_top_n("best value buying stocks", default_n=10) == 10


def test_save_stock_list_report_writes_with_ist_timestamp(tmp_path: Path):
    """Verify save_stock_list_report writes to the exact subfolder with YYYY-MM-DD_HHMM_IST naming."""
    fixed_ts = datetime(2026, 10, 13, 11, 5, tzinfo=IST)
    saved = save_stock_list_report(
        content="# Top 25 Pre-Fly Stocks\n1. FRONTSP\n",
        category_or_query="user ask top 25 prefly list",
        timestamp=fixed_ts,
        base_root=tmp_path,
    )
    assert saved.exists()
    assert saved.parent.name == "Pre_Fly"
    assert saved.name == "PRE_FLY_TOP_25_2026-10-13_1105_IST.md"
    assert "FRONTSP" in saved.read_text(encoding="utf-8")


def test_quarantine_unnecessary_files_moves_stray_files_without_deleting(tmp_path: Path):
    """Verify quarantine_unnecessary_files moves non-canonical files into DELETION_REQUIRED without overwriting."""
    # Seed a canonical file and a stray file
    (tmp_path / "README.md").write_text("# Equity Lab", encoding="utf-8")
    (tmp_path / "temp_screen_dump.json").write_text('{"tmp": 1}', encoding="utf-8")
    del_dir = tmp_path / "DELETION_REQUIRED"
    del_dir.mkdir()
    # Pre-existing file inside DELETION_REQUIRED with same name must NEVER be overwritten or deleted
    (del_dir / "temp_screen_dump.json").write_text('{"original": true}', encoding="utf-8")

    moved = quarantine_unnecessary_files(base_root=tmp_path)
    assert len(moved) == 1
    assert (tmp_path / "README.md").exists()
    assert not (tmp_path / "temp_screen_dump.json").exists()
    # Both original and newly quarantined collision-renamed file exist inside DELETION_REQUIRED
    del_files = list(del_dir.iterdir())
    assert len(del_files) == 2
    assert (del_dir / "temp_screen_dump.json").read_text(encoding="utf-8") == '{"original": true}'

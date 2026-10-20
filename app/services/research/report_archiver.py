"""Automated Stock Analysis Report Archiver & Workspace Quarantine Manager (Phase 171).

Provides:
1. Deterministic routing of user-requested Top-N stock lists (Top 10 / 15 / 25, etc.)
   into `Stocks_Analysis_Report/<Category>/` with sortable IST date-time filenames:
   `<PREFIX>_TOP_<N>_<YYYY-MM-DD>_<HHMM_IST>.<ext>`
2. Collision-safe automatic quarantine of non-required / temporary root files into
   `DELETION_REQUIRED/` during project upgrades without ever deleting or overwriting
   existing files inside `DELETION_REQUIRED/`.
"""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine

IST = timezone(timedelta(hours=5, minutes=30))

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_ROOT_DIR_NAME = "Stocks_Analysis_Report"
QUARANTINE_DIR_NAME = "DELETION_REQUIRED"

# Canonical 9-subfolder taxonomy under Stocks_Analysis_Report/
CANONICAL_REPORT_SUBFOLDERS: Tuple[str, ...] = (
    "Deadliest_Combo",
    "Pre_Fly",
    "Multibagger",
    "Micro_Multibagger",
    "SIP",
    "Swing",
    "Turnaround",
    "Value_Buying",
    "Comparison_And_Single",
)

# Maps canonical intent / alias keys -> (Subfolder Name, Filename Prefix)
INTENT_TO_FOLDER_AND_PREFIX: Dict[str, Tuple[str, str]] = {
    "DEADLIEST_COMBO": ("Deadliest_Combo", "DEADLIEST_COMBO"),
    "DEADLIEST": ("Deadliest_Combo", "DEADLIEST_COMBO"),
    "DEDLISTCOMBO": ("Deadliest_Combo", "DEADLIEST_COMBO"),
    "PRE_FLY": ("Pre_Fly", "PRE_FLY"),
    "PREFLY": ("Pre_Fly", "PRE_FLY"),
    "PRE_FLY_IGNITION": ("Pre_Fly", "PRE_FLY"),
    "MULTIBAGGER": ("Multibagger", "MULTIBAGGER"),
    "KEDIA_SMILE": ("Multibagger", "MULTIBAGGER_KEDIA_SMILE"),
    "KACHOLIA_SCALABILITY": ("Multibagger", "MULTIBAGGER_KACHOLIA"),
    "AGRAWAL_INFLECTION": ("Multibagger", "MULTIBAGGER_AGRAWAL"),
    "MICRO_MULTIBAGGER": ("Micro_Multibagger", "MICRO_MULTIBAGGER"),
    "MICROMULTIBAGGER": ("Micro_Multibagger", "MICRO_MULTIBAGGER"),
    "EARLY_MICROCAP": ("Micro_Multibagger", "MICRO_MULTIBAGGER"),
    "SIP_COMPOUNDER": ("SIP", "SIP"),
    "SIP": ("SIP", "SIP"),
    "SWING_3D": ("Swing", "SWING_3D"),
    "SWING3": ("Swing", "SWING_3D"),
    "SWING_10D": ("Swing", "SWING_10D"),
    "SWING10": ("Swing", "SWING_10D"),
    "POSITIONAL_30D": ("Swing", "SWING_30D"),
    "SWING_30D": ("Swing", "SWING_30D"),
    "SWING30": ("Swing", "SWING_30D"),
    "SWING_POSITIONAL": ("Swing", "SWING_POSITIONAL"),
    "SWING": ("Swing", "SWING"),
    "TURNAROUND": ("Turnaround", "TURNAROUND"),
    "TURNARROUND": ("Turnaround", "TURNAROUND"),
    "VALUE_BUYING": ("Value_Buying", "VALUE_BUYING"),
    "VALUEBUYING": ("Value_Buying", "VALUE_BUYING"),
    "VALUE": ("Value_Buying", "VALUE_BUYING"),
    "PEER_COMPARE": ("Comparison_And_Single", "COMPARISON"),
    "GENERAL": ("Comparison_And_Single", "STOCK_ANALYSIS"),
}

# Canonical root files & directories required by the project (never quarantined)
CANONICAL_ROOT_FILES: Set[str] = {
    ".dockerignore",
    ".env",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    ".python-version",
    ".vercelignore",
    "AGENTS.md",
    "AI_Growth_Arbitrage_Engine_Institutional_Grade.md",
    "API_DOCUMENTATION.md",
    "API_KEYS_CONFIG.env",
    "API_KEYS_CONFIG.env.template",
    "API_PROVIDERS_AND_FREE_TIERS_GUIDE.md",
    "API_SURFACE.md",
    "DEPLOYMENT_GUIDE.md",
    "DESIGN.md",
    "DISASTER_RECOVERY.md",
    "EQUITY_BRAIN_MASTER_PROMPT.md",
    "EQUITY_LAB_BUNDLE_INSTRUCTIONS.md",
    "EQUITY_LAB_PROJECT_INSTRUCTION_PROMPT.md",
    "GEMINI.md",
    "KNOWLEDGE_SUMMERY.md",
    "MASTER_PROJECT_STOCK_DIRECTORY.md",
    "METHODOLOGY.md",
    "POSTMORTEM.md",
    "PROJECT_ARCHITECTURE_OVERVIEW.md",
    "README.md",
    "SECURITY_CHECKLIST.md",
    "UPGRADE_ROADMAP_SUMMARY.md",
    "alembic.ini",
    "conformal_calibration_cache.json",
    "ierl_research.db",
    "pytest.ini",
    "requirements.txt",
    "vercel.json",
}

CANONICAL_ROOT_DIRS: Set[str] = {
    ".git",
    ".github",
    ".pytest_cache",
    ".pytest_temp",
    ".venv",
    "venv",
    "__pycache__",
    "alembic",
    "app",
    "canonical_source",
    "data",
    "DELETION_REQUIRED",
    "docs",
    "frontend_deploy",
    "scripts",
    "Stocks_Analysis_Report",
    "Smart_Suparstar_Investor_Selection",
}


def ensure_report_directories(base_root: Optional[Path] = None) -> Path:
    """Ensure `Stocks_Analysis_Report/` and all 9 canonical strategy subfolders exist."""
    root = base_root or PROJECT_ROOT
    reports_root = root / REPORTS_ROOT_DIR_NAME
    reports_root.mkdir(parents=True, exist_ok=True)
    for sub in CANONICAL_REPORT_SUBFOLDERS:
        sub_dir = reports_root / sub
        sub_dir.mkdir(parents=True, exist_ok=True)
        gitkeep = sub_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
    return reports_root


def extract_top_n(query_or_title: str, default_n: int = 10) -> int:
    """Extract requested Top-N count (e.g. 'top 25 prefly list' -> 25)."""
    if not query_or_title:
        return default_n
    m = re.search(r"\btop[\s_\-]*(\d{1,3})\b", query_or_title, flags=re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 500:
            return val
    return default_n


def resolve_report_subfolder(category_or_query: str) -> Tuple[str, str]:
    """Resolve any category key, alias, or natural-language user query to (Subfolder, Prefix)."""
    raw = (category_or_query or "").strip()
    if not raw:
        return ("Comparison_And_Single", "STOCK_ANALYSIS")

    norm_key = re.sub(r"[\s\-]+", "_", raw.upper())
    if norm_key in INTENT_TO_FOLDER_AND_PREFIX:
        return INTENT_TO_FOLDER_AND_PREFIX[norm_key]

    # Check direct substring keywords for rapid explicit matching
    q_low = raw.lower()
    if "deadliest" in q_low or "dedlist" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["DEADLIEST_COMBO"]
    if "pre-fly" in q_low or "prefly" in q_low or "pre fly" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["PRE_FLY"]
    if "micro" in q_low and "multibagger" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["MICRO_MULTIBAGGER"]
    if "multibagger" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["MULTIBAGGER"]
    if re.search(r"\bsip\b", q_low):
        return INTENT_TO_FOLDER_AND_PREFIX["SIP_COMPOUNDER"]
    if "turnaround" in q_low or "turnarround" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["TURNAROUND"]
    if "value" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["VALUE_BUYING"]
    if "swing" in q_low or "positional" in q_low:
        if re.search(r"\b3\s*d|\b3\s*day", q_low):
            return INTENT_TO_FOLDER_AND_PREFIX["SWING_3D"]
        if re.search(r"\b10\s*d|\b10\s*day", q_low):
            return INTENT_TO_FOLDER_AND_PREFIX["SWING_10D"]
        if re.search(r"\b30\s*d|\b30\s*day", q_low):
            return INTENT_TO_FOLDER_AND_PREFIX["POSITIONAL_30D"]
        return INTENT_TO_FOLDER_AND_PREFIX["SWING"]
    if "kedia" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["KEDIA_SMILE"]
    if "kacholia" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["KACHOLIA_SCALABILITY"]
    if "mukul" in q_low or "agrawal" in q_low:
        return INTENT_TO_FOLDER_AND_PREFIX["AGRAWAL_INFLECTION"]

    # Fallback to QueryAdaptiveConstraintEngine intent detection
    if hasattr(QueryAdaptiveConstraintEngine, "detect_query_intent"):
        primary = QueryAdaptiveConstraintEngine.detect_query_intent(raw)
    elif hasattr(QueryAdaptiveConstraintEngine, "detect_intent"):
        res = QueryAdaptiveConstraintEngine.detect_intent(raw)
        primary = res.get("primary_intent", "GENERAL") if isinstance(res, dict) else str(res)
    else:
        primary = "GENERAL"
    return INTENT_TO_FOLDER_AND_PREFIX.get(primary, ("Comparison_And_Single", "STOCK_ANALYSIS"))


def build_report_filename(
    category_or_query: str,
    top_n: Optional[int] = None,
    ext: str = "md",
    timestamp: Optional[datetime] = None,
) -> Tuple[str, str]:
    """Return (subfolder_name, filename) with IST date-time stamp."""
    subfolder, prefix = resolve_report_subfolder(category_or_query)
    n_val = top_n if (top_n is not None and top_n > 0) else extract_top_n(category_or_query, default_n=10)
    ts = (timestamp or datetime.now(IST)).astimezone(IST)
    clean_ext = ext.lstrip(".")
    filename = f"{prefix}_TOP_{n_val}_{ts.strftime('%Y-%m-%d_%H%M_IST')}.{clean_ext}"
    return subfolder, filename


def save_stock_list_report(
    content: str | bytes,
    category_or_query: str,
    top_n: Optional[int] = None,
    ext: str = "md",
    timestamp: Optional[datetime] = None,
    base_root: Optional[Path] = None,
) -> Path:
    """Save a Top-N stock analysis report into the matching `Stocks_Analysis_Report/<Subfolder>/` directory."""
    reports_root = ensure_report_directories(base_root=base_root)
    subfolder, filename = build_report_filename(
        category_or_query=category_or_query,
        top_n=top_n,
        ext=ext,
        timestamp=timestamp,
    )
    target_path = reports_root / subfolder / filename
    if isinstance(content, bytes):
        target_path.write_bytes(content)
    else:
        target_path.write_text(content, encoding="utf-8")
    return target_path


def format_disqualification_ledger(disqualified_results: List[Any]) -> str:
    """Format disqualified stocks into a clean, auditable Markdown Disqualification Ledger."""
    if not disqualified_results:
        return ""
    lines = [
        "\n## Disqualification & Re-Classification Ledger",
        "The following candidates were evaluated and rejected by institutional hard gates:\n",
        "| Symbol | Company Name | Hard Gate Failure Reason | Status |",
        "|:---|:---|:---|:---:|",
    ]
    for dq in disqualified_results:
        sym = getattr(dq, "symbol", "UNKNOWN")
        name = getattr(dq, "company_name", sym)
        reason = getattr(dq, "disqualification_reason", "Unspecified hard gate failure")
        lines.append(f"| **{sym}** | {name} | `{reason}` | `DISQUALIFIED` |")
    lines.append("")
    return "\n".join(lines)


def quarantine_unnecessary_files(base_root: Optional[Path] = None) -> List[Path]:
    """Automatically move any non-required root files or scratch files into `DELETION_REQUIRED/`.

    Guarantees:
    - Never deletes any file.
    - Never overwrites an existing file inside `DELETION_REQUIRED/` (appends IST timestamp if collision).
    - Preserves all canonical project files and directories untouched.
    """
    root = base_root or PROJECT_ROOT
    del_dir = root / QUARANTINE_DIR_NAME
    del_dir.mkdir(parents=True, exist_ok=True)
    moved_paths: List[Path] = []
    ts_suffix = datetime.now(IST).strftime("%Y%m%d_%H%M%S")

    def _safe_move_to_quarantine(src_path: Path, custom_name: Optional[str] = None) -> Path:
        target_name = custom_name or src_path.name
        dst_path = del_dir / target_name
        if dst_path.exists():
            dst_path = del_dir / f"{ dst_path.stem }_{ts_suffix}{ dst_path.suffix }"
        shutil.move(str(src_path), str(dst_path))
        moved_paths.append(dst_path)
        return dst_path

    for item in sorted(root.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_file():
            if item.name not in CANONICAL_ROOT_FILES:
                _safe_move_to_quarantine(item)
        elif item.is_dir():
            if item.name not in CANONICAL_ROOT_DIRS and not item.name.startswith("CONSOLIDATED"):
                # Flatten files inside non-canonical root directories (e.g. scratch/) into DELETION_REQUIRED/
                for sub_item in sorted(item.rglob("*")):
                    if sub_item.is_file():
                        rel_flat = str(sub_item.relative_to(root)).replace("\\", "__").replace("/", "__")
                        _safe_move_to_quarantine(sub_item, custom_name=rel_flat)
                shutil.rmtree(item, ignore_errors=True)

    return moved_paths

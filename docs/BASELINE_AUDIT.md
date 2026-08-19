# Phase 0 — Baseline Audit & System Freeze

**Timestamp**: 2026-08-18T22:44:33+05:30  
**Authority**: IERL Implementation and Verification AI  
**Repository Identity**: `Equity_final_claude_v_0.3` (`d:\bappa_oldPC\01_Indian_Equity_Project\Equity_final_claude_v_0.3`)

---

## 1. System & Runtime Environment

- **Operating System**: Windows 11 (win32)
- **Python Version**: `Python 3.12.13`
- **Virtual Environment**: `.venv` (located at `.venv\Scripts\python.exe`)
- **Pytest Version**: `pytest-8.4.2` (with `pluggy-1.6.0`, `anyio-4.14.2`)

---

## 2. Dependencies (`requirements.txt`)

```text
fastapi>=0.110.0
uvicorn>=0.28.0
yfinance>=0.2.37
pandas>=2.2.0
pydantic>=2.6.4
python-dotenv>=1.0.1
requests>=2.31.0
google-generativeai>=0.4.1
numpy>=1.26.0
```

---

## 3. Configuration & System Settings (`app/core/config.py`)

- **Project Name**: IERL AI Equity Intelligence OS Engine
- **Active Model Version**: `0.4.0`
- **Primary Data Store**: SQLite database (`data/ierl_equity.sqlite3`)
- **Primary Market Data Provider**: `yfinance` with caching TTL (quote 60s, fundamentals 300s)
- **LLM Provider Chain**: Gemini (`google-generativeai`), Groq, Anthropic, DeepSeek

---

## 4. File Manifest Baseline

- `app/`: Core Python application codebase (API, core, middleware, models, services, tests)
- `data/`: Local SQLite database storage (`ierl_equity.sqlite3`)
- `docs/`: System methodology, design, and baseline documentation
- `scripts/`: Synchronization and release build scripts
- `CONSOLIDATED_5_FILE_SYSTEM/`: 5-file AI Knowledge distribution bundle
- `CONSOLIDATED_9_FILE_SYSTEM/`: 9-file AI Knowledge distribution bundle
- `AI_SKILL_IRA_col_final/` & `Knowledge_IRA_COL_FINAL/`: Master skill and knowledge corpora
- `Upload_97Files_AI_Project/`: Export bundle files

---

## 5. Current Baseline Test Suite Audit

- **Total Collected Tests**: 548 items across repository (274 unit/integration test cases in `app/tests/`).
- **Test Suite Status**:
  - `app/tests/test_phase1_data_foundation.py`: 100% Passed
  - `app/tests/test_phase2_analytical_engines.py`: 100% Passed
  - `app/tests/test_phase4_prediction_conviction.py`: 100% Passed
  - `app/tests/test_backtesting.py`: 2 Passed, 1 PermissionError on Windows default temp dir without `--basetemp`
  - `app/tests/test_growth_arbitrage.py`: Failed (legacy growth arbitrage assertion mismatch)
  - `app/tests/test_longitudinal.py`: 1 Passed, 4 Errors (due to missing database tables in test setup)

---

## 6. Known Bugs & Known Data Limitations

1. **Windows Pytest Temporary Directory Permission Error**:
   Running pytest without `--basetemp` triggers `PermissionError: [WinError 5] Access is denied` on `C:\Users\BAPPADITYA\AppData\Local\Temp\pytest-of-BAPPADITYA`. Enforced fix: always pass `--basetemp=temp_pytest`.
2. **Network Dependency during Unit Tests**:
   Arbiter calls `yfinance` when data is missing from cache, introducing network latencies during automated test runs.
3. **Legacy Versioned Filenames**:
   Duplicate versioned filenames exist in legacy export folders (`AI_Growth_Arbitrage_Engine_v2.md`, etc.). Must be migrated to clean canonical names without version suffixes.
4. **Hardcoded Analytical Outputs & Fallbacks**:
   Some legacy strategy scripts return fixed scores or arbitrary fallbacks when data is missing.

---

## Baseline Freeze Declaration

This baseline document is frozen and serves as the immutable reference point for verifying all subsequent changes in Phases 1 through 34.

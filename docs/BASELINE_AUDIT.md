# Phase 0 — Baseline Audit & System Verification

> **IMPORTANT NOTICE FOR DEVELOPERS & CI**: This document is a point-in-time snapshot. It must be regenerated after every significant commit or pre-release pass. The automated GitHub Actions CI workflow (`.github/workflows/ci.yml`) is the authoritative live source of truth for repository health and test status.

**Latest Audit Timestamp**: 2026-08-21T00:47:00+05:30  
**Authority**: IERL Release & Hardening Engineer  
**Repository Identity**: `Equity_Lab_v_0.0` (`d:\bappa_oldPC\01_Indian_Equity_Project\Equity_Lab_v_0.0`)

---

## 1. System & Runtime Environment

- **Operating System**: Windows 11 / Windows 10 (win32)
- **Python Version**: `Python 3.14.6` (compatible with standard Python 3.11+ environments)
- **Pytest Version**: `pytest-9.1.1` (with `pluggy-1.6.0`, `anyio-4.14.2`)
- **CI / CD Pipeline**: GitHub Actions (`.github/workflows/ci.yml`) with automated secret scanning, preflight checks, full pytest suite, and pip-audit.

---

## 2. Pinned Dependencies (`requirements.txt`)

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

- **Project Name**: Equity Lab
- **Active Model Version**: `0.0.0`
- **Primary Data Store**: Point-in-time SQLite database (`data/ierl_equity.sqlite3`)
- **Primary Market Data Provider**: `yfinance` with caching TTL (quote 60s, fundamentals 300s)
- **LLM Provider Chain**: Multi-LLM interchangeability supporting Gemini (`google-generativeai`), Groq, Anthropic Claude, DeepSeek, Kimi/Moonshot, OpenAI ChatGPT.
- **Security & Secret Safeguards**: Automated credential scanner (`scripts/check_no_real_secrets.py`) integrated into CI.

---

## 4. File Manifest Baseline

- `app/`: Core Python application codebase (API, core, middleware, models, services, strategies, tests)
- `data/`: Local SQLite database storage (`ierl_equity.sqlite3`)
- `docs/`: System methodology, design, API contracts, and baseline documentation
- `scripts/`: Build tools, canonical manifest generators, secret scanners, and preflight checks
- `canonical_source/`: Canonical source for Domain Knowledge and AI Skill reference trees
- `CONSOLIDATED_5_FILE_SYSTEM/`: 5-file AI Knowledge distribution bundle
- `CONSOLIDATED_9_FILE_SYSTEM/`: 9-file AI Knowledge distribution bundle
- `frontend_deploy/`: Production HTML/CSS/JS frontend application

---

## 5. Live Test Suite Audit Results

- **Command Executed**: `python -m pytest app/tests/ -v`
- **Execution Timestamp**: 2026-08-21T00:47:00+05:30
- **Total Test Cases Executed**: 317 unit/integration test cases across `app/tests/`
- **Test Suite Results**:
  - **Passed**: 317
  - **Failed**: 0
  - **Errors**: 0
  - **Pass Rate**: **100.0%**
- **Test Breakdown by Service Domain**:
  - `app/tests/test_phase1_data_foundation.py`: 100% PASSED
  - `app/tests/test_phase2_analytical_engines.py`: 100% PASSED
  - `app/tests/test_phase3_decision_brain.py`: 100% PASSED
  - `app/tests/test_phase4_prediction_conviction.py`: 100% PASSED
  - `app/tests/test_phase5_learning_loop.py`: 100% PASSED
  - `app/tests/test_phase6_monitoring.py`: 100% PASSED
  - `app/tests/test_quality_growth_screener.py`: 100% PASSED
  - `app/tests/test_security.py`: 100% PASSED
  - `app/tests/test_strategies.py`: 100% PASSED
  - `app/tests/test_watchlist.py`: 100% PASSED

---

## 6. System Status & Known Scope Decision Boundaries

Per `docs/SCOPE_DECISION_v0.0.md`:
1. **Single Data-Source Dependency**: Market data relies primarily on `yfinance` for free-tier data ingestion with fallback caching.
2. **Strategy Module Classifications**: Active production strategy modules vs. suspended/coming-soon strategy modules are registered deterministically in `app/services/strategies/registry.py`.
3. **Confidence Scoring Terminology**: All conviction outputs represent heuristic analytical scores (0–100 scale) and are strictly labeled as heuristic conviction/scores, never as mathematical statistical probabilities.
4. **Secret Scrubbing**: All environment configurations strictly use placeholder templates (`your_*_api_key_here`). Real credentials are strictly prohibited from codebase files.

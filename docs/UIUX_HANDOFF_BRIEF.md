# UI/UX Design & Frontend Integration Handoff Brief

> **Target Audience**: Frontend Engineers, UI/UX Designers, API Integrators  
> **Backend Contract Source of Truth**: [`docs/api_contract.json`](file:///d:/bappa_oldPC/01_Indian_Equity_Project/Equity_Lab_v_0.0/docs/api_contract.json)  
> **Timestamp**: 2026-08-21T00:50:00+05:30  
> **Version Baseline**: `v0.0.0-uiux-ready`

---

## 1. Authentication & Security Model

The backend API enforces an explicit security tier structure based on configuration (`SECURITY_AUTHENTICATION_ENABLED`):

### Public / Unauthenticated Endpoints (No API Key Required)
These endpoints are open and accessible by the frontend for public dashboard status, market ticker tape, and health diagnostics:
- `GET /api/v1/health`: System health and version check
- `GET /api/v1/readiness`: Readiness probe
- `GET /api/v1/ticker-strip`: Scrolling market quotes tape
- `GET /api/v1/regime`: Macro market regime status (VIX, Nifty level)

### Product / Analytical Endpoints (Requires `X-API-Key` Header when Auth Enabled)
Analytical and conviction endpoints require the `X-API-Key` HTTP request header:
- `GET /api/v1/decision/{symbol}`: Full Arbiter conviction synthesis
- `POST /api/v1/compare`: Multi-ticker comparative analysis
- `GET /api/v1/research/*`: Engine specific research endpoints (`/growth-arbitrage`, `/expectation-gap`, etc.)
- `GET /api/v1/strategies` & `/run`: Strategy module catalog and execution
- `GET /api/v1/watchlist` & `POST/DELETE`: User watchlist management

### Data Ingestion / Write Endpoints (Requires `X-Data-Write-Key` Header)
Write endpoints under `/api/v1/data/*` require a separate administrative key (`X-Data-Write-Key`). Frontend UI components must **not** attempt client-side raw data writes directly.

---

## 2. Mandatory UI Copy & Governance Rules (Confidence Labeling)

> **CRITICAL GOVERNANCE MANDATE** (per `docs/SCOPE_DECISION_v0.0.md`):
> **NEVER** use the word **"probability"** or imply statistical mathematical certainty when displaying scores, conviction ratings, or analytical outputs in the UI.

### Mandatory UI Terminology Rules:
1. **Scores (0–100 scale)**: Always label as **"Conviction Score"**, **"Heuristic Score"**, or **"Analytical Score"**.
2. **Confidence Tiers**: Label as **"Confirmed"**, **"Probable"**, or **"Speculative"** based on data availability and engine consensus.
3. **Verdict Categories**:
   - `Conviction Score >= 75`: **High Conviction Buy**
   - `60 <= Conviction Score < 75`: **Watch / Accumulate**
   - `Conviction Score < 60`: **Avoid / Neutral**
4. **Disclaimers**: Every conviction card must include the standard footer disclaimer:  
   *"Analytical scores represent heuristic evaluation based on published historical observations and multi-engine consensus, not guaranteed statistical probabilities or financial advice."*

---

## 3. Strategy Module Registry Status (Production vs. Suspended)

The UI must dynamically read status from `GET /api/v1/strategies` and render modules accordingly:

### Active Production Modules (17 Expert Modules + 7 Research Engines)
- **Expert Modules**: `A1`, `A3`, `B4`, `B5`, `B6`, `B7`, `B8`, `C9`, `C10`, `C11`, `C12`, `C13`, `C14`, `D15`, `D16`, `D17`, `D18`
- **Research Engines**:
  - `E1`: Growth Inflection Engine
  - `E2`: Turnaround Stage Engine
  - `E3`: Growth vs Market Recognition Gap Engine
  - `E4`: Multi-Factor Multibagger Intelligence Screener
  - `E5`: AI Growth Arbitrage & DCF Valuation Engine
  - `E6`: Quality-Growth Candidate Screener (Pre-Filter)
  - `E7`: Expectation Gap Engine

### Suspended Modules (UI Must Grey Out or Show Warning Badge)
- **Module `A2` (Zero-DTE Range Option Selling Engine)**:
  - **Status**: `suspended`
  - **UI Requirement**: Render with a grayed-out "Suspended" badge and tooltip notice:  
    *"Strategy suspended pending live option chain data pipeline activation."*

---

## 4. Known Backend Data & System Limitations

The UI design must transparently reflect the current backend capabilities:

1. **Single Market Data Source**: Free-tier market data relies on `yfinance` with fallback caching. High-frequency or real-time tick charts should indicate quote timestamps.
2. **No Live Earnings-Revision Feed**: Consensus earnings revisions rely on historical quarterly observations and point-in-time financial statement parses.
3. **Validated Sample Size**: Empirical validation reports (`docs/validation_report.md`) reflect historical backtest outcomes across the Nifty 500 universe.
4. **Variant Perception Fields**: Endpoint responses from `/api/v1/decision/{symbol}` contain detailed `variant_perception` breakdown objects (Market Consensus vs IERL Variant Thesis) which should be highlighted in dedicated UI panels.

---

## 5. API Endpoint Coverage & Integration Backlog

### Endpoints Currently Integrated in Prototype Frontend (`frontend_deploy/`):
- `/api/v1/health`
- `/api/v1/ticker-strip`
- `/api/v1/regime`
- `/api/v1/strategies`
- `/api/v1/ticker/{symbol}/history`
- `/api/v1/decision/{symbol}`
- `/api/v1/query`
- `/api/v1/watchlist`
- `/api/v1/digest/watchlist`

### High-Priority Backend Endpoints Available for Full UI Integration:
- `E7 Expectation Gap`: `/api/v1/research/expectation-gap?symbol=XYZ`
- `C14 / E2 Turnaround Diagnostic`: `/api/v1/research/turnaround-stage?symbol=XYZ`
- `Governance & Forensic Quality (D15/C13)`: `/api/v1/research/governance-quality?symbol=XYZ`
- `Multi-Ticker Comparison`: `/api/v1/compare` [POST]
- `Prediction Ledger & Model Drift`: `/api/v1/monitoring/prediction-ledger`, `/api/v1/monitoring/drift`
- `Point-in-Time Timeline`: `/api/v1/data/companies/{symbol}/timeline`

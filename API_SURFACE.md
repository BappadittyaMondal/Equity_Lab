# Equity Lab — Frozen API Surface Contract (`API_SURFACE.md`)

Version: `1.0.0-PROD`  
Base Path: `/api/v1`

---

## 1. Executive Summary & UI Integration Contract

This document freezes the backend API surface for **Equity Lab UI/UX Integration**. All endpoints are live, fully typed with Pydantic V2 schemas, enforce point-in-time data boundaries, handle explicit `DataMode` status (`LIVE`, `RECENT`, `CACHED`, `STALE`, `INSUFFICIENT`, `ERROR`), and return deterministic responses.

---

## 2. Core Endpoint Specifications

### 2.1 Health & System Diagnostics
- **`GET /api/v1/health`**
  - **Description**: Verifies live database, cache, market feeds, and system environment status.
  - **Auth**: None required.
  - **Response Schema**:
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-08-21T15:41:15Z",
      "environment": "production",
      "db_connected": true,
      "providers": {
        "yfinance": "LIVE",
        "yahoo_direct": "LIVE",
        "nse_india": "CACHED"
      }
    }
    ```

### 2.2 Ticker & Market Data
- **`GET /api/v1/ticker/{symbol}`**
  - **Description**: Fetches normalized market quote, price metrics, and data mode header.
  - **Parameters**: `symbol` (e.g. `RELIANCE` or `RELIANCE.NS`)
  - **Response Schema**:
    ```json
    {
      "symbol": "RELIANCE.NS",
      "price": 2850.50,
      "change": 15.20,
      "change_pct": 0.54,
      "high_52w": 3020.00,
      "low_52w": 2220.00,
      "pe_ratio": 24.8,
      "market_cap_cr": 1928400.0,
      "data_mode": "LIVE",
      "as_of": "2026-08-21T15:41:15Z"
    }
    ```

- **`GET /api/v1/regime`**
  - **Description**: Returns live India VIX, Nifty 200DMA distance, FII/DII flow metrics, and regime classification (`CALM`, `ELEVATED`, `VOLATILE`, `CRISIS`).

- **`GET /api/v1/ticker-strip`**
  - **Description**: Lightweight ticker tape quotes for benchmark indices (Nifty 50, Bank Nifty, Nifty Smallcap 100, India VIX).

---

### 2.3 Conviction & Decision Brain
- **`GET /api/v1/decision/{symbol}`**
  - **Description**: Runs Arbiter decision engine across all 18 strategy modules, forensic engines, and debate brain. Auto-logs call to `prediction_ledger`.
  - **Parameters**: `symbol` (str), `as_of` (optional ISO-8601 string)
  - **Response Schema**:
    ```json
    {
      "symbol": "RELIANCE.NS",
      "verdict": "Buy",
      "conviction_score": 88,
      "confidence_tier": "Confirmed",
      "primary_thesis": "Strong retail margin expansion and FCF inflection combined with clean Beneish M-Score (-2.45).",
      "contributing_engines": ["E1_GROWTH_INFLECTION", "E3_GROWTH_GAP", "B8_SEPA"],
      "contradicting_engines": [],
      "vetoes_triggered": [],
      "audit_trail": {
        "decision_id": 1042,
        "model_version": "1.0.0-PROD-ML-LOGISTIC",
        "data_mode": "LIVE",
        "why_explainer": "Verdict: Buy (Score: 88/100). Supported by E1 Growth Inflection and E3 Expectation Gap. No forensic vetoes triggered."
      }
    }
    ```

---

### 2.4 Multibagger Screener & Research MVP
- **`GET /api/v1/research/multibagger-screener?symbol={symbol}`**
  - **Description**: Multi-factor composite evaluation combining E1 Inflection (30%), E2 Turnaround (25%), E3 Expectation Gap (20%), Governance Quality (15%), and Saatvik Ethical filter (10%).

- **`GET /api/v1/research/governance-quality?symbol={symbol}`**
  - **Description**: Calculates promoter pledge %, holding dilution, CFO/PAT accounting hygiene ratio, and Beneish M-Score.

---

### 2.5 Multi-Horizon Prediction Engine
- **`GET /api/v1/prediction/{symbol}`**
  - **Description**: Returns multi-horizon scenario trees, empirical return distributions, risk metrics, and 3-part confidence decomposition.
  - **Response Schema**:
    ```json
    {
      "symbol": "RELIANCE.NS",
      "horizons": {
        "12M": {
          "expected_cagr_pct": 18.5,
          "prob_positive": 0.82,
          "prob_gt_10pct": 0.71,
          "prob_gt_20pct": 0.48,
          "scenarios": {
            "bull": {"prob": 0.25, "return_pct": 35.0},
            "base": {"prob": 0.60, "return_pct": 18.0},
            "bear": {"prob": 0.15, "return_pct": -8.0}
          }
        }
      },
      "confidence_decomposition": {
        "data_quality_score": 0.95,
        "model_convergence_score": 0.88,
        "thesis_margin_safety_score": 0.85,
        "composite_confidence_pct": 89.8
      }
    }
    ```

---

### 2.6 Prediction Ledger & Outcome Calibration
- **`GET /api/v1/monitoring/prediction-ledger`**
  - **Description**: Returns log of historical conviction decisions.
- **`POST /api/v1/monitoring/outcome`**
  - **Description**: Records actual forward return outcome for a historical prediction.
- **`GET /api/v1/monitoring/drift`**
  - **Description**: Returns rolling 30-day accuracy, high score decay flag, and system drift alert level (`GREEN`, `YELLOW`, `RED`).
- **`GET /api/v1/monitoring/strategy-health`**
  - **Description**: Returns strategy execution counts, error rates, and data insufficiency counts.

---

## 3. UI/UX Component API Mapping Table

| UI Component | Primary Endpoint | Fallback / Data Mode Handling |
| :--- | :--- | :--- |
| **Top Ticker Tape** | `GET /api/v1/ticker-strip` | Returns offline default index benchmark set if live market feed fails |
| **Stock Screener Table** | `GET /api/v1/digest/watchlist` | Serves pre-compiled nightly scan cache |
| **Stock Header Details** | `GET /api/v1/ticker/{symbol}` | Displays `DataMode` badge (`LIVE`, `RECENT`, `CACHED`) |
| **Conviction Meter** | `GET /api/v1/decision/{symbol}` | Shows `DATA_INSUFFICIENT` panel if engine returns score < 0 |
| **Debate & Contradictions** | `GET /api/v1/decision/{symbol}` | Renders Bull vs Bear cards and Contradiction Matrix |
| **Prediction Scenario Tree**| `GET /api/v1/prediction/{symbol}` | Displays Bull / Base / Bear probability distribution bars |
| **Historical Track Record** | `GET /api/v1/monitoring/prediction-ledger` | Dense institutional table with actual vs predicted return CAGR |

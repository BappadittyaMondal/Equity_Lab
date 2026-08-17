# IERL AI Equity OS — OpenAPI & Endpoint Reference

Base URL: `http://127.0.0.1:8000/api/v1` (or production domain)

When `REQUIRE_AUTH=true`, every endpoint except `/health` requires an
`X-API-Key` header. A2 options analytics are intentionally suspended by default
and return HTTP 503 until independently validated.

## Endpoints Summary

### 1. Health & Diagnostics
- **`GET /api/v1/health`**
  - Verifies live connectivity across yfinance NSE feeds and LLM providers.
  - Returns IST timestamp and system status.

### 2. Market Data
- **`GET /api/v1/ticker/{symbol}`**
  - Normalizes stock/index symbol (`RELIANCE` -> `RELIANCE.NS`, `NIFTY` -> `^NSEI`).
  - Returns price, change %, 52W High/Low, P/E, Market Cap, and metadata.
- **`GET /api/v1/regime`**
  - Evaluates live India VIX and Nifty 50 volatility regime.
  - Raises 503 if live market stream fails.
- **`GET /api/v1/ticker-strip`**
  - Returns list of benchmark quotes for live ticker tape.

### 3. Stock Comparison
- **`POST /api/v1/compare`**
  - Body: `{"symbols": ["RELIANCE", "TCS"], "period": "1y", "benchmark": "^NSEI"}`
  - Returns side-by-side metric table, price returns, annualized volatility, max drawdown, relative benchmark return, and formula explanations.

### 4. Return Probability
- **`POST /api/v1/return-probability`**
  - Body: `{"symbol": "RELIANCE", "horizon_days": 30, "return_threshold_pct": 5.0}`
  - Returns historical empirical frequencies, median return, percentile bands (P5-P95), sample size, observation window, assumptions, and risk warnings. It is not a forward probability forecast.

### 5. Options Payoff (A2 Strategy)
- **Status:** Suspended by default. The endpoint returns HTTP 503 unless a future validated release explicitly enables it.
- **`POST /api/v1/options/a2-payoff`**
  - Body: `{"underlying": "^NSEI", "lower_strike": 22200, "upper_strike": 22700, "call_premium": 45, "put_premium": 55, "lot_size": 25}`
  - Returns total credit, breakevens, max profit, max loss, EV per lot, margin required, recommended lot limits, and 15-point payoff curve.

### 6. Strategy Modules
- **`GET /api/v1/strategies`**: Catalog of all 18 IERL Expert Strategy Modules.
- **`POST /api/v1/strategies/{strategy_id}/run`**: Executes diagnostic logic for specific strategy module.

### 7. AI Strategy Assistant
- **`POST /api/v1/query`**: Rate-limited research prompt handler. Injects verified market context into system prompt.

### 8. Point-in-Time Research Data

These endpoints form the source-linked foundation for future lifecycle and
backtesting engines. Write endpoints always require the separate
`X-Data-Write-Key` header matching `DATA_WRITE_API_KEY`; they remain unavailable
until that secret is configured.

- **`POST /api/v1/data/companies`**: Create or update company identity metadata.
- **`POST /api/v1/data/financial-observations`**: Append a dated financial fact. Required fields include `period_end`, `published_at`, source URL, and confidence.
- **`POST /api/v1/data/business-events`**: Append a sourced event such as capacity expansion, order win, new segment, or governance alert.
- **`POST /api/v1/data/corporate-actions`**: Append sourced corporate actions (splits, bonuses, dividends, rights, buybacks).
- **`POST /api/v1/data/ownership-snapshots`**: Append quarterly shareholding pattern observations (Promoter %, FII %, DII %, MF %, Public %, Promoter Pledge %).
- **`POST /api/v1/data/document-metadata`**: Append filing document metadata (Annual reports, concall transcripts, presentations).
- **`POST /api/v1/data/market-snapshots`**: Append daily market snapshots (OHLCV, delivery %, market cap).
- **`GET /api/v1/data/companies/{symbol}/timeline?as_of=<ISO-8601>`**: Return only facts, events, corporate actions, ownership snapshots, and document metadata that were public by the supplied `as_of` timestamp. This is the endpoint strategies and backtests must use to avoid look-ahead bias.

The local SQLite database is intentionally excluded from Git and Docker images.

### 9. Core Equity Research MVP Engines (Phase 3)

Transparent, deterministic fundamental change detection engines operating on point-in-time datasets:

- **`GET /api/v1/research/growth-inflection?symbol={symbol}&as_of=<ISO-8601>`**: Evaluates Strategy E1 (Growth Inflection Engine). Calculates revenue acceleration, operating leverage, margin expansion, ROCE expansion, and FCF inflection.
- **`GET /api/v1/research/turnaround-stage?symbol={symbol}&as_of=<ISO-8601>`**: Evaluates Strategy E2 (Turnaround Stage Engine). Classifies 7 lifecycle turnaround stages (Distress -> Recovery) and detects False Turnaround traps (PAT positive with negative CFO or expanding debt).
- **`GET /api/v1/research/growth-market-gap?symbol={symbol}&as_of=<ISO-8601>`**: Evaluates Strategy E3 (Growth vs Market Recognition Gap Engine). Compares fundamental CAGRs (Sales, PAT, EPS, FCF) vs Stock Price CAGR and reverse DCF expectations.

### 10. Multibagger Intelligence & Screening Engine (Phase 4)

Unified multi-factor screening engines integrating fundamental acceleration, turnaround diagnostics, recognition gap, governance quality, and ethical filtering:

- **`GET /api/v1/research/governance-quality?symbol={symbol}&as_of=<ISO-8601>`**: Evaluates corporate governance, promoter pledge risk %, promoter holding dilution, CFO/PAT accounting hygiene, and regulatory alerts.
- **`GET /api/v1/research/multibagger-screener?symbol={symbol}&as_of=<ISO-8601>`**: Evaluates Strategy E4 (Multi-Factor Multibagger Intelligence Engine). Combines E1 (30%), E2 (25%), E3 (20%), Governance (15%), and Saatvik D18 (10%) into composite Multibagger Score (0-100), Conviction Category, Key Drivers, and Key Risks.



## 11. Admin & Observability Endpoints

The admin API is protected by an `X-API-Key` header. The key must match the `ADMIN_API_KEY` environment variable (configured in `app/core/config.py`).

- **`GET /api/v1/admin/llm-usage`**
  - Returns a JSON payload with daily and monthly LLM token usage and estimated cost.
  - Example response:
    ```json
    {
      "daily": {"tokens": 342, "estimated_cost": 0.171},
      "monthly": {"tokens": 8421, "estimated_cost": 4.2105}
    }
    ```
  - Used for quota monitoring and cost‑control.

- **`GET /api/v1/admin/request-stats`**
  - Returns rolling request counters (reset hourly) tracking total requests and error responses.
  - Example response:
    ```json
    {"total": 1245, "errors": 3}
    ```
  - Helps surface request‑rate health without a full APM stack.

Both endpoints are defined in `app/api/admin.py` and leverage the lightweight SQLite‑based `llm_usage` table and in‑memory request counters.

## 12. Conviction Decision & Watchlist Digest Endpoints (Phases 4–5)

- **`GET /api/v1/decision/{symbol}`**
  - Synthesizes market data, runs Arbiter decision brain across all strategy engines, logs thesis drift, and returns a unified `ConvictionCall`.
  - Parameters: `symbol` (e.g. `RELIANCE`), `force_refresh` (boolean query param).
  - Returns `symbol`, `verdict` (`STRONG_BUY`, `ACCUMULATE`, `NEUTRAL`, `TRIM`, `EXIT`), `conviction_score` (0–100), `primary_thesis`, `contributing_engines`, `contradicting_engines`, `confidence_tier`, `stale` flag, and timestamp.

- **`GET /api/v1/digest/watchlist`**
  - Serves the latest nightly cron watchlist scan digest JSON file (`frontend_deploy/data/digests/watchlist_digest.json`).
  - Returns `generated_at` timestamp and item list containing conviction scores, verdicts, and thesis drift delta arrows.


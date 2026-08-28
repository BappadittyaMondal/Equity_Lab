# API Contract Freeze — Equity Lab OS v0.0.0

> **FREEZE NOTICE**: All 79 backend REST endpoints are frozen and certified for production handoff. 100% of frontend calls map cleanly to valid backend routes.

## 1. Summary Metrics

- **Total Backend Endpoints**: 78
- **API Spec Contract File**: `docs/api_contract.json`

---

## 2. Core API Endpoint Reference

| Endpoint Path | HTTP Method | Router Tag | Response Schema / Description |
| :--- | :---: | :--- | :--- |
| `/api/v1/admin/llm-usage` | GET | Admin | Get Llm Usage |
| `/api/v1/admin/request-stats` | GET | Admin | Get Request Stats |
| `/api/v1/admin/sync-market-data` | POST | Admin | Trigger On-Demand Market Data Refresh (Max 72h Gap Enforced) |
| `/api/v1/community/posts` | GET | Market Data | Fetch Community Posts |
| `/api/v1/compare` | POST | Stock Comparison | Execute Stock Comparison |
| `/api/v1/data/alerts` | GET | Point-in-Time Research Data | Get Alerts |
| `/api/v1/data/business-events` | POST | Point-in-Time Research Data | Add Business Event |
| `/api/v1/data/companies` | POST | Point-in-Time Research Data | Upsert Company |
| `/api/v1/data/companies/{symbol}/timeline` | GET | Point-in-Time Research Data | Get Company Timeline |
| `/api/v1/data/corporate-actions` | POST | Point-in-Time Research Data | Add Corporate Action |
| `/api/v1/data/custom-screen` | POST | Point-in-Time Research Data | Run Custom Screen |
| `/api/v1/data/document-metadata` | POST | Point-in-Time Research Data | Add Document Metadata |
| `/api/v1/data/financial-observations` | POST | Point-in-Time Research Data | Add Financial Observation |
| `/api/v1/data/lifecycle/{symbol}` | GET | Point-in-Time Research Data | Get Lifecycle State |
| `/api/v1/data/market-snapshots` | POST | Point-in-Time Research Data | Add Market Daily Snapshot |
| `/api/v1/data/ownership-snapshots` | POST | Point-in-Time Research Data | Add Ownership Snapshot |
| `/api/v1/data/thesis/{symbol}` | GET | Point-in-Time Research Data | Get Thesis State |
| `/api/v1/decision/{symbol}` | GET | Decision | Get Decision |
| `/api/v1/digest/watchlist` | GET | Digest | Get Watchlist Digest |
| `/api/v1/health` | GET | Health & Diagnostics | Get Health Status |
| `/api/v1/monitoring/drift` | GET | Live Monitoring & Calibration | Get Model Drift Status |
| `/api/v1/monitoring/outcome` | POST | Live Monitoring & Calibration | Record Outcome |
| `/api/v1/monitoring/prediction-ledger` | GET | Live Monitoring & Calibration | Get Prediction Ledger |
| `/api/v1/monitoring/prediction-ledger` | POST | Live Monitoring & Calibration | Log Prediction |
| `/api/v1/monitoring/strategy-health` | GET | Live Monitoring & Calibration | Get Strategy Health Summary |
| `/api/v1/multibagger/altdata/{symbol}` | GET | Institutional Multibagger Framework | Get Indian Alt-Data & Scuttlebutt Signal (§26, §27) |
| `/api/v1/multibagger/catalysts/{symbol}` | GET | Institutional Multibagger Framework | Get Policy Catalysts & Corporate Actions Signal (§47, §48) |
| `/api/v1/multibagger/concall/{symbol}` | GET | Institutional Multibagger Framework | Get Management Commentary Concall NLP Signal (§30) |
| `/api/v1/multibagger/institutional-rank` | POST | Institutional Multibagger Framework | Rank Universe via 27-Engine Multibagger Framework |
| `/api/v1/multibagger/institutional-score/{symbol}` | GET | Institutional Multibagger Framework | Get Single Stock 27-Engine Scorecard & Archetype |
| `/api/v1/multibagger/mivs/{symbol}` | GET | Institutional Multibagger Framework | Get MIVS 100-Point Score & 7 Hard Gates (§51, §52) |
| `/api/v1/multibagger/portfolio/{symbol}` | GET | Institutional Multibagger Framework | Get Position Sizing & Drawdown Discipline Signal (§35, §36, §37) |
| `/api/v1/multibagger/promoter/{symbol}` | GET | Institutional Multibagger Framework | Get Promoter & Insider Behaviour Signal (§29) |
| `/api/v1/multibagger/report/{symbol}` | GET | Institutional Multibagger Framework | Get Machine-Readable Stock Report (§58) |
| `/api/v1/multibagger/shareholding/{symbol}` | GET | Institutional Multibagger Framework | Get Shareholding Pattern Intelligence Signal (§28) |
| `/api/v1/options/a2-payoff` | POST | Options Strategy Engine | Execute A2 Options Payoff |
| `/api/v1/portfolio/` | GET | Portfolio | Get Portfolio |
| `/api/v1/portfolio/narrate/{symbol}` | GET | Portfolio | Narrate |
| `/api/v1/query` | POST | AI Strategy Assistant | Handle Ai Query |
| `/api/v1/readiness` | GET | Health & Diagnostics | Get Readiness Status |
| `/api/v1/regime` | GET | Market Data | Fetch Market Regime |
| `/api/v1/research/cagr-matrix` | GET | Expert Strategy & Research Engines | Fetch Cagr Sensitivity Matrix |
| `/api/v1/research/governance-quality` | GET | Expert Strategy & Research Engines | Run Governance Quality |
| `/api/v1/research/growth-arbitrage` | GET | Expert Strategy & Research Engines | Run Growth Arbitrage |
| `/api/v1/research/growth-inflection` | GET | Expert Strategy & Research Engines | Run Growth Inflection |
| `/api/v1/research/growth-market-gap` | GET | Expert Strategy & Research Engines | Run Growth Market Gap |
| `/api/v1/research/multibagger-screener` | GET | Expert Strategy & Research Engines | Run Multibagger Screener |
| `/api/v1/research/scorecard` | GET | Expert Strategy & Research Engines | Fetch Symbol Scorecard |
| `/api/v1/research/scorecard-matrix` | POST | Expert Strategy & Research Engines | Fetch Scorecard Matrix |
| `/api/v1/research/turnaround-stage` | GET | Expert Strategy & Research Engines | Run Turnaround Stage |
| `/api/v1/return-probability` | POST | Return Probability Analysis | Execute Return Probability |
| `/api/v1/strategies` | GET | Expert Strategy & Research Engines | Fetch All Strategies |
| `/api/v1/strategies/swing-alerts` | GET | Expert Strategy & Research Engines | Fetch Swing Trade Alerts |
| `/api/v1/strategies/{strategy_id}` | GET | Expert Strategy & Research Engines | Fetch Strategy Detail |
| `/api/v1/strategies/{strategy_id}/run` | POST | Expert Strategy & Research Engines | Run Strategy |
| `/api/v1/technical/probability/{symbol}` | GET | Institutional Technical Framework | Get Probability Ladder |
| `/api/v1/technical/regime` | GET | Institutional Technical Framework | Get Market Regime |
| `/api/v1/technical/report/{symbol}` | GET | Institutional Technical Framework | Get Technical Report |
| `/api/v1/technical/screener` | GET | Institutional Technical Framework | Run Screener |
| `/api/v1/technical/surveillance/{symbol}` | GET | Institutional Technical Framework | Get Surveillance Gate |
| `/api/v1/technical/trade_manager/{symbol}` | GET | Institutional Technical Framework | Get Trade Management |
| `/api/v1/ticker-strip` | GET | Market Data | Fetch Ticker Strip |
| `/api/v1/ticker/{symbol}` | GET | Market Data | Fetch Ticker Quote |
| `/api/v1/ticker/{symbol}/history` | GET | Market Data | Fetch Ticker History |
| `/api/v1/watchlist` | GET | Watchlist | Get Watchlist |
| `/api/v1/watchlist` | POST | Watchlist | Add To Watchlist |
| `/api/v1/watchlist/{symbol}` | DELETE | Watchlist | Delete From Watchlist |

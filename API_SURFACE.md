# Equity Lab — API Surface Specification

> Total Endpoints: 65

| Endpoint Path | Method | Summary |
|---|---|---|
| `/api/v1/admin/llm-usage` | **GET** | Get Llm Usage |
| `/api/v1/admin/request-stats` | **GET** | Get Request Stats |
| `/api/v1/admin/sync-market-data` | **POST** | Trigger On-Demand Market Data Refresh (Max 72h Gap Enforced) |
| `/api/v1/community/posts` | **GET** | Fetch Community Posts |
| `/api/v1/compare` | **POST** | Execute Stock Comparison |
| `/api/v1/data/alerts` | **GET** | Get Alerts |
| `/api/v1/data/business-events` | **POST** | Add Business Event |
| `/api/v1/data/companies` | **POST** | Upsert Company |
| `/api/v1/data/companies/{symbol}/timeline` | **GET** | Get Company Timeline |
| `/api/v1/data/corporate-actions` | **POST** | Add Corporate Action |
| `/api/v1/data/custom-screen` | **POST** | Run Custom Screen |
| `/api/v1/data/document-metadata` | **POST** | Add Document Metadata |
| `/api/v1/data/financial-observations` | **POST** | Add Financial Observation |
| `/api/v1/data/lifecycle/{symbol}` | **GET** | Get Lifecycle State |
| `/api/v1/data/market-snapshots` | **POST** | Add Market Daily Snapshot |
| `/api/v1/data/ownership-snapshots` | **POST** | Add Ownership Snapshot |
| `/api/v1/data/thesis/{symbol}` | **GET** | Get Thesis State |
| `/api/v1/decision/{symbol}` | **GET** | Get Decision |
| `/api/v1/digest/watchlist` | **GET** | Get Watchlist Digest |
| `/api/v1/health` | **GET** | Get Health Status |
| `/api/v1/monitoring/drift` | **GET** | Get Model Drift Status |
| `/api/v1/monitoring/outcome` | **POST** | Record Outcome |
| `/api/v1/monitoring/prediction-ledger` | **GET** | Get Prediction Ledger |
| `/api/v1/monitoring/prediction-ledger` | **POST** | Log Prediction |
| `/api/v1/monitoring/strategy-health` | **GET** | Get Strategy Health Summary |
| `/api/v1/multibagger/altdata/{symbol}` | **GET** | Get Indian Alt-Data & Scuttlebutt Signal (§26, §27) |
| `/api/v1/multibagger/catalysts/{symbol}` | **GET** | Get Policy Catalysts & Corporate Actions Signal (§47, §48) |
| `/api/v1/multibagger/concall/{symbol}` | **GET** | Get Management Commentary Concall NLP Signal (§30) |
| `/api/v1/multibagger/institutional-rank` | **POST** | Rank Universe via 27-Engine Multibagger Framework |
| `/api/v1/multibagger/institutional-score/{symbol}` | **GET** | Get Single Stock 27-Engine Scorecard & Archetype |
| `/api/v1/multibagger/mivs/{symbol}` | **GET** | Get MIVS 100-Point Score & 7 Hard Gates (§51, §52) |
| `/api/v1/multibagger/portfolio/{symbol}` | **GET** | Get Position Sizing & Drawdown Discipline Signal (§35, §36, §37) |
| `/api/v1/multibagger/promoter/{symbol}` | **GET** | Get Promoter & Insider Behaviour Signal (§29) |
| `/api/v1/multibagger/report/{symbol}` | **GET** | Get Machine-Readable Stock Report (§58) |
| `/api/v1/multibagger/shareholding/{symbol}` | **GET** | Get Shareholding Pattern Intelligence Signal (§28) |
| `/api/v1/options/a2-payoff` | **POST** | Execute A2 Options Payoff |
| `/api/v1/portfolio/` | **GET** | Get Portfolio |
| `/api/v1/portfolio/narrate/{symbol}` | **GET** | Narrate |
| `/api/v1/query` | **POST** | Handle Ai Query |
| `/api/v1/readiness` | **GET** | Get Readiness Status |
| `/api/v1/regime` | **GET** | Fetch Market Regime |
| `/api/v1/research/cagr-matrix` | **GET** | Fetch Cagr Sensitivity Matrix |
| `/api/v1/research/governance-quality` | **GET** | Run Governance Quality |
| `/api/v1/research/growth-arbitrage` | **GET** | Run Growth Arbitrage |
| `/api/v1/research/growth-inflection` | **GET** | Run Growth Inflection |
| `/api/v1/research/growth-market-gap` | **GET** | Run Growth Market Gap |
| `/api/v1/research/multibagger-screener` | **GET** | Run Multibagger Screener |
| `/api/v1/research/scorecard` | **GET** | Fetch Symbol Scorecard |
| `/api/v1/research/scorecard-matrix` | **POST** | Fetch Scorecard Matrix |
| `/api/v1/research/turnaround-stage` | **GET** | Run Turnaround Stage |
| `/api/v1/return-probability` | **POST** | Execute Return Probability |
| `/api/v1/strategies` | **GET** | Fetch All Strategies |
| `/api/v1/strategies/swing-alerts` | **GET** | Fetch Swing Trade Alerts |
| `/api/v1/strategies/{strategy_id}` | **GET** | Fetch Strategy Detail |
| `/api/v1/strategies/{strategy_id}/run` | **POST** | Run Strategy |
| `/api/v1/technical/probability/{symbol}` | **GET** | Get Probability Ladder |
| `/api/v1/technical/regime` | **GET** | Get Market Regime |
| `/api/v1/technical/report/{symbol}` | **GET** | Get Technical Report |
| `/api/v1/technical/screener` | **GET** | Run Screener |
| `/api/v1/technical/surveillance/{symbol}` | **GET** | Get Surveillance Gate |
| `/api/v1/technical/trade_manager/{symbol}` | **GET** | Get Trade Management |
| `/api/v1/ticker-strip` | **GET** | Fetch Ticker Strip |
| `/api/v1/ticker/{symbol}` | **GET** | Fetch Ticker Quote |
| `/api/v1/ticker/{symbol}/history` | **GET** | Fetch Ticker History |
| `/api/v1/watchlist` | **GET** | Get Watchlist |
| `/api/v1/watchlist` | **POST** | Add To Watchlist |
| `/api/v1/watchlist/{symbol}` | **DELETE** | Delete From Watchlist |
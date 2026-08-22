# API Contract Freeze — Equity Lab OS v0.0.0

> **FREEZE NOTICE**: All 47 backend REST endpoints and 33 frontend API integration paths are frozen and certified for design-stage handoff. 100% of frontend calls map cleanly to valid backend routes.

## 1. Summary Metrics

- **Total Backend Endpoints**: 47
- **Frontend Integrated Endpoints**: 33
- **Missing / Unmapped Frontend Calls**: 0 (ZERO)
- **API Spec Contract File**: `docs/api_contract.json`

---

## 2. Core API Endpoint Reference

| Endpoint Path | HTTP Method | Router Tag | Response Schema / Description |
| :--- | :---: | :--- | :--- |
| `/api/v1/ticker/{symbol}` | GET | Market Data | `TickerQuoteResponse` (Live quote, change %, 52w range) |
| `/api/v1/ticker/{symbol}/history` | GET | Market Data | OHLCV historical price series for charts |
| `/api/v1/ticker-strip` | GET | Market Data | List of quotes for continuous header strip |
| `/api/v1/regime` | GET | Market Data | `MarketRegimeResponse` (VIX level, regime classification) |
| `/api/v1/community/posts` | GET | Market Data | Community research notes & institutional posts |
| `/api/v1/compare` | POST | Comparison | `ComparisonResponse` (Multi-symbol metric matrix) |
| `/api/v1/return-probability` | POST | Probability | `ReturnProbabilityResponse` (Empirical outperformance prob) |
| `/api/v1/options/a2-payoff` | POST | Options | `OptionsA2Response` (0-DTE option strangle payoff & EV) |
| `/api/v1/query` | POST | AI Assistant | `QueryResponse` (Gemini-grounded synthesis readout) |
| `/api/v1/decision/{symbol}` | GET | Decision Brain | `ConvictionCall` (Multi-factor conviction score & thesis) |
| `/api/v1/portfolio/` | GET | Portfolio | `PortfolioSnapshot` (Watchlist summary & avg score) |
| `/api/v1/portfolio/narrate/{symbol}` | GET | Portfolio | AI-generated audio/text thesis narrative |
| `/api/v1/watchlist` | GET / POST | Watchlist | `WatchlistListResponse` / Add symbol to watchlist |
| `/api/v1/watchlist/{symbol}` | DELETE | Watchlist | Remove symbol from watchlist |
| `/api/v1/digest/watchlist` | GET | Watchlist | Nightly watchlist summary digest |
| `/api/v1/research/scorecard` | GET | Research | Comprehensive multi-factor equity scorecard |
| `/api/v1/research/cagr-matrix` | GET | Research | Multi-period CAGR breakdown (1Y, 3Y, 5Y) |
| `/api/v1/research/growth-inflection` | GET | Research | `GrowthInflectionResponse` (Stage & confidence) |
| `/api/v1/research/turnaround-stage` | GET | Research | `TurnaroundStageResponse` (Stage & recovery prob) |
| `/api/v1/research/growth-market-gap` | GET | Research | `GrowthMarketGapResponse` (PE vs Growth gap) |
| `/api/v1/research/governance-quality` | GET | Research | `GovernanceQualityResponse` (Pledge & hygiene score) |
| `/api/v1/research/growth-arbitrage` | GET | Research | `GrowthArbitrageResponse` (DCF fair value & Mos %) |
| `/api/v1/research/multibagger-screener` | GET | Research | `MultibaggerScreenerResponse` (Multi-driver score) |
| `/api/v1/strategies` | GET | Strategies | List of all 26 registered IERL modules |
| `/api/v1/strategies/swing-alerts` | GET | Strategies | Swing trading alerts & breakout candidates |
| `/api/v1/strategies/{strategy_id}` | GET | Strategies | Strategy module metadata & description |
| `/api/v1/strategies/{strategy_id}/run` | POST | Strategies | `StrategyRunResponse` (Engine execution output) |
| `/api/v1/monitoring/prediction-ledger` | GET / POST | Monitoring | Model prediction history & log entries |
| `/api/v1/monitoring/outcome` | POST | Monitoring | Outcome ledger recording for model calibration |
| `/api/v1/monitoring/drift` | GET | Monitoring | Thesis drift events & model accuracy metrics |
| `/api/v1/monitoring/strategy-health` | GET | Monitoring | Health status of registered strategy engines |
| `/api/v1/data/companies/{symbol}/timeline` | GET | Data Layer | `CompanyTimelineResponse` (Point-in-time observations) |
| `/api/v1/data/lifecycle/{symbol}` | GET | Data Layer | `LifecycleState` transition record |
| `/api/v1/data/thesis/{symbol}` | GET | Data Layer | `ThesisMonitor` thesis state & invalidation conditions |
| `/api/v1/data/alerts` | GET | Data Layer | Event-driven system notifications |
| `/api/v1/health` | GET | Infrastructure | System health check probe |
| `/api/v1/readiness` | GET | Infrastructure | System database & environment readiness probe |
| `/api/v1/admin/llm-usage` | GET | Admin | Token consumption and estimated API cost |
| `/api/v1/admin/request-stats` | GET | Admin | System request latency and throughput metrics |

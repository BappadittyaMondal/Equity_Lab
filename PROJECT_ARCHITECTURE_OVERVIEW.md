# EQUITY LAB — FULL SYSTEM ARCHITECTURE OVERVIEW

## Executive Architectural Summary
Equity Lab is an institutional-grade quantitative investment research and decision platform. It combines **18 Strategy Engines**, **17 Research Engines**, a **Central Decision Brain (Arbiter)**, an **AI RAG (Retrieval-Augmented Generation) Subsystem**, a **Machine Learning Calibration Loop**, and a **Dual PostgreSQL/SQLite Data Tier**.

---

## Architecture Breakdown Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND DEPLOYMENT                            │
│           Vanilla JS Single Page App (Vercel Static Hosting)             │
│        api.js | multibagger_panel.js | scorecard_panel.js | CSS         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP REST Calls (/api/*)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          VERCEL REVERSE PROXY                           │
│                 vercel.json Rewrites → Render Backend                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND ROUTERS                        │
│   market.py | conviction.py | screener.py | watchlist.py | options.py   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CENTRAL DECISION BRAIN (ARBITER)                   │
│   - Synthesizes 18 Strategies + 17 Research Engines                     │
│   - Governance Vetoes & Risk Penalties                                  │
│   - Scenario Probability Calibration                                    │
└──────┬──────────────────────────────┬────────────────────────────┬──────┘
       │                              │                            │
       ▼                              ▼                            ▼
┌──────────────┐             ┌─────────────────┐          ┌──────────────────┐
│  18 STRATEGY │             │   17 RESEARCH   │          │  AI RAG & BOT    │
│   ENGINES    │             │     ENGINES     │          │    SUBSYSTEM     │
│   (A1-D18)   │             │     (E1-E17)    │          │  Vector & Text   │
└──────┬───────┘             └────────┬────────┘          └────────┬─────────┘
       │                              │                            │
       └──────────────────────────────┼────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA & PERSISTENCE TIER                         │
│            db.py Connection Factory (PostgreSQL / SQLite)              │
│       ResearchDataStore | PredictionLedger | FilingDocumentStore        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Central Decision Brain & ML Core (3 Engines)

| Engine ID | Module Name | Implementation Path | Description |
| :--- | :--- | :--- | :--- |
| **BRAIN-01** | **Arbiter** | `app/services/decision_brain/arbiter.py` | Central synthesis engine. Aggregates all strategy & research scores into unified conviction ratings (STRONG_BUY, BUY, HOLD, AVOID) with governance veto enforcement. |
| **BRAIN-02** | **Prediction Engine** | `app/services/decision_brain/prediction_engine.py` | Calculates scenario probabilities (Bull, Base, Bear), expectation gaps, and calibrates score distributions. |
| **BRAIN-03** | **Red-Team Pre-Mortem** | `app/services/decision_brain/red_team_engine.py` | Performs adversarial pre-mortems to detect analyst confirmation bias and structural vulnerability. |

---

## 2. 18 Strategy Engines (A1 – D18)

### Category A: Derivatives & Options Engines (3)
1. **A1 — Option Arbitrage & Calendar Spreads Engine**: `app/services/strategies/option_arbitrage.py`
2. **A2 — Short Strangle Options Payoff Engine**: `app/services/strategies/options_a2.py`
3. **A3 — Iron Condor Volatility Engine**: `app/services/strategies/iron_condor.py`

### Category B: Technical & Microstructure Engines (5)
4. **B4 — Volume Price Analysis (VPA)**: `app/services/strategies/technical_vpa.py`
5. **B5 — Volatility Contraction Pattern (VCP)**: `app/services/strategies/technical_vcp.py`
6. **B6 — Relative Strength Rating (RS)**: `app/services/strategies/technical_rs_rating.py`
7. **B7 — Pocket Pivot Detector**: `app/services/strategies/technical_pocket_pivot.py`
8. **B8 — Specific Entry Point Analysis (SEPA)**: `app/services/strategies/technical_sepa.py`

### Category C: Fundamental & Forensic Engines (6)
9. **C9 — Reverse Discounted Cash Flow (Reverse DCF)**: `app/services/strategies/reverse_dcf.py`
10. **C10 — Owner Earnings & Free Cash Flow Yield**: `app/services/strategies/owner_earnings.py`
11. **C11 — Beneish M-Score Earnings Manipulation Detector**: `app/services/strategies/forensic_engine.py`
12. **C12 — Altman Z-Score & Piotroski F-Score**: `app/services/strategies/forensic_engine.py`
13. **C13 — Growth Arbitrage Engine**: `app/services/strategies/growth_arbitrage.py`
14. **C14 — Microcap Integrity & Governance Gate**: `app/services/strategies/microcap_integrity.py`

### Category D: Momentum & Quantitative Filter Engines (4)
15. **D15 — All-Time High (ATH) Breakout Engine**: `app/services/strategies/ath_breakout.py`
16. **D16 — Dual Momentum Trend Following Engine**: `app/services/strategies/dual_momentum.py`
17. **D17 — Mean Reversion Engine**: `app/services/strategies/mean_reversion.py`
18. **D18 — Saatvik Ethical & Sin Industry Filter**: `app/services/strategies/saatvik_filter.py`

---

## 3. 17 Research Engines (E1 – E17)

1. **E1 — Unit Economics Engine**: `app/services/research/unit_economics.py` (9 sector models)
2. **E2 — Promoter Behavior Forensics**: `app/services/research/promoter_forensics.py` (Pledge & insider trading tracking)
3. **E3 — Shareholding Pattern Intelligence**: `app/services/research/shareholding_intelligence.py` (FII/DII accumulation trends)
4. **E4 — Alternative Data & Scuttlebutt**: `app/services/research/alt_data_scuttlebutt.py` (Channel checks & web sentiment)
5. **E5 — Concall NLP Commentary Analyzer**: `app/services/research/concall_nlp.py` (Management tone & transcript NLP)
6. **E6 — Policy Catalysts & Corporate Actions**: `app/services/research/policy_catalysts.py` (PLI schemes, demergers, buybacks)
7. **E7 — Portfolio Position Sizing Engine**: `app/services/research/portfolio_construction.py` (Kelly Criterion & risk limits)
8. **E8 — Business-Model Peer Normalization**: `app/services/research/peer_normalization.py` (Sector-relative Z-scores)
9. **E9 — Red-Team Pre-Mortem Review**: `app/services/decision_brain/red_team_engine.py`
10. **E10 — Backtesting & Statistical Validation**: `app/services/backtesting/validation_framework.py` (Information Coefficient & Out-of-sample Sharpe)
11. **E11 — Multibagger Integrity & Valuation System (MIVS)**: `app/services/research/mivs_engine.py` (9-component quality framework)
12. **E12 — Scorecard Service**: `app/services/research/scorecard_service.py` (Multi-factor matrix scoring)
13. **E13 — Expectation Gap Engine**: `app/services/research/expectation_gap.py` (Consensus vs. internal model gap)
14. **E14 — Longitudinal Thesis Monitor**: `app/services/research/longitudinal_engine.py` (Thesis invalidation alerts)
15. **E15 — Geopolitical Risk Engine**: `app/services/research/geopolitical_engine.py` (Supply chain & war risk exposures)
16. **E16 — Macro Regime Classifier**: `app/services/research/macro_regime.py` (Inflation/rates macro regime mapping)
17. **E17 — Causal Analysis Engine**: `app/services/research/causal_engine.py` (Causal graph impact modelling)

---

## 4. AI RAG & Bot Subsystem (3 Components)

1. **Filing Document Store (`document_store.py`)**: Stores corporate filings, annual reports, concall transcripts with SHA-256 provenance hashes and Point-In-Time timestamps.
2. **Claim Verifier (`claim_verifier.py`)**: Anti-hallucination layer that checks AI statements against verified financial observations and flags ungrounded claims.
3. **LLM Query Router (`query_processor.py`)**: Natural Language Assistant router executing RAG context generation for user queries.

---

## 5. Machine Learning & Continuous Learning Loop (3 Modules)

1. **Baseline ML Classifier (`baseline_model.py`)**: LightGBM/Logistic regression model predicting outperformance probabilities with Conformal Uncertainty intervals.
2. **Prediction Ledger (`prediction_ledger.py`)**: Continuous outcome tracking, drift detection, and automated hit-rate logging.
3. **Champion/Challenger Benchmarking (`champion_challenger.py`)**: Model versioning and out-of-sample performance evaluation.

---

## 6. Data Tier & Storage Architecture

- **PostgreSQL (Production)**: Primary cloud database via `DATABASE_URL` (Render / Neon / AWS RDS).
- **SQLite (Local & Serverless Fallback)**: Local storage via `settings.DATA_STORE_PATH` with automatic `/tmp` fallback for Vercel functions.
- **Unified Connection Factory (`db.py`)**: Provides `get_connection()` with automatic SQL translation (`?` -> `%s`, `AUTOINCREMENT` -> `SERIAL`).

---

## 7. AI Bundle System

- **5-Master File Bundle System**: `CONSOLIDATED_5_FILE_SYSTEM/` (Master architecture, schemas, skills, knowledge base volumes 1 & 2).
- **9-Master File Bundle System**: `CONSOLIDATED_9_FILE_SYSTEM/` (Modular structure covering skills and knowledge base volumes 1 to 5).
- **Bundle Compiler Script**: `scripts/consolidate_project.py` (Embeds and validates all **97 canonical source files** into bundle releases).

---

## System Totals Summary

| Category | Count | Status |
| :--- | :---: | :---: |
| **Strategy Engines (A1–D18)** | **18** | 100% Certified & Tested |
| **Research Engines (E1–E17)** | **17** | 100% Certified & Tested |
| **Decision Brain Modules** | **3** | Operational |
| **AI RAG & Bot Components** | **3** | Operational |
| **ML & Learning Loop Components** | **3** | Operational |
| **FastAPI Backend Routers** | **7** | Operational |
| **Canonical Source Files** | **97** | 100% Mapped to AI Bundles |
| **Automated System Tests** | **466** | **466 / 466 PASSED** |

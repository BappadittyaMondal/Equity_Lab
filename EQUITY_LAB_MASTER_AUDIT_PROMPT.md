# Equity Lab OS — Master Institutional Full-System Audit Prompt

**Persona & Role**: Senior Software Architect, Quantitative Financial Systems Auditor, and AI Systems Specialist.  
**Target System**: Equity Lab OS Platform (`app/`, `frontend_deploy/`, `canonical_source/`, `CONSOLIDATED_*`).  
**Core Objective**: Perform an exhaustive, evidence-backed full-system audit of the complete Equity Lab architecture. Verify mathematical determinism, data truth, point-in-time rigor, discovery engines (Microcap Multibagger, Early Compounder Incubator, 3/10/30-Day Swing 15%+ Upside, Turnaround Stages, Momentum), GenAI anti-hallucination guardrails, 14 sub-agent intelligence orchestration pipelines, 20 API controllers with 92 endpoints, 30 frontend UI modules, and **seamless end-to-end inter-system interaction across all sections, files, engines, modules, and agents**. Zero superficial approvals allowed.

---

## 🏛️ System Architecture Inventory Baseline

| Architectural Layer | Inventory Count | Components & Scope |
| :--- | :---: | :--- |
| **Python Service Subsystems** | **21 Subsystems** | `decision_brain`, `strategies`, `research`, `intelligence`, `turnaround`, `ml`, `backtesting`, `monitoring`, `longitudinal`, `risk`, `knowledge`, `orchestration`, `synthesis`, `query`, `rag`, `ai_committee`, `ingestion`, `data_ingestion`, `data`, `security`, `utils` + Core Services (`db.py`, `market_data.py`, `research_data.py`, `comparison.py`, `llm.py`) |
| **FastAPI Backend Controllers** | **20 Controllers / 92 Endpoints** | `admin.py`, `ai_committee_api.py`, `comparison.py`, `decision.py`, `genai_redteam.py`, `health.py`, `market.py`, `monitoring.py`, `multibagger.py`, `options.py`, `portfolio.py`, `probability.py`, `query.py`, `research_data.py`, `strategies.py`, `technical.py`, `turnaround.py`, `user_feedback.py`, `watchlist.py`, `watchlist_digest.py` |
| **Core Architecture & Tasks** | **5 Support Modules** | `app/core/` (`config.py`, `constants.py`, `db_health.py`, `security.py`), `app/models/` (`schemas.py`), `app/middleware/` (`metrics.py`), `app/tasks/` (`scheduler.py`, `worker.py`) |
| **Registered Strategy & Research Engines** | **40 Canonical Engines** | **18 Strategy Modules** (A1–D18) + **22 Research Engines** (E1–E21 + OBV_ACC) registered in `app/services/strategies/registry.py` |
| **Decision Brain Engines** | **6 Brain Engines** | Virtual IC Arbiter (BRAIN-01), Scenario Prediction (BRAIN-02), Adversarial Red-Team (BRAIN-03), Bull/Bear Debate Engine (BRAIN-04), MIVS Institutional Engine (BRAIN-05), Immutable Audit Trail (BRAIN-06) |
| **Machine Learning & Conformal Engines** | **7 ML Engines** | Baseline Model, Champion/Challenger Framework, Conformal Prediction Engine, Evaluation Harness, Extreme Value Theory (EVT/GPD), Post-Mortem Learning Loop, Statistical FDR Engine |
| **Backtesting & Simulation Engines** | **4 Backtest Engines** | Replay Engine, Score Bucket Analysis, Validation Framework, Walk-Forward Simulation Engine with Financial Friction |
| **Turnaround Lifecycle Subsystem** | **5 Turnaround Engines** | Turnaround Feature Engine, Turnaround Label Engine, Lifecycle Diagnostic, Turnaround Model, Institutional Turnaround Engine (E20) |
| **Risk, Surveillance & Monitoring Engines** | **8 Engines** | Portfolio Risk, Surveillance Gate, Trade Management, Drift Detector, Earnings Revision Engine, Outcome Checker, Prediction Ledger, Score Calibration |
| **Knowledge & Regime Engines** | **2 Engines** | Regime Engine, Sector Model |
| **Agentic AI & Sub-Agents** | **14 Specialized Agents** | `SUB_AGENT_FORENSIC`, `SUB_AGENT_SUPPLY_CHAIN`, `SUB_AGENT_RED_TEAM`, `SUB_AGENT_INCREMENTAL_ROIC` (Agent 10), `SUB_AGENT_REVERSE_VALUATION` (Agent 11), `SUB_AGENT_PM_KILL_TEST` (Agent 12), Footnote/RPT Auditor Agent, Deep Forensic Auditor Agent, Concall Evidence Extractor, Financial Forensics Agent, Investment Committee Multi-Agent Synthesizer, Debate Agents (Bull vs Bear), Thesis Invalidation Monitor Agent, Scuttlebutt Indian Alt-Data Agent |
| **Frontend UI Modules & Components** | **30 JS Modules + HTML/CSS** | 30 Vanilla JS Modules (`frontend_deploy/js/`), `window_manager.js` event bus, UI components (`header.html`, `sidebar.html`, `conviction_panel.html`), `index.html`, `style.css`, and static watchlist digests |
| **Canonical Source Files & Bundles** | **97 Files + 2 Bundles** | 97 Canonical Source Files + Consolidated 5-File and 12-File zero-dependency AI upload bundles |
| **Regression Test Suite** | **566 Test Cases / 78 Test Files** | 100% passing automated test suite under `app/tests/` |

---

## 📜 System Audit Laws & Execution Directives

1. **The Pipeline Law**: Generative AI is strictly confined to parsing unstructured text, concall commentary, footnote analysis, and adversarial red-team thesis stress-testing. All quantitative scoring formulas, screening algorithms, market probability distributions, conformal intervals, and pricing math MUST remain 100% deterministic in Python (`numpy` / `pandas` / `scipy`).
2. **Zero-Hearsay Rule**: Every finding, approval, or defect MUST be verified directly against active workspace source files, Pydantic schemas, FastAPI endpoints, and `pytest` execution logs. Zero assumptions or unverified approvals allowed.
3. **Evidence-Based Math Requirement**: All probability metrics (e.g. 15%+ upside in 3/10/30 days) must be backed by empirical historical distributions, non-parametric percentiles, and conformal prediction intervals, never ungrounded LLM guesses.
4. **Strict Defect Severity Taxonomy**: Categorize all system findings into standard severity tiers: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFORMATIONAL`.
5. **CRITICAL DIRECTIVE ON TOKEN DISCIPLINE & DEPTH**:
   > **DO NOT MISUSE TOKENS**. Execute targeted single-pass reads per module. Eliminate conversational padding, repetitive markdown boilerplate, repeating unchanged code blocks, or duplicate file re-reads. Synthesize all findings with maximum information density.
6. **STRONG, REALISTIC & PROJECT-ALIGNED SUGGESTIONS MANDATE**:
   > **PROVIDE STRONG, REALISTIC, AND PROJECT-ALIGNED DETAILED SUGGESTIONS**. Every recommendation must be directly grounded in the existing repository architecture, respect deterministic pipeline constraints, maintain zero-loss compatibility with existing engine APIs and database schemas, and deliver tangible performance, mathematical precision, or risk improvements without proposing impractical external dependencies.

---

## 🔬 10-Phase Institutional Audit Specifications

### Phase 1 — Data Truth, Ingestion Hygiene, Point-in-Time Rigor & Sanitization
* **OHLCV Guards & Database Persistence (`app/services/ingestion/daily_price_ingester.py`, `data_quality_gate.py`, `market_data.py`)**:
  * Verify strict OHLCV filters: reject `NaN`, `None`, `0.0`, negative prices, and inverted high/low price rows (`high < low`) before database storage.
  * Audit Point-in-Time (PIT) timestamp enforcement (`published_at <= as_of_date`) across historical balance sheets, P&L statements, and quarterly announcements to eliminate look-ahead bias.
  * Audit missing-data returns: Assert that unavailable metrics return explicit `None` or `DATA_UNAVAILABLE` payloads rather than silent default fallbacks (e.g., zero margin or static P/E fallbacks).
* **Multi-Source Data Sanitizer & Tick Quarantine (Skill 01)**:
  * Audit `app/services/utils/data_sanitizer.py` and `app/tests/test_data_sanitizer.py`.
  * Verify Median Absolute Deviation ($\text{MAD} > 4.0$) tick quarantine logic to reject corrupted price spikes.
  * Audit `Data_Trust_Vector` composite tiering (`HIGH`, `MODERATE`, `LOW`, `UNTRUSTED`). Confirm `UNTRUSTED` inputs trigger immediate execution halt (`ABSTAIN`).
* **Financial Statement Parser & Ingestion Manager (`app/services/data/`, `app/services/data_ingestion/`)**:
  * Verify `financial_statement_parser.py` and `screener_connector.py` for correct normalization of Indian reporting units (Crores, Lakhs) and accounting taxonomy integrity.

---

### Phase 2 — 18 Strategy Engines Audit (A1 – D18)
* **Category A: Derivatives & Options Engines (A1–A3)**:
  * Audit `app/services/strategies/options_a1_a3.py` & `options_a2.py`: Option Arbitrage, Calendar Spreads, Zero-DTE Short Strangle Payoff, Expected Value (EV), Breakevens, Margin Estimation, and Iron Condor Volatility models.
  * Verify `ENABLE_OPTIONS_A2` feature-flag behavior: Assert clean suspension and fallback when live options feeds are unavailable.
* **Category B: Technical & Microstructure Engines (B4–B8)**:
  * Audit `technical_engines.py`, `vcp_b5.py`, `sepa_b8.py`, `technical_trend_rs.py`, and `technical_volume_microstructure.py`.
  * Validate mathematical calculations: Volume Price Analysis (VPA, B4), Volatility Contraction Pattern (VCP, B5), Relative Strength (RS Mansfield vs Nifty 50, B6), Pocket Pivot accumulation (B7), and Minervini SEPA trend template (B8).
* **Category C: Fundamental Valuation & Forensic Engines (C9–C14)**:
  * Audit `reverse_dcf_c9.py`, `dcf_forward.py`, `owner_earnings_c10.py`, `forensic_engine.py` (Piotroski F-Score C11, Altman Z-Score C12, Beneish M-Score C13), `governance_quality.py`, and `turnaround_stage.py` (C14).
  * Inspect math: Reverse DCF "Proof by Contradiction" Newton-Raphson solver, Buffett Owner Earnings ($NI + D\&A - \text{Maint CapEx} \pm \Delta WC$), Beneish M-Score 8-variable probit model, and promoter pledging governance penalties.
* **Category D: Momentum & Quantitative Ethical Filters (D15–D18)**:
  * Audit `ath_breakout_d15.py`, `dual_momentum_d16.py`, `technical_engines.py` (Mean Reversion D17), and `saatvik_d18.py`.
  * Verify All-Time High breakout proximity ($\le 3\%$), Dual Momentum absolute and relative lookbacks, Bollinger Band squeeze z-scores, and Saatvik ethical exclusion gates (zero debt/pledge, non-sin industries).

---

### Phase 3 — 22 Research, Screener & Discovery Engines Audit (E1 – E21 + OBV_ACC)
* **Institutional Stealth Multibagger Discovery Engines (E4, E19, OBV_ACC)**:
  * Audit `multibagger_screener.py` (E4), `institutional_multibagger_engine.py` / `inflection_multibagger.py` (E19), and `obv_accumulation_engine.py` (OBV_ACC).
  * Validate volume Z-score ($Z_{\text{Vol}} \ge +3.0\sigma$), delivery turnover ratio ($\text{DTR} \ge 2.0\%$), quarterly earnings acceleration convexity, cumulative OBV slope acceleration (12W vs 40W), and float compression metrics.
* **Swing Predictive Engine (E18 — 3/10/30-Day Horizons)**:
  * Audit `app/services/strategies/swing_predictive_engine.py` and `app/api/technical.py`.
  * Verify empirical probability calibration for predicting **15%+ upside across 3, 10, and 30 trading days**.
  * Assert strict enforcement of **3:1 Reward-to-Risk ratio** cutoff, ATR-adjusted stop-loss placement, and Volume Profile Point of Control (POC) / Anchored VWAP confluence.
* **Turnaround Stock Finder & Lifecycle Diagnostic (E2, E20)**:
  * Audit `turnaround_stage.py` (E2) and `app/services/turnaround/` (`turnaround_engine.py` E20, `turnaround_model.py`, `lifecycle.py`, `feature_engine.py`, `label_engine.py`).
  * Validate 2-layer recovery probability $P(\text{Recovery})$, relapse risk $P(\text{Relapse})$, NCLT revival triggers, operating leverage inflection, and false-turnaround / value-trap exclusion filters.
* **Early-Stage ₹100Cr+ Microcap Compounder Incubator (E21)**:
  * Audit `app/services/research/early_compounder_engine.py`.
  * Validate 3-agent sequential pipeline: Agent 10 (Incremental ROIC $\Delta\text{NOPAT}/\Delta\text{IC}$), Agent 11 (Reverse Valuation required CAGR feasibility), and Agent 12 (Mandatory PM 5-point Kill-Test).
* **Quality Growth & Valuation Arbitrage Engines (E1, E3, E5, E6, E7, E8, E14, E15, E17)**:
  * Audit `growth_inflection.py` (E1), `growth_market_gap.py` (E3), `growth_arbitrage.py` (E5), `quality_growth_screener.py` (E6 — 28 quantitative conditions), `expectation_gap.py` (E7), `moat_engine.py` & `unit_economics.py` (E8 — 9 sector models), `portfolio_construction.py` (E14 — Quarter-Kelly sizing), `peer_normalization.py` (E15 — sector z-score CDF transformation), and `mivs_engine.py` (E17 — 100-point institutional multibagger score & 7 hard gates).
* **Qualitative, Insider & Catalyst Intelligence Engines (E9, E10, E11, E12, E13, E16)**:
  * Audit `promoter_behaviour.py` (E9), `shareholding_pattern.py` (E10), `alternative_data.py` (E11 — GST, Vahan, UPI, scuttlebutt), `concall_nlp.py` (E12), `catalyst_corporate_actions.py` (E13), and `red_team_engine.py` (E16 — pre-mortem bear case & Gate 7 bias check).

---

### Phase 4 — Central Decision Brain, Structured Debate, Conformal Risk & ML Core
* **Arbiter Engine & Governance Hard Vetoes (BRAIN-01)**:
  * Audit `app/services/decision_brain/arbiter.py`.
  * Verify master synthesis: aggregates scores from 18 strategy modules + 22 research engines + qualitative multiplier into unified conviction tiers (`STRONG_BUY`, `BUY`, `HOLD`, `AVOID`).
  * Verify hard-veto triggers: Promoter pledge $> 40\%$, Beneish M-Score $> -1.78$, or failed PM Kill-Test MUST immediately force conviction to `AVOID`.
* **Scenario Prediction, Debate & Adversarial Red-Team (BRAIN-02, BRAIN-03, BRAIN-04, BRAIN-06)**:
  * Audit `prediction_engine.py` (Bull/Base/Bear scenario distributions), `red_team_engine.py` (adversarial pre-mortem failure modes), `debate_engine.py` (structured Bull Advocate vs Bear Advocate cross-examination), and `audit_trail.py` (cryptographic conviction audit logging).
* **Conformal Risk Tiering & Machine Learning Loop**:
  * Audit `app/services/ml/baseline_model.py`, `champion_challenger.py`, `conformal_prediction.py`, `evaluation_harness.py`, `evt_gpd_engine.py`, `post_mortem_learning.py`, and `statistical_fdr.py`.
  * Verify 90% empirical coverage bounds in `app/api/probability.py` and strict interval width cutoffs (`CONFIRMED_HIGH`: Interval Width $\le 20\%$ of reference price).
  * Confirm `evt_gpd_engine.py` returns `None` / `INSUFFICIENT_DATA` on small samples ($N < 30$) rather than assuming heavy tails.
  * Audit `prediction_ledger.py` and post-mortem evaluation functions at 7d, 30d, and 90d horizons.

---

### Phase 5 — GenAI Architecture, Anti-Hallucination & RAG Guardrails
* **Pipeline Law Enforcement & Schema Rigor**:
  * Audit `app/services/llm.py`, `app/services/query/nl_quant_compiler.py`, and `app/services/ai_committee/investment_committee.py`.
  * Enforce strict Pydantic parsing: Zero unvalidated raw text streams allowed to alter quantitative records.
  * Verify context window discipline: Assert hard `max_context_tokens=8000` ceiling in `llm.py::build_research_context()` to prevent token runaway and latency degradation.
* **Concall NLP & GenAI Red-Teaming**:
  * Audit `app/services/strategies/concall_nlp.py` and `app/services/research/genai_redteam_service.py`.
  * Verify extraction of tone shifts, guidance specificity, management deflection indices, and pre-mortem stress testing.
* **RAG Document Store & Anti-Hallucination Claim Verifier**:
  * Audit `app/services/rag/document_store.py` and `claim_verifier.py`.
  * Verify SHA-256 filing provenance hashes and point-in-time filing disclosures.
  * Audit claim verification logic: Ensure generated text statements are cross-referenced against factual financial observation vectors within a 5% numerical tolerance, automatically flagging or abstaining on ungrounded claims.

---

### Phase 6 — Agentic AI & 14 Sub-Agents Orchestration
* **Rule-Engine Sub-Agents (`app/services/intelligence/sub_agents.py`)**:
  * Audit `ForensicAuditorSubAgent`, `SupplyChainCatalystSubAgent`, `RedTeamBearCaseSubAgent`, `IncrementalROICSubAgent` (Agent 10), `ReverseValuationSubAgent` (Agent 11), and `PMKillTestSubAgent` (Agent 12).
  * Verify strict adherence to standardized schema: `FINDING / EVIDENCE / SEVERITY / CONFIDENCE / SOURCE / THESIS_INVALIDATION_TRIGGER`.
* **Specialized Research & Forensic Agents**:
  * Audit `footnote_rpt_auditor.py`, `forensic_auditor.py`, `financial_forensics.py`, `concall_evidence_extractor.py`, `investment_committee.py`, `debate_engine.py`, `thesis_tracker.py` / `thesis_monitor.py`, and `alternative_data.py`.
* **Skill 42 Multi-Lens Evidence Synthesis & Qualitative Multiplier**:
  * Audit `app/services/intelligence/event_extractor.py` and `qualitative_multiplier_engine.py`.
  * Confirm sub-agent finding severities (`CRITICAL_RED_FLAG`, `HIGH_PENALTY`, `MODERATE_RISK`, `POSITIVE_CATALYST`) map to deterministic score adjustments.
  * **CRITICAL INVARIANT**: Confirm GenAI CANNOT shift quantitative scores by arbitrary un-audited percentages (bounded strictly within $M_{\text{Qual}} \in [0.85, 1.15]$).

---

### Phase 7 — Financial Friction, Backtesting, Risk Gates & Provider Resilience
* **Data Provider Fallback Chain**:
  * Audit `app/services/market_data.py` across YFinance, Yahoo Direct, and NSE India APIs under rate-limiting and connection drops.
* **Backtest Friction & Slippage Modeling**:
  * Audit `app/services/backtesting/` (`walk_forward.py`, `replay_engine.py`, `score_bucket_analysis.py`, `validation_framework.py`).
  * Verify explicit deduction of transaction costs (`slippage_pct`, `stt_brokerage_pct`) and capital allocation sizing (`capital_allocated_pct`, `portfolio_contribution_alpha`).
* **Risk & Surveillance Gates**:
  * Audit `app/services/risk/` (`portfolio_risk.py`, `surveillance_gate.py`, `trade_management.py`).
  * Verify ₹1.5Cr Average Daily Turnover (ADTV) liquidity floor and multi-asset sector concentration caps ($>35\%$ sector weight triggers hard rejection).
* **Unified Persistence & Data Tier (`db.py`)**:
  * Audit database connection factory for PostgreSQL (Production) and SQLite (Local/Vercel) parameter translation (`?` vs `%s`).

---

### Phase 8 — API Synchronization & 30 Frontend Modules UI/UX Architecture
* **API Route & Schema Synchronization**:
  * Audit 100% of FastAPI endpoints in `app/api/` (20 controllers, 92 operations) against frontend fetch calls in `frontend_deploy/js/api.js` and `docs/api_contract.json`.
  * Confirm zero route mismatches, proper query parameter passing, response parsing, and error status handling.
* **30 Frontend JavaScript Modules Audit (`frontend_deploy/js/`)**:
  * Audit all 30 JS files: `aiassistant_dock.js`, `ai_committee_panel.js`, `api.js`, `bootstrap.js`, `cagr_matrix_panel.js`, `community_feed.js`, `compare_panel.js`, `conviction_panel.js`, `drift_panel.js`, `footer.js`, `genai_redteam_panel.js`, `growth_market_gap_panel.js`, `header_nav.js`, `institutional_intelligence_panel.js`, `lifecycle_panel.js`, `main_canvas.js`, `mivs_scorecard_panel.js`, `mobile_drawer.js`, `multibagger_panel.js`, `news_notifications.js`, `probability_panel.js`, `red_team_stress_panel.js`, `scorecard_panel.js`, `sidebar_nav.js`, `swing_alerts_panel.js`, `technical_panel.js`, `thesis_panel.js`, `timeline_panel.js`, `watchlist_panel.js`, `window_manager.js`.
  * Verify UI state management, window focus, event dispatching, and fallback handling when backend returns `coming_soon` or `data_insufficient`.
* **HTML Components & Data Digests**:
  * Audit `frontend_deploy/index.html`, `components/header.html`, `components/sidebar.html`, `components/conviction_panel.html`, and `frontend_deploy/data/digests/watchlist_digest.json`.

---

### Phase 9 — Comprehensive Inter-Module, Cross-Engine & Cross-Agent Interaction Audit
* **End-to-End Pipeline & Cross-Subsystem Interoperability**:
  * Trace and audit the complete live execution chain across all sections and files:
    $$\text{Data Ingestion} \longrightarrow \text{Sanitizer (MAD)} \longrightarrow \text{PIT Research DB} \longrightarrow \text{Candidate Gate (E6)} \longrightarrow \text{Quant Engines (A1-D18, E1-E21)} \longrightarrow \text{14 Sub-Agents} \longrightarrow \text{Debate \& Red-Team} \longrightarrow \text{Arbiter Brain (Hard Vetoes)} \longrightarrow \text{Conformal ML Calibration} \longrightarrow \text{Prediction Ledger} \longrightarrow \text{REST APIs (20 Controllers)} \longrightarrow \text{Frontend UI (30 Panels)}$$
  * Verify that **every section, file, engine, module, and agent can interact with upstream and downstream components without data type mismatches, missing attributes, or broken contracts**.
* **Governance Veto Propagation**:
  * Verify that a veto emitted in an upstream forensic engine or sub-agent (e.g., Promoter Pledge $> 40\%$ in `SUB_AGENT_FORENSIC` or failed `SUB_AGENT_PM_KILL_TEST`) propagates unbroken through `QualitativeMultiplierEngine` and `Arbiter` to force final conviction to `AVOID`.
* **Closed-Loop Outcome & Recalibration Interaction**:
  * Verify interaction between `PredictionLedger` $\rightarrow$ `OutcomeChecker` $\rightarrow$ `ScoreCalibration` $\rightarrow$ `DriftDetector` $\rightarrow$ `ChampionChallenger`: Confirm that actual market outcomes trigger automated learning and model recalibration.
* **Background Asynchronous Task Interaction**:
  * Verify `app/tasks/scheduler.py` and `worker.py` interaction with database refresh, market data ingestion, and watchlist digest generation.

---

### Phase 10 — System Bundles, Knowledge Parity & Full Pytest Regression Certification
* **Consolidated System Bundle Parity**:
  * Audit bundle manifests (`CONSOLIDATED_5_FILE_SYSTEM/MANIFEST.json`, `CONSOLIDATED_12_FILE_SYSTEM/MANIFEST.json`).
  * Verify source hash parity between bundle files and active workspace code across all 97 canonical source files.
* **Automated Regression Suite Execution**:
  * Execute full `pytest` regression suite across all 566 test cases in 78 test files.
  * Assert 100% pass rate with zero unhandled exceptions, regressions, or broken contracts.

---

## 📊 Final Master Deliverable Format

Produce a dense, highly analytical, token-efficient Markdown report (`EQUITY_LAB_MASTER_AUDIT_REPORT.md`) containing:
1. **Executive Verdict & System Scorecard** (0–100 composite institutional rating & individual phase sub-scores).
2. **Previous-Audit Remediation Matrix** (`FIXED` | `PARTIALLY FIXED` | `UNRESOLVED` | `REGRESSED`).
3. **Phase-by-Phase Detailed Findings** (Phases 1 to 10: code snippets, file URIs, mathematical formulas, inter-module interaction proofs — concise, dense, zero redundancy).
4. **Discovered Defect & Gap Log** categorized strictly by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`).
5. **Strong, Realistic & Project-Aligned Detailed Suggestions**:
   * Concrete architectural, algorithmic, latency, and token-optimization proposals.
   * Actionable enhancements for engine throughput, conformal calibration speed, and risk gate strictness.
   * 100% project-aligned: Zero disruptive external rewrites; fully compatible with existing Python, FastAPI, and vanilla JS structures.
6. **Final Production Status Certification**: `PRODUCTION READY` | `CONDITIONALLY READY` | `NOT READY`.

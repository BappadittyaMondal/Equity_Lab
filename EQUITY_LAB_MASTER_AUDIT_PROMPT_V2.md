# Master Audit Request: 8-Phase Institutional Full-System Audit

**Persona & Role**: Senior Software Architect, Quantitative Financial Systems Auditor, and AI Systems Specialist.  
**Target System**: Equity Lab v0.0 Platform (`app/`, `frontend_deploy/`, `canonical_source/`, `CONSOLIDATED_*`).  
**Core Objective**: Perform an exhaustive, evidence-backed full-system audit of the Equity Lab architecture. Verify data truth, mathematical determinism, discovery engines (Microcap Multibagger, 3/10/30-Day Swing 15%+ Upside, Turnaround, Momentum), GenAI anti-hallucination guardrails, sub-agent intelligence orchestration, API synchronization, and production readiness. Zero superficial approvals allowed.

---

## 🏛️ System Architecture Inventory Baseline

| Architectural Layer | Inventory Count | Components & Scope |
| :--- | :---: | :--- |
| **Python Service Subsystems** | **15 Modules** | `decision_brain`, `strategies`, `research`, `intelligence`, `rag`, `ml`, `turnaround`, `ai_committee`, `data_ingestion`, `longitudinal`, `orchestration`, `synthesis`, `query`, `risk/monitoring`, `core/models` |
| **Specialized Engines** | **46 Engines** | 3 Brain Engines + 18 Strategy Engines (A1–D18) + 19 Research Engines (E1–E19) + 6 ML/Turnaround Engines |
| **GenAI Subsystems** | **6 Modules** | LLM Query Router, Concall NLP Commentary, GenAI Red-Team, RAG Document Store, Anti-Hallucination Claim Verifier, Investment Committee Synthesizer |
| **Agentic AI & Sub-Agents** | **7 Sub-Agents** | `SUB_AGENT_FORENSIC`, `SUB_AGENT_SUPPLY_CHAIN`, `SUB_AGENT_RED_TEAM`, Arbiter Veto Gatekeeper, Skill 42 Multi-Lens Synthesizer, Thesis Invalidation Agent, Scuttlebutt Agent |
| **Libraries & Source Code** | **12 Core + 97 Files** | 12 Python Core Libraries (`pandas`, `numpy`, `lightgbm`, `fastapi`, `pydantic`, etc.) + 97 Canonical Source Files |
| **Canonical AI Skills** | **42 Skills** | 25 Workflow & Sector Skills (`04_Skills_Reference_v_0_0.md`) + 17 Standalone Analytical Lens Skill Files |
| **Knowledge Base** | **48 Domains** | 48 Institutional & Trading Knowledge Domains across 51 Files & 5 Consolidated Master Knowledge Volumes |

---

## 📜 System Audit Laws & Execution Rules

1. **The Pipeline Law**: Generative AI is strictly confined to parsing unstructured text, concall commentary, footnote analysis, and adversarial red-team thesis stress-testing. All quantitative scoring formulas, screening algorithms, market probability distributions, and pricing math MUST remain 100% deterministic in Python (`numpy` / `pandas`).
2. **Zero-Hearsay Rule**: Every finding, approval, or defect MUST be verified directly against active workspace source files, Pydantic schemas, FastAPI endpoints, and `pytest` execution logs.
3. **Evidence-Based Math Requirement**: All probability metrics (e.g. 15%+ upside in 3/10/30 days) must be backed by empirical historical distributions and conformal prediction intervals, never ungrounded LLM guesses.
4. **Strict Defect Severity Taxonomy**: Categorize all system findings into standard severity tiers: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFORMATIONAL`.
5. **Token Efficiency & Anti-Redundancy Directive**: Maximize token efficiency without compromising audit depth. Do NOT re-read the same file repeatedly; execute targeted single-pass reads per module, synthesize findings densely, and eliminate repetitive markdown boilerplate or conversational filler.
6. **Project-Aligned Strict Optimization Suggestions**: Deliver deeply analytical, highly actionable, and project-aligned optimization recommendations that maintain 100% compatibility with existing engine capabilities, performance, and deterministic pipeline rules.

---

## 🔬 Phase-by-Phase Detailed Audit Requirements

### Phase 1 — Data Truth, Sanitization & High-Frequency Signal Integrity
* **OHLCV Guards & Ingestion Protection**:
  * Audit `DailyPriceIngester` in `app/services/market_data.py` to ensure strict OHLCV guards filter out `NaN`, `None`, `0.0`, negative prices, and inverted high/low price rows before DB persistence.
  * Verify Point-in-Time (PIT) timestamp enforcement (`published_at <= as_of_date`) across historical financial statements to eliminate look-ahead bias.
  * Audit missing-data returns: Confirm unavailable metrics return `None` (or `DATA_UNAVAILABLE` payload) rather than silent default fallbacks (e.g., zero margin or static P/E fallbacks).
* **Multi-Source Data Sanitizer & Tick Quarantine (Skill 01)**:
  * Audit `app/services/utils/data_sanitizer.py` and `app/tests/test_data_sanitizer.py`.
  * Verify Median Absolute Deviation (MAD > 4.0) tick quarantine logic to reject corrupt price spikes.
  * Audit `Data_Trust_Vector` composite tiering (`HIGH`, `MODERATE`, `LOW`, `UNTRUSTED`). Confirm `UNTRUSTED` inputs trigger immediate execution halt (`ABSTAIN`).

---

### Phase 2 — 18 Strategy Engines Audit (A1 – D18)
* **Category A: Derivatives & Options Engines (A1–A3)**:
  * Audit `options_a1_a3.py` & `options_a2.py`: Option Arbitrage, Calendar Spreads, Short Strangle Payoff, and Iron Condor Volatility models.
* **Category B: Technical & Microstructure Engines (B4–B8)**:
  * Audit `technical_engines.py`, `vcp_b5.py`, `sepa_b8.py`, `technical_trend_rs.py`, and `obv_accumulation_engine.py`.
  * Validate mathematical calculation of Volume Price Analysis (VPA), Volatility Contraction Pattern (VCP), Relative Strength (RS) Mansfield score, Pocket Pivots, and SEPA trend templates.
* **Category C: Fundamental & Forensic Engines (C9–C14)**:
  * Audit `reverse_dcf_c9.py`, `owner_earnings_c10.py`, `forensic_engine.py`, `growth_arbitrage.py`, and `microcap_integrity.py`.
  * Inspect math for Reverse DCF "Proof by Contradiction", Beneish M-Score, Altman Z-Score, Piotroski F-Score, CAGR Matrix, and Microcap Integrity risk gates.
* **Category D: Momentum & Quantitative Filters (D15–D18)**:
  * Audit `ath_breakout_d15.py`, `dual_momentum_d16.py`, and `saatvik_d18.py`.
  * Verify All-Time High (ATH) breakouts, Dual Momentum lookbacks, and Saatvik Ethical/Sin-Industry exclusion filters.

---

### Phase 3 — Research, Screener & Discovery Engines Audit (E1 – E19)
* **Institutional Stealth Multibagger Discovery Engine (E19)**:
  * Audit `app/services/research/institutional_multibagger_engine.py` and `app/services/strategies/inflection_multibagger.py`.
  * Verify early-stage inflection detection: Vectorized base consolidation filtering, capex expansion triggers, and forensic risk gates.
* **Swing Predictive Engine (E18 — 3/10/30-Day Horizon)**:
  * Audit `app/services/strategies/swing_predictive_engine.py` and `app/api/technical.py`.
  * Verify historical probability calibration for predicting **15%+ upside within 3, 10, and 30 trading days**.
  * Assert strict adherence to **3:1 Reward-to-Risk ratio** cutoffs and volatility-adjusted stop-loss placement.
* **Turnaround Stock Finder & Life-Cycle Engine**:
  * Audit `app/services/turnaround/turnaround_engine.py`, `turnaround_model.py`, and `lifecycle.py`.
  * Validate NCLT corporate turnaround triggers, operating leverage recovery inflection, and value-trap exclusion filters.
* **Microcap & Quality Growth Discovery Engines (E1, E11, E12)**:
  * Audit `unit_economics.py` (9 sector models), `mivs_engine.py` (Multibagger Integrity & Valuation System), `scorecard_service.py`, and `peer_normalization.py`.

---

### Phase 4 — Central Decision Brain, Conformal Risk & ML Core
* **Arbiter Engine & Governance Vetoes (BRAIN-01)**:
  * Audit `app/services/decision_brain/arbiter.py`.
  * Verify master synthesis logic combining 18 strategies + 19 research engine scores into unified conviction tiers (`STRONG_BUY`, `BUY`, `HOLD`, `AVOID`).
  * Confirm governance hard-veto enforcement: A single critical promoter pledge or forensic manipulation flag MUST force conviction to `AVOID`.
* **Scenario Prediction Engine & Red-Team (BRAIN-02, BRAIN-03)**:
  * Audit `prediction_engine.py` and `red_team_engine.py` for Bull/Base/Bear probability distributions and pre-mortem risk identification.
* **Conformal Risk Tiering & Machine Learning Loop**:
  * Audit `app/services/ml/baseline_model.py`, `conformal_prediction.py`, `evt_gpd_engine.py`, and `prediction_ledger.py`.
  * Verify 90% empirical coverage bounds in `app/api/probability.py` and explicit numerical width cutoffs (`CONFIRMED_HIGH`: Interval Width ≤ 20% of reference price).
  * Confirm prediction ledger UUID logging and automated post-mortem hit-rate evaluations (7d, 30d, 90d horizons).

---

### Phase 5 — GenAI Architecture, Anti-Hallucination & RAG Guardrails
* **Pipeline Law Enforcement & Structuring**:
  * Audit `app/services/llm.py`, `app/services/query/`, and `app/services/ai_committee/investment_committee.py`.
  * Confirm LLM output parsing enforces strict Pydantic schemas without loose, unvalidated raw text streams.
* **Concall NLP Commentary & GenAI Red-Teaming**:
  * Audit `app/services/strategies/concall_nlp.py` and `app/services/research/genai_redteam_service.py`.
  * Verify extraction of management guidance shifts, tone metrics, and adversarial pre-mortem bear case generation.
* **RAG Document Store & Anti-Hallucination Claim Verifier**:
  * Audit `app/services/rag/document_store.py` and `claim_verifier.py`.
  * Verify SHA-256 filing provenance hashes and point-in-time filing disclosures.
  * Audit claim verification logic: Ensure generated text statements are verified against factual observation vectors, automatically flagging ungrounded claims.

---

### Phase 6 — Agentic AI, Sub-Agent Orchestration & Skill 42 Synthesis
* **Sub-Agent Rule Rubrics (`app/services/intelligence/sub_agents.py`)**:
  * Audit `ForensicAuditorSubAgent`, `SupplyChainCatalystSubAgent`, and `RedTeamBearCaseSubAgent`.
  * Verify strict `FINDING / EVIDENCE / SEVERITY / CONFIDENCE / SOURCE` schema compliance.
* **Skill 42 v2 Multi-Lens Evidence Synthesis**:
  * Audit `app/services/intelligence/event_extractor.py` and `qualitative_multiplier_engine.py`.
  * Confirm sub-agent finding severities (`CRITICAL_RED_FLAG`, `HIGH_PENALTY`, `MODERATE_RISK`, `POSITIVE_CATALYST`) map to deterministic score adjustments.
  * **CRITICAL RULE**: Confirm GenAI CANNOT shift quantitative scores by arbitrary un-audited percentages (no bare ±15% LLM shifts).
* **Longitudinal Thesis & Scuttlebutt Agents**:
  * Audit `app/services/research/thesis_tracker.py` and `app/services/strategies/alternative_data.py`.

---

### Phase 7 — Financial Friction, Backtesting & Provider Resilience
* **Data Provider Fallback Chain**:
  * Audit `app/services/market_data.py` across YFinance, Yahoo Direct, and NSE India APIs under rate-limiting and connection drops.
* **Backtest Friction & Slippage Modeling**:
  * Audit `app/services/backtesting/walk_forward.py` and `app/tests/test_backtesting.py`.
  * Verify explicit deduction of transaction costs (`slippage_pct`, `stt_brokerage_pct`) during multi-horizon backtests.
* **Unified Persistence & Data Tier (`db.py`)**:
  * Audit database connection factory for PostgreSQL (Production) and SQLite (Local/Vercel) parameter translation (`?` -> `%s`).

---

### Phase 8 — API Synchronization, System Bundles & Master Production Certification
* **API & Frontend Contract Synchronization**:
  * Audit 100% of FastAPI endpoints in `app/api/` (20 controllers) against frontend fetch calls in `frontend_deploy/js/api.js`.
  * Verify exact path matching (e.g. `/api/v1/research/ai-committee/`, `/api/v1/technical/swing-predictive`).
  * Confirm payload parameter alignment, nullability handling, and UI fallbacks.
* **Consolidated System Bundle Parity**:
  * Audit bundle manifests (`CONSOLIDATED_5_FILE_SYSTEM/MANIFEST.json`, `CONSOLIDATED_9_FILE_SYSTEM/MANIFEST.json`).
  * Verify source hash parity between bundle files and active workspace code across all 97 canonical source files.
* **Automated System Test Certification**:
  * Execute full `pytest` regression suite across all 543+ tests.
  * Confirm 100% pass rate with zero unhandled failures or regressions.

---

## 📊 Final Master Deliverable Format

Produce a dense, highly analytical, token-efficient Markdown report (`EQUITY_LAB_MASTER_AUDIT_REPORT.md`) containing:
1. **Executive Verdict & System Scorecard** (0–100 overall score & sub-scores).
2. **Previous-Audit Remediation Matrix** (`FIXED` | `PARTIALLY FIXED` | `UNRESOLVED` | `REGRESSED`).
3. **Phase-by-Phase Detailed Findings** (Phases 1 to 8, with code snippets, file URIs, and math formulas — concise and zero-redundancy).
4. **Discovered Defect Log** categorized by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
5. **Strict & Actionable Optimization Recommendations**: Deeply analytical, realistic, and project-aligned suggestions for architecture, speed, token consumption reduction, and risk gates — maintaining 100% compatibility with existing platform capabilities and performance.
6. **Final Production Status Certification**: `PRODUCTION READY` | `CONDITIONALLY READY` | `NOT READY`.

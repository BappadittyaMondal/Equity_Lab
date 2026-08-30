# Master Audit Request: 6-Phase Institutional Full-System Audit

**Persona & Role**: Senior Software Architect, Quantitative Financial Systems Auditor, and AI Systems Specialist.  
**Target System**: Equity Lab v0.0 Platform (`app/`, `frontend_deploy/`, `CONSOLIDATED_*`).  
**Core Objective**: Perform an exhaustive, evidence-backed full-system audit from scratch. Verify system quality, data truth, financial math, API contract synchronization, sub-agent intelligence orchestration, and production readiness. Zero superficial approvals allowed.

---

## 📜 System Audit Laws & Execution Rules

1. **The Pipeline Law**: Generative AI is strictly confined to parsing unstructured text, footnote analysis, and red-team thesis stress-testing. All quantitative metrics, screening formulas, and pricing calculations MUST remain 100% deterministic in Python.
2. **Zero-Hearsay Rule**: Every finding, approval, or defect must be verified directly against actual source files, Pydantic schemas, REST endpoints, and `pytest` execution outputs.
3. **Strict Severity Taxonomy**: Categorize all system issues as `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFORMATIONAL`.

---

## 🔬 Phase-by-Phase Detailed Audit Requirements

### Phase 1 — Ground Truth Audit (Data Truth, Financial Math & Code Quality)
* **Data Integrity & Provenance**:
  * Audit `DailyPriceIngester` to ensure strict OHLCV guards filter out `NaN`, `None`, `0.0`, and inverted high/low price rows before DB storage.
  * Verify Point-in-Time (PIT) timestamp enforcement (`published_at <= as_of_date`) across backtest datasets to prevent look-ahead bias.
  * Inspect missing-data handling: Ensure unavailable financial metrics return `None` rather than arbitrary default fallbacks (e.g. no default P/E of 22.0 or 0.0 margin fallbacks).
* **Core Financial Mathematics & Models**:
  * Inspect mathematical formulas for CAGR, DCF, Reverse DCF, Beneish M-Score, Altman Z-Score, ROE, ROCE, and ROIC.
  * Audit centralized math utilities (`app/services/utils/math.py`) for zero-period handling, negative start values, infinity/NaN bounds, and numerical stability.
* **Codebase Health & Structure**:
  * Audit Python modules for broken imports, circular dependencies, dead code, and redundant files.
  * Verify exception handling: Ensure failures are cleanly logged without silent try-except blocks or unhandled runtime crashes.

### Phase 2 — Integration, Decision Logic & API Synchronization
* **End-to-End Pipeline & Strategy Engine**:
  * Trace complete data flow: `Ingestion → DataSanitizer → Quant Engines → Dynamic Candidate Gate → Sub-Agents → VirtualICArbiter → Conformal Tiering → REST APIs → Frontend UI`.
  * Audit factor weighting, screening logic, multibagger detectors (`InstitutionalMultibaggerEngine`), turnaround gates, and value-trap filters.
* **GenAI Integration & Guardrails**:
  * Audit GenAI orchestration modules and enforce the **Pipeline Law**.
  * Validate Pydantic schemas: Ensure qualitative findings conform to structured `QualitativeEvidenceFinding` formats without unvalidated raw text leaks.
* **API & Frontend Synchronization**:
  * Audit 100% of FastAPI endpoints in `app/api/` against frontend calls in `frontend_deploy/js/api.js`.
  * Verify exact endpoint path matching (specifically `/api/v1/research/ai-committee/`).
  * Validate JSON request/response parameter names, data types, nullability, and default fallback values.

### Phase 3 — Red-Teaming, Stress Testing & Consolidated Bundles
* **Adversarial Financial Stress Testing**:
  * Stress-test system response under extreme conditions: debt explosions ($D/E > 2.0x$), sudden margin collapse, promoter pledge spikes ($> 50\%$), and missing price history.
  * Confirm that engines emit hard risk flags or `ABSTAIN` tiers rather than mechanically outputting optimistic scores.
* **Consolidated System Bundle Audit**:
  * Audit bundle manifests (`CONSOLIDATED_5_FILE_SYSTEM/MANIFEST.json`, `CONSOLIDATED_12_FILE_SYSTEM/MANIFEST.json`).
  * Verify 100% source hash parity between bundle files and active workspace source code.
  * Confirm bundle self-sufficiency for external LLM deployment without missing references or broken prompts.

### Phase 4 — Market Signal & Sub-Agent Orchestration Audit
* **Multi-Source Data Sanitizer (Skill 01)**:
  * Audit `app/services/utils/data_sanitizer.py` and `app/tests/test_data_sanitizer.py`.
  * Verify Median Absolute Deviation (MAD > 4.0) tick spike quarantine logic.
  * Audit `Data_Trust_Vector` composite tiering (`HIGH`, `MODERATE`, `LOW`, `UNTRUSTED`). Verify that `UNTRUSTED` data halts engine execution (`ABSTAIN`).
* **Sub-Agent Structured Evidence & Arbiter Synthesis (Skill 42 v2)**:
  * Audit `app/services/intelligence/event_extractor.py`, `sub_agents.py`, and `arbiter.py`.
  * Verify sub-agents (`ForensicAuditor`, `SupplyChainCatalyst`, `RedTeamBearCase`) emit strict `FINDING / EVIDENCE / SEVERITY / CONFIDENCE / SOURCE` schemas.
  * Verify `VirtualICArbiter`: Confirm that finding severity (`CRITICAL_RED_FLAG`, `HIGH_PENALTY`, `MODERATE_RISK`, `POSITIVE_CATALYST`) maps to deterministic Python score adjustments.
  * **CRITICAL RULE**: Confirm GenAI CANNOT shift quantitative scores by arbitrary un-audited percentages (no bare ±15% LLM score shifts).
* **Dynamic Candidate Gate & Conformal Risk Tiering (Skill 99)**:
  * Audit `app/services/intelligence/candidate_gate.py` and `conformal_tiering.py`.
  * Verify `DynamicCandidateGate`: Confirm fixed candidate headcounts (e.g. hardcoded "Top 25") are eliminated in favor of dynamic threshold gating (`Data_Trust >= HIGH & Inflection_Score >= Min_Threshold`).
  * Verify `ConformalTieringEngine`: Confirm integration with `app/api/probability.py` 90% empirical coverage bounds and explicit numeric interval width cutoffs (`CONFIRMED_HIGH`: Width ≤ 20% of reference price).
* **Immutable Prediction Ledger**:
  * Audit `app/services/intelligence/prediction_ledger.py` and `app/tests/test_prediction_ledger.py`.
  * Verify prediction logging (UUID generation, base price, target bounds, confidence tier, thesis invalidation triggers).
  * Audit post-mortem evaluation functions at 7d, 30d, and 90d horizons.

### Phase 5 — Multi-Model Resilience & Financial Friction Audit
* **Data Provider Fallback Resilience**:
  * Audit provider chain in `app/services/market_data.py` across YFinance, Yahoo Direct, and NSE India providers under API rate limits and network degradation.
* **Backtest Friction & Slippage Modeling**:
  * Audit `app/services/backtesting/walk_forward.py` and `app/tests/test_backtesting.py`.
  * Verify explicit deduction of transaction costs (`slippage_pct`, `stt_brokerage_pct`) during multi-horizon backtesting.

### Phase 6 — Master Production Certification & Scorecard
* **Test Suite Certification**:
  * Execute the full test suite (`pytest`) across all 500+ unit and integration test files.
  * Confirm 100% pass rate with zero unhandled failures.
* **Final Deliverable Requirements**:
  * Produce a detailed Markdown audit report containing:
    1. Executive Verdict & Summary Scorecard (0–100 Rating).
    2. Previous-Audit Cross-Check Matrix (`FIXED` | `PARTIALLY FIXED` | `UNRESOLVED` | `REGRESSED`).
    3. Phase 1 Ground Truth Audit (Data Truth, Financial Math & Code Quality).
    4. Phase 2 Integration & API Synchronization Audit.
    5. Phase 3 Red-Team & Bundle Audit.
    6. Phase 4 Sub-Agent & Intelligence Audit.
    7. Phase 5 Data Resilience & Backtest Audit.
    8. Phase 6 Master Production Certification & Handoff Guide.
    9. Final Production Status: `PRODUCTION READY` | `CONDITIONALLY READY` | `NOT READY`.

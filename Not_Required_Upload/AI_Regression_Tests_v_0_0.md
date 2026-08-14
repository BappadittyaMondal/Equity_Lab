# AI Regression Tests

**Version:** v_0.0  
**Status:** Production Ready (Final)  
**Category:** Verification & QA  
**Priority:** Critical  
**Role:** Standard Regression Test Scenarios  
**Architecture State:** Frozen

---

## 1. Pipeline Verification Path

Every test scenario in this suite exercises and verifies the complete pipeline path:

```
[Intent] ──> [TaskObject] ──> [ResearchPlanObject] ──> [Research & Evidence] 
                │
                └──> [Reasoning & Decision] ──> [QA & Audit] ──> [OutputObject]
```

---

## 2. Regression Test Scenarios

### Scenario 1: Stock Screening
*   **Intent**: Identify high-growth mid-caps with ROCE > 20% and Debt/Equity < 0.5.
*   **Task**: Task Orchestrator classifies intent and creates `TaskObject` with `ResearchDepth: Quick` and specific screener query filters.
*   **Plan**: Intelligence Engine selects `Domain_40_Screening_Strategies` and `DCF Valuation Skill`.
*   **Research & Evidence**: Research Engine runs queries, captures screening result table, creates `EvidenceObject` pointing to the screener database.
*   **Reasoning & Decision**: Reasoning Engine processes results, applies DCF model, and constructs `DecisionObject` with a candidate buy list.
*   **QA & Audit**: Quality Audit checks schema compliance and validates that criteria filters match the output list.
*   **Output**: Output System formats a table of screened companies with associated metrics.

### Scenario 2: Swing Trade Setup
*   **Intent**: Evaluate short-term swing entry for Company X based on a breakout pattern.
*   **Task**: `TaskObject` specifies `TimeHorizon: Short-Term` (Swing) and `ResearchDepth: Quick`.
*   **Plan**: Intelligence Engine loads `Domain_07_Technical_Analysis`, `Domain_30_Swing_Positional_Technical_Patterns`, and `Technical Pattern Skill`.
*   **Research & Evidence**: Research Engine extracts price, volume, and moving averages; creates `EvidenceObject` with recent chart data.
*   **Reasoning & Decision**: Technical Pattern Skill evaluates resistance breakouts and relative strength (RSI); produces `DecisionObject` detailing entry/exit levels.
*   **QA & Audit**: Quality Audit checks risk parameters and stop-loss inclusion.
*   **Output**: Output System formats a trade setup card with visual price thresholds.

### Scenario 3: Multibagger Research
*   **Intent**: Analyze high-conviction small-cap multibagger potential for Company Y.
*   **Task**: `TaskObject` specifies `ResearchDepth: Institutional` and `TimeHorizon: Long-Term`.
*   **Plan**: Intelligence Engine schedules `Domain_28_Multibagger_Turnaround_Framework`, `Domain_29_MicroCap_Risk_Framework`, and `Multibagger/Turnaround Skill`.
*   **Research & Evidence**: Research Engine gathers 5-year financials, promoter shareholding histories, and industry growth rates (creates 12+ `EvidenceObjects`).
*   **Reasoning & Decision**: Skill Pack computes reinvestment rates, industry tailwinds, and promoter integrity metrics; produces a long-term conviction thesis.
*   **QA & Audit**: Quality Audit reviews liquidity filters and governance scores.
*   **Output**: Output System delivers an Institutional Investment Memo.

### Scenario 4: Turnaround Analysis
*   **Intent**: Assess Company Z undergoing corporate restructuring and debt reduction.
*   **Task**: `TaskObject` specifies `ResearchDepth: Deep`.
*   **Plan**: Loads `Domain_28_Multibagger_Turnaround_Framework` and `Domain_20_Credit_Debt_Markets`.
*   **Research & Evidence**: Extracts quarterly debt ratios, asset sale filings, and promoter pledged shares.
*   **Reasoning & Decision**: Reasoning Engine evaluates interest coverage improvements and cash flow generation to pay down debt.
*   **QA & Audit**: Quality Audit validates debt reconciliation math against filings.
*   **Output**: Output System emits a Turnaround Rating scorecard.

### Scenario 5: Long-Term Compounder
*   **Intent**: Analyze Company A for a permanent compounder portfolio.
*   **Task**: `TaskObject` specifies `TimeHorizon: 10-Year` and `ResearchDepth: Deep`.
*   **Plan**: Loads `Domain_25_Moat_Competitive_Advantage` and `Domain_06_Fundamental_Analysis`.
*   **Research & Evidence**: Extracts 10-year ROCE, market share stability, and pricing power history.
*   **Reasoning & Decision**: Moat Skill analyzes entry barriers, cost advantages, and brand strength to project returns.
*   **QA & Audit**: Quality Audit checks consistency of pricing power assertions.
*   **Output**: Output System outputs a Moat & Franchise Quality profile.

### Scenario 6: Forensic Accounting
*   **Intent**: Conduct a forensic audit on Company B's related-party transactions.
*   **Task**: `TaskObject` specifies `ResearchDepth: Institutional` and flags `Forensic Accounting` as mandatory.
*   **Plan**: Loads `Domain_24_Forensic_Accounting`, `Domain_08_Corporate_Governance`, and `Forensic Accounting Skill`.
*   **Research & Evidence**: Extracts CEO salary, auditor fees, related-party sales, and trade receivables.
*   **Reasoning & Decision**: Forensic Accounting Skill calculates accounting quality scores and flags promoter compensation anomalies.
*   **QA & Audit**: Quality Audit checks that all forensic red flags are linked to verified citations.
*   **Output**: Output System generates a Forensic Risk report.

### Scenario 7: Portfolio Sizing & Decision
*   **Intent**: Size an allocation to Company C within a model portfolio.
*   **Task**: `TaskObject` specifies `ResearchDepth: Standard` and loads portfolio weights.
*   **Plan**: Loads `Domain_43_Portfolio_Management_Rules` and `Portfolio Sizing Skill`.
*   **Research & Evidence**: Collects volatility metrics, correlation coefficients, and target return variables.
*   **Reasoning & Decision**: Computes target weights based on conviction level and micro-cap risk caps.
*   **QA & Audit**: Quality Audit verifies that sizing does not violate maximum sector concentration rules.
*   **Output**: Output System outputs a Portfolio Allocation sheet.

### Scenario 8: Conflicting Evidence
*   **Intent**: Reconcile Company D's high revenue growth with zero cash flow from operations.
*   **Task**: `TaskObject` specifies `ResearchDepth: Deep`.
*   **Plan**: Intelligence Engine schedules Forensic Accounting and Fundamental analysis.
*   **Research & Evidence**: `EvidenceObject_1` lists revenue growth (+35%), while `EvidenceObject_2` lists Operating Cash Flow (-$2M) due to ballooning receivables.
*   **Reasoning & Decision**: Reasoning Engine detects the divergence, sets `ContradictionFlag: true`, applies the `ConsistencyFactor = 0.6` penalty, and limits `DecisionConfidence` to `0.50`.
*   **QA & Audit**: Quality Audit confirms the confidence penalty is correctly computed.
*   **Output**: Output System presents both positive growth and cash flow risk as competing scenarios.

### Scenario 9: Stale Data
*   **Intent**: Evaluate Company E using financial statements that are 120 days old.
*   **Task**: `TaskObject` specifies `ResearchDepth: Standard`.
*   **Plan**: Loads standard fundamental models.
*   **Research & Evidence**: Research Engine extracts the latest filing date (dated 120 days ago). The Context Manager sets `StalenessFlag: true`.
*   **Reasoning & Decision**: The `EvidenceConfidence` is multiplied by the staleness penalty (0.85).
*   **QA & Audit**: Quality Audit ensures the output contains a warning of stale inputs.
*   **Output**: Output System outputs research with an prominent warning label: `WARNING: STALE DATA USED`.

### Scenario 10: Failed Tool/Research Step
*   **Intent**: Scrape regulatory filings for Company F.
*   **Task**: `TaskObject` specifies `ResearchDepth: Standard`.
*   **Plan**: Schedules PDF extraction.
*   **Research & Evidence**: The extraction tool fails due to a network lease lock (transient error).
*   **Reasoning & Decision**: The Execution Engine catches the transient error, updates `AttemptID = 2`, and initiates backoff.
*   **QA & Audit**: Logged as recovery in progress.
*   **Output**: Step retries and succeeds, producing the required `EvidenceObject` with no downstream confidence impact.

### Scenario 11: Retry & Backoff
*   **Intent**: Retrieve historical pricing data for Company G.
*   **Task**: `TaskObject` specifies `ResearchDepth: Quick`.
*   **Plan**: Schedules API query.
*   **Research & Evidence**: The pricing API returns a 429 Rate Limit error.
*   **Reasoning & Decision**: The Execution Engine designates this a `retryable failure`, calculates backoff duration (2 seconds), and increments `RetryCount` on the `StateObject`.
*   **QA & Audit**: Verified as retry compliant.
*   **Output**: The second attempt succeeds. The final output is completed.

### Scenario 12: Partial Execution
*   **Intent**: Perform comprehensive analysis on Company H.
*   **Task**: `TaskObject` specifies `ResearchDepth: Institutional`.
*   **Plan**: Schedules 12 Knowledge Domains.
*   **Research & Evidence**: Due to context constraints, 2 optional Knowledge Domains are dropped. The Context Manager sets `CONTEXT_LIMITED` and `CoverageFactor = 0.83`.
*   **Reasoning & Decision**: Research Engine proceeds. The final `ResearchConfidence` is scaled down by the `CoverageFactor`.
*   **QA & Audit**: Quality Audit approves the partial execution since no gate-critical domains were dropped.
*   **Output**: Deliverable contains the research findings with a disclosure of omitted optional coverage.

### Scenario 13: Invalid Object (Schema Failure)
*   **Intent**: Submit research request with a malformed `TaskObject`.
*   **Task**: A malformed request is received (missing mandatory `Company` field).
*   **Plan**: Halted.
*   **Research & Evidence**: The Task Orchestrator validates the object, detects the missing parameter, and sets the validation status to `REJECTED`.
*   **Reasoning & Decision**: The Execution Engine catches this as a `non-retryable failure` and escalates to `F4 (Blocking)`.
*   **QA & Audit**: Session status marked `Failed` and immediately archived.
*   **Output**: Output System returns a request validation error: `INVALID_INPUT_OBJECT`.

### Scenario 14: Low-Confidence Decision
*   **Intent**: Evaluate speculative pharmaceutical startup Company I.
*   **Task**: `TaskObject` specifies `ResearchDepth: Deep`.
*   **Plan**: Loads sector deep dive and clinical trial tracking.
*   **Research & Evidence**: Data collected shows unverified tertiary blog posts regarding trial outcomes (`SourceTier: Tertiary`, weight = 0.4).
*   **Reasoning & Decision**: The `AdjustedEvidenceConfidence` drops to `0.28`. Since the core trial evidence is below `0.50`, the overall `DecisionConfidence` is capped at `0.50`.
*   **QA & Audit**: Quality Audit flags the low confidence.
*   **Output**: Output System delivers the report with a low conviction warning.

---

## Document Information

**Document:** AI_Regression_Tests_v_0.0.md  
**Version:** v_0.0  
**Status:** Production Ready  
**Dependencies:** AI_Pipeline_Specification_v_0.0.md, AI_Confidence_Standard_v_0.0.md  
**Consumed By:** Quality Audit, System Testing Harness  

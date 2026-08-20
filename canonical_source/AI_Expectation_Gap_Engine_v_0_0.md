<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Expectation Gap Engine (E7)
> **Role:** Fundamental valuation strategy engine
> **Use when:** Evaluating the gap between Reverse DCF market-implied growth rate and internal forecast fundamental growth rate.
> **Evidence rule:** Explicitly calculate Expectation Gap = Internal Forecast Growth - Reverse DCF Implied Growth. Categorize based on framework thresholds (+5% / -5%).

# Expectation Gap Engine (E7)

**Version:** v_0.0  
**Status:** Production  
**Category:** Fundamental Valuation  

## 1. Purpose

The Expectation Gap Engine (`E7`) evaluates the core premise of institutional multibagger stock selection: a stock becomes a multibagger when actual fundamental business performance materially exceeds what the current market share price already assumes. `E7` quantifies this expectation gap by comparing Reverse DCF market-implied growth against empirical internal forecast CAGRs.

## 2. Contract

**Required input:** `symbol`, optional `discount_rate` (default 12%), `terminal_growth` (default 4%), and point-in-time observation history.

**Output:** `ExpectationGapResponse` containing:
- `market_implied_growth`: 10-year FCF/earnings CAGR implied by current P/E multiple (C9 Reverse DCF).
- `internal_forecast_growth`: Empirical fundamental CAGR derived across Sales, PAT, EPS, FCF observations.
- `expectation_gap`: `internal_forecast_growth - market_implied_growth` (in percentage points).
- `gap_classification`: `POSITIVE_EXPECTATION_GAP`, `BALANCED_EXPECTATION`, `NEGATIVE_EXPECTATION_GAP`, or `DATA_INSUFFICIENT`.
- `evidence`: Audit trail documenting mathematical basis and classification logic.

## 3. Operating Rules

1. Normalize symbol before execution.
2. Calculate market-implied growth from Reverse DCF model (`C9`).
3. Compute internal forecast growth rate using empirical multi-period financial CAGRs from `ResearchDataStore`.
4. `Expectation Gap = Internal Forecast Growth - Market-Implied Growth`.
5. Classify according to institutional framework:
   - `POSITIVE_EXPECTATION_GAP` (Gap >= +5.0%): Market under-prices fundamental growth trajectory (Re-rating opportunity).
   - `NEGATIVE_EXPECTATION_GAP` (Gap <= -5.0%): Market price requires higher growth than company delivers (De-rating risk).
   - `BALANCED_EXPECTATION` (-5.0% < Gap < +5.0%): Current valuation fairly reflects internal growth forecast.
6. When price, P/E, or fundamental inputs are missing, output `DATA_INSUFFICIENT` without synthetic numbers.

## 4. Risk And Governance

A positive expectation gap is a valuation catalyst signal, not a guaranteed return. Materialization depends on management execution, operational delivery, and market re-rating. Analysts must verify forensic hygiene (`C13`), financial health (`C11`/`C12`), and macro regime context (`RegimeEngine`) before acting.

## 5. Failure Handling

If quote or fundamental history is unavailable, flag `data_insufficient = True` and set `confidence_score = 0.0`. Never fabricate baseline growth figures without explicit data lineage warnings.

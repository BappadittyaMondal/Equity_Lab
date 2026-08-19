<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** E6 Quality-Growth Candidate Screener
> **Role:** Universe pre-filter strategy
> **Use when:** Screening candidates before multi-engine conviction synthesis.
> **Evidence rule:** Preserve condition-level availability and distinguish a pre-filter from a recommendation.

# E6 Quality-Growth Candidate Screener

**Version:** v_0.0  
**Status:** Production  
**Category:** Universe Compounder Pre-Filter

## 1. Purpose

E6 screens an equity universe for quality-growth characteristics before a candidate is passed to the Arbiter and broader decision workflow. It is a narrowing mechanism, not a final investment call.

## 2. Contract

**Required input:** `symbol` and the available point-in-time fundamental, market, and governance observations.

**Output:** A structured audit containing `total_conditions`, `conditions_passed`, `conditions_failed`, `conditions_unavailable`, condition-level evidence, and risk warnings.

The implementation evaluates 28 quantitative and fundamental conditions. Every condition remains visible in the audit trail; unavailable observations are not silently converted into failures or passes.

## 3. Operating Rules

1. Normalize the symbol before lookup.
2. Use point-in-time observations and preserve the relevant observation dates.
3. Evaluate each quality, growth, financial-strength, valuation, and governance condition independently.
4. Report missing inputs explicitly.
5. Pass candidates onward for full analysis; never present the pre-filter result as a `BUY` recommendation.

## 4. Risk And Governance

A high pass count indicates alignment with the configured screen only. It does not establish intrinsic value, future returns, liquidity, suitability, or absence of fraud. Analysts must apply valuation, technical, forensic, sector, and macro checks before a conviction decision.

## 5. Failure Handling

If the required observation set is incomplete, return condition-level unavailable states and explain how missing data affects confidence. Do not invent values or use synthetic fallback observations.

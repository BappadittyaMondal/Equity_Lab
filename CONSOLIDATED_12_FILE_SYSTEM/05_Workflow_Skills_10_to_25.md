# 05_Workflow_Skills_10_to_25

> **IERL AI Equity OS — curated upload artifact**  
> Project Version: `0.0.0` · Bundle Version: `2.0` · Source Commit: `c45f42a`  
> Generated At: `2026-08-31T09:32:27.285839+00:00` · Source Hash: `cf810ace1a6fbc91` · Compiler: `consolidate_project.py` v2.0

## Operating contract

This is a generated, read-only working volume. The separately maintained source documents are authoritative; regenerate this file after changing a source. The wrapper provides navigation and execution discipline, but does not replace a source rule. Embedded source payloads are preserved verbatim between the `BEGIN` and `END` markers.

1. Route the request to the narrowest relevant upload file, then use the named embedded document(s); do not treat an unrelated volume as evidence.
2. Execute applicable skill steps in order. If a required input, timeframe, benchmark, or source is absent, state the gap and the effect on confidence; never silently invent it.
3. Separate **reported facts**, **calculations**, **assumptions**, and **inference**. Date all market-sensitive claims and identify the data source or user-provided input.
4. Surface disconfirming evidence, governance/forensic risk, liquidity risk, valuation risk, and material uncertainty before a conclusion. A positive screen is not investment advice or a guarantee.
5. When source documents conflict, prefer the more specific, later-versioned requirement; if unresolved, disclose the conflict and use the more conservative interpretation. Never override platform safety requirements.

## Fast task routing

| Upload file | Primary use | Sources |
|---|---|---:|
| `01_System_Core_Instructions_Architecture.md` | 01 System Core Instructions Architecture | 8 |
| `02_Engine_Contracts_Schemas.md` | 02 Engine Contracts Schemas | 9 |
| `03_Engine_Registries_Pipelines.md` | 03 Engine Registries Pipelines | 9 |
| `04_Workflow_Skills_01_to_09.md` | 04 Workflow Skills 01 to 09 | 2 |
| `05_Workflow_Skills_10_to_25.md` | 05 Workflow Skills 10 to 25 | 4 |
| `06_Analytical_Lens_Skills_26_to_34.md` | 06 Analytical Lens Skills 26 to 34 | 7 |
| `07_Analytical_Lens_Skills_35_to_41.md` | 07 Analytical Lens Skills 35 to 41 | 8 |
| `08_Knowledge_Base_Vol_1_Economics_Financials.md` | 08 Knowledge Base Vol 1 Economics Financials | 12 |
| `09_Knowledge_Base_Vol_2_Markets_Governance_Macro.md` | 09 Knowledge Base Vol 2 Markets Governance Macro | 12 |
| `10_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md` | 10 Knowledge Base Vol 3 Forensics Moats Banking | 8 |
| `11_Knowledge_Base_Vol_4_Sector_Deep_Dives.md` | 11 Knowledge Base Vol 4 Sector Deep Dives | 9 |
| `12_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md` | 12 Knowledge Base Vol 5 Screening Portfolio Glossaries | 10 |

**Default research sequence:** define decision and horizon → gather dated evidence → run the relevant workflow/analytical skill → apply risk and forensic checks → calculate/compare → present conclusion, counter-case, and confidence. For a company decision, consult core instructions, the applicable skill, fundamentals/valuation, sector context, and risk/forensics rather than relying on one metric.

## Scope and privacy boundary

This bundle contains static methodology and knowledge only. It contains no credentials and cannot by itself read local files, call APIs, fetch live market data, trade, or access private accounts. The following local integration/private files are intentionally excluded: `.env.example`, `API_KEYS_CONFIG.env`, `API_PROVIDERS_AND_FREE_TIERS_GUIDE.md`, `test_apis.py`.

## Embedded source manifest

The SHA-256 values cover the exact UTF-8 source payload, not this wrapper. Use the manifest to audit a rebuild.

| # | Source document | UTF-8 bytes | SHA-256 |
|---:|---|---:|---|
| 1 | `AI_18_Expert_Strategies_Execution_Skill.md` | 20,746 | `a7d5dfcc99cc6ee87f1524ba76de7b9a1341ed8c6b5beb5a7b3904728a8a0d39` |
| 2 | `AI_Comparison_Engine_Skill.md` | 11,607 | `347a6c211877aa7c9c2b90c5ce80652ada167ca53d8446bb60c0767a89d000fb` |
| 3 | `AI_Concentrated_SmallCap_Style_Thinking_Skill.md` | 14,363 | `1bf7e975808e08991688f65a4b64d0572eecc5b4abd6503231981ffe0c607e22` |
| 4 | `AI_DCF_Valuation_Skill.md` | 19,216 | `9ffb983cae45bd92e8392b39aafb423199e0040632c93f4991b5120e6cf27c93` |

---

<!-- BEGIN SYSTEM FILE 1: AI_18_Expert_Strategies_Execution_Skill.md | SHA256: a7d5dfcc99cc6ee87f1524ba76de7b9a1341ed8c6b5beb5a7b3904728a8a0d39 -->
## Embedded source 1: AI 18 Expert Strategies Execution Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI 18 Expert Strategies Execution Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI 18 Expert Strategies Execution Skill

Version: 1.0 | Status: Production Ready (Canonical Workflow Skill)  
Category: Execution Specialist — Master Strategy Orchestration & Diagnostic Engine  

---

## Purpose
This skill provides a standardized, gate-based diagnostic execution workflow to evaluate, screen, calculate, and generate decision cards across all 18 Expert Investing and Trading Strategies categorized into four distinct expert domains:
- **Category A (A1–A4):** Rule-Based Options & Systematic Strategies (Mr. Ankit Rai)
- **Category B (B5–B8):** Technical Growth & Second Brain Strategies (Mr. Aniketh Dsouza)
- **Category C (C9–C14):** Fundamental, Value & Structural Strategies (Mr. Anshul Saigal)
- **Category D (D15–D18):** Quant Momentum & Screening Strategies (Mr. Rohan Mehta)

---

## Pre-Flight Requirements

Before executing any of the 18 strategies, verify the mandatory input data requirements below. Declare any missing inputs explicitly as gaps in the output decision card.

```
Common Pre-Flight Inputs:
□ Target company name, ticker symbol, and asset class (Equity, Futures, Options)
□ Current Market Price (CMP) and as-of date/timestamp
□ Ethical screening status (Saatvik filter verification — Strategy D18)

Derivatives Pre-Flight Inputs (Category A: A1–A4):
□ Opening spot price at 09:16 AM (for zero-DTE range selling)
□ Weekly / Monthly option chain with IV, Delta, Theta, and strike price grid
□ Intraday timestamp (09:15 AM panic window, 09:20 AM straddle entry)
□ SuperTrend (10,3) status on Index Futures (for trend-following delta strategy)
□ India VIX current level (regime check)

Technical Growth Pre-Flight Inputs (Category B: B5–B8):
□ Daily & Weekly price chart history (minimum 1–2 years)
□ 50-day, 150-day, and 200-day Simple Moving Averages (SMAs)
□ 30-week (150-day) Moving Average slope for Stage Analysis
□ 52-week High and 52-week Low prices
□ Daily volume bars and 50-day average volume line
□ Relative Strength (RS) rating / line vs Nifty 50 or Nifty 500
□ TTM EPS growth rate (for SEPA catalyst verification)

Fundamental Value Pre-Flight Inputs (Category C: C9–C14):
□ Trailing Twelve Month (TTM) PAT, Revenue, and Free Cash Flow (FCF)
□ Reverse DCF model assumptions (WACC, implied growth rate, terminal growth rate)
□ Sell-side consensus revenue/PAT expectations vs Variant Perception thesis
□ Historical Price-to-Book (P/B) 5–10 year range (for cyclical bottom buying)
□ Return on Capital Employed (ROIC) trend (for capital-light fast growers)
□ Average Revenue Per User (ARPU) & Return on Equity (ROE) trend (for misunderstood stalwarts)
□ NCLT resolution status, debt write-off details, and acquiring promoter track record (for turnarounds)

Quant Momentum Pre-Flight Inputs (Category D: D15–D18):
□ All-Time High (ATH) price confirmation and ATH breakout volume
□ Trailing Twelve Month (TTM) PAT ATH confirmation
□ 52-week rolling Relative Strength score vs Nifty 500 and Sector Index
□ Total Portfolio Capital amount and Max Risk % tolerance per trade (default 1.2%)
□ Target Entry Price and 200-day EMA Exit Price (for position sizing calculation)
□ Segment-wise revenue breakdown (for 6 Sin Business Categories audit)
```

---

## Analysis Modules — The 18 Expert Strategy Diagnostics

### Module A1 — Option Arbitrage & Spreads Strategy
- **Expert:** Mr. Ankit Rai | **Domain:** Domain 45
- **Activation Trigger:** Request for non-directional options trading, arbitrage spreads, or morning panic window execution.
- **Minimum Data Required:** Option chain IV skew, bid-ask depth, 09:15:00–09:15:30 AM open timestamp.
- **Gate Check:** Is captured yield spread ≥ 12%–14% annualized after accounting for execution slippage?
- **Invalidation Rule:** Cancel order if slippage erodes margin below 12% annualized or leg execution fails.

### Module A2 — Range-Bound Probability Option Selling
- **Expert:** Mr. Ankit Rai | **Domain:** Domain 45
- **Activation Trigger:** Request for zero-DTE weekly option selling on Nifty 50 or Bank Nifty.
- **Minimum Data Required:** 09:16 AM opening spot price, zero-DTE option chain, India VIX level.
- **Gate Check:** Are sold Call and Put strikes placed 250+ points away from 09:16 AM spot price against the ~187 pt historical average range?
- **Invalidation Rule:** Exit position immediately if spot moves >200 pts toward sold strike or India VIX > 25.

### Module A3 — Time-Based Straddle Selling
- **Expert:** Mr. Ankit Rai | **Domain:** Domain 45
- **Activation Trigger:** Request for mechanical intraday theta decay straddle execution.
- **Minimum Data Required:** Precise entry timestamp (09:20 AM, 09:25 AM, or 09:30 AM), ATM Call & Put premiums.
- **Gate Check:** Is combined ATM straddle premium backed by a strict directional stop-loss or delta hedge?
- **Invalidation Rule:** Exit immediately if combined premium expands by >30% due to trend gap move.

### Module A4 — Trend-Following with Futures / Synthetic Futures
- **Expert:** Mr. Ankit Rai | **Domain:** Domain 45
- **Activation Trigger:** Request for high-delta trend breakout capturing 300–500+ point index moves.
- **Minimum Data Required:** SuperTrend (10,3) signal status on Index Futures, high-delta instrument data.
- **Gate Check:** Has SuperTrend (10,3) generated a confirmed Buy (Green) or Sell (Red) breakout signal?
- **Invalidation Rule:** Close position immediately when SuperTrend reverses signal color.

---

### Module B5 — Volatility Contraction Pattern (VCP) Strategy
- **Expert:** Mr. Aniketh Dsouza | **Domain:** Domain 46
- **Activation Trigger:** Request for VCP chart pattern recognition or tight consolidation breakout.
- **Minimum Data Required:** Daily chart showing 2–4 successive contractions (e.g. 10% → 5% → 2%), volume bars.
- **Gate Check:** Does pullback depth contract sequentially AND does right-side volume dry up well below 50-day average?
- **Invalidation Rule:** Reject setup if contractions expand or breakout occurs on weak volume.

### Module B6 — Mark Minervini’s 8-Step Trend Template
- **Expert:** Mr. Aniketh Dsouza | **Domain:** Domain 46
- **Activation Trigger:** Request for Stage 2 trend qualification or Minervini 8-point checklist audit.
- **Minimum Data Required:** 50, 150, 200 SMAs, 52-week High/Low, 200 SMA slope, RS rating > 80.
- **Gate Check:** Does stock pass ALL 8 mandatory Trend Template rules without exception?
- **Invalidation Rule:** Failing even 1 of the 8 rules results in an immediate FAIL verdict.

### Module B7 — Stan Weinstein’s Stage Analysis
- **Expert:** Mr. Aniketh Dsouza | **Domain:** Domain 46
- **Activation Trigger:** Request to classify stock structural lifecycle stage (Stage 1, 2, 3, or 4).
- **Minimum Data Required:** Weekly price chart, 30-week (150-day) moving average slope, weekly volume bars.
- **Gate Check:** Is stock transitioning from Stage 1 base to Stage 2 advancing above rising 30-week MA on heavy volume?
- **Invalidation Rule:** Never buy in Stage 3 (distribution) or Stage 4 (downtrend below falling 30-week MA).

### Module B8 — Specific Entry Point Analysis (SEPA) Strategy
- **Expert:** Mr. Aniketh Dsouza | **Domain:** Domain 46
- **Activation Trigger:** Request for combined technical VCP setup + fundamental earnings catalyst entry.
- **Minimum Data Required:** VCP base chart, TTM EPS growth rate (>25%–50%), identified pivot price, 3%–7% stop loss.
- **Gate Check:** Are technical base, fundamental EPS acceleration, and low-risk pivot point simultaneously aligned?
- **Invalidation Rule:** Exit immediately if price drops >7% below pivot entry.

---

### Module C9 — Reverse DCF "Proof by Contradiction" Strategy
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for reverse valuation, implied growth extraction, or market contradiction analysis.
- **Minimum Data Required:** Stock price, Market Cap, TTM FCF, WACC discount rate.
- **Gate Check:** Is the market-implied growth/terminal rate (e.g. 0% terminal growth in Century Ply model) logically absurd for an established industry leader?
- **Invalidation Rule:** Discard thesis if market implied growth rate is realistic or justified by structural decline.

### Module C10 — Variant Perception & Trigger Investing
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for non-consensus investment thesis or catalyst-driven stock evaluation.
- **Minimum Data Required:** 4-Point Card inputs (Idea, Consensus View, Variant Perception, Specific Trigger Event).
- **Gate Check:** Is there a clear, dated catalyst event within 3–12 months that will force market consensus to re-rate?
- **Invalidation Rule:** Discard thesis if variant perception lacks a concrete catalyst event.

### Module C11 — Cyclical Bottom-Buying Strategy
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for deep-value cyclical stock evaluation (metals, optical fiber, chemicals).
- **Minimum Data Required:** 5–10 year historical P/B range, industry capacity utilization trend, Debt/EBITDA solvency.
- **Gate Check:** Is Price-to-Book (P/B) at a historic trough while industry overcapacity shows initial demand recovery? (Ignore P/E).
- **Invalidation Rule:** Reject if buying based on low P/E at peak earnings (value trap) or if debt balance threatens solvency.

### Module C12 — Capital-Light "Fast Growers" Strategy
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for high-ROIC asset-light compounder evaluation.
- **Minimum Data Required:** Multi-year ROIC (>30%+ requirement), Capex / OCF ratio (<15%–20%), IP/licensing asset proof.
- **Gate Check:** Does revenue scale with minimal incremental capex due to unique IP, content library, or platform rights? (Tips Industries model).
- **Invalidation Rule:** Reject if ROIC drops below 20% or management re-invests cash into capex-heavy side businesses.

### Module C13 — Misunderstood Stalwarts with Expanding ROE
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for depressed large-cap industry leader evaluation.
- **Minimum Data Required:** ARPU / unit economics history, multi-year ROE trend, pricing power catalyst.
- **Gate Check:** Is current weak ROE at a floor due to temporary headwinds with a clear catalyst for expansion back toward historical norms? (Bharti Airtel model).
- **Invalidation Rule:** Reject if price war deepens permanently or market share is lost to low-cost entrants.

### Module C14 — Corporate Turnaround (NCLT) Strategy
- **Expert:** Mr. Anshul Saigal | **Domain:** Domain 47
- **Activation Trigger:** Request for distressed, bankrupt, or NCLT turnaround evaluation.
- **Minimum Data Required:** NCLT resolution approval, acquiring promoter track record, debt write-down balance sheet.
- **Gate Check:** Is the distressed entity acquired out of insolvency by a Tier-1 promoter group with capital injection and operational restructuring? (CG Power model).
- **Invalidation Rule:** Reject if acquired by weak promoter group or if positive OCF fails to materialize within 4 quarters.

---

### Module D15 — Quant Momentum (All-Time High Strategy)
- **Expert:** Mr. Rohan Mehta | **Domain:** Domain 48
- **Activation Trigger:** Request for All-Time High price breakout momentum evaluation.
- **Minimum Data Required:** Historical ATH price check, breakout volume (>1.5x avg), 50/200 EMA alignment.
- **Gate Check:** Has stock price closed above its historical All-Time High, eliminating overhead supply?
- **Invalidation Rule:** Exit if price closes back below ATH line or overall market index drawdowns >10%.

### Module D16 — Triple-Filter Quant Momentum Strategy
- **Expert:** Mr. Rohan Mehta | **Domain:** Domain 48
- **Activation Trigger:** Request for multi-factor quant momentum screening.
- **Minimum Data Required:** ATH Price status, TTM PAT ATH status, 52-week RS score vs Nifty 500 & Sector Index.
- **Gate Check:** Does stock pass ALL 3 filters: Price at ATH AND TTM PAT at ATH AND RS outperforming Nifty 500 & Sector Index?
- **Invalidation Rule:** Reject if price is at ATH but TTM PAT is declining (speculative bubble).

### Module D17 — Risk-Based Position Sizing Strategy
- **Expert:** Mr. Rohan Mehta | **Domain:** Domain 48
- **Activation Trigger:** Request for mathematical portfolio allocation or stop-loss distance sizing.
- **Minimum Data Required:** Total Portfolio Capital, Max Risk % (default 1.2%), Entry Price, 200-day EMA Exit Price.
- **Gate Check:** Calculate exact position allocation % using formula:
  $$\text{Allocation \%} = \frac{\text{Max Risk \% (1.2\%)}}{\text{Distance \% to 200 EMA Exit}}$$
- **Invalidation Rule:** Never exceed calculated allocation % regardless of subjective conviction.

### Module D18 — "Saatvik" (Ethical/Sin-Free) Quant Filter
- **Expert:** Mr. Rohan Mehta | **Domain:** Domain 48
- **Activation Trigger:** Mandatory pre-screening filter for all equity research requests.
- **Minimum Data Required:** Segment-wise revenue breakdown from Annual Report.
- **Gate Check:** Does company derive 0% revenue from the 6 Sin Categories (Meat, Alcohol, Tobacco, Leather, Gambling, Sin Hospitality)?
- **Invalidation Rule:** Deriving any revenue from sin categories results in an immediate FAIL and complete purge from investment universe.

---

## Strategy Confidence & Diagnostic Matrix


> **Evidence Note:** Win rates in this matrix are sourced from domain expert descriptions in Domains 45–48 and are classified as **Assumptions** per the IERL Evidence Protocol (not independently backtested). Use as relative confidence guides, not statistical guarantees. Strategy A1 (Option Arbitrage) win rate references a pre-HFT market regime; current operational yield is 12%–14% annualized.

| Strategy | Primary Category | Historical / Empirical Win Rate | Max Confidence | Key Auto-Fail Condition |

|---|---|---|---|---|
| A1: Option Arbitrage | Options / Systematic | >90% | Medium (Latency dependent) | Slippage erodes spread < 12% annualized |
| A2: Range Option Selling | Options / Systematic | 87% – 90% | High | Spot moves >200 pts or India VIX > 25 |
| A3: Time Straddle Selling | Options / Systematic | 65% – 75% | Moderate | Combined premium expands >30% |
| A4: Trend Futures | Options / Systematic | 40% – 50% | High (Big winners) | SuperTrend color reverses |
| B5: VCP Pattern | Technical Growth | 65% – 70% | High | Contractions expand; weak volume breakout |
| B6: Minervini 8-Step | Technical Growth | 70% – 75% | Very High | Fails even 1 of the 8 mandatory rules |
| B7: Weinstein Stage | Technical Growth | 65% – 70% | High | Buying in Stage 3 or Stage 4 |
| B8: SEPA Strategy | Technical Growth | 75% – 80% | Very High | Price drops >7% below pivot entry |
| C9: Reverse DCF | Fundamental Value | 70% – 75% | High | Implied market growth rate is reasonable |
| C10: Variant Perception | Fundamental Value | 65% – 70% | High | Lack of a concrete catalyst event |
| C11: Cyclical Bottom | Fundamental Value | 70% – 80% | High | Buying low P/E at peak earnings |
| C12: Capital-Light Fast | Fundamental Value | 80% – 85% | Very High | ROIC drops <20%; heavy capex shift |
| C13: Misunderstood Stalwart | Fundamental Value | 75% – 80% | High | Price war becomes permanent |
| C14: Turnaround NCLT | Fundamental Value | 60% – 70% | Moderate (High Risk) | Acquisition by weak promoter group |
| D15: Quant Momentum ATH | Quant Momentum | 66% | High | False breakout closes below ATH |
| D16: Triple-Filter Quant | Quant Momentum | 82% | Very High | Price at ATH but TTM PAT declining |
| D17: Position Sizing | Quant Momentum | N/A (Risk Rule) | Very High | Allocation exceeds calculated formula limit |
| D18: Saatvik Filter | Ethical Screening | N/A (Gate) | Absolute | Revenue present in any of 6 Sin Categories |

---

## Mandatory Execution Decision Card Output Template

When executing any of the 18 Expert Strategies, generate output strictly using this format:

```
═══════════════════════════════════════════════════════════════════════
EXPERT STRATEGY EXECUTION DECISION CARD
Strategy: [Strategy Number & Name] | Expert Origin: [Expert Name]
Category: [Category A / B / C / D] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════════

SETUP STATUS:        [PASS / FAIL / PENDING — MISSING DATA]
TARGET INSTRUMENT:   [Company / Index / Ticker]
CURRENT PRICE (CMP): [Price / Spot Level] | As-of: [Timestamp]

1. ETHICAL PRE-SCREEN (Saatvik Filter — Strategy D18):
   Status:           [PASS / FAIL]
   Sin Revenue:      [0% / Details if failed]

2. INPUT DATA AUDIT:
   Provided Inputs:  [List all inputs supplied by user]
   Missing Inputs:   [List missing required inputs, or "None"]

3. DIAGNOSTIC GATE RESULTS:
   Gate 1 [Name]:    [PASS / FAIL — Detailed quantitative result]
   Gate 2 [Name]:    [PASS / FAIL — Detailed quantitative result]
   Gate 3 [Name]:    [PASS / FAIL — Detailed quantitative result]
   Overall Diagnostic: [ALL GATES PASSED / CRITICAL GATE FAILED]

4. MATHEMATICAL & SCREENING EVIDENCE:
   Formula Used:     [State relevant formula: DCF / Sizing / Trend / Range]
   Calculation:      [Show explicit calculation with numbers]
   Result:           [Quantified output value]

5. REFERENCE CASE STUDY ALIGNMENT:
   Historical Analog:[Century Ply / Sterlite / Tips / Bharti / CG Power / Nifty 0-DTE]
   Alignment Note:   [How target instrument matches or differs from reference case]

6. COUNTER-CASE & INVALIDATION THRESHOLDS:
   Counter-Case:     [What conditions would cause this thesis to fail]
   Hard Exit Trigger:[Exact stop loss price, VIX level, or rule break]

7. POSITION SIZING & RISK ALLOCATION (Strategy D17):
   200 EMA Exit Price: ₹[Price] (Distance: [X]%)
   Portfolio Capital:  ₹[Amount] | Max Risk Cap: [1.2]%
   Calculated Size:    [X]% of Portfolio (₹[Amount] / [N] shares)

8. FINAL DECISION & CONFIDENCE:
   Verdict:          [EXECUTE SETUP / REJECT SETUP / PEND FOR DATA]
   Confidence Level: [Very High / High / Moderate / Low]
   Confidence Basis: [1-sentence explanation of evidence strength]
═══════════════════════════════════════════════════════════════════════
```

---

## Non-Negotiable Rules

1. **Ethical Priority:** Strategy D18 (Saatvik Filter) is a mandatory pre-screen for all equity setups. If a company fails D18, reject immediately without evaluating technical or fundamental merit.
2. **Hard Gate Integrity:** For multi-rule strategies (e.g. B6 Minervini 8-Step, D16 Triple-Filter), failing even a single gate results in an overall FAIL verdict.
3. **No Narrative Substitution:** In Category C (Value/Structural) strategies, narrative optimism can never substitute for evidence of ROIC, FCF, or Reverse DCF contradiction.
4. **Position Sizing Floor:** Position size per Strategy D17 is a mathematical ceiling. Never override allocation upward based on subjective conviction.
5. **Missing Data Protocol:** If a mandatory input is missing, flag status as "PENDING — MISSING DATA" and state the exact required inputs. Never fabricate or assume missing prices or financial figures.
6. **Stop Loss Discipline:** Exit triggers defined in failure modes (e.g. 7% SEPA pivot break, 200 EMA cross, VIX > 25) are hard stops, not soft monitoring guidelines.

---
End of Document — AI 18 Expert Strategies Execution Skill
<!-- END SYSTEM FILE 1: AI_18_Expert_Strategies_Execution_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 2: AI_Comparison_Engine_Skill.md | SHA256: 347a6c211877aa7c9c2b90c5ce80652ada167ca53d8446bb60c0767a89d000fb -->
## Embedded source 2: AI Comparison Engine Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Comparison Engine Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Comparison Engine Skill v1.0

**Status:** Production Ready
**Category:** New Skill (genuinely missing capability, confirmed by institutional audit — Comparison Engine scored 52/100 with "no dedicated workflow")
**Goal:** Comparison Engine 52 → 90
**Action:** Upload as new standalone skill file — reuses all existing data/objects, adds zero new schema

---

## Why This File Exists

The audit confirmed: comparison capability existed only as unstructured general reasoning — no defined workflow, despite all the underlying data (ratios, valuation, quality scores) already being available via `Screener_Field_Glossary`, `Domain_04_Financial_Ratios`, and the Forensic/Risk skills. This file is a **workflow wrapper**, not a new data source.

---

## Trigger Keywords

"compare," "vs," "versus," "which is better," "how does X stack up against Y," "relative valuation," "peer comparison"

---

## Comparison Types Supported

### 1. Company vs Company

```
Step 1 — Pull core fundamentals for both (via Screener Field Glossary fields)
Step 2 — Run Forensic Accounting red-flag check on both independently
         (a company that "wins" on growth but fails red-flag checks is
         not a fair winner — apply CIO Authority Rule: forensic flag
         caps conviction regardless of comparative growth)
Step 3 — Compare across 5 fixed dimensions:
         Growth | Profitability (ROCE/ROE) | Balance Sheet Strength |
         Valuation | Capital Allocation Quality
Step 4 — State which company wins each dimension explicitly — do not
         average into one score without showing the breakdown
Step 5 — Decision Summary: overall lean, with the single most decisive
         differentiating factor named explicitly
```

### 2. Company vs Sector

```
Step 1 — Pull sector averages/benchmarks from the relevant Sector
         Quick-Reference row or dedicated sector skill (Banking, NBFC, etc.)
Step 2 — Compare company's Key Metrics (per that sector's specific
         metric list — e.g., NIM for Banking, not generic ROE) against
         sector norms
Step 3 — Classify: Sector Leader / In-Line / Laggard, with the metric
         gap stated numerically
```

### 3. Company vs Index

```
Step 1 — Compare Returns (per Screener Glossary period fields: 1Y/3Y/5Y)
         against the relevant index return for the same period
Step 2 — State whether outperformance is Alpha (business-driven, check
         if fundamentals improved commensurately) or Beta-driven
         (broad market/sector rally lifted the stock without matching
         fundamental improvement — check via Domain 44 macro cross-reference)
```

### 4. Growth vs Value Classification

```
A stock is classified Growth if: Sales Growth 3Y >15% AND PE > Industry PE
A stock is classified Value if: PE < Industry PE x 0.8 AND ROCE > 12%
A stock is classified Blend if it fits neither cleanly — state why

This reuses Library 9 (Valuation) thresholds already established in the
Multibagger Quick Screen — no new thresholds invented.
```

### 5. Quality / Risk / Valuation / Capital Allocation / Competitive Advantage Comparison

```
For any two companies, generate a single comparison table:

| Dimension | Company A | Company B | Winner |
|---|---|---|---|
| Business Quality (Domain 6) | | | |
| Governance (Domain 8) | | | |
| Forensic Risk (Forensic Accounting Skill) | | | |
| Valuation (PE/PB/EV-EBITDA vs sector) | | | |
| Capital Allocation (ROCE trend, per Multibagger Module 0B Category 4) | | | |
| Competitive Moat (Domain 25 - Moat & Competitive Advantage) | | | |

Never declare an overall winner without showing this breakdown table —
a single blended score hides which dimension actually decided it.
```

---

## Decision Summary Standard (Required for Every Comparison)

Every comparison output must end with:
```
Bottom Line: [1-2 sentences, plain language]
Decisive Factor: [the single dimension that most drove the conclusion]
Where They're Close: [any dimension that was near-tied, stated honestly]
Confidence: [per Confidence Standard vocabulary — comparisons with
             incomplete data on one side should show reduced confidence,
             not be silently treated as fully resolved]
```

---

## Self-Audit

- ✓ No new data objects introduced — uses existing `ResearchObject`, `DecisionObject` fields
- ✓ No new numeric thresholds invented — reuses Multibagger Quick Screen, Valuation Library 9, and sector-specific metrics already defined
- ✓ Forensic/CIO Authority Rules explicitly carried into comparison logic — a company cannot "win" a comparison by outscoring on growth while failing a forensic gate

---

## Pre-Flight Requirements

Before running any comparison, the user must supply the following minimum data. Derived from the 5 comparison types and 6 dimensions defined above.

```
□ Company A name, ticker, and as-of date for all financial data
□ Company B name, ticker, and as-of date for all financial data
  (or sector benchmark / index name for Company vs Sector / Company vs Index comparisons)

DIMENSION DATA REQUIRED:
□ Growth: Revenue CAGR (3 years) and PAT CAGR (3 years) for both entities
□ Profitability: ROCE % and ROE % (most recent full year) for both entities
□ Balance Sheet: Debt/EBITDA and Current Ratio for both entities
□ Valuation: P/E, P/B, EV/EBITDA — current vs sector average — for both entities
□ Capital Allocation: ROCE trend (3 years) for both entities
□ Moat: Domain 25 moat type classification + trajectory (Widening / Holding / Eroding)

FORENSIC PRE-SCREEN (Domain 24):
□ CFO/PAT ratio for both entities (3-year trend)
□ Promoter pledge % for both entities
□ Any active auditor change or related-party flag for both entities

MISSING DATA RULE: If financial data is available for Company A but not Company B
(or vice versa), declare the data gap explicitly in the output. Do NOT fill missing
data with estimates, assumptions, or industry averages without labeling them as such.
Confidence must be reduced when a comparison is asymmetric in data quality.
```

---

## Standardized Comparison Output Template

Every comparison output must use this format exactly. Do not produce free-form narrative comparisons without completing this template first.

```
═══════════════════════════════════════════════════════════════════════
COMPARISON REPORT
Company A: [Name / Ticker] | Company B: [Name / Ticker]
Comparison Type: [Company vs Company | Company vs Sector | Company vs Index | Growth-Value]
As-of Date: [DD/MM/YYYY] | Data Vintage: [State period for each entity's data]
═══════════════════════════════════════════════════════════════════════

FORENSIC PRE-SCREEN (per Domain 24 — Hard Gate):
  Company A: [PASS / CAUTION / FAIL + reason if not PASS]
  Company B: [PASS / CAUTION / FAIL + reason if not PASS]
  ⚠️ Gate Rule: A company with a FAIL verdict cannot be declared a winner
     regardless of scorecard performance in any other dimension.

DIMENSION SCORECARD:
| Dimension | Company A | Company B | Winner |
|---|---|---|---|
| Growth (Revenue CAGR 3yr / PAT CAGR 3yr) | | | |
| Profitability (ROCE % / ROE %) | | | |
| Balance Sheet (Debt/EBITDA / Current Ratio) | | | |
| Valuation (PE / PB / EV-EBITDA vs sector avg) | | | |
| Capital Allocation (ROCE trend 3yr) | | | |
| Moat (Domain 25 — type + trajectory) | | | |

SCORECARD TALLY:
  Company A wins: [X of 6 dimensions]
  Company B wins: [Y of 6 dimensions]
  Near-tied: [list any dimensions where gap < 10%]

BOTTOM LINE: [1–2 sentences, plain language verdict]
DECISIVE FACTOR: [The single dimension that most drove the conclusion — named explicitly]
WHERE THEY ARE CLOSE: [Any near-tied dimension, stated honestly]
DATA GAPS: [List any missing data that limited comparison quality, or "None"]
CONFIDENCE: [High / Moderate / Low]
  Basis: [1 sentence explaining what limits or supports confidence]
═══════════════════════════════════════════════════════════════════════
```

---

## Non-Negotiable Rules for Comparison

**Rule 1 — Forensic gate failure caps the winner verdict:**
A company that fails the Domain 24 Forensic Pre-Screen (2+ flags from different categories) cannot be declared a winner in this comparison, regardless of how strongly it leads in growth, valuation, or any other dimension. This is the CIO Authority Rule already embedded in the existing Company vs Company workflow above: "a company that 'wins' on growth but fails red-flag checks is not a fair winner."

**Rule 2 — Never declare a winner without showing the dimension scorecard:**
A bottom-line verdict delivered without completing the 6-dimension scorecard is not a valid comparison output. The scorecard breakdown is mandatory — it shows which dimensions drove the conclusion and prevents a single compelling metric (e.g., very high revenue growth) from masking weakness in governance or valuation.

**Rule 3 — Confidence must reflect data asymmetry:**
If meaningful financial data is available for Company A but missing for Company B (or vice versa), the comparison confidence must be stated as Low or "Data Incomplete" — not Moderate or High. A one-sided data comparison cannot support a high-confidence verdict, regardless of how decisive the available data appears.

**Rule 4 — Use sector-specific metrics, not generic defaults:**
As stated in the Company vs Sector comparison workflow above, sector-specific key metrics must be used where applicable. For Banking: NIM, GNPA, Cost-to-Income, CASA ratio. For Insurance: Embedded Value, VNB margin. Applying generic P/E or ROCE comparisons to a bank without adjusting for sector-specific metrics produces a misleading comparison.

**Rule 5 — State the decisive factor — do not blend into a single score:**
The Comparison Report requires an explicit "Decisive Factor" field. Do not replace this with a weighted average score or a single blended number. Averaging conceals the dimension-by-dimension trade-off that is the entire value of a structured comparison. The decisive factor must be a named, specific dimension (e.g., "Capital Allocation — Company A's ROCE has improved from 14% to 22% over 3 years while Company B's has declined from 18% to 11%").

---

**Document:** AI_Comparison_Engine_Skill.md  
**Version:** 1.1 (expanded with Pre-Flight, Output Template, Non-Negotiable Rules)
<!-- END SYSTEM FILE 2: AI_Comparison_Engine_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 3: AI_Concentrated_SmallCap_Style_Thinking_Skill.md | SHA256: 1bf7e975808e08991688f65a4b64d0572eecc5b4abd6503231981ffe0c607e22 -->
## Embedded source 3: AI Concentrated SmallCap Style Thinking Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Concentrated SmallCap Style Thinking Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Concentrated Small-Cap Style Thinking Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Heuristic Lens — Concentrated, Under-the-Radar Small-Cap Investing Pattern

---

## CRITICAL AI INSTRUCTION

This skill is a **heuristic lens**, not a personality simulation and not investment advice attributed to any named individual. It is built from publicly reported, widely discussed patterns associated with a concentrated, deeply-researched, under-the-radar small-cap investing style — the kind of approach characterized by small portfolios (often single-digit number of holdings), multi-year holding periods, extensive on-the-ground and unconventional due diligence, and a willingness to be early and look wrong for extended periods before being proven right. Claude must apply this as a **way of asking questions and weighting evidence**, never as a claim that any real person endorses a specific stock or would make a specific decision. Do not attribute quotes, specific past picks, or personal opinions to any individual. This lens supplements — it never replaces — the mandatory gates in Forensic Accounting, Governance, and the Pre-Investment Master Checklist.

---

## Purpose

Apply a concentrated, deep-diligence, contrarian-leaning analytical lens to small-cap candidates — emphasizing extreme business-model understanding, unconventional evidence-gathering, comfort with being early against consensus, and extreme selectivity (favoring very few, very high-conviction positions over broad diversification) — as a complement to, not a replacement for, the standard IERL research process.

---

## Pre-Flight Requirements

```
□ Confirm the user wants this specific heuristic lens applied (this is a
  style choice, not a default) — if invoked generically ("analyze this
  small cap"), default to Skill 01/04 instead and only apply this lens
  if the user signals interest in a concentrated, contrarian approach
□ Company must already have passed, or be run alongside, the standard
  Governance Gate and Forensic Gate from Skill 01 — this lens sharpens
  conviction, it does not substitute for the baseline safety checks
□ Access to primary sources beyond standard financial disclosures where
  possible: dealer/distributor channel checks, customer reviews, import-
  export data, job postings (hiring signal), local news, patent filings
□ User's willingness to hold a concentrated position (this lens is
  only coherent alongside high position sizing — presenting it alongside
  a 1-2% diversified position undersells the approach's own logic)
```

---

## Analysis Module 1 — The Concentration Mindset

```
Core premise of this lens: if you have done truly deep, unconventional
diligence on a business and have very high conviction, diversifying away
from that conviction into 20-30 mediocre-conviction ideas dilutes your
best insight rather than protecting you. This is the opposite instinct
from standard portfolio theory diversification, and it requires a much
higher diligence bar to be responsible.

Implication for Claude's output when this lens is invoked:
□ Push for FEWER, deeper ideas rather than a list of 5-10 plausible names
□ For each idea presented, go materially deeper than a standard Skill 01
  report on the SPECIFIC things that would make or break the thesis —
  not a comprehensive checklist, but an intense focus on the 2-3 variables
  that actually matter most for this specific business
□ Explicitly note where conviction is NOT yet high enough to warrant
  concentration — "interesting but not yet a concentrated-position-grade
  idea, here is specifically what more diligence would need to show"
```

---

## Analysis Module 2 — Under-the-Radar Screening Criteria

```
□ Limited or no institutional/analyst coverage (fewer eyes on the name =
  higher chance of a genuine information or insight edge, but also higher
  execution/liquidity risk — both must be stated)
□ Business model that is not easily understood from a 5-minute read of
  the annual report — genuine complexity or obscurity that would deter
  a casual screener, but which becomes an edge once properly understood
□ Situated in a niche, unglamorous, or currently out-of-favor category —
  actively look at where sentiment or narrative attention is LOW, not high
  (the opposite screening direction from momentum-based approaches)
□ Owner-operator or promoter-driven management with a long personal
  history in the specific business, ideally with a track record the
  market has not yet fully re-rated for
```

---

## Analysis Module 3 — Unconventional Diligence Prompts

```
Beyond standard financial statement analysis, this lens explicitly prompts
for evidence types that a purely desk-based screen would miss. Claude
should proactively ask the user whether any of the following are available,
and incorporate them if so — while being explicit when they are NOT
available (never fabricate this kind of ground-level evidence):

□ Channel checks: dealer/distributor sentiment, reorder patterns,
  inventory levels reported informally in trade channels
□ Customer-side evidence: reviews, satisfaction signals, switching
  behavior for the company's specific product/service
□ Competitive intelligence: what are direct competitors NOT able to
  replicate about this company's specific advantage, and why
□ Regulatory/industry-body filings beyond the standard annual report
  (e.g., import-export data, sector association disclosures)
□ Hiring patterns / job postings (a leading indicator of where the
  company is actually investing, sometimes ahead of what commentary suggests)
□ On-the-ground factory/plant/store visit reports, if available
  (explicitly note this is rarely available to a remote research process
  and treat its absence as a stated diligence gap, not silently ignored)

If none of this ground-level evidence is available, state explicitly:
"This analysis is limited to desk-based financial and disclosure review;
the unconventional diligence this lens typically emphasizes was not
available — treat conviction accordingly as more moderate than the
lens would ideally support."
```

---

## Analysis Module 4 — Contrarian Comfort and Patience Framework

```
□ Explicitly separate "the market disagrees with this thesis right now"
  from "the market has good reason to disagree" — the lens requires being
  able to articulate WHY the market's current view is wrong or incomplete,
  not just noting that the stock is unpopular
□ State the expected time horizon for the thesis to be recognized —
  concentrated contrarian positions typically require patience measured
  in years, not quarters; if the thesis logically requires a near-term
  catalyst, this may be a better fit for Skill 03 (Positional) than this lens
□ Pre-define, explicitly and in writing as part of the output, what
  would prove the thesis WRONG — this lens's biggest risk is conviction
  hardening into stubbornness; an explicit invalidation condition set in
  advance is the discipline that prevents that
□ Distinguish "the stock price is down and I am adding" (average-down
  because thesis intact, with fresh evidence reviewed) from "the stock
  price is down and I am doubling down because I don't want to be wrong"
  (an emotional/ego-driven add) — Claude must ask what fresh evidence,
  if any, justifies conviction being maintained or increased after a decline
```

---

## Analysis Module 5 — Profit-Taking Discipline and Key-Man Risk (Upgrade — Previously Missing)

```
This lens previously covered entry and patience but not exit — a
concentration approach without a trim discipline can turn a winning
thesis into an outsized, unmanaged risk.

□ Define, in advance, what "the thesis has been recognized by the market"
  looks like (specific valuation/re-rating level) — at that point, trim
  toward standard portfolio ceilings (per AI_Portfolio_Construction_Skill)
  even if long-term conviction in the business remains high; concentration
  is a tool for capturing an insight the market hasn't priced yet, not a
  permanent state once that gap has closed
□ Key-Man Risk Test: since this lens favors owner-operator businesses,
  explicitly assess and state what happens to the thesis if the specific
  individual driving it is unexpectedly unavailable (health, succession,
  departure) — a concentrated position resting heavily on one person's
  judgment carries materially higher single-point-of-failure risk than a
  diversified holding in the same sector, and this must be disclosed
  alongside the conviction rating, not left implicit
```

## Red Flag Summary — Concentrated Style Context

### CRITICAL Flags
```
❗ Concentration recommended without the company having passed the
  standard Governance and Forensic Gates from Skill 01
❗ "Contrarian" framing applied to a stock where the market's negative
  view is actually well-supported by deteriorating fundamentals (i.e.,
  this is a value trap being mistaken for a contrarian opportunity —
  cross-check explicitly against AI_Turnaround_Analysis_Skill's Signal
  vs Trap checklist before proceeding)
❗ No stated invalidation condition for the thesis
```

### HIGH Flags
```
⚠️ Limited institutional coverage cited as a positive (edge) without also
  flagging the corresponding liquidity risk that comes with it
⚠️ Ground-level/unconventional diligence claimed as a basis for conviction
  but not actually available or provided
⚠️ Position sizing implied or recommended significantly above what the
  user's stated risk tolerance or portfolio structure (per AI_Portfolio_
  Construction_Skill) would otherwise support
```

---

## Output Format

```
CONCENTRATED SMALL-CAP LENS ANALYSIS
Company: [Name] | Ticker: [NSE] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

BASELINE GATE CHECK:
  Governance Gate (Skill 01):  [Pass/Fail/Not yet run]
  Forensic Gate (Skill 01):    [Pass/Fail/Not yet run]
  → If either not passed, this lens cannot proceed to a conviction rating.

UNDER-THE-RADAR PROFILE:
  Institutional Coverage:      [Minimal/Moderate/High] — liquidity implication: [X]
  Complexity/Obscurity Factor: [What specifically makes this hard to screen
                                 casually, and why that is an edge once understood]
  Sentiment Context:           [Out-of-favor/Neutral/In-favor — lens favors
                                 out-of-favor]

THE 2–3 VARIABLES THAT ACTUALLY MATTER:
  1. [Specific variable] — [Why this, above all else, determines the outcome]
  2. [Specific variable] — [Same]
  3. [Specific variable, if applicable] — [Same]

UNCONVENTIONAL DILIGENCE AVAILABLE:
  [List what ground-level evidence was actually available and incorporated,
  or state explicitly: "Desk-based review only — ground-level diligence
  this lens typically emphasizes was not available"]

CONTRARIAN THESIS ARTICULATION:
  Why the Market Disagrees:   [Current consensus view]
  Why That View Is Incomplete/Wrong: [Specific reasoning, not just disagreement]
  Expected Recognition Horizon: [Years, stated explicitly]
  Value-Trap Cross-Check:      [Confirmed this is NOT a deteriorating business
                                 mistaken for contrarian opportunity — reference
                                 to Turnaround Skill's Signal vs Trap check if relevant]

INVALIDATION CONDITION (Written in Advance):
  [Explicit, specific condition that would prove this thesis wrong]

CONCENTRATION SUITABILITY:
  Conviction Level:            [High enough for concentration / Not yet —
                                 here is what more diligence would need to show]
  Position Sizing Note:        [Cross-check against AI_Portfolio_Construction_
                                 Skill Tier ceilings — even high conviction should
                                 not exceed portfolio-level hard caps]

⚠️ REMINDER: This is a heuristic lens for how to think about the idea, not
investment advice attributed to any individual, and does not override the
mandatory Governance/Forensic gates or portfolio-level position ceilings.
```

---

## Rules (Non-Negotiable)

```
1. This lens never substitutes for the Governance Gate or Forensic Gate —
   it sharpens conviction after those gates are passed, never before.
2. No specific past trades, quotes, or opinions are ever attributed to any
   named individual — this is a generic pattern-based lens only.
3. Every application of this lens must include an explicit, written-in-
   advance invalidation condition.
4. Contrarian framing must be explicitly cross-checked against the
   Turnaround Skill's Signal vs Trap checklist to avoid mistaking a
   genuine value trap for a contrarian opportunity.
5. Position sizing recommendations under this lens are still bound by the
   hard caps in AI_Portfolio_Construction_Skill — conviction does not
   override portfolio-level risk architecture.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Heuristic Lens — Concentrated Small-Cap Style*
*Integrates with: Skill 01 (Master Research — Governance/Forensic Gates), AI_Turnaround_Analysis_Skill,
AI_Multibagger_Discovery_Skill, AI_Portfolio_Construction_Skill, Skill 15 (Pre-Investment Master Checklist)*
<!-- END SYSTEM FILE 3: AI_Concentrated_SmallCap_Style_Thinking_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 4: AI_DCF_Valuation_Skill.md | SHA256: 9ffb983cae45bd92e8392b39aafb423199e0040632c93f4991b5120e6cf27c93 -->
## Embedded source 4: AI DCF Valuation Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI DCF Valuation Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI DCF Valuation Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Valuation — Applies when intrinsic value estimation is required

---

## CRITICAL AI INSTRUCTION

This skill executes when a fundamental intrinsic value is required for any company. A DCF output is **not a price target** — it is a range of fair values under defined assumptions. All assumptions must be stated, challenged, and stress-tested. False precision is more dangerous than honest uncertainty. Always produce a **Reverse DCF** alongside the forward DCF.

---

## Purpose

Build a rigorous, assumption-transparent Discounted Cash Flow valuation model for Indian-listed companies. Produce a defensible intrinsic value range, identify the key value drivers, and perform a reverse DCF to understand what the market is already pricing in.

---

## Pre-Flight Requirements

```
□ Minimum 5 years of historical financials (P&L, Balance Sheet, Cash Flow)
□ Latest 4 quarters of results for TTM calculation
□ Industry growth rate benchmarks
□ Peer valuation multiples (for cross-validation)
□ Company's own guidance or management commentary on growth
□ CapEx guidance (maintenance vs. growth split)
□ Working capital trend (to estimate NWC changes)
□ Effective tax rate (use 5-year average, not single year)
□ Debt schedule (for FCFE or EV bridge)
□ Beta estimate (or sector beta for unlisted comparable)
```

If historical cash flows are unavailable: Use EBIT-based approximation, flag as lower confidence.

---

## Analysis Module 1 — Business Quality Pre-Assessment

Before running numbers, assess:

### Step 1.1 — Business Predictability Score
```
High Predictability (Score 3):
→ Recurring revenue model (subscription, annuity)
→ Long-term contracts (3+ years)
→ Essential service / regulated business

Medium Predictability (Score 2):
→ Consumer staples, utility-adjacent
→ Business with visible order book (1–2 years)

Low Predictability (Score 1):
→ Cyclical business (commodities, capital goods)
→ Project-based revenue
→ New/unproven business model
```

**DCF Discount Rule:** Low predictability businesses should use higher WACC and lower terminal growth rate. A cyclical business valued at peak earnings is a valuation error.

### Step 1.2 — Competitive Moat Assessment
```
Wide Moat → Use 10-year explicit period + high terminal value confidence
Narrow Moat → Use 7-year explicit period + moderate terminal value
No Moat → Use 5-year explicit period + minimal terminal value reliance
         → Terminal value should be <40% of total enterprise value
```

---

## Analysis Module 2 — Free Cash Flow Calculation

### Step 2.1 — FCFF (Free Cash Flow to Firm)
```
FCFF = EBIT × (1 − Tax Rate)
       + Depreciation & Amortisation
       − Capital Expenditure (Total)
       − Change in Net Working Capital

Where:
→ EBIT: use adjusted EBIT (exclude one-time items)
→ Tax Rate: use 5-year average effective rate (not statutory 25.17%)
→ CapEx: include maintenance + growth CapEx
→ NWC Change = Change in (Current Assets − Cash − Current Liabilities + Short-term Debt)
```

### Step 2.2 — Historical FCFF Analysis (5 Years)
```
Build table:
Year    | Revenue | EBIT | NOPAT | D&A | CapEx | ΔNWC | FCFF | FCF Margin
FY2021  |         |      |       |     |       |      |      |
FY2022  |         |      |       |     |       |      |      |
FY2023  |         |      |       |     |       |      |      |
FY2024  |         |      |       |     |       |      |      |
FY2025  |         |      |       |     |       |      |      |
5yr Avg |         |      |       |     |       |      |      |

Key Checks:
□ Is FCFF consistently positive? (Negative FCF businesses need special treatment)
□ Is FCF margin expanding or contracting?
□ CapEx intensity: CapEx/Revenue ratio trend
□ Reinvestment Rate: how much of NOPAT is reinvested?
   Reinvestment Rate = (CapEx − D&A + ΔNWC) / NOPAT
```

### Step 2.3 — FCFE (Free Cash Flow to Equity) — Optional
```
FCFE = Net Profit
       + Depreciation & Amortisation
       − Capital Expenditure
       − Change in Net Working Capital
       + Net Borrowing (New Debt − Repayments)

Use FCFE for equity valuation directly.
Use FCFF → EV → subtract debt → Equity value approach otherwise.
Consistency rule: FCFF discounted at WACC; FCFE discounted at Cost of Equity.
```

---

## Analysis Module 3 — WACC Calculation

### Step 3.1 — Cost of Equity (Ke) — CAPM
```
Ke = Rf + β × (Rm − Rf) + Additional Premiums

Where:
→ Rf (Risk-Free Rate): Use current 10-year G-Sec yield
   [As of analysis date — always use current, not historical]
→ β (Beta): Use 3-year weekly beta vs. Nifty 50
   → If stock is too small/illiquid: use sector unlevered beta + relevered for target structure
→ Rm − Rf (Equity Risk Premium): India ERP = 6.0–7.5% (use 7%)
→ Additional Premiums:
   Liquidity Premium (small/micro cap): +1.0% to +2.5%
   Country Premium (if significant foreign operations): adjust
   Company-Specific Premium (fraud/governance risk): +0.5% to +2.0%

Typical range for Indian equities:
→ Large cap blue chip: 10–12%
→ Mid cap quality: 12–14%
→ Small cap: 14–18%
→ Microcap / speculative: 18–22%
```

### Step 3.2 — Cost of Debt (Kd)
```
Kd (post-tax) = (Total Interest Expense / Average Debt) × (1 − Tax Rate)
→ Use actual interest from P&L, not headline rate
→ If interest coverage < 2x: Kd may understate true credit risk
→ Include lease liabilities (IND-AS 116) as debt if material
```

### Step 3.3 — Capital Structure and WACC
```
WACC = (E/V) × Ke + (D/V) × Kd

Where:
→ E = Market Capitalisation
→ D = Total Financial Debt (book value acceptable for stable businesses)
→ V = E + D

Note: Use target/normalised capital structure for stable businesses,
      not current structure if company is in debt-reduction mode.

WACC Sanity Check:
→ Must exceed inflation rate
→ Must be credible vs. sector benchmarks
→ Report WACC to 1 decimal place only — false precision beyond this
```

---

## Analysis Module 4 — Projection Framework

### Step 4.1 — Three-Stage Projection Model

**Stage 1: Explicit Forecast Period (Years 1–5)**
```
Build revenue and margin projections bottom-up:
→ Volume growth + Pricing growth = Revenue growth
→ Operating leverage: margin expansion per 100bps revenue growth
→ CapEx: maintenance + growth (use management guidance if available)
→ Working capital: use trend-adjusted days

Sources for assumptions:
→ Company management guidance (Tier 1, but verify with track record)
→ Industry association reports
→ Government data (PLI targets, infrastructure pipeline)
→ Peer company performance
```

**Stage 2: Transition Period (Years 6–10, if using 10-year model)**
```
→ Growth rate tapers from Stage 1 rate toward terminal growth
→ ROIC converges toward WACC as competitive advantages erode
→ CapEx intensity normalises
```

**Stage 3: Terminal Value**
```
Terminal Value = FCFF (Year N+1) / (WACC − g)

Where g = Long-term terminal growth rate
→ Conservative: g = India's long-term nominal GDP growth × 0.5
   (Company cannot grow faster than economy forever)
→ Typical range: 4–6% for India
→ Use lower g for: cyclicals, declining industries, governance-risk businesses
→ Use higher g for: regulated utilities, essential services, deep moat businesses

CRITICAL: Terminal Value should ideally be <70% of total enterprise value.
If TV >80%: model is too sensitive to terminal assumptions — use higher WACC
           or shorten explicit period.
```

### Step 4.2 — Three Scenarios (Mandatory)
```
BEAR CASE:
→ Revenue growth at -30% of base case
→ Margins compress to 5-year lows
→ WACC +200bps
→ Terminal growth -1%

BASE CASE:
→ Revenue growth at management-guided or industry-average rate
→ Margins at 5-year trend
→ WACC at calculated value
→ Terminal growth at India LT GDP growth rate

BULL CASE:
→ Revenue growth at historical peak or addressable market expansion
→ Margins at best-in-class peer level
→ WACC −50bps (execution premium)
→ Terminal growth +0.5%
```

---

## Analysis Module 5 — Reverse DCF (Always Run)

### Step 5.1 — Reverse Engineering Market Expectations
```
What growth rate does the current market price imply?

Process:
1. Start with Current Market Cap (= current enterprise value + net cash − debt)
2. Use company's actual FCFF margin and WACC
3. Solve for Revenue CAGR that yields the current EV
4. Compare implied growth to historical growth and analyst consensus

Output question: "At CMP of ₹X, the market is pricing in Y% revenue CAGR 
                 for the next N years. Is this achievable?"
```

### Step 5.2 — Market Expectation Assessment
```
Implied growth rate vs. reality:
→ Implied growth < historical average: Stock may be UNDERVALUED
→ Implied growth = historical average: Stock is FAIRLY VALUED
→ Implied growth > historical average: Stock may be OVERVALUED
   → BUT: Is there a genuine step-change catalyst? If yes, justify premium.

This is more useful than DCF alone because it anchors the analysis 
to what is priced in, not just what the model predicts.
```

---

## Analysis Module 6 — Valuation Cross-Check

### Step 6.1 — Multiple-Based Cross Validation
```
After DCF, cross-check with:

Method 1 — P/E based:
  Fair Value = Normalised EPS × Justified P/E
  Justified P/E = Based on ROE, growth, and peer comparison

Method 2 — EV/EBITDA based:
  Fair EV = EBITDA × Sector median EV/EBITDA
  Equity Value = Fair EV − Net Debt

Method 3 — Price/Book based:
  Useful for: Banks, NBFCs, asset-heavy businesses
  Fair P/B = ROE / Ke (Gordon Growth Model)
  
Method 4 — Dividend Discount Model (DDM):
  Useful for: High-dividend, stable businesses
  Fair Value = D1 / (Ke − g)

Coherence Check:
→ All methods should point to roughly similar ranges (+/− 20%)
→ Wide divergence = model assumption error or market mispricing
```

---

## Analysis Module 6A — India Sector WACC Reference Table

Use as sanity check after calculating WACC from first principles:

```
SECTOR                          TYPICAL WACC RANGE    NOTES
─────────────────────────────────────────────────────────────────
Consumer Staples (large cap)     10–12%               Low beta, stable
IT Services (large cap)          11–13%               Low debt, high ROE
Private Banks                    12–14%               Regulatory moat
Pharmaceuticals                  12–15%               Diversified, USFDA risk
NBFCs (quality)                  13–15%               Funding risk premium
Consumer Discretionary           12–15%               Cyclical premium
Capital Goods / Engineering      13–16%               Long-cycle, capex risk
Specialty Chemicals              13–16%               RM volatility
Auto Ancillaries                 13–16%               OEM dependency
Renewable Energy (project-level)  8–10%               Near-certain PPA CF
Regulated Utilities (NTPC type)   9–11%               Quasi-sovereign
Defence (PSU)                    10–12%               Government backing
Realty / Developers              15–19%               Execution + regulatory risk
Microcap / Early stage           18–24%               Illiquidity + governance
MFI / High-risk NBFC             16–20%               Asset quality volatility

RULE: If your calculated WACC falls outside ±200bps of sector range, 
      re-examine beta, risk-free rate, and capital structure assumptions.
```

## Analysis Module 6B — Negative FCF Company Protocol

When company has negative or near-zero FCF (common: early-stage, growth-capex phase):

```
Step 1 — Diagnose the reason:
Type A: Growing too fast (CapEx > OCF temporarily) → Acceptable
  Signal: OCF positive and rising, CapEx for proven demand
Type B: Business generating no cash despite profits → Investigate
  Signal: PAT positive, OCF negative = working capital trap or manipulation
Type C: Structurally unprofitable → Avoid unless turnaround thesis
  Signal: Operating loss, no path to profitability

Step 2 — For Type A only: use forward FCF model
→ Project when CapEx normalises (capacity commissions)
→ Use "normalised FCF" = current OCF × (1 + growth) − maintenance CapEx
→ Discount back at appropriate WACC
→ Apply higher WACC (+200bps) to reflect uncertainty on timing

Step 3 — Negative FCF runway check:
Cash + Undrawn Lines / Monthly Cash Burn = Months of Runway
→ < 12 months: Dilution or debt raise imminent = near-term shareholder risk
→ 12–24 months: Monitor
→ > 24 months: Adequate buffer

Step 4 — Terminal value reliability:
→ For negative FCF companies, TV is often >90% of EV
→ This makes DCF extremely fragile
→ ALWAYS cross-check with: (a) peer EV/Revenue, (b) scenario where FCF 
  positive date slips 2 years → what is value impact?
```

## Analysis Module 6C — Reinvestment Efficiency

```
Reinvestment Rate = (Net CapEx + ΔNWC) / NOPAT
  Where Net CapEx = CapEx − Depreciation

ROIC = NOPAT / Invested Capital

Value creation requires: ROIC > WACC

Reinvestment Return = ROIC × Reinvestment Rate = Sustainable Growth Rate
  Example: ROIC 20%, Reinvestment Rate 50% → Sustainable growth = 10%

Cross-check: Does DCF-assumed growth rate ≤ sustainable growth rate?
  If DCF assumes 15% growth but sustainable growth is 10% → Overoptimistic model

Companies with ROIC >> WACC and low reinvestment rate:
→ Compounders: high-quality but limited reinvestment opportunity
→ Value to shareholders via dividends/buybacks
→ Value in DCF = high terminal value relative to explicit period

Companies with ROIC < WACC but high reinvestment:
→ Destroying value with every rupee reinvested
→ Growth is a negative in DCF when ROIC < WACC
→ Management should return capital, not reinvest
```

## Margin of Safety Framework

```
Business Quality → Minimum Required Margin of Safety

Wide Moat, Strong Governance:    Buy if CMP < 85% of Bear Case Value (15% MoS)
Narrow Moat, Good Governance:    Buy if CMP < 75% of Base Case Value (25% MoS)
No Moat or Governance Concern:   Buy if CMP < 60% of Base Case Value (40% MoS)
Cyclical at Trough Earnings:     Buy if EV/EBITDA < 5x trough EBITDA

Valuation Exit Signal:
→ CMP > 120% of Bull Case Value: consider reducing position
→ CMP > Bear Case Value only by 10%: exit or tight stop
```

---

## Final DCF Output Format

```
DCF VALUATION REPORT
Company: [Name] | Ticker: [NSE/BSE] | CMP: ₹[X]
Analysis Date: [DD/MM/YYYY] | Model: [FCFF/FCFE/DDM]
═══════════════════════════════════════════════════════════════════

KEY ASSUMPTIONS:
  Risk-Free Rate:     [%] (10-yr G-Sec as of [date])
  Beta:               [X.XX] ([3-year weekly vs. Nifty 50])
  Cost of Equity:     [%]
  Cost of Debt:       [%] (post-tax)
  WACC:               [%]
  Terminal Growth:    [%]
  Forecast Period:    [N] years
  Model Confidence:   [High / Medium / Low] — [reason]

─────────────────────────────────────────────
SCENARIO ANALYSIS:
                     Bear     Base     Bull
Revenue CAGR (5yr): [%]      [%]      [%]
EBITDA Margin:      [%]      [%]      [%]
Intrinsic Value:   ₹[X]    ₹[X]    ₹[X]
Upside/Downside:   [%]     [%]     [%]
Terminal Value %:   [%]     [%]     [%]

REVERSE DCF:
  Implied Revenue CAGR (at CMP ₹[X]):  [%]
  This vs. Historical CAGR:             [%] (5yr historical)
  Assessment:  [Underpriced / Fairly priced / Overpriced]
  Embedded Expectation: [What must happen for CMP to be justified]

─────────────────────────────────────────────
MULTIPLE CROSS-CHECK:
  P/E Based Value:        ₹[X] (at [X]x on ₹[Y] normalised EPS)
  EV/EBITDA Based Value:  ₹[X] (at [X]x on ₹[Y]Cr EBITDA)
  Price/Book Based Value: ₹[X] (at [X]x P/B justified by [X]% ROE)
  Coherence Check:        [All methods aligned / Divergent — reason]

─────────────────────────────────────────────
VALUATION CONCLUSION:
  Intrinsic Value Range:  ₹[Bear Value] — ₹[Bull Value]
  Base Case Fair Value:   ₹[Base Value]
  CMP:                    ₹[X]
  Margin of Safety:       [%] — [Adequate / Insufficient / Strong]
  Required MoS for this business: [%]
  
  BUY ZONE:     ₹[Lower] – ₹[Upper] (offers required margin of safety)
  FAIR VALUE:   ₹[X]
  EXPENSIVE:    Above ₹[X]
  
  KEY VALUE DRIVERS (in order of impact):
  1. [Assumption X — what it does to value if changes ±1%]
  2. [Assumption Y]
  3. [Assumption Z]
  
  WHAT COULD BE WRONG WITH THIS MODEL:
  → [Key assumption that is most uncertain]
  → [Data limitation that reduces confidence]
  
  VALUATION RECOMMENDATION:
  → [ATTRACTIVE — Strong Buy Zone | FAIR — Hold/Accumulate | 
     EXPENSIVE — Reduce | SIGNIFICANTLY OVERVALUED — Exit]
```

---

## Universal Rules — DCF Valuation

1. **Terminal value dependency >70% = model is fragile.** Increase explicit forecast period or use conservative TV.
2. **Never value a cyclical at peak earnings.** Use mid-cycle normalised earnings.
3. **Always run the Reverse DCF.** Market expectation analysis is more honest than model precision.
4. **Assumptions kill DCFs, not arithmetic.** State every assumption and challenge it.
5. **WACC below 10% for Indian equities = almost certainly wrong.** Minimum floor: 10%.
6. **A model that always gives the answer you expected is not a model — it is confirmation bias.**
7. **Range is more honest than point estimate.** Always output bear/base/bull.
8. **Cross-check with multiples.** If all methods disagree, find out why before concluding.

---

*Skill Version 1.0 | IERL Specialist Skill Library | Indian Equity Research Lab*
*This skill integrates with: Skill 01 (Master Research), Skill 07 (Valuation Comparator), Skill 15 (Pre-Investment Checklist)*
<!-- END SYSTEM FILE 4: AI_DCF_Valuation_Skill.md -->

---


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

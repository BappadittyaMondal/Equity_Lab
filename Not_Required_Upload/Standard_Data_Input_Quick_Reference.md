# Standard Data Input Quick Reference
## Prepare These Inputs Before Your IERL Expert Strategy Session

**Purpose:** This is a portable checklist for users of the IERL AI Equity OS.  
Before starting any session using the 18 Expert Strategies, gather the inputs  
below. For each strategy, locate the row that matches the module you intend to run.

---

## Common Inputs (Required for ALL 18 Strategies)

```
□ Company name / Instrument name / Ticker symbol
□ Asset class: Equity | Nifty Futures | Bank Nifty Futures | Options
□ Current Market Price (CMP) or Spot Level + exact as-of date and time
□ Segment-wise revenue breakdown from Annual Report
  (mandatory for the Saatvik D18 ethical filter — always run this first)
```

---

## Category A — Derivatives Strategies (Modules A1 to A4)
*Expert: Mr. Ankit Rai | Domain 45*

```
□ Opening Nifty / Bank Nifty spot price at exactly 09:16 AM
  (required for A2 Range Option Selling — 250+ pt OTM strike calculation)

□ Weekly / Monthly Option Chain — complete table with:
  — Strike price grid (ATM, OTM Call, OTM Put)
  — Implied Volatility (IV) for each strike
  — Delta and Theta for each strike
  — Bid-Ask spread / market depth for each strike

□ Intraday session timestamp:
  — 09:15:00 – 09:15:30 AM (morning panic window, for A1 Arbitrage)
  — 09:20 AM, 09:25 AM, or 09:30 AM (for A3 Straddle entry — pick one)

□ Zero-DTE (weekly expiry) session confirmation:
  — Is today a weekly expiry day? (YES / NO)

□ SuperTrend (10,3) indicator current signal:
  — GREEN (Buy) or RED (Sell)? (for A4 Trend-Following Futures)
  — Chart timeframe used (daily / hourly)

□ India VIX current level (for regime check — mandatory before any selling strategy):
  — VIX < 13 | 13–20 | 20–25 | > 25 ?
  — If VIX > 25: Do NOT execute A2 or A3 option-selling strategies this session.
```

---

## Category B — Technical Growth Strategies (Modules B5 to B8)
*Expert: Mr. Aniketh Dsouza | Domain 46*

```
□ Daily price chart — minimum 1–2 years of historical OHLCV data

□ Weekly price chart — minimum 1–2 years of historical OHLCV data
  (required for B7 Weinstein Stage Analysis)

□ Moving Averages — all of the following:
  — 50-day SMA (Simple Moving Average)
  — 150-day SMA (30-week MA for Stage Analysis)
  — 200-day SMA

□ 200-day SMA slope direction:
  — Is it trending upward for at least 1 month? (YES / NO)

□ 52-week High (₹ ______)
□ 52-week Low (₹ ______)

□ Daily volume bars — last 60 trading days
□ 50-day average volume value (for VCP right-side volume dryup check)

□ Relative Strength (RS) rating vs Nifty 50 / Nifty 500:
  — Current RS rating (1–99 scale) or RS line position vs index
  — Is RS line trending up and outperforming? (YES / NO)

□ TTM (Trailing Twelve Month) EPS growth rate (%):
  — Required for B8 SEPA — must be >25% to qualify as a catalyst
```

---

## Category C — Fundamental Value Strategies (Modules C9 to C14)
*Expert: Mr. Anshul Saigal | Domain 47*

```
□ Current Stock Price (CMP) + Market Capitalization (₹ Crore)

□ Trailing Twelve Month (TTM) Profit After Tax (PAT) — ₹ Crore
□ Trailing Twelve Month (TTM) Revenue — ₹ Crore
□ Trailing Twelve Month (TTM) Free Cash Flow (FCF) — ₹ Crore

□ For C9 Reverse DCF:
  — WACC (Weighted Average Cost of Capital) assumption (%)
  — Your estimated implied market terminal growth rate (derived from Reverse DCF model)
  — Historical context: Is the implied growth assumption logically absurd
    for the company's market position and industry? (YES = potential setup)

□ For C10 Variant Perception:
  — Sell-side analyst consensus Revenue / PAT expectation
  — Your differentiated Variant Perception estimate (must differ from consensus)
  — Specific named catalyst event + target date (within 3–12 months)

□ For C11 Cyclical Bottom:
  — Historical 5–10 year Price-to-Book (P/B) range: Low [____] to High [____]
  — Current P/B: [____]
  — Industry capacity utilization % (current vs. peak): [____]
  — Debt/EBITDA ratio (solvency check): [____]

□ For C12 Capital-Light Fast Growers:
  — Multi-year ROIC trend (3 years): [____%, ____%, ____%]
  — Capex as % of Operating Cash Flow (must be <15%–20%): [____]
  — Description of proprietary IP / content library / licensing asset

□ For C13 Misunderstood Stalwarts:
  — ARPU or key unit economics trend (3 years)
  — ROE trend (3 years): currently at floor vs. historical high?
  — Specific catalyst for ROE recovery (pricing power, tariff hike, etc.)

□ For C14 Turnaround (NCLT):
  — NCLT resolution order date + acquiring promoter group name
  — Pre-acquisition: Debt amount and net worth (₹ Crore)
  — Post-restructuring: Capital injected + management installed
  — Operating Cash Flow status (positive / negative) since acquisition
```

---

## Category D — Quant Momentum & Screening Strategies (Modules D15 to D18)
*Expert: Mr. Rohan Mehta | Domain 48*

```
□ For D15 / D16 All-Time High & Triple-Filter:
  — Stock historical All-Time High price: ₹ [______]
  — Current price: ₹ [______] — Is it AT or ABOVE historical ATH? (YES / NO)
  — ATH breakout volume: [____] — Is it ≥ 1.5x average daily volume? (YES / NO)
  — Trailing Twelve Month (TTM) PAT historical peak: ₹ [______] Crore
  — Current TTM PAT: ₹ [______] Crore — Is it AT or ABOVE historical ATH? (YES / NO)
  — 52-week Relative Strength vs Nifty 500: +[____]% outperformance
  — 52-week Relative Strength vs Sector Index: +[____]% outperformance

□ For D17 Risk-Based Position Sizing:
  — Total Portfolio Capital: ₹ [______________]
  — Maximum Risk % per trade (default = 1.2%): [____]%
  — Target Entry Price: ₹ [______]
  — 200-day EMA Exit Price: ₹ [______]
  — Distance % = (Entry - Exit) / Entry × 100 = [____]%
  — Calculated Position Size = Max Risk % / Distance % = [____]% of portfolio

□ For D18 Saatvik Ethical Filter (ALWAYS RUN FIRST):
  — Segment revenue breakdown: [Provide table from Annual Report]
  — Check: Any revenue from Animal Slaughter / Alcohol / Tobacco /
    Leather / Gambling / Sin Hospitality?
  — If YES to any: FAIL — stop all further analysis on this company.
  — If NO to all: PASS — proceed to financial analysis.
```

---

## Quick Session Sequence (Recommended Order)

```
1. Gather Common Inputs above (CMP, ticker, segment revenue)
2. Run D18 Saatvik Filter FIRST — if FAIL, stop immediately
3. Select your strategy category (A / B / C / D) based on your objective
4. Gather the category-specific inputs for your chosen module(s)
5. Provide all gathered inputs to the AI and reference the relevant module
   (e.g., "Run Module C9 on [Company] using the following inputs: ...")
6. Review the Decision Card output — check Confidence level and Data Gaps
7. If gaps exist, gather the missing data and re-run before making any decision
```

---

*Source: All inputs derived from `AI_18_Expert_Strategies_Execution_Skill.md` Pre-Flight Requirements section.*  
*This file is NOT part of the compiler bundles — it is a user reference tool only.*

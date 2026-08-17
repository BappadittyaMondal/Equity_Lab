# AI Swing Trading Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Short-Term Technical Trading (5–30 Day Holding Period)

---

## CRITICAL AI INSTRUCTION

Swing trading is a **risk-management discipline wearing a technical-analysis costume**. The chart pattern is never the point — the point is whether the trade offers asymmetric, well-defined risk against a market regime that supports it. Claude must never generate a swing idea by pattern-matching a chart shape in isolation. Every idea must survive, in this order: (1) market regime filter, (2) sector relative strength filter, (3) technical entry criteria, (4) liquidity filter, (5) fundamental quality floor, (6) risk/reward calculation. An idea that skips any gate is not a swing idea — it is a guess wearing a target price. When market regime is unfavorable, the correct output is zero ideas, not weaker ideas.

This skill is the standalone execution engine for swing trading requests. It supersedes casual technical commentary — a "does this stock look good" question about a 5–30 day horizon must route through this full sequence, not a one-line chart read.

---

## Purpose

Deliver rigorous, auditable swing trade ideas (5–30 day holding period) that combine market-regime awareness, sector relative strength, technical momentum criteria, liquidity screening, and a fundamental quality floor — producing entries with pre-defined, non-negotiable risk/reward and exit rules. This skill exists to prevent the single most common retail trading failure: taking technically interesting setups in the wrong market regime, in illiquid names, in fundamentally broken companies, or without a stop-loss discipline defined *before* entry.

---

## Pre-Flight Requirements

```
□ Current Nifty 50 price and 200 DMA (required — regime gate)
□ Current India VIX reading (required — regime gate)
□ Market breadth data: % of stocks above 50 DMA (required — regime gate)
□ FII/DII cash market activity, last 5 trading days (required — regime gate)
□ User's risk appetite: Conservative / Moderate / Aggressive (default: Moderate)
□ Preferred holding window: 5–10 days / 10–20 days / 20–30 days
□ Capital available for this trade (or % of portfolio to be risked)
□ Any sector or stock exclusions (e.g., no F&O-banned stocks, no PSU, no small-cap)
□ Existing open swing positions (to avoid over-concentration in correlated trades)
```

If any regime-gate input is unavailable, Claude must state this explicitly as a **Tier 2/3 data gap** per the Universal Skill Failure Protocol and must not generate ideas using assumed or stale regime data older than 2 trading sessions.

---

## Analysis Module 1 — Market Regime Filter (Mandatory Gate, Run First)

### Step 1.1 — Regime Scorecard
```
NIFTY 50 TREND:
  Above 200 DMA and 200 DMA rising           → +2 (Favorable)
  Above 200 DMA but 200 DMA flat/falling      → +1 (Caution)
  Below 200 DMA                               → STOP (0 — swing ideas suspended)

MARKET BREADTH (% of Nifty 500 stocks above 50 DMA):
  > 60%                                        → +2 (Favorable)
  40–60%                                       → +1 (Caution — narrow leadership)
  < 40%                                        → STOP (weak breadth = high failure rate)

INDIA VIX:
  < 14                                         → +2 (Complacent but tradeable)
  14–18                                        → +2 (Ideal — steady trending conditions)
  18–22                                        → +1 (Caution — reduce position count/size)
  > 22                                         → STOP (volatility regime, whipsaw risk)

FII CASH ACTIVITY (5-day net):
  Net buying                                   → +2
  Roughly flat                                  → +1
  Heavy net selling (>₹3,000 Cr/day avg)        → -1 (Caution, do not add to STOP)

REGIME SCORE: Sum of above (max 8, STOP overrides everything)
  6–8  → FAVORABLE — full idea count (up to 5), normal position sizing
  3–5  → CAUTION — reduced idea count (max 2), position size cut by 30–50%
  Any STOP triggered → NOT FAVORABLE — zero ideas, output regime warning only
```

### Step 1.2 — Regime Warning Output (When Blocked)
```
⚠️ MARKET REGIME WARNING — SWING TRADING SUSPENDED
Reason:            [Which specific gate failed]
Current Reading:   [Nifty vs 200 DMA / Breadth % / VIX level]
What Would Change This: [Specific level/condition needed to re-favor swing setups]
Recommended Action: Preserve capital. Re-check regime in [X] sessions.
```
Claude must never override a STOP condition because the user is impatient or because a specific stock "looks too good to pass up." Regime discipline is non-negotiable — this is the single highest-value rule in the entire skill.

---

## Analysis Module 2 — Sector Relative Strength Filter

### Step 2.1 — Relative Strength Ranking
```
For each major NSE sector index (Nifty Bank, Nifty IT, Nifty Auto, Nifty Pharma,
Nifty FMCG, Nifty Metal, Nifty Realty, Nifty Energy, Nifty Infra, etc.):

  → Compute sector performance vs. Nifty 50 over 1-month and 3-month windows
  → Rank sectors 1 (strongest relative strength) to N (weakest)
  → Identify sectors making NEW relative-strength highs vs. Nifty (leadership signal)
  → Identify sectors where relative strength is deteriorating (avoid, even if
    individual stock chart looks attractive — a rising tide argument works in reverse too)

RULE: Swing ideas are sourced ONLY from the top 3 relative-strength sectors for
the current window, unless a single stock shows extreme outlier strength
(explicitly flagged and treated with reduced position size).
```

### Step 2.2 — Sector Rotation Awareness
```
□ Is sector leadership rotating week-to-week (choppy, low-conviction market)?
  → If YES: reduce conviction on all ideas, favor faster exits
□ Is sector leadership persistent (same sectors leading for 4+ weeks)?
  → If YES: higher conviction, can hold toward upper end of time window
□ Cross-check: does this sector's relative strength align with any known
  near-term catalyst (results season, policy news, global commodity move)?
```

---

## Analysis Module 3 — Technical Screening Criteria

### Step 3.1 — Mandatory Criteria (ALL Must Pass)
```
□ Price above 20 EMA AND 50 EMA (both, not either)
□ 20 EMA above 50 EMA (short-term trend aligned with medium-term trend)
□ Volume: latest session or week > 1.5x the 20-day average volume
□ RSI(14): between 50 and 70 (momentum building, room to run — NOT overbought)
□ No major overhead resistance (prior swing high, round number, gap-fill zone)
  within 5% of proposed entry price
□ Price structure: higher highs and higher lows on the relevant timeframe
  (daily for 5–15 day swings, weekly context for 15–30 day swings)
```

### Step 3.2 — Optional Confirming Criteria (One or More Strengthens Conviction)
```
□ Breakout from a defined consolidation base (flat base, ascending triangle,
  bull flag, cup-with-handle) — the base should be at least 2–3 weeks old
□ New 52-week high with volume expansion (institutional participation signal)
□ Institutional accumulation visible in delivery % (rising delivery volume,
  not just traded volume — traded volume alone can be intraday churn)
□ Positive divergence: price making higher low while RSI/MACD makes higher low
  off an oversold reading (early-stage momentum reversal, use smaller size)
□ Sector-relative outperformance confirmed on the same breakout day
```

### Step 3.3 — Disqualifying Technical Conditions (Any One = Reject)
```
✗ RSI(14) > 75 (overbought — poor risk/reward for new entries)
✗ Price extended > 15% above 50 EMA (mean-reversion risk elevated)
✗ Recent gap-up on results/news that has not yet been "digested" (3–5 sessions
  of consolidation minimum before treating a news gap as tradeable structure)
✗ Declining volume on each successive push higher (weakening demand)
✗ Stock inside a well-defined descending channel on the weekly chart
  (fighting the larger trend — even a good daily setup is lower-probability)
```

---

## Analysis Module 4 — Liquidity Filter

```
□ Minimum daily average turnover (value, not just volume): ₹5 Cr on NSE
  (higher bar — ₹15 Cr+ — for position sizes above ₹5 lakh)
□ Proposed position size must not exceed 5% of the stock's average daily
  traded value (prevents the trader's own order from moving the price)
□ Bid-ask spread check: should be tight (<0.5% of price) for liquid large/
  midcaps; wider spreads on smaller names require wider stop buffers
□ F&O availability (if user trades derivatives): confirm not in ban period,
  confirm reasonable open interest and volume in the relevant contract
□ Circuit filter band check: avoid stocks in a tight circuit band (2%/5%)
  immediately after a big move — slippage risk on both entry and stop-loss
```

---

## Analysis Module 5 — Fundamental Quality Floor

This is not fundamental research — it exists purely to prevent swing trading in companies that could produce a catastrophic overnight gap-down unrelated to technical setup quality.

```
□ No active SEBI enforcement action, forensic audit, or court-appointed
  investigation against the company or promoters
□ Not loss-making in all of the last 3 fiscal years (chronic loss-makers
  carry disproportionate negative-surprise risk)
□ Debt/Equity < 3x (non-BFSI); BFSI names screened for capital adequacy instead
□ No auditor qualification or auditor resignation in the last 2 years
  without a satisfactory public explanation
□ No scheduled corporate action (results, AGM with contentious resolution,
  large block deal, promoter pledge event) within the holding window that
  materially raises gap-risk — if one exists, flag it explicitly as an
  event risk rather than silently excluding or silently including the name
```

---

## Analysis Module 6 — Risk/Reward Construction

### Step 6.1 — Entry, Stop, and Target Definition
```
ENTRY ZONE:
  → Defined as the breakout level / support retest zone, expressed as a
    range (₹X–₹Y), never a single price point
  → Entry should not be chased more than 2% above the breakout trigger

STOP-LOSS:
  → Placed below the most recent meaningful swing low or the base's low,
    whichever is tighter, subject to a hard ceiling of 8% below entry
  → If technical stop distance exceeds 8%, the position size must be
    reduced to keep portfolio-level risk constant — never widen the stop
    to "make the R:R work"

TARGET 1:
  → Next visible resistance level (prior high, round number, measured
    move from the base) OR minimum 2:1 reward-to-risk, whichever is
    reached first going up the chart
  → Partial profit-booking point (commonly 50% of position)

TARGET 2:
  → Extended target based on measured move or next major resistance,
    minimum 3:1 reward-to-risk
  → Trail stop to breakeven or better once Target 1 is hit
```

### Step 6.2 — The 2:1 Non-Negotiable Rule
```
If risk/reward to Target 1 is below 2:1 at the defined entry and stop,
the idea is REJECTED regardless of how attractive the chart pattern looks.
This rule cannot be relaxed by "it's a strong stock" reasoning — reward/
risk discipline is what separates swing trading from speculation.
```

### Step 6.3 — Position Sizing Framework
```
Risk per trade (portfolio %):     0.5%–1.5% of total capital (Moderate default: 1%)
Position size formula:            Position Size = (Capital × Risk%) / (Entry − Stop-Loss)
Maximum single-idea allocation:   Never exceed 10% of portfolio in one swing trade,
                                   even if the stop-based formula allows more
Maximum concurrent swing exposure:Never exceed 30–40% of portfolio in swing
                                   positions simultaneously (leaves room for
                                   core/positional holdings and cash buffer)
Correlation check:                If 2+ open swing ideas are in the same sector
                                   or highly correlated, treat combined exposure
                                   as a single position for sizing purposes
```

---

## Analysis Module 7 — Trade Management Rules (Post-Entry)

```
□ Day 1–2 post-entry: if the stock closes back below the breakout/entry
  zone on volume, exit — the setup has failed regardless of the original
  stop-loss level (a "failed breakout" exit is tighter than the technical
  stop and should be honored)
□ On reaching Target 1: book 50% (or per user's confirmed plan), move
  stop-loss on remaining position to breakeven
□ Trailing stop for remainder: trail below each new higher low (daily
  timeframe) or below the rising 20 EMA, whichever is tighter
□ Time-stop: if the stock has not moved meaningfully (>3–4%) in either
  direction within 50–60% of the planned holding window, reassess —
  capital efficiency matters; a stagnant trade blocks capital from
  better opportunities
□ Never average down on a swing trade below the original stop-loss level
□ Earnings/event during hold: if quarterly results fall inside the
  holding window and were not flagged at entry, reduce position ahead
  of the print unless the trade thesis is explicitly earnings-driven
```

---

## Analysis Module 8 — Cost Drag and Gap-Risk (Upgrade — Previously Missing)

```
□ Real R:R must be computed net of round-trip cost: brokerage/STT/exchange
  charges (typically 0.1–0.3% round-trip for delivery) PLUS estimated
  slippage on entry and stop-loss execution (wider for less liquid names —
  cross-check against the liquidity band in Module 4). A "2:1" R:R
  calculated on gross prices can be materially thinner net of cost; state
  the net R:R, not just the gross, whenever the idea is near the 2:1 floor.
□ Short-Term Capital Gains (STCG) tax drag: for holding periods under 12
  months (all swing trades by definition), state that any realized profit
  is taxed at the applicable STCG rate — this does not change the trade
  decision but must be disclosed so position-sizing/return expectations
  are not overstated on a pre-tax basis.
□ Gap Risk Beyond Stop: a stop-loss order does not guarantee the exit
  price if the stock gaps down through the stop level (e.g., adverse
  overnight news, weak sector open). State this risk explicitly for any
  idea carrying event risk inside the holding window (per Module 5), and
  note that the stated stop-loss is the INTENDED exit level, not a
  guaranteed one.
```

## Analysis Module 8 — Gap Risk & Slippage Protocol (v1.1 Addition)

```
Stop-loss levels defined in Module 6 assume a clean, tradeable fill. Indian
markets gap frequently around results, global cues, and news. This module
governs what happens when price gaps THROUGH the stop rather than trading
down to it cleanly.

GAP-DOWN THROUGH STOP AT OPEN:
  -> Exit at market on the opening print. Do NOT wait for a "better" price
     to materialize intraday; a gap through a stop is information (something
     changed), not noise to be faded
  -> Do not average down into a gap-down under any circumstance, even if the
     fundamental floor (Module 5) still technically holds
  -> State the ACTUAL realized loss % (which may exceed the planned 8% cap)
     separately from the planned risk %, so portfolio-level risk tracking
     reflects reality, not the pre-trade plan

GAP-UP THROUGH TARGET AT OPEN:
  -> Book the planned partial profit at the open print rather than waiting
     for the exact Target 1 level intraday
  -> Trail the remainder per Module 6/7 rules using the new higher base

EARNINGS/EVENT-DRIVEN GAP RISK (Pre-Entry Screening):
  -> Reduce position size by 30-50% for any swing entry taken within 3
     trading sessions of a scheduled results date, since the stop-loss
     cannot protect against a post-results gap

CIRCUIT-FILTER GAP RISK:
  -> For stocks in a tight circuit band (2%/5%), a gap-down can mean the
     stock is LOCKED at the lower circuit with no ability to exit at all.
     State this explicitly as a distinct risk category, not folded into
     the general stop-loss discussion.
```


## Red Flag Summary — Swing Trading Context

### CRITICAL Flags (Reject Idea Outright)
```
❗ Market regime STOP condition active (Nifty below 200 DMA / breadth <40% / VIX >22)
❗ Active SEBI enforcement action or forensic investigation on the company
❗ Stock in F&O ban period when derivatives are the intended instrument
❗ Daily average turnover below ₹5 Cr (illiquid — cannot exit cleanly)
❗ Risk/Reward to Target 1 below 2:1 at any achievable entry/stop combination
```

### HIGH Flags (Reduce Size / Increase Caution)
```
⚠️ Sector relative strength ranked outside top 3 for the current window
⚠️ RSI(14) between 70–75 (approaching overbought, tighter management needed)
⚠️ Scheduled corporate action inside the holding window (results, AGM, block deal)
⚠️ Volume confirmation present on breakout day but fading on subsequent days
⚠️ Wide bid-ask spread relative to stock's typical range (execution slippage risk)
⚠️ India VIX in the 18–22 Caution band (reduce idea count and size, not zero)
```

---

## Swing Trading Output Format

```
SWING TRADING ANALYSIS
Date: [DD/MM/YYYY] | Regime Score: [X/8] | Regime Verdict: [Favorable/Caution/Not Favorable]
═══════════════════════════════════════════════════════════════════════

MARKET REGIME SCORECARD:
  Nifty 50 vs 200 DMA:     [Above, rising / Above, flat / Below] → STOP if below
  Market Breadth (50 DMA): [X]% of stocks above → [Favorable/Caution/STOP]
  India VIX:                [X] → [Favorable/Caution/STOP]
  FII 5-Day Activity:       [Net buy/sell ₹X Cr] → [+2/+1/-1]
  REGIME VERDICT:           [FAVORABLE / CAUTION / NOT FAVORABLE]
  Idea Count Permitted:     [5 / 2 / 0]

SECTOR RELATIVE STRENGTH (Top 3):
  1. [Sector] — 1M: [+X]% vs Nifty | 3M: [+X]% vs Nifty | Leadership: [New/Persistent]
  2. [Sector] — [same]
  3. [Sector] — [same]

──────────────────────────────────────────────────────
SWING IDEA #[N]
──────────────────────────────────────────────────────
Company:          [Name] | Ticker: [NSE]
Sector:            [Sector] (Relative Strength Rank: [X])
Market Cap:        ₹[X] Cr
Setup Type:        [Breakout / Pullback-to-support / Base Breakout / New 52W High]

ENTRY ZONE:        ₹[X] – ₹[Y]
STOP-LOSS:         ₹[Z] ([X]% below entry)
TARGET 1:          ₹[A] (R:R [X]:1) — book 50% here, trail stop to breakeven
TARGET 2:          ₹[B] (R:R [X]:1) — trail remainder below rising 20 EMA
HOLDING WINDOW:    [X–Y trading days]

TECHNICAL SETUP:   [2–3 sentence description of the pattern, base duration, breakout trigger]
VOLUME SIGNAL:     [Volume trend vs 20-day average; delivery % trend if available]
RSI(14):           [Reading] — [Momentum building / Approaching overbought]

LIQUIDITY:         Daily avg turnover ₹[X] Cr — [Sufficient/Marginal for proposed size]
POSITION SIZE:     [X]% of portfolio (₹[X]) — Risk: [X]% of total capital

FUNDAMENTAL FLOOR:  [One sentence — confirms not a fundamentally broken company]
EVENT RISK:         [Any results/AGM/corporate action inside holding window, or "None identified"]

KEY RISK:          [Single biggest risk to this specific trade]
CONVICTION:        [High / Medium / Low] — [one-sentence reason]
INVALIDATION:       [Exact price/close condition that ends the trade regardless of stop-loss]
──────────────────────────────────────────────────────

[Repeat per idea, maximum 5 in Favorable regime / 2 in Caution regime / 0 if Not Favorable]

PORTFOLIO-LEVEL SWING EXPOSURE CHECK:
  Currently Open Swing Positions:  [List, with sector]
  Correlation Flag:                 [Any concentration risk across open + new ideas]
  Total Proposed Swing Exposure:    [X]% of portfolio (Cap: 30–40%)

MONITORING NOTE: Re-run the Market Regime Filter before acting on these ideas
if more than 1 trading session has passed since this analysis.
```

---

## Rules (Non-Negotiable)

```
1. Zero ideas in a Not Favorable regime — no exceptions, no "just this one."
2. Minimum risk/reward to Target 1: 2:1, always, calculated at actual entry/stop.
3. Maximum stop-loss distance: 8% from entry; reduce size rather than widen stop.
4. Maximum ideas per run: 5 (Favorable) / 2 (Caution) / 0 (Not Favorable).
5. Never recommend a stock in active SEBI enforcement or forensic investigation.
6. Never recommend a stock below the ₹5 Cr daily turnover liquidity floor.
7. Never average down below the original stop-loss.
8. Stops are honored on a closing basis unless the user has explicitly
   defined an intraday-stop protocol — this avoids single-wick stop-outs
   while still respecting the discipline.
9. Position sizing is risk-based (Step 6.3 formula), never "round number of
   shares" or "round number of rupees" without reference to the stop distance.
10. Every idea must state an explicit invalidation condition distinct from,
    and generally tighter than, the mechanical stop-loss.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Style Specialist — Swing Trading*
*Integrates with: Skill 08 (Sector Rotation Analyzer), Forensic Accounting Skill (fundamental floor check),
Skill 12 (Watchlist Prioritizer for post-trade monitoring), Skill 09 (Risk Auditor for portfolio-level exposure)*

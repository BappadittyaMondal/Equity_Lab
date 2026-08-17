# AI Uptrend Momentum Stock Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Trend-Following, Trailing-Stop Momentum Framework

---

## CRITICAL AI INSTRUCTION

This skill is deliberately distinct from AI_Swing_Trading_Skill in its core exit philosophy. Swing trading uses FIXED targets and a defined holding window (5-30 days) — the trade has a planned endpoint. This skill uses NO fixed target and NO fixed holding window — a position is held for as long as the trend remains intact, exiting only when a trailing stop is breached, however long or short that takes. The entire discipline of this skill is: let winners run, cut losers fast, and let the trailing stop — not a prediction of where the stock will stop going up — decide the exit. Claude must never impose a target price ceiling on a position managed under this skill; doing so contradicts the method's entire premise. The single hardest behavioral failure this skill guards against is the trader's own instinct to book profits early "just in case" — the trailing stop exists precisely so that discipline, not prediction, governs the exit.

---

## Purpose

Identify and manage positions in stocks exhibiting genuine, sustained price uptrends using a trend-following framework with objective entry criteria and a strictly mechanical, progressively tightening trailing-stop exit discipline — explicitly avoiding fixed profit targets so that strong trends are allowed to run for their full duration, while losing or reversing positions are cut quickly and without hesitation.

---

## Pre-Flight Requirements

```
□ Market regime check (same Module 1 gate as AI_Swing_Trading_Skill — a
  trend-following approach still performs far better in a broad market
  uptrend than in a choppy or declining one; run the identical regime
  scorecard before generating ideas)
□ User's understanding that this approach has NO fixed target and requires
  discipline to hold through normal pullbacks that do not breach the
  trailing stop — confirm this fits the user's temperament before proceeding
  (a user who wants defined, predictable exits is better served by
  AI_Swing_Trading_Skill instead)
□ Timeframe for trend definition: daily (shorter-duration trends, weeks to
  a few months) or weekly (longer-duration trends, several months to years)
□ Capital allocation intended for this style, distinct from swing/tactical
  capital per AI_Portfolio_Construction_Skill's Tier 4 framework
```

---

## Analysis Module 1 — Market Regime Filter

```
Identical gate structure to AI_Swing_Trading_Skill Module 1:
  Nifty 50 vs 200 DMA, market breadth, India VIX, FII activity.

RULE: Trend-following as a style has a structurally poor edge in a broad
market that is itself trendless or declining — most individual-stock
uptrends fail to sustain when the index itself is not trending up. Apply
the same STOP conditions as the Swing Trading Skill. In a Caution regime,
reduce new-idea count and tighten initial stop distances; existing open
trend positions already past their initial stop can continue to be
managed by their trailing stop regardless of regime (the regime filter
governs NEW entries, not the exit discipline for positions already trending).
```

---

## Analysis Module 2 — Trend Qualification Criteria

```
Step 2.1 — Primary Trend Definition (All Required)
  □ Price above the 50 DMA/WMA AND the 200 DMA/WMA (both, on the chosen
    timeframe), with the 50 above the 200 (established uptrend structure,
    not just a recent bounce)
  □ A pattern of higher highs and higher lows over the qualifying lookback
    (minimum 3 swing points confirming the structure, not just 1)
  □ 200 DMA/WMA itself sloping upward, not flat or declining (confirms the
    longer-term trend has genuinely turned, not just a short-term rally
    within a larger downtrend)

Step 2.2 — Strength Confirmation (Preferred, Strengthens Conviction)
  □ Relative strength vs. Nifty 50 also in a confirmed uptrend (the stock
    should be a market leader, not merely moving with a rising tide)
  □ New 52-week highs being made with reasonable regularity (a stock
    making fresh highs is, by definition, in unchallenged price discovery —
    there is no overhead supply of trapped sellers at higher prices)
  □ Volume pattern generally expanding on up-moves and contracting on
    pullbacks (healthy accumulation pattern)

Step 2.3 — Entry Timing Within a Qualified Trend
  □ Preferred entry: a pullback to a rising moving average (20 or 50
    DMA/WMA depending on timeframe) that holds without breaking trend
    structure, rather than chasing a stock extended far above its
    moving averages
  □ Acceptable alternative entry: a fresh breakout to new highs with
    volume confirmation, accepting a somewhat wider initial stop
  □ Avoid entry when price is extended more than ~15-20% above the
    50 DMA — wait for either a pullback or a basing period first
```

---

## Analysis Module 3 — The Trailing Stop Discipline (Core of This Skill)

```
This is the entire exit mechanism. There is no fixed target, no profit
booking schedule, and no discretionary "this looks like enough of a move"
exit under this skill — only the trailing stop.

Step 3.1 — Initial Stop-Loss (At Entry)
  → Placed below the most recent meaningful swing low, or below the
    moving average being used for the pullback entry, whichever gives a
    coherent technical reason — NOT an arbitrary fixed percentage
  → Position size is set using this initial stop distance via the same
    risk-based formula as the Swing Trading Skill (Risk% of capital ÷
    entry-to-stop distance)

Step 3.2 — Trailing Mechanism (Progressive, Mechanical, Non-Discretionary)
  As the trend progresses, the stop is raised — NEVER lowered — using one
  of these mechanical rules (state which is being used, applied consistently
  for the life of the position, not switched opportunistically):

  METHOD A — Moving Average Trail:
    Trail the stop below the rising 20 DMA (shorter-duration, tighter,
    more trades/whipsaws) or 50 DMA (longer-duration, looser, fewer
    whipsaws but gives back more profit on the eventual reversal)

  METHOD B — Swing Low Trail:
    Trail the stop below each new confirmed higher swing low as the
    uptrend's price structure creates one — inherently adapts to the
    stock's own volatility rather than a fixed indicator

  METHOD C — ATR-Based Trail (Volatility-Adjusted):
    Trail the stop at a multiple (commonly 2-3x) of Average True Range
    below the highest close achieved since entry — automatically widens
    in volatile names and tightens in calm ones

  → Once a method is selected for a given position, use it consistently
    for that position's entire life. Do not switch methods mid-trade to
    rationalize staying in past what the original method would have exited.

Step 3.3 — Breakeven Protection
  Once the position has moved favorably by an amount equal to roughly the
  initial risk (a 1:1 move), raise the stop to at minimum breakeven —
  this ensures a qualifying trend-follow trade, once it has shown initial
  confirmation, cannot turn into a net loss from that point forward.

Step 3.4 — No Fixed Target, By Design
  □ Claude must NOT state a target price for a position under this skill.
  □ If asked "where should I book profit," the correct answer under this
    skill's discipline is: "This method has no fixed target — the position
    is held as long as the trend holds and the trailing stop is not hit.
    The trailing stop is the exit mechanism, not a price prediction."
  □ Partial profit-booking is permissible ONLY if explicitly pre-defined
    by the user as part of their plan before entry (e.g., "I will trim
    25% after a 50% gain, and trail the rest") — this must be stated as a
    user-chosen modification, not a default recommendation, since it
    partially reintroduces the "cut winners short" behavior this method
    is designed to avoid.
```

---

## Analysis Module 5 — Pyramiding Protocol (Adding to Winners) (v1.1 Addition)

```
The original skill defined a single entry and a trailing exit but did not
address adding to a working position - a natural extension of "let winners
run" that, done without discipline, can undermine the risk-based sizing
this skill otherwise enforces. This module makes pyramiding explicit and
bounded rather than discretionary.

QUALIFYING CONDITIONS (All Required Before Adding):
  □ The position is already profitable and the stop has been moved to at
    least breakeven (per Module 3, Step 3.3) - never pyramid a position
    still at initial risk
  □ The stock has made a fresh higher high with the same trend-qualification
    criteria (Module 2) still fully intact, not merely "still above the
    stop" - the add should be justified by the SAME quality of setup as
    the original entry, not a lower bar
  □ Confluence score from AI_Technical_Analysis_Master_Skill Module 7 for
    the add-on entry is at least as strong as it was at initial entry

ADD-ON SIZING RULE:
  □ Each subsequent add uses the SAME risk-based formula as the initial
    entry (Risk% of capital / entry-to-new-stop distance), calculated
    independently for that tranche - never simply double the original
    share count without recalculating risk
  □ Each add-on tranche should be smaller than the previous one (a common
    convention: 100% initial size, 50% first add, 25% second add) - this
    keeps the average cost basis closer to the trend's realized gains and
    limits how much fresh capital is exposed at any single price level
  □ Maximum of 2 add-on tranches per position - beyond this, the position's
    total size risks breaching the portfolio-level ceilings in AI_Portfolio_
    Construction_Skill even if each individual add was independently
    risk-sized correctly

STOP MANAGEMENT AFTER AN ADD:
  □ The trailing stop for the ENTIRE combined position (original + adds)
    moves to whichever level the chosen trailing method (Module 3.2)
    dictates for the position as a whole - do not maintain separate stops
    for each tranche, which would contradict the "hold until trend fails"
    discipline this skill is built around
  □ An add-on tranche NEVER lowers the effective stop level below where it
    already stood for the original position
```


## Analysis Module 4 — Trend Failure and Re-Entry

```
□ Trend failure (stop hit) is treated as simply the trend ending for now —
  not as evidence the analysis was wrong. Trend-following inherently means
  accepting a lower win rate in exchange for letting winners run further
  than a fixed-target method would; this must be explained to the user
  so a stopped-out position is not treated as a "mistake" to be second-guessed
□ Re-entry is permitted if the stock re-qualifies under Module 2's full
  criteria again later — there is no rule against re-entering a name that
  was previously stopped out, provided the trend structure has genuinely
  reformed and is not just a bounce within the same failed structure
□ Track the historical win rate and average winner-vs-average-loser ratio
  for the user's trend-following positions over time if data is available —
  this method's viability depends on winners being meaningfully larger than
  losers on average, since the win rate itself is typically well below 50%
```

---

## Analysis Module 5 — Gap Risk and Corporate Action Adjustment (Upgrade — Previously Missing)

```
□ A trailing stop is an intended exit level, not a guaranteed one — a
  stock can gap through the stop on adverse news/weak open, especially
  around results inside a long-held trend position. State this risk
  explicitly whenever a position is held through a scheduled event without
  a pre-event size reduction
□ Corporate Actions (bonus/split/dividend): when any of these occur mid-
  trade, ALL reference levels — initial stop, trailing stop, moving
  averages used for the trail — must be adjusted by the same ratio/amount
  as the price adjustment on the ex-date. Failing to adjust the stop
  produces a false trigger (a stop that appears hit due to the mechanical
  price drop, not an actual trend failure) — this is a common, avoidable
  error and must be checked explicitly whenever a corporate action is
  announced for an open position
```

## Red Flag Summary — Uptrend Momentum Context

### CRITICAL Flags
```
❗ A fixed target price being stated or implied for a position under this
  skill (contradicts the method's core discipline)
❗ Market regime STOP condition active for new entries (same gate as
  Swing Trading Skill)
❗ Trailing stop being moved DOWN or removed to avoid taking a loss —
  never permitted under any circumstance
❗ Entry taken on a stock extended more than 20% above its 50 DMA with
  no pullback or basing structure
```

### HIGH Flags
```
⚠️ Trailing stop method switched mid-position to rationalize staying in
  a weakening trend past where the original method would have exited
⚠️ Position sizing not based on the initial stop distance (risk-based formula)
⚠️ Relative strength vs. Nifty deteriorating while price is still nominally
  above moving averages (early warning the trend may be losing leadership status)
⚠️ Partial profit-booking being defaulted into the plan without the user
  having explicitly pre-chosen this modification
```

---

## Output Format

```
UPTREND MOMENTUM ANALYSIS
Date: [DD/MM/YYYY] | Regime Score: [X/8] | Regime Verdict: [Favorable/Caution/Not Favorable]
Timeframe: [Daily/Weekly] | Trail Method: [A-Moving Average / B-Swing Low / C-ATR]
═══════════════════════════════════════════════════════════════════

MARKET REGIME: [Same scorecard structure as Swing Trading Skill]

──────────────────────────────────────────────────────
TREND CANDIDATE #[N]
──────────────────────────────────────────────────────
Company:            [Name] | Ticker: [NSE] | Sector: [Sector]

TREND QUALIFICATION:
  Above 50 & 200 DMA/WMA:     [Yes — 50 above 200]
  Higher Highs/Higher Lows:    [Confirmed, [X] swing points]
  200 DMA/WMA Slope:           [Rising]
  Relative Strength vs Nifty:  [Confirmed uptrend / Neutral / Weakening]
  52-Week Highs:                [Regular / Occasional / None yet]

ENTRY:
  Type:               [Pullback to rising MA / Fresh breakout]
  Entry Zone:          ₹[X] – ₹[Y]
  Initial Stop-Loss:   ₹[Z] — [Below swing low / Below MA — specific reason]
  Initial Risk:         [X]% from entry
  Position Size:        [X]% of portfolio — Risk: [X]% of total capital

TRAILING STOP PLAN:
  Method:              [A/B/C — as selected, applied consistently]
  Breakeven Trigger:    [Price level equal to ~1:1 initial risk move]
  Current Trailing Stop (if position open): ₹[X]

TARGET: None — position held as long as trend and trailing stop discipline
  permit. No profit ceiling is set under this method.

TREND HEALTH MONITORING:
  Volume Pattern:       [Expanding on advances / Contracting on pullbacks]
  Warning Signs:         [Any — e.g., relative strength weakening, or "None"]
──────────────────────────────────────────────────────

[Repeat per idea]

PORTFOLIO-LEVEL NOTE:
  Trend-following capital allocation: [X]% of portfolio (Tier 4-adjacent,
  per AI_Portfolio_Construction_Skill — track separately from swing/tactical)

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]
```

---

## Rules (Non-Negotiable)

```
1. No fixed target price is ever stated for a position under this skill —
   the trailing stop is the exit mechanism, by design.
2. The trailing stop is only ever raised, never lowered or removed, for
   any reason.
3. The trailing stop method selected for a position is used consistently
   for that position's full life — no switching methods mid-trade.
4. Position sizing is always risk-based, tied to the initial stop distance,
   never a round-number allocation disconnected from the stop.
5. A stopped-out trend position is treated as a normal, expected outcome of
   the method's lower win rate — not evidence the entry analysis was flawed.
6. Market regime gate applies to new entries using the same STOP conditions
   as AI_Swing_Trading_Skill.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Style Specialist — Uptrend Momentum (Trend-Following)*
*Integrates with: AI_Swing_Trading_Skill (shares regime filter, distinct exit philosophy),
AI_Portfolio_Construction_Skill (Tier 4 tactical capital), Skill 08 (Sector Rotation Analyzer)*

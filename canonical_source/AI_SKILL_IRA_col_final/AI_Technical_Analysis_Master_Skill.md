<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Technical Analysis Master Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Technical Analysis Master Skill
**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Core Toolkit — Reusable Indicator & Chart-Pattern Engine

---

## CRITICAL AI INSTRUCTION

This skill is a **shared toolkit**, not a standalone trading strategy. Every other skill in the library that references "technical setup," "RSI," "trend," or "volume confirmation" (Swing Trading, Uptrend Momentum, Positional Opportunity Finder, Sector Rotation) calls into THIS skill for the actual indicator math and interpretation rules, so that indicator logic is defined once, consistently, and never re-invented differently in different places. Claude must never let an indicator reading stand alone as a signal — every technical read in this skill is deliberately paired with a required confirmation (volume, a second indicator, or price structure) because single-indicator signals in isolation have a materially higher false-positive rate than confirmed multi-factor reads. An RSI reading without a trend/volume context is noise, not a signal.

---

## Purpose

Provide a single, consistent, well-specified toolkit of technical indicators, oscillators, and chart-pattern definitions — RSI, MACD, Bollinger Bands, moving averages, volume/OBV, and standard chart patterns — with explicit calculation conventions, interpretation thresholds, and mandatory confirmation rules, so every other skill in the library reads technical evidence the same way.

---

## Pre-Flight Requirements

```
□ Timeframe explicitly stated before any read (intraday/daily/weekly) —
  every indicator behaves differently by timeframe; a "bullish RSI" on a
  5-minute chart and a "bullish RSI" on a weekly chart are not comparable
  and must never be blended into one conclusion
□ Sufficient historical price/volume data for the indicator's lookback
  (state the lookback explicitly per indicator, per Module 1)
□ Confirm which calling skill/context this analysis feeds into (Swing,
  Positional, Uptrend, Sector Rotation) — the confirmation bar and
  actionability threshold differ by intended use
```

---

## Analysis Module 1 — Moving Averages

```
STANDARD PERIODS USED ACROSS THE IERL LIBRARY:
  20 EMA  — short-term trend / pullback entry reference (Swing, Uptrend)
  50 DMA/EMA — medium-term trend filter (all skills)
  200 DMA — primary long-term trend definition (regime filter, Uptrend)

INTERPRETATION RULES:
  Price > 50 DMA > 200 DMA, both sloping up   → Confirmed uptrend structure
  Price < 50 DMA < 200 DMA, both sloping down → Confirmed downtrend structure
  Moving averages tightly bunched/crossing repeatedly → Choppy/trendless —
    lower confidence in ANY trend-following signal during this condition
  Golden Cross (50 crosses above 200):  → Lagging confirmation signal, not
    an early one — often arrives after much of an initial move has occurred;
    treat as trend CONFIRMATION, never as an entry trigger by itself
  Death Cross (50 crosses below 200):   → Same caveat in reverse — lagging
    warning, not a precise exit-timing tool by itself

MANDATORY PAIRING: A moving-average trend read must always be stated
alongside the SLOPE of the longer average (flat vs. rising/falling) — price
being technically "above the 200 DMA" while the 200 DMA itself is flat or
declining is a materially weaker signal than the same price position with
a rising 200 DMA, and must be labeled distinctly, not both called "uptrend."
```

---

## Analysis Module 2 — RSI (Relative Strength Index)

```
STANDARD SETTING: RSI(14), unless the calling context specifies otherwise
(state the period explicitly if not 14).

INTERPRETATION BANDS:
  > 70   → Overbought zone — elevated risk of a pullback, NOT an automatic
           sell signal by itself (strong trends can stay overbought for
           extended periods; this is a caution flag, not a standalone trigger)
  50–70  → Bullish momentum zone — the "sweet spot" the Swing Trading Skill
           screens for (momentum building, room before overbought)
  30–50  → Bearish-leaning / neutral-weak zone
  < 30   → Oversold zone — elevated risk of a bounce, NOT an automatic buy
           signal by itself (a stock can be oversold and continue falling
           in a genuine downtrend — "oversold" describes momentum
           exhaustion risk, not a floor guarantee)

DIVERGENCE (Higher-Value Signal Than the Raw Level):
  Bullish Divergence: price makes a lower low, RSI makes a higher low
    → Early signal of weakening downside momentum — requires price
      confirmation (a subsequent higher high) before being treated as
      an actionable reversal signal, not acted on at the divergence alone
  Bearish Divergence: price makes a higher high, RSI makes a lower high
    → Early signal of weakening upside momentum — requires a subsequent
      break of trend structure (e.g., a break below the prior swing low
      or a rising moving average) before being treated as actionable

MANDATORY PAIRING: RSI must always be read alongside volume and, where
relevant, the moving-average trend context — a 65 RSI reading on rising
volume within a confirmed uptrend (Module 1) is a materially different
signal than a 65 RSI reading on declining volume within a choppy market,
even though the raw RSI number is identical. Never report an RSI level
in isolation as "bullish" or "bearish" without this context.
```

---

## Analysis Module 3 — MACD (Moving Average Convergence Divergence)

```
STANDARD SETTING: 12, 26, 9 (fast EMA, slow EMA, signal line), unless
calling context specifies otherwise.

INTERPRETATION RULES:
  MACD line crosses above Signal line       → Bullish crossover (lagging,
                                                confirmation-style signal)
  MACD line crosses below Signal line       → Bearish crossover
  MACD Histogram expanding (growing bars)    → Momentum accelerating in the
                                                current direction
  MACD Histogram contracting (shrinking bars)→ Momentum decelerating — an
                                                early warning ahead of an
                                                eventual crossover, useful
                                                for tightening a trailing stop
                                                (Uptrend Momentum Skill) even
                                                before the crossover confirms
  MACD Divergence (same logic as RSI divergence in Module 2) → Early
    momentum-exhaustion warning, requires price confirmation before acting

CAUTION: MACD crossovers are inherently lagging (both inputs are already-
smoothed moving averages of price). In choppy/range-bound markets, MACD
crossovers generate a materially higher false-signal rate — cross-check
Module 1's trend structure before treating any MACD crossover as actionable,
and explicitly downgrade confidence in a ranging market.
```

---

## Analysis Module 4 — Bollinger Bands

```
STANDARD SETTING: 20-period moving average, ±2 standard deviations, unless
calling context specifies otherwise.

INTERPRETATION RULES:
  Price touching/exceeding upper band       → Statistically extended to the
    upside — in a STRONG trend this can mean "riding the band" (healthy
    trend continuation), NOT automatically overbought — distinguish this
    from a range-bound market where an upper-band touch is more often a
    reversal signal; state which regime applies (per Module 1) before interpreting
  Price touching/exceeding lower band        → Mirror logic, downside
  Band Squeeze (bands narrowing to a multi-month low width) → Volatility
    contraction — historically often precedes a significant directional
    move, but the squeeze itself gives NO directional information; do not
    imply a direction from the squeeze alone, wait for the breakout direction
  Band Expansion (bands widening rapidly)     → Volatility expansion,
    typically confirms a move already underway rather than predicting one

MANDATORY PAIRING: A Bollinger Band signal must always be paired with the
trend-regime context from Module 1 (trending vs. ranging) before
interpretation, since the same band-touch event means opposite things in
each regime — this is one of the most commonly misapplied indicators when
used without this pairing.
```

---

## Analysis Module 5 — Volume and On-Balance Volume (OBV)

```
CORE PRINCIPLE: Volume is the confirmation layer for every other indicator
in this skill — a price or oscillator signal without volume confirmation
is treated as lower-confidence throughout this entire skill, not just in
this module.

VOLUME INTERPRETATION:
  Rising price + rising volume               → Healthy, well-supported move
  Rising price + falling volume               → Weakening participation —
    caution flag on trend sustainability, even if price structure still
    looks intact
  Falling price + rising volume               → Strong distribution/selling
    pressure — a more urgent bearish signal than a price decline on light volume
  Falling price + falling volume               → Often a low-conviction
    pullback within an intact trend, rather than a reversal — but must be
    distinguished from genuine "quiet distribution," which requires the
    On-Balance Volume cross-check below

ON-BALANCE VOLUME (OBV):
  OBV making new highs alongside price new highs   → Confirms trend, volume
    is supporting the move
  Price making new highs while OBV fails to confirm (lower high on OBV)
    → Bearish divergence — volume is not supporting the price advance,
    an early warning sign even while price structure still looks intact
  Mirror logic applies for downtrends and bullish OBV divergence

BREAKOUT-SPECIFIC VOLUME RULE (feeds directly into Swing/Uptrend Skills):
  A breakout from a base/consolidation is only treated as "confirmed" if
  volume on the breakout session/week is at least 1.5x the prior 20-period
  average — a breakout on average or below-average volume is flagged as
  UNCONFIRMED and should be sized smaller or watched for a retest rather
  than treated as a full-conviction entry trigger.
```

---

## Analysis Module 6 — Standard Chart Patterns

```
CONTINUATION PATTERNS (favor the pre-existing trend continuing):
  Flag / Pennant:        Short, tight consolidation after a sharp move,
                           typically resolves in the direction of the
                           prior move — requires the prior move to be a
                           genuine sharp advance, not a slow grind, to qualify
  Ascending Triangle:      Flat resistance, rising support — bullish
                           continuation bias, breakout confirmation via
                           Module 5's volume rule required
  Cup and Handle:          Rounded base (cup) followed by a shorter, tighter
                           consolidation (handle) — breakout above the
                           handle's resistance with volume confirmation is
                           the actionable trigger, not the cup formation alone

REVERSAL PATTERNS (signal a potential trend change — require more
confirmation than continuation patterns before acting):
  Head and Shoulders (Top):  Three peaks, middle highest, neckline break
    with volume confirmation required before treating as confirmed
    (an unbroken neckline means the pattern is not yet valid, regardless
    of how clearly the three peaks are visible)
  Double Top / Double Bottom: Two comparable extremes with a confirmed
    break of the intervening support/resistance level, plus volume
    confirmation on the break
  Rounding Top / Bottom:       Gradual, longer-duration reversal — lower
    urgency signal, typically relevant to Positional/longer-horizon
    contexts rather than short-duration Swing trades

MANDATORY RULE: No chart pattern is treated as "confirmed" until its
specific breakout/breakdown trigger level is actually breached WITH volume
confirmation per Module 5. A pattern that "looks like" a setup but has not
yet triggered is described as "forming" or "developing," never as an
actionable signal.
```
--
	ADDITIONAL PATTERN CLASSES (Taxonomy Extension):

DISTRIBUTION PATTERNS (smart-money exit signature, distinct from a
  reversal pattern -- often precedes one):
  High volume on price declines, low volume on rallies, lower highs
  forming while price still appears range-bound -- classify as
  "Distribution" even before a clean reversal pattern completes.

ACCUMULATION PATTERNS (mirror of Distribution):
  High volume on price advances, low volume on declines, higher lows
  forming within an apparent range -- classify as "Accumulation," a
  leading indicator ahead of a confirmed breakout.

VOLATILITY PATTERNS:
  Bollinger Band squeeze (Module 4) preceding a directional move --
  classify direction only after the breakout, not during the squeeze
  itself, consistent with the existing "forming vs actionable" rule.

FAILED PATTERNS:
  A pattern that triggers (breaches its level with volume per Module 5)
  but reverses back within 1-3 sessions -- classify explicitly as
  "Failed Pattern" and treat as a bearish/bullish signal in the OPPOSITE
  direction of the original pattern, not simply as "no signal."

PATTERN RELIABILITY & MATURITY:
  New pattern (first occurrence in the visible data window) -> lower
  reliability weight in the Module 7 confluence score
  Pattern that has played out successfully within the same trend
  earlier in the dataset -> higher reliability weight
  A pattern late in an extended trend (post-ADX>40 exhaustion warning
  per Module 8) carries elevated invalidation risk -- flag explicitly
---

## Analysis Module 6B — Horizontal Support/Resistance and Timeframe Conflict Resolution (Upgrade — Previously Missing)

```
Two gaps in the original toolkit: price-history-based S/R (distinct from
moving-average or Bollinger-based levels) and what to do when timeframes disagree.

HORIZONTAL SUPPORT/RESISTANCE:
□ Identify prior significant swing highs/lows and high-volume price zones
  on the relevant timeframe — these act as memory levels where past buyers/
  sellers are likely to react again, independent of any indicator
□ A level is stronger with more historical touches and higher volume at
  that zone; a level touched only once carries materially lower weight
□ Cross-reference with OI-based strikes from AI_Options_Data_Skill (Module
  2 there) when the name is F&O-active — convergence of a horizontal level
  and a high-OI strike is a stronger combined zone than either alone

MULTI-TIMEFRAME CONFLICT RESOLUTION:
□ When the daily and weekly trend reads disagree (e.g., daily uptrend
  within a weekly downtrend, or vice versa), the LONGER timeframe governs
  the default bias; the shorter timeframe read is treated as a tactical/
  counter-trend signal only, sized smaller and held for a shorter duration
  than a fully-aligned multi-timeframe setup
□ State BOTH timeframe reads explicitly whenever they conflict — never
  report only the timeframe that supports the conclusion being presented
```

## Analysis Module 7 — Multi-Indicator Confluence Scoring

```
For any technical read feeding into another skill, score confluence rather
than reporting single indicators in isolation:

  Trend (Module 1):            Aligned / Neutral / Against
  Momentum (RSI + MACD):        Aligned / Neutral / Against
  Volatility Context (Bollinger):Trending-regime / Ranging-regime
  Volume Confirmation (Module 5): Confirmed / Unconfirmed
  Pattern Trigger (Module 6):    Triggered / Forming / None

CONFLUENCE VERDICT:
  4-5 factors aligned   → High-confidence technical read
  2-3 factors aligned   → Moderate-confidence — state which factors disagree
  0-1 factors aligned   → Low-confidence / Do not treat as actionable
    regardless of how compelling any single indicator looks in isolation

This scoring output is what Swing Trading, Uptrend Momentum, and Positional
Opportunity Finder should request from this skill, rather than pulling a
single indicator reading directly.
```

---

## Analysis Module 8 — ADX (Trend Strength) and Fibonacci Retracement (v_0.0 Addition)

```
ADX (AVERAGE DIRECTIONAL INDEX):
  Standard setting: ADX(14). Unlike the directional indicators in Modules
  1-4, ADX measures TREND STRENGTH only - it does not indicate direction.
  This is the missing piece that resolves a common failure mode: applying
  trend-following rules (Uptrend Momentum Skill) or mean-reversion reads
  (Bollinger Band ranging-regime logic) to a market that is actually
  directionless.

  ADX < 20          -> Weak or absent trend - Bollinger Band ranging-regime
                        interpretation applies with higher confidence;
                        trend-following entries (Uptrend Momentum Skill)
                        should be deferred until ADX rises
  ADX 20-25          -> Trend developing - moderate confidence in trend
                        continuation reads
  ADX > 25            -> Established trend - trend-following signals
                        (Module 1 moving average structure, MACD crossovers)
                        carry materially higher confidence; this is the
                        regime the Uptrend Momentum Skill is best suited for
  ADX > 40             -> Strong trend, but also watch for trend EXHAUSTION -
                        an ADX that has been above 40 for an extended period
                        and begins rolling over is an early warning the
                        trend's strength is peaking, even while price is
                        still making new highs

  MANDATORY PAIRING: ADX should be checked BEFORE applying Module 1's trend
  structure or Module 4's Bollinger regime classification - it is the gate
  that determines which interpretation framework is appropriate, not an
  independent signal to be read in isolation.

FIBONACCI RETRACEMENT:
  Standard levels: 23.6%, 38.2%, 50%, 61.8%, 78.6%, drawn from a clearly
  defined swing low to swing high (or vice versa for a downtrend).

  USE CASE: identifying probable pullback-entry zones within an already-
  confirmed uptrend (Module 1) - NOT for predicting reversals in the
  absence of other confirmation.

  INTERPRETATION:
  - 38.2%-50% retracement holding, within a confirmed uptrend (Module 1 +
    ADX > 25) -> Higher-probability pullback-entry zone, consistent with
    the "preferred entry" logic in the Swing Trading and Uptrend Momentum
    Skills' pullback-to-moving-average criteria
  - 61.8%-78.6% retracement -> Deeper pullback, requires the trend structure
    (higher-high/higher-low pattern) to still be technically intact; if this
    level is breached with a lower low forming, treat the uptrend
    classification itself as under threat, not merely "a deep pullback"

  MANDATORY PAIRING: A Fibonacci level is never used as a standalone entry
  trigger - it must coincide with a moving-average support level (Module 1)
  or a volume-confirmed reaction (Module 5) to be treated as an actionable
  zone, per the same confluence-scoring discipline as every other tool in
  this skill.
```


## Red Flag Summary — Technical Analysis Context

### CRITICAL Flags
```
❗ Any single indicator (RSI, MACD, a chart pattern) being reported as an
  actionable signal without the mandatory pairing/confirmation specified
  in its module
❗ A breakout/breakdown pattern treated as "confirmed" without volume
  confirmation per Module 5's 1.5x rule
❗ Timeframe not stated before an indicator read (e.g., mixing a daily
  RSI reading into a weekly-timeframe trend conclusion)
```

### HIGH Flags
```
⚠️ MACD crossover treated as high-confidence in a choppy/ranging market
  without the Module 1 trend-regime check
⚠️ Bollinger Band touch interpreted as overbought/oversold without first
  establishing trending vs. ranging regime
⚠️ Divergence (RSI/MACD/OBV) treated as an immediate action trigger rather
  than an early-warning requiring subsequent price confirmation
```

---

## Output Format

```
TECHNICAL READ
Company: [Name] | Ticker: [NSE] | Timeframe: [Daily/Weekly] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

TREND (Moving Averages):
  Structure:          [Price vs 20/50/200 — aligned uptrend/downtrend/choppy]
  200 DMA Slope:       [Rising/Flat/Falling]

MOMENTUM:
  RSI(14):             [Reading] — [Band] — Divergence: [None/Bullish/Bearish
                        — confirmed by price / not yet confirmed]
  MACD:                [Above/Below Signal] — Histogram: [Expanding/Contracting]
                        — Divergence: [None/Bullish/Bearish]

VOLATILITY CONTEXT (Bollinger Bands):
  Regime:              [Trending/Ranging]
  Band Position:        [Riding upper/lower band / Mid-band / Squeeze]

VOLUME:
  Price-Volume Relationship: [Healthy/Weakening/Distribution warning]
  OBV Confirmation:           [Confirmed/Diverging]

CHART PATTERN:
  Pattern Identified:   [Name, or "None"]
  Status:                [Triggered with volume confirmation / Forming — not
                          yet actionable / None]

CONFLUENCE SCORE: [X/5 factors aligned] — [High/Moderate/Low confidence]

FEEDS INTO: [Which calling skill this read supports — Swing/Uptrend/Positional/
  Sector Rotation — and what threshold that skill requires]
```

---

## Rules (Non-Negotiable)

```
1. No single indicator is ever reported as an actionable signal without
   its mandatory pairing/confirmation.
2. Timeframe must be stated before every indicator read; readings across
   different timeframes are never blended into one conclusion.
3. Breakout/breakdown patterns require volume confirmation (≥1.5x 20-period
   average) before being called "confirmed" rather than "forming."
4. Divergence signals (RSI/MACD/OBV) require subsequent price confirmation
   before being treated as actionable, not acted on at the divergence itself.
5. Every technical read delivered to another skill includes the Module 7
   confluence score, not just a single headline indicator. 6. Any actionable signal (Confluence Score of Moderate or High per Module 7)
   must state: Entry level, Stop level (nearest invalidation point — e.g.,
   below the recent swing low or below the triggering support/moving-average
   level), Target (nearest resistance or Fibonacci level per Module 8), and
   Risk/Reward Ratio = (Target - Entry) / (Entry - Stop). A setup with R:R
   below 1.5 is flagged "poor risk/reward — size accordingly if taken at all."


```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Core Toolkit — Technical Analysis*
*Integrates with: AI_Swing_Trading_Skill, AI_Uptrend_Momentum_Stock_Skill, Skill 03 (Positional
Opportunity Finder), Skill 08 (Sector Rotation Analyzer), AI_Volume_Delivery_Analysis_Skill*
# Technical Analysis — Data Input Template (Addendum v_0.0)

**Paste Target:** AI_Technical_Analysis_Master_Skill.md — insert as new "Pre-Flight Data Requirements" section, right after the existing "Pre-Flight Requirements"

---

## Why This Addendum Exists

This skill already has full indicator logic (Moving Averages, RSI, MACD, Bollinger Bands, OBV, ADX, Fibonacci — Modules 1–8). What it never specified was **exactly what data the user needs to paste in** for the AI to actually compute these — without a live price feed, the AI can only be as good as the numbers it's given. This addendum closes that gap. It does not add new indicator logic; it makes the existing logic usable.

---

## Minimum Data Required (Paste This In Before Requesting Technical Analysis)

For a **single-timeframe** analysis (e.g., daily chart only), provide:

```
Stock: [Name/Ticker]
Timeframe: [Daily / Weekly / Intraday]
Date Range: [At least 60 trading periods — 200+ preferred for 200-DMA]

OHLCV data (one row per period), minimum:
Date | Open | High | Low | Close | Volume

Example:
2026-07-01 | 1420 | 1435 | 1415 | 1428 | 3,200,000
2026-07-02 | 1428 | 1440 | 1422 | 1432 | 2,850,000
...
```

**Minimum period counts needed per indicator** (so the AI can tell you if your data is insufficient before running an incomplete analysis):

| Indicator | Minimum Periods Needed |
|---|---|
| 20-DMA / 50-DMA | 50 (for 50-DMA to be valid) |
| 200-DMA | 200 |
| RSI (14) | 15 |
| MACD (12,26,9) | 35 |
| Bollinger Bands (20,2) | 20 |
| ADX (14) | 28 (needs a warm-up period beyond the base 14) |
| Fibonacci Retracement | 1 clear swing high + 1 clear swing low (no minimum count, but must be visually/numerically identifiable in the data provided) |

**Rule:** If the data provided is shorter than an indicator's minimum, the AI states explicitly "insufficient data for [indicator] — need at least N periods" rather than computing an unreliable value silently.

---

## For Multi-Timeframe Confluence (Module 6B — Timeframe Conflict Resolution)

Provide OHLCV for **each** timeframe being compared (e.g., both Daily and Weekly), clearly labeled. The AI cannot infer a weekly trend from daily data alone with full reliability — always provide each timeframe's data separately if multi-timeframe analysis is requested.

---

## Where To Get This Data

This skill does not fetch data itself. Common sources: your broker's historical data export (Zerodha Kite, Upstox, etc.), NSE/BSE historical data downloads, or a financial data site's CSV export. Paste the relevant rows directly into the chat, or upload as a CSV/spreadsheet file.

---

## What This Does Not Fix

This addendum makes the existing indicator modules usable with pasted historical data. It does **not** provide live/real-time price updates, live order book depth, or automatic data retrieval — those require a connected market-data source (broker API or data connector), which is outside what any document in this project can do on its own.

---

## Self-Audit

- ✓ No new indicator logic added — Modules 1–8 remain the single source of truth for calculation methodology
- ✓ Does not overstate capability — explicitly states the live-data limitation rather than implying it's solved
- ✓ Gives the user a concrete, actionable template rather than a vague "provide price data" instruction

---

**Document:** Technical_Analysis_Data_Input_Template_v_0.0.md
**Version:** v_0.0
**Paste Into:** AI_Technical_Analysis_Master_Skill.md (after Pre-Flight Requirements)


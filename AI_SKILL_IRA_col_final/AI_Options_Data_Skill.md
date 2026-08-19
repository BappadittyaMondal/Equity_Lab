<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Options Data Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Options Data Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Core Toolkit — Open Interest, PCR, and Options-Derived Sentiment Analysis

---

## CRITICAL AI INSTRUCTION

Options data tells Claude about POSITIONING and SENTIMENT among derivatives participants — it does not tell Claude anything directly about a company's fundamental value, and it must never be used as a valuation input. Its correct use is as a sentiment/positioning overlay on top of technical and fundamental work, primarily useful for short-duration contexts (Swing Trading) and for identifying where large concentrations of market participants have a stake in a specific price outcome (which can itself influence near-term price behavior around those levels). Claude must never treat options data as available for or relevant to any small/micro-cap company without active, liquid F&O contracts — most of the IERL universe (per AI_Microcap_Research_Skill and much of Skill 04) has no F&O contract at all, and this skill simply does not apply there.

---

## Purpose

Provide a dedicated toolkit for reading options market data — Open Interest (OI), Put-Call Ratio (PCR), OI concentration by strike, Implied Volatility (IV), and Max Pain — to extract sentiment and near-term positioning signals for F&O-enabled stocks and indices, strictly as a supplementary overlay to technical and fundamental analysis, never as a standalone basis for a trade or investment decision.

---

## Pre-Flight Requirements

```
□ Confirm the stock/index has active, liquid F&O contracts — if not,
  state explicitly that this skill does not apply and no options-based
  commentary should be generated for the name
□ Current expiry cycle context (weekly vs. monthly, and days remaining
  to expiry) — options signals behave very differently in the final days
  before expiry versus early in a fresh monthly cycle
□ Open Interest data by strike, for both calls and puts, across at least
  the near-the-money and adjacent strikes
□ Implied Volatility data, ideally with a historical IV percentile/rank
  for context (a given IV number is only meaningful relative to that
  stock's own IV history)
□ Confirm whether the analysis is intended to support a short-duration
  (Swing Trading Skill) context or a broader market-regime sentiment read
  (feeds into the regime filter shared by Swing/Uptrend skills)
```

---

## Analysis Module 1 — Open Interest (OI) and OI Change Analysis

```
CORE PRINCIPLE: OI alone (a static number) is far less informative than
the CHANGE in OI combined with the price move on the same session —
this pairing is mandatory for any OI-based read.

PRICE-OI INTERPRETATION MATRIX (Mandatory Pairing):
  Price UP + OI UP        → Long Buildup — fresh bullish positions being
                              added, generally the highest-confidence
                              bullish OI signal
  Price UP + OI DOWN       → Short Covering — existing bearish positions
                              being closed, a bullish move but driven by
                              unwinding rather than fresh conviction —
                              distinguish explicitly from Long Buildup, as
                              short-covering rallies can reverse faster
                              once the covering is complete
  Price DOWN + OI UP        → Short Buildup — fresh bearish positions being
                               added, highest-confidence bearish signal
  Price DOWN + OI DOWN       → Long Unwinding — existing bullish positions
                               being closed, a bearish move but driven by
                               unwinding rather than fresh bearish conviction

□ Apply this matrix at both the STOCK level (aggregate futures OI) and,
  where relevant, at specific option STRIKES (Module 2) — the two can
  sometimes diverge and both should be reported if so
```

---

## Analysis Module 2 — OI Concentration by Strike (Support/Resistance Proxy)

```
□ Identify strikes with the HIGHEST call OI (often acts as a near-term
  resistance zone — large call writers have a stake in price staying
  below that strike through expiry) and the HIGHEST put OI (often acts
  as a near-term support zone, by mirror logic)
□ Track whether this OI concentration is SHIFTING toward higher/lower
  strikes as sessions pass — a shifting resistance strike (call OI
  migrating higher) can indicate building bullish conviction; a static or
  declining resistance strike suggests capped near-term upside expectations
□ CAUTION: these levels are a PROXY based on options writers' current
  positioning, not a guarantee — they can and do break, especially on
  strong fundamental news or outside the immediate pre-expiry window; state
  this explicitly whenever citing an OI-based support/resistance level,
  and note that this proxy is most reliable in the final 3-5 sessions
  before expiry and least reliable early in a fresh monthly cycle
```

---

## Analysis Module 3 — Put-Call Ratio (PCR)

```
PCR (OI-based) = Total Put OI / Total Call OI

INTERPRETATION (Contrarian-Leaning, Requires Context):
  PCR > 1.3-1.5   → Historically associated with oversold/bearish-extreme
                      sentiment — often read as a CONTRARIAN bullish signal
                      (excessive put positioning can precede a bounce), but
                      this is a probabilistic tendency, not a rule — must be
                      cross-checked against the broader trend/technical
                      context (AI_Technical_Analysis_Master_Skill) before
                      being treated as a signal
  PCR 0.7-1.0      → Broadly neutral positioning
  PCR < 0.6-0.7      → Historically associated with overbought/bullish-
                        extreme sentiment — often read as a CONTRARIAN
                        bearish signal, same caveats as above

□ Track PCR TREND over recent sessions, not just the current snapshot —
  a PCR rising rapidly toward an extreme is more informative than a PCR
  that has been stable at a moderate level for weeks
□ Distinguish index-level PCR (a broad market-regime sentiment input,
  can supplement the Swing Trading Skill's regime filter) from single-
  stock PCR (a narrower, name-specific positioning read) — never blend
  the two into one number or one conclusion
```

---

## Analysis Module 4 — Implied Volatility (IV) and IV Percentile

```
□ Report current IV alongside its percentile/rank versus the stock's own
  trailing 6-12 month IV range — an IV of 35% is high for a historically
  low-volatility stock and unremarkable for a historically high-volatility
  one; never interpret a raw IV number without this context
□ Rising IV ahead of a known event (results, corporate action) is normal
  and expected — distinguish this from IV rising WITHOUT an identifiable
  upcoming catalyst, which can itself be an early signal that informed
  participants are positioning for unexpected news
□ IV Crush: a sharp IV decline typically follows a known event's actual
  occurrence (e.g., results are announced) — relevant context for any
  options-strategy discussion, though this skill's core purpose is
  sentiment reading rather than options-strategy construction
```

---

## Analysis Module 5 — Max Pain (Use With Explicit Caveats)

```
Max Pain Theory: the strike price at which option writers (as a group)
would face the least aggregate payout at expiry — some market participants
believe price tends to gravitate toward this level into expiry.

□ Report Max Pain level if requested, but ALWAYS alongside an explicit
  caveat: this is a theory with mixed, inconsistent empirical support, is
  most (weakly) relevant only in the final 1-2 sessions before expiry, and
  should never be presented with the same confidence as the Price-OI
  matrix (Module 1) or PCR trend (Module 3), which have more consistent
  interpretive value
□ Never use Max Pain as a standalone basis for any trade recommendation
```

---

## Analysis Module 6 — F&O Ban Period Cross-Check (Upgrade — Previously Missing)

```
□ Before generating any options commentary, check whether the stock is
  currently in an exchange-mandated F&O ban period (triggered when
  aggregate market-wide position exceeds a regulatory threshold of open
  interest) — new positions cannot be initiated during a ban, only
  existing positions unwound
□ If in ban: state this explicitly, note that fresh OI-based signals
  (Module 1) are mechanically distorted (OI can only fall during a ban,
  making any "Long/Short Buildup" read unreliable for that period), and
  limit commentary to PCR/IV context only until the ban lifts
```

## Analysis Module 6 — Rollover Analysis at Monthly Expiry (v1.1 Addition)

```
Rollover data (the % of open positions carried forward from the expiring
monthly contract to the next month, plus the roll cost/premium) is a
distinct signal from the intra-cycle OI/PCR reads in Modules 1-3, and is
only available/meaningful in the final 3-5 sessions before monthly expiry.

ROLLOVER PERCENTAGE:
  □ Compare current rollover % against the stock's own 3-month average
    rollover % (never a fixed universal threshold, consistent with this
    skill's approach elsewhere)
  □ Rollover % meaningfully ABOVE average -> Participants are carrying
    conviction into the next cycle rather than closing out - supports
    continuation of the current positioning bias (bullish or bearish,
    per Module 1's Price-OI read) into the new month
  □ Rollover % meaningfully BELOW average -> Position unwinding into
    expiry rather than continuation - treat any OI-based directional
    read from Modules 1-2 with reduced confidence for the upcoming cycle,
    since the participants holding those positions are choosing not to
    carry them forward

ROLL COST (COST-OF-CARRY PREMIUM):
  □ A rollover executed at an unusually HIGH premium to fair value
    (cost-of-carry) suggests aggressive demand to maintain long exposure
    into the new cycle - a bullish positioning signal
  □ A rollover executed at a LOW or negative premium (backwardation)
    suggests the opposite - weak demand to carry the position forward

MANDATORY CONTEXT: Rollover analysis is only informative in the expiry
week itself - reporting a "rollover trend" outside this window is not
meaningful, since the underlying data does not exist until participants
begin actually rolling positions. State the days-to-expiry explicitly
whenever rollover data is presented, consistent with the expiry-proximity
caveats already required elsewhere in this skill (OI concentration, Max
Pain).
```


## Red Flag Summary — Options Data Context

### CRITICAL Flags
```
❗ Options-based commentary generated for a stock with no active, liquid
  F&O contract
❗ OI level (static) reported as a bullish/bearish signal without the
  mandatory Price-OI Change pairing from Module 1
❗ Options data (PCR, OI, Max Pain) being used as an input to a fundamental
  valuation or a long-duration (Multibagger/Turnaround-style) conviction
  rating — this skill's scope is short-duration sentiment/positioning only
```

### HIGH Flags
```
⚠️ PCR extreme reported as a signal without cross-checking the broader
  technical trend context first
⚠️ OI-based support/resistance level cited without noting it is a proxy
  that can break, and without stating proximity to expiry
⚠️ IV reported without its percentile/rank context against the stock's
  own historical range
⚠️ Max Pain presented with the same confidence level as Price-OI or PCR readings
```

---

## Output Format

```
OPTIONS DATA READ
Underlying: [Name] | Expiry: [Date, X days remaining] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

F&O ELIGIBILITY CHECK: [Confirmed active, liquid contract / NOT APPLICABLE
  — no active F&O contract, skill does not apply]

PRICE-OI READ (Futures, Aggregate):
  Price Move:          [+/-X]%  |  OI Change: [+/-X]%
  Classification:       [Long Buildup / Short Covering / Short Buildup /
                          Long Unwinding]

OI CONCENTRATION BY STRIKE:
  Highest Call OI Strike (Resistance Proxy): ₹[X] — [Static/Shifting higher/
    Shifting lower over recent sessions]
  Highest Put OI Strike (Support Proxy):      ₹[X] — [Same tracking]
  Proximity to Expiry:                          [X days — Higher/Lower
                                                  reliability of these levels]

PUT-CALL RATIO:
  Current PCR:          [X] | Recent Trend: [Rising/Falling/Stable]
  Reading:               [Neutral / Contrarian-Bullish extreme / Contrarian-
                          Bearish extreme]
  Cross-Check vs Technical Trend: [Aligned/Contradicts — per AI_Technical_
                                    Analysis_Master_Skill]

IMPLIED VOLATILITY:
  Current IV:            [X]% | Percentile vs own 6-12mo range: [X]th percentile
  Context:                [Event-driven rise expected/observed / Rise without
                            identifiable catalyst — flag]

MAX PAIN (If Requested):
  Level:                 ₹[X] — ⚠️ Low-reliability signal, most relevant only
                          in final 1-2 sessions before expiry; not used as a
                          standalone basis for any recommendation

OVERALL SENTIMENT OVERLAY: [Bullish/Bearish/Neutral positioning bias] —
  Supplementary to, never a substitute for, the technical (AI_Technical_
  Analysis_Master_Skill) and fundamental work already done on this name.

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]
```

---

## Rules (Non-Negotiable)

```
1. This skill applies only to stocks/indices with active, liquid F&O
   contracts — state explicitly and stop when this is not the case.
2. OI is never interpreted without the Price-OI Change pairing (Module 1's matrix).
3. Options data is never used as an input to fundamental valuation or a
   long-duration conviction rating — sentiment/positioning overlay only,
   and primarily relevant to short-duration (Swing Trading) contexts.
4. OI-based support/resistance and Max Pain levels are always presented
   with an explicit reliability caveat and proximity-to-expiry context.
5. IV is never reported without its percentile/rank against the stock's
   own historical range.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Core Toolkit — Options Data Analysis*
*Integrates with: AI_Swing_Trading_Skill, AI_Technical_Analysis_Master_Skill, AI_Volume_Delivery_Analysis_Skill*

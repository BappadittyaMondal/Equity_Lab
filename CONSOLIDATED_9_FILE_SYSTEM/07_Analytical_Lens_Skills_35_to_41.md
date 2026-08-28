# 06_Analytical_Lens_Skills_35_to_41

<!-- BEGIN SYSTEM FILE 10: AI_Options_Data_Skill.md | SHA256: 0cbf74e08253796a4cde2ad3f0c7237b3f6b14a10c43b573ee8b9346cc33a6e0 -->
## Embedded source 10: AI Options Data Skill

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
<!-- END SYSTEM FILE 10: AI_Options_Data_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 11: AI_Portfolio_Construction_Skill.md | SHA256: 956392fffa8ccf7af50df6737415ffdd09d8914ec370884d15f6204823ad8189 -->
## Embedded source 11: AI Portfolio Construction Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Portfolio Construction Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Portfolio Construction Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Portfolio Design, Sizing, and Allocation Architecture

---

## CRITICAL AI INSTRUCTION

Portfolio construction is the discipline that determines whether good individual stock-picking actually compounds into good outcomes. A portfolio of 15 excellent individual research reports, sized and combined carelessly, can still produce a poor investor experience — through unintended concentration, correlated drawdowns, or a risk profile the investor cannot emotionally sustain through a bad year. This skill's job is not to pick stocks; it is to architect how conviction, risk, liquidity, time horizon, and the investor's own behavioral limits combine into a portfolio that a real person can actually hold through a full market cycle. A portfolio the investor abandons at the bottom has a expected return of zero, regardless of how correct the underlying research was.

---

## Purpose

Design and audit portfolio structure — position sizing methodology, diversification architecture, conviction-to-allocation mapping, rebalancing discipline, and behavioral-capacity matching — so that a collection of individually sound ideas becomes a portfolio the investor can hold through both bull and bear phases without abandoning the plan at the worst possible moment.

---

## Pre-Flight Requirements

```
□ Total investable capital (or % breakdown if absolute figures withheld)
□ Investment horizon: overall portfolio purpose (retirement, wealth
  creation, specific goal with a date, trading capital)
□ Risk tolerance: stated AND behaviorally inferred (has the investor
  previously panic-sold in a downturn? this matters more than a stated
  "aggressive" self-label)
□ Existing holdings with allocation %, purchase price, purchase date
□ Cash flow pattern: lump sum available now, or recurring monthly
  additions (SIP-style)? This materially changes construction approach
□ Liquidity needs: any known near-term (within 3 years) cash requirement
  that should not be equity-exposed
□ Tax status of existing holdings (LTCG/STCG boundary awareness)
```

---

## Analysis Module 1 — Conviction-to-Allocation Mapping

```
Every position in the portfolio must trace to an explicit conviction tier,
and allocation must follow the tier — not the other way around (i.e., never
justify a large position after the fact by inflating conviction language).

TIER 1 — CORE HOLDING (High conviction, quality business, reasonable valuation):
  → Individual position: 5–8% of portfolio
  → Characteristics: Business Quality Score ≥7/10, Governance Score ≥7/10,
    multi-year thesis, low turnover expected
  → Maximum combined Tier 1 allocation: 40–55% of portfolio

TIER 2 — SATELLITE HOLDING (Good business, moderate conviction or earlier stage):
  → Individual position: 3–5%
  → Characteristics: solid fundamentals but shorter track record, or a
    Stage 2–3 multibagger candidate, or a positional/catalyst-driven idea
  → Maximum combined Tier 2 allocation: 25–35% of portfolio

TIER 3 — SPECULATIVE / EXPLORATORY (Early-stage, turnaround, high-uncertainty):
  → Individual position: 1–3% (per the relevant specialist skill's stage
    ceiling — Multibagger Discovery Stage 1, Turnaround T0–T1, etc.)
  → Maximum combined Tier 3 allocation: 10–15% of portfolio
  → This bucket exists explicitly to contain speculation so it cannot
    silently expand to dominate the portfolio

TIER 4 — TACTICAL / SWING (Short-duration technical trades):
  → Sized per the Swing Trading Skill's own risk-based formula
  → Maximum combined Tier 4 allocation at any time: 15–25% of portfolio,
    separate from and not competing with Tier 1–3 capital
  → Kept structurally distinct because the exit discipline (stop-loss,
    time-stop) differs fundamentally from long-duration holdings

CASH / LIQUID RESERVE:
  → Minimum 5–10% of portfolio, higher in Caution/Not-Favorable market
    regimes (per the Swing Trading Skill's regime filter, applied here
    at the whole-portfolio level too)
  → Cash is a position, not an absence of one — it should be sized
    deliberately, not left as an accidental residual
```

---

## Analysis Module 2 — Diversification Architecture

```
Step 2.1 — Direct Diversification Limits
  □ Single stock: never exceed the Tier ceiling above, hard cap 10% even
    for the highest-conviction Tier 1 name (concentration beyond this
    turns portfolio outcome into single-company outcome)
  □ Single sector: cap at 25–30% (hard flag above this, requires explicit
    documented justification, e.g., a deliberate high-conviction thematic bet)
  □ Market cap mix: define and track Large/Mid/Small% split against a
    stated target band appropriate to the investor's risk tolerance and
    horizon — do not let this drift silently

Step 2.2 — Hidden Concentration (Overlap) Analysis
  □ Supply chain overlap: are multiple holdings dependent on the same
    upstream input or downstream customer base?
  □ Macro-factor overlap: do multiple holdings share the same primary
    macro sensitivity (e.g., 3 holdings all highly INR/USD sensitive,
    or all highly dependent on a single commodity price)?
  □ Thematic overlap: are multiple "different sector" holdings actually
    the same underlying bet (e.g., a capex-cycle theme expressed through
    3 different sector labels)?
  → Report an "effective concentration" view alongside the nominal
    sector/stock split — nominal diversification can mask real concentration

Step 2.3 — Correlation-Aware Position Sizing
  When two or more holdings are identified as correlated (Step 2.2), treat
  their COMBINED allocation against the single-position/sector ceilings in
  Step 2.1, not each position independently.
```

---

## Analysis Module 3 — Rebalancing Discipline

```
Step 3.1 — Trigger-Based Rebalancing (Preferred Over Calendar-Only)
  □ Position drift trigger: rebalance a holding if it drifts more than
    ~50% relative to its target weight (e.g., a 5% target position that
    has grown to 8%+ through price appreciation warrants a trim decision,
    even absent a fundamental change)
  □ Thesis-status trigger: any holding moved to "Weakened" or "Invalidated"
    status (per the relevant research skill) triggers an immediate review,
    not a wait-for-the-next-calendar-date review
  □ Regime trigger: a shift from Favorable to Not-Favorable market regime
    (per the Swing Trading Skill's regime filter) is a portfolio-level
    signal to raise the cash reserve tier, not just a swing-book signal

Step 3.2 — Calendar-Based Review (Minimum Cadence)
  □ Full portfolio review: at minimum, quarterly (aligned with results season)
  □ Tier 3 (speculative) holdings: monthly check-in given faster-moving
    thesis-validity windows
  □ Tax-aware rebalancing: check LTCG-threshold-crossing dates before
    executing a trim that could otherwise be timed better for tax efficiency

Step 3.3 — Adding to Positions (Scaling In)
  □ Tier 1: can be built via 2–3 tranches as thesis confirms
  □ Tier 3: must follow the specific specialist skill's stage-based
    build-up trigger (e.g., Multibagger Discovery Module 1, Turnaround
    Module 2) — never accelerate the build-up ahead of stage-confirming evidence
  □ Never average down into a Tier 3 position below its original thesis-
    invalidation level — averaging down on a broken thesis is a sizing
    error dressed up as conviction
```

---

## Analysis Module 4 — Behavioral Capacity Matching

```
This module exists because the "optimal" portfolio on paper is worthless if
the investor cannot hold it through a real drawdown.

□ Stress-test the proposed allocation against a -20% to -30% broad market
  scenario and a -40%+ scenario concentrated in the portfolio's largest
  sector exposure — translate this into an approximate ₹ or % portfolio
  decline the investor should be prepared to see without panic-selling
□ Ask (or infer from stated history): has this investor previously exited
  positions during a drawdown at or near the bottom? If yes, the actual
  safe Tier 3/Tactical allocation ceiling should be set lower than the
  theoretical maximum in Module 1 — behavioral capacity overrides the
  textbook ceiling
□ Match SIP/recurring-investment portfolios to the AI_Small_to_Mid_Cap_SIP_
  Stocks_Analysis_Skill's durability screen — a portfolio built for monthly
  recurring investment should weight survivability and consistency more
  heavily than a lump-sum portfolio, since SIP investors are buying through
  every phase of the cycle including the worst of it
□ If the investor's stated risk tolerance and their behaviorally inferred
  tolerance conflict, flag this explicitly rather than silently defaulting
  to either — this is a decision the investor should make consciously
```

---

## Analysis Module 5 — Pre-Equity Liquidity Carve-Out (Upgrade — Previously Missing)

```
This skill previously started allocation logic assuming all capital was
investable. Sequence a liquidity layer first:

□ Emergency Fund: confirm 6–12 months of essential expenses is held
  outside this equity portfolio (liquid fund/FD/savings) BEFORE any
  Tier 1–4 allocation is finalized — if not yet in place, recommend
  carving this out first rather than treating 100% of stated capital as investable
□ Goal-Proximity Check: any known cash need within 3 years (per Pre-
  Flight) must be excluded from equity allocation entirely, not merely
  weighted toward Tier 1 "safer" stocks — near-term goals do not belong
  in single-stock equity regardless of conviction tier
□ This carve-out is computed BEFORE the Tier 1–4 percentages in Module 1,
  which apply only to the remaining genuinely long-horizon investable capital
```

## Analysis Module 5 — New Capital Deployment Sequencing (v1.1 Addition)

```
This module addresses a gap in the original skill: it defined target
allocation but not HOW to get there when new capital arrives (a lump sum,
or a fresh SIP-eligible surplus).

LUMP SUM DEPLOYMENT (New Money Arriving at Once):
  □ Check current market regime (per AI_Swing_Trading_Skill's Module 1
    scorecard, applied here at the whole-portfolio level) before deploying
  □ Favorable regime: deploy in 2-3 tranches over 4-8 weeks rather than
    100% in a single session, even in a favorable regime - this reduces
    single-point-in-time timing risk without meaningfully sacrificing
    the benefit of being invested
  □ Caution/Not-Favorable regime: extend deployment to 3-6 tranches over
    8-16 weeks, and raise the interim cash reserve above the standard 5-10%
    band while deployment is in progress
  □ Deploy into Tier 1 (Core) allocations first, Tier 2/3 allocations only
    after Tier 1 targets are substantially filled - this ensures the
    portfolio's foundation is established before speculative allocations
    are built out, regardless of which individual ideas look most exciting
    at the moment of capital arrival

RECURRING SURPLUS DEPLOYMENT (Regular New Savings):
  □ Route recurring surplus first to underweight Tier 1 positions (below
    their target allocation due to prior non-participation or having been
    added later than other Core holdings), then to Tier 2, maintaining the
    overall tier-ratio discipline from Module 1 rather than letting
    whichever idea is most recently discussed absorb all new capital
  □ For SIP-style direct-stock recurring investment specifically, hand off
    to AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill's durability screen
    and modulation protocol - this skill governs which TIER and how much
    of the portfolio a name should occupy, that skill governs the specific
    monthly-investment mechanics for direct-stock SIP candidates

REBALANCING VS. FRESH DEPLOYMENT PRIORITY:
  □ When both a rebalancing trim (Module 3) is due AND fresh capital has
    arrived, prioritize using the fresh capital to correct underweight
    positions FIRST, rather than immediately selling the overweight
    position - this reduces unnecessary transaction costs and, where
    relevant, avoids realizing a taxable gain that a fresh-capital
    correction could have addressed without a sale
```


## Red Flag Summary — Portfolio Construction Context

### CRITICAL Flags
```
❗ Any single stock exceeding 15% of portfolio (regardless of conviction)
❗ Tier 3 (speculative) allocation exceeding 20% of total portfolio
❗ Zero cash/liquid reserve heading into a Not-Favorable market regime
❗ Effective concentration (post-overlap-analysis) exceeding stated
  diversification targets while nominal sector split looks diversified
```

### HIGH Flags
```
⚠️ Single sector exceeding 30% without documented deliberate justification
⚠️ 3+ holdings sharing the same primary macro sensitivity, uncounted as
  combined exposure
⚠️ No rebalancing activity in 6+ months despite significant position drift
⚠️ Tactical/swing capital and long-term Tier 1–3 capital commingled without
  clear separation (making true portfolio risk hard to assess)
⚠️ Stated risk tolerance materially inconsistent with behaviorally inferred
  tolerance, unflagged
```

---

## Output Format

```
PORTFOLIO CONSTRUCTION REPORT
Date: [DD/MM/YYYY] | Total Portfolio: ₹[X] Cr (if provided) | Holdings: [N]
═══════════════════════════════════════════════════════════════════════

CONVICTION-TIER ALLOCATION:
  Tier 1 (Core):          [X]% — Target band: 40–55%
  Tier 2 (Satellite):     [X]% — Target band: 25–35%
  Tier 3 (Speculative):   [X]% — Target band: 10–15%
  Tier 4 (Tactical/Swing):[X]% — Target band: 15–25% (separate capital pool)
  Cash Reserve:           [X]% — Target band: 5–10% (higher if regime Caution/Not Favorable)

TIER-BY-TIER HOLDINGS TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company | Tier | Alloc% | Sector | Thesis Status | Ceiling Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIVERSIFICATION MAP:
  Largest Single Stock:    [X]% — [Within/Exceeds ceiling]
  Largest Sector:          [X]% — [Within/Exceeds ceiling]
  Market Cap Split:        Large [%] | Mid [%] | Small [%]

HIDDEN CONCENTRATION (Effective, Post-Overlap):
  Correlated Cluster 1:    [Holdings] — Combined effective exposure: [X]%
  Correlated Cluster 2:    [Holdings] — Combined effective exposure: [X]%
  Effective vs. Nominal Concentration: [Materially different / Consistent]

STRESS TEST:
  -20% broad market scenario:      Estimated portfolio impact: [-X]%
  Largest-sector -40% scenario:    Estimated portfolio impact: [-X]%
  Behavioral Capacity Check:       [Investor's inferred tolerance vs.
                                     stress-test outcome — Match/Mismatch]

REBALANCING STATUS:
  Positions Beyond Drift Threshold: [List — target% vs current%]
  Thesis-Status Triggers Active:    [Any Weakened/Invalidated holdings]
  Regime-Driven Cash Adjustment:    [Recommended cash % change, if any]

RECOMMENDED ACTIONS:
  Immediate:   [Trim/add/rebalance — specific holding and reason]
  This Month:  [Action — reason]
  Monitoring:  [What to watch before the next scheduled review]

⚠️ FLAGS DETECTED: [Critical/High flags list, or "None detected"]
```

---

## Rules (Non-Negotiable)

```
1. Allocation size follows conviction tier — never justify size after the
   fact by inflating the conviction description.
2. Tier ceilings are hard caps; a single stock never exceeds 15% regardless
   of stated conviction.
3. Tactical/swing capital is tracked as a separate pool from long-duration
   Tier 1–3 capital — never let the two commingle in reporting or sizing.
4. Correlated holdings are sized against combined ceilings, not evaluated
   independently.
5. Behavioral capacity, when it conflicts with stated risk tolerance, must
   be flagged explicitly rather than silently resolved in either direction.
6. Cash reserve is a deliberate position sized to the market regime, not a
   leftover residual.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Style Specialist — Portfolio Construction*
*Integrates with: Skill 06 (Portfolio Auditor), Skill 09 (Risk Auditor), AI_Swing_Trading_Skill,
AI_Multibagger_Discovery_Skill, AI_Turnaround_Analysis_Skill, AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill*
<!-- END SYSTEM FILE 11: AI_Portfolio_Construction_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 12: AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill.md | SHA256: 47d95e38d502403ad70582c96d8265db2e4cc23dd52d6bd808c80d90efdb8660 -->
## Embedded source 12: AI Small to Mid Cap SIP Stocks Analysis Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Small to Mid Cap SIP Stocks Analysis Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Small-to-Mid Cap SIP Stocks Analysis Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Durability Screening for Recurring Monthly Direct-Stock Investment

---

## CRITICAL AI INSTRUCTION

A stock that is a good lump-sum buy at today's price is not automatically a good SIP (systematic, recurring monthly investment) candidate — and the reverse is also true. Lump-sum entry is a single-point-in-time valuation and timing decision. A SIP into a direct stock (as opposed to a diversified mutual fund SIP) means the investor is committing to buy this SPECIFIC company every month for years, through every phase of its cycle, every bad quarter, every sector downturn — with no diversification cushioning any single bad outcome the way a mutual fund SIP would. This is a fundamentally different risk than a one-time entry, and the screening bar must be correspondingly different: SURVIVABILITY and CONSISTENCY matter more than upside magnitude. A company that could 5x but has a 20% chance of going to zero is a poor direct-stock SIP candidate even if it is an excellent one-time speculative bet, because the SIP structure forces continued buying through the exact period where a fragile business is most likely to reveal its fragility.

---

## Purpose

Screen small and mid-cap companies specifically for suitability as a **recurring monthly direct-stock SIP target** — evaluating balance sheet durability, business model resilience across cycles, governance consistency, and downside survivability — distinct from and stricter than the entry-timing logic used for a one-time lump-sum purchase.

---

## Pre-Flight Requirements

```
□ Company name, ticker, current market cap (must fall within small/mid-cap
  band — typically <₹20,000 Cr for this skill's intended use; if the user's
  candidate is large-cap, note this skill is not the right tool and redirect
  to Skill 01 / Skill 07 for a standard research/valuation approach)
□ Minimum 5 years of financial history (SIP suitability requires seeing the
  company through at least one full down-cycle or stress period — a company
  with only 2–3 years of listed history has not yet been tested this way,
  and should be flagged as "insufficient cycle history for SIP-grade
  confidence" rather than screened out entirely)
□ Debt structure and covenant history through any prior stress period
□ Promoter holding and pledge history across the full available period,
  not just the current snapshot
□ Sector cyclicality classification (secular grower / mild cyclical /
  deep cyclical) — materially changes what "durability" should look like
□ User's intended SIP duration (minimum should be 3+ years for this skill
  to be meaningfully applied — shorter horizons should route to Skill 02/03
  instead of a direct-stock SIP approach)
```

---

## Analysis Module 1 — Why SIP Suitability Is a Different Question Than "Is This a Good Stock"

```
The SIP structure changes the risk calculus in three specific ways that
this skill must explicitly screen for:

1. FORCED BUYING THROUGH BAD PERIODS:
   A lump-sum investor can wait for a better entry point or avoid a company
   heading into visible trouble. A SIP investor, by design, keeps buying
   every month regardless — including the exact months when a fragile
   business is deteriorating. This means the single most important SIP-
   specific question is not "what is the upside" but "what is the probability
   this company is meaningfully worse, or gone, 3–5 years from now."

2. NO DIVERSIFICATION CUSHION:
   Unlike a mutual fund SIP (where one bad holding among 40–60 is absorbed),
   a direct-stock SIP concentrates the investor's recurring capital into a
   single-company outcome. This raises the bar for balance sheet resilience
   and governance consistency far above what would be acceptable for a
   single position within a diversified portfolio.

3. AVERAGING BENEFIT REQUIRES SURVIVAL, NOT JUST VOLATILITY:
   Rupee-cost averaging only works to the investor's benefit if the company
   survives and eventually recovers/grows — averaging down into a business
   that is structurally declining does not average into a good outcome, it
   compounds a bad one. This skill must distinguish "volatile but durable"
   (SIP-suitable) from "volatile because structurally fragile" (SIP-unsuitable).
```

---

## Analysis Module 2 — Durability Screen (Mandatory Gates)

```
BALANCE SHEET SURVIVABILITY:
□ Debt/Equity < 1x (stricter than the standard 1.5–3x thresholds used
  elsewhere in the IERL library — SIP candidates should not depend on
  favorable refinancing conditions persisting for years)
□ Interest Coverage Ratio > 5x in the most recent normalized year
□ Company has never breached a debt covenant or required emergency
  refinancing/restructuring in its listed history
□ Cash + liquid investments sufficient to cover at least 12 months of
  fixed obligations (interest + minimum capex) even at zero incremental
  operating cash flow — a genuine stress-survival buffer, not just a
  comfortable-times ratio

CYCLE-TESTED RESILIENCE:
□ Company has been through at least one meaningful sector or macro
  downturn (state which one — e.g., 2018–19 NBFC crisis, 2020 COVID
  demand shock, a specific commodity down-cycle) while listed
□ Revenue decline during that downturn, if any, was less severe than
  sector peers OR recovery afterward was faster than sector peers —
  state the specific comparison, not a general "resilient" label
□ The company did NOT require equity dilution at a distressed valuation
  to survive that downturn (dilution under duress is a durability failure,
  even if the company technically survived)

GOVERNANCE CONSISTENCY (Higher Bar Than Standard Screening):
□ Same promoter/management control for the full history reviewed
  (leadership discontinuity is a specific SIP risk — a multi-year
  recurring commitment should not rest on an unproven new regime)
□ Promoter pledge has never exceeded 10% at any point in the reviewed
  history (not just currently — a company that pledged heavily in the
  past and later cleared it still carries a demonstrated willingness to
  lever personal holdings under stress)
□ No history of auditor qualification, resignation, or forensic
  investigation in the reviewed period
□ Dividend or buyback consistency (even if modest) through the down-cycle
  reviewed above — a company that maintained shareholder returns discipline
  even in a bad year demonstrates balance sheet and cash-flow durability
  under real stress, which is more informative than performance in good years

BUSINESS MODEL DURABILITY:
□ Revenue is not concentrated in a single customer or single short-cycle
  product/geography beyond levels the company has proven it can survive
  losing (cross-check against the cycle-tested resilience evidence above)
□ Company does not depend on a single regulatory dispensation or subsidy
  regime whose renewal is uncertain over the SIP horizon
□ Structural demand driver (not just current cyclical tailwind) can be
  named and is expected to persist over the full SIP horizon
```

---

## Analysis Module 3 — Sector Cyclicality Adjustment

```
SECULAR GROWERS (e.g., certain consumption, healthcare, specialty categories):
  → Durability bar centers on competitive position and balance sheet;
    cycle-testing requirement can be satisfied by a milder demand shock
    if a genuine severe downturn hasn't occurred in the company's history —
    but still require at least one visible stress quarter/year to assess
    behavior under pressure

MILD CYCLICALS (e.g., autos ancillaries, select industrials):
  → Full cycle-tested resilience module applies as written
  → Pay particular attention to capacity utilization trough behavior —
    did fixed-cost absorption problems threaten solvency, or was the
    company comfortably profitable even at trough utilization?

DEEP CYCLICALS (e.g., commodity-linked, real estate, shipping):
  → This category is generally POOR-FIT for direct-stock SIP by nature —
    the "buy every month regardless" structure works against an investor
    in a business where entry timing relative to the cycle matters enormously
  → Default output posture for deep cyclicals should lean toward
    "Not Recommended for SIP — consider Skill 03 (Positional) or Skill 11
    (Turnaround) framework for point-in-time entries instead," unless the
    specific company shows genuinely exceptional balance sheet strength
    that meaningfully decouples its survivability from the cycle itself
```

---

## Analysis Module 4 — SIP Amount Modulation Protocol (v1.1 Addition)

```
A static monthly amount is the simplest SIP approach but is not the only
one, and this skill should be able to recommend the right variant based
on the durability score from Module 2 and the investor's stated preference.

STANDARD SIP (Default):
  Fixed monthly amount regardless of price - appropriate for Strong (80-100)
  and most Conditional (60-79) durability candidates where the primary
  goal is disciplined accumulation without decision fatigue.

VALUE-AVERAGED SIP (For Conditional/Volatile Candidates):
  Monthly amount adjusts inversely to recent price movement within a
  pre-defined band (e.g., increase allocation by 20-30% if the stock has
  fallen more than 15% from its trailing 3-month average, decrease by a
  similar amount if it has risen more than 15%) - requires the durability
  gates in Module 2 to be firmly passed, since this approach effectively
  increases exposure into weakness, which is only appropriate for a company
  already screened as survivable through stress.

STEP-UP SIP (For Strong Candidates With Rising Investible Surplus):
  Scheduled periodic increase in the monthly amount (e.g., annually, tied
  to the investor's own income growth) - appropriate only for Strong (80+)
  candidates, since a step-up compounds the SIP-specific risk described in
  Module 1 (forced buying through bad periods) by committing MORE capital
  over time, not less.

PAUSE PROTOCOL (Mandatory, Not Optional):
  A SIP must be explicitly paused, not merely continued on autopilot, if:
  - Any CRITICAL Flag from the Red Flag Summary below newly triggers
  - The SIP Durability Score (Module 2) drops by more than 20 points at
    any scheduled re-screen
  - Leadership discontinuity occurs (per the Governance Consistency gate)
    and there is not yet a multi-year track record under the new regime

  Pausing is distinct from stopping: a paused SIP resumes once the
  triggering condition is resolved or a re-screen confirms durability is
  restored; a stopped SIP requires a fresh Module 2 screen before resuming,
  treating it as a new candidate rather than assuming prior durability still
  holds.
```


## SIP Durability Score (0–100)

| Category | Max Points | What It Measures |
|---|---|---|
| Balance Sheet Survivability | 25 | Debt/Equity, interest coverage, stress-liquidity buffer |
| Cycle-Tested Resilience | 25 | Demonstrated behavior through a real prior downturn |
| Governance Consistency | 25 | Leadership continuity, pledge history, dividend discipline under stress |
| Business Model Durability | 15 | Concentration risk, regulatory dependency, structural demand driver |
| Sector Cyclicality Fit | 10 | Secular/mild-cyclical fit bonus; deep-cyclical penalty |

**Interpretation:**
```
80–100:  Strong SIP Candidate — durability well-evidenced across a real stress period
60–79:   Conditional SIP Candidate — durable on most gates, monitor the specific
         gap identified; consider a smaller recurring amount initially
40–59:   Weak SIP Candidate — meaningful durability gaps; better suited to
         lump-sum, opportunistic entry (Skill 01/07) than recurring commitment
<40:     Not Recommended for SIP — route to Turnaround (if distressed) or
         avoid entirely (if simply low-quality)
```

---

## Analysis Module 4 — Valuation-Aware SIP Adjustment (Upgrade — Previously Missing)

```
A static monthly amount ignores that the SAME company can be a better or
worse SIP entry depending on where it trades relative to its own history.

□ If current valuation (per Skill 07's historical band) is BELOW the
  stock's 5-year average multiple, standard or slightly increased monthly
  amount is justified
□ If current valuation is materially ABOVE the 5-year average (e.g., top
  quartile of its historical range) without a corresponding step-up in
  business quality/durability score, reduce the monthly amount rather
  than pausing entirely — this preserves the averaging discipline while
  respecting valuation risk
□ Never pause a SIP purely on a durability-score downgrade without first
  checking whether the downgrade stems from a temporary, cycle-linked
  factor (which the SIP structure is designed to average through) versus
  a genuine structural deterioration (which should trigger a full re-screen,
  not just an amount adjustment)
```

## Red Flag Summary — SIP Context

### CRITICAL Flags
```
❗ Equity dilution at a distressed valuation during any prior downturn
❗ Debt covenant breach or emergency refinancing anywhere in reviewed history
❗ Promoter pledge has ever exceeded 25% at any point in the reviewed history
❗ Deep cyclical sector with no evidence of balance-sheet decoupling from the cycle
❗ Leadership discontinuity within the last 3 years with no multi-year track
  record yet under the new regime
```

### HIGH Flags
```
⚠️ Debt/Equity currently below 1x but was materially higher during the last
  downturn (durability improvement is recent and not yet cycle-tested)
⚠️ Dividend/buyback suspended during the last downturn without later resumption
⚠️ Revenue concentration in a single customer/geography exceeding 40%, no
  evidence the company has weathered losing a similarly-sized customer before
⚠️ Company has less than one full down-cycle of listed history — insufficient
  evidence either way, must be stated explicitly as such rather than scored confidently
```

---

## Output Format

```
SIP DURABILITY ANALYSIS
Company: [Name] | Ticker: [NSE] | Market Cap: ₹[X] Cr | Sector Cyclicality: [Secular/Mild/Deep]
Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

SIP DURABILITY SCORE: [0–100] — [Strong/Conditional/Weak/Not Recommended]

BALANCE SHEET SURVIVABILITY: [/25]
  Debt/Equity:              [X]x — [Pass/Fail vs <1x gate]
  Interest Coverage:        [X]x — [Pass/Fail vs >5x gate]
  Stress-Liquidity Buffer:  [X months of obligations covered]

CYCLE-TESTED RESILIENCE: [/25]
  Downturn Reviewed:        [Named event/period]
  Revenue Impact vs Peers:  [Better/Worse/In-line, with data]
  Recovery Speed vs Peers:  [Faster/Slower/In-line]
  Dilution Under Stress:    [None / Yes — disqualifying]

GOVERNANCE CONSISTENCY: [/25]
  Leadership Continuity:    [Full period / Changed in year X]
  Max Historical Pledge:    [%] (not just current)
  Auditor History:          [Clean / Issues noted]
  Dividend Discipline in Downturn: [Maintained / Suspended]

BUSINESS MODEL DURABILITY: [/15]
  Concentration Risk:       [Customer/geography % and evidence of survivability]
  Regulatory Dependency:    [None material / Named dependency]
  Structural Demand Driver: [Named — expected to persist over SIP horizon]

SECTOR CYCLICALITY FIT: [/10]
  Classification:           [Secular/Mild/Deep]
  Fit Assessment:            [Bonus applied / Penalty applied / Neutral]

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]

RECOMMENDATION:            [Strong SIP Candidate / Conditional / Weak — Prefer
  Lump-Sum Instead / Not Recommended]
Suggested Monthly Sizing:   [Full standard allocation / Reduced amount pending
  gap resolution / Not applicable]
Re-Screen Trigger:          [What event — leadership change, debt spike, next
  down-cycle — should trigger an immediate re-screen rather than waiting for
  the next scheduled review]
```

---

## Rules (Non-Negotiable)

```
1. This skill applies stricter balance sheet and governance gates than
   standard lump-sum research (Skill 01) — do not substitute one for the other.
2. A company with no evidenced downturn in its listed history cannot receive
   a "Strong" rating — cap the rating at "Conditional" pending real stress evidence.
3. Deep cyclical sector companies default to Not Recommended for SIP unless
   exceptional, specifically evidenced balance-sheet decoupling exists.
4. Equity dilution at a distressed valuation during any past downturn is an
   automatic disqualifier from "Strong" or "Conditional," regardless of
   current-period financial strength.
5. Score and recommendation must be re-run whenever a leadership change,
   debt-covenant event, or new sector downturn occurs — do not treat a
   prior SIP-suitability rating as durable through a materially changed
   circumstance.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Style Specialist — SIP Durability Screening*
*Integrates with: Forensic Accounting Skill, Skill 09 (Risk Auditor), AI_Portfolio_Construction_Skill,
AI_Turnaround_Analysis_Skill (for deep-cyclical/distressed redirect)*
<!-- END SYSTEM FILE 12: AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 13: AI_Swing_Trading_Skill.md | SHA256: 3719df5eb93f4dd027bbfb56825649a6db6a5462cae4af9096689d733da21172 -->
## Embedded source 13: AI Swing Trading Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Swing Trading Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


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
<!-- END SYSTEM FILE 13: AI_Swing_Trading_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 14: AI_Technical_Analysis_Master_Skill.md | SHA256: 39016471186c06d2ff7fb271aa44e19e8529b56a705aa4d9ba92b13674279ea5 -->
## Embedded source 14: AI Technical Analysis Master Skill

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

<!-- END SYSTEM FILE 14: AI_Technical_Analysis_Master_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 15: Technical_Analysis_Data_Input_Template_v_0.0.md | SHA256: d3d197d73284c932385c45eff34fcf82c96bed6cda473782d2b486eced42f170 -->
## Embedded source 15: Technical Analysis Data Input Template v 0.0

# Technical Analysis — Data Input Template (Addendum v_0.0)

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
<!-- END SYSTEM FILE 15: Technical_Analysis_Data_Input_Template_v_0.0.md -->

---

<!-- BEGIN SYSTEM FILE 16: AI_Turnaround_Analysis_Skill.md | SHA256: acaa4c25f8f169e9eaa1a23f0cc74632aa836ea2293c31c3851828097e91b124 -->
## Embedded source 16: AI Turnaround Analysis Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Turnaround Analysis Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Turnaround Analysis Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Distressed & Recovery Situation Analysis

---

## CRITICAL AI INSTRUCTION

The central risk in turnaround investing is not picking a bad stock — it is mistaking a value trap for a turnaround because both look identical in the early stages: falling price, negative headlines, a hopeful management narrative. The only reliable differentiator is *evidence of operational change*, not commentary about intent. Claude must never upgrade a turnaround stage based on management's stated plans alone — only on delivered, measurable results. When in doubt between "stabilizing" and "still deteriorating," classify as deteriorating; the cost of a missed early entry is much lower than the cost of capital permanently impaired in a company that was never actually turning around.

---

## Purpose

Distinguish genuine operational and financial turnarounds from value traps and permanently impaired businesses, using a staged evidence framework, an explicit signal-versus-trap checklist, and stage-matched position sizing — so that speculative recovery bets are sized appropriately for their actual uncertainty rather than for the narrative's appeal.

---

## Pre-Flight Requirements

```
□ Reason for the distress clearly identified (cyclical downturn, company-
  specific mismanagement, industry disruption, balance sheet stress,
  regulatory action, fraud/governance failure) — the turnaround playbook
  differs materially by cause
□ Minimum 8 quarters of financial history spanning the distress period
□ Current management team background — is this the same team that caused
  the distress, or a new team brought in specifically for recovery?
□ Debt structure: secured vs. unsecured, maturity schedule, any restructuring
  (CDR/IBC/OTS) history
□ Promoter shareholding and pledge trend through the distress period
□ Auditor history through the distress period (changes, qualifications)
□ Peer/industry context: is the whole sector distressed (cyclical) or is
  this company uniquely troubled within a healthy sector (company-specific)?
```

---

## Analysis Module 1 — Root Cause Classification (Run First)

```
The recovery playbook and appropriate confidence level differ fundamentally
by cause. Classify before anything else:

CAUSE A — CYCLICAL DOWNTURN (commodity price crash, demand cycle trough):
  → Highest base-rate for genuine recovery; recovery is largely a function
    of the cycle turning, not company-specific fixes
  → Key evidence to track: industry-wide indicators (utilization rates,
    realizations, order books) alongside company financials

CAUSE B — COMPANY-SPECIFIC OPERATIONAL FAILURE (poor execution, failed
  expansion, cost overruns) with sector otherwise healthy:
  → Recovery depends entirely on management fixing identifiable, specific
    operational issues — requires new/reformed management and hard evidence
    of the specific fix, not just "we are addressing it"

CAUSE C — BALANCE SHEET DISTRESS (over-leveraged, possibly from Cause A or B
  compounding into a debt problem):
  → Recovery requires either a credible deleveraging plan with visible early
    execution (asset sales, equity infusion, refinancing) or restructuring
    (CDR/IBC) with clarity on the resulting equity structure post-resolution
  → Equity holders may face severe or total dilution in restructuring — this
    is not automatically a "turnaround buy" opportunity even if the business
    itself eventually recovers

CAUSE D — GOVERNANCE FAILURE / FRAUD:
  → Lowest base rate for genuine recovery as an equity investment
  → Requires: complete management change, forensic audit closure, and a
    multi-year clean track record before this skill should treat the name
    as investable at all — early-stage "recovery" claims post-fraud
    disclosure should default to AVOID, not WATCH

→ State the classified cause explicitly before proceeding to staging.
  If the cause is ambiguous or unstated, treat this as a Tier 2 data gap
  per the Universal Skill Failure Protocol and proceed with reduced confidence.
```

---

## Analysis Module 2 — Turnaround Stage Assessment

```
STAGE T0 — DISTRESS PEAK:
  Losses, debt concerns, possible management crisis, still deteriorating
  → DO NOT INVEST. Monitor only, for T1 signals.
  → Risk: further deterioration, potential equity dilution or wipeout
  → Position size: 0%

STAGE T1 — STABILIZATION:
  Losses narrowing (not yet profitable) for 2+ consecutive quarters,
  debt not rising further (flat, not necessarily falling yet), new
  management in place with a stated and specific plan
  → Initial small position possible: 1–2% maximum
  → This is inherently speculative — evidence is directional, not confirmed

STAGE T2 — EARLY RECOVERY:
  Revenue growing for 2+ consecutive quarters, margins recovering
  (2+ quarters of sequential improvement), debt reducing in absolute
  terms, management demonstrating delivery against its own stated plan
  → Position building justified: 2–3%
  → Evidence-based but still meaningfully uncertain — do not treat as a
    "confirmed" story yet

STAGE T3 — RECOVERY CONFIRMED:
  Business sustainably profitable, balance sheet healing measurably
  (Debt/EBITDA improving toward sector-normal levels), competitive
  position demonstrably stabilized or improving
  → Full conviction position possible: 3–5%
  → Primary remaining risk shifts to valuation — the market may have
    already priced in much of the recovery by this stage

RULE: Advancing a company from one stage to the next requires the FULL
quarter-count of evidence specified above — a single strong quarter does
not upgrade the stage, even if it is a dramatic beat. Management's forward
guidance or investor-day promises never advance a stage on their own.
```

---

## Analysis Module 3 — Signal vs. Trap Checklist

```
GENUINE TURNAROUND SIGNALS (Require Evidence, Not Claims):
□ New management with a documented, verifiable turnaround track record
  at a prior company (not merely "experienced industry professional")
□ Debt/EBITDA declining for 2+ consecutive quarters
□ Gross margin recovering through operational improvement (better mix,
  cost efficiency), not merely through one-time cost cuts that cannot repeat
□ Order book / revenue visibility rebuilding (relevant for capital
  goods, infra, EPC-type businesses)
□ Working capital improving — receivable days genuinely reducing, not
  merely reclassified or factored off balance sheet
□ Promoter buying shares in the open market with personal funds during
  the distress/recovery phase (not a pledged-share buyback structure)
□ Industry cycle independently turning (for Cause A situations) —
  corroborated by industry-level data, not just company commentary
□ A specific regulatory or legal overhang has been formally, finally
  resolved (order/settlement in hand — not "expected to resolve soon")
□ Auditor providing a clean opinion after a prior qualification, with
  no material change in accounting policy required to achieve this
□ Related-party exposures visibly and verifiably being wound down

TURNAROUND TRAPS — TREAT AS EXIT OR AVOID SIGNALS:
□ Revenue declining while management describes the same period as
  "restructuring for future growth" (a common way deterioration is reframed)
□ Debt continuing to rise despite an active "turnaround" narrative
□ Promoter selling shares, or pledge increasing, during the supposed
  recovery phase — the person with the most information is not
  behaving as if they believe the recovery
□ 3 or more management changes within 3 years (structural leadership
  instability, not a one-time reset)
□ Auditor resignation without a satisfactory, specific public explanation
□ Rights issue or QIP priced at a steep discount to prevailing price
  (often a desperation signal for capital, not a growth-funding signal)
□ New related-party transactions initiated during a period of financial
  stress (value potentially being extracted even as minority shareholders
  are asked to be patient)
□ Loss-making quarters attributed, quarter after quarter, exclusively to
  "one-time" items (if it recurs, it is not one-time by definition)
□ Guidance consistently missed despite management repeatedly describing
  its own guidance as "conservative" — the pattern of repeated misses is
  the signal, regardless of how each individual miss is explained
```

---

## Analysis Module 4 — Financial Recovery Tracking

```
Track the following on a rolling 4-quarter basis, always presented as a
trend line, never as a single data point:

  Revenue:               [Trend — accelerating/decelerating/flat]
  Gross Margin:           [Trend]
  EBITDA Margin:          [Trend]
  Net Debt:               [Trend, absolute ₹ and Debt/EBITDA ratio]
  Operating Cash Flow:    [Trend — is cash generation improving alongside
                            or ahead of reported profitability?]
  Working Capital Days:   [Trend]
  Promoter Buy/Sell:      [Net activity over last 12 months]
  Interest Coverage:      [Trend — is debt servicing capacity improving?]

Cross-check reported PAT improvement against OCF improvement — a recovery
where PAT improves but OCF does not is a lower-confidence recovery (earnings
quality concern per the Forensic Accounting Skill; this skill should
explicitly hand off to that skill for any Stage T2+ candidate).
```

---

## Analysis Module 5 — Equity Dilution Scenario Modeling (Upgrade — Previously Missing)

```
For Cause C (Balance Sheet Distress) candidates specifically, entering
before dilution/restructuring terms are known is a distinct risk this
skill previously left implicit. Make it explicit:

□ If restructuring (CDR/IBC/OTS) is active or likely, state the range of
  plausible equity dilution outcomes (e.g., "resolution plans in
  comparable cases have diluted existing equity 60–95%") rather than
  silently assuming pre-restructuring share count in any return projection
□ Distinguish "recovering EBITDA at the operating level" from "recovering
  value for CURRENT equity holders" — under IBC, the two can diverge
  completely; a business can survive and even thrive post-resolution while
  pre-resolution shareholders are wiped out or near-wiped out
□ Position size for any Cause C name still under active restructuring
  should be treated as Stage T0 (0% / monitoring only) regardless of
  operational stabilization signals, until the resolution plan's equity
  treatment is known
```

## Output Format

```
TURNAROUND ANALYSIS REPORT
Company: [Name] | Ticker: [NSE] | Root Cause: [A/B/C/D] | Stage: T[0/1/2/3]
Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

ROOT CAUSE CLASSIFICATION: [Cyclical / Company-Specific Operational /
  Balance Sheet Distress / Governance Failure]
  Basis: [1–2 sentences on why this classification, with evidence]

STAGE ASSESSMENT: T[X] — [DISTRESS PEAK / STABILIZATION / EARLY RECOVERY /
  RECOVERY CONFIRMED]
  Stage Evidence: [Specific quarter-count and metrics justifying this stage
    — must show the FULL required evidence window, not a partial one]

SIGNAL VS. TRAP SCORECARD:
  Genuine Signal Count:   [X]/10
  Trap Signal Count:      [X]/9
  Net Signal Score:       [Signals − Traps]
  Signals Present:        [List with specific evidence for each]
  Traps Present:          [List with specific evidence for each, or "None detected"]

FINANCIAL RECOVERY TRACK (Rolling 4 Quarters):
  Revenue:            [Trend]
  Gross/EBITDA Margin: [Trend]
  Net Debt / Debt-EBITDA: [Trend]
  OCF vs PAT:          [Trend — earnings quality flag if diverging]
  Working Capital Days: [Trend]
  Promoter Buy/Sell (12mo): [Net activity]

MANAGEMENT ASSESSMENT:
  Current Team:            [Same team that caused distress, or new team]
  Turnaround Track Record: [Verified prior experience, or "unverified/none"]
  Promise vs. Delivery:    [Last 4 quarters of guidance vs. actual]

WHAT WOULD CONFIRM THE NEXT STAGE:
  [Specific metrics and quarter-count needed to advance stage classification]

WHAT WOULD INVALIDATE THIS THESIS:
  [Specific triggers — e.g., debt rising again, promoter pledge increasing,
  guidance miss streak extending]

RECOMMENDATION:            [Avoid / Watch Only / Speculative Position / Build Position]
Stage-Based Max Position:   [0% / 1–2% / 2–3% / 3–5%]
Re-Rating Trigger:          [What specific evidence, once confirmed, justifies
  increasing position or advancing the stage]

HANDOFF NOTE: [If Stage T2 or higher — recommend running the Forensic
  Accounting Skill for a full earnings-quality check before further sizing]
```

---

## Rules (Non-Negotiable)

```
1. A single strong quarter never advances a stage — the full evidence
   window specified for that stage is mandatory.
2. Management's stated plans and intentions carry zero weight in staging —
   only delivered, measured results count.
3. Cause D (governance failure/fraud) situations default to AVOID until a
   multi-year clean track record exists post-disclosure — no shortcut path
   to WATCH or BUY status regardless of price decline.
4. Promoter selling or increasing pledge during a claimed recovery phase is
   treated as a Trap signal even if simultaneous financial metrics look
   superficially improving.
5. Position size is capped by Stage, never by conviction or narrative appeal.
6. Any recovery in reported PAT not corroborated by OCF improvement must be
   flagged explicitly and routed to the Forensic Accounting Skill.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Style Specialist — Turnaround Analysis*
*Integrates with: Forensic Accounting Skill, Skill 06 (Portfolio Auditor), Skill 09 (Risk Auditor),
Skill 15 (Pre-Investment Master Checklist)*
<!-- END SYSTEM FILE 16: AI_Turnaround_Analysis_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 17: AI_Uptrend_Momentum_Stock_Skill.md | SHA256: 22d53163913f3eb56761046a7dea391ab72457e8d2b153d08bfb94416e3c87c4 -->
## Embedded source 17: AI Uptrend Momentum Stock Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Uptrend Momentum Stock Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


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
<!-- END SYSTEM FILE 17: AI_Uptrend_Momentum_Stock_Skill.md -->

---

<!-- BEGIN SYSTEM FILE 18: AI_Volume_Delivery_Analysis_Skill.md | SHA256: a5d06dfab9833ebb5788345cfb0359f7b977f38ea1198483f4789e5d8525a9bb -->
## Embedded source 18: AI Volume Delivery Analysis Skill

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Volume Delivery Analysis Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Volume & Delivery Analysis Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Core Toolkit — Delivery %, Bulk/Block Deal, and Participation-Quality Analysis

---

## CRITICAL AI INSTRUCTION

Traded volume alone tells Claude how many shares changed hands — it says nothing about WHO was buying or whether the buying reflects genuine investment intent versus intraday churn. This skill exists specifically to go one layer deeper than the basic volume module in AI_Technical_Analysis_Master_Skill, using NSE/BSE delivery percentage, bulk/block deal disclosures, and shareholding pattern changes to distinguish real accumulation from noise. Claude must never treat a volume spike alone as an institutional accumulation signal — delivery percentage, and ideally a corroborating bulk/block deal or shareholding filing, is required before that specific claim is made.

---

## Purpose

Provide a dedicated toolkit for reading beneath headline traded volume — delivery percentage trends, bulk/block deal disclosures, and shareholding pattern changes — to assess whether price/volume action reflects genuine accumulation or distribution by informed participants, versus short-term speculative or intraday-driven volume that carries much lower signal value.

---

## Pre-Flight Requirements

```
□ Daily delivery volume and delivery percentage data (NSE/BSE disclose this
  separately from total traded volume — total volume includes intraday
  trades that are squared off same-day and never actually change ownership)
□ Bulk deal and block deal disclosures for the relevant period (exchange-
  mandated disclosures for large single transactions above threshold size)
□ Latest available shareholding pattern (quarterly disclosure) showing FII,
  DII, and public shareholding changes
□ Historical baseline: 20-day and 90-day average delivery % for the stock,
  to judge whether a current reading is unusual for THIS specific stock
  (delivery % baselines vary widely stock-to-stock and must never be
  compared against a fixed universal threshold alone)
```

---

## Analysis Module 1 — Delivery Percentage Analysis

```
WHAT IT MEASURES: Delivery % = (Shares actually transferred to demat
accounts / Total shares traded) × 100. A trade that is bought and sold
within the same day (intraday) is NOT delivered and does not count —
so delivery % is a proxy for how much of the day's volume reflects
genuine, held positions versus short-term trading churn.

INTERPRETATION (Always Relative to the Stock's OWN Baseline, Never a
Fixed Universal Number):
  Delivery % meaningfully ABOVE its 20/90-day average, on a day of price
  strength AND above-average total volume → Strongest combination — genuine
    accumulation signal, materially more informative than volume alone
  Delivery % meaningfully ABOVE its own average, on a day of price weakness
    → Genuine distribution/selling signal — informed participants exiting,
    a more urgent bearish signal than a price decline on low delivery %
  Delivery % BELOW its own average despite a large total volume/price move
    → The move is being driven primarily by intraday/speculative activity
    — lower-confidence signal, treat any accompanying technical breakout
    (per AI_Technical_Analysis_Master_Skill) as UNCONFIRMED until delivery
    % catches up or a retest with higher delivery volume occurs

MANDATORY PAIRING: Delivery % must always be stated alongside (a) the
stock's own historical baseline for comparison and (b) the direction of
price on that session — a delivery % figure without both of these is not
interpretable and should not be presented as a signal.
```

---

## Analysis Module 2 — Bulk & Block Deal Analysis

```
BULK DEALS: Single transactions ≥0.5% of a company's total equity in a
  day, disclosed by the exchange with buyer/seller identity (for
  registered categories) and price.
BLOCK DEALS: Large single trades executed through a separate block
  window, typically institutional, above a higher minimum threshold.

INTERPRETATION:
  □ Identify WHO is on each side where disclosed — a promoter entity, a
    known institutional investor (mutual fund, FII/FPI, insurance company),
    or an unidentified/individual counterparty — the信号 value differs
    materially by category
  □ Price relative to prevailing market price: a bulk/block deal at a
    PREMIUM to the current market price is a stronger positive signal
    (buyer paid up for size/urgency) than one executed at a discount
    (seller accepted a lower price to exit size quickly — can reflect
    either liquidity need or lower conviction from the seller)
  □ Repeated bulk deals from the SAME buyer category over successive
    sessions/weeks → Building conviction signal — a pattern is more
    informative than a single isolated deal
  □ Promoter-side bulk/block SELLING must be cross-checked against the
    Governance module in Skill 01 and the Turnaround Skill's Signal vs
    Trap checklist — promoter selling during a period the company is
    also presenting a growth or recovery narrative is a specific red
    flag combination that must be flagged explicitly, not reported as a
    neutral data point
  □ A single bulk deal, in isolation, without corroborating price/delivery
    trend (Module 1) or subsequent shareholding filing confirmation
    (Module 3), should be treated as a data point to monitor, not yet a
    standalone actionable signal
```

---

## Analysis Module 3 — Shareholding Pattern Change Analysis

```
Quarterly shareholding disclosures are the lowest-frequency but highest-
confirmation-value data source in this skill — they show actual position
changes by category, not inferred from trading activity.

□ FII/FPI holding: quarter-on-quarter change, in both percentage points
  and, where derivable, approximate share count
□ DII (domestic institutional — mutual funds, insurance, banks) holding:
  same tracking
□ Promoter holding: any change at all warrants explicit comment — even a
  small reduction should be investigated for reason (pledge-related
  forced sale, OFS participation, estate/succession-related transfer,
  or open-market sale) rather than assumed to be routine
□ Public/retail holding: a rising retail share alongside falling
  institutional share (or vice versa) is itself informative about who is
  driving recent price action, and should be stated explicitly

CROSS-CHECK AGAINST MODULES 1 & 2:
  □ Did FII/DII holding increase in a quarter that also showed elevated
    delivery % and bulk/block deals from institutional counterparties?
    → Corroborated signal, materially higher confidence than any single
      data source alone
  □ Did delivery % or bulk-deal activity suggest accumulation, but the
    subsequent shareholding filing showed NO corresponding increase in
    FII/DII holding? → The apparent accumulation may have been from a
    category not separately disclosed (e.g., domestic HNI/family office
    activity, or accumulation that occurred and partially reversed within
    the same quarter) — state this explicitly as an unresolved data point
    rather than forcing a conclusion the data doesn't fully support
```

---

## Analysis Module 4 — Pledge-Triggered Forced-Selling Cross-Check (Upgrade — Previously Missing)

```
Bulk/block promoter selling was previously flagged generically — add the
specific, higher-severity sub-case:

□ Cross-check any promoter bulk/block sale against DISCLOSED PLEDGE LEVEL
  at the most recent filing — a sale from a heavily-pledged promoter
  entity during a price decline is more likely to be a FORCED sale
  (lender invoking pledge/margin call) than a voluntary portfolio
  decision, and this distinction changes the interpretation materially:
  a forced sale is a mechanical liquidity event, not necessarily a
  conviction signal about the business, but it also frequently triggers
  further downside as the mechanism can repeat at lower prices
□ If pledge level is elevated (>25%) AND price has declined >20% from the
  pledge-creation price, treat this combination as a CRITICAL flag
  regardless of what the standalone bulk-deal read in Module 2 would
  otherwise suggest
```

## Red Flag Summary — Volume & Delivery Context

### CRITICAL Flags
```
❗ Promoter bulk/block selling during a period the company is presenting
  a growth, turnaround, or capacity-expansion narrative, without this
  being explicitly flagged and cross-referenced to Governance/Turnaround checks
❗ A "volume breakout" being reported as institutional accumulation with
  no delivery % or shareholding corroboration at all
❗ Delivery % compared against a fixed universal threshold rather than the
  stock's own historical baseline
```

### HIGH Flags
```
⚠️ Elevated total volume with delivery % below the stock's own baseline,
  on a reported "breakout" day — flagged as unconfirmed but the calling
  skill's output does not carry this caveat forward
⚠️ A single isolated bulk/block deal being treated as a standalone
  actionable signal without monitoring for repetition or corroboration
⚠️ Shareholding pattern data more than one quarter stale being used to
  support a current-period accumulation/distribution claim
```

---

## Output Format

```
VOLUME & DELIVERY ANALYSIS
Company: [Name] | Ticker: [NSE] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

DELIVERY PERCENTAGE:
  Current Session/Week Delivery %:  [X]%
  20-Day Baseline:                   [X]% | 90-Day Baseline: [X]%
  Reading vs. Baseline:               [Above/Below/In-line]
  Price Direction Same Session:        [Up/Down/Flat]
  Interpretation:                      [Genuine accumulation/distribution/
                                        Intraday-driven, unconfirmed]

BULK & BLOCK DEALS (Recent Period):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date | Buyer Category | Seller Category | Qty | Price vs Market | Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pattern Assessment:   [Repeated same-side activity / Isolated / None]
  Promoter-Side Activity: [None / Buying — positive / Selling — flag
                            cross-referenced to Governance & Turnaround checks]

SHAREHOLDING PATTERN CHANGE (Last Disclosed Quarter):
  FII/FPI:              [X]% → [Y]% ([+/-] pts)
  DII:                  [X]% → [Y]% ([+/-] pts)
  Promoter:              [X]% → [Y]% ([+/-] pts) — Reason if changed: [State
                          or "Not disclosed — investigate"]
  Public/Retail:          [X]% → [Y]% ([+/-] pts)

CROSS-CORROBORATION CHECK:
  Delivery/Bulk-Deal Signal vs. Shareholding Filing: [Corroborated /
    Unresolved — categories don't fully reconcile / Contradictory]

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]

OVERALL PARTICIPATION-QUALITY VERDICT: [High-confidence institutional
  accumulation / High-confidence distribution / Unconfirmed — insufficient
  corroboration / Neutral]

FEEDS INTO: [Which calling skill — Swing, Uptrend, Multibagger Discovery,
  Governance checks in Skill 01 — this reading supports]
```

---

## Rules (Non-Negotiable)

```
1. Delivery % is always compared against the stock's own historical
   baseline, never a fixed universal threshold.
2. A volume spike is never labeled "institutional accumulation" without
   delivery % and, where possible, bulk/block or shareholding corroboration.
3. Promoter-side bulk/block selling is always explicitly cross-referenced
   to the Governance Gate (Skill 01) and Turnaround Skill's Signal vs Trap
   checklist, never reported as a neutral data point alone.
4. A single isolated bulk/block deal is treated as a monitoring item, not
   a standalone actionable signal, until repeated or corroborated.
5. Shareholding pattern data is dated explicitly, and its staleness (time
   since last quarterly disclosure) is stated whenever used to support a
   current-period claim.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Core Toolkit — Volume & Delivery Analysis*
*Integrates with: AI_Technical_Analysis_Master_Skill, AI_Swing_Trading_Skill, AI_Uptrend_Momentum_Stock_Skill,
Skill 01 (Master Research, Governance Gate), AI_Turnaround_Analysis_Skill, AI_Multibagger_Discovery_Skill*
<!-- END SYSTEM FILE 18: AI_Volume_Delivery_Analysis_Skill.md -->

---

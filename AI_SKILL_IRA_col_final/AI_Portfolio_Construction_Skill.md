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

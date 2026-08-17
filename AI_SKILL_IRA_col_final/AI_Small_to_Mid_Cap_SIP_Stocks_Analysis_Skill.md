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

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Multibagger Discovery Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Multibagger Discovery Skill
**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Style Specialist — Long-Duration Structural Growth Discovery (3–10 Year Horizon)

---

## CRITICAL AI INSTRUCTION

A multibagger is not a stock that "looks cheap and could go up a lot." It is a business whose earnings power can compound at a high rate for many years because of a structural, evidence-backed reason — not a story. The single most common failure mode in multibagger discovery is narrative substitution: replacing "prove the moat is widening and the TAM is real" with "this sounds like the next big thing." This skill exists to force evidence before excitement at every stage. Claude must classify every candidate into an explicit Stage (Pre-Proof → Scaling) and must never recommend a position size larger than the Stage justifies, regardless of how compelling the story sounds. Size follows evidence, not conviction from narrative.

---

## Purpose

Systematically identify small and emerging companies with genuine potential for outsized, multi-year compounding — driven by underpenetrated markets, emerging or widening moats, disciplined capital allocation, and credible management — while explicitly filtering out story stocks, momentum plays disguised as growth stories, and structurally impaired businesses wearing a turnaround narrative.

---

## Pre-Flight Requirements

```
□ Company name, ticker, current market cap (required)
□ Minimum 3 years of revenue/PAT/ROCE history (if company is younger than 3
  years listed, flag explicitly as "insufficient track record" — do not waive)
□ Investor presentation or annual report with segment/product-level detail
□ Promoter shareholding history (5 years) and pledge status
□ Any available industry TAM estimates (broker reports, industry associations)
□ Concall transcripts (last 4 quarters) — management delivery evidence
□ Peer set at similar revenue scale (for stage-appropriate comparison, not
  comparison against the eventual scaled-up market leader)
□ User's position sizing framework and total portfolio size (for stage-based
  sizing recommendations to be actionable)
```

---

## Analysis Module 1 — Stage Gate Classification (Run First, Always)

```
STAGE 1 — PRE-PROOF:
  Revenue < ₹100 Cr | ROCE improving but not yet excellent (<12%)
  → Business model unproven at scale; thesis rests heavily on TAM + management
  → Position size ceiling: 1–2% at initial entry
  → Evidence bar for even a Stage 1 recommendation: management credibility +
    early unit economics (not just revenue growth %, but per-unit profitability
    trending toward viability)

STAGE 2 — EARLY PROOF:
  Revenue ₹100–500 Cr | ROCE > 12% | moat showing early, specific evidence
  (not "network effects" as a label — actual retention/pricing power data)
  → Position size ceiling: 2–3%
  → This is where most false positives occur — a company can show one or two
    good quarters without the underlying moat being real; require at least
    4–6 quarters of consistent trend, not two

STAGE 3 — GROWING:
  Revenue ₹500–2,000 Cr | ROCE > 15% | moat clear and demonstrable
  (documented pricing power, customer retention data, or cost advantage
  with a specific, named mechanism)
  → Position size ceiling: 3–5%
  → Risk shifts from "does the business work" to "is execution continuing
    and is the runway still long enough to matter"

STAGE 4 — SCALING:
  Revenue > ₹2,000 Cr | ROCE > 20% | moat solidifying, market leadership
  visible in at least one sub-segment
  → Position size ceiling: 5–7%
  → Primary risk is now valuation and law-of-large-numbers deceleration,
    not business model risk — treat as a quality compounder, not a speculative bet

RULE: A company cannot be recommended at a position size associated with a
higher stage than its financial metrics currently support, even if qualitative
evidence (management quality, TAM) is exceptional. Stage is set by the hardest
financial gate the company currently fails, not the easiest one it passes.
```

---

## Analysis Module 2 — Total Addressable Market (TAM) and Penetration Analysis

```
Step 2.1 — TAM Sizing Discipline
  □ TAM estimate must cite a source (industry body, credible broker research,
    government data) — Claude must never invent a TAM figure
  □ Distinguish Total TAM (theoretical maximum) from Serviceable Addressable
    Market (SAM — what this company's specific model can realistically reach)
  □ TAM growth rate: is the market itself growing, or is this a share-gain
    story within a flat/slow-growing market? (Both can work, but the
    multibagger math is very different — share gain requires the company
    to beat competitors, market growth requires only participation)

Step 2.2 — Penetration Gap Assessment
  □ Current market share of the company within its SAM: [%]
  □ Preferred multibagger profile: current penetration < 40% of SAM, meaning
    room to grow 3–10x without needing to "win" the entire category
  □ Historical penetration curve of comparable categories (e.g., how did
    penetration evolve for an earlier-generation analogous business) —
    use only if a genuinely comparable analog exists; do not force-fit

Step 2.3 — Structural Tailwind Verification
  Identify which of these (if any) is genuinely driving the opportunity:
  □ Policy tailwind (PLI, government spending, regulatory mandate)
  □ Demographic tailwind (income growth, urbanization, age cohort shift)
  □ Technology adoption curve (digitization, new capability unlocking demand)
  □ Import substitution / China+1 (must have company-specific evidence,
    not sector-generic assumption)
  → A multibagger candidate ideally has 1–2 tailwinds, clearly named, with
    at least one leading indicator already visible in the company's own data
    (not just industry-level commentary)
```

---

## Analysis Module 3 — Moat Emergence Assessment

```
Step 3.1 — Evidence-Based Moat Testing (Not Label-Based)
  For each claimed moat type, require the specific evidence listed:

  PRICING POWER CLAIM → Evidence required: realized price increases held
    or grew even when a lower-cost competitor entered; gross margin stable
    or expanding through at least one input-cost-inflation cycle

  CUSTOMER STICKINESS CLAIM → Evidence required: repeat order rate, customer
    retention %, or reorder cycle data — not just "customers love the brand"

  COST ADVANTAGE CLAIM → Evidence required: specific, named source of the
    cost edge (backward integration, scale, location, proprietary process)
    and a quantified gap vs. the nearest competitor

  NETWORK EFFECT CLAIM → Evidence required: demonstrated unit economics
    improvement as scale increases (CAC declining, LTV rising, or take-rate
    improving with volume) — the mechanism must be shown, not asserted

  BRAND CLAIM → Evidence required: ability to command a price premium
    versus unbranded/private-label alternatives, sustained over time

Step 3.2 — Moat Trajectory
  □ Is the moat widening (competitive gap growing) or merely holding?
  □ What would cause the moat to erode — name the specific threat
    (new entrant with capital, technology shift, regulatory change,
    customer concentration risk)
  □ Durability estimate: rough years before the current moat advantage
    would need to be refreshed or extended
```

---

## Analysis Module 4 — Management and Capital Allocation Track Record

```
□ Promoter holding: >40% preferred (skin in the game); trend over 3 years
  (increasing = strong signal; declining without stated reason = caution)
□ Promoter pledge: must be 0% or near-0% — any pledge above 10% during
  a "growth story" phase is disqualifying at Stage 1–2 (the promoter
  should not need to leverage personal holdings if the story is real)
□ Guidance delivery: track the last 4–8 quarters of management guidance
  vs. actual — a credible multibagger management under-promises and
  over-delivers more often than not; chronic guidance misses are a red flag
  regardless of how good the narrative sounds
□ Capital allocation history: has the company made value-accretive
  reinvestment decisions (expansion into adjacent, provably profitable
  areas) or has it diversified into unrelated, unproven areas
  ("diworsification") — the latter is a common way managements destroy
  a good core business while chasing a second narrative
□ Related-party transactions: scrutinize for value leakage to promoter-
  controlled entities outside the listed company — a specific and
  underrated way small-cap "growth" masks value extraction
```

---

## Analysis Module 5 — Financial Quality Gates (Mandatory, All Must Pass for Stage 2+)

```
□ Revenue CAGR > 20% over a minimum 3-year window (single-year spikes do
  not qualify — require consistency, not a one-off base effect)
□ ROCE trend: improving, and trending toward or above 15%
□ Free cash flow: positive, or on a clearly visible path to positive within
  a stated, reasonable horizon (state the horizon explicitly — "eventually"
  is not an acceptable answer)
□ Debt discipline: Debt/EBITDA < 3x, and not rising faster than EBITDA
□ Working capital discipline: receivable days not silently expanding while
  revenue growth is reported as strong (a classic way growth quality
  is overstated — check this every time)

Any company failing 2 or more of these gates cannot be classified above
Stage 1 regardless of narrative quality, and should carry an explicit
warning that the growth being reported may not yet be translating into
compounding shareholder value.
```

---

## Multibagger Scoring Framework (0–100)

| Category | Max Points | What It Measures |
|---|---|---|
| Revenue Growth Quality (consistency, not one year) | 20 | CAGR + consistency across years |
| Moat Stage & Evidence Strength | 20 | Emerging / Narrow / Wide + named mechanism |
| Management Track Record | 15 | Guidance delivery, capital allocation discipline |
| Market Opportunity (TAM × penetration gap) | 15 | Sourced TAM, SAM, current share |
| Financial Quality (ROCE, FCF, balance sheet) | 15 | Gate pass rate from Module 5 |
| Governance Quality | 10 | Pledge level, RPT cleanliness, board quality |
| Valuation (appropriateness for stage, not absolute cheapness) | 5 | Is price reasonable for the stage and growth rate |

---

## Analysis Module 6 — Exit and Trim Discipline (Upgrade — Previously Missing)

```
This skill previously specified entry/build-up rules only. A multibagger
thesis that plays out still needs a discipline for taking money off the
table — silence here defaults investors to "hold forever," which is not
the same as "the thesis is still intact."

□ Stage-Advancement Trim: when a Stage 1–2 position advances two full
  stages faster than the base-case runway assumed (Module Growth Runway),
  trim toward the NEW stage's position ceiling rather than letting size
  drift up passively with price — this locks in gains without fully exiting
□ Valuation Divergence Trim: if price appreciation outpaces the
  fundamental growth runway (Scoring Module) such that the stock now
  trades meaningfully above what the Stage 4 valuation band would
  justify, trim even if the business narrative is fully intact —
  a good business at a bad price is still a poor forward return
□ Key-Man / Succession Trigger: an unplanned exit of the founder/promoter
  who was central to the moat and capital-allocation thesis is a
  mandatory re-underwrite event, not a routine monitoring note — treat
  as a Tier 2 gap per the Universal Skill Failure Protocol until the
  successor's credibility is independently evidenced
□ Never fully exit solely because a stock has "gone up a lot" — trims are
  tied to the specific triggers above, not to price appreciation alone
```

## Analysis Module 6 — Exit Discipline (v_0.0 Addition)

```
Multibagger Discovery is entry-and-staging focused by design, but a
multi-year holding period without a defined exit framework leaves the
investor exposed to giving back gains with no discipline once the thesis
plays out. This module defines when to trim, hold, or fully exit.

TIER 1 - THESIS MATURATION EXIT (Partial):
  When a Stage 3-4 company's growth decelerates toward GDP-plus levels
  (from the >20% CAGR bar in Module 5) for 4+ consecutive quarters, with
  no new TAM/moat evidence emerging (Module 2/3), trim 30-50% of the
  position. This is not a thesis failure, it is thesis completion - the
  compounding phase this skill screens for has largely played out.

TIER 2 - VALUATION-DRIVEN TRIM (Partial):
  If the stock re-rates to a P/E or EV/EBITDA multiple more than 2x its
  own 5-year average AND more than 1.5x the peer group average, with no
  corresponding step-up in growth quality or moat evidence, trim toward
  the position's original Tier ceiling (per AI_Portfolio_Construction_
  Skill) even if the long-term thesis remains intact. Multibagger
  investing requires patience through volatility, not indifference to
  valuation extremes.

TIER 3 - THESIS BREAK EXIT (Full):
  Any of the following triggers a full exit, not a trim:
  - Two or more Financial Quality Gates (Module 5) fail simultaneously
    after previously passing
  - Promoter pledge crosses 20% at any point post-entry
  - A Critical Flag from the Red Flag Summary below is newly triggered
  - Moat erosion evidence (a named competitive threat materializing,
    not merely a risk being discussed) is confirmed

TIER 4 - STAGE-BASED REVIEW CADENCE:
  Stage 1-2 positions: review every quarter (fast-moving evidence window)
  Stage 3-4 positions: review every 2 quarters (slower-moving, but do not
  extend beyond 6 months without a check given position size is largest here)

RULE: Never exit a multibagger position purely on short-term price
volatility unaccompanied by any of the Tier 1-3 triggers above - price
volatility without fundamental deterioration is the normal texture of
this investing style, not a signal.
```


## Red Flag Summary — Multibagger Context

### CRITICAL Flags
```
❗ Promoter pledge > 20% during a "growth story" narrative phase
❗ Revenue growth reported strong while OCF/PAT ratio deteriorating (growth
  quality is being funded by working capital stretch, not real cash generation)
❗ Diworsification: capital being deployed into unrelated new segments while
  the core business's growth is decelerating
❗ TAM claim with no cited, credible source
❗ 3+ consecutive quarters of guidance materially missed despite unchanged
  or increasingly confident management tone (credibility gap widening)
```

### HIGH Flags
```
⚠️ Single-customer or single-geography concentration > 40% of revenue
  with no diversification trend
⚠️ Moat claim based on a label ("network effects," "brand") without the
  specific evidence required in Module 3.1
⚠️ Stage classification implied by the user or narrative is higher than
  what the financial gates in Module 5 actually support
⚠️ Recent capital raise (QIP/preferential) at a steep discount to CMP
  (may signal the company itself doubts current valuation is sustainable,
  or needed cash urgently)
⚠️ Related-party transaction volume rising as a % of revenue
```

---

## Output Format

```
MULTIBAGGER DISCOVERY REPORT
Company: [Name] | Ticker: [NSE] | Stage: [1/2/3/4] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════════

MULTIBAGGER SCORE: [0–100]
  Revenue Growth Quality:   [/20]
  Moat Stage & Evidence:    [/20]
  Management Track Record:  [/15]
  Market Opportunity:       [/15]
  Financial Quality:        [/15]
  Governance Quality:       [/10]
  Valuation (stage-adjusted):[/5]

STAGE CLASSIFICATION: Stage [X] — [PRE-PROOF/EARLY PROOF/GROWING/SCALING]
  Stage Evidence: [Which specific financial gates set this stage — the
  hardest-failed metric, not the easiest-passed one]

TAM & PENETRATION:
  TAM Source:        [Cited source]
  SAM Estimate:       ₹[X] Cr
  Current Penetration:[%] of SAM
  Structural Tailwind:[Named — policy/demographic/tech/import-substitution]
  Leading Indicator:  [Company-specific evidence the tailwind is materializing]

MOAT ASSESSMENT:
  Claimed Type:      [Pricing power / stickiness / cost / network / brand]
  Evidence Provided:  [Specific data supporting the claim — or "insufficient
                        evidence, claim not yet verified"]
  Trajectory:         [Widening / Holding / Uncertain]
  Erosion Risk:        [Named specific threat]

MANAGEMENT & CAPITAL ALLOCATION:
  Promoter Holding:   [%] (Trend: [X])
  Promoter Pledge:    [%] — [Clean / Caution / Disqualifying]
  Guidance Delivery:  [X/4 last 4 quarters met]
  Capital Allocation: [Disciplined reinvestment / Diworsification signs / Neutral]

FINANCIAL QUALITY GATES:
  Revenue CAGR (3yr):   [%] — [Pass/Fail]
  ROCE Trend:           [X% → Y%] — [Pass/Fail]
  FCF Status:           [Positive/Path to positive by ~[year]/Fail]
  Debt/EBITDA:          [X]x — [Pass/Fail]
  Working Capital:      [Disciplined/Deteriorating] — [Pass/Fail]
  Gates Passed:         [X/5]

GROWTH RUNWAY:
  Revenue Target:     ₹[X] Cr in [Y] years at [Z]% CAGR (stated assumption basis)
  Return Potential:   [X]x in [Y] years — base case, NOT a promise

POSITION SIZING:
  Stage-Based Ceiling: [1–2% / 2–3% / 3–5% / 5–7%]
  Recommended Entry:   [%] — [Initial tranche / build-up plan]
  Build-Up Trigger:    [What evidence, if it appears, justifies adding]

CRITICAL FLAGS:        [Count + list, or "None detected"]
HIGH FLAGS:             [Count + list, or "None detected"]

⚠️ MANDATORY WARNING: This is a high-uncertainty, long-duration bet whose
outcome depends on evidence continuing to accumulate over multiple years.
Position size per Stage ceiling above — do not exceed regardless of conviction.
```

---

## Rules (Non-Negotiable)

```
1. Stage is set by the hardest-failed financial gate, never by narrative strength.
2. Position size ceiling is dictated by Stage — never override upward for conviction.
3. TAM figures require a cited source; invented TAM numbers are prohibited.
4. Moat claims require the specific evidence type in Module 3.1 — a label
   alone ("strong brand," "network effects") is not sufficient to score points.
5. A single strong quarter never upgrades a Stage classification — require the
   full trailing window specified for that stage.
6. Promoter pledge above 20% is disqualifying for new Stage 1–2 recommendations.
7. Diworsification evidence (capital flowing to unrelated new segments while
   core growth decelerates) must be flagged even if headline revenue growth
   looks intact.
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Style Specialist — Multibagger Discovery*
*Integrates with: Skill 04 (Early Multibagger Finder), Forensic Accounting Skill, AI_Future_Growth_Skill,
AI_Concentrated_SmallCap_Style_Thinking_Skill, Skill 15 (Pre-Investment Master Checklist)*
# Multibagger Finder — Quick Screening Checklist (Addendum v_0.0)

**Paste Target:** AI_Multibagger_Discovery_Skill.md — insert as new "Analysis Module 0" before the existing "Analysis Module 1 — Stage Gate Classification"

---

## Why This Addendum Exists

The skill's existing modules (Stage Gate, TAM, Moat, Management, Financial Quality Gates) are a **deep, one-stock-at-a-time** analysis — thorough, but too slow to run against a list of 20–50 candidate names. This addendum adds a **fast numeric pre-filter**: a single pass/fail screen you run first on a batch of stocks, so the deep 6-module analysis only gets applied to names that already clear the basic bar.

---

## Analysis Module 0 — Quick Numeric Pre-Filter (Run Before Module 1)

**Purpose:** Eliminate obviously disqualified candidates in seconds, before spending deep-analysis effort on them.

```
□ Revenue CAGR > 20% over the last 3 years (reject if not met — no exceptions at this stage)
□ ROCE > 15% in the most recent full year (reject if materially below, unless explicitly flagged as a turnaround candidate — see Module 1)
□ Debt/Equity < 0.5 (reject if higher, unless the business is asset-heavy by nature — e.g., capital goods — and Module 5's Debt/EBITDA <3x still passes)
□ Promoter Holding > 50% (flag, don't auto-reject, if between 35–50%; reject below 35% unless institutional ownership quality is independently verified as strong)
□ Promoter Pledge < 10% of holding (reject if higher — this is a hard gate, not a soft flag)
□ Average Daily Traded Value > ₹1 crore over the last 30 days (reject if lower — insufficient liquidity to build or exit a position safely)
□ Market Cap > ₹500 crore (reject if lower, unless explicitly operating in Microcap Research Protocol mode — see Skill 25 in 04_Skills_Reference_v_0.0.md, which has its own separate liquidity and risk rules)
```

**Pass Rule:** A candidate must pass **all 7** checks to proceed to the full Module 1–6 deep analysis. Failing 1 check → flag as "Marginal — proceed only with explicit override reasoning." Failing 2 or more → reject, do not proceed to deep analysis.

**Output for a batch screen:**

```
Screened: [N] candidates
Passed all 7 gates: [list]
Marginal (1 gate failed): [list + which gate]
Rejected (2+ gates failed): [list, no further detail needed]
```

---

## Relationship to Existing Module 5

Module 5 (Financial Quality Gates) already contains Revenue CAGR, ROCE, and Debt/EBITDA checks — this addendum does **not** duplicate those; it pulls the same thresholds forward into a faster pre-filter so they can be applied to a whole list at once, before the FCF, working-capital, and governance depth of Module 5 is applied to the survivors. Promoter Holding, Promoter Pledge, Liquidity, and Market Cap floor are genuinely new — they were previously only implied inside the Governance Quality scoring line, never stated as explicit numeric gates.

---

## Self-Audit

- ✓ No conflict with existing Module 1 (Stage Gate) or Module 5 (Financial Quality Gates) — this runs strictly before both
- ✓ Reuses the same Revenue CAGR / ROCE / Debt thresholds already in the skill, doesn't redefine them differently
- ✓ Adds 4 genuinely new numeric gates (Promoter Holding, Pledge, Liquidity, Market Cap floor) that were previously unstated

---

**Document:** Multibagger_Quick_Screen_Addendum.md
**Version:** v_0.0
**Paste Into:** AI_Multibagger_Discovery_Skill.md (as Analysis Module 0, before Module 1)
# Top-12 Combination Checks Addendum v_0.0

**Paste Target:** `Multibagger_Quick_Screen_Addendum_v_0.0.md` (or directly into `AI_Multibagger_Discovery_Skill.md` Module 0 once merged) — insert as "Module 0B — Combination Confirmation Checks," run after the 7-gate Quick Pre-Filter passes.

**Scope:** Only the top 4 priority categories from the source document's own hierarchy (Red Flag Detection, Cash Flow Quality, Balance Sheet Strength, Capital Allocation) — skipping Valuation, Technical Momentum, and the other 8 lower-priority libraries, which are already covered elsewhere (Valuation in DCF skill, Technical in Technical Analysis skill).

---

## Module 0B — Combination Confirmation Checks

Run these 12 checks on any candidate that passed Module 0's 7-gate pre-filter. Each is a two-metric combination — more reliable than either metric alone.

### Category 1 — Red Flag Detection (highest priority — any match here overrides a positive screen)

```
1. PAT growing BUT Cash from Operations falling
   → Flag: earnings quality concern, do not proceed without resolving

2. Receivables growing faster than Sales Growth
   → Flag: possible aggressive revenue recognition

3. Debt increasing AND Interest Coverage falling simultaneously
   → Flag: debt trap pattern forming
```

### Category 2 — Cash Flow Quality (confirms earnings are real)

```
4. Cash from Operations > Net Profit × 1.20
   → Positive: profit is well-backed by cash, stronger than reported PAT suggests

5. Free Cash Flow positive for 3 consecutive years
   → Positive: business is self-funding, not dependent on external capital

6. Operating Cash Flow trend improving over 5 years (not just latest year)
   → Positive: sustained cash generation, not a one-off
```

### Category 3 — Balance Sheet Strength (survivability check)

```
7. Debt/Equity < 0.30
   → Positive: low balance-sheet risk

8. Interest Coverage Ratio > 6
   → Positive: comfortable debt servicing capacity

9. Current Ratio > 2
   → Positive: strong short-term liquidity
```

### Category 4 — Capital Allocation (management quality signal)

```
10. ROCE (current) > Average ROCE 3 Years
    → Positive: capital efficiency improving, not just historically good

11. ROE (current) > Average ROE 5 Years
    → Positive: same signal on equity returns

12. ROCE > ROE
    → Positive: business is not relying on financial leverage to
      generate its equity returns — capital efficiency is organic
```

---

## Scoring Integration

Add to the existing Multibagger Scoring Framework (0–100 table, already in the skill) as a modifier:

```
Category 1 (Red Flag Detection) match → subtract 15 points per flag from
   total score, regardless of how strong other categories score
   (consistent with the skill's existing Financial Quality Gates:
   any 2+ gate failures already cap classification at Stage 1)

Category 2/3/4 matches → each confirmed check adds up to +2 points to the
   Financial Quality (15 max) scoring line already in the framework —
   these checks refine that existing line, they don't create a new one
```

---

## Self-Audit

- ✓ Only 12 of 250+ possible combinations included — the 4 highest-priority categories per the source document's own stated hierarchy
- ✓ No new scoring category created — Category 1 reinforces the existing Financial Quality Gates (Module 5); Categories 2–4 refine the existing Financial Quality scoring line rather than adding a new axis
- ✓ Explicitly skips Valuation and Technical combination libraries — those already live in `AI_DCF_Valuation_Skill.md` and `AI_Technical_Analysis_Master_Skill.md` respectively

---

**Document:** Top12_Combination_Checks_Addendum_v_0.0.md
**Version:** v_0.0
**Paste Into:** Multibagger Quick Screen (Module 0B, after the 7-gate pre-filter)

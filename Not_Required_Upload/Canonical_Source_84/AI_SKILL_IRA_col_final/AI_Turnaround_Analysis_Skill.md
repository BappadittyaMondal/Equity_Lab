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

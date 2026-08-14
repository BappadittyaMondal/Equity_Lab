<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Concentrated SmallCap Style Thinking Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Concentrated Small-Cap Style Thinking Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Heuristic Lens — Concentrated, Under-the-Radar Small-Cap Investing Pattern

---

## CRITICAL AI INSTRUCTION

This skill is a **heuristic lens**, not a personality simulation and not investment advice attributed to any named individual. It is built from publicly reported, widely discussed patterns associated with a concentrated, deeply-researched, under-the-radar small-cap investing style — the kind of approach characterized by small portfolios (often single-digit number of holdings), multi-year holding periods, extensive on-the-ground and unconventional due diligence, and a willingness to be early and look wrong for extended periods before being proven right. Claude must apply this as a **way of asking questions and weighting evidence**, never as a claim that any real person endorses a specific stock or would make a specific decision. Do not attribute quotes, specific past picks, or personal opinions to any individual. This lens supplements — it never replaces — the mandatory gates in Forensic Accounting, Governance, and the Pre-Investment Master Checklist.

---

## Purpose

Apply a concentrated, deep-diligence, contrarian-leaning analytical lens to small-cap candidates — emphasizing extreme business-model understanding, unconventional evidence-gathering, comfort with being early against consensus, and extreme selectivity (favoring very few, very high-conviction positions over broad diversification) — as a complement to, not a replacement for, the standard IERL research process.

---

## Pre-Flight Requirements

```
□ Confirm the user wants this specific heuristic lens applied (this is a
  style choice, not a default) — if invoked generically ("analyze this
  small cap"), default to Skill 01/04 instead and only apply this lens
  if the user signals interest in a concentrated, contrarian approach
□ Company must already have passed, or be run alongside, the standard
  Governance Gate and Forensic Gate from Skill 01 — this lens sharpens
  conviction, it does not substitute for the baseline safety checks
□ Access to primary sources beyond standard financial disclosures where
  possible: dealer/distributor channel checks, customer reviews, import-
  export data, job postings (hiring signal), local news, patent filings
□ User's willingness to hold a concentrated position (this lens is
  only coherent alongside high position sizing — presenting it alongside
  a 1-2% diversified position undersells the approach's own logic)
```

---

## Analysis Module 1 — The Concentration Mindset

```
Core premise of this lens: if you have done truly deep, unconventional
diligence on a business and have very high conviction, diversifying away
from that conviction into 20-30 mediocre-conviction ideas dilutes your
best insight rather than protecting you. This is the opposite instinct
from standard portfolio theory diversification, and it requires a much
higher diligence bar to be responsible.

Implication for Claude's output when this lens is invoked:
□ Push for FEWER, deeper ideas rather than a list of 5-10 plausible names
□ For each idea presented, go materially deeper than a standard Skill 01
  report on the SPECIFIC things that would make or break the thesis —
  not a comprehensive checklist, but an intense focus on the 2-3 variables
  that actually matter most for this specific business
□ Explicitly note where conviction is NOT yet high enough to warrant
  concentration — "interesting but not yet a concentrated-position-grade
  idea, here is specifically what more diligence would need to show"
```

---

## Analysis Module 2 — Under-the-Radar Screening Criteria

```
□ Limited or no institutional/analyst coverage (fewer eyes on the name =
  higher chance of a genuine information or insight edge, but also higher
  execution/liquidity risk — both must be stated)
□ Business model that is not easily understood from a 5-minute read of
  the annual report — genuine complexity or obscurity that would deter
  a casual screener, but which becomes an edge once properly understood
□ Situated in a niche, unglamorous, or currently out-of-favor category —
  actively look at where sentiment or narrative attention is LOW, not high
  (the opposite screening direction from momentum-based approaches)
□ Owner-operator or promoter-driven management with a long personal
  history in the specific business, ideally with a track record the
  market has not yet fully re-rated for
```

---

## Analysis Module 3 — Unconventional Diligence Prompts

```
Beyond standard financial statement analysis, this lens explicitly prompts
for evidence types that a purely desk-based screen would miss. Claude
should proactively ask the user whether any of the following are available,
and incorporate them if so — while being explicit when they are NOT
available (never fabricate this kind of ground-level evidence):

□ Channel checks: dealer/distributor sentiment, reorder patterns,
  inventory levels reported informally in trade channels
□ Customer-side evidence: reviews, satisfaction signals, switching
  behavior for the company's specific product/service
□ Competitive intelligence: what are direct competitors NOT able to
  replicate about this company's specific advantage, and why
□ Regulatory/industry-body filings beyond the standard annual report
  (e.g., import-export data, sector association disclosures)
□ Hiring patterns / job postings (a leading indicator of where the
  company is actually investing, sometimes ahead of what commentary suggests)
□ On-the-ground factory/plant/store visit reports, if available
  (explicitly note this is rarely available to a remote research process
  and treat its absence as a stated diligence gap, not silently ignored)

If none of this ground-level evidence is available, state explicitly:
"This analysis is limited to desk-based financial and disclosure review;
the unconventional diligence this lens typically emphasizes was not
available — treat conviction accordingly as more moderate than the
lens would ideally support."
```

---

## Analysis Module 4 — Contrarian Comfort and Patience Framework

```
□ Explicitly separate "the market disagrees with this thesis right now"
  from "the market has good reason to disagree" — the lens requires being
  able to articulate WHY the market's current view is wrong or incomplete,
  not just noting that the stock is unpopular
□ State the expected time horizon for the thesis to be recognized —
  concentrated contrarian positions typically require patience measured
  in years, not quarters; if the thesis logically requires a near-term
  catalyst, this may be a better fit for Skill 03 (Positional) than this lens
□ Pre-define, explicitly and in writing as part of the output, what
  would prove the thesis WRONG — this lens's biggest risk is conviction
  hardening into stubbornness; an explicit invalidation condition set in
  advance is the discipline that prevents that
□ Distinguish "the stock price is down and I am adding" (average-down
  because thesis intact, with fresh evidence reviewed) from "the stock
  price is down and I am doubling down because I don't want to be wrong"
  (an emotional/ego-driven add) — Claude must ask what fresh evidence,
  if any, justifies conviction being maintained or increased after a decline
```

---

## Analysis Module 5 — Profit-Taking Discipline and Key-Man Risk (Upgrade — Previously Missing)

```
This lens previously covered entry and patience but not exit — a
concentration approach without a trim discipline can turn a winning
thesis into an outsized, unmanaged risk.

□ Define, in advance, what "the thesis has been recognized by the market"
  looks like (specific valuation/re-rating level) — at that point, trim
  toward standard portfolio ceilings (per AI_Portfolio_Construction_Skill)
  even if long-term conviction in the business remains high; concentration
  is a tool for capturing an insight the market hasn't priced yet, not a
  permanent state once that gap has closed
□ Key-Man Risk Test: since this lens favors owner-operator businesses,
  explicitly assess and state what happens to the thesis if the specific
  individual driving it is unexpectedly unavailable (health, succession,
  departure) — a concentrated position resting heavily on one person's
  judgment carries materially higher single-point-of-failure risk than a
  diversified holding in the same sector, and this must be disclosed
  alongside the conviction rating, not left implicit
```

## Red Flag Summary — Concentrated Style Context

### CRITICAL Flags
```
❗ Concentration recommended without the company having passed the
  standard Governance and Forensic Gates from Skill 01
❗ "Contrarian" framing applied to a stock where the market's negative
  view is actually well-supported by deteriorating fundamentals (i.e.,
  this is a value trap being mistaken for a contrarian opportunity —
  cross-check explicitly against AI_Turnaround_Analysis_Skill's Signal
  vs Trap checklist before proceeding)
❗ No stated invalidation condition for the thesis
```

### HIGH Flags
```
⚠️ Limited institutional coverage cited as a positive (edge) without also
  flagging the corresponding liquidity risk that comes with it
⚠️ Ground-level/unconventional diligence claimed as a basis for conviction
  but not actually available or provided
⚠️ Position sizing implied or recommended significantly above what the
  user's stated risk tolerance or portfolio structure (per AI_Portfolio_
  Construction_Skill) would otherwise support
```

---

## Output Format

```
CONCENTRATED SMALL-CAP LENS ANALYSIS
Company: [Name] | Ticker: [NSE] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

BASELINE GATE CHECK:
  Governance Gate (Skill 01):  [Pass/Fail/Not yet run]
  Forensic Gate (Skill 01):    [Pass/Fail/Not yet run]
  → If either not passed, this lens cannot proceed to a conviction rating.

UNDER-THE-RADAR PROFILE:
  Institutional Coverage:      [Minimal/Moderate/High] — liquidity implication: [X]
  Complexity/Obscurity Factor: [What specifically makes this hard to screen
                                 casually, and why that is an edge once understood]
  Sentiment Context:           [Out-of-favor/Neutral/In-favor — lens favors
                                 out-of-favor]

THE 2–3 VARIABLES THAT ACTUALLY MATTER:
  1. [Specific variable] — [Why this, above all else, determines the outcome]
  2. [Specific variable] — [Same]
  3. [Specific variable, if applicable] — [Same]

UNCONVENTIONAL DILIGENCE AVAILABLE:
  [List what ground-level evidence was actually available and incorporated,
  or state explicitly: "Desk-based review only — ground-level diligence
  this lens typically emphasizes was not available"]

CONTRARIAN THESIS ARTICULATION:
  Why the Market Disagrees:   [Current consensus view]
  Why That View Is Incomplete/Wrong: [Specific reasoning, not just disagreement]
  Expected Recognition Horizon: [Years, stated explicitly]
  Value-Trap Cross-Check:      [Confirmed this is NOT a deteriorating business
                                 mistaken for contrarian opportunity — reference
                                 to Turnaround Skill's Signal vs Trap check if relevant]

INVALIDATION CONDITION (Written in Advance):
  [Explicit, specific condition that would prove this thesis wrong]

CONCENTRATION SUITABILITY:
  Conviction Level:            [High enough for concentration / Not yet —
                                 here is what more diligence would need to show]
  Position Sizing Note:        [Cross-check against AI_Portfolio_Construction_
                                 Skill Tier ceilings — even high conviction should
                                 not exceed portfolio-level hard caps]

⚠️ REMINDER: This is a heuristic lens for how to think about the idea, not
investment advice attributed to any individual, and does not override the
mandatory Governance/Forensic gates or portfolio-level position ceilings.
```

---

## Rules (Non-Negotiable)

```
1. This lens never substitutes for the Governance Gate or Forensic Gate —
   it sharpens conviction after those gates are passed, never before.
2. No specific past trades, quotes, or opinions are ever attributed to any
   named individual — this is a generic pattern-based lens only.
3. Every application of this lens must include an explicit, written-in-
   advance invalidation condition.
4. Contrarian framing must be explicitly cross-checked against the
   Turnaround Skill's Signal vs Trap checklist to avoid mistaking a
   genuine value trap for a contrarian opportunity.
5. Position sizing recommendations under this lens are still bound by the
   hard caps in AI_Portfolio_Construction_Skill — conviction does not
   override portfolio-level risk architecture.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Heuristic Lens — Concentrated Small-Cap Style*
*Integrates with: Skill 01 (Master Research — Governance/Forensic Gates), AI_Turnaround_Analysis_Skill,
AI_Multibagger_Discovery_Skill, AI_Portfolio_Construction_Skill, Skill 15 (Pre-Investment Master Checklist)*

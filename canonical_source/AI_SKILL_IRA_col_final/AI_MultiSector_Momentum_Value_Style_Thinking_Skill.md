<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI MultiSector Momentum Value Style Thinking Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Multi-Sector Momentum-Value Style Thinking Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Heuristic Lens — Diversified, Sector-Rotating, Inflection-Driven Investing Pattern

---

## CRITICAL AI INSTRUCTION

This skill is a **heuristic lens**, not a personality simulation and not investment advice attributed to any named individual. It is built from publicly reported, widely discussed patterns associated with a diversified, sector-rotating, inflection-point-driven investing style — the kind of approach characterized by broader diversification across many sectors, active rotation as cycles and catalysts change, a blend of value discipline with momentum/earnings-inflection triggers, and a willingness to exit a position once its specific catalyst has played out rather than holding indefinitely. This is deliberately the OPPOSITE instinct from the Concentrated Small-Cap lens — where that lens says "find the few best ideas and hold with conviction for years," this lens says "cast a wider net, rotate toward where the evidence and price momentum currently align, and don't be sentimental about exiting when the setup changes." Claude must apply this as a way of structuring analysis and portfolio thinking, never as a claim that any real person endorses a specific stock or would make a specific decision.

---

## Purpose

Apply a diversified, catalyst-driven, sector-rotation-aware analytical lens — combining valuation discipline with earnings-inflection and price-momentum triggers across a broader universe of names — as a complement to, not a replacement for, the standard IERL research process. This lens is best suited to medium-term (Skill 03 Positional-adjacent) time horizons and explicitly favors turnover and rotation over long-duration static holding.

---

## Pre-Flight Requirements

```
□ Confirm the user wants this specific heuristic lens applied — this is a
  style choice; if invoked generically, default to Skill 08 (Sector Rotation)
  and Skill 03 (Positional) and only layer this lens on top when signaled
□ Access to sector-level relative strength and earnings-revision data
  (per Skill 08's activation sequence — this lens leans heavily on that skill)
□ User's tolerance for higher portfolio turnover (this lens is only coherent
  with a willingness to exit positions relatively promptly once a catalyst
  plays out, distinct from a buy-and-hold-for-years approach)
□ Diversification target: this lens explicitly favors a broader number of
  positions (meaningfully more than the Concentrated lens) — confirm this
  aligns with the user's portfolio structure via AI_Portfolio_Construction_Skill
```

---

## Analysis Module 1 — The Rotation Mindset

```
Core premise of this lens: rather than finding a handful of businesses to
hold indefinitely, this style continuously re-scans the opportunity set
across sectors, looking for where (a) valuation is reasonable relative to
history/peers, AND (b) a specific, identifiable inflection point (earnings
acceleration, margin recovery, a policy tailwind newly materializing) is
either underway or about to become visible to the broader market. Positions
are held while the inflection thesis is playing out and the price trend
confirms it — and are exited, without sentimentality, once the catalyst is
priced in or the setup deteriorates, freeing capital to rotate to the next
best-positioned opportunity.

Implication for Claude's output when this lens is invoked:
□ Favor a WIDER set of ideas across MULTIPLE sectors rather than a narrow,
  single-sector-deep list — explicitly check that ideas presented are not
  clustered in one theme unless that clustering is itself the deliberate,
  stated rotation call
□ For every idea, require BOTH a valuation angle (why is this not expensive
  relative to its own history/peers) AND a momentum/inflection angle (what
  is changing right now that the market has not yet fully re-rated for) —
  an idea with only one of these two legs is a weaker fit for this lens
  and should be flagged as such rather than presented with full conviction
□ Build in an explicit exit/rotation trigger for every idea from the outset —
  this lens's discipline is knowing when to move on, not just when to enter
```

---

## Analysis Module 2 — The Value + Inflection Screen

```
Step 2.1 — Valuation Leg (Necessary, Not Sufficient)
  □ Current valuation multiple (P/E, EV/EBITDA, or sector-appropriate metric
    per Skill 07) vs. its own 3-5 year historical average
  □ Current valuation vs. sector peer average
  □ This lens does NOT require deep-value "cheap for a structural reason"
    situations — reasonable/fair valuation with a credible inflection catalyst
    is preferred over statistically cheap stocks with no visible catalyst
    (the latter can stay cheap indefinitely, which defeats this lens's
    rotation-based capital efficiency goal)

Step 2.2 — Inflection Leg (The Differentiator)
  Identify and name the SPECIFIC inflection driver, which must be one of:
  □ Earnings inflection: 2+ consecutive quarters of accelerating growth
    or margin expansion after a period of stagnation/decline
  □ Estimate revision inflection: sell-side/consensus estimates being
    revised UP for 2+ consecutive periods after a period of downgrades
    or flat estimates (a specific, checkable signal, not a vague "sentiment
    is improving" claim)
  □ Policy/regulatory inflection: a specific, dated policy change that
    newly and directly benefits this company/sector, distinguishable from
    a long-standing tailwind already priced in
  □ Capacity/capex inflection: new capacity coming online that visibly
    changes the growth or margin trajectory, distinct from capacity that
    has been "coming soon" for many quarters without materializing
  □ Balance sheet inflection: a specific deleveraging or refinancing event
    that materially changes the risk profile and could trigger a re-rating

  → An idea without a specifically named, checkable inflection driver from
    this list does not qualify for this lens — "the stock looks like it's
    turning" is not itself evidence; state what specifically is turning.

Step 2.3 — Price Confirmation
  □ Cross-check with the technical relative-strength framework from
    Skill 08/Skill 03 — is price action beginning to confirm the
    fundamental inflection, or is the thesis still purely anticipatory?
  □ Purely anticipatory (no price confirmation yet) ideas should be sized
    smaller and flagged as earlier-stage/higher-uncertainty within this lens
```

---

## Analysis Module 3 — Sector Rotation Discipline

```
□ Maintain awareness across the FULL sector universe (per Skill 08's
  activation sequence), not just the sector currently under discussion —
  this lens's edge comes partly from comparing opportunity sets across
  sectors, not evaluating one sector in isolation
□ Explicitly compare the current idea's inflection strength against the
  best available inflection setups in OTHER sectors at the same time —
  "is this actually the best use of this capital right now, or merely a
  reasonable one" is the right question under this lens
□ Track portfolio-level sector exposure actively — because this lens
  naturally rotates toward whatever sector currently shows the best
  inflection setups, concentration can build up unintentionally; cross-
  check against AI_Portfolio_Construction_Skill's sector ceiling regularly
```

---

## Analysis Module 4 — Exit and Rotation Triggers

```
Define explicitly, for every idea, BEFORE entry:
□ Catalyst-Realized Exit: the specific inflection driver named in Module 2
  has now visibly played out (e.g., the estimate revisions have stopped,
  the capacity is now fully reflected in results) — exit and look for the
  next setup, regardless of whether the stock could theoretically go higher
□ Thesis-Broken Exit: the inflection driver fails to materialize as
  expected within a stated reasonable window — exit promptly rather than
  waiting indefinitely for it to eventually show up
□ Valuation-Exhausted Exit: the stock has re-rated to a premium beyond
  its own historical range or peer group without a corresponding step-up
  in the underlying business quality — the value leg of Module 2.1 is gone
□ Better-Opportunity Rotation: a materially stronger inflection setup has
  emerged elsewhere and portfolio capital is constrained — this lens
  explicitly permits rotating out of an "okay, still working" position
  into a better one, distinct from a buy-and-hold discipline that would
  discourage this kind of turnover
```

---

## Analysis Module 5 — Turnover Cost and Tax Drag (Upgrade — Previously Missing)

```
This lens explicitly encourages rotation, which was previously specified
without quantifying its cost — high turnover is only worth it if the
edge captured exceeds the drag.

□ For every rotation decision, state the approximate round-trip cost
  (brokerage/STT/exchange charges) and the tax treatment of the exit
  (STCG if under 12 months — the common case for this lens's typical
  holding periods; LTCG if over)
□ A "better opportunity" rotation (Module 4) should only be executed when
  the expected incremental return of the new idea, net of exit tax and
  round-trip cost on the old position, still clears a meaningful margin —
  do not rotate for a marginal setup-quality improvement that the cost/tax
  drag would erase
□ Track cumulative annual turnover-driven cost/tax drag at the portfolio
  level as an explicit line item when reporting this lens's performance,
  not just the gross idea-level returns
```

## Red Flag Summary — Multi-Sector Momentum-Value Context

### CRITICAL Flags
```
❗ Idea presented under this lens with no specifically named, checkable
  inflection driver (Module 2.2) — this is not a fit for the lens
❗ Portfolio-level sector concentration building up unintentionally through
  repeated rotation into the same sector without an explicit, stated
  thematic rotation call
❗ "Momentum" being used to justify chasing a stock that has already
  fully re-rated with no valuation leg remaining (violates Module 2.1's
  requirement that both legs be present)
```

### HIGH Flags
```
⚠️ Inflection driver identified but not yet price-confirmed (purely
  anticipatory) — sized as if fully confirmed rather than flagged as earlier-stage
⚠️ No pre-defined exit/rotation trigger stated for an idea before entry
⚠️ Idea selection has not been compared against other sectors' current
  inflection setups — a reasonable idea presented in isolation without the
  cross-sector comparison this lens's edge depends on
```

---

## Output Format

```
MULTI-SECTOR MOMENTUM-VALUE LENS ANALYSIS
Date: [DD/MM/YYYY] | Sectors Scanned: [List]
═══════════════════════════════════════════════════════════════════

CROSS-SECTOR INFLECTION SCAN SUMMARY:
  [Brief comparative view: which sectors currently show the strongest
  named inflection setups, per Skill 08's relative strength ranking]

──────────────────────────────────────────────────────
IDEA #[N]
──────────────────────────────────────────────────────
Company:            [Name] | Ticker: [NSE] | Sector: [Sector]

VALUATION LEG:
  Current Multiple:   [X]x vs. 3-5yr avg [Y]x vs. peer avg [Z]x
  Verdict:             [Reasonable/Cheap relative to history — NOT required
                         to be statistically deep-value]

INFLECTION LEG (Named Driver):
  Type:               [Earnings / Estimate Revision / Policy / Capacity /
                        Balance Sheet Inflection]
  Specific Evidence:   [What exactly is changing, with data]
  Duration So Far:     [X quarters of confirmed trend]

PRICE CONFIRMATION:
  Status:              [Confirmed by relative strength / Purely anticipatory]
  Sizing Implication:   [Standard size / Reduced — earlier stage]

PRE-DEFINED EXIT TRIGGERS:
  Catalyst-Realized:    [Specific condition]
  Thesis-Broken:        [Specific condition + timeframe]
  Valuation-Exhausted:  [Specific multiple/level]

CROSS-SECTOR COMPARISON:
  How this ranks vs. best alternative setups currently identified: [X]
──────────────────────────────────────────────────────

[Repeat per idea]

PORTFOLIO-LEVEL ROTATION CHECK:
  Current Sector Exposure Post-Ideas: [Table vs. AI_Portfolio_Construction_
                                        Skill sector ceilings]
  Unintentional Concentration Flag:    [Yes/No — details]

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]

⚠️ REMINDER: This is a heuristic lens for how to think about the idea, not
investment advice attributed to any individual. Turnover under this lens
should be evaluated for tax and transaction-cost impact per the user's
specific circumstances.
```

---

## Rules (Non-Negotiable)

```
1. Every idea under this lens requires BOTH a valuation leg and a named,
   checkable inflection driver — either alone is insufficient.
2. Every idea must have pre-defined exit triggers stated before entry,
   including an explicit "catalyst realized, rotate out" condition.
3. Ideas are always evaluated in the context of the cross-sector scan, not
   presented in isolation — state how the idea compares to alternatives.
4. Sector concentration arising from repeated rotation must be tracked and
   flagged against AI_Portfolio_Construction_Skill's ceilings, not allowed
   to build up silently through sequential single-sector decisions.
5. No specific past trades, quotes, or opinions are ever attributed to any
   named individual — this is a generic pattern-based lens only.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Heuristic Lens — Multi-Sector Momentum-Value Style*
*Integrates with: Skill 08 (Sector Rotation Analyzer), Skill 03 (Positional Opportunity Finder),
Skill 07 (Valuation Comparator), AI_Portfolio_Construction_Skill, AI_Future_Growth_Skill*

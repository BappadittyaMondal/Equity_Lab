<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Skill 42 — Four-Lens Evidence Weighting Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when evaluating early-stage multibagger candidates to attach qualitative evidence quality and investor-lens sub-question answers to the 7 canonical factors.  
> **Cognitive mode:** Gate-based diagnostic execution: test the qualitative evidence quality and falsifiable investor questions before scoring.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · completed modules · sub-question findings · evidence quality (HIGH/MEDIUM/LOW) · red flags.  

# Skill 42 — Four-Lens Evidence Weighting Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** August 2026  
**Category:** Analytical Lens — Kedia, Kacholia, Agrawal, Parikh Qualitative Evidence Weighting  

---

## CRITICAL AI INSTRUCTION

Do not output four separate investor scores (e.g. "Kedia Score", "Kacholia Score"). Use this skill to attach evidence-quality ratings (HIGH/MEDIUM/LOW) and structured sub-question findings to the SEVEN canonical factors (Inflection, Runway, Management, Scalability, Cash Quality, Valuation, Market) defined in the Institutional Multibagger Engine. This skill modifies HOW qualitative evidence is evaluated; it does NOT add an eighth scoring system or duplicate quantitative points.

---

## Purpose

Operationalize Kedia, Kacholia, Agrawal, and Parikh's investment philosophies as falsifiable sub-questions inside the 100-point structure, without double-counting overlapping traits (management quality, business quality) across multiple buckets.

---

## Pre-Flight Requirements

```
□ Candidate has passed the Hard Risk Gate (pledge ≤35%, no auditor resignation, no related-party red flags).
□ Candidate has a Discovery Status classification (0-3 institutional attention scale, used as context not reward).
□ Primary-source disclosures available (exchange filings, audited financials, concalls, investor presentations).
```

---

## Analysis Module 1 — Kacholia Sub-Question (feeds: Capital Efficiency & Scalability)

```
"Is the incremental capital required to add the next ₹100cr of revenue falling or rising over the last 3 years?"
Required evidence: Incremental ROCE trend, fixed-asset turnover trend, operating leverage metrics.
Output: Sub-score contribution + Evidence Quality (HIGH/MEDIUM/LOW).
```

---

## Analysis Module 2 — Kedia Sub-Question (feeds: Management Execution)

```
"Has this specific management team allocated capital well through at least one prior cycle, even at smaller scale?"
Required evidence: Prior capex execution, downturn margin resilience, capital allocation history.
Output: Sub-score contribution + Evidence Quality (HIGH/MEDIUM/LOW).
```

---

## Analysis Module 3 — Agrawal Sub-Question (feeds: Operating Inflection & Market Confirmation)

```
"Is this quarter's growth rate higher than the trailing 8-quarter average (post one-off strip) — and is price/volume confirming it?"
Required evidence: QoQ vs 8-quarter trailing comparison, one-off operating profit adjustments, delivery volume trends.
Output: Sub-score contribution + Evidence Quality (HIGH/MEDIUM/LOW).
```

---

## Analysis Module 4 — Parikh Sub-Question (feeds: Cash-Flow Quality & Durability)

```
"Would cumulative free cash flow over 5 years, at a fair multiple, justify today's market cap?"
Required evidence: 5-year FCF trajectory, working capital turn, cash conversion efficiency (CFO / PAT).
Output: Sub-score contribution + Evidence Quality (HIGH/MEDIUM/LOW).
```

---

## Red Flag Summary — Four-Lens Context

### CRITICAL Flags
- Any sub-question answered from PR/interview quotes alone without regulatory exchange filings.
- Same underlying evidence used to answer two different modules (double-attribution).

### HIGH Flags
- Evidence Quality LOW on 2 or more modules (flag output as "High-scoring hypothesis, weak evidence").

---

## Output Format

```json
{
  "skill_name": "Skill 42 — Four-Lens Evidence Weighting",
  "kacholia_evidence": {"finding": "...", "evidence_quality": "HIGH|MEDIUM|LOW"},
  "kedia_evidence": {"finding": "...", "evidence_quality": "HIGH|MEDIUM|LOW"},
  "agrawal_evidence": {"finding": "...", "evidence_quality": "HIGH|MEDIUM|LOW"},
  "parikh_evidence": {"finding": "...", "evidence_quality": "HIGH|MEDIUM|LOW"},
  "contradictions": [],
  "red_flags": []
}
```

---

## Rules (Non-Negotiable)

1. This skill NEVER outputs a "Kedia Score" or "Kacholia Score".
2. This skill does not run on candidates that failed the Hard Risk Gate.
3. Discovery Status (low institutional ownership) is analytical context only, never a scoring reward.

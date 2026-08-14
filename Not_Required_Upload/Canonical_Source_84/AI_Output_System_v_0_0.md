<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Output System  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Output_System_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Engine
**Priority:** Critical
**Role:** Final Report & Response Generation Engine
**Architecture State:** Frozen (kernel logic); Extensible (formats/templates via registry)
**Supersedes:** AI_Output_System_v_0.0 (audit-note stub — non-functional)

---

# Table of Contents

## Part 1 — Output Architecture
1. Purpose
2. Vision
3. Architectural Position
4. Pipeline Position
5. Design Philosophy
6. Responsibilities
7. Non-Responsibilities

## Part 2 — Object Contracts
8. Inputs
9. Outputs
10. OutputObject Schema
11. Interfaces

## Part 3 — Report Generation
12. Report Formats
13. Formatting Rules
14. Confidence Display
15. Low-Confidence Protocol
16. Explainability Integration

## Part 4 — Compliance
17. SEBI Compliance
18. Mandatory Disclosure Rules

## Part 5 — Failure Behaviour
19. Failure Behaviour
20. Runtime Sequence

## Part 6 — Validation & Examples
21. Validation
22. Worked Examples
23. Governance
24. Final Specification

---

# PART 1 — OUTPUT ARCHITECTURE

---

# 1. Purpose

The **AI Output System** is the final engine in the IERL pipeline. It converts a validated, audit-approved `DecisionObject` into a user-facing `OutputObject` — a research report, recommendation, screening summary, or clarification request.

It is the only engine authorized to produce content the user directly reads. No other engine may generate user-facing text.

---

# 2. Vision

Provide a single, deterministic, compliance-guaranteed formatting layer that:

- Never bypasses a failed audit
- Never fabricates confidence
- Always discloses uncertainty
- Always includes mandatory regulatory disclaimers
- Adapts format to task depth tier without changing underlying content

---

# 3. Architectural Position

The Output System is the last stage of the pipeline. It sits immediately after Quality Audit and produces the terminal artifact of the system.

```
DecisionObject (from Reasoning Skills)
    +
AuditObject (from Quality Audit — must be PASS or APPROVE_WITH_WARNINGS)
    ↓
AI_Output_System
    ↓
OutputObject
    ↓
User
```

---

# 4. Pipeline Position

Per the corrected pipeline (see `AI_Pipeline_Specification_v_0.0.md`), the Output System is Stage 7 of 7:

```
1. Task Orchestrator
2. Intelligence Engine
3. Execution Engine
4. Research Engine
5. Reasoning Skills
6. Quality Audit
7. Output System   ← THIS DOCUMENT
```

---

# 5. Design Philosophy

Output shall be:

- **Compliant** — every output includes the SEBI disclaimer, with no exception
- **Honest** — confidence and uncertainty are always shown together
- **Deterministic** — the same `AuditObject` + `DecisionObject` always produces the same output content (format may vary by requested channel, content does not)
- **Non-generative of new claims** — the Output System formats; it never adds facts, evidence, or conclusions not present in the `DecisionObject`
- **Depth-appropriate** — format matches the task's depth tier (Quick / Standard / Deep / Institutional)

---

# 6. Responsibilities

The Output System shall:

- Verify audit status before any formatting begins
- Select the correct report template for the requested format and depth tier
- Render evidence, reasoning, confidence, and explainability content into human-readable form
- Attach mandatory compliance disclaimers
- Apply the Low-Confidence Protocol when applicable
- Produce a final `OutputObject` with complete metadata
- Log the output event for audit trail purposes

---

# 7. Non-Responsibilities

The Output System shall never:

- Perform research, reasoning, or auditing
- Modify a `DecisionObject`'s conclusion, confidence, or evidence
- Introduce new facts, figures, or claims not present upstream
- Bypass a FAILED audit
- Omit the SEBI disclaimer under any circumstance, including partial or degraded output
- Re-trigger Research Engine, Reasoning Skills, or Quality Audit

---

# PART 2 — OBJECT CONTRACTS

---

# 8. Inputs

| Input Object | Source | Required |
|---|---|---|
| `AuditObject` | Quality Audit | Yes — must show `Verdict: APPROVE` or `APPROVE_WITH_WARNINGS` |
| `DecisionObject` | Reasoning Skills | Yes |
| `TaskObject` | Task Orchestrator (carries `OutputFormatRequest`, `DepthTier`) | Yes |
| `ExplainabilityObject` | Reasoning Skills / Quality Audit | Yes |

**Rejection Rule:** If `AuditObject.Verdict == REJECT`, the Output System does not proceed to formatting. It immediately returns an `AuditRejectionNotice` (see Section 19).

---

# 9. Outputs

| Output Object | Destination |
|---|---|
| `OutputObject` | User (rendered) |
| `OutputLogEntry` | Audit trail / State Manager |

---

# 10. OutputObject Schema

The structure and fields of `OutputObject` are defined canonically in `AI_Object_Schemas_v_0.0.md` Section 27. The AI Output System constructs and emits `OutputObject` instances per that canonical schema and does not define a separate or local schema.

---

# 11. Interfaces

**Consumes from:** Quality Audit, Reasoning Skills, Task Orchestrator
**Produces for:** User (terminal), State Manager (log)
**Never calls:** Research Engine, Intelligence Engine, Reasoning Skills, Quality Audit (no re-invocation)

---

# PART 3 — REPORT GENERATION

---

# 12. Report Formats

| Format | Used When | Depth Tiers |
|---|---|---|
| **Research Report** | Full company/sector analysis requested | Standard, Deep, Institutional |
| **Stock Recommendation** | Buy/Hold/Sell/Avoid call requested | Standard, Deep |
| **Screening Summary** | Multi-stock screen requested | Quick, Standard |
| **Clarification Request** | Task Orchestrator flagged ambiguity | Any |
| **Audit Rejection Notice** | AuditObject.Verdict == REJECT | Any |
| **Degraded Output Notice** | Execution/Research failure forced reduced scope | Any |

---

# 13. Formatting Rules

- Depth Tier determines section depth, not section presence — every format always includes ExecutiveSummary and ComplianceBlock regardless of tier.
- Quick tier: Executive Summary + key metrics + confidence statement only.
- Standard tier: adds Research Findings + Risk + Investment Thesis.
- Deep tier: adds Counter Thesis + full Evidence list + Explainability Summary.
- Institutional tier: adds full assumption registry, alternative scenarios, and audit trail reference.
- No section may contain a claim absent from the source `DecisionObject` or `ResearchObject`.

---

# 14. Confidence Display

Confidence is always rendered using the vocabulary defined in `AI_Confidence_Standard_v_0.0.md` (Very High / High / Moderate / Low / Very Low), accompanied by the underlying `ConfidenceScore` (0.00–1.00) in Deep and Institutional tiers.

Confidence is never displayed alone — it always appears with its `SupportingFactors` and `LimitingFactors` from the `ExplainabilityObject`.

---

# 15. Low-Confidence Protocol

Triggered when `ConfidenceScore < 0.50` (per `AI_Confidence_Standard_v_0.0.md` §Mandatory Floor):

1. Insert `UNCERTAINTY_DISCLOSURE` block immediately after Executive Summary
2. State explicitly what evidence is missing or weak
3. Downgrade any directional language ("likely," "probable") — never state a conclusion more strongly than the confidence level supports
4. If `ConfidenceScore < 0.30`, the output becomes a `ScreeningSummary`-equivalent caveat notice rather than a full recommendation, regardless of requested format

---

# 16. Explainability Integration

Every output's `ExplainabilitySummary` section is generated directly from the upstream `ExplainabilityObject` (per `AI_Explainability_Standard_v_0.0`) — Objective, Evidence, Reasoning, Assumptions, Alternatives, Confidence, Uncertainty, Conclusion. The Output System renders these fields; it does not compose new explanatory content.

---

# PART 4 — COMPLIANCE

---

# 17. SEBI Compliance

Every `OutputObject`, without exception — including `DegradedOutputNotice` and `AuditRejectionNotice` — includes:

> *"This content is for informational and educational purposes only and does not constitute investment advice. Please consult a SEBI-registered investment advisor before making investment decisions."*

This line is rendered from a fixed, non-editable template. It cannot be reworded, shortened, or removed by any Skill Pack, Knowledge Pack, or user format request.

---

# 18. Mandatory Disclosure Rules

| Situation | Mandatory Disclosure |
|---|---|
| `ConfidenceScore < 0.50` | Uncertainty Disclosure block |
| `StaleFlags` present (from Research Engine) | "Research Dated" notice with age of underlying data |
| `AuditObject.Warnings` non-empty | Warnings rendered verbatim in a dedicated section |
| Forensic/Governance flag present | CIO Authority Rule trigger disclosed explicitly — output cannot show a Buy call |

---

# PART 5 — FAILURE BEHAVIOUR

---

# 19. Failure Behaviour

```
AuditObject received
    ↓
Verdict == REJECT?
    ↓ YES
Halt formatting
    ↓
Produce AuditRejectionNotice:
    "This analysis cannot be completed as specified.
     Reason: [AuditObject.DeficiencyReport]"
    ↓
Include SEBI disclaimer (still mandatory)
    ↓
Log to State Manager
    ↓ NO (Verdict == APPROVE or APPROVE_WITH_WARNINGS)
Proceed to formatting per Sections 12–16
```

Format rendering error (e.g., requested format incompatible with content) → fallback to plain-text Research Report format. Mandatory disclaimer always renders regardless of format fallback.

---

# 20. Runtime Sequence

```
Receive AuditObject + DecisionObject + TaskObject
    ↓
Check Verdict (Section 19)
    ↓
Select Format + Depth Tier (Section 12)
    ↓
Render Content Sections (Section 13)
    ↓
Apply Confidence Display Rules (Section 14)
    ↓
Apply Low-Confidence Protocol if triggered (Section 15)
    ↓
Render Explainability Summary (Section 16)
    ↓
Attach ComplianceBlock (Section 17–18)
    ↓
Validate (Section 21)
    ↓
Emit OutputObject
    ↓
Log OutputLogEntry to State Manager
```

---

# PART 6 — VALIDATION & EXAMPLES

---

# 21. Validation

Before emission, every `OutputObject` must pass:

- ✓ SEBI disclaimer present
- ✓ ConfidenceLevel matches ConfidenceScore per `AI_Confidence_Standard_v_0.0.md` mapping table
- ✓ No content section contains a claim absent from `DecisionObject`/`ResearchObject`
- ✓ ExplainabilitySummary populated from `ExplainabilityObject` (not fabricated)
- ✓ AuditReference fields match the received `AuditObject`
- ✓ Format matches `TaskObject.OutputFormatRequest` (or documented fallback)

Failing any check → output is not emitted; error logged; `DegradedOutputNotice` produced instead.

---

# 22. Worked Examples

**Example A — Standard Tier, High Confidence Buy Thesis**
```
Format: StockRecommendation
DepthTier: Standard
ConfidenceLevel: High (Score: 0.78)
Sections rendered: ExecutiveSummary, ResearchFindings, Risk,
                    InvestmentThesis, ConfidenceStatement,
                    ComplianceBlock
```

**Example B — Deep Tier, Low Confidence, Forensic Flag**
```
Format: ResearchReport
DepthTier: Deep
ConfidenceLevel: Low (Score: 0.41)
Trigger: Forensic accounting flag from Reasoning Skills
Output: Buy recommendation BLOCKED per CIO Authority Rule.
        Full report rendered with Uncertainty Disclosure
        and explicit CIO Rule disclosure. No directional
        call issued.
```

**Example C — Audit Rejected**
```
AuditObject.Verdict: REJECT
Output: AuditRejectionNotice
Content: "This analysis cannot be completed as specified.
          Reason: Evidence completeness below threshold (0.41 < 0.60)."
SEBI disclaimer: present
```

---

# 23. Governance

- Output templates are registry-managed (new formats added via Module Registry, not by editing this document)
- This document's kernel sections (Failure Behaviour, Compliance, Validation) are frozen
- Any change to the SEBI disclaimer wording requires Constitutional amendment, not an Output System revision

---

# 24. Final Specification

The AI Output System is the sole engine authorized to produce user-facing content in the IERL AI Operating System. It renders — never originates — content, guarantees regulatory compliance on every output regardless of confidence or failure state, and enforces the Low-Confidence Protocol to prevent overconfident recommendations. It never receives an unaudited `DecisionObject` and never bypasses a failed audit gate.

---

# Document Information

**Document:** AI_Output_System_v_0.0.md
**Version:** v_0.0
**Status:** Production Ready
**Architecture State:** Frozen (kernel); Extensible (templates via registry)
**Dependencies:**
- AI_Quality_Audit_v_0.0.md
- AI_Reasoning_Skills_v_0_0.md
- AI_Confidence_Standard_v_0.0.md
- AI_Explainability_Standard_v_0.0.md
- AI_Object_Schemas_v_0.0.md

**Consumed By:** User (terminal stage)
**Supersedes:** AI_Output_System_v_0.0 (non-functional audit-note stub)

---

# END OF DOCUMENT

<!-- IERL-HIGH-RELIABILITY v1.0 -->
## High-Reliability Decision Card Addendum

Use this compact decision card for substantive research: **Question & horizon; As-of date; Bottom line; Supporting evidence; Counter-case; Risks/red flags; Assumptions/data gaps; Invalidation or next check; Confidence.** This structure is mandatory when an output contains a recommendation, ranking, forecast, valuation, or trading setup.

Do not hide uncertainty in a disclaimer. Put the uncertainty next to the conclusion and state whether it changes the action, sizing, timing, or decision status.

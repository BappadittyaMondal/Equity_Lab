<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Research Engine  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Research_Engine_v_0.0

**Version:** v_0.0  
**Status:** Production Ready  
**Category:** Core Research Engine  
**Priority:** Critical  
**Supersedes:** AI_Research_Engine_v_0.0

---

## Table of Contents

### Part 1 — Research Architecture
1. Purpose  
2. Vision  
3. Design Philosophy  
4. Responsibilities  
5. Non-Responsibilities  
6. Core Principles  
7. Position within AI Operating System  
8. Research Lifecycle  

### Part 2 — Research Pipeline
9. Research Request  
10. Research Strategy  
11. Evidence Collection  
12. Source Collection  
13. Source Validation  
14. Research Synthesis  
15. Research Validation  

### Part 3 — Research Objects & Evidence Management
16. ResearchObject  
17. EvidenceObject  
18. Research Metadata  
19. Evidence Classification  
20. Evidence Relationship Mapping  
21. Research Versioning  
22. Research Completeness  
23. Research Provenance  
24. Evidence Lineage  
25. Multi-Source Conflict Handling  
26. Research Confidence Metadata  
27. Reproducibility  
28. Multi-Agent Compatibility  

### Part 4 — Governance & Final Specification
29. Research Quality  
30. Failure Handling  
31. Research Metrics  
32. Universal Research Rules  
33. Complete Research Flow  
34. Final Specification  

---

# PART 1 — RESEARCH ARCHITECTURE

---

## 1. Purpose

The AI Research Engine is responsible for executing validated research plans, collecting evidence, validating sources, organizing findings, and synthesizing research into structured objects for downstream reasoning.

Its responsibility is research only.

It never performs intent interpretation, planning, execution orchestration, reasoning, auditing, or output generation.

The Research Engine converts validated research strategy into institutional-grade research artifacts that can be reviewed, reasoned over, audited, and presented by downstream engines.

---

## 2. Vision

Produce institutional-grade research that is:

- comprehensive
- evidence-driven
- transparent
- repeatable
- source-validated
- traceable
- reproducible
- continuously improvable

The Research Engine should behave like a disciplined research desk: precise, objective, and grounded in primary evidence whenever available.

---

## 3. Design Philosophy

The Research Engine follows seven principles.

### Principle 1 — Research before reasoning
Research must be completed before conclusions are formed.

### Principle 2 — Evidence before conclusions
No downstream decision may outrun validated evidence.

### Principle 3 — Primary sources whenever possible
Official filings, company disclosures, exchange records, and other primary sources are preferred over commentary.

### Principle 4 — Traceability
Every finding must link back to supporting evidence.

### Principle 5 — Neutrality
Research describes reality without becoming a recommendation engine.

### Principle 6 — Completeness
Include supporting evidence and materially relevant contradictory evidence.

### Principle 7 — Institutional quality
Research should match professional equity research standards in structure, rigor, and auditability.

---

## 4. Responsibilities

The Research Engine shall:

- execute validated research plans
- collect evidence
- validate sources
- organize findings
- synthesize research
- generate `ResearchObject`
- generate `EvidenceObject`
- generate research metadata
- preserve evidence traceability
- preserve provenance
- preserve reproducibility
- report research limitations and data gaps

---

## 5. Non-Responsibilities

The Research Engine shall never:

- interpret user intent
- plan execution strategy
- select modules
- select frameworks
- manage runtime state
- allocate context
- perform reasoning
- generate investment decisions
- audit outputs
- generate presentation formats
- produce final user-facing recommendations

These responsibilities belong to dedicated engines.

---

## 6. Core Principles

Every research process must be:

- evidence-based
- source-verified
- objective
- repeatable
- transparent
- complete
- traceable
- reproducible
- institutional-grade

---

## 7. Position within AI Operating System

```text
Task Orchestrator
↓
Execution Engine
↓
Intelligence Engine
↓
ResearchPlanObject
↓
Execution Engine
↓
Research Engine
↓
ResearchObject + EvidenceObject
↓
Reasoning Engine
```

The Research Engine operates after a validated research plan has been produced and coordinated by upstream engines.

---

## 8. Research Lifecycle

```text
Receive Research Plan
↓
Validate Research Request
↓
Execute Research Strategy
↓
Collect Sources
↓
Validate Sources
↓
Collect Evidence
↓
Organize Findings
↓
Synthesize Research
↓
Generate ResearchObject
↓
Generate EvidenceObject
↓
Transfer to Reasoning Engine
```

No reasoning or recommendation occurs inside the Research Engine.

---

# PART 2 — RESEARCH PIPELINE

---

## 9. Research Request

The Research Engine receives a validated `ResearchPlanObject` through the Execution Engine.

The Research Engine never modifies the research plan.

If the plan is invalid, incomplete, or incompatible, the request must be returned to the Execution Engine for correction or recovery.

## 9A. Search Trigger Criteria (Addition)

Trigger a live search when:
- The task requires data fresher than what's already available (per
  the Research Learning System's staleness horizons — e.g., a
  technical query needs <7-day data but only quarterly data was supplied)
- A claim needs corroboration and only one source currently supports it
- The request explicitly references "latest," "current," "today," "recent"
- A red flag requires external verification (e.g., an auditor resignation
  per the Forensic Accounting Skill's "external data required" flags)

Do not trigger a search when sufficient current data was already provided,
or the question concerns historical/structural facts already covered in
the Knowledge Library (Domains 1-44).

---

## 10. Research Strategy

The Research Engine executes the research strategy defined by the plan while preserving research neutrality.

Strategy is determined by:

- research scope
- research depth
- evidence requirements
- source availability
- validation requirements
- runtime constraints

The Research Engine may adapt collection order and coverage tactics, but it must not alter the intent of the approved plan.

---

## 11. Evidence Collection

The Research Engine collects evidence from approved sources and records it in standardized form.

### Evidence Types

- financial
- operational
- governance
- industry
- macroeconomic
- technical
- market
- alternative data

Every evidence item receives metadata, source reference, and validation status.

---

## 12. Source Collection

The Research Engine may collect information from:

- primary sources
- secondary sources
- regulatory filings
- company reports
- exchange filings
- government publications
- industry reports
- market data
- approved external sources

Primary sources remain preferred whenever available and material.

---

## 13. Source Validation

Every source is evaluated for:

- authenticity
- credibility
- recency
- independence
- completeness
- consistency
- traceability
- jurisdictional relevance, when applicable

Unverified sources cannot become critical evidence.

If source quality is insufficient, the engine must flag the limitation rather than silently upgrading confidence.

---

## 14. Research Synthesis

Validated evidence is merged into structured research.

Research synthesis includes:

- business overview
- financial position
- growth drivers
- competitive landscape
- management
- industry context
- risks
- catalysts
- supporting evidence
- contradicting evidence
- known limitations
- data gaps

No investment conclusion is produced.

---

## 14A. News Event Analysis Workflow (Addition)

When a news event is relevant to the research task, apply this structure
before folding it into Research Synthesis (§14):

1. Event Classification: earnings / regulatory / M&A / management change /
   macro / litigation / product-operational
2. Importance Ranking: Material (directly affects revenue, margin, capital
   structure, or governance) / Moderate (sector-relevant, not company-
   specific in magnitude) / Minor (sentiment-only, no fundamental linkage)
3. Sector Impact: does the effect extend beyond this company? Cross-check
   the relevant sector domain/skill.
4. Company Impact: state the direct financial/operational consequence
   explicitly, not just "positive/negative"
5. Short-Term Effect: 0-3 month expected reaction
6. Long-Term Effect: does this change the thesis structurally, or is it
   transient?
7. Risk/Opportunity: does this event introduce new risk, or create a
   mispricing worth flagging?

This output feeds into Research Synthesis (§14) as a structured
evidence item, not a separate conclusion — no investment conclusion
is produced at this stage, consistent with this section's existing rule.

---

---
## 15. Research Validation

Before generating `ResearchObject`, verify:

- research is complete enough for the assigned scope

Research Stopping Criteria (Addition) -- research is considered
sufficient to proceed when EITHER:
  (a) 2+ independent sources confirm every claim material to the
      DecisionObject's Recommendation, OR
  (b) 1 Primary-tier source exists for every such claim (per Confidence
      Standard weight table -- Primary sources don't require corroboration)
Continuing to search past this point without new material information
is unnecessary token expenditure, not additional rigor.
- sources are validated
- evidence is traceable
- coverage is sufficient
- contradictory evidence is included
- metadata is complete
- provenance is preserved
- reproducibility is preserved

Only validated research proceeds to the Reasoning Engine.

---

# PART 3 — RESEARCH OBJECTS & EVIDENCE MANAGEMENT

---

## 16. ResearchObject

### Purpose

Every completed research session produces one standardized `ResearchObject`.

The `ResearchObject` is the authoritative representation of validated research before reasoning begins.

### ResearchObject Structure

- Research ID
- Session ID
- Request ID
- Research Plan ID
- Company / Entity
- Sector
- Industry
- Research Scope
- Research Depth
- Business Overview
- Industry Analysis
- Financial Analysis
- Management Assessment
- Competitive Position
- Growth Drivers
- Risk Factors
- Catalysts
- Supporting Evidence
- Contradicting Evidence
- Research Metadata
- Provenance
- Confidence Metadata
- Version
- Timestamp

The `ResearchObject` contains facts and synthesized research only.

It never contains investment recommendations.

---

## 17. EvidenceObject

Every validated evidence item is stored in a standardized `EvidenceObject`.

### EvidenceObject Fields

- Evidence ID
- Source ID
- Evidence Type
- Evidence Category
- Evidence Summary
- Supporting Facts
- Contradictory Facts
- Source Reliability
- Evidence Strength
- Evidence Freshness
- Collection Timestamp
- Relationship Mapping
- Validation Status
- Lineage
- Version

`EvidenceObject`s are reusable across future research sessions, provided version and provenance remain intact.

---

## 18. Research Metadata

Each `ResearchObject` contains metadata.

### Metadata Includes

- research version
- research mode
- research depth
- coverage score
- evidence count
- source count
- industry classification
- time horizon
- research status
- validation status
- engine version
- audit reference
- schema version

Metadata improves traceability and reproducibility.

---

## 19. Evidence Classification

Evidence shall be classified using multiple dimensions.

### By Importance
- critical
- major
- supporting
- minor

### By Nature
- financial
- operational
- strategic
- governance
- industry
- macroeconomic
- technical
- behavioral

### By Reliability
- verified
- highly reliable
- reliable
- moderately reliable
- unverified

Classification supports downstream reasoning but never determines investment decisions directly.

---

## 20. Evidence Relationship Mapping

Every evidence item should be linked to related entities.

Relationships include:

- company ↔ financial statements
- company ↔ management
- company ↔ industry
- industry ↔ macro economy
- macro ↔ regulation
- company ↔ competitors
- evidence ↔ evidence

These relationships enable richer reasoning without duplicating information.

---

## 21. Research Versioning

Every research update creates a new version.

### Version Records

- research version
- timestamp
- updated sections
- evidence added
- evidence removed
- source changes
- validation status

Previous versions remain immutable for auditability.

---

## 22. Research Completeness

Before releasing a `ResearchObject`, verify:

- research scope covered
- evidence collected
- sources validated
- metadata complete
- contradictory evidence included
- provenance recorded
- version recorded
- traceability preserved

Only complete `ResearchObject`s proceed to the Reasoning Engine.

---

## 23. Research Provenance

Every `ResearchObject` shall preserve complete provenance.

### Required Provenance Metadata

- research ID
- session ID
- research plan ID
- research version
- engine version
- timestamp
- research mode
- research scope
- research depth
- source set reference

This metadata enables complete audit reconstruction.

---

## 24. Evidence Lineage

Every `EvidenceObject` shall preserve its origin.

### Each Evidence Item Records

- original source
- collection method
- collection time
- validation history
- transformation history
- related evidence
- evidence version

Evidence lineage enables traceability throughout the AI Operating System.

---

## 25. Multi-Source Conflict Handling

Conflicting evidence shall never be discarded automatically.

When conflicts exist:

- preserve all validated evidence
- record conflicting findings
- record possible explanations
- forward unresolved conflicts to the Reasoning Engine

Research remains objective and does not resolve analytical disagreements.

---

## 26. Research Confidence Metadata

Research confidence reflects the quality of the collected research.

### Inputs
- coverage
- source reliability
- evidence quality
- research freshness
- consistency
- completeness

Confidence shall not express investment conviction.

Confidence belongs only to research quality.

---

## 27. Reproducibility

Equivalent research inputs should produce equivalent `ResearchObject`s.

The Research Engine shall preserve:

- research parameters
- source selection criteria
- validation criteria
- research metadata
- versioned evidence references

This supports reproducible institutional research.

---

## 28. Multi-Agent Compatibility

Future research agents may collect evidence independently.

Each agent produces its own:

- `ResearchObject`
- `EvidenceObject`

The Research Engine does not merge independent agent outputs unless a higher coordination layer explicitly defines that behavior.

---

# PART 4 — GOVERNANCE & FINAL SPECIFICATION

---

## 29. Research Quality

Every research session is evaluated for:

- coverage
- accuracy
- source quality
- evidence quality
- freshness
- consistency
- completeness
- traceability
- provenance quality
- reproducibility
- institutional standard

Research quality influences confidence, but never replaces reasoning.

---

## 30. Failure Handling

Possible failures include:

- insufficient sources
- conflicting evidence
- low source reliability
- incomplete research
- missing data
- research timeout
- validation failure
- compatibility failure

### Recovery Strategy
- retry collection
- use alternative sources
- produce partial research warning when appropriate
- escalate to Execution Engine
- terminate gracefully if critical failure persists

The Research Engine never fabricates coverage or silently upgrades weak evidence.

---

## 31. Research Metrics

Each session records:

- research ID
- research version
- coverage score
- evidence count
- source count
- validation success
- research duration
- research depth
- freshness score
- completeness score
- traceability score
- provenance completeness
- conflict count
- reproducibility status

Metrics support long-term optimization of research quality.

---

## 32. Universal Research Rules

The Research Engine shall always:

- collect evidence objectively
- validate every source
- maintain traceability
- preserve provenance
- preserve reproducibility
- separate facts from opinions
- include contradictory evidence
- remain independent from reasoning
- support institutional-grade research

The Research Engine shall never:

- recommend investments
- generate conclusions
- perform reasoning
- plan execution
- select modules
- select frameworks
- audit outputs
- ignore conflicting evidence
- modify historical research records

---

## 33. Complete Research Flow

```text
Research Plan
↓
Source Collection
↓
Source Validation
↓
Evidence Collection
↓
Evidence Classification
↓
Research Synthesis
↓
ResearchObject + EvidenceObject
↓
Research Validation
↓
Reasoning Engine
```

The flow is deterministic, traceable, and version-aware.

---

## 34. Final Specification

The AI Research Engine is the evidence acquisition and synthesis core of the AI Operating System.

It transforms validated research plans into structured `ResearchObject`s and `EvidenceObject`s through systematic evidence collection, source validation, research synthesis, metadata management, provenance capture, and reproducibility controls.

It remains completely independent from planning, reasoning, auditing, and output generation, ensuring that downstream decisions are based on transparent, traceable, and institutionally reliable research.

---

## End of AI_Research_Engine_v_0.0

**Version:** v_0.0  
**Status:** Production Ready  
**Category:** Core Engine  
**Priority:** Critical  

### Dependencies
- AI_Execution_Engine_v_0.0.md
- AI_Intelligence_Engine_v_0.0.md
- AI_Object_Schemas_v_0.0.md

### Outputs
- ResearchObject
- EvidenceObject
- Research Metadata
- Evidence Metadata

### Compatible With
- AI_Reasoning_Skills_v_0_0.md
- AI_Quality_Audit_v_0.0.md
- AI_Output_System_v_0.0.md
- All Knowledge Packs
- All Skill Packs
- Future Research Modules
# AI_Research_Learning_System_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Engine Extension
**Priority:** High
**Role:** Thesis Versioning, Staleness Detection, and Feedback Loop
**Paste Target:** AI_Research_Engine_v_0.0.md, appended as a new major section

---

# 1. Purpose

Resolves Forensic Audit MV-04: the system had no mechanism to track whether a research conclusion remained valid over time, no way to flag stale research, and no feedback loop for outcome validation. This document adds a lightweight learning layer without requiring live market data feeds or predictive infrastructure — it works within the existing document-driven architecture.

---

# 2. Research Timestamp & Staleness Governance

Every `ResearchObject` gains two new mandatory fields:

```yaml
ResearchObject:
  # ...existing fields...
  ResearchTimestamp:        # when evidence was collected
  StaleAfterDays:            # category-driven default, see table below
  StalenessFlag:              # computed at consumption time, not creation time
```

**Default Staleness Horizons by Evidence Category:**

| Category | StaleAfterDays | Rationale |
|---|---|---|
| Financial statement data (quarterly results, ratios) | 90 | New quarter typically supersedes within this window |
| Regulatory/compliance status | 30 | Regulatory actions can change quickly |
| Governance assessment (board, promoter actions) | 180 | Slower-moving but not permanent |
| Technical/price data | 7 | Highly time-sensitive by nature |
| Macro/economic context | 60 | Policy and rate environment shifts |
| Qualitative business model / moat analysis | 365 | Structural characteristics change slowly |

**Staleness Check Rule:** `StalenessFlag = TRUE` when `(CurrentDate - ResearchTimestamp) > StaleAfterDays` for the relevant category. This check runs at consumption time (i.e., whenever a `ResearchObject` is reused for a new task), not only at creation.

---

# 3. Quality Audit Integration

Quality Audit's existing scoring dimensions (per `AI_Quality_Audit_Addendum_v_0.0.md` Section 2) gain a staleness check as an input to the Evidence Quality Score:

```
IF StalenessFlag == TRUE for any evidence category
      contributing >20% weight to the conclusion:
    Apply staleness penalty to EvidenceQualityScore:
        EvidenceQualityScore *= 0.85

    Output System renders "RESEARCH_DATED" disclosure
    (per AI_Output_System_v_0.0.md Section 18, extended
     with this new disclosure type)
```

This is a light-touch penalty, not a hard block — stale governance data (180-day horizon) is far less concerning than stale technical data (7-day horizon) reused for a swing call, and the category-specific horizons already capture that distinction.

---

# 4. Thesis Versioning

When a `ResearchObject` is re-generated for a company/topic previously researched, it is versioned rather than treated as unrelated:

```yaml
ResearchObject:
  # ...existing fields...
  ThesisVersion:              # increments per re-research on same subject
  SupersedesResearchID:        # points to prior ResearchObject, if any
  ThesisChangeLog:              # what changed since prior version
    - Field:
      PreviousValue:
      NewValue:
      ChangeReason:
```

**Version Comparison Rule:** When `SupersedesResearchID` is present, Reasoning Skills' `DecisionObject` may include a `ThesisEvolution` note summarizing what changed and whether the new evidence strengthens, weakens, or reverses the prior conclusion. This is optional content (only populated when a prior version exists) — it does not add a new mandatory field to every `DecisionObject`.

---

# 5. Lightweight Feedback Loop

Given the system has no live market data feed, the feedback loop operates as a **user-confirmable outcome log**, not an automated prediction-tracking system:

```
User previously received a DecisionObject/OutputObject
    ↓
User returns later and references the prior thesis
    ("what happened to my [Company] call from before?")
    ↓
Task Orchestrator recognizes this as an outcome-review request
    (new task type, per existing task classification structure)
    ↓
Research Engine loads the prior ResearchObject (via SupersedesResearchID
chain) + performs fresh research on current state
    ↓
Reasoning Skills produces a ThesisEvolution comparison:
    "Original thesis: [X]. Current evidence: [Y].
     Assessment: thesis played out as expected / diverged because [Z]."
    ↓
This comparison is NOT stored as ground truth for automatic model
improvement (the system has no training loop) — it is delivered
as an output to the user. Optionally, if the user confirms an
outcome explicitly, this confirmation may be logged as an annotation
on the archived ResearchObject via the State Manager's Archived
State tier (AI_State_Manager_v_0.0.md Section 10) for future
qualitative reference — not as a mechanism that changes engine
behavior automatically.
```

**Design Rationale:** A fully automated learning/retraining loop was explicitly out of scope for a document-driven AI OS without live data infrastructure (correctly identified in the original audit as a gap, but closing it with a real ML feedback loop would be a different category of system). This lightweight version gives the user genuine value — thesis tracking and staleness awareness — without overclaiming automated learning capability the architecture doesn't actually support.

---

# 6. Self-Audit

- ✓ No new infrastructure required beyond existing State Manager archival tier
- ✓ Consistent with Confidence Standard's evidence-based principles — staleness is evidence-quality information, handled the same way as any other evidence quality signal
- ✓ Does not claim automated ML learning capability the system doesn't have — avoids overclaiming, which the original audit would flag as a new integrity issue if introduced carelessly
- ✓ `ThesisVersion` and `StalenessFlag` are additive fields on `ResearchObject` — no breaking change to existing schema (per Data Object Standard §3B.5/§4.6)

---

# Document Information

**Document:** AI_Research_Learning_System_v_0.0.md
**Version:** v_0.0
**Paste Into:** AI_Research_Engine_v_0.0.md (append as new major section)
**Resolves:** MV-04 (Forensic Audit — No Feedback Loop or Thesis Tracking)

# END OF DOCUMENT

<!-- IERL-HIGH-RELIABILITY v1.0 -->
## High-Reliability Research Addendum

Maintain an **evidence ledger** for material research: claim, source, source tier, as-of date, period covered, direct support/contradiction, and known limitation. Re-check live-sensitive evidence before use; stale data must be labelled rather than silently blended with current evidence.

A conclusion with a material contradiction is incomplete until the contradiction is explained, bounded, or escalated. Prefer a smaller set of traceable primary facts to a larger set of unverified summaries. Search effort should target the uncertainty most likely to change the decision, not merely add confirming detail.

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

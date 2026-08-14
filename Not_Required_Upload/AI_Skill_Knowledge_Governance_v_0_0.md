# AI_Skill_Knowledge_Governance_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Registry Extension
**Priority:** High
**Role:** Priority Rules, Conflict Resolution, and Fallback Behavior for Skill/Knowledge Loading
**Paste Target:** AI_Dependency_Map_v_0.0.md, appended after Section 8 (Resolution Algorithm)

---

# 1. Purpose

`AI_Dependency_Map_v_0.0.md` already defines the Skill↔Knowledge dependency matrix (Section 5) and the automatic loading resolution algorithm (Section 8). This document completes Prompt 9's remaining requirements: **priority rules when multiple skills compete for context**, **conflict resolution when two active Skill Packs recommend contradictory Knowledge Pack versions**, and **fallback behavior when a required domain is entirely unavailable.**

---

# 2. Priority Rules When Multiple Skills Are Active

A single task may activate more than one Skill Pack (e.g., "Analyze this NBFC for both forensic risk and technical entry point" activates both Forensic Accounting Skill and Technical Pattern Skill simultaneously).

**Priority order when multiple skills compete for limited context budget** (extends Context Manager §6):

1. **Gate-critical skills first** — Forensic Accounting Skill, Governance Assessment Skill (any skill tied to a CIO Authority Rule per Architecture Overview §13D) receive loading priority over all other active skills
2. **Primary task skill second** — the skill most directly matching the Task Orchestrator's classified intent (e.g., if the user asked for "forensic risk with a secondary technical note," Forensic Accounting is primary, Technical Pattern is secondary)
3. **Secondary/supporting skills third** — loaded only if budget remains after (1) and (2)
4. **Skills below priority rank whose required domains cannot fit are deferred, not dropped** — see Section 4 (Fallback)

---

# 3. Conflict Resolution — Contradictory Knowledge Pack Guidance

When two simultaneously active Skill Packs draw on Knowledge Packs that offer conflicting guidance (e.g., DCF Valuation Skill's Domain 5 suggests a growth-adjusted multiple while a loaded Sector Deep Dive domain suggests a sector-capped multiple for the same company), resolution follows this order:

```
1. Domain-specific guidance overrides general guidance
   (Sector Deep Dive > general Valuation domain, when both apply
   to the same company's sector)

2. Higher-numbered "Critical Gate" domains override standard domains
   (Domain 24 Forensic Accounting > Domain 6 Fundamental Analysis,
   consistent with existing Knowledge Index Global Conflict
   Arbitration rules)

3. If neither rule resolves the conflict, both viewpoints are
   preserved and passed to Reasoning Skills as competing evidence
   — per AI_Confidence_Standard_v_0.0.md Section 12's
   ConsistencyFactor = 0.6 case (material contradiction presented
   as competing scenarios, never silently resolved by the loading
   layer)
```

**Critical rule:** The Dependency Map / Context Manager layer never silently picks a winner between conflicting Knowledge Pack guidance on a substantive analytical question. Rule 3 ensures unresolved conflicts are explicitly surfaced downstream to Reasoning Skills, consistent with the existing prohibition on suppressing contradictory evidence (Confidence Standard §23, Explainability Standard §11).

---

# 4. Fallback Behavior — Required Domain Unavailable

Triggered when a Skill Pack's `required_domains` (per Dependency Map §5 matrix) cannot be loaded due to context overflow (per Context Manager §10) or a missing/deprecated Knowledge Pack:

```
Required domain unavailable
    ↓
Check: is this a Critical Gate domain (e.g., Domain 24, Domain 8)?
    ↓ YES
Escalate as F3 failure (Architecture Overview §13C)
    ↓
Skill Pack does not execute; Intelligence Engine notified;
ResearchPlanObject flags SKILL_BLOCKED with reason
    ↓ NO (non-critical required domain)
Attempt substitution: is there an "optional" domain from the
same matrix entry that covers similar ground?
    ↓ YES
Load substitute; flag DOMAIN_SUBSTITUTED in ContextAllocationObject
    ↓ NO
Proceed with reduced scope; flag REQUIRED_DOMAIN_MISSING;
Research Engine's completeness gate reflects this gap, which
propagates a CoverageFactor penalty per Confidence Standard §12
```

This directly extends the existing Context Manager Overflow Protocol (§10) with skill-specific fallback logic, rather than treating skill/knowledge loading failures generically.

---

# 5. Worked Example

```
Task: "Deep dive on [NBFC]: forensic risk + technical entry"
Active Skills: Forensic Accounting Skill (primary, gate-critical),
               Technical Pattern Skill (secondary)

Priority resolution (Section 2):
  1. Forensic Accounting's required domains (24, 2, 3) load first
     — gate-critical, guaranteed
  2. Technical Pattern's required domains (7, 30) load second
     — primary/secondary skill budget allows both to fit at Deep tier

No conflict detected (Section 3 not triggered — domains don't overlap
on the same analytical question)

Result: Both skills execute with full required-domain coverage.
No fallback needed.
```

```
Alternate scenario — context-constrained (Standard tier instead of Deep):
  1. Forensic Accounting's required domains load first (gate-critical)
  2. Technical Pattern's required domains exceed remaining budget
     at Standard tier
  3. Fallback (Section 4): Technical Pattern is non-critical →
     attempt substitution → no suitable substitute found →
     proceed with SKILL_DEFERRED flag; Technical Pattern does not
     execute this pass; user output notes technical analysis was
     not included due to depth tier constraints
```

---

# 6. Self-Audit

- ✓ Extends (does not duplicate) Dependency Map §5/§8 and Context Manager §6/§10
- ✓ Consistent with Confidence Standard §12 ConsistencyFactor handling for unresolved conflicts
- ✓ Consistent with Architecture Overview §13C Failure Classification (F3 escalation for gate-critical domain unavailability)
- ✓ No new objects introduced; uses existing `ResearchPlanObject`, `ContextAllocationObject` flag fields

---

# Document Information

**Document:** AI_Skill_Knowledge_Governance_v_0.0.md
**Version:** v_0.0
**Paste Into:** AI_Dependency_Map_v_0.0.md (append after Section 8)
**Resolves:** Remaining Prompt 9 requirements (priority rules, conflict resolution, fallback)

# END OF DOCUMENT

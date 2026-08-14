<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Context Manager  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Context_Manager_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Registry / Runtime Infrastructure
**Priority:** Critical
**Role:** Context Window Allocation and Token Budget Authority
**Architecture State:** Frozen

---

# Table of Contents

1. Purpose
2. Architectural Position
3. Responsibilities
4. Non-Responsibilities
5. Context Budget Model
6. Context Priority Hierarchy
7. Allocation by Depth Tier
8. Dynamic Loading Rules
9. Context Eviction Policy
10. Overflow Protocol
11. Context Allocation Object
12. Interfaces
13. Governance
14. Final Specification

---

# 1. Purpose

The AI Context Manager governs how the limited LLM context window is allocated across the Constitution, active engine instructions, loaded Knowledge Packs, loaded Skill Packs, and Frameworks during a single task's processing.

It exists because the system has 43 Knowledge Pack domains and 34 Skill Packs — far more content than fits in any context window simultaneously. Without this component (identified as missing in Forensic Audit CV-03/MV-07), the Execution Engine has no way to decide what to load, what to drop, or what to do when a task's true content need exceeds capacity.

---

# 2. Architectural Position

```
AI_Execution_Engine
    ↓ (requests context allocation)
AI_Context_Manager
    ↓ (allocates budget, selects packs within budget)
Loaded Context for Current Session
```

The Execution Engine requests context; the Context Manager allocates it. The Execution Engine never manages token budgets directly (per Execution Engine §32, already stated in the existing spec — this document fulfills that referenced dependency).

---

# 3. Responsibilities

The Context Manager shall:

- Define token budget ceilings per depth tier
- Rank requested Knowledge Packs / Skill Packs / Frameworks by priority when the request exceeds budget
- Select which packs are loaded, deferred, or dropped
- Evict low-priority content when a session needs to load additional packs mid-session
- Report `CONTEXT_LIMITED` flags to the Intelligence Engine's `ResearchPlanObject` when full scope cannot be loaded
- Preserve the Constitution and current TaskObject in context at all times (non-evictable)

---

# 4. Non-Responsibilities

The Context Manager shall never:

- Select which packs are analytically relevant (Intelligence Engine's responsibility, via Module/Framework Registry)
- Modify pack content
- Make research or reasoning decisions
- Override a Constitutional requirement to save space (Constitution is always non-evictable)

---

# 5. Context Budget Model

Total context window is divided into five allocation classes:

| Class | Content | Evictable? |
|---|---|---|
| **Class 0 — Constitutional** | AI_Project_Instructions core rules | Never |
| **Class 1 — Task Core** | Current TaskObject, ResearchPlanObject | Never |
| **Class 2 — Engine Instructions** | Active engine's own operating spec | Never during that engine's turn |
| **Class 3 — Knowledge Packs** | Domain knowledge (up to 43 packs) | Yes — priority-ranked |
| **Class 4 — Skill Packs / Frameworks** | Analytical methodology packs | Yes — priority-ranked |

Classes 0–2 are guaranteed. Classes 3–4 compete for remaining budget.

---

# 6. Context Priority Hierarchy

When Class 3/4 content exceeds available budget, priority is assigned in this order:

1. Packs explicitly required by the selected Skill Pack (per `AI_Dependency_Map_v_0.0.md` Skill↔Knowledge dependency table)
2. Packs flagged as "Critical Gate" domains (Domain 24 — Forensic Accounting; Domain 8 — Governance) — these are near-non-evictable per CIO Authority Rules, since bypassing them risks a constitutional violation
3. Packs matching the task's primary sector/domain classification
4. Packs matching the task's depth tier defaults (see Section 7)
5. Optional/supplementary packs (lowest priority — first evicted)

---

## 6A. Retrieval Deduplication Rule (Addition)

Before loading a Knowledge Pack or Skill Pack, check whether its content
is already resident from an earlier stage in the same session (e.g., a
domain loaded for Research Engine that's still resident when Reasoning
Skills runs). Do not reload identical content — extend its residency
instead. This reduces redundant retrieval as the repository grows,
without changing the existing Priority Hierarchy or Overflow Protocol.

---

---

# 7. Allocation by Depth Tier

| Depth Tier | Max Knowledge Packs | Max Skill Packs | Max Frameworks | Approx. Context Share (Class 3+4) |
|---|---|---|---|---|
| **Quick** | 3 | 1 | 1 | 20% |
| **Standard** | 6 | 2 | 2 | 45% |
| **Deep** | 12 | 4 | 4 | 75% |
| **Institutional** | All relevant (priority-ranked if exceeding budget) | All relevant | All relevant | 90% |

These are ceilings, not targets — the Intelligence Engine may request fewer. The Context Manager never pads a request up to the ceiling.

---

# 8. Dynamic Loading Rules

- Packs are loaded just-in-time at the stage that consumes them (e.g., Knowledge Packs load at Research Engine's stage, not earlier)
- A pack loaded for Research Engine is released once Reasoning Skills' `DecisionObject` is produced, unless Quality Audit requests re-verification
- Frameworks load at Intelligence Engine planning time and remain resident through Execution only if actively referenced downstream

---

# 9. Context Eviction Policy

When a mid-session request needs additional context beyond current budget:

1. Identify lowest-priority currently-loaded pack (per Section 6 ranking, reversed)
2. Confirm the pack is not from a Critical Gate domain (Section 6, item 2) — Critical Gate content is never evicted to make room for lower-priority content
3. Evict lowest-priority pack; log eviction in the session's `ContextAllocationRef` (tracked via State Manager)
4. Load new pack
5. If no evictable pack exists (all loaded content is Critical Gate or Class 0–2), trigger Overflow Protocol (Section 10)

---

# 10. Overflow Protocol

Triggered when requested content cannot fit even after full eviction of evictable content:

```
Overflow detected
    ↓
Reduce scope: drop lowest-priority Class 4 (Frameworks) first
    ↓
Still overflowing?
    ↓
Drop lowest-priority Class 3 (non-critical-gate Knowledge Packs)
    ↓
Still overflowing?
    ↓
Flag CONTEXT_LIMITED on ResearchPlanObject
    ↓
Notify Intelligence Engine: scope must be reduced or depth tier lowered
    ↓
Research proceeds with reduced scope; Research Engine's completeness
gate (per Research Engine §22) will reflect this as reduced coverage,
propagating an appropriate confidence reduction downstream
```

**Critical Rule:** Overflow never silently truncates. Every dropped pack is logged and flagged. This directly closes the audit finding (MV-07) that context overflow could cause silent truncation — under this protocol, it cannot.

---

# 10B. Context Governance Rules

To prevent the Context Manager from becoming an uncontrolled second memory system, the following governance rules are enforced:

*   **Context Source**: The origin of any loaded context item (e.g., Knowledge Packs, Skill Packs, active inputs).
*   **Context Priority**: Rank-ordering of context assets. Constitutional rules (Class 0) and Task Core parameters (Class 1) are non-evictable. Domain-specific and dependency-required packs are prioritised over optional assets.
*   **Context Freshness**: Every context asset carries a metadata timestamp indicating when it was retrieved.
*   **Context Expiry**: Context is automatically cleared from active memory upon session termination, or when the pipeline transitions to a stage that no longer requires it.
*   **Conflict Resolution**: When conflicting context fragments are loaded (e.g., differing sector thresholds), the Context Manager resolves them using rank authority: Domain-specific deep dives override general sector profiles. Unresolved analytical conflicts must be propagated directly to the reasoning engine, rather than arbitrated by the context layer.
*   **Stale Context Detection**: The Context Manager compares the context asset's freshness timestamp against its staleness threshold. If stale, a `CONTEXT_STALE` flag is set, which down-weights the downstream `EvidenceQualityScore` by 15% and mandates an explicit output warning.
*   **Context Lineage**: All loaded context segments must preserve their full lineage: Source ID, retrieval time, parent-child relations, and transformation/summarization history.
*   **Memory Isolation**: The Context Manager serves as a transient buffer for the current session. It never stores permanent session histories or logs, which remains the sole responsibility of the State Manager.

---

# 11. Context Allocation Object

```yaml
ContextAllocationObject:
  AllocationID:
  TaskID:
  DepthTier:
  LoadedKnowledgePacks: []
  LoadedSkillPacks: []
  LoadedFrameworks: []
  EvictionLog:
    - PackID:
      EvictedAt:
      Reason:
  OverflowFlags:
    - Stage:
      DroppedContent: []
      ScopeReductionNote:
  TotalBudgetUsed:      # percentage of context window
  CreatedAt:
  UpdatedAt:
```

This object is referenced by the `StateObject` (per `AI_State_Manager_v_0.0.md` §5, field `ContextAllocationRef`).

---

# 12. Interfaces

**Consumed by:** AI_Execution_Engine (exclusively, per Execution Engine §32)
**Reads from:** AI_Module_Registry, AI_Framework_Registry, AI_Dependency_Map (for priority and dependency data)
**Writes to:** State Manager (via `ContextAllocationRef`)

---

# 13. Governance

- Context budget ceilings (Section 7) may only be changed via explicit architectural revision, not runtime adjustment
- Critical Gate domains (Section 6, item 2) are defined by the Constitution's CIO Authority Rules and cannot be redefined by this document — this document only enforces their non-evictable status
- Every eviction and overflow event must be logged; silent context loss is a governance violation

---

# 14. Final Specification

The AI Context Manager makes multi-pack knowledge loading operationally safe within real context window limits. It guarantees that scope reduction is always visible and flagged rather than silently absorbed — directly resolving the audit's context capacity gap (CV-03, MV-07).

---

# Document Information

**Document:** AI_Context_Manager_v_0_0.md
**Version:** v_0.0
**Status:** Production Ready
**Dependencies:** AI_Execution_Engine_v_0.0.md, AI_Module_Registry_v_0.0.md, AI_Framework_Registry_v_0.0.md, AI_Dependency_Map_v_0.0.md
**Consumed By:** AI_Execution_Engine_v_0.0.md (exclusively)
**Resolves:** CV-03 (Missing Context Manager), MV-07 (No Context Capacity Model)

# END OF DOCUMENT


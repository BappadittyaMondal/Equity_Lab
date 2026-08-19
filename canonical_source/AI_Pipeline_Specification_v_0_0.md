<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Pipeline Specification  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Pipeline_Specification_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Authoritative)
**Category:** Cross-Cutting Governance Document
**Priority:** Critical
**Role:** Single Source of Truth for Pipeline Order
**Architecture State:** Frozen

---

# 1. Purpose

This document resolves the pipeline-order contradiction identified in the forensic audit (CV-02), where `AI_Task_Orchestrator_v_0.0`, `AI_Execution_Engine_v_0.0`, and `AI_Architecture_Overview_v_0.0` each declared a different processing sequence.

This document is now the **single authoritative source** for pipeline order. All three source documents are corrected to reference this specification rather than re-declaring the sequence independently (see Section 5 — Propagation).

---

# 2. Analysis — Why the Contradiction Existed

| Document | Declared Sequence |
|---|---|
| Task Orchestrator v_0.0 | Orchestrator → **Execution Engine** → Intelligence Engine → Research → Reasoning → Audit → Output |
| Execution Engine v_0.0 | Orchestrator → **Intelligence Engine** → ResearchPlanObject → Execution Engine → Research → Reasoning → Audit → Output |
| Architecture Overview v_0.0 | Orchestrator → Execution Engine → Intelligence Engine → Research → Reasoning → Audit → Output |

**Root cause:** The Execution Engine's own object contract requires a `ResearchPlanObject` as input (per its Section 8 — Runtime Session Object, and Section 11 — Session Initialization, which lists `ResearchPlanObject validation` as a required step). A `ResearchPlanObject` can only be produced by the Intelligence Engine. Therefore the Execution Engine **cannot** run before the Intelligence Engine — its own input contract makes this structurally impossible.

The Task Orchestrator and Architecture Overview diagrams were drawn incorrectly and never validated against the Execution Engine's actual object contract.

---

# 3. Authoritative Pipeline

The following sequence is now binding on every document in the system:

```
┌─────────────────────────────────────────────────────────┐
│ STAGE 0 — Constitutional Authority                       │
│ AI_Project_Instructions_v_0.0.md (governs all stages)          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 1 — Task Orchestrator                              │
│ Input:  Raw user request                                 │
│ Output: TaskObject                                       │
└─────────────────────────────────────────────────────────┘
                        ↓ TaskObject
┌─────────────────────────────────────────────────────────┐
│ STAGE 2 — Intelligence Engine                            │
│ Input:  TaskObject                                       │
│ Output: ResearchPlanObject                                │
│         (module selection, framework selection,          │
│          execution graph, depth tier confirmation)       │
└─────────────────────────────────────────────────────────┘
                        ↓ ResearchPlanObject
┌─────────────────────────────────────────────────────────┐
│ STAGE 3 — Execution Engine                               │
│ Input:  ResearchPlanObject                                │
│ Output: Scheduled runtime session; coordinates Stages 4-6 │
│         via Registry Layer, State Manager, Context Mgr    │
└─────────────────────────────────────────────────────────┘
                        ↓ (orchestrates)
┌─────────────────────────────────────────────────────────┐
│ STAGE 4 — Research Engine                                 │
│ Input:  ResearchPlanObject (via Execution Engine)         │
│ Output: ResearchObject + EvidenceObject                   │
└─────────────────────────────────────────────────────────┘
                        ↓ ResearchObject + EvidenceObject
┌─────────────────────────────────────────────────────────┐
│ STAGE 5 — Reasoning Skills                                │
│ Input:  ResearchObject + EvidenceObject                   │
│ Output: DecisionObject                                    │
└─────────────────────────────────────────────────────────┘
                        ↓ DecisionObject
┌─────────────────────────────────────────────────────────┐
│ STAGE 6 — Quality Audit                                   │
│ Input:  DecisionObject                                    │
│ Output: AuditObject (Verdict: Approve/Warnings/Reject)    │
└─────────────────────────────────────────────────────────┘
                        ↓ AuditObject (if not REJECT)
┌─────────────────────────────────────────────────────────┐
│ STAGE 7 — Output System                                   │
│ Input:  AuditObject + DecisionObject + TaskObject          │
│ Output: OutputObject → User                                │
└─────────────────────────────────────────────────────────┘
```

**Critical clarification on Stage 3:** The Execution Engine does not perform research, reasoning, or auditing itself. It is the **runtime coordinator** — it schedules Stages 4, 5, and 6, resolves their dependencies via the Registry Layer, manages context and state throughout, and hands off the final validated objects between them. It is drawn as a single stage here because it is the architectural "kernel" the other stages run inside of, not because it executes sequentially before them in the object-flow sense.

---

# 4. Object Flow Validation

| Stage | Consumes | Produces | Validated Against |
|---|---|---|---|
| 1. Task Orchestrator | Raw text | `TaskObject` | AI_Data_Object_Standard |
| 2. Intelligence Engine | `TaskObject` | `ResearchPlanObject` | AI_Module_Registry, AI_Framework_Registry |
| 3. Execution Engine | `ResearchPlanObject` | Runtime session (coordinates 4–6) | AI_Dependency_Map, AI_State_Manager, AI_Context_Manager |
| 4. Research Engine | `ResearchPlanObject` (via Execution Engine) | `ResearchObject`, `EvidenceObject` | AI_Data_Object_Standard |
| 5. Reasoning Skills | `ResearchObject`, `EvidenceObject` | `DecisionObject` | AI_Confidence_Standard_v_0.0 |
| 6. Quality Audit | `DecisionObject` | `AuditObject` | AI_Confidence_Standard_v_0.0, AI_Explainability_Standard |
| 7. Output System | `AuditObject`, `DecisionObject`, `TaskObject` | `OutputObject` | AI_Output_System_v_0.0 |

No stage in this table has a circular or backward dependency. This resolves CV-02 in full.

---

# 5. Propagation — Required Corrections to Source Documents

The following corrections must be applied to the three original documents. Each correction is a **surgical replacement** of the incorrect pipeline diagram only — no other content in these documents is affected.

### 5.1 — AI_Task_Orchestrator_v_0.0.md, Section 3 (Architectural Position)

**Replace:**
```
The Task Orchestrator sits immediately after the constitutional layer and immediately before execution.

User Request → AI_Project_Instructions → AI_Task_Orchestrator → TaskObject
→ AI_Execution_Engine → AI_Intelligence_Engine → AI_Research_Engine
→ AI_Reasoning_Skills → AI_Quality_Audit → AI_Output_System
```

**With:**
```
The Task Orchestrator sits immediately after the constitutional layer and
immediately before intelligence planning. Authoritative pipeline order is
defined in AI_Pipeline_Specification_v_0.0.md.

User Request → AI_Project_Instructions → AI_Task_Orchestrator → TaskObject
→ AI_Intelligence_Engine → ResearchPlanObject → AI_Execution_Engine
→ [Research → Reasoning → Audit] → AI_Output_System
```

### 5.2 — AI_Execution_Engine_v_0.0.md, Section 3 (Architectural Position)

No change required — this document's diagram was already correct and matches Section 3 of this specification. Add one line:

**Append:** *"This sequence is the authoritative pipeline order; see AI_Pipeline_Specification_v_0.0.md."*

### 5.3 — AI_Architecture_Overview_v_0.0, Section 7 (End-to-End Processing Flow)

**Replace** the existing flow diagram with the diagram in Section 3 of this document, and add a reference line:

**Add:** *"Full pipeline authority and object-flow validation: see AI_Pipeline_Specification_v_0.0.md (Section 13A/D — Dependency Rules and Decision Authority Matrix apply this ordering)."*

### 5.4 — Dependency Rules cross-check (from Architecture Overview Task 03)

The previously delivered **Dependency Rules** section (Task 03 of the earlier architecture expansion) already lists:
```
Allowed: Task → Execution, Execution → Intelligence, Research → Reasoning...
```
This line requires correction to match the authoritative order:
```
Allowed: Task Orchestrator → Intelligence Engine → Execution Engine
         (Execution Engine coordinates) → Research Engine → Reasoning Skills
         → Quality Audit → Output System
```

---

# 6. Governance Rule

> Going forward, **no document may redraw the pipeline diagram independently**. Every engine specification references `AI_Pipeline_Specification_v_0.0.md` rather than re-stating the sequence. This is now enforced as Synchronization Rule S-10 (extending the rule set delivered previously):

**Rule S-10 — Single Pipeline Source of Truth**
> The processing pipeline sequence is defined exclusively in AI_Pipeline_Specification_v_0.0.md. All engine and architecture documents reference this file for sequence; none redeclare it. Any apparent pipeline diagram elsewhere is illustrative only and defers to this document on conflict.

---

# 7. Self-Audit

- ✓ Checked against Execution Engine's own object contract (`ResearchPlanObject` requirement) — consistent
- ✓ Checked against Intelligence Engine's declared output (`ResearchPlanObject`) — consistent
- ✓ Checked against Architecture Overview's Engine Contracts (Task 02, delivered previously) — consistent, no changes needed there
- ✓ No circular dependency introduced
- ✓ No object introduced that isn't already defined in existing engine specs

**Downstream files requiring the propagation edits above:** `AI_Task_Orchestrator_v_0.0.md` (Section 3), `AI_Architecture_Overview_v_0.0` (Section 7, and the Dependency Rules addendum), `AI_Execution_Engine_v_0.0.md` (append-only, one line).

---

# Document Information

**Document:** AI_Pipeline_Specification_v_0.0.md
**Version:** v_0.0
**Status:** Production Ready — Authoritative
**Resolves:** CV-02 (Forensic Audit, Critical Vulnerability)

# END OF DOCUMENT

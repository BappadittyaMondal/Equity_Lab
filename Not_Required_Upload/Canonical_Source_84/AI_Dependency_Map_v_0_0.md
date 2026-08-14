<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Dependency Map  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# **AI\_Dependency\_Map\_v_0.0**

**Version:** v_0.0 **Status:** Production Ready (Final) **Category:** Core Registry / Runtime Infrastructure **Priority:** Critical **Role:** Dependency Resolution and Loading Order Authority **Architecture State:** Frozen

---

# **Table of Contents**

1. Purpose  
2. Architectural Position  
3. Engine Dependency Graph  
4. Object Dependency Graph  
5. Skill ↔ Knowledge Dependency Matrix  
6. Forbidden Cycles  
7. Loading Order  
8. Resolution Algorithm  
9. Interfaces  
10. Governance  
11. Final Specification

---

# **1\. Purpose**

The AI Dependency Map is the authoritative graph of every dependency relationship in the IERL AI Operating System: engine-to-engine, object-to-object, and — critically — Skill Pack-to-Knowledge Pack. It was identified as missing in the Forensic Audit (CV-03), leaving the Execution Engine, Intelligence Engine, and Context Manager with no machine-readable dependency graph to resolve against.

---

# **2\. Architectural Position**

AI\_Intelligence\_Engine ──┐  
                          ├──→ AI\_Dependency\_Map (read-only query)  
AI\_Execution\_Engine ──────┤  
                          │  
AI\_Context\_Manager ───────┘

The Dependency Map is a registry-tier component. It is never modified at runtime — only queried. Updates happen through deliberate version-controlled revision (per Synchronization Rule S-09, Frozen Core Amendment Protocol).

---

# **3\. Engine Dependency Graph**

This restates and formalizes the Allowed Dependency Table already established in `AI_Architecture_Overview_v_0.0` §13A, now expressed as a queryable graph:

EngineDependencyGraph:  
  AI\_Task\_Orchestrator:  
    depends\_on: \[AI\_Project\_Instructions\]  
  AI\_Intelligence\_Engine:  
    depends\_on: \[AI\_Task\_Orchestrator.TaskObject, AI\_Module\_Registry, AI\_Framework\_Registry, AI\_Dependency\_Map\]  
  AI\_Execution\_Engine:  
    depends\_on: \[AI\_Intelligence\_Engine.ResearchPlanObject, AI\_Module\_Registry, AI\_Framework\_Registry,  
                 AI\_State\_Manager, AI\_Context\_Manager, AI\_Dependency\_Map\]  
  AI\_Research\_Engine:  
    depends\_on: \[AI\_Execution\_Engine (scheduled\_by), AI\_Module\_Registry, AI\_Framework\_Registry, Knowledge\_Packs\]  
  AI\_Reasoning\_Skills:  
    depends\_on: \[AI\_Research\_Engine.ResearchObject, AI\_Research\_Engine.EvidenceObject,  
                 AI\_Confidence\_Standard, AI\_Explainability\_Standard, Skill\_Packs\]  
  AI\_Quality\_Audit:  
    depends\_on: \[AI\_Reasoning\_Skills.DecisionObject, AI\_Confidence\_Standard,  
                 AI\_Explainability\_Standard, AI\_Project\_Instructions\]  
  AI\_Output\_System:  
    depends\_on: \[AI\_Quality\_Audit.AuditObject (verdict \!= REJECT), AI\_Reasoning\_Skills.DecisionObject,  
                 AI\_Confidence\_Standard, AI\_Explainability\_Standard\]

This graph is consistent with `AI_Pipeline_Specification_v_0.0.md` and contains no cycles (verified in Section 6).

---

# **4\. Object Dependency Graph**

ObjectDependencyGraph:  
  TaskObject:  
    produced\_by: AI\_Task\_Orchestrator  
    required\_for: \[ResearchPlanObject, OutputObject\]  
  ResearchPlanObject:  
    produced\_by: AI\_Intelligence\_Engine  
    requires: \[TaskObject\]  
    required\_for: \[ExecutionSession, ResearchObject\]  
  ResearchObject:  
    produced\_by: AI\_Research\_Engine  
    requires: \[ResearchPlanObject\]  
    required\_for: \[DecisionObject\]  
  EvidenceObject:  
    produced\_by: AI\_Research\_Engine  
    requires: \[ResearchPlanObject\]  
    required\_for: \[DecisionObject\]  
  DecisionObject:  
    produced\_by: AI\_Reasoning\_Skills  
    requires: \[ResearchObject, EvidenceObject\]  
    required\_for: \[AuditObject, OutputObject\]  
  AuditObject:  
    produced\_by: AI\_Quality\_Audit  
    requires: \[DecisionObject\]  
    required\_for: \[OutputObject\]  
  OutputObject:  
    produced\_by: AI\_Output\_System  
    requires: \[AuditObject, DecisionObject, TaskObject\]  
    required\_for: \[\] \# terminal object  
  StateObject:  
    produced\_by: AI\_State\_Manager  
    requires: \[TaskObject\]  
    required\_for: \[\] \# cross-cutting, referenced not chained  
  ContextAllocationObject:  
    produced\_by: AI\_Context\_Manager  
    requires: [ResearchPlanObject]
    required_for: [] # cross-cutting, referenced not chained

---

# **4A. Canonical Dependency Contract**

Every active dependency relationship in the operating system must conform to this canonical contract schema:

`DependencyRelation: [Provider] → [Consumer] → [Object] → [Interface] → [Direction] → [Failure Owner] → [Retry Owner] → [Version]`

### Semantics:
*   **Provider**: The source engine or registry that produces the object or capability.
*   **Consumer**: The downstream engine or registry that consumes the object or capability.
*   **Object**: The structured canonical data object (e.g., `TaskObject`, `ResearchObject`) being exchanged.
*   **Interface**: The specific API endpoint, schema segment, or method signature used for communication.
*   **Direction**: The flow direction of data (`FORWARD` for pipeline progression, `REVERSE` for feedback/rollback).
*   **Failure Owner**: The component responsible for catching failures at this boundary (e.g., Execution Engine).
*   **Retry Owner**: The component that determines and triggers retries for this link.
*   **Version**: The locked version of the interface (e.g., `v_0.0`).

### Master Dependency Table:

| Provider | Consumer | Object | Interface | Direction | Failure Owner | Retry Owner | Version |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| Task Orchestrator | Intelligence Engine | `TaskObject` | `TaskObjectSchema` | FORWARD | Task Orchestrator | None | v_0.0 |
| Intelligence Engine | Execution Engine | `ResearchPlanObject` | `ResearchPlanSchema` | FORWARD | Intelligence Engine | None | v_0.0 |
| Execution Engine | Research Engine | `ResearchPlanObject` | `ResearchPlanSchema` | FORWARD | Execution Engine | Execution Engine | v_0.0 |
| Research Engine | Reasoning Skills | `ResearchObject` | `ResearchObjectSchema` | FORWARD | Execution Engine | Execution Engine | v_0.0 |
| Research Engine | Reasoning Skills | `EvidenceObject` | `EvidenceObjectSchema` | FORWARD | Execution Engine | Execution Engine | v_0.0 |
| Reasoning Skills | Quality Audit | `DecisionObject` | `DecisionObjectSchema` | FORWARD | Execution Engine | Execution Engine | v_0.0 |
| Quality Audit | Output System | `AuditObject` | `AuditObjectSchema` | FORWARD | Execution Engine | None | v_0.0 |
| Output System | Downstream User | `OutputObject` | `OutputObjectSchema` | FORWARD | Output System | None | v_0.0 |

---

# **5\. Skill ↔ Knowledge Dependency Matrix**

This closes the gap identified in Forensic Audit MV-05 (no formal Skill Pack → Knowledge Pack dependency declaration). Full matrix for representative Skill Packs (extend this table for all 34 Skill Packs as they are formally onboarded — this is the required schema and a representative sample):

| Skill Pack | Required Knowledge Domains | Optional Knowledge Domains |
| ----- | ----- | ----- |
| Banking Analysis Skill | 31 (Banking Sector), 26 (Financial Institution Analysis), 2 (Financial Statements), 8 (Governance) | 22 (Regulatory), 9 (Risk Management) |
| Forensic Accounting Skill | 24 (Forensic Accounting), 2 (Financial Statements), 3 (Accounting) | 8 (Governance), 6 (Fundamental Analysis) |
| DCF Valuation Skill | 5 (Valuation), 2 (Financial Statements), 1 (Economics) | 13 (Macroeconomic Themes), 25 (Moat & Competitive Advantage) |
| Moat/Competitive Advantage Skill | 25 (Moat), 6 (Fundamental Analysis), 12 (Industry Knowledge) | 27 (Super-Investor Tracking) |
| Multibagger/Turnaround Skill | 28 (Multibagger Framework), 29 (Micro/Small-Cap Risk) | 27 (Smart Money Signals), 40 (Screening) |
| Technical Pattern Skill | 7 (Technical Analysis), 30 (Swing/Positional Patterns) | 19 (Derivatives & Options) |
| Pharma Sector Skill | 32 (Pharma Deep Dive), 2 (Financial Statements) | 22 (Regulatory & Tax) |
| Portfolio Sizing Skill | 43 (Portfolio Management Rules), 29 (Micro/Small-Cap Risk) | 9 (Risk Management), 10 (Portfolio Management conceptual) |

**Format Rule for Remaining 26 Skill Packs:** Each entry follows the schema `Skill: Required Domains [comma list] | Optional Domains [comma list]`. Required domains are non-evictable in the Context Manager's priority ranking (Context Manager §6, item 1\) when that skill is active.

---

# **6\. Forbidden Cycles**

Per AI\_Architecture\_Overview\_v_0.0.md §13A, the following are confirmed structurally absent from this graph:

* ❌ Output System → Research Engine  
* ❌ Research Engine → Reasoning Skills (backward)  
* ❌ Reasoning Skills → Research Engine (backward)  
* ❌ Quality Audit → Research Engine / Intelligence Engine  
* ❌ Any Registry → Any Engine (registries are query-only)

**Verification method:** A topological sort of the Engine Dependency Graph (Section 3\) completes without a cycle-detection failure — confirmed by inspection: every `depends_on` edge points strictly toward an earlier pipeline stage or a registry-tier component, never forward or to itself.

---

# **7\. Loading Order**

Derived directly from the Object Dependency Graph (Section 4\) and Pipeline Specification:

1\. AI\_Project\_Instructions      (always resident — Class 0\)  
2\. TaskObject                    (Stage 1 output)  
3\. Module Registry \+ Framework Registry \+ Dependency Map (queried at Stage 2\)  
4\. ResearchPlanObject            (Stage 2 output)  
5\. State Manager session init \+ Context Manager allocation (Stage 3\)  
6\. Knowledge Packs (per Section 5 matrix, loaded at Stage 4\)  
7\. ResearchObject \+ EvidenceObject (Stage 4 output)  
8\. Skill Packs (per Section 5 matrix, loaded at Stage 5\)  
9\. DecisionObject                (Stage 5 output)  
10\. AuditObject                  (Stage 6 output)  
11\. OutputObject                 (Stage 7 output — terminal)

---

# **8\. Resolution Algorithm**

When the Intelligence Engine requests a Skill Pack, the Execution Engine resolves its full dependency set as follows:

FUNCTION resolve\_dependencies(skill\_pack\_id):  
    required \= lookup(Section 5 matrix, skill\_pack\_id).required\_domains  
    optional \= lookup(Section 5 matrix, skill\_pack\_id).optional\_domains

    FOR domain IN required:  
        request\_load(domain, priority \= CRITICAL\_IF\_GATE\_DOMAIN else HIGH)

    FOR domain IN optional:  
        request\_load(domain, priority \= LOW)

    submit\_to\_context\_manager(required \+ optional)  
    // Context Manager applies its own priority ranking (Context Manager §6)  
    // if total exceeds budget — see AI\_Context\_Manager\_v_0.0.md Section 10  
    RETURN loaded\_set, overflow\_flags

If a required domain cannot be loaded due to context overflow, the `OverflowFlags` from Context Manager propagate to the `ResearchPlanObject`, and Research Engine's completeness gate reflects the gap (per Research Engine §22), triggering appropriate confidence reduction downstream — consistent with the Failure & Recovery Architecture already defined.

---

# **AI\_Skill\_Knowledge\_Governance\_v_0.0**

**Version:** v_0.0 **Status:** Production Ready (Final) **Category:** Core Registry Extension **Priority:** High **Role:** Priority Rules, Conflict Resolution, and Fallback Behavior for Skill/Knowledge Loading **Paste Target:** AI\_Dependency\_Map\_v_0.0.md, appended after Section 8 (Resolution Algorithm)

---

# **1\. Purpose**

`AI_Dependency_Map_v_0.0.md` already defines the Skill↔Knowledge dependency matrix (Section 5\) and the automatic loading resolution algorithm (Section 8). This document completes Prompt 9's remaining requirements: **priority rules when multiple skills compete for context**, **conflict resolution when two active Skill Packs recommend contradictory Knowledge Pack versions**, and **fallback behavior when a required domain is entirely unavailable.**

---

# **2\. Priority Rules When Multiple Skills Are Active**

A single task may activate more than one Skill Pack (e.g., "Analyze this NBFC for both forensic risk and technical entry point" activates both Forensic Accounting Skill and Technical Pattern Skill simultaneously).

**Priority order when multiple skills compete for limited context budget** (extends Context Manager §6):

1. **Gate-critical skills first** — Forensic Accounting Skill, Governance Assessment Skill (any skill tied to a CIO Authority Rule per Architecture Overview §13D) receive loading priority over all other active skills  
2. **Primary task skill second** — the skill most directly matching the Task Orchestrator's classified intent (e.g., if the user asked for "forensic risk with a secondary technical note," Forensic Accounting is primary, Technical Pattern is secondary)  
3. **Secondary/supporting skills third** — loaded only if budget remains after (1) and (2)  
4. **Skills below priority rank whose required domains cannot fit are deferred, not dropped** — see Section 4 (Fallback)

---

# **3\. Conflict Resolution — Contradictory Knowledge Pack Guidance**

When two simultaneously active Skill Packs draw on Knowledge Packs that offer conflicting guidance (e.g., DCF Valuation Skill's Domain 5 suggests a growth-adjusted multiple while a loaded Sector Deep Dive domain suggests a sector-capped multiple for the same company), resolution follows this order:

1\. Domain-specific guidance overrides general guidance  
   (Sector Deep Dive \> general Valuation domain, when both apply  
   to the same company's sector)

2\. Higher-numbered "Critical Gate" domains override standard domains  
   (Domain 24 Forensic Accounting \> Domain 6 Fundamental Analysis,  
   consistent with existing Knowledge Index Global Conflict  
   Arbitration rules)

3\. If neither rule resolves the conflict, both viewpoints are  
   preserved and passed to Reasoning Skills as competing evidence  
   — per AI\_Confidence\_Standard\_v_0.0.md Section 12's  
   ConsistencyFactor \= 0.6 case (material contradiction presented  
   as competing scenarios, never silently resolved by the loading  
   layer)

**Critical rule:** The Dependency Map / Context Manager layer never silently picks a winner between conflicting Knowledge Pack guidance on a substantive analytical question. Rule 3 ensures unresolved conflicts are explicitly surfaced downstream to Reasoning Skills, consistent with the existing prohibition on suppressing contradictory evidence (Confidence Standard §23, Explainability Standard §11).

---

# **4\. Fallback Behavior — Required Domain Unavailable**

Triggered when a Skill Pack's `required_domains` (per Dependency Map §5 matrix) cannot be loaded due to context overflow (per Context Manager §10) or a missing/deprecated Knowledge Pack:

Required domain unavailable  
    ↓  
Check: is this a Critical Gate domain (e.g., Domain 24, Domain 8)?  
    ↓ YES  
Escalate as F3 failure (Architecture Overview §13C)  
    ↓  
Skill Pack does not execute; Intelligence Engine notified;  
ResearchPlanObject flags SKILL\_BLOCKED with reason  
    ↓ NO (non-critical required domain)  
Attempt substitution: is there an "optional" domain from the  
same matrix entry that covers similar ground?  
    ↓ YES  
Load substitute; flag DOMAIN\_SUBSTITUTED in ContextAllocationObject  
    ↓ NO  
Proceed with reduced scope; flag REQUIRED\_DOMAIN\_MISSING;  
Research Engine's completeness gate reflects this gap, which  
propagates a CoverageFactor penalty per Confidence Standard §12

This directly extends the existing Context Manager Overflow Protocol (§10) with skill-specific fallback logic, rather than treating skill/knowledge loading failures generically.

---

# **5\. Worked Example**

Task: "Deep dive on \[NBFC\]: forensic risk \+ technical entry"  
Active Skills: Forensic Accounting Skill (primary, gate-critical),  
               Technical Pattern Skill (secondary)

Priority resolution (Section 2):  
  1\. Forensic Accounting's required domains (24, 2, 3\) load first  
     — gate-critical, guaranteed  
  2\. Technical Pattern's required domains (7, 30\) load second  
     — primary/secondary skill budget allows both to fit at Deep tier

No conflict detected (Section 3 not triggered — domains don't overlap  
on the same analytical question)

Result: Both skills execute with full required-domain coverage.  
No fallback needed.

Alternate scenario — context-constrained (Standard tier instead of Deep):  
  1\. Forensic Accounting's required domains load first (gate-critical)  
  2\. Technical Pattern's required domains exceed remaining budget  
     at Standard tier  
  3\. Fallback (Section 4): Technical Pattern is non-critical →  
     attempt substitution → no suitable substitute found →  
     proceed with SKILL\_DEFERRED flag; Technical Pattern does not  
     execute this pass; user output notes technical analysis was  
     not included due to depth tier constraints

---

# **6\. Self-Audit**

* ✓ Extends (does not duplicate) Dependency Map §5/§8 and Context Manager §6/§10  
* ✓ Consistent with Confidence Standard §12 ConsistencyFactor handling for unresolved conflicts  
* ✓ Consistent with Architecture Overview §13C Failure Classification (F3 escalation for gate-critical domain unavailability)  
* ✓ No new objects introduced; uses existing `ResearchPlanObject`, `ContextAllocationObject` flag fields

---

# **Document Information**

**Document:** AI\_Skill\_Knowledge\_Governance.md **Version:** v_0.0 **Paste Into:** AI\_Dependency\_Map\_v_0.0.md (append after Section 8\) **Resolves:** Remaining Prompt 9 requirements (priority rules, conflict resolution, fallback)

# **END OF DOCUMENT**

—---------------------------------------------------------------------------------------------------

# **9\. Interfaces**

**Queried by:** AI\_Intelligence\_Engine, AI\_Execution\_Engine, AI\_Context\_Manager **Never modified by:** Any engine at runtime — updates are a deliberate registry maintenance event only

---

# **10\. Governance**

* Every new Skill Pack onboarded must add an entry to the Section 5 matrix before it can be selected by the Intelligence Engine  
* A Skill Pack with no matrix entry is treated as `UNRESOLVED_DEPENDENCY` and cannot be activated — this prevents the exact gap identified in MV-05 from recurring as new packs are added  
* Cycle-detection (Section 6 method) must be re-run any time a new engine or object type is introduced

---

# **11\. Final Specification**

The AI Dependency Map closes the formal dependency-resolution gap identified across CV-03 and MV-05. It gives the Intelligence Engine and Context Manager a queryable, versioned graph for engine dependencies, object dependencies, and — critically — which Knowledge Packs are mandatory companions to which Skill Packs, preventing incomplete knowledge context during skill execution.

---

# **Document Information**

**Document:** AI\_Dependency\_Map.md **Version:** v_0.0 **Status:** Production Ready **Dependencies:** AI\_Module\_Registry.md, AI\_Framework\_Registry.md, AI\_Pipeline\_Specification\_v_0.0.md **Consumed By:** AI\_Intelligence\_Engine.md, AI\_Execution\_Engine.md, AI\_Context\_Manager.md **Resolves:** CV-03 (Missing Dependency Map), MV-05 (No Skill↔Knowledge Dependency Declaration)

# **END OF DOCUMENT**


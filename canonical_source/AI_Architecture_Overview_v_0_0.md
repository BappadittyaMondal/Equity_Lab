<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Architecture Overview  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Architecture_Overview_v_0.0

**Version:** v_0.0 (Final — Phase 1 Complete)
**Status:** Production Ready
**Category:** Master Structural Blueprint
**Priority:** Critical
**Supersedes:** AI_Architecture_Overview_v_0.0 (Sections 8–17 were listed but never written; Tasks 01–06 were pasted out of order and out of location in the v_0.0 working draft — both defects corrected here)

---

# Table of Contents

## Part 1 — Architecture Foundation
1. Purpose
2. Vision
3. Scope
   **3A. Architecture Boundaries**
4. Design Principles
5. Architecture Layers
6. Core Components
7. End-to-End Processing Flow

## Part 2 — Engine Architecture
8. Core Engine Responsibilities
   **8A. Engine Contracts**
9. Object Flow
10. Object Ownership
11. Cross-Cutting Standards
12. Registries & Libraries
13. Dependency Hierarchy
    **13A. Dependency Rules**
    **13B. Synchronization Rules**
    **13C. Failure & Recovery Architecture**
    **13D. Decision Authority Matrix**

## Part 3 — Governance
14. Version Compatibility
15. Future Expansion
16. Frozen Core Documents
17. Final Specification

---

# PART 1 — ARCHITECTURE FOUNDATION

---

# 1. Purpose

The AI_Architecture_Overview is the master structural blueprint of the IERL AI Operating System. It defines the system's layers, engines, object flow, dependency structure, and governance rules — the single reference for how the system is built, not how any individual engine reasons internally.

---

# 2. Vision

A modular, auditable, and explainable AI Operating System for institutional-grade equity research, where every engine has one clearly bounded responsibility, every handoff between engines is a standardized object, and every architectural decision is traceable to a governing document.

---

# 3. Scope

This overview applies to:

- Core Engines
- Registries
- Object Standards
- Cross-Cutting Standards
- Knowledge Packs
- Skill Packs
- Future Extensions

---

# 3A. Architecture Boundaries

## What This Document Governs

The AI_Architecture_Overview governs:

- System layer definitions
- Engine identification and responsibilities
- Standard object flow between engines
- Engine interaction patterns
- Registry and library structure
- Dependency hierarchy
- Architectural governance rules
- Extension strategy for future capabilities

## What This Document Does NOT Govern

The Architecture Overview is deliberately boundary-limited. The following responsibilities belong exclusively to their dedicated specifications and must NEVER be defined, embedded, or implied inside this document:

| Category | Belongs To |
|---|---|
| Prompt wording and templates | AI_Output_System_v_0.0.md |
| Research methodology and evidence rules | AI_Research_Engine_v_0_0.md |
| Reasoning logic and conflict resolution | AI_Reasoning_Skills_v_0_0.md |
| Object field definitions and schema | AI_Object_Schemas_v_0.0.md |
| Confidence calculation and vocabulary | AI_Confidence_Standard_v_0.0.md |
| Explainability rules and formatting | AI_Explainability_Standard_v_0.0.md |
| Quality metrics and pass/fail thresholds | AI_Quality_Audit_v_0.0.md |
| Module and framework algorithms | AI_Module_Registry_v_0.0.md / AI_Framework_Registry_v_0.0.md |
| Task classification logic | AI_Task_Orchestrator_v_0.0.md |
| Execution sequencing and scheduling | AI_Execution_Engine_v_0.0.md |
| Domain-specific analysis rules | Knowledge Packs and Skill Packs (via Module Registry) |
| Constitutional principles and ethics | AI_Project_Instructions_v_0.0.md |
| Runtime state tracking | AI_State_Manager_v_0.0.md |
| Context window management | AI_Context_Manager_v_0_0.md |

## Boundary Rule

> If a fact, rule, formula, or instruction belongs to one of the owned documents above, it does not appear here — even as a summary or example. Duplication across documents creates drift. Drift creates inconsistency. Inconsistency degrades system behavior. When in doubt, the rule lives in its owning document. This document only maps that it exists.

## Architecture Scope Summary

```
IN SCOPE                          OUT OF SCOPE
──────────────────────────────    ────────────────────────────────
Layer definitions                 Prompt wording
Engine names and roles            Research strategies
Object flow between engines       Reasoning logic
Registry structure                Scoring formulas
Dependency hierarchy              Object field schemas
Extension points                  Module algorithms
Governance rules                  Quality thresholds
Failure routing patterns          Domain knowledge
Decision authority                Constitutional principles
Synchronization hierarchy         Task classification logic
```

---

# 4. Design Principles

The architecture follows seven principles.

### Separation of Responsibility
Every engine owns one responsibility.

### Object-Based Communication
Engines exchange standardized objects only.

### Loose Coupling
Internal implementation changes shall not affect other engines.

### Explainability
Every important decision must remain traceable.

### Confidence Awareness
Every conclusion shall include calibrated confidence.

### Extensibility
New capabilities are added through registries, modules, or knowledge packs.

### Auditability
Every major decision must be reproducible and auditable.

---

# 5. Architecture Layers

```
User
   │
Project Instructions
   │
System Constitution
   │
Core Engines
   │
Registries
   │
Knowledge & Skill Libraries
   │
Modules & Frameworks
   │
Output
```

Each layer depends only on the layer above.

---

# 6. Core Components

The AI Operating System consists of:

- Project Instructions
- System Constitution
- Task Orchestrator
- Intelligence Engine
- Execution Engine
- Research Engine
- Reasoning Engine
- Quality Audit
- Output System

Supporting infrastructure:

- State Manager
- Context Manager
- Dependency Map

Supporting standards include:

- Object Schemas / Data Object Standard
- Confidence Standard
- Explainability Standard

Supporting registries include:

- Module Registry
- Framework Registry
- Knowledge Registry
- Skill Registry

---

# 7. End-to-End Processing Flow

**Authoritative sequence** (per AI_Pipeline_Specification_v_0.0.md — this diagram defers to that document on any conflict, per Synchronization Rule S-10, Section 13B):

```
User Request
      │
Task Orchestrator
      │
TaskObject
      │
Intelligence Engine
      │
ResearchPlanObject
      │
Execution Engine
      │  (coordinates the three stages below via
      │   State Manager, Context Manager, Dependency Map)
      │
Research Engine
      │
ResearchObject + EvidenceObject
      │
Reasoning Engine
      │
DecisionObject
      │
Quality Audit
      │
AuditObject
      │
Output System
      │
OutputObject
      │
User Response
```

Every stage exchanges standardized objects defined by **AI_Data_Object_Standard_v_0.0**.

---

# PART 2 — ENGINE ARCHITECTURE

---

# 8. Core Engine Responsibilities

| Engine | One-Line Responsibility |
|---|---|
| Task Orchestrator | Interprets user intent and produces a validated TaskObject |
| Intelligence Engine | Plans research strategy and selects modules/frameworks, producing a ResearchPlanObject |
| Execution Engine | Coordinates runtime scheduling, state, and context across Research, Reasoning, and Audit |
| Research Engine | Collects and validates evidence, producing ResearchObject + EvidenceObject |
| Reasoning Skills | Forms a conclusion from evidence, producing a DecisionObject |
| Quality Audit | Independently validates the DecisionObject, producing an AuditObject |
| Output System | Renders the audited decision into a compliant, user-facing OutputObject |

Full input/output/failure detail for each engine is defined in Section 8A below — this table is a summary only, per the Boundary Rule (Section 3A).

---

# 8A. Engine Contracts

Every engine in the IERL AI Operating System operates under a formal contract. The contract defines what each engine consumes, produces, guarantees, how it handles failure, and what it depends on. Engine contracts are binding. No engine may accept inputs outside its contract or produce outputs not defined by its contract.

## Contract Table — All Core Engines

### ENGINE 1 — AI Task Orchestrator

| Contract Field | Definition |
|---|---|
| Consumes | Raw user request (natural language string) |
| Produces | Validated TaskObject (intent, task type, depth tier, constraints, context) |
| Guarantees | Every output TaskObject is fully validated, unambiguous, and machine-readable before handoff |
| Dependencies | AI_Project_Instructions_v_0.0.md (constitutional compliance check) |
| Failure Behavior | If intent cannot be resolved → return ClarificationRequest to user; never pass an ambiguous TaskObject downstream |
| Extension Points | New task types registered via Module Registry; never hard-coded here |
| Version Compatibility | TaskObject schema is owned by AI_Object_Schemas_v_0.0.md; changes to schema require version bump |

### ENGINE 2 — AI Intelligence Engine

| Contract Field | Definition |
|---|---|
| Consumes | Validated TaskObject |
| Produces | Validated ResearchPlanObject (modules selected, frameworks selected, depth tier confirmed, execution graph) |
| Guarantees | Every module and framework selected is registry-validated; planning output is explainable; no un-registered capability is invoked |
| Dependencies | AI_Task_Orchestrator_v_0.0.md, AI_Module_Registry_v_0.0.md, AI_Framework_Registry_v_0.0.md, AI_Dependency_Map_v_0.0.md |
| Failure Behavior | If planning fails → simplify plan → attempt reduced-depth research plan → flag confidence reduction; never produce empty plan |
| Extension Points | New planning strategies registered via Module Registry; planning logic is not hard-coded |
| Version Compatibility | ResearchPlanObject schema governed by AI_Object_Schemas_v_0.0.md |

### ENGINE 3 — AI Execution Engine

| Contract Field | Definition |
|---|---|
| Consumes | Validated ResearchPlanObject from Intelligence Engine |
| Produces | Coordinated runtime session; registry load decisions; runtime state via AI_State_Manager |
| Guarantees | Deterministic orchestration: same validated inputs + same registry snapshot → same execution sequence; no gate bypassed |
| Dependencies | AI_Intelligence_Engine_v_0.0.md, AI_Module_Registry_v_0.0.md, AI_Framework_Registry_v_0.0.md, AI_State_Manager_v_0.0.md, AI_Context_Manager_v_0_0.md, AI_Dependency_Map_v_0.0.md |
| Failure Behavior | Engine failure → log state → retry per retry policy → escalate to Quality Audit if unresolved → graceful degradation |
| Extension Points | New execution strategies added via Module Registry; kernel logic is frozen |
| Version Compatibility | Object schemas and state contracts governed by AI_Object_Schemas_v_0.0.md |

### ENGINE 4 — AI Research Engine

| Contract Field | Definition |
|---|---|
| Consumes | Validated ResearchPlanObject (via Execution Engine) |
| Produces | Validated ResearchObject + EvidenceObject (evidence collected, sources validated, completeness flag set) |
| Guarantees | Every piece of evidence is source-attributed; no conclusion is formed during research; research is reproducible |
| Dependencies | AI_Intelligence_Engine_v_0.0.md, AI_Module_Registry_v_0.0.md, AI_Framework_Registry_v_0.0.md, Knowledge Packs (loaded via registry) |
| Failure Behavior | Source unavailable → retry → alternative source → reduce scope → flag incomplete research → continue with confidence reduction; never fabricate evidence |
| Extension Points | New domain knowledge loaded via Knowledge Packs through Module Registry |
| Version Compatibility | ResearchObject and EvidenceObject schemas governed by AI_Object_Schemas_v_0.0.md |

### ENGINE 5 — AI Reasoning Skills

| Contract Field | Definition |
|---|---|
| Consumes | Validated ResearchObject + EvidenceObject |
| Produces | Validated DecisionObject (conclusion, confidence level, risk flags, reasoning chain, assumptions stated) |
| Guarantees | Every conclusion is traceable to evidence; reasoning chain is explicit; confidence level conforms to AI_Confidence_Standard_v_0.0.md; assumptions are disclosed |
| Dependencies | AI_Research_Engine_v_0_0.md, AI_Confidence_Standard_v_0.0.md, AI_Explainability_Standard_v_0.0.md, Reasoning Skill Packs |
| Failure Behavior | Conflicting evidence → state conflict explicitly → present scenario probabilities → never suppress conflict; if reasoning cannot complete → escalate to Quality Audit |
| Extension Points | New reasoning primitives added via Skill Packs through Module Registry; never hard-coded |
| Version Compatibility | DecisionObject schema governed by AI_Object_Schemas_v_0.0.md |

### ENGINE 6 — AI Quality Audit

| Contract Field | Definition |
|---|---|
| Consumes | Validated DecisionObject from Reasoning Engine |
| Produces | Validated AuditObject (pass/fail verdict, bias flags, confidence assessment, quality score, override authority if applicable) |
| Guarantees | Independent review — never influenced by Research Engine or Reasoning Engine post-completion; every audit is reproducible; mandatory gates cannot be bypassed |
| Dependencies | AI_Reasoning_Skills_v_0_0.md, AI_Confidence_Standard_v_0.0.md, AI_Explainability_Standard_v_0.0.md, AI_Project_Instructions_v_0.0.md (constitutional compliance) |
| Failure Behavior | Audit fail → reject DecisionObject → return to responsible engine with specific deficiency report → never pass a failed audit to Output System |
| Extension Points | New audit gates added via Quality Audit specification; not extensible through Module Registry (audit is independent) |
| Version Compatibility | AuditObject schema governed by AI_Object_Schemas_v_0.0.md |

### ENGINE 7 — AI Output System

| Contract Field | Definition |
|---|---|
| Consumes | Validated AuditObject (pass verdict required); DecisionObject (for content); OutputFormatRequest (from TaskObject) |
| Produces | Final OutputObject formatted for the user — report, recommendation, analysis, or clarification |
| Guarantees | No output is produced from a failed audit; every output includes mandatory SEBI disclaimer; output format matches requested depth tier; confidence vocabulary conforms to AI_Confidence_Standard_v_0.0.md |
| Dependencies | AI_Quality_Audit_v_0.0.md, AI_Reasoning_Skills_v_0_0.md, AI_Explainability_Standard_v_0.0.md, AI_Confidence_Standard_v_0.0.md, Output Templates (via registry) |
| Failure Behavior | Audit fail → Output System returns AuditRejectionNotice to user; low-confidence output → add explicit uncertainty disclosure; never produce unsourced output |
| Extension Points | New output formats and templates registered via Module Registry |
| Version Compatibility | OutputObject schema governed by AI_Object_Schemas_v_0.0.md |

## Contract Enforcement Rule

> No engine may: accept an input object not in its contract; produce an output object not in its contract; skip a contracted dependency; bypass a failure behavior defined in its contract. Contract violations are architecture defects, not runtime configuration issues.

---

# 9. Object Flow

Object flow follows the sequence defined in Section 7 (End-to-End Processing Flow) and the authoritative `AI_Pipeline_Specification_v_0.0.md`. Each engine consumes exactly the object(s) listed as "Consumes" in its Section 8A contract and produces exactly the object(s) listed as "Produces" — no engine may introduce an undeclared object into the flow. Full object field definitions are owned by `AI_Object_Schemas_v_0.0.md` (per the Boundary Rule, Section 3A).

---

# 10. Object Ownership

Each object in the pipeline has exactly one producing engine, per Section 8A:

| Object | Owner (Producer) |
|---|---|
| TaskObject | Task Orchestrator |
| ResearchPlanObject | Intelligence Engine |
| ResearchObject, EvidenceObject | Research Engine |
| DecisionObject | Reasoning Skills |
| AuditObject | Quality Audit |
| OutputObject | Output System |
| StateObject | State Manager (cross-cutting) |
| ContextAllocationObject | Context Manager (cross-cutting) |

No object may be modified by any engine other than its owner once validated and handed off — downstream engines consume, they do not edit.

---

# 11. Cross-Cutting Standards

The following standards apply across every engine and are never redefined locally within an engine specification:

- **AI_Confidence_Standard_v_0.0.md** — universal confidence vocabulary, scoring, and propagation rules
- **AI_Explainability_Standard_v_0.0.md** — universal explanation structure and evidence traceability rules
- **AI_Object_Schemas_v_0.0.md** — universal object schema definitions

---

# 12. Registries & Libraries

| Registry/Library | Purpose |
|---|---|
| Module Registry | Catalog of executable analytical modules |
| Framework Registry | Catalog of analytical frameworks (DCF, Porter's Five Forces, Piotroski F-Score, etc.) |
| Knowledge Registry / Knowledge Packs | Domain reference knowledge (24 domains) |
| Skill Registry / Skill Packs | Analytical methodology and workflow procedures |
| Dependency Map | Cross-component dependency graph, including Skill↔Knowledge dependencies |

Registries are read-only at runtime — consumed by engines, never modified during processing (per Section 13A, Registry Dependency Rules).

---

# 13. Dependency Hierarchy

The dependency hierarchy governs which engines and registries may depend on which others. Full rules are defined in Sections 13A–13D below.

---

# 13A. Dependency Rules

## Purpose

Dependency rules define which engines may call which engines, and which calls are permanently forbidden. Rules prevent architectural drift, circular dependencies, and unauthorized cross-layer access as the system grows.

## Allowed Dependency Chains

```
AI_Project_Instructions (Constitution)
       ↓ governs
AI_Architecture_Overview (Blueprint)
       ↓ governs
AI_Task_Orchestrator
       ↓ produces TaskObject →
AI_Intelligence_Engine
       ↓ produces ResearchPlanObject →
AI_Execution_Engine
       ↓ schedules and loads →
  ├── AI_Module_Registry
  ├── AI_Framework_Registry
  ├── AI_Dependency_Map
  ├── AI_State_Manager
  └── AI_Context_Manager
       ↓ activates →
AI_Research_Engine
       ↓ produces ResearchObject + EvidenceObject →
AI_Reasoning_Skills
       ↓ produces DecisionObject →
AI_Quality_Audit
       ↓ produces AuditObject (Pass) →
AI_Output_System
       ↓ produces OutputObject →
User Response
```

## Allowed Dependency Table

| Engine | May Call / Depend On |
|---|---|
| Task Orchestrator | AI_Project_Instructions only |
| Intelligence Engine | Task Orchestrator output, Module Registry, Framework Registry, Dependency Map |
| Execution Engine | Intelligence Engine output, Module Registry, Framework Registry, State Manager, Context Manager, Dependency Map |
| Research Engine | Execution Engine (scheduled by), Module Registry, Framework Registry, Knowledge Packs |
| Reasoning Skills | Research Engine output, Confidence Standard, Explainability Standard, Skill Packs |
| Quality Audit | Reasoning Skills output, Confidence Standard, Explainability Standard, Constitution |
| Output System | Quality Audit output (pass only), Reasoning Skills output, Confidence Standard, Explainability Standard |

## Forbidden Dependencies — Never Permitted

| Forbidden Dependency | Reason |
|---|---|
| Output System → Research Engine | Output never re-triggers research; audit must complete first |
| Output System → Intelligence Engine | Output never re-plans; planning must complete upstream |
| Output System → Constitution | Output never interprets constitutional rules directly |
| Research Engine → Output System | Research never formats output; flows only forward |
| Research Engine → Reasoning Skills | Research produces evidence only; reasoning is downstream |
| Research Engine → Quality Audit | Research never audits itself |
| Reasoning Skills → Research Engine | Reasoning never re-triggers research; research must be complete |
| Reasoning Skills → Task Orchestrator | Reasoning never reinterprets the task |
| Quality Audit → Research Engine | Audit never re-collects evidence |
| Quality Audit → Intelligence Engine | Audit never re-plans |
| Any Engine → Constitution (for modification) | No engine modifies the constitution at runtime |
| Any Engine → Architecture Overview (for modification) | No engine modifies the architecture at runtime |
| Any Registry → Any Engine | Registries supply metadata only; they never invoke engines |
| Knowledge Pack → Core Engine | Knowledge Packs are consumed; they never call engines |
| Skill Pack → Core Engine | Skill Packs are executed; they never call core engines |

## Registry Dependency Rules

Registries operate as read-only metadata suppliers. Registry modifications are configuration events, not runtime events — they happen through deliberate version-controlled updates, not through engine execution.

## Circular Dependency Rule

No engine may directly or indirectly depend on itself. Specifically: Research Engine may not call a component that calls Research Engine. Reasoning Engine may not call a component that calls Reasoning Engine. Quality Audit may not call a component that calls Quality Audit. Output System may not call a component that calls Output System. If circular dependency is detected → execution halts → defect is logged → human review required.

## Dependency Direction Principle

> Information flows forward through the pipeline. Feedback flows back through objects, not through direct engine calls. An engine that needs a previous engine's result must receive it via a validated object — never by calling that engine again.

---

# 13B. Synchronization Rules

## Purpose

Synchronization rules define the authority hierarchy across all system documents, the precedence order when conflicts arise, and the rules that govern how documents stay consistent as the system evolves.

## Document Authority Hierarchy

```
RANK 1:  AI_Project_Instructions_v_0.0.md        ← Constitutional supreme authority
           (Mission, Principles, Ethics, CIO Authority Rules)

RANK 2:  AI_Architecture_Overview_v_0.0.md      ← Technical structural authority
           (Layers, Engines, Contracts, Dependencies, Failure, Decision Authority)

RANK 3:  AI_Object_Schemas_v_0.0.md       ← Object schema authority
           (All shared object definitions — TaskObject, ResearchObject, etc.)

RANK 4:  AI_Confidence_Standard_v_0.0.md        ← Confidence vocabulary authority
         AI_Explainability_Standard_v_0.0.md     ← Explainability rules authority

RANK 5:  Core Engine Specifications        ← Engine-level operational authority
           (Task Orchestrator, Execution Engine, Intelligence Engine,
            Research Engine, Reasoning Skills, Quality Audit, Output System)

RANK 6:  AI_Module_Registry_v_0.0.md            ← Module discovery authority
         AI_Framework_Registry_v_0.0.md          ← Framework discovery authority
         AI_Dependency_Map_v_0.0.md              ← Cross-component dependency authority

RANK 7:  Knowledge Packs                  ← Domain knowledge authority
         Skill Packs                       ← Analytical methodology authority

RANK 8:  Modules and Frameworks           ← Implementation detail authority

RANK 9:  Runtime Output                   ← No governing authority over other documents
```

## Conflict Resolution Rule

> When two documents state conflicting rules, the higher-ranked document wins. The lower-ranked document is treated as containing an error and must be corrected — the higher-ranked document is never revised to match the lower one. Silent conflict is a defect, not a nuance to reconcile during runtime. Flag and escalate — never resolve silently.

## Specific Synchronization Rules

**Rule S-01 — Constitution Supremacy.** AI_Project_Instructions_v_0.0.md is supreme on all constitutional matters: principles, ethics, CIO authority, mission, and what outputs are permitted. No other document — including this Architecture Overview — may override it.

**Rule S-02 — Architecture Technical Authority.** AI_Architecture_Overview_v_0.0.md is supreme on technical structural matters: engine contracts, dependency rules, failure routing, and decision authority. When the Architecture Blueprint's technical description conflicts with a lower engine spec, the engine spec is corrected.

**Rule S-03 — Object Schema Authority.** Object field definitions, names, required fields, and validation rules are owned exclusively by AI_Object_Schemas_v_0.0.md. No engine specification may define or redefine object schemas — only reference them.

**Rule S-04 — Confidence Vocabulary Lock.** Confidence level labels, thresholds, and output vocabulary are owned exclusively by AI_Confidence_Standard_v_0.0.md. All engines, when producing or referencing confidence, use this vocabulary only.

**Rule S-05 — Registry Non-Duplication.** Module Registry and Framework Registry are the single source of truth for what capabilities exist. No core engine document may list specific module names, skill pack names, or knowledge pack names as hard-coded content. Discovery always happens through registries at runtime.

**Rule S-06 — Engine Specification Scope Lock.** Each engine specification owns only its own responsibilities. No engine specification may describe the internal logic of another engine. Cross-engine references are limited to: "this engine receives X from / produces Y for [engine name]."

**Rule S-07 — Knowledge and Skill Pack Independence.** Knowledge Packs and Skill Packs are domain-specific extensions. They may override a general default in their domain (per AI_Project_Instructions_v_0.0.md Section 3, Rule 3 — specificity wins). They may never override constitutional principles, object schemas, confidence standards, or engine contracts.

**Rule S-08 — No Silent Restating.** No document may restate content owned by another document. If a fact must be referenced, it is cited by document name — never copied verbatim. Duplication creates drift. Drift creates inconsistency.

**Rule S-09 — Frozen Core Amendment Protocol.** Changing any frozen core document's actual logic requires: (1) an explicit deliberate revision request, (2) a version bump in that document, (3) an update to the Manifest in AI_Project_Instructions_v_0.0.md, (4) a changelog entry in the amended document. Incidental edits during pack development are not permitted.

**Rule S-10 — Single Pipeline Source of Truth.** The processing pipeline sequence is defined exclusively in AI_Pipeline_Specification_v_0.0.md. All engine and architecture documents reference this file for sequence; none redeclare it. Any apparent pipeline diagram elsewhere is illustrative only and defers to this document on conflict.

**Rule S-11 — Naming Alias Rule.** Where an object has both a formal schema name (e.g., QualityAuditObject) and a commonly used short form in engine prose (e.g., AuditObject), the short form is a recognized alias, not a separate object. AI_Data_Object_Standard is the single source of truth for the formal name.

## Inter-Registry Synchronization

Registries do not own each other. They reference each other through declared metadata.

```
Knowledge Registry
    ↕ (referenced by)
Skill Registry
    ↕ (referenced by)
Framework Registry
    ↕ (referenced by)
Module Registry
```

A Skill Pack may reference a Knowledge Pack it depends on. A Framework may reference a Module it requires. No registry modifies another registry at runtime. Registry relationships are declared in AI_Dependency_Map_v_0.0.md.

---

# 13C. Failure & Recovery Architecture

## Purpose

The AI Operating System must behave predictably when components fail, evidence is incomplete, confidence falls below acceptable thresholds, or internal conflicts cannot be resolved. This section defines the system-wide failure handling architecture: what triggers a failure, who owns recovery, what escalation paths exist, and how the system degrades gracefully rather than halting silently.

## Failure Classification

| Level | Label | Definition | Recovery Owner |
|---|---|---|---|
| F1 | Recoverable | Failure can be resolved by retry or alternative strategy within the same engine | Engine itself |
| F2 | Degraded | Failure reduces confidence or completeness but output remains valid with disclosure | Quality Audit endorses with flag |
| F3 | Escalated | Failure cannot be resolved internally; requires upstream engine or human review signal | Quality Audit → User notification |
| F4 | Blocking | Failure represents a constitutional violation; output is unconditionally suppressed | Constitution authority; no output permitted |

## Engine-Level Failure Behavior

**Task Orchestrator Failure** — Trigger: User intent cannot be interpreted with sufficient certainty.
```
User Request → Interpretation attempt → [Failure: ambiguous intent]
→ Retry with alternate classification → [Still ambiguous]
→ Return ClarificationRequest to user [Never pass ambiguous TaskObject downstream]
→ Await user clarification → Reprocess with clarified input
```
Severity: F1 → F3 if clarification not received. Never: Produce a TaskObject with unresolved ambiguity.

**Intelligence Engine Failure** — Trigger: Registry unavailable; no suitable modules found; planning cannot produce a valid ResearchPlanObject.
```
TaskObject received → Planning attempt → [Failure: module not available]
→ Retry with alternative module selection → [Failure: no modules available]
→ Produce reduced-scope ResearchPlanObject [Flag: LIMITED_SCOPE]
→ Confidence reduction applied → Downstream engines notified via flags
```
Severity: F1 → F2. Never: Produce empty ResearchPlanObject or silently skip planning.

**Execution Engine Failure** — Trigger: Runtime scheduling error; dependency resolution failure; state corruption; context limit exceeded.
```
Execution attempt → [Failure: dependency unresolvable]
→ Log failure state to AI_State_Manager → Retry with simplified execution plan
→ [Failure: still unresolvable] → Flag EXECUTION_DEGRADED
→ Reduce context scope via AI_Context_Manager → Continue with available components
→ [If unresolvable after retry] → Escalate to Quality Audit as F3 failure
→ Produce AuditObject with EXECUTION_FAILURE flag
→ Output System produces degradation notice to user
```
Severity: F1 → F2 → F3. Never: Silently skip a scheduled component; never bypass required gates.

**Research Engine Failure** — Trigger: Source unavailable; evidence insufficient; research completeness gate not met.
```
Research plan received → Evidence collection attempt → [Failure: primary source unavailable]
→ Retry with alternative source → [Failure: alternative also unavailable]
→ Reduce evidence scope [flag SOURCE_UNAVAILABLE] → Continue with available evidence
→ [Completeness gate check] → Pass with reduced scope [flag INCOMPLETE_RESEARCH]
                              → Fail: below minimum threshold → F3 escalation
→ ResearchObject produced with explicit completeness flags
```
Severity: F1 → F2 → F3. Never: Fabricate evidence; never produce a ResearchObject without source attribution.

**Reasoning Skills Failure** — Trigger: Conflicting evidence that cannot be reconciled; insufficient evidence; reasoning loop detected.
```
ResearchObject + EvidenceObject received → Reasoning attempt → [Failure: conflicting evidence]
→ Do NOT suppress conflict → State conflict explicitly in DecisionObject
→ Produce scenario-based output (Scenario A / Scenario B)
→ Set confidence per AI_Confidence_Standard
→ [Failure: evidence too thin] → Produce INSUFFICIENT_EVIDENCE DecisionObject
→ Quality Audit receives with appropriate flag
```
Severity: F2 → F3. Never: Suppress conflicting evidence; never manufacture a conclusion from insufficient data.

**Quality Audit Failure** — Trigger: DecisionObject fails mandatory audit gate.
```
DecisionObject received → Audit gates applied → [Gate fails]
→ AuditObject produced: AUDIT_FAIL status + specific deficiency
→ Returned to responsible engine with deficiency report
→ [Correction successful] → re-audit
→ [Correction not possible] → F3 or F4 escalation
→ [F4: constitutional violation] → Output unconditionally suppressed
→ User receives: "This analysis cannot be completed as specified."
```
Severity: F3 → F4. Never: Pass a failed DecisionObject to Output System; never suppress deficiency information.

**Output System Failure** — Trigger: AuditObject has FAIL status; output format cannot be produced; mandatory disclaimer missing.
```
AuditObject received → [Status: FAIL] → Output System halts immediately
→ Return AuditRejectionNotice to user
→ [Status: PASS but low confidence] → Add UNCERTAINTY_DISCLOSURE section
→ [Format error] → Fallback to plain-text format
→ Mandatory SEBI disclaimer always included regardless of format
```
Severity: F3 → F4. Never: Produce output from a failed audit; never omit the mandatory SEBI disclaimer.

## System-Wide Failure Governance Rules

| Rule | Requirement |
|---|---|
| FR-01 | Every failure must be logged in AI_State_Manager with timestamp and engine ID |
| FR-02 | Confidence must be reduced whenever research scope, evidence quality, or reasoning completeness is degraded |
| FR-03 | Degraded outputs must explicitly disclose the nature and scope of degradation to the user |
| FR-04 | Constitutional violations (F4) unconditionally suppress output — no override permitted |
| FR-05 | No engine may silently absorb a failure and produce output as if the failure did not occur |
| FR-06 | SEBI disclaimer appears on every output, including degraded and partial outputs |
| FR-07 | Circular failure (engine A fails → engine B fails → engine A) triggers F3 escalation immediately |
| FR-08 | Human review signal is issued for any F3 failure that cannot be resolved by the system |

## Failure Recovery Priority

```
1. Retry within engine (F1)
2. Alternative strategy within engine (F1)
3. Reduced scope with disclosed confidence reduction (F2)
4. Upstream escalation with deficiency flag (F3)
5. User notification with available partial output (F3)
6. Full output suppression with explanation (F4)
```

> Silence is never a valid failure response. Every failure produces a traceable outcome.

---

# 13D. Decision Authority Matrix

## Core Decision Authority Table

| Decision | Authority Owner | Governing Document | Override Permitted By |
|---|---|---|---|
| Constitutional compliance | AI_Project_Instructions_v_0.0.md | AI_Project_Instructions_v_0.0.md | No one — absolute |
| System architecture structure | AI_Architecture_Overview_v_0.0.md | AI_Architecture_Overview_v_0.0.md | Only explicit amendment |
| Task interpretation and classification | AI Task Orchestrator | AI_Task_Orchestrator_v_0.0.md | None at runtime |
| Depth tier selection | AI Task Orchestrator | AI_Task_Orchestrator_v_0.0.md | None at runtime |
| Research mode and strategy planning | AI Intelligence Engine | AI_Intelligence_Engine_v_0.0.md | None at runtime |
| Module selection | AI Intelligence Engine (via Module Registry) | AI_Module_Registry_v_0.0.md | None at runtime |
| Framework selection | AI Intelligence Engine (via Framework Registry) | AI_Framework_Registry_v_0.0.md | None at runtime |
| Runtime scheduling and sequencing | AI Execution Engine | AI_Execution_Engine_v_0.0.md | None at runtime |
| Context loading decisions | AI_Context_Manager | AI_Context_Manager_v_0_0.md | AI Execution Engine |
| State tracking and recovery | AI_State_Manager | AI_State_Manager_v_0.0.md | AI Execution Engine |
| Research completeness determination | AI Research Engine | AI_Research_Engine_v_0_0.md | None at runtime |
| Evidence validity | AI Research Engine | AI_Research_Engine_v_0_0.md | None at runtime |
| Source credibility classification | AI Research Engine | AI_Research_Engine_v_0_0.md | None at runtime |
| Logical conclusion formation | AI Reasoning Skills | AI_Reasoning_Skills_v_0_0.md | None at runtime |
| Confidence level assignment | AI_Confidence_Standard_v_0.0.md | AI_Confidence_Standard_v_0.0.md | No engine at runtime |
| Bias detection and challenge | AI Reasoning Skills + Quality Audit | AI_Reasoning_Skills_v_0_0.md + AI_Quality_Audit_v_0.0.md | None at runtime |
| Reasoning conflict resolution | AI Reasoning Skills | AI_Reasoning_Skills_v_0_0.md | None — conflict must be disclosed |
| Final audit verdict (pass/fail) | AI Quality Audit | AI_Quality_Audit_v_0.0.md | No downstream engine |
| Audit gate severity determination | AI Quality Audit | AI_Quality_Audit_v_0.0.md | None |
| Output format and template | AI Output System | AI_Output_System_v_0.0.md | TaskObject format request |
| SEBI disclaimer inclusion | AI Output System | AI_Project_Instructions_v_0.0.md (Ethical Standards §8) | No one — mandatory always |
| Output approval (allow/suppress) | AI Quality Audit audit verdict | AI_Quality_Audit_v_0.0.md | F4 failures: Constitution |
| CIO judgment override | CIO Authority Rules | AI_Project_Instructions_v_0.0.md (Section 6) | Constitution only |
| Module registry modification | Module Registry governance | AI_Module_Registry_v_0.0.md | Explicit deliberate revision only |
| Framework registry modification | Framework Registry governance | AI_Framework_Registry_v_0.0.md | Explicit deliberate revision only |
| Knowledge Pack loading | AI Execution Engine (via Module Registry) | AI_Module_Registry_v_0.0.md | None at runtime |
| Skill Pack activation | AI Execution Engine (via Module Registry) | AI_Module_Registry_v_0.0.md | None at runtime |
| Confidence vocabulary enforcement | AI_Confidence_Standard_v_0.0.md | AI_Confidence_Standard_v_0.0.md | No engine |
| Explainability format enforcement | AI_Explainability_Standard_v_0.0.md | AI_Explainability_Standard_v_0.0.md | No engine |
| Object schema definition | AI_Object_Schemas_v_0.0.md | AI_Object_Schemas_v_0.0.md | Only explicit schema revision |
| Architecture amendment approval | AI_Project_Instructions_v_0.0.md (Frozen Core Amendment Protocol) | Both documents | Only explicit revision process |

## CIO Authority Special Cases

| CIO Rule | Effect on Decision Authority |
|---|---|
| Forensic Accounting flag blocks Buy | Quality Audit's FORENSIC_FLAG overrides any positive composite score; no Buy output permitted |
| Governance score caps position size | Reasoning Engine's governance rating caps Output System's position size guidance |
| Composite score alone insufficient for Buy | Valuation margin-of-safety check (owned by Research Engine) must independently pass |
| Macro adverse conditions → conviction discount | Research Engine applies system-wide discount; Reasoning Engine propagates |
| Cooling period on emotion-driven market events | Task Orchestrator may flag; Quality Audit enforces output suppression for 24 hours |
| ASM/GSM surveillance → mandatory governance review | Research Engine triggers governance pack; Quality Audit enforces gate |

## Capability Ownership Matrix

| Capability | Owner Engine | Extension Path |
|---|---|---|
| Intent understanding | Task Orchestrator | None — core engine function |
| Task classification | Task Orchestrator | None — core engine function |
| Research planning | Intelligence Engine | Module Registry (new planning strategies) |
| Module and framework selection | Intelligence Engine | Module Registry, Framework Registry |
| Runtime orchestration | Execution Engine | None — kernel is frozen |
| Dependency resolution | Execution Engine + Dependency Map | Dependency Map updates |
| Context optimization | Context Manager | Context Manager specification |
| State recovery | State Manager | State Manager specification |
| Evidence collection | Research Engine | Knowledge Packs (domain extension) |
| Source validation | Research Engine | Knowledge Packs (source authority lists) |
| Hypothesis testing | Reasoning Skills | Skill Packs (domain-specific hypotheses) |
| Causal analysis | Reasoning Skills | Skill Packs |
| Scenario analysis | Reasoning Skills | Skill Packs |
| Probabilistic reasoning | Reasoning Skills | Skill Packs |
| Conviction formation | Reasoning Skills | Skill Packs |
| Forensic accounting detection | Reasoning Skills + Quality Audit | Forensic Accounting Skill Pack |
| Bias gate enforcement | Quality Audit | Quality Audit specification |
| Constitutional compliance check | Quality Audit + Constitution | Constitution (supreme) |
| Output formatting | Output System | Module Registry (new format templates) |
| Confidence calibration | All engines (consumes standard) | AI_Confidence_Standard_v_0.0.md |
| Explainability tagging | All engines (consumes standard) | AI_Explainability_Standard_v_0.0.md |

## Decision Authority Enforcement Rule

> No engine may make a decision owned by another engine or document. When an engine encounters a decision outside its authority, it must route that decision to the correct owner via the standard object flow — never approximate, assume, or substitute its own judgment for the owner's rule.

---

# PART 3 — GOVERNANCE

---

# 14. Version Compatibility

Every core object schema is owned and versioned by `AI_Object_Schemas_v_0.0.md`. An engine's declared "Version Compatibility" (Section 8A) always points to that document, not to a locally redefined schema. Breaking schema changes require a version bump in the Data Object Standard and a corresponding compatibility note in every consuming engine's Document Information block.

---

# 15. Future Expansion

New capabilities are added through the registry layer — Module Registry, Framework Registry, Knowledge Packs, Skill Packs — never by editing a core engine's kernel logic (per Design Principle: Extensibility, Section 4). New engines, if ever required, must be onboarded with a full Section 8A-style contract before being added to Section 8 and the Dependency Hierarchy (Section 13).

---

# 16. Frozen Core Documents

The following are frozen (kernel logic only — extensible at the registry/template layer per each document's own governance section):

- AI_Project_Instructions_v_0.0.md (Constitution)
- AI_Architecture_Overview_v_0.0.md (this document)
- AI_Pipeline_Specification_v_0.0.md
- AI_Object_Schemas_v_0.0.md
- AI_Confidence_Standard_v_0.0.md
- AI_Explainability_Standard_v_0.0.md
- Each core engine's kernel failure-behavior and contract logic (Section 8A)

---

# 17. Final Specification

The AI_Architecture_Overview is the single authoritative structural blueprint for the IERL AI Operating System. It defines seven core engines, each with a formal contract; a single authoritative pipeline sequence; a complete dependency and forbidden-dependency graph; a document authority hierarchy that resolves any cross-document conflict deterministically; a four-tier failure classification with engine-specific recovery behavior; and a decision authority matrix that assigns exactly one owner to every architectural decision in the system. Every other document in the system operates within the boundaries this document defines and defers to it on any structural question.

---

# Document Information

**Document:** AI_Architecture_Overview_v_0.0.md
**Version:** v_0.0 (Final)
**Status:** Production Ready
**Supersedes:** v_0.0 (incomplete — Sections 8–17 unwritten; Tasks 01–06 misordered)
**Resolves:** Completes Phase 1 of the IERL remediation plan — all six Task additions correctly placed, missing sections reconstructed

# END OF DOCUMENT

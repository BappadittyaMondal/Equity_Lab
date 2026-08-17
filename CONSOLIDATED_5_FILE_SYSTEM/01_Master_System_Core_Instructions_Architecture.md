# 01_Master_System_Core_Instructions_Architecture

> **IERL AI Equity OS — curated upload artifact**  
> Project Version: `0.4.0` · Bundle Version: `2.0` · Git Commit: `33f3193`  
> Generated At: `2026-08-17T07:00:33.834392+00:00` · Source Hash: `311073031dcedc44` · Compiler: `consolidate_project.py` v2.0

## Operating contract

This is a generated, read-only working volume. The separately maintained source documents are authoritative; regenerate this file after changing a source. The wrapper provides navigation and execution discipline, but does not replace a source rule. Embedded source payloads are preserved verbatim between the `BEGIN` and `END` markers.

1. Route the request to the narrowest relevant upload file, then use the named embedded document(s); do not treat an unrelated volume as evidence.
2. Execute applicable skill steps in order. If a required input, timeframe, benchmark, or source is absent, state the gap and the effect on confidence; never silently invent it.
3. Separate **reported facts**, **calculations**, **assumptions**, and **inference**. Date all market-sensitive claims and identify the data source or user-provided input.
4. Surface disconfirming evidence, governance/forensic risk, liquidity risk, valuation risk, and material uncertainty before a conclusion. A positive screen is not investment advice or a guarantee.
5. When source documents conflict, prefer the more specific, later-versioned requirement; if unresolved, disclose the conflict and use the more conservative interpretation. Never override platform safety requirements.

## Fast task routing

| Upload file | Primary use | Sources |
|---|---|---:|
| `01_Master_System_Core_Instructions_Architecture.md` | 01 System Core Instructions Architecture | 8 |
| `02_Master_Engine_Contracts_Schemas_Registries.md` | 02 Engine Contracts Schemas Registries | 12 |
| `03_Master_Skill_Library.md` | 03 Skill Library | 18 |
| `04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md` | 04 Knowledge Base Vol 1 Fundamentals Valuation Governance | 24 |
| `05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md` | 05 Knowledge Base Vol 2 Sectors Frameworks Screening | 27 |

**Default research sequence:** define decision and horizon → gather dated evidence → run the relevant workflow/analytical skill → apply risk and forensic checks → calculate/compare → present conclusion, counter-case, and confidence. For a company decision, consult core instructions, the applicable skill, fundamentals/valuation, sector context, and risk/forensics rather than relying on one metric.

## Scope and privacy boundary

This bundle contains static methodology and knowledge only. It contains no credentials and cannot by itself read local files, call APIs, fetch live market data, trade, or access private accounts. The following local integration/private files are intentionally excluded: `.env.example`, `API_KEYS_CONFIG.env`, `API_PROVIDERS_AND_FREE_TIERS_GUIDE.md`, `test_apis.py`.

## Embedded source manifest

The SHA-256 values cover the exact UTF-8 source payload, not this wrapper. Use the manifest to audit a rebuild.

| # | Source document | UTF-8 bytes | SHA-256 |
|---:|---|---:|---|
| 1 | `AI_Project_Instructions_v_0_0.md` | 5,681 | `0f7bc06c1404a61102226a5837d0f8452e83046c99efd45a503cd5e02cf577c9` |
| 2 | `AI_Architecture_Overview_v_0_0.md` | 44,635 | `723f1b6f9145f0da08137a30de2624b7f04c6c347347f2cae159bf21252495a2` |
| 3 | `AI_Pipeline_Specification_v_0_0.md` | 13,093 | `3cd2c5abf48b617bce1402de8bec156a41ebab116b281449770f1d8660e473dc` |
| 4 | `AI_Task_Orchestrator_v_0_0.md` | 28,810 | `bd87c94df4e323367a224d8f259f05336f10ae19533673beff6cd7d607e4f7e0` |
| 5 | `AI_State_Manager_v_0_0.md` | 10,133 | `90bbff840a8b2db879e97ae6bc3775f351977d0740ba51ea21e88c79f97a9015` |
| 6 | `AI_Context_Manager_v_0_0.md` | 11,311 | `1aca7a69c529a8a3872de6b4bdf02a9e38c599b7dbaae65e473dab2cdc5002fb` |
| 7 | `AI_Confidence_Standard_v_0_0.md` | 13,432 | `3a85bef2f6e98ad0eec61c46d3cbb59ab7d0ea9697aa80c4ffb024d897dac38e` |
| 8 | `AI_Explainability_Standard_v_0_0.md` | 5,933 | `dc945149d1491c05cafbd8fda6eb56c41e50cb51862fb6baf408a84effc57a7e` |

---

<!-- BEGIN SYSTEM FILE 1: AI_Project_Instructions_v_0_0.md | SHA256: 0f7bc06c1404a61102226a5837d0f8452e83046c99efd45a503cd5e02cf577c9 -->
## Embedded source 1: AI Project Instructions

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Project Instructions  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# IERL AI Equity OS — Project Instructions and Decision Constitution

**Status:** Canonical · **Scope:** All workflows, engines, knowledge domains, and generated upload bundles.  
**Purpose:** Define how the Equity OS selects a workflow, handles evidence, resolves conflicts, and reports a decision. This document replaces a misplaced duplicate of the Comparison Engine skill; comparison logic now lives only in `AI_Comparison_Engine_Skill.md`.

## 1. Operating objective

Produce useful, auditable investment research—not unsupported certainty. A response must identify the decision being considered, the horizon, the available evidence, material uncertainty, downside risks, and the conditions that would change the conclusion.

## 2. Authority hierarchy

Apply requirements in this order when they conflict:

1. Platform safety requirements and applicable law.
2. Verifiable current primary evidence: exchange filings, company filings, audited statements, regulator notices, and official market data.
3. Hard integrity and risk gates: governance/forensic issues, surveillance/liquidity constraints, and explicit portfolio risk limits.
4. The most specific applicable workflow skill and its mandatory gates.
5. Engine contracts, schemas, confidence, explainability, and audit standards.
6. Knowledge domains, heuristics, historic examples, and secondary commentary.

When a conflict remains unresolved, name it, use the more conservative interpretation, and lower confidence. Static knowledge never overrides dated evidence.

## 3. Task routing

| Request type | Primary operating source | Required supporting sources |
|---|---|---|
| Company research, comparison, valuation | Relevant analytical skill | Financial statements, ratios, valuation, governance, forensics, relevant sector |
| Swing/positional idea | Swing/technical workflow | Market regime, liquidity, risk rules, fundamental floor, sector context |
| Portfolio construction or review | Portfolio skill | Risk management, portfolio rules, forensic/governance review |
| Sector or thematic question | Relevant sector/domain | Current primary evidence, macro/industry context, risk analysis |
| Screening request | Screening workflow | Field glossary, risk/forensic gates, confirmation skill |
| Current event, price, regulation, or result | Research engine | Current dated primary source; static files are context only |

Ask for the company, horizon, benchmark, data date, and risk tolerance when they materially affect the answer. If they are unavailable, declare the assumption rather than silently choosing one.

## 4. Evidence protocol

For every material claim, keep these four categories distinct:

- **Fact:** a dated, attributable observation or user-provided input.
- **Calculation:** formula, inputs, units, and period stated.
- **Assumption:** an input not established by evidence.
- **Inference:** an interpretation drawn from facts and assumptions.

Use primary sources where available. State data date/as-of period, currency/unit, and whether a value is reported, adjusted, annualised, or estimated. Never fabricate a price, financial figure, filing, source, or access to live data. Missing evidence is a finding, not a reason to fill a gap with narrative.

## 5. Mandatory decision gates

Before a positive investment conclusion, apply the gates relevant to the task:

1. Identity and data-date check.
2. Governance and forensic review.
3. Financial quality, balance-sheet, and cash-flow review.
4. Sector-appropriate business and valuation comparison.
5. Liquidity, event, concentration, and downside-risk review.
6. For technical/trading outputs: market regime, timeframe, entry invalidation, and risk/reward check.

A passed screen is not proof of investment merit. A hard red flag, insufficient current evidence, or an unresolved contradiction caps conviction and may require a no-decision outcome.

## 6. Confidence and output standard

Use the vocabulary and scoring rules in `AI_Confidence_Standard_v_0_0.md`. Confidence measures evidence/process reliability, not the probability that a prediction will be correct. Every substantive conclusion should include:

1. Bottom line and decision horizon.
2. Evidence used, with dates and gaps.
3. Key drivers and counter-case.
4. Risks, red flags, and invalidation conditions.
5. Confidence level and why it is limited or supported.
6. Next verification step when evidence is incomplete or time-sensitive.

Do not turn a relative comparison, screen, or model output into personalised financial advice. Do not imply execution, trading, account access, API access, or live-market access unless such capability and its data are explicitly supplied.

## 7. Source maintenance rules

The 89 sources in `Not_Required_Upload/Canonical_Source_84` are the editable source of truth. The 5- and 9-file folders are generated upload artifacts. Update a canonical source, run the compiler, then verify source manifests before uploading. Credentials and local integration files remain outside both source and upload bundles.
<!-- END SYSTEM FILE 1: AI_Project_Instructions_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 2: AI_Architecture_Overview_v_0_0.md | SHA256: 723f1b6f9145f0da08137a30de2624b7f04c6c347347f2cae159bf21252495a2 -->
## Embedded source 2: AI Architecture Overview

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
<!-- END SYSTEM FILE 2: AI_Architecture_Overview_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 3: AI_Pipeline_Specification_v_0_0.md | SHA256: 3cd2c5abf48b617bce1402de8bec156a41ebab116b281449770f1d8660e473dc -->
## Embedded source 3: AI Pipeline Specification

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
<!-- END SYSTEM FILE 3: AI_Pipeline_Specification_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 4: AI_Task_Orchestrator_v_0_0.md | SHA256: bd87c94df4e323367a224d8f259f05336f10ae19533673beff6cd7d607e4f7e0 -->
## Embedded source 4: AI Task Orchestrator

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Task Orchestrator  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Task_Orchestrator_v_0.0

**Version:** v_0.0  
**Status:** Production Ready  
**Category:** Core Engine  
**Priority:** Critical  
**Role:** Request Interpretation Engine  
**Supersedes:** AI_Task_Orchestrator_v_0.0

---

# Part 1 — Task Architecture

## Table of Contents

1. Purpose  
2. Vision  
3. Architectural Position  
4. Design Philosophy  
5. Responsibilities  
6. Non-Responsibilities  
7. Design Principles  
8. Task Lifecycle  
9. Task Processing Pipeline  
10. Universal Interpretation Rules  
11. Inputs & Outputs  
12. Engine Interfaces  
13. Governance  
14. Success Criteria  
15. Final Specification  

---

## 1. Purpose

The **AI Task Orchestrator** is the official entry point of the AI Operating System.

Its responsibility is to convert unstructured natural language into a standardized, validated, machine-readable **TaskObject** that downstream engines can process safely and consistently.

It understands **what the user wants** and records that intent in structured form. It does **not** decide how the task will be executed, researched, reasoned about, audited, or presented.

The Task Orchestrator exists to establish a common interpretation layer that every downstream engine can trust.

---

## 2. Vision

Every user request should be interpreted consistently, regardless of:

- AI model
- conversation length
- request complexity
- domain
- execution strategy
- deployment environment

The Task Orchestrator provides a single authoritative interpretation that becomes the foundation for all subsequent processing.

Its purpose is to separate **language understanding** from **execution planning**, so the system can scale without ambiguity or architectural drift.

---

## 3. Architectural Position

The Task Orchestrator sits immediately after the constitutional layer and
immediately before intelligence planning. Authoritative pipeline order is
defined in AI_Pipeline_Specification_v_0.0.md.

```text
User Request
    ↓
AI_Project_Instructions
    ↓
AI_Task_Orchestrator
    ↓
TaskObject
    ↓
AI_Intelligence_Engine
    ↓
ResearchPlanObject
    ↓
AI_Execution_Engine
    ↓
AI_Research_Engine
    ↓
AI_Reasoning_Skills
    ↓
AI_Quality_Audit
    ↓
AI_Output_System
```

Its responsibility ends immediately after the validated TaskObject has been created and transferred.

---

## 4. Design Philosophy

The Task Orchestrator follows these architectural principles.

### Principle 1 — Understand Before Acting
Interpret the request before classifying it.

### Principle 2 — Single Source of Truth
One request produces one authoritative interpretation.

### Principle 3 — Execution Independence
Never determine execution strategy.

### Principle 4 — Intelligence Independence
Never select frameworks, skills, knowledge packs, or modules.

### Principle 5 — Domain Neutrality
Describe the task rather than solving it.

### Principle 6 — Deterministic Interpretation
The same request should produce the same TaskObject, given the same conversation context.

### Principle 7 — Explainability
Every interpretation must be explainable and traceable.

### Principle 8 — Minimal Responsibility
Only interpret requests. Delegate everything else.

### Principle 9 — Immutable Task Definition
Once validated, a TaskObject is never edited in place.

### Principle 10 — Future Scalability
The architecture must support multi-agent systems, multiple AI models, persistent memory, API integrations, distributed execution, and enterprise workflows without redesign.

---

## 5. Responsibilities

The Task Orchestrator shall:

- interpret natural language
- detect user intent
- estimate intent confidence
- classify task type
- assess task complexity
- extract user objectives
- decompose complex requests
- detect conversation continuity
- recognize named entities
- estimate research depth
- detect urgency
- detect output preference
- detect constraints
- assess information sufficiency
- classify task risk
- generate dependency hints
- produce ParentTaskObject and ChildTaskObjects when required
- validate all task metadata
- transfer the TaskObject to the Execution Engine

---

## 6. Non-Responsibilities

The Task Orchestrator shall never:

- create execution plans
- select modules
- select frameworks
- select reasoning methodologies
- estimate execution cost
- estimate runtime
- allocate context
- manage execution state
- perform reasoning
- perform research
- evaluate evidence
- produce recommendations
- perform quality audits
- generate user reports

These responsibilities belong exclusively to downstream engines.

---

## 7. Design Principles

Every interpretation must be:

- accurate
- deterministic
- consistent
- explainable
- traceable
- version-controlled
- immutable
- registry-compatible
- AI-model independent
- scalable

When uncertainty exists, the engine records uncertainty rather than inventing information.

---

## 8. Task Lifecycle

```text
Receive Request
    ↓
Interpret Request
    ↓
Intent Detection
    ↓
Complexity Assessment
    ↓
Task Classification
    ↓
Task Decomposition
    ↓
Conversation Analysis
    ↓
Entity Recognition
    ↓
Constraint Detection
    ↓
Information Sufficiency Assessment
    ↓
Validation
    ↓
TaskObject Generation
    ↓
Transfer to Execution Engine
```

The lifecycle terminates immediately after TaskObject transfer.

---

## 9. Task Processing Pipeline

The Task Orchestrator performs interpretation in this order:

1. Intent  
2. Complexity  
3. Task Type  
4. User Objective  
5. Query Decomposition  
6. Multi-Task Decomposition  
7. Conversation Analysis  
8. Entity Recognition  
9. Research Depth  
10. Urgency  
11. Output Preference  
12. Constraints  
13. Information Sufficiency  
14. Risk Classification  
15. Dependency Hints  
16. Validation  
17. TaskObject generation  

Execution planning never occurs inside this pipeline.

---

## 10. Universal Interpretation Rules

The Task Orchestrator shall always:

- understand before classifying
- classify before validating
- validate before generating objects
- generate immutable TaskObjects
- preserve provenance
- preserve metadata
- remain execution-independent
- remain reasoning-independent
- remain research-independent

The Task Orchestrator shall never assume missing facts.

If information is incomplete, it records the gap and routes the request to clarification policy.

---

## 11. Inputs & Outputs

### Inputs

- User Request
- Conversation Context
- Project Constitution
- Prior TaskObjects when the request is a continuation

### Outputs

- ParentTaskObject
- ChildTaskObjects
- Task Metadata
- Validation Status
- Interpretation Confidence
- Dependency Hints
- Execution Readiness

---

## 12. Engine Interfaces

Consumes:

- AI_Project_Instructions

Produces:

- TaskObject

Transfers to:

- AI_Execution_Engine

No direct communication with:

- Intelligence Engine
- Research Engine
- Reasoning Engine
- Quality Audit
- Output System

All communication occurs through standardized objects.

---

## 13. Governance

The Task Orchestrator must:

- maintain deterministic behavior
- preserve backward compatibility
- support immutable TaskObjects
- preserve complete interpretation metadata
- preserve auditability
- maintain object versioning
- support future extensions without redesign

### Clarification Decision Policy

The engine must decide whether clarification is required before TaskObject creation.

| Situation | Action |
|---|---|
| Complete information | Continue |
| Minor ambiguity | Continue and record assumptions |
| Missing important information | Ask user |
| Unsupported request | Reject gracefully |
| Unsafe request | Stop processing |

Clarification should occur before execution, never during execution.

### Failure Handling

**Validation failure**  
Missing or invalid task metadata.

Action:
- reject TaskObject
- log failure
- request clarification if recoverable

**Interpretation failure**  
Intent or objective cannot be determined.

Action:
- ask user
- never guess

**Unsupported request**  
Outside project capability.

Action:
- explain limitation
- do not fabricate output

**Unsafe request**  
Violates constitutional or safety policies.

Action:
- reject immediately
- record audit event

---

## 14. Success Criteria

A successful Task Orchestrator:

- correctly understands the request
- classifies intent accurately
- decomposes complex requests cleanly
- identifies missing information
- generates a valid TaskObject
- hands control to the Execution Engine without retaining execution state

---

## 15. Final Specification

The AI Task Orchestrator is the **request interpretation gateway** of the AI Operating System.

It converts human language into structured, validated, immutable TaskObjects while remaining completely independent of execution, reasoning, research, module selection, framework selection, auditing, and output generation.

Its sole mission is to ensure every request enters the AI Operating System with a complete, standardized, explainable, and institutionally consistent interpretation.

---

# Part 2 — Request Interpretation Engine

## Table of Contents

1. Purpose  
2. Interpretation Workflow  
3. Intent Detection  
4. Intent Confidence  
5. User Objective Extraction  
6. Complexity Classification  
7. Task Classification  
8. Research Depth Classification  
9. Query Decomposition  
10. Multi-Task Decomposition  
11. Conversation Continuation Detection  
12. Entity Recognition  
13. Output Preference Detection  
14. Constraint Detection  
15. Information Sufficiency Assessment  
16. Task Risk Classification  
17. Dependency Hints  
18. Execution Readiness  
19. Validation Rules  
20. Final Output  

---

## 1. Purpose

The Request Interpretation Engine transforms natural language into structured machine-readable intent.

Its responsibility is to understand **what the user wants**, not **how the task should be executed**.

Every downstream engine relies on this interpretation.

---

## 2. Interpretation Workflow

```text
User Request
    ↓
Intent Detection
    ↓
Intent Confidence
    ↓
User Objective
    ↓
Complexity Classification
    ↓
Task Classification
    ↓
Research Depth
    ↓
Query Decomposition
    ↓
Multi-Task Decomposition
    ↓
Conversation Analysis
    ↓
Entity Recognition
    ↓
Output Preference
    ↓
Constraint Detection
    ↓
Information Sufficiency
    ↓
Risk Classification
    ↓
Dependency Hints
    ↓
Execution Readiness
    ↓
Validation
    ↓
TaskObject
```

---

## 3. Intent Detection

Determine the primary purpose of the request.

Possible intents include:

- Research
- Analysis
- Comparison
- Screening
- Recommendation
- Portfolio Review
- Monitoring
- Valuation
- Risk Assessment
- Documentation
- Strategy
- Planning
- Education
- General Assistance

The engine may detect multiple intents, but it must identify one primary intent.

---

## 4. Intent Confidence

Every detected intent receives a confidence score.

Example:

```yaml
PrimaryIntent: Research
Confidence: 94%

AlternativeIntent: Education
Confidence: 61%

Reason: User requested institutional analysis.
```

Low confidence increases clarification probability.

---

## 5. User Objective Extraction

Identify the user's actual objective.

Examples:

- find opportunities
- learn a concept
- compare companies
- build valuation
- review portfolio
- generate report
- validate thesis
- monitor investment

Objectives remain implementation-independent.

---

## 6. Complexity Classification

Research depth and complexity are independent.

### Complexity Levels

- Simple
- Moderate
- Complex
- Multi-Stage
- Institutional

### Factors

- number of objectives
- number of entities
- cross-domain requirements
- required reasoning
- expected output

Complexity influences execution planning but does not perform it.

---

## 7. Task Classification

Identify the dominant task type.

Examples:

- Research
- Analysis
- Comparison
- Screening
- Monitoring
- Reporting
- Portfolio
- Education
- Strategy
- Documentation

One parent task may contain multiple child task types.

---

## 8. Research Depth Classification

Depth reflects analytical rigor.

### Levels

- Quick
- Standard
- Deep
- Institutional
- Expert

Depth depends upon:

- user objective
- complexity
- risk
- expected deliverable

---

## 9. Query Decomposition

Complex requests are divided into logical actions.

Example:

```text
Compare BEL and HAL,
build a DCF,
recommend one,
update portfolio.
```

becomes:

```text
Compare
↓
Valuation
↓
Recommendation
↓
Portfolio Update
```

Execution Engine receives structured actions instead of raw language.

---

## 10. Multi-Task Decomposition

One request may generate multiple TaskObjects.

Example:

```text
Parent Task
    ├── Child Task A
    ├── Child Task B
    └── Child Task C
```

Each child task includes:

```yaml
TaskID
TaskType
Priority
Dependencies
MergeStrategy
```

Merge strategies:

- Sequential Merge
- Parallel Merge
- Hierarchical Merge
- Independent Results

---

## 11. Conversation Continuation Detection

Determine request relationship.

Possible states:

- New Request
- Continuation
- Follow-up
- Refinement
- Correction
- Expansion
- Restart

Examples:

- “Continue” → Continuation
- “Compare with Tata Motors” → Refinement
- “Ignore previous analysis” → Correction

---

## 12. Entity Recognition

Extract structured entities.

Supported entities:

- Company
- Sector
- Industry
- Exchange
- Ticker
- Financial Statement
- Ratio
- Metric
- Economic Indicator
- Country
- Currency
- Benchmark
- Peer Group
- Time Period
- Regulation
- Government Policy

Entity extraction is semantic only. Validation occurs downstream.

---

## 13. Output Preference Detection

Determine preferred output format.

Supported formats:

- Executive Summary
- Narrative
- Markdown
- Table
- JSON
- Investment Memo
- Research Report
- Checklist
- Presentation Outline

If unspecified, Output System selects the default format.

---

## 14. Constraint Detection

Detect user-imposed constraints.

Examples:

```yaml
Time
Language
Token Budget
Evidence Requirement
Source Requirement
Formatting
Regulatory
Investment Horizon
Risk Preference
```

Constraints are metadata only.

---

## 15. Information Sufficiency Assessment

Evaluate whether the request contains enough information.

### Levels

- Complete
- Partial
- Insufficient

If insufficient, the Clarification Policy determines the next action.

---

## 16. Task Risk Classification

Estimate interpretation risk.

### Levels

- Low
- Medium
- High
- Critical

High-risk domains include:

- Finance
- Medical
- Legal
- Regulatory

Higher risk increases validation requirements.

---

## 17. Dependency Hints

The Task Orchestrator never selects modules.

Instead, it suggests dependency categories.

Example:

```yaml
Likely Domains:
  - Financial Analysis
  - Technical Analysis
  - Valuation
  - Portfolio

Required Capabilities:
  - Reasoning
  - Research
  - Knowledge
  - Skills
```

Execution Engine resolves actual dependencies.

---

## 18. Execution Readiness

Before TaskObject generation determine:

- Ready
- Needs Clarification
- Insufficient Information
- Unsupported
- Unsafe

Only **Ready** tasks proceed directly.

---

## 19. Validation Rules

Every interpretation must satisfy:

- Intent detected
- Objective extracted
- Complexity assigned
- Task classified
- Research depth assigned
- Entities extracted
- Constraints detected
- Information sufficiency assessed
- Execution readiness determined

Otherwise, the engine must clarify or reject according to policy.

---

## 20. Final Output

The Request Interpretation Engine produces:

```yaml
ParentTaskObject
ChildTaskObjects
PrimaryIntent
AlternativeIntents
IntentConfidence
UserObjective
Complexity
TaskType
ResearchDepth
ConversationType
Entities
OutputPreference
Constraints
InformationSufficiency
RiskClassification
DependencyHints
ExecutionReadiness
ValidationStatus
```

This becomes the official TaskObject transferred to the AI_Execution_Engine.

---

# Part 3 — TaskObject Generation & Transfer

## Table of Contents

1. Purpose  
2. TaskObject Philosophy  
3. Parent–Child Task Architecture  
4. TaskObject Structure  
5. ParentTaskObject  
6. ChildTaskObject  
7. Task Metadata  
8. Task Priority  
9. Task Constraints  
10. Dependency Hints  
11. Task Validation  
12. Clarification Decision Policy  
13. Execution Readiness  
14. Task Transfer Protocol  
15. Versioning & Immutability  
16. Final Specification  

---

## 1. Purpose

After interpreting the user's request, the Task Orchestrator converts the interpretation into standardized **TaskObjects**.

TaskObjects become the official communication contract between the Task Orchestrator and the Execution Engine.

The Execution Engine never interprets natural language. It consumes only validated TaskObjects.

---

## 2. TaskObject Philosophy

A TaskObject describes **what must be accomplished**, not **how it will be accomplished**.

It contains:

- interpretation
- objectives
- metadata
- constraints
- validation
- dependency hints

It never contains:

- execution plans
- framework selections
- module selections
- skill selections
- knowledge selections
- reasoning logic

---

## 3. Parent–Child Task Architecture

Simple requests generate one TaskObject.

Complex requests generate a ParentTaskObject with multiple ChildTaskObjects.

```text
User Request
    ↓
ParentTaskObject
    ├── Child Task A
    ├── Child Task B
    └── Child Task C
    ↓
Execution Engine
```

---

## 4. TaskObject Structure

The structure and fields of `TaskObject` are defined canonically in `AI_Object_Schemas_v_0.0.md` Section 22. The AI Task Orchestrator generates `TaskObject` instances per that canonical schema and does not define a separate or local schema.

---

## 5. ParentTaskObject

Purpose:

Represents the complete user request.

Fields:

```yaml
ParentTaskID
TaskSummary
OverallObjective
OverallPriority
ChildTaskCount
ExecutionDependency
MergeStrategy
OverallConstraints
OverallRisk
OverallComplexity
```

Responsibilities:

- maintain overall objective
- coordinate child tasks
- preserve task hierarchy
- define merge strategy

---

## 6. ChildTaskObject

Each child task represents one executable objective.

Fields:

```yaml
ChildTaskID
ParentTaskID
TaskType
Objective
Priority
Dependencies
Constraints
EstimatedComplexity
ValidationStatus
```

Child tasks remain independent until merged.

---

## 7. Task Metadata

Every TaskObject includes standard metadata.

```yaml
TaskID
SessionID
Timestamp
ConversationID
Version
SchemaVersion
Creator
Status
```

Metadata enables auditability and traceability.

---

## 8. Task Priority

Priority levels:

- Critical
- High
- Normal
- Low

Priority influences execution scheduling but does not determine execution strategy.

---

## 9. Task Constraints

Detected constraints are preserved as metadata.

Examples:

```yaml
Language
TokenBudget
EvidenceRequirement
Formatting
Deadline
TimeHorizon
Jurisdiction
RegulatoryRequirements
```

Execution Engine is responsible for enforcing them.

---

## 10. Dependency Hints

TaskObjects expose only dependency categories.

Example:

```yaml
LikelyDomains:
  - Financial Analysis
  - Technical Analysis
  - Valuation
  - Portfolio
  - Macroeconomics

Capabilities:
  - Research
  - Reasoning
  - Knowledge
  - Skills
```

The Task Orchestrator never references specific modules.

---

## 11. Task Validation

Before transfer, every TaskObject must satisfy:

- intent detected
- objective defined
- complexity assigned
- task classified
- research depth assigned
- constraints captured
- entities extracted
- information sufficiency assessed
- risk classified
- dependency hints generated
- validation completed

If validation fails, the TaskObject is rejected.

---

## 12. Clarification Decision Policy

The Task Orchestrator determines whether clarification is required before TaskObject creation.

| Condition | Action |
|---|---|
| Complete Information | Continue |
| Minor Ambiguity | Continue with assumptions noted |
| Missing Critical Information | Ask user |
| Unsupported Request | Reject gracefully |
| Unsafe Request | Stop |

Clarification occurs before execution whenever possible.

---

## 13. Execution Readiness

Every TaskObject receives one readiness status:

- Ready
- Needs Clarification
- Insufficient Information
- Unsupported
- Unsafe

Only **Ready** TaskObjects are transferred immediately.

---

## 14. Task Transfer Protocol

Validated TaskObjects are transferred to the Execution Engine.

```text
TaskObject
    ↓
Validation Check
    ↓
Transfer
    ↓
Execution Engine
    ↓
Acknowledgement
    ↓
Task Closed
```

No execution decisions occur before transfer.

---

## 15. Versioning & Immutability

TaskObjects are immutable.

Rules:

- never edit an existing TaskObject
- corrections create a new version
- parent-child relationships remain preserved
- previous versions remain available for audit

---

## 16. Final Specification

The TaskObject is the official contract between interpretation and execution.

It guarantees:

- standardized communication
- immutable task definitions
- deterministic interpretation
- complete metadata
- auditability
- version control
- scalability
- execution independence

No downstream engine may reinterpret the original user request once a validated TaskObject has been generated.

---

# Part 4 — Governance, Performance Metrics & Operational Rules

## Table of Contents

1. Purpose  
2. Governance Principles  
3. Universal Operational Rules  
4. Clarification Policy  
5. Failure Handling  
6. Immutable Task Policy  
7. Task Lifecycle Governance  
8. Performance Metrics  
9. Quality Metrics  
10. Monitoring & Analytics  
11. Compliance Rules  
12. Future Compatibility  
13. Architecture Freeze Policy  
14. Final Assessment  

---

## 1. Purpose

This section defines the governance framework for the AI Task Orchestrator.

It ensures every TaskObject is:

- deterministic
- auditable
- immutable
- explainable
- version controlled
- backward compatible

The governance layer guarantees consistent behavior across AI models, execution environments, and future system expansions.

---

## 2. Governance Principles

The AI Task Orchestrator shall always:

- interpret before classifying
- classify before validating
- validate before generating TaskObjects
- generate immutable TaskObjects
- preserve provenance
- preserve version history
- preserve audit trails
- preserve deterministic behavior

The AI Task Orchestrator shall never:

- execute tasks
- perform reasoning
- select modules
- select frameworks
- allocate context
- modify existing TaskObjects

---

## 3. Universal Operational Rules

Every request must pass through the following sequence.

```text
Receive Request
    ↓
Interpret
    ↓
Classify
    ↓
Assess Complexity
    ↓
Assess Information Sufficiency
    ↓
Generate TaskObject
    ↓
Validate
    ↓
Transfer
    ↓
Complete
```

No stage may be skipped.

---

## 4. Clarification Policy

The Task Orchestrator determines whether clarification is required before TaskObject creation.

| Situation | Action |
|---|---|
| Complete Information | Continue |
| Minor Ambiguity | Continue and record assumptions |
| Missing Important Information | Ask user |
| Unsupported Request | Reject gracefully |
| Unsafe Request | Stop processing |

Clarification should always occur before execution, never during execution.

---

## 5. Failure Handling

### Validation Failure
Missing or invalid task metadata.

Action:
- reject TaskObject
- log failure
- request clarification if recoverable

### Interpretation Failure
Intent or objective cannot be determined.

Action:
- ask user
- never guess

### Unsupported Request
Outside project capability.

Action:
- explain limitation
- do not fabricate output

### Unsafe Request
Violates constitutional or safety policies.

Action:
- reject immediately
- record audit event

---

## 6. Immutable Task Policy

Once validated:

TaskObjects become immutable.

Updates require:

```text
Task v1
    ↓
Task v2
    ↓
Task v3
```

Older versions remain archived.

No TaskObject may be edited in place.

---

## 7. Task Lifecycle Governance

Every TaskObject follows:

```text
Created
    ↓
Validated
    ↓
Approved
    ↓
Transferred
    ↓
Executed
    ↓
Archived
```

If invalid:

```text
Created
    ↓
Rejected
```

If replaced:

```text
Superseded
    ↓
Archived
```

---

## 8. Performance Metrics

Operational metrics measure efficiency.

Track:

- average interpretation time
- average classification time
- validation time
- task transfer time
- task throughput
- average task complexity
- average task size

These metrics optimize system performance but never influence interpretation quality.

---

## 9. Quality Metrics

The following metrics measure interpretation accuracy.

- Intent Accuracy
- False Classification Rate
- Clarification Rate
- Task Retry Rate
- Validation Pass Rate
- Multi-Task Accuracy
- Entity Extraction Accuracy
- Information Sufficiency Accuracy
- Conversation Continuity Accuracy

The system should use these metrics for improvement, not self-congratulation.

---

## 10. Monitoring & Analytics

The Task Orchestrator continuously records:

```yaml
TasksProcessed
IntentDistribution
ComplexityDistribution
ClarificationRequests
FailureTypes
ValidationResults
AverageConfidence
TaskGrowth
ConversationStatistics
```

Analytics improve future optimization without changing historical TaskObjects.

---

## 11. Compliance Rules

Every TaskObject must satisfy:

- schema validation
- metadata validation
- version compatibility
- provenance recording
- object integrity
- immutable storage
- audit logging
- execution readiness

Objects failing compliance cannot enter the Execution Engine.

---

## 12. Future Compatibility

The architecture supports future expansion including:

- multi-agent AI
- multiple LLM providers
- persistent memory
- external APIs
- cloud execution
- distributed processing
- workflow automation
- enterprise integrations
- knowledge graphs
- autonomous research pipelines

No redesign should be required.

---

## 13. Architecture Freeze Policy

After Version v_0.0:

The architectural responsibilities of the Task Orchestrator are considered stable.

Future updates should focus only on:

- better intent classifiers
- better entity recognition
- better language understanding
- additional task categories
- improved decomposition heuristics

The architecture itself should remain stable.

---

## 14. Final Assessment

The **AI_Task_Orchestrator_v_0.0** is the official **Request Interpretation Engine** of the AI Operating System.

It transforms unstructured human language into deterministic, validated, immutable TaskObjects while remaining completely independent of execution, reasoning, research, module selection, framework selection, and output generation.

By separating interpretation from execution, the Task Orchestrator establishes a stable contract that enables the AI Operating System to scale without architectural redesign.

---

# Document Information

**Document:** AI_Task_Orchestrator_v_0.0.md  
**Version:** v_0.0  
**Status:** Production Ready  
**Architecture State:** Frozen  
**Dependencies:**  
- AI_Project_Instructions_v_0.0.md  
- AI_Object_Schemas_v_0.0.md  

**Consumed By:**  
- AI_Execution_Engine_v_0.0.md  

**Supersedes:** AI_Task_Orchestrator_v_0.0

---

# END OF DOCUMENT

<!-- IERL-HIGH-RELIABILITY v1.0 -->
## High-Reliability Task Framing Addendum

At task start, explicitly classify: decision type, horizon, entity/universe, required freshness, user constraints, and consequence of being wrong. Route to the narrowest sufficient workflow; do not invoke every available source by default.

If a missing input can materially reverse the result, ask for it or continue only with a labelled assumption and reduced confidence. Split compound requests into evidence collection, analysis, risk review, and output stages so an early narrative cannot anchor later reasoning.
<!-- END SYSTEM FILE 4: AI_Task_Orchestrator_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 5: AI_State_Manager_v_0_0.md | SHA256: 90bbff840a8b2db879e97ae6bc3775f351977d0740ba51ea21e88c79f97a9015 -->
## Embedded source 5: AI State Manager

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI State Manager  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_State_Manager_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Registry / Runtime Infrastructure
**Priority:** Critical
**Role:** Runtime State Tracking, Checkpoint, and Recovery Authority
**Architecture State:** Frozen

---

# Table of Contents

1. Purpose
2. Architectural Position
3. Responsibilities
4. Non-Responsibilities
5. State Object Schema
6. State Lifecycle
7. Checkpoint System
8. Rollback Protocol
9. Retry Coordination
10. Runtime Memory Model
11. Persistence Rules
12. Failure Recovery Integration
13. Interfaces
14. Governance
15. Final Specification

---

# 1. Purpose

The AI State Manager is the runtime infrastructure component responsible for tracking the execution state of every task session, recording checkpoints, and enabling recovery when an engine fails partway through processing.

It is consumed exclusively by the Execution Engine, which uses it to log, checkpoint, and recover runtime sessions per the Failure & Recovery Architecture (AI_Architecture_Overview_v_0.0.md §13C).

---

# 2. Architectural Position

```
AI_Execution_Engine
    ↓ (requests state read/write)
AI_State_Manager
    ↓ (persists)
Session State Store
```

The State Manager never initiates action. It responds only to Execution Engine requests to read, write, checkpoint, or roll back state.

---

# 3. Responsibilities

The State Manager shall:

- Track the current status of every active runtime session
- Record checkpoints at defined stage boundaries
- Store failure events with full context for recovery
- Provide rollback data on request
- Maintain state history for audit reconstruction
- Enforce state immutability once a session is archived

---

# 4. Non-Responsibilities

The State Manager shall never:

- Make scheduling decisions (Execution Engine's responsibility)
- Interpret task content
- Modify object content (TaskObject, ResearchObject, etc.)
- Retry failed operations itself (it stores retry counts; Execution Engine acts on them)
- Decide confidence, research completeness, or audit verdicts

---

# 5. State Object Schema

```yaml
StateObject:
  StateID:
  TaskID:
  SessionStatus:          # Pending | Active | Checkpointed | Completed | Failed | Archived
  CurrentStage:           # 1-7 per AI_Pipeline_Specification_v_0.0
  CheckpointHistory:
    - CheckpointID:
      Stage:
      Timestamp:
      SnapshotRef:
  FailureLog:
    - FailureID:
      Stage:
      Timestamp:
      FailureClass:       # F1 | F2 | F3 | F4 (per AI_Architecture_Overview_v_0.0.md §13C)
      RecoveryAttempt:
      FinalStatus:
  RetryCount:
  ActiveModules:
  ActiveFrameworks:
  ContextAllocationRef:   # pointer to Context Manager's allocation record
  CreatedAt:
  UpdatedAt:
  ArchivedAt:
```

---

# 6. State Lifecycle

```
Created
   ↓
Active
   ↓
Checkpointed  ←──┐
   ↓             │ (loop per stage)
[Stage complete]─┘
   ↓
Completed  ─────────→  Archived

   OR (at any point)

Failed → Recovery Attempt → [Active (resumed) | Archived (terminal failure)]
```

Once `Archived`, a `StateObject` is immutable. No field may be edited in place — corrections require a new `StateObject` version with `SupersedesStateID` reference.

---

# 7. Checkpoint System

A checkpoint is recorded at the completion of each pipeline stage (per `AI_Pipeline_Specification_v_0.0.md`):

| Checkpoint | Recorded After |
|---|---|
| CP-1 | TaskObject validated |
| CP-2 | ResearchPlanObject validated |
| CP-3 | Execution session initialized |
| CP-4 | ResearchObject + EvidenceObject produced |
| CP-5 | DecisionObject produced |
| CP-6 | AuditObject produced |
| CP-7 | OutputObject emitted |

**Recovery Rule:** On failure, the Execution Engine resumes from the nearest valid checkpoint, not from Stage 1. Only checkpoints with `SnapshotRef` fully written are considered valid resume points.

---

# 8. Rollback Protocol

Rollback restores the session to the state recorded at a specified checkpoint. Rollback affects only:

- Execution state
- Context allocation record (delegates actual reallocation to Context Manager)
- Active module/framework list

Rollback never affects already-produced validated objects (`TaskObject`, `ResearchObject`, etc.) — those are immutable once validated, per each engine's own contract. Rollback discards only in-progress, unvalidated work.

---

# 9. Retry Coordination

The State Manager tracks `RetryCount` per stage. It does not decide whether to retry — that is the Execution Engine's responsibility per its Retry Policy (Execution Engine §48). The State Manager enforces one governance rule:

> **Retry Ceiling:** If `RetryCount` for any single stage exceeds the Resource Governor's `maximum retry count` (Execution Engine §27), the State Manager marks the session `Failed` and refuses further retry recording for that stage, forcing escalation per Failure Classification F3.

---

# 10. Runtime Memory Model

State is held in two tiers:

| Tier | Scope | Lifetime |
|---|---|---|
| **Hot State** | Current active session only | Duration of task processing |
| **Archived State** | Completed/failed sessions | Persisted for audit trail; read-only |

Hot State is what Execution Engine reads/writes during processing. Archived State is what Quality Audit and downstream reviewers query for provenance reconstruction — it is never written to during active processing.

---

# 10A. State Consistency & Authority Rules

To prevent data drift and architectural fragmentation, the system enforces the following state consistency rules:

*   **Authoritative State**: The master session state (`StateObject`) stored and managed exclusively by the AI State Manager. This is the single source of truth for runtime progress.
*   **Derived State**: Temporary flags or values calculated dynamically from the authoritative state (e.g., stage durations, progress percentages, active loop counters). Derived state is never persisted.
*   **Cached State**: Local read-only copies of state held temporarily by engines to reduce query latency. Cached state must be validated using the `StateVersion` before use.
*   **StateVersion**: A monotonic integer counter included in the `StateObject` header. It starts at 1 and increments on every write operation.
*   **Expiration**: Inactive Hot State entries are marked expired after 24 hours of task inactivity and are moved to the Archived State tier.
*   **Invalidation**: When the Execution Engine writes a state change, a broadcast is sent to all engine instances to invalidate their local Cached State.
*   **Recovery**: If an engine loses synchronization, it must discard its local state and query the State Manager for the latest valid checkpoint snapshot (`CP-1` to `CP-7`).
*   **Conflict Resolution**: Enforces Optimistic Concurrency Control (OCC). If two write requests arrive with the same version, the State Manager accepts the first and rejects the second. The rejected transaction must reload the updated state and retry.
*   **Single Authority**: The AI State Manager is the sole writer of the runtime state. No engine or skill may silently maintain or act upon alternative authoritative states.

---

# 11. Persistence Rules

- Every `StateObject` write is versioned; no in-place mutation of Archived State
- CheckpointHistory is append-only
- FailureLog is append-only
- State persists independently of context window — it is not lost on context reallocation (this is precisely why it exists as a separate component from Context Manager)

---

# 12. Failure Recovery Integration

This maps directly onto the Failure & Recovery Architecture already defined in `AI_Architecture_Overview_v_0.0` §13C:

| Failure Severity | State Manager Action |
|---|---|
| F1 (Recoverable) | Log retry attempt; no checkpoint rollback needed |
| F2 (Degraded) | Log degradation flag on current `StateObject`; checkpoint preserved |
| F3 (Escalated) | Mark session `Failed`; preserve full `FailureLog` for human/audit review |
| F4 (Blocking) | Mark session `Failed`; set `SessionStatus: Archived` immediately; no retry permitted |

---

# 13. Interfaces

**Consumed by:** AI_Execution_Engine (exclusively)
**Never accessed by:** Research Engine, Reasoning Skills, Quality Audit, Output System directly — these engines' state needs are mediated through Execution Engine's coordination role, consistent with the Dependency Rules (AI_Architecture_Overview_v_0.0.md §13A: "Any Registry → Any Engine" is forbidden; the State Manager is a registry-tier component).

---

# 14. Governance

Every `StateObject` must satisfy:

- Unique `StateID`
- Valid `TaskID` reference to an existing `TaskObject`
- `SessionStatus` transitions only follow the lifecycle in Section 6 (no skipping states)
- `CheckpointHistory` entries are chronologically ordered
- Archived sessions are immutable

---

# 15. Final Specification

The AI State Manager provides the runtime memory backbone that makes the Failure & Recovery Architecture operational. Without it, failures have nowhere to be logged and no checkpoint to resume from — this document resolves that gap (Forensic Audit CV-03, State Manager component).

---

# Document Information

**Document:** AI_State_Manager_v_0.0.md
**Version:** v_0.0
**Status:** Production Ready
**Dependencies:** AI_Execution_Engine_v_0.0.md, AI_Pipeline_Specification_v_0.0.md
**Consumed By:** AI_Execution_Engine_v_0.0.md (exclusively)
**Resolves:** CV-03 (Forensic Audit — Missing State Manager)

# END OF DOCUMENT
<!-- END SYSTEM FILE 5: AI_State_Manager_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 6: AI_Context_Manager_v_0_0.md | SHA256: 1aca7a69c529a8a3872de6b4bdf02a9e38c599b7dbaae65e473dab2cdc5002fb -->
## Embedded source 6: AI Context Manager

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

<!-- END SYSTEM FILE 6: AI_Context_Manager_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 7: AI_Confidence_Standard_v_0_0.md | SHA256: 3a85bef2f6e98ad0eec61c46d3cbb59ab7d0ea9697aa80c4ffb024d897dac38e -->
## Embedded source 7: AI Confidence Standard

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Confidence Standard  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Confidence_Standard_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Cross-Cutting Standard
**Priority:** Critical
**Role:** Universal Confidence Framework
**Encoding:** UTF-8 (corrects v_0.0 UTF-16LE defect -- CV-04)
**Architectural Authority:** AI_System_Constitution prevails over this standard on any conflict.
**Scope Clarification:** This standard defines confidence *representation*, not truth or probability of an outcome. Confidence measures the reliability of process and evidence -- never the likelihood that a prediction will be correct.

---

# Table of Contents

## Part 1 -- Confidence Architecture
1. Purpose, 2. Vision, 3. Scope, 4. Design Philosophy, 5. Responsibilities, 6. Non-Responsibilities, 7. Universal Principles, 8. Confidence Lifecycle

## Part 2 -- Confidence Model
9. Confidence Levels & Numeric Mapping, 10. Confidence Sources, 11. Confidence Categories, 12. Confidence Aggregation Formula, 13. Confidence Propagation & Calibration, 14. Confidence Metadata, 15. Confidence Validation

## Part 3 -- Engine Confidence Standards
16-22. Task / Research / Evidence / Reasoning / Decision / Audit / Output Confidence

## Part 4 -- Governance
23. Universal Rules, 24. Compliance, 25. Future Extensions, 26. Final Specification

---

# PART 1 -- CONFIDENCE ARCHITECTURE

# 1. Purpose
Defines how confidence is represented, calculated, propagated, and reported across the AI Operating System. All engines use this common framework -- no engine defines its own confidence vocabulary or math.

# 2. Vision
A transparent, mathematically reproducible measure of certainty at every pipeline stage. Confidence reflects the reliability of available information and processing quality -- not correctness of the eventual outcome.

# 3. Scope
Applies to: Task Orchestrator, Intelligence Engine, Research Engine, Reasoning Skills, Quality Audit, Output System.

# 4. Design Philosophy
Confidence shall be: Consistent, Explainable, Evidence-based, Traceable, Comparable, Versioned, and Numerically reproducible (new in v_0.0).

# 5. Responsibilities
This standard defines: confidence representation, numeric scoring, aggregation formula, propagation rules, calibration behavior, metadata, validation.

# 6. Non-Responsibilities
Does not: perform reasoning, make decisions, override evidence, replace Quality Audit, predict outcomes.

# 7. Universal Principles
Confidence shall never exceed evidence quality; shall decrease when uncertainty increases; shall be explainable, traceable, and -- as of v_0.0 -- reproducible from a stated formula, not a subjective judgment.

# 8. Confidence Lifecycle
```
Generated -> Validated -> Propagated -> Consumed -> Archived
```

---

# PART 2 -- CONFIDENCE MODEL

# 9. Confidence Levels & Numeric Mapping

This is the primary gap closed from v_0.0 (Forensic Audit MV-01: no quantitative model existed).

| Level | Score Range | Interpretation |
|---|---|---|
| Very High | 0.85 - 1.00 | Strong, multi-source, internally consistent evidence; no material contradictions |
| High | 0.70 - 0.84 | Solid evidence base; minor gaps or single-source reliance on non-critical points |
| Moderate | 0.50 - 0.69 | Adequate evidence with identifiable gaps or some unresolved conflict |
| Low | 0.30 - 0.49 | Weak or thin evidence; significant gaps or unresolved conflicts |
| Very Low | 0.00 - 0.29 | Minimal or contradictory evidence; conclusion is provisional at best |

ConfidenceScore is always a float in [0.00, 1.00]. ConfidenceLevel is the label derived by table lookup -- never assigned independently of the score.

# 10. Confidence Sources
Evidence Quality, Source Reliability, Data Completeness, Research Coverage, Logical Consistency, Validation Results.

Source Reliability Weight Table (used in Section 12):

| Source Tier | Weight |
|---|---|
| Primary (exchange filings, audited financials, regulatory filings) | 1.00 |
| Secondary (reputable financial media, sell-side research) | 0.70 |
| Tertiary (aggregator sites, unverified commentary) | 0.40 |

# 11. Confidence Categories
Task, Research, Evidence, Reasoning, Decision, Audit, Output Confidence -- each computed per Part 3.

# 12. Confidence Aggregation Formula

Evidence to Research Confidence (weighted mean by source credibility):

```
ResearchConfidence = Sum(weight_i x confidence_i) / Sum(weight_i)

where:
  confidence_i = individual EvidenceObject's ConfidenceScore
  weight_i     = Source Reliability Weight (Section 10 table)
```

Coverage Penalty: If Research Engine's completeness gate (Research Engine section 22) reports coverage below its threshold, apply a multiplicative penalty:

```
AdjustedResearchConfidence = ResearchConfidence x CoverageFactor

where CoverageFactor = min(1.0, ActualCoverage / RequiredCoverage)
```

Reasoning to Decision Confidence:

```
DecisionConfidence = AdjustedResearchConfidence x ConsistencyFactor

where ConsistencyFactor in [0.6, 1.0]:
  1.0  -> no unresolved contradictions in evidence
  0.8  -> minor contradictions, disclosed and reconciled
  0.6  -> material contradiction presented as competing scenarios
         (per Reasoning Skills conflict handling -- never suppressed)
```

Audit Confidence: equals DecisionConfidence unless Quality Audit's own review identifies a defect not visible upstream (e.g., a bias flag), in which case Quality Audit may apply a further documented reduction -- never an increase (per Section 13).

Output Confidence: equals the final AuditConfidence passed through unchanged. The Output System never recalculates confidence -- it only renders it (per AI_Output_System_v_0.0.md section 14).

# 13. Confidence Propagation & Calibration

Core Rule (unchanged from v_0.0, now formalized):

```
OutputConfidence <= AuditConfidence <= DecisionConfidence
                  <= AdjustedResearchConfidence <= max(EvidenceConfidence_i)
```

Confidence is monotonically non-increasing as it moves downstream, with exactly one exception:

Calibration Exception: A downstream stage may increase confidence only when it obtains genuinely new supporting evidence not available upstream (e.g., Quality Audit cross-validates a claim against an independent source the Research Engine didn't have access to). Any such increase must be logged in ConfidenceInheritedFrom with an explicit CalibrationReason field -- silent increases are a standard violation (Section 23).

# 14. Confidence Metadata

Every confidence value includes:

```yaml
ConfidenceLevel:            # table lookup from Section 9
ConfidenceScore:             # float 0.00-1.00
AssessmentBasis:              # which formula/rule produced this value
ConfidenceSource:             # engine that generated it
ConfidenceInheritedFrom:      # upstream ConfidenceScore(s) consumed
SupportingFactors: []
LimitingFactors: []
CalibrationReason:            # only present if Section 13 exception applied
Timestamp:
```

# 15. Confidence Validation
Every confidence assessment shall be: evidence-backed, internally consistent with the aggregation formula (Section 12), explainable, traceable, and reproducible -- i.e., re-running the formula on the same inputs yields the same score.

--

# 15A. Confidence Decay Horizons (Addition)

Evidence confidence decays over time. Apply a StalenessFlag when
evidence age exceeds its category horizon:

| Category | Staleness Horizon |
|---|---|
| Financial statement data | 90 days |
| Regulatory/compliance status | 30 days |
| Governance/promoter assessment | 180 days |
| Technical/price data | 7 days |
| Shareholding pattern | 90 days (one quarter) |

StalenessFlag: true -> the evidence is treated as a starting point
requiring re-verification, not a current fact. Apply a confidence
penalty consistent with Section 12's CoverageFactor mechanism:
EvidenceConfidence is multiplied by 0.85 when StalenessFlag is true
and no fresher corroborating evidence exists.

---

# 15B. Canonical Data & Evidence Quality Chain

To guarantee that weak sources directly lower downstream decisions, every task execution enforces a single, traceable quality chain:

`Source → Evidence → Quality → Confidence → Decision → Output`

### 1. Evidence Quality Metrics
Every `EvidenceObject` must capture the following metadata parameters:
*   **SourceTier**: `Primary` (weight = 1.0), `Secondary` (weight = 0.7), or `Tertiary` (weight = 0.4).
*   **RetrievalTimestamp**: The ISO-8601 timestamp when the data was scraped or ingested.
*   **AsOfDate**: The original reporting date of the underlying source record.
*   **Freshness**: Calculated dynamically: `Freshness = (CurrentTime - AsOfDate) <= StalenessHorizon`.
*   **Completeness**: A ratio `[0.0, 1.0]` of expected fields successfully extracted.
*   **ContradictionFlag**: Set to `true` if this evidence conflicts with another loaded evidence item.
*   **Provenance**: A verifiable URI/link pointing to the exact page, table, or line of the source.
*   **PrimarySourceAvailability**: `true` if a primary document was audited; `false` if secondary reports were used.
*   **DataQualityStatus**: One of `VERIFIED` | `UNVERIFIED` | `STALE` | `CORRUPTED`.

### 2. Math for Downstream Impact
A weak source lowers downstream confidence according to the following formulas:

```
AdjustedEvidenceConfidence = SourceTierWeight * Completeness * StalenessPenalty * VerificationPenalty

Where:
  StalenessPenalty = 0.85 if (Freshness == False) else 1.0
  VerificationPenalty = 0.70 if (DataQualityStatus == UNVERIFIED) else 1.0
```

If any critical piece of evidence (e.g., forensic risk or accounting data) has an `AdjustedEvidenceConfidence < 0.50`, it limits the overall `DecisionConfidence` to a maximum ceiling of `0.50` (Moderate), regardless of other high-quality inputs.

---


# PART 3 -- ENGINE CONFIDENCE STANDARDS

# 16. Task Confidence
Measures: interpretation certainty of user intent. Inputs: ambiguity signals from Task Orchestrator's classification step. Output: informs whether ClarificationRequest is triggered. Upstream relationship: none -- first confidence generated.

# 17. Research Confidence
Measures: completeness and reliability of collected research. Inputs: weighted evidence scores (Section 12) + coverage factor. Output: AdjustedResearchConfidence. Upstream relationship: aggregates all EvidenceConfidence values.

# 18. Evidence Confidence
Measures: quality/reliability of one evidence item. Inputs: source tier weight (Section 10) + Research Engine's own source validation. Output: per-item ConfidenceScore. Upstream relationship: none -- atomic input.

# 19. Reasoning Confidence
Measures: logical strength and internal consistency of reasoning. Inputs: AdjustedResearchConfidence + ConsistencyFactor. Output: feeds Decision Confidence. Upstream relationship: derived from Research Confidence.

# 20. Decision Confidence
Measures: confidence in the DecisionObject's conclusion. Inputs: Section 12 formula. Output: DecisionConfidence. Upstream relationship: = Research Confidence x Consistency Factor.

# 21. Audit Confidence
Measures: confidence after independent validation. Inputs: DecisionConfidence, adjusted only downward unless Section 13 exception applies. Output: AuditConfidence. Upstream relationship: <= Decision Confidence.

# 22. Output Confidence
Measures: final confidence shown to the user. Inputs: AuditConfidence, passed through unchanged. Output: rendered per AI_Output_System_v_0.0.md section 14/15. Upstream relationship: = Audit Confidence exactly.

---

# PART 4 -- GOVERNANCE

# 23. Universal Rules
Always: separate confidence from certainty; base confidence on the Section 12 formula; explain confidence via metadata; preserve confidence history; maintain traceability.
Never: inflate confidence; hide uncertainty; ignore contradictory evidence; increase confidence downstream without a logged Calibration Reason.

# 24. Compliance
Every engine implements this standard's formula exactly -- not an approximation. Non-compliant confidence calculations are architectural defects.

# 25. Future Extensions
Additional confidence categories may be added without changing the core aggregation formula, provided they follow the monotonic propagation rule.

# 26. Final Specification
The AI Confidence Standard v_0.0 defines a mathematically reproducible method for representing and propagating confidence across the AI Operating System. It resolves CV-04 (UTF-16 encoding made v_0.0 unreadable -- this document is plain UTF-8) and MV-01 (no aggregation formula existed -- Section 12 now provides one).

---

# Document Information

Document: AI_Confidence_Standard_v_0.0.md
Version: v_0.0
Supersedes: AI_Confidence_Standard_v_0.0 (UTF-16 encoded, no numeric model)
Status: Production Ready
Applies To: All Core Engines, All Future Engines
Resolves: CV-04, MV-01
Architecture State: Frozen

# END OF DOCUMENT

<!-- END SYSTEM FILE 7: AI_Confidence_Standard_v_0_0.md -->

---

<!-- BEGIN SYSTEM FILE 8: AI_Explainability_Standard_v_0_0.md | SHA256: dc945149d1491c05cafbd8fda6eb56c41e50cb51862fb6baf408a84effc57a7e -->
## Embedded source 8: AI Explainability Standard

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Explainability Standard  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Explainability_Standard_v_0.0

**Version:** v_0.0  
**Status:** Production Ready  
**Category:** Cross-Cutting Standard  
**Priority:** High  
**Role:** Universal Explainability Framework

---

# Table of Contents

## Part 1 — Explainability Architecture

1. Purpose
2. Vision
3. Scope
4. Design Principles
5. Core Responsibilities
6. Explainability Lifecycle
7. Universal Principles

---

## Part 2 — Explainability Framework

8. Explainability Model
9. Explainability Object
10. Evidence Traceability
11. Reasoning Traceability
12. Assumption Management
13. Confidence & Uncertainty
14. Decision Rationale
15. Explainability Validation

---

## Part 3 — Engine Standards

16. Engine Requirements
17. Output Requirements
18. Governance
19. Final Specification

---

# PART 1 — EXPLAINABILITY ARCHITECTURE

---

# 1. Purpose

The AI Explainability Standard defines how every important conclusion, recommendation, and decision within the AI Operating System shall be explained.

Every material output must be understandable, traceable, and evidence-backed.

---

# 2. Vision

Provide a single explainability framework that is:

- Transparent
- Evidence-based
- Traceable
- Auditable
- Reproducible
- Consistent

---

# 3. Scope

This standard applies to:

- AI_Task_Orchestrator
- AI_Execution_Engine
- AI_Intelligence_Engine
- AI_Research_Engine
- AI_Reasoning_Engine
- AI_Quality_Audit
- AI_Output_System

---

# 4. Design Principles

Every explanation shall be:

- Honest
- Complete
- Evidence-driven
- Consistent
- Human-readable
- Machine-readable

---

# 5. Core Responsibilities

This standard defines:

- Explanation structure
- Evidence linkage
- Reasoning trace
- Assumption disclosure
- Confidence explanation
- Uncertainty disclosure
- Decision rationale

It does not perform reasoning or modify conclusions.

---

# 6. Explainability Lifecycle

```
Evidence
    │
Reasoning
    │
Decision
    │
Explanation
    │
Validation
    │
Output
```

Every stage preserves traceability.

---

# 7. Universal Principles

Every explanation shall:

✓ Reference supporting evidence

✓ Distinguish facts from inference

✓ Record assumptions

✓ Disclose uncertainty

✓ Explain reasoning

✓ Remain internally consistent

✓ Be reproducible

Hidden reasoning is prohibited.

# PART 2 — EXPLAINABILITY FRAMEWORK

---

# 8. Explainability Model

Every important output shall include a standardized explanation composed of the following elements.

| Component | Purpose |
|------------|---------|
| Objective | What decision was made |
| Evidence | Facts supporting the decision |
| Reasoning | How the evidence was evaluated |
| Assumptions | Conditions accepted as true |
| Alternatives | Plausible competing conclusions |
| Confidence | Degree of confidence |
| Uncertainty | Known limitations and risks |
| Conclusion | Final rationale |

---

# 9. ExplainabilityObject

Every DecisionObject and OutputObject shall include an ExplainabilityObject.

```yaml
ExplainabilityObject:

ExplainabilityID:

Objective:

EvidenceReferences:

ReasoningTrace:

Assumptions:

AlternativeViews:

ConfidenceSummary:

UncertaintySummary:

DecisionRationale:

ValidationStatus:
```

This object provides a standardized explanation that can be audited independently of the final recommendation.

---

# 10. Evidence Traceability

Every material conclusion shall reference one or more EvidenceObjects.

Evidence references shall include:

- Evidence ID
- Source
- Source Type
- Collection Date
- Validation Status

Evidence without traceability shall not support decisions.

---

# 11. Reasoning Traceability

Reasoning shall describe how evidence produced the conclusion.

Minimum requirements:

- Reasoning method used
- Key logical steps
- Major evidence considered
- Evidence rejected
- Trade-offs evaluated

The system explains the reasoning process, not hidden internal model computations.

---

# 12. Assumption Management

Every significant assumption shall be explicitly recorded.

Typical assumptions include:

- Market conditions
- Economic outlook
- Business expectations
- Financial estimates
- Data completeness

Each assumption should state:

- Description
- Impact
- Confidence
- Evidence (if available)

Hidden assumptions are prohibited.

---

# 13. Confidence & Uncertainty

Confidence and uncertainty shall always be reported together.

Confidence explains:

- Why confidence is high or low
- Supporting factors
- Limiting factors

Uncertainty explains:

- Missing evidence
- Conflicting information
- Model limitations
- External risks

Confidence shall never imply certainty.

---

# 14. Decision Rationale

Every important recommendation shall answer:

- What decision was reached?
- Why was it selected?
- What evidence mattered most?
- What alternatives were rejected?
- What could change the decision?

The rationale should be concise, evidence-based, and reproducible.

---

# 15. Explainability Validation

Before output generation, the Quality Audit shall verify:

✓ Evidence is traceable

✓ Reasoning is documented

✓ Assumptions are disclosed

✓ Alternatives are considered

✓ Confidence is justified

✓ Uncertainty is disclosed

✓ Decision rationale is complete

Outputs failing explainability validation shall be flagged for review.

<!-- END SYSTEM FILE 8: AI_Explainability_Standard_v_0_0.md -->

---


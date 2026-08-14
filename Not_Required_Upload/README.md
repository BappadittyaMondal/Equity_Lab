# IERL — Indian Equity Research Lab
## AI Operating System — README

**Version:** v_0.0 (Production)
**Status:** Production Ready

---

## 1. What Is This?

IERL is an AI Operating System for institutional-grade Indian equity research. It is not a software application — it is a **document-driven AI system**: a set of specification files that instruct an LLM (Claude) how to interpret a research request, plan analysis, gather evidence, reason to a conclusion, independently audit that conclusion, and deliver a compliant, explainable output.

Every engine, standard, and rule the AI follows is written down in this repository. There is no hidden logic — if it isn't in a file here, the AI doesn't do it.

---

## 2. Purpose

To produce institutional-quality equity research (company analysis, valuation, sector reviews, portfolio checks) that is:

- **Evidence-based** — every conclusion traces back to a source
- **Confidence-calibrated** — the AI states how sure it is, and why
- **Auditable** — every output passed an independent quality gate before reaching the user
- **Compliant** — every output carries the mandatory SEBI disclaimer
- **Explainable** — reasoning, assumptions, and alternatives are always disclosed, never hidden

---

## 3. Who Should Use This

- Anyone running equity research through a Claude Project configured with these files
- Anyone maintaining, extending, or auditing this AI system
- Any future LLM session picking up this repository cold — this README and `PROJECT_INSTRUCTIONS.md` are the two files that should be read first

---

## 4. Where To Start

1. Read this file (you're here).
2. Read `PROJECT_INSTRUCTIONS.md` — the rules for working on this repository.
3. Read `00_Index.md` — the Knowledge Library map (24 domains).
4. Read `AI_Architecture_Overview_v_0.0.md` — the master structural blueprint.
5. Read `AI_Pipeline_Specification_v_0.0.md` — the exact processing sequence.

---

## 5. High-Level Architecture

```
User Request
     │
Task Orchestrator          → interprets intent
     │
Intelligence Engine         → plans research strategy
     │
Execution Engine            → coordinates the three stages below
     │
Research Engine              → gathers evidence
     │
Reasoning Skills              → forms a conclusion
     │
Quality Audit                  → independently validates the conclusion
     │
Output System                   → renders the final, compliant response
     │
User Response
```

Supporting infrastructure (State Manager, Context Manager, Dependency Map) and supporting standards (Confidence Standard, Explainability Standard, Data Object Standard) sit alongside this pipeline — full detail in `AI_Architecture_Overview_v_0.0.md`.

---

## 6. Repository Structure

```
/  (root)
├── README.md                              ← you are here
├── PROJECT_INSTRUCTIONS.md                 ← repository rules
│
├── AI_Project_Instructions_v_0.0.md              ← Constitution (Rank 1 authority)
├── AI_Architecture_Overview_v_0.0.md        ← Master blueprint (Rank 2)
├── AI_Pipeline_Specification_v_0.0.md       ← Authoritative processing sequence
│
├── Core Engines
│   ├── AI_Task_Orchestrator_v_0.0.md
│   ├── AI_Intelligence_Engine_v_0.0.md
│   ├── AI_Execution_Engine_v_0.0.md
│   ├── AI_Research_Engine_v_0_0.md          (+ AI_Research_Learning_System_v_0.0.md addendum)
│   ├── AI_Reasoning_Skills_v_0_0.md
│   ├── AI_Quality_Audit_v_0.0.md            (+ AI_Quality_Audit_Addendum content merged in)
│   └── AI_Output_System_v_0.0.md
│
├── Infrastructure
│   ├── AI_State_Manager_v_0.0.md
│   ├── AI_Context_Manager_v_0_0.md
│   └── AI_Dependency_Map_v_0.0.md            (+ AI_Skill_Knowledge_Governance_v_0.0.md addendum)
│
├── Cross-Cutting Standards
│   ├── AI_Confidence_Standard_v_0.0.md
│   ├── AI_Explainability_Standard_v_0.0.md
│   ├── AI_Object_Schemas_v_0.0.md            ← single canonical object standard
│   ├── AI_Object_Field_Reconciliation_v_0.0.md   ← historical reconciliation record
│   └── AI_Unified_Pattern_Taxonomy_v_0.0.md  ← shared pattern classes across domains
│
├── Registries
│   ├── AI_Module_Registry_v_0.0.md
│   └── AI_Framework_Registry_v_0.0.md
│
├── Knowledge Library (Knowledge_IRA_COL_FINAL/)
│   ├── 00_Index.md                          ← 44 domains, start here
│   ├── Domain_01_Economics.md … Domain_44_Geo_Economic_Impact.md
│   ├── Screener_Field_Glossary_v_0.0.md
│   └── Sector_Quick_Reference_v_0.0.md
│
├── Skill Library (AI_SKILL_IRA_col_final/)
│   ├── 04_Skills_Reference_v_0.0.md          ← 25 workflow skills, single file
│   ├── AI_Comparison_Engine_Skill.md
│   ├── AI_Forensic_Accounting_Skill.md … (14 more analytical lens skills)
│   ├── Technical_Analysis_Data_Input_Template_v_0.0.md
│   └── Skill_Library_Manifest.md            ← which files are canonical
│
├── Governance / Records
│   ├── AI_Global_Synchronization_Report_v_0.0.md
│   ├── AI_Object_Synchronization_Report_v_0.0.md
│   ├── AI_Knowledge_Mode_Architecture_v_0.0.md
│   ├── AI_Conformance_Matrix_v_0.0.md       ← engine × input/output × authority matrix
│   ├── AI_Regression_Tests_v_0.0.md         ← test scenarios for core workflows
│   ├── FINAL_PROJECT_CERTIFICATION.md       ← status snapshot, re-verify before trusting
│   └── IRA_Final_Status_and_Roadmap.md
│
└── Validation Tools
    ├── %%IRA_Project_Validator_v1.0.py         ← run before every upload
    └── %%IRA_Validation_Report_Sample_Run.md
```

---

## 7. Document Hierarchy (Who Governs Whom)

```
Rank 1  AI_Project_Instructions_v_0.0.md          — Constitution, supreme
Rank 2  AI_Architecture_Overview_v_0.0.md    — Technical structure
Rank 3  AI_Data_Object_Standard / Object_Schemas — Object schemas
Rank 4  AI_Confidence_Standard / Explainability_Standard
Rank 5  Core Engine specifications
Rank 6  Module Registry / Framework Registry / Dependency Map
Rank 7  Knowledge Packs / Skill Packs
Rank 8  Modules and Frameworks
Rank 9  Runtime Output (governs nothing else)
```

Full detail and conflict-resolution rules: `AI_Architecture_Overview_v_0.0.md` §13B.

---

## 8. Version Policy

- Each file's version number is independent — bumping one file does not require bumping others.
- Version format: `v<major>.<minor>` (e.g., `v_0.0`, `v_0.0`).
- A **major** version bump means a breaking change to that file's contract, schema, or logic.
- A **minor** version bump means additive content — new sections, expanded detail, corrected references — with no breaking change.
- Every file's own "Document Information" footer states its version, status, and what it supersedes (if anything).

---

## 9. Frozen vs. Extensible

**Frozen** (kernel logic — changed only via the amendment protocol in `PROJECT_INSTRUCTIONS.md`):
Constitution, Architecture Overview, Pipeline Specification, Data Object Standard, Confidence Standard, Explainability Standard, each engine's core contract and failure behavior.

**Extensible** (add without touching the above):
New Knowledge domains, new Skill packs, new Modules, new Frameworks, new output templates — all added through the registry layer.

---

## 10. Key Documents Quick-Reference

| Question | Read |
|---|---|
| "What does the system do, step by step?" | `AI_Pipeline_Specification_v_0.0.md` |
| "What can this engine consume/produce?" | `AI_Architecture_Overview_v_0.0.md` §8A |
| "What happens when something fails?" | `AI_Architecture_Overview_v_0.0.md` §13C |
| "Who decides X?" | `AI_Architecture_Overview_v_0.0.md` §13D |
| "What fields does object Y have?" | `AI_Object_Field_Reconciliation_v_0.0.md` |
| "Which knowledge domain covers Z?" | `00_Index.md` |
| "Which skill file do I run for task W?" | `Skill_Library_Manifest.md` |

---

## 11. Status

Production Ready. All critical and major defects identified in the project's forensic audits have been resolved. See `AI_Global_Synchronization_Report_v_0.0.md` for the full validation record.

---

**Document:** README.md
**Version:** v_0.0
**Maintained alongside:** PROJECT_INSTRUCTIONS.md

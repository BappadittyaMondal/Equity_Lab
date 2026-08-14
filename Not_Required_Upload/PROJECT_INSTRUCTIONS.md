# PROJECT_INSTRUCTIONS.md
## IERL AI Operating System — Repository Working Rules

**Version:** v_0.0 (Production)
**Status:** Production Ready
**Role:** Defines how anyone — human or AI — works on this repository. This is not the system's Constitution (`AI_Project_Instructions_v_0.0.md`, which governs the AI's behavior at runtime); this is the repository's own maintenance constitution.

---

## 1. Project Philosophy

This repository is a **document-driven AI system**. The specification files are not documentation *about* the system — they *are* the system. An LLM reading these files correctly is the entire runtime. This means:

- Precision matters more than prose quality.
- A contradiction between two files is not a style issue — it's a runtime defect.
- Every file must be readable by an LLM (plain UTF-8 markdown; no corrupted encoding, no unreadable binary formats for anything load-bearing).

---

## 2. Non-Negotiable Rules

1. **One object, one field list.** Every core object (TaskObject, ResearchObject, EvidenceObject, DecisionObject, AuditObject, OutputObject) has exactly one canonical field set, recorded in `AI_Object_Field_Reconciliation_v_0.0.md`. Both `AI_Data_Object_Standard` and `AI_Object_Schemas` must display that same field set — never a different one.
2. **One pipeline sequence.** `AI_Pipeline_Specification_v_0.0.md` is the only place the processing order is defined. No other file may draw a conflicting sequence diagram.
3. **Constitution is supreme.** `AI_Project_Instructions_v_0.0.md` overrides every other document on constitutional matters (ethics, CIO Authority Rules, mandatory disclaimers). No architecture or engine file may contradict it.
4. **No silent duplication.** If a fact belongs to another document, reference it by name — never copy it in. Duplication is how drift happens (see `AI_Object_Field_Reconciliation_v_0.0.md` for what duplication without sync caused).
5. **Registries are read-only at runtime.** Module Registry, Framework Registry, Knowledge Packs, and Skill Packs are consumed, never modified, during a live task.

---

## 3. Frozen Architecture

The following are frozen — their kernel logic does not change without the Amendment Protocol (Section 6):

- `AI_Project_Instructions_v_0.0.md`
- `AI_Architecture_Overview_v_0.0.md`
- `AI_Pipeline_Specification_v_0.0.md`
- `AI_Object_Schemas_v_0.0.md` / `AI_Object_Schemas_v_0.0.md` (schema definitions)
- `AI_Confidence_Standard_v_0.0.md`
- `AI_Explainability_Standard_v_0.0.md`
- Each core engine's contract and failure-behavior sections

Everything else — Knowledge domains, Skill packs, Modules, Frameworks, output templates — is extensible without amendment.

---

## 4. Modification Rules

**Before changing any frozen file:**
- State explicitly what is changing and why.
- Bump that file's version number.
- Check every file that references the changed section (use the Dependency Rules in `AI_Architecture_Overview_v_0.0.md` §13A to find them).
- Update all referencing files in the same edit pass — never leave a stale reference for "later."

**Before adding a new Knowledge domain:**
- Add it to `00_Index.md` with a number, trigger keywords, cross-domain links, and a conflict-arbitration rule.
- If it's a Critical Gate domain (forensic, governance-type), add it to the Global Conflict Arbitration table.

**Before adding a new Skill:**
- Decide: is it a workflow skill (belongs in `04_Skills_Reference_v_0.0.md`) or an analytical lens skill (its own standalone file)? Don't create a third pattern.
- If it depends on specific Knowledge domains, add that dependency to `AI_Dependency_Map_v_0.0.md` §5 (the Skill↔Knowledge matrix) in the same edit.

---

## 5. Naming Conventions

- Knowledge domains: `Domain_NN_Name.md` — two-digit number, sequential, no gaps.
- Skills (workflow): live inside `04_Skills_Reference_v_0.0.md`, numbered `Skill NN`.
- Skills (analytical lens): `AI_Name_Skill.md` — descriptive name, no numbering.
- Core engines/standards: `AI_Name_vX.Y.md` — version in the filename, matching the internal Document Information footer exactly. **A mismatch between filename version and internal version is a defect** (this happened once with `AI_Module_Registry` — fixed; don't reintroduce it).
- One skill or domain = one file. If a second copy of the same skill/domain content exists anywhere in the repository, one of them is wrong — resolve immediately, don't keep "just in case."

---

## 6. Frozen Core Amendment Protocol

To change a frozen document's actual logic (not just add a section):

1. State the explicit reason for the change.
2. Bump the version number.
3. Update this file's Section 3 (Frozen Architecture) list if scope changed.
4. Add a changelog entry to `CHANGELOG.md` (if present) or the file's own Document Information footer.
5. Re-check every dependent file per the Dependency Map.

Incidental edits made "while working on something else" are not permitted on frozen files — if you notice something wrong, log it and fix it deliberately, don't drift it in passing.

---

## 7. Synchronization Rules (Summary)

Full rules: `AI_Architecture_Overview_v_0.0.md` §13B (Rules S-01 through S-12). The ones that matter most day-to-day:

- **S-03 / S-12 — Object Schema Lock.** Field definitions live in one place (`AI_Object_Field_Reconciliation_v_0.0.md`), mirrored — never redefined — in `AI_Data_Object_Standard` and `AI_Object_Schemas`.
- **S-10 — Single Pipeline Source.** Sequence lives only in `AI_Pipeline_Specification_v_0.0.md`.
- **S-11 — Naming Alias Rule.** A formal schema name (e.g., `QualityAuditObject`) and its prose short form (`AuditObject`) are the same object — don't treat them as two.

---

## 8. Dependency Update Rules

When any engine's input/output contract changes:
1. Update that engine's Section 8A contract entry in `AI_Architecture_Overview_v_0.0.md`.
2. Check `AI_Dependency_Map_v_0.0.md` for any graph edge that assumed the old contract.
3. Check `AI_Pipeline_Specification_v_0.0.md` §4 (Object Flow Validation table) for consistency.

---

## 9. Registry Update Requirements

Adding a Module or Framework:
- Must include complete metadata (ID, name, category, applicable domains, compatible skills, input/output objects, version).
- Must not duplicate an existing registry entry.
- Framework additions go in `AI_Framework_Registry_v_0.0.md`; Module additions go in `AI_Module_Registry_v_0.0.md`.

---

## 10. Validation Checklist Before Any Commit

Before treating a change as final, confirm:

- [ ] No object's field list was edited in only one of the two schema files
- [ ] No pipeline diagram was added or edited outside `AI_Pipeline_Specification_v_0.0.md`
- [ ] Every new/edited file's internal version matches its filename version
- [ ] Every new Knowledge domain is indexed in `00_Index.md`
- [ ] Every new Skill is either merged into `04_Skills_Reference_v_0.0.md` or added as one standalone lens file — not both
- [ ] No file contains corrupted or escaped markdown (check for stray `\*`, `\_`, `\#` characters — this happened once with `AI_Framework_Registry`, fixed)
- [ ] Every cross-reference to another file uses that file's current filename and version, not a stale one
- [ ] Constitutional compliance (SEBI disclaimer, CIO Authority Rules) is untouched

---

## 11. Review Process

Single-maintainer repository — no formal review board. But every change should pass through the same self-audit discipline used to build this system: state the change, check its dependents, verify no contradiction was introduced, then apply.

---

# Document Information

**Document:** PROJECT_INSTRUCTIONS.md
**Version:** v_0.0
**Status:** Production Ready
**Companion file:** README.md

# END OF DOCUMENT

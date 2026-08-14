# AI_Knowledge_Mode_Architecture_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Cross-Cutting Governance Document
**Priority:** High
**Role:** Resolves Investment-Horizon Scope Contradiction in Knowledge Layer
**Paste Target:** Knowledge_01/00_Index.md — replaces the "Built for" scope line with the mode framework below

---

# 1. Purpose

Resolves Forensic Audit MV-06: the Knowledge Index declared itself "Built for Micro/Small-Cap Swing (2-10 day) & Positional Trading," while the Constitution (`AI_Project_Instructions_v_0.0.md`, Principle 8: Long-Term Compounding; Principle 29: Mode-Appropriate Depth) positions IERL as an institutional long-term research system. This created an epistemic mismatch — a long-horizon query would load knowledge packs optimized for short-horizon trading.

This document introduces a formal multi-mode framework so the same 43-domain knowledge layer serves every investment horizon the Constitution supports, without contradiction.

---

# 2. Root Cause

The Knowledge Index was originally authored for a swing/positional use case and never updated when the Constitution was generalized to institutional scope. The 43 domains themselves are horizon-agnostic (e.g., Domain 2 — Financial Statements applies equally to a 5-day trade and a 5-year hold) — only the *selection and weighting* of domains needs to vary by mode. No new Knowledge Pack content is required to fix this; only a selection layer.

---

# 3. Mode Framework

Five modes are defined, each mapping to a specific domain selection profile. Mode selection is driven by the Task Orchestrator's classification of investment horizon (already a natural output of intent interpretation — no new input required from the user beyond what's already asked).

| Mode | Horizon | Primary Domains |
|---|---|---|
| **Mode A — Institutional / Long-Term** | 1+ years, compounding thesis | Tier 0 (Domains 1–23, full) + relevant sector Tier 2 |
| **Mode B — Swing / Positional** | 2 days – 2 months | Domains 7 (Technical), 30 (Swing Patterns), 40 (Screening), 43 (Portfolio Rules) + relevant sector Tier 2 |
| **Mode C — Deep Fundamental** | 6 months – 3 years, single-company deep dive | Full Tier 0 + relevant Tier 1 + relevant Tier 2 + relevant Tier 3 |
| **Mode D — Hybrid** | Position trade with fundamental backstop (e.g., "swing entry, but only in fundamentally sound names") | Domains 6, 8, 24 (fundamental screen) + Domains 7, 30, 40 (technical/swing execution) |
| **Mode E — Screening / Idea Generation** | No single horizon; broad universe scan | Domain 40 (Screening) + Domain 6 (Fundamental) at summary depth only — deep domains loaded only for shortlisted candidates in a follow-up task |

---

# 4. Mode Selection Logic

```
Task Orchestrator classifies TaskObject.InvestmentHorizon
    ↓
    < 2 months, single trade idea           → Mode B
    < 2 months, but requires quality filter → Mode D
    6 months - 3 years, single company      → Mode C
    1+ years, portfolio/compounding thesis  → Mode A
    No horizon stated, multi-stock scan     → Mode E
    Horizon ambiguous                        → ClarificationRequest
                                                (per Task Orchestrator
                                                 failure protocol)
    ↓
ResearchPlanObject.KnowledgeMode = [selected mode]
    ↓
Intelligence Engine selects domains per Section 3 table for that mode
```

**Ambiguity Rule:** If the user's request does not state or imply a horizon (e.g., "should I buy this stock?" with no further context), the Task Orchestrator does not default silently to Mode B (the original swing-only assumption). Instead, per Task Orchestrator's existing ClarificationRequest protocol, horizon is confirmed before mode selection — closing the exact silent-mismatch risk identified in MV-06.

---

# 5. Constitutional Alignment Check

| Constitutional Principle | How This Framework Satisfies It |
|---|---|
| Principle 8 — Long-Term Compounding | Mode A exists as a first-class, fully-resourced mode — not a fallback |
| Principle 29 — Mode-Appropriate Depth ("a swing-trade call must never masquerade as long-term conviction") | Every `OutputObject` (per `AI_Output_System_v_0.0.md`) now carries `KnowledgeMode` in its metadata, and the Output System's Investment Thesis section explicitly states the mode/horizon the analysis was conducted under — preventing horizon conflation at the output stage |

---

# 6. Required Edit to Knowledge Index — SUPERSEDED

> **This section is superseded by `00_Index.md` v_0.0 (Phase 5).** The Knowledge Index was updated directly to 24 domains with its own scope statement — do not apply the edit below. Kept only for historical record of the original fix design. Sections 1–5 above (the mode framework itself) remain valid and in effect.

**Replace** in `Knowledge_01/00_Index.md`:
```
Built for: Micro/Small-Cap Swing (2-10 day) & Positional
(1 week-2 month) Trading, Stock-Finding.
```

**With:**
```
Built for: Multi-mode institutional and trading research —
see AI_Knowledge_Mode_Architecture_v_0.0.md for the five supported
modes (Institutional/Long-Term, Swing/Positional, Deep Fundamental,
Hybrid, Screening). Mode is selected per-task by the Task
Orchestrator based on stated or clarified investment horizon.
```

The existing Global Conflict Arbitration rules within the Index (e.g., "cash-based evidence outranks accrual profit," "forensic/governance flags override everything") are **mode-independent** and require no change — they apply identically across all five modes.

---

# 7. Self-Audit

- ✓ No new Knowledge Pack content required — existing 43 domains are reused, only selection logic is added
- ✓ Consistent with Task Orchestrator's existing ClarificationRequest failure protocol — no new failure path introduced
- ✓ Consistent with `AI_Output_System_v_0.0.md` §12 (Formatting Rules already ties format to depth tier; this adds `KnowledgeMode` as a parallel, non-conflicting metadata field)
- ✓ Directly resolves MV-06 without touching Constitution, Architecture, or any engine's core logic

---

# Document Information

**Document:** AI_Knowledge_Mode_Architecture_v_0.0.md
**Version:** v_0.0
**Paste Into:** Knowledge_01/00_Index.md (replace scope line, Section 6 above)
**Resolves:** MV-06 (Forensic Audit — Knowledge Index Scope Tension)

# END OF DOCUMENT

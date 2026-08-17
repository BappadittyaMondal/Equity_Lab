# AI Comparison Engine Skill v1.0

**Status:** Production Ready
**Category:** New Skill (genuinely missing capability, confirmed by institutional audit — Comparison Engine scored 52/100 with "no dedicated workflow")
**Goal:** Comparison Engine 52 → 90
**Action:** Upload as new standalone skill file — reuses all existing data/objects, adds zero new schema

---

## Why This File Exists

The audit confirmed: comparison capability existed only as unstructured general reasoning — no defined workflow, despite all the underlying data (ratios, valuation, quality scores) already being available via `Screener_Field_Glossary`, `Domain_04_Financial_Ratios`, and the Forensic/Risk skills. This file is a **workflow wrapper**, not a new data source.

---

## Trigger Keywords

"compare," "vs," "versus," "which is better," "how does X stack up against Y," "relative valuation," "peer comparison"

---

## Comparison Types Supported

### 1. Company vs Company

```
Step 1 — Pull core fundamentals for both (via Screener Field Glossary fields)
Step 2 — Run Forensic Accounting red-flag check on both independently
         (a company that "wins" on growth but fails red-flag checks is
         not a fair winner — apply CIO Authority Rule: forensic flag
         caps conviction regardless of comparative growth)
Step 3 — Compare across 5 fixed dimensions:
         Growth | Profitability (ROCE/ROE) | Balance Sheet Strength |
         Valuation | Capital Allocation Quality
Step 4 — State which company wins each dimension explicitly — do not
         average into one score without showing the breakdown
Step 5 — Decision Summary: overall lean, with the single most decisive
         differentiating factor named explicitly
```

### 2. Company vs Sector

```
Step 1 — Pull sector averages/benchmarks from the relevant Sector
         Quick-Reference row or dedicated sector skill (Banking, NBFC, etc.)
Step 2 — Compare company's Key Metrics (per that sector's specific
         metric list — e.g., NIM for Banking, not generic ROE) against
         sector norms
Step 3 — Classify: Sector Leader / In-Line / Laggard, with the metric
         gap stated numerically
```

### 3. Company vs Index

```
Step 1 — Compare Returns (per Screener Glossary period fields: 1Y/3Y/5Y)
         against the relevant index return for the same period
Step 2 — State whether outperformance is Alpha (business-driven, check
         if fundamentals improved commensurately) or Beta-driven
         (broad market/sector rally lifted the stock without matching
         fundamental improvement — check via Domain 44 macro cross-reference)
```

### 4. Growth vs Value Classification

```
A stock is classified Growth if: Sales Growth 3Y >15% AND PE > Industry PE
A stock is classified Value if: PE < Industry PE x 0.8 AND ROCE > 12%
A stock is classified Blend if it fits neither cleanly — state why

This reuses Library 9 (Valuation) thresholds already established in the
Multibagger Quick Screen — no new thresholds invented.
```

### 5. Quality / Risk / Valuation / Capital Allocation / Competitive Advantage Comparison

```
For any two companies, generate a single comparison table:

| Dimension | Company A | Company B | Winner |
|---|---|---|---|
| Business Quality (Domain 6) | | | |
| Governance (Domain 8) | | | |
| Forensic Risk (Forensic Accounting Skill) | | | |
| Valuation (PE/PB/EV-EBITDA vs sector) | | | |
| Capital Allocation (ROCE trend, per Multibagger Module 0B Category 4) | | | |
| Competitive Moat (Domain 25 - Moat & Competitive Advantage) | | | |

Never declare an overall winner without showing this breakdown table —
a single blended score hides which dimension actually decided it.
```

---

## Decision Summary Standard (Required for Every Comparison)

Every comparison output must end with:
```
Bottom Line: [1-2 sentences, plain language]
Decisive Factor: [the single dimension that most drove the conclusion]
Where They're Close: [any dimension that was near-tied, stated honestly]
Confidence: [per Confidence Standard vocabulary — comparisons with
             incomplete data on one side should show reduced confidence,
             not be silently treated as fully resolved]
```

---

## Self-Audit

- ✓ No new data objects introduced — uses existing `ResearchObject`, `DecisionObject` fields
- ✓ No new numeric thresholds invented — reuses Multibagger Quick Screen, Valuation Library 9, and sector-specific metrics already defined
- ✓ Forensic/CIO Authority Rules explicitly carried into comparison logic — a company cannot "win" a comparison by outscoring on growth while failing a forensic gate

---

**Document:** AI_Comparison_Engine_Skill.md
**Version:** 1.0
**Resolves:** Confirmed Comparison Engine gap (Institutional Audit, Section 10)

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Comparison Engine Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


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

## Pre-Flight Requirements

Before running any comparison, the user must supply the following minimum data. Derived from the 5 comparison types and 6 dimensions defined above.

```
□ Company A name, ticker, and as-of date for all financial data
□ Company B name, ticker, and as-of date for all financial data
  (or sector benchmark / index name for Company vs Sector / Company vs Index comparisons)

DIMENSION DATA REQUIRED:
□ Growth: Revenue CAGR (3 years) and PAT CAGR (3 years) for both entities
□ Profitability: ROCE % and ROE % (most recent full year) for both entities
□ Balance Sheet: Debt/EBITDA and Current Ratio for both entities
□ Valuation: P/E, P/B, EV/EBITDA — current vs sector average — for both entities
□ Capital Allocation: ROCE trend (3 years) for both entities
□ Moat: Domain 25 moat type classification + trajectory (Widening / Holding / Eroding)

FORENSIC PRE-SCREEN (Domain 24):
□ CFO/PAT ratio for both entities (3-year trend)
□ Promoter pledge % for both entities
□ Any active auditor change or related-party flag for both entities

MISSING DATA RULE: If financial data is available for Company A but not Company B
(or vice versa), declare the data gap explicitly in the output. Do NOT fill missing
data with estimates, assumptions, or industry averages without labeling them as such.
Confidence must be reduced when a comparison is asymmetric in data quality.
```

---

## Standardized Comparison Output Template

Every comparison output must use this format exactly. Do not produce free-form narrative comparisons without completing this template first.

```
═══════════════════════════════════════════════════════════════════════
COMPARISON REPORT
Company A: [Name / Ticker] | Company B: [Name / Ticker]
Comparison Type: [Company vs Company | Company vs Sector | Company vs Index | Growth-Value]
As-of Date: [DD/MM/YYYY] | Data Vintage: [State period for each entity's data]
═══════════════════════════════════════════════════════════════════════

FORENSIC PRE-SCREEN (per Domain 24 — Hard Gate):
  Company A: [PASS / CAUTION / FAIL + reason if not PASS]
  Company B: [PASS / CAUTION / FAIL + reason if not PASS]
  ⚠️ Gate Rule: A company with a FAIL verdict cannot be declared a winner
     regardless of scorecard performance in any other dimension.

DIMENSION SCORECARD:
| Dimension | Company A | Company B | Winner |
|---|---|---|---|
| Growth (Revenue CAGR 3yr / PAT CAGR 3yr) | | | |
| Profitability (ROCE % / ROE %) | | | |
| Balance Sheet (Debt/EBITDA / Current Ratio) | | | |
| Valuation (PE / PB / EV-EBITDA vs sector avg) | | | |
| Capital Allocation (ROCE trend 3yr) | | | |
| Moat (Domain 25 — type + trajectory) | | | |

SCORECARD TALLY:
  Company A wins: [X of 6 dimensions]
  Company B wins: [Y of 6 dimensions]
  Near-tied: [list any dimensions where gap < 10%]

BOTTOM LINE: [1–2 sentences, plain language verdict]
DECISIVE FACTOR: [The single dimension that most drove the conclusion — named explicitly]
WHERE THEY ARE CLOSE: [Any near-tied dimension, stated honestly]
DATA GAPS: [List any missing data that limited comparison quality, or "None"]
CONFIDENCE: [High / Moderate / Low]
  Basis: [1 sentence explaining what limits or supports confidence]
═══════════════════════════════════════════════════════════════════════
```

---

## Non-Negotiable Rules for Comparison

**Rule 1 — Forensic gate failure caps the winner verdict:**
A company that fails the Domain 24 Forensic Pre-Screen (2+ flags from different categories) cannot be declared a winner in this comparison, regardless of how strongly it leads in growth, valuation, or any other dimension. This is the CIO Authority Rule already embedded in the existing Company vs Company workflow above: "a company that 'wins' on growth but fails red-flag checks is not a fair winner."

**Rule 2 — Never declare a winner without showing the dimension scorecard:**
A bottom-line verdict delivered without completing the 6-dimension scorecard is not a valid comparison output. The scorecard breakdown is mandatory — it shows which dimensions drove the conclusion and prevents a single compelling metric (e.g., very high revenue growth) from masking weakness in governance or valuation.

**Rule 3 — Confidence must reflect data asymmetry:**
If meaningful financial data is available for Company A but missing for Company B (or vice versa), the comparison confidence must be stated as Low or "Data Incomplete" — not Moderate or High. A one-sided data comparison cannot support a high-confidence verdict, regardless of how decisive the available data appears.

**Rule 4 — Use sector-specific metrics, not generic defaults:**
As stated in the Company vs Sector comparison workflow above, sector-specific key metrics must be used where applicable. For Banking: NIM, GNPA, Cost-to-Income, CASA ratio. For Insurance: Embedded Value, VNB margin. Applying generic P/E or ROCE comparisons to a bank without adjusting for sector-specific metrics produces a misleading comparison.

**Rule 5 — State the decisive factor — do not blend into a single score:**
The Comparison Report requires an explicit "Decisive Factor" field. Do not replace this with a weighted average score or a single blended number. Averaging conceals the dimension-by-dimension trade-off that is the entire value of a structured comparison. The decisive factor must be a named, specific dimension (e.g., "Capital Allocation — Company A's ROCE has improved from 14% to 22% over 3 years while Company B's has declined from 18% to 11%").

---

**Document:** AI_Comparison_Engine_Skill.md  
**Version:** 1.1 (expanded with Pre-Flight, Output Template, Non-Negotiable Rules)

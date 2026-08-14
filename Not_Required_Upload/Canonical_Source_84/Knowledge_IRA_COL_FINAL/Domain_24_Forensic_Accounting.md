<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Forensic Accounting  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 24 — Financial Quality & Forensic Accounting
Version: v_0.0 | Status: Production Ready (New Domain)

## Purpose
Detect earnings manipulation, aggressive accounting, and fraud risk before capital is committed — critical for micro/small-cap investing where disclosure quality is inconsistent and promoter integrity varies widely. This is the single highest-leverage screen for avoiding permanent capital loss in small-cap investing.

## Core Principle
Profits can be manipulated. Cash is much harder to fake. Assume every reported number is a claim to be verified, not a fact to be accepted.

## Quantitative Forensic Models

**1. Beneish M-Score** — Statistical model estimating probability of earnings manipulation using 8 variables (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA). Score > -1.78 signals elevated manipulation risk.

**2. Piotroski F-Score** — 9-point financial strength score (profitability, leverage/liquidity, operating efficiency). Score ≥7 = strong; ≤3 = weak. Widely used as a small-cap quality filter.

**3. Altman Z-Score** — Bankruptcy/distress prediction combining working capital, retained earnings, EBIT, market value of equity, and sales, each scaled by total assets. Z < 1.8 = distress zone; Z > 3.0 = safe zone.

**4. Sloan Accrual Ratio** — (Net Income – Operating Cash Flow) / Total Assets. High accruals relative to cash flow predict future earnings disappointment — a core small-cap quality filter.

## Core Red Flag Categories

**1. Earnings Quality**
- Cash Conversion Ratio = CFO / PAT, sustained below 0.7-0.8 is a warning.
- Frequent "exceptional items" normalizing weak core operations.
- Revenue growth without matching receivables discipline (DSO rising faster than sales).

**2. Balance Sheet Red Flags**
- Rapid, unexplained growth in "Other Assets," "Loans & Advances," or intercorporate deposits.
- Goodwill/intangibles ballooning post-acquisition without impairment testing.
- Large contingent liabilities disclosed in fine print but not discussed in MD&A.

**3. Promoter & Governance Forensics**
- Rising promoter pledge % — the single most dangerous small-cap signal; pledged shares can trigger forced selling in a downturn.
- Frequent preferential allotments to promoters at low valuation.
- Auditor resignation mid-year, or repeated small/unknown audit firm changes.
- Complex web of unlisted related entities receiving loans/guarantees from the listed company.

**4. Revenue Red Flags**
- Revenue growth concentrated in Q4 (channel stuffing pattern) not seen in other quarters.
- Large related-party sales inflating topline.
- Sudden unexplained margin expansion without cost/pricing rationale.

## Application Framework (Small/Micro-Cap Specific)
1. **Pledge check first** — any promoter pledge >25% is an automatic caution flag for swing/positional entries.
2. **CFO/PAT trend over 3 years**, not one year — one bad year can be explained; three years of divergence cannot.
3. **Cross-check auditor tenure and size** — Big-4/reputed regional auditor vs. unknown small firm is a meaningful signal in micro-caps.
4. **Screen for related-party revenue %** disclosed in notes — anything above 10-15% of revenue needs scrutiny.
5. Run Piotroski F-Score as a fast pre-screen before deeper qualitative work — cheap to compute, high signal for eliminating weak candidates from a large watchlist.

## Worked Example
A micro-cap shows PAT growth of 45% YoY, but CFO actually declined. Notes reveal trade receivables grew 60% and a new related entity (promoter-linked) accounts for 20% of incremental revenue. Auditor changed twice in 18 months. Individually explainable; together this is a textbook manipulation cluster — pass regardless of how attractive the chart looks.

## Red Flags Checklist (Quick Screen)
- Promoter pledge rising or >25%
- CFO/PAT < 0.7 for 2+ consecutive years
- Auditor changed in last 12 months without clear reason
- Related-party revenue/loans >10% of base
- Beneish M-Score > -1.78
- Piotroski F-Score ≤ 3
- Frequent preferential allotments at discount to market

## AI Trigger Keywords
is this fraud, forensic, manipulation, red flag, promoter pledge, auditor change, M-Score, F-Score, Z-Score, fake profit, accounting quality, is this safe to buy.

## Cross-Domain Links
→ Domain 3 (accounting policy mechanics) · Domain 8 (governance red flags, qualitative) · Domain 27 (micro-cap specific risk overlay) · Domain 9 (Financial/Governance Risk).

## Conflict Rule
Forensic red flags override every other positive signal (chart pattern, valuation cheapness, sector tailwind) — this domain acts as a hard gate, not a weighted factor, for small/micro-cap entries.

## Universal Rule Applied
Never conclude fraud from a single indicator. Require a cluster of 2+ independent red flags before assigning high manipulation risk, and always disclose which specific indicators triggered the flag.

---

## Forensic Gate — 12-Point Mandatory Execution Checklist

Complete before approving any small/micro-cap stock idea for investment or swing entry. This checklist operationalizes the red flag categories above into a structured gate.

```
FORENSIC GATE — 12-POINT MANDATORY CHECKLIST
Complete before approving any small/micro-cap stock idea.

EARNINGS QUALITY (Points 1–4):
□ 1. CFO/PAT ratio (3-year trend): [____] — Target: ≥ 0.7 for all 3 years
       Flag: Below 0.7 for 2+ consecutive years = earnings quality concern.
□ 2. DSO trend (Days Sales Outstanding, 3 years): [____]
       Flag: Receivables growing materially faster than sales growth rate.
□ 3. Exceptional items frequency: [____]
       Flag: "One-off" items appear in 2 or more consecutive years.
□ 4. Beneish M-Score: [____] — Source: 8-variable statistical model
       Flag: Score > -1.78 = elevated manipulation risk.

BALANCE SHEET INTEGRITY (Points 5–8):
□ 5. "Other Assets" / "Loans & Advances" 3-year growth: [____]
       Flag: Unexplained growth > 30% with no business rationale disclosed.
□ 6. Goodwill / Intangibles post-acquisition: [____]
       Flag: No impairment testing disclosed in notes / MD&A.
□ 7. Contingent liabilities as % of net worth: [____]
       Flag: Contingent liabilities > 20% of net worth, undiscussed in MD&A.
□ 8. Piotroski F-Score: [____] — 9-point financial strength model
       Flag: Score ≤ 3 = structurally weak balance sheet.

GOVERNANCE INTEGRITY (Points 9–12):
□ 9. Promoter pledge % (current): [____]
       Hard Stop: Any promoter pledge > 25% = automatic swing/entry caution.
□ 10. Auditor profile: [____]
       Flag: Auditor changed in last 12 months without stated reason, or
       small/unknown firm auditing a mid-cap+ company.
□ 11. Related-party revenue / loans as % of total: [____]
       Flag: Related-party revenue or loans > 10% of revenue base require
       independent verification of arm's-length pricing.
□ 12. Preferential allotments at discount: [____]
       Flag: Any preferential allotment to promoter entities at discount to
       market price in the last 3 years.

GATE RESULT:
  □ PASS — Proceed to investment analysis (0–1 flags, all in same category)
  □ CAUTION — Elevated scrutiny required (1 flag in different categories)
  □ FAIL — Hard Exit / Do not commit capital (2+ flags from different categories)

GATE RULE: 2+ independent flags from DIFFERENT categories = HIGH manipulation
risk cluster. This is the single most important rule — one flag in isolation may
be explainable; a cluster across Earnings + Balance Sheet + Governance cannot.
```

---

## Worked Forensic Cluster Example — 12-Point Gate Applied

Using the existing worked example (micro-cap with 45% PAT growth, declining CFO, rising receivables, related-party revenue, and auditor changes):

```
Step 1 — Point 1 (CFO/PAT): PAT grew 45% YoY but CFO DECLINED.
          CFO/PAT ratio deteriorated below 0.7. → FLAG RAISED: Point 1.

Step 2 — Point 2 (DSO): Trade receivables grew 60% vs revenue growth ~35%.
          Receivables outpacing sales materially. → FLAG RAISED: Point 2.

Step 3 — Point 11 (Related-Party Revenue): New promoter-linked entity now
          accounts for 20% of incremental revenue — well above the 10% threshold.
          → FLAG RAISED: Point 11.

Step 4 — Point 10 (Auditor Change): Auditor changed twice in 18 months with
          no stated rationale. → FLAG RAISED: Point 10.

Step 5 — Cluster Assessment: Flags 1, 2 = Earnings Quality category.
          Flags 10, 11 = Governance category.
          Two independent categories flagged simultaneously.

Step 6 — GATE RESULT: FAIL — Hard Exit. Do not commit capital regardless
          of how attractive the chart pattern, sector tailwind, or valuation
          appears. This is a textbook manipulation cluster.
```

---

## Forensic Gate — Conflict Resolution Rules

**Rule 1 — Forensic flags override all positive signals:**  
A forensic FAIL verdict overrides a positive technical chart pattern, cheap valuation, strong sector tailwind, or institutional buying — without exception. This is codified in `00_Index.md` Global Conflict Arbitration Rule #1: "Forensic red flags (24) and Governance red flags (8) override everything."

**Rule 2 — A single flag requires scrutiny, not automatic exit:**  
One isolated flag (e.g., CFO/PAT slightly below 0.7 for one year during a high-growth capex cycle) is a watch item, not a hard exit. Require a second independent flag from a different category before raising to CAUTION or FAIL. Never conclude fraud from a single indicator.

**Rule 3 — Positive stock price action does not reduce flag severity:**  
A rising stock price, recent mutual fund buying, or analyst upgrades do NOT reduce the risk associated with active forensic flags. Manipulation often occurs precisely when stock narratives are strongest. If the gate flags are present, they must be resolved with evidence (e.g., auditor explanation, CFO/PAT recovery for 2+ years) before the flag is cleared — not dismissed because price is rising.

---
End of Document — Domain 24

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
End of Document — Domain 24

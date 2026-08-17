# AI Forensic Accounting Skill
**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Universal — Applies to ALL company analyses regardless of sector

---

## CRITICAL AI INSTRUCTION

This skill executes **automatically and mandatorily** whenever any financial statement, annual report, quarterly result, or company analysis is requested. It is not optional. No investment opinion or recommendation may be issued without first completing the forensic accounting review. Forensic findings override all other positive signals.

**Governance overrides growth. Cash flow validates earnings. Transparency increases confidence.**

---

## Purpose

Detect accounting manipulation, earnings quality issues, governance concerns, and financial red flags BEFORE forming any investment view. This skill protects against fraudulent, manipulative, or misleading financial disclosures that are common in Indian listed markets.

---

## Objectives

Identify and score:
- Earnings manipulation and revenue fabrication
- Accounting irregularities and policy changes
- Weak cash conversion and working capital stress
- Governance failures and promoter concerns
- Financial statement inconsistencies
- Aggressive accounting and capitalisation
- Capital allocation concerns and value destruction
- Hidden financial and contingent liabilities

---

## Pre-Flight Requirements

Before executing, confirm:
```
□ Latest 3 years Annual Reports available (or at minimum 5 years P&L data)
□ Quarterly results for last 8 quarters
□ Cash Flow Statement (not just P&L)
□ Balance Sheet with full notes
□ Auditor's Report and CARO (Companies Auditor's Report Order)
□ Related Party Transaction disclosures
□ Contingent Liability schedule
□ Shareholding pattern (last 4 quarters)
```
If Cash Flow Statement is unavailable → Tier 2 Gap Protocol. Earnings quality cannot be confirmed.

---

## Analysis Module 1 — Revenue Quality

### Step 1.1 — Revenue Recognition Policy
- Read the accounting policy note on revenue recognition
- Flag if policy changed in last 3 years (ask: what changed and why?)
- Check for IND-AS 115 compliance (IFRS 15 equivalent)
- Identify if revenue is point-in-time or over-time — which is appropriate for this business?

### Step 1.2 — Revenue Pattern Analysis
Check for:
```
□ Sudden revenue spike (>30% in one year without clear business reason)
□ Q4 heavy revenue concentration (channel stuffing signal)
□ Revenue growth significantly outpacing sector peers
□ Revenue from new geographies/segments suddenly dominating
□ Deferred revenue declining sharply (pull-forward recognition)
□ Revenue recognised but cash not received (ballooning debtors)
```

### Step 1.3 — Customer and Channel Quality
```
□ Customer concentration >30% in single customer = HIGH RISK
□ Related-party revenue as % of total revenue (benchmark: <5% is safe)
□ Export revenue: verify with DGFT data where possible
□ One-time income included in revenue (should be below-the-line)
□ Government receivables: high risk if PSU-dependent
```

### Step 1.4 — Revenue Red Flags Scoring
| Flag | Severity |
|------|----------|
| Revenue spike >50% with no capacity addition | CRITICAL |
| Q4 revenue >40% of annual | HIGH |
| Debtors growing 2x faster than revenue | HIGH |
| Related-party revenue >15% of total | HIGH |
| Revenue recognition policy change | MEDIUM |
| Customer concentration >50% | HIGH |

---

## Analysis Module 2 — Profit Quality

### Step 2.1 — EBITDA Quality Assessment
```
□ Adjust EBITDA for:
   → One-time gains (asset sales, insurance claims, write-backs)
   → Non-operating income included in EBITDA
   → Employee stock option costs excluded
   → Lease adjustments (IND-AS 116 impact)
□ Reported EBITDA vs. Adjusted EBITDA: gap >10% = flag
□ EBITDA margin: Is it sustainable vs. 5-year average?
□ Operating leverage check: Revenue grew X% → EBITDA should grow proportionally
```

### Step 2.2 — Below-the-Line Items
```
□ "Other Income" as % of PBT — Benchmark: <10% healthy, >25% = RED FLAG
□ Exceptional items frequency: >2 times in 5 years = pattern, not exception
□ Deferred Tax Asset creation: large DTAs may be aggressive
□ Depreciation rate: is company under-depreciating to inflate profit?
□ Amortisation of intangibles: how fast? Any sudden extension?
```

### Step 2.3 — Margin Sustainability Test
```
Benchmark against:
→ 5-year average OPM
→ Closest 3 peers (same sub-sector)
→ Raw material cost trends

If OPM has expanded >500bps in 2 years:
→ Is this operating leverage? (Revenue grew faster — acceptable)
→ Is this cost reduction? (Verify employee/material cost trends)
→ Is this accounting? (Check capitalisation of costs)
```

---

## Analysis Module 3 — Cash Flow Quality (MOST CRITICAL)

### Step 3.1 — The Three-Layer Cash Test
```
Layer 1: Net Profit → Operating Cash Flow
  → OCF/PAT ratio: >80% = Excellent | 60–80% = Good | 40–60% = Caution | <40% = CRITICAL FLAG

Layer 2: Operating Cash Flow → Free Cash Flow
  → FCF = OCF − Maintenance CapEx
  → Growing PAT + Falling OCF = EARNINGS MANIPULATION SIGNAL

Layer 3: Free Cash Flow → Cash Returned to Shareholders
  → Dividends + Buybacks vs. FCF generated
  → Cash building without deployment = capital allocation concern
```

### Step 3.2 — Working Capital Cash Drain Analysis
```
□ Debtors: Days Receivable Outstanding trend (3 years)
   → Increasing DRO = cash trapped, potential revenue inflation
□ Inventory: Days Inventory Outstanding trend
   → Rising inventory + flat/falling revenue = demand weakness signal
□ Creditors: Days Payable Outstanding trend
   → Falling DPO = supplier pressure (working capital stress)
□ Cash Conversion Cycle = DRO + DIO − DPO
   → CCC deteriorating = business stress or manipulation
```

### Step 3.3 — Non-Cash Working Capital Test
```
If revenue grew 20% but:
→ Debtors grew 50% → Revenue may be booked but not real
→ Advances from customers fell → Pre-sales business under stress
→ Trade payables fell → Company losing supplier credibility
```

### Step 3.4 — Capital Expenditure Quality
```
□ Maintenance CapEx vs Growth CapEx — is company disclosing both?
□ CWIP (Capital Work in Progress) as % of Gross Block
   → CWIP >30% for >3 years without commissioning = RED FLAG
   → Sudden CWIP write-off = past capitalisation error admitted
□ CapEx claimed vs. physical asset addition: verify coherence
□ CapEx funded by: internal accruals (healthy) vs. debt (check returns)
```

---

## Analysis Module 4 — Balance Sheet Forensics

### Step 4.1 — Asset Quality Review
```
Receivables:
□ Gross vs. Net receivables (provision adequacy)
□ Ageing analysis: what % is >180 days?
□ Related-party receivables: amount and collectability

Inventory:
□ Raw material vs. WIP vs. Finished goods mix
□ Inventory write-offs: any in last 3 years?
□ Inventory vs. Revenue ratio trend

Investments:
□ What are the investments? (Subsidiaries, mutual funds, unlisted equity)
□ Valuation basis: cost or fair value?
□ Quoted investments: market value vs book value gap
□ Loans and advances to related parties: purpose and repayment history
```

### Step 4.2 — Intangibles and Goodwill
```
□ Goodwill impairment: has it been tested? When was last impairment taken?
□ Goodwill rising with no acquisition = RED FLAG (capitalising expenses?)
□ Brand/IP value: internally generated intangibles should not be on balance sheet
□ R&D capitalisation: % of R&D capitalised vs. expensed (higher capitalisation = aggressive)
□ Deferred Revenue: falling without corresponding revenue fall = premature recognition
```

### Step 4.3 — Debt Quality
```
□ Total Debt composition: secured vs. unsecured
□ Related-party loans: terms vs. market rate
□ Debt maturity profile: any major refinancing due in 12–24 months?
□ Interest coverage ratio: EBIT/Interest > 3x = comfortable | <1.5x = distressed
□ Debt covenants: any restrictions on operations or dividends?
□ Hidden debt: operating leases pre-IND-AS 116, supplier financing arrangements
□ Contingent liabilities: what triggers these and probability of crystallisation?
```

### Step 4.4 — Off-Balance Sheet Exposures
```
□ Corporate guarantees given to subsidiaries/associates
□ Letter of Credit and buyer's credit facilities
□ Forward contracts and hedging positions
□ Litigations: tax disputes, customer claims, labour disputes
□ Environmental liabilities
□ Operating lease commitments (note disclosures)
```

---

## Analysis Module 5 — Auditor and Governance Review

### Step 5.1 — Auditor Quality
```
□ Big 4 / Top 10 Indian firms = Higher credibility
□ Auditor tenure: >10 years same firm may indicate familiarity bias
□ Auditor change: was it voluntary rotation or forced? Was reason disclosed?
□ Joint audit: both firms' qualifications should be checked
□ Audit fee vs. non-audit fee ratio: high consulting fee from auditor = CONFLICT
```

### Step 5.2 — Audit Report Red Flags
```
□ Qualified Opinion: STOP. Understand the qualification fully before proceeding.
□ Emphasis of Matter: not a qualification but deserves full reading
□ CARO report: any adverse remarks on internal financial controls?
□ Key Audit Matters (KAM): read all KAMs — they signal what auditor worried about
□ Going Concern doubt: CRITICAL FLAG — immediate exit trigger
```

### Step 5.3 — Board and Governance Quality
```
□ Independent directors: are they truly independent? (check interlocking)
□ Audit committee: does it include financially qualified members?
□ Related party approval: are all RPTs approved by audit committee?
□ Whistle-blower policy: is it publicly disclosed?
□ Board meeting attendance: any director with <50% attendance = flag
□ Remuneration vs. profit: is MD/promoter salary growing faster than profit?
```

---

## Analysis Module 6 — Promoter and Ownership Analysis

### Step 6.1 — Promoter Holding Quality
```
□ Current promoter holding %: >50% preferable | <30% = concern
□ Direction of change: increasing (positive) or decreasing (negative)
□ Creeping acquisition vs. open market sale
□ Promoter buying at what price vs. CMP?
```

### Step 6.2 — Pledge Analysis
```
Pledge % Thresholds:
→ 0–10%: Low concern
→ 10–25%: Moderate concern — monitor
→ 25–50%: HIGH RISK — stock price fall can trigger margin call cascade
→ >50%: CRITICAL — potential forced selling, company in financial stress

Check:
□ Pledge trend: increasing or decreasing?
□ Purpose of pledge: working capital (some acceptable) vs. personal use (RED FLAG)
□ Lender identity: NBFC pledge = higher risk than bank pledge
```

### Step 6.3 — Insider Transaction Analysis
```
□ Director/promoter buying: within 6 months of positive news = legal concern
□ Director/promoter selling: timing vs. business announcements
□ ESOP grants: dilution impact and vesting conditions
□ Bulk/block deals: who sold, who bought, at what price?
□ MF/FII entry: is institutional interest rising or falling?
```

---

## Analysis Module 7 — Related Party Transactions

### Step 7.1 — RPT Volume and Nature
```
□ Total RPT as % of revenue: benchmark <10%
□ Types: Sales to subsidiaries | Purchases from promoter entities | Loans given/received
□ Pricing: are transactions at arm's length? How determined?
□ Business rationale: is the RPT commercially necessary?
□ Approval: board and shareholder approval documented?
```

### Step 7.2 — Subsidiary and Associate Analysis
```
□ Loss-making subsidiaries: how long? Plan to restructure?
□ Cash flows to subsidiaries: loans given vs. dividends received
□ Subsidiary revenue as % of consolidated vs. standalone — growing disproportionately?
□ Acquisition of promoter-owned businesses into listed company (related-party M&A)
□ Inter-company receivables: aged? Provision made?
```

---

## Analysis Module 7A — Piotroski F-Score Integration

Piotroski F-Score = Sum of 9 binary signals (0 or 1 each). Max = 9.

```
PROFITABILITY (4 signals):
F1: ROA > 0 this year                              → 1 if YES
F2: OCF > 0 this year                              → 1 if YES
F3: ROA higher than prior year                      → 1 if YES
F4: OCF/Total Assets > ROA (accruals quality)       → 1 if YES

LEVERAGE / LIQUIDITY (3 signals):
F5: Long-term debt ratio lower than prior year      → 1 if YES
F6: Current ratio higher than prior year            → 1 if YES
F7: No new shares issued in past year               → 1 if YES

OPERATING EFFICIENCY (2 signals):
F8: Gross margin higher than prior year             → 1 if YES
F9: Asset turnover higher than prior year           → 1 if YES

INTERPRETATION:
F-Score 0–2: WEAK — high short-selling candidate, avoid
F-Score 3–5: NEUTRAL — average; rely on other modules
F-Score 6–7: STRONG — improving fundamentals
F-Score 8–9: VERY STRONG — broad-based fundamental improvement

Note: F-Score is a SIGNAL, not a standalone decision. A manipulated company
can score high on reported numbers. Always confirm with Module 3 (Cash Flow).
```

## Analysis Module 7B — Tax Expense Cross-Check

Cash Tax vs. P&L Tax Verification:
```
Step 1: Tax Expense in P&L (Current Tax + Deferred Tax)
Step 2: Actual Tax Paid (Cash Flow Statement — "Income Tax Paid")
Step 3: Gap = P&L Tax − Cash Tax Paid

Normal gap: ±20% acceptable (timing differences)
Gap > 30% consistently: Company may be booking tax expense 
                         but not paying — possible profit inflation

Effective Tax Rate (ETR) Analysis:
ETR = Tax Expense / Profit Before Tax

India Corporate Tax Rate: 25.17% (new regime) or 22% (Sec 115BAA)
ETR significantly below applicable rate:
→ Check: Deferred tax asset creation (aggressive)
→ Check: Tax holiday benefits (80-IC, SEZ, etc.) — is it disclosed?
→ Check: Bogus deductions
→ ETR < 10% without disclosed reason = RED FLAG

MAT (Minimum Alternate Tax) credit accumulation:
→ Rising MAT credit balance with no utilisation prospect = trapped asset
```

## Analysis Module 7C — Inter-Statement Reconciliation Table

Run this mandatory cross-check before finalising any forensic review:

```
CHECK 1: Revenue reconciliation
P&L Revenue ←→ GST Returns (Form GSTR-1) — available for some sectors
If company discloses segment revenue: segments must sum to total

CHECK 2: Debt reconciliation
Balance Sheet Total Debt ←→ Cash Flow (Net Borrowings section)
Opening Debt + New Borrowings − Repayments = Closing Debt
Mismatch > 5% = accounting error or concealment

CHECK 3: Cash reconciliation
Opening Cash + OCF + ICF + FCF = Closing Cash
Any mismatch = error in one of the three statements

CHECK 4: Profit reconciliation
PAT in P&L ←→ Retained Earnings change in Balance Sheet
PAT − Dividends = Change in Retained Earnings ± Adjustments
Unexplained gap = possible restatement or error

CHECK 5: CapEx reconciliation
Cash Flow CapEx ←→ Gross Block change + CWIP change in Balance Sheet
CapEx (CF) = ΔGross Block + ΔCWIP (adjusting for disposals)
CapEx claimed >> asset addition = capitalising expenses as assets → RED FLAG
```

## Red Flag Master Register

### Automatic CRITICAL Flags (Any one = Immediate Concern)
```
❗ Going concern doubt expressed by auditor
❗ Auditor resignation without explanation
❗ Qualified opinion on financial statements
❗ Promoter pledge >60% of promoter holding
❗ OCF negative for 2 consecutive years while PAT is positive
❗ SEBI enforcement action against promoter in last 3 years
❗ Goodwill rising without corresponding acquisition
❗ Revenue growing >30% with no physical capacity addition and no customer evidence
```

### HIGH Severity Flags
```
⚠️ OCF/PAT ratio <40% for 2+ years
⚠️ Debtor days increasing >50% in 2 years
⚠️ CWIP stuck >3 years without commissioning
⚠️ Other income >25% of PBT
⚠️ Frequent equity dilution (>3 rounds in 5 years)
⚠️ Related-party transactions >15% of revenue
⚠️ Audit firm changed twice in 5 years
⚠️ Promoter consistently selling over 3+ years
⚠️ Contingent liabilities >50% of net worth
⚠️ Debt growing faster than revenue for 3 years
```

### MEDIUM Severity Flags
```
〽️ Accounting policy change (revenue recognition, depreciation, capitalisation)
〽️ Inventory growing faster than revenue
〽️ Gross margin unexpectedly stable despite input cost increases
〽️ Non-audit fee to auditor >30% of audit fee
〽️ Board independent director resigned mid-term
〽️ Exceptional income/loss 3+ years consecutively
〽️ Working capital days deteriorating vs. 5-year average
〽️ Tax rate consistently lower than statutory rate without explanation
```

### LOW Severity Flags (Monitor Only)
```
ℹ️ Single-quarter revenue concentration (seasonal business may justify)
ℹ️ Minor promoter pledge (<15%)
ℹ️ One-time exceptional item in single year
ℹ️ Subsidiary loss-making in its first 2 years
```

---

## Earnings Quality Score (EQS)

Score each dimension 0–10. Weighted total gives Final EQS.

| Dimension | Weight | Score (0–10) | Weighted Score |
|-----------|--------|--------------|----------------|
| Revenue Quality | 20% | | |
| Profit Quality | 15% | | |
| Cash Flow Quality | 25% | | |
| Balance Sheet Quality | 15% | | |
| Auditor & Governance | 10% | | |
| Accounting Conservatism | 10% | | |
| Promoter & RPT Quality | 5% | | |
| **FINAL EQS** | **100%** | | **/10** |

### EQS Interpretation
```
8.0 – 10.0  →  Excellent quality. Proceed with high confidence.
6.0 – 7.9   →  Good quality. Minor concerns — monitor flagged items.
4.0 – 5.9   →  Moderate quality. Multiple flags. Invest only with wide margin of safety.
2.0 – 3.9   →  Poor quality. Major structural concerns. Avoid or exit.
0.0 – 1.9   →  Critical quality failure. Hard avoid. Possible fraud signal.
```

---

## Final Output Format

```
FORENSIC ACCOUNTING REVIEW
Company: [Name] | Ticker: [NSE/BSE] | Period: [FY/Quarter]
Analyst: IERL Forensic Engine | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

CRITICAL FLAGS:         [Count] — [List any Critical flags]
HIGH FLAGS:             [Count] — [List]
MEDIUM FLAGS:           [Count] — [List]
LOW FLAGS:              [Count] — [List]

EARNINGS QUALITY SCORE: [X.X / 10] — [Excellent/Good/Moderate/Poor/Critical]

─────────────────────────────────────────────
MODULE 1 — REVENUE QUALITY:          [Score/10]
  Finding:    [Key finding in 2 sentences]
  Red Flags:  [List or "None"]
  
MODULE 2 — PROFIT QUALITY:           [Score/10]
  Finding:    [Key finding]
  Red Flags:  [List or "None"]
  
MODULE 3 — CASH FLOW QUALITY:        [Score/10]
  OCF/PAT:    [%] — [Assessment]
  FCF:        [Positive/Negative/Marginal]
  Finding:    [Key finding]
  Red Flags:  [List or "None"]
  
MODULE 4 — BALANCE SHEET QUALITY:    [Score/10]
  Finding:    [Key finding]
  Red Flags:  [List or "None"]
  
MODULE 5 — GOVERNANCE:               [Score/10]
  Auditor:    [Name | Opinion type | Changes]
  Promoter:   [Pledge % | Trend]
  Finding:    [Key finding]
  Red Flags:  [List or "None"]

─────────────────────────────────────────────
FORENSIC VERDICT:
  Clean Bill:       [YES / NO / CONDITIONAL]
  Key Strengths:    [2–3 items]
  Key Concerns:     [2–3 items]
  
  Investment Implication:
  → [PROCEED WITH CONFIDENCE / PROCEED WITH CAUTION / DO NOT INVEST
     PENDING CLARIFICATION / HARD AVOID]
  
  Required Before Investment:
  → [Specific disclosure or clarification needed, or "None"]
  
  Monitoring Points Post-Investment:
  → [What to watch each quarter]
```

---

## Universal Rules — Forensic Accounting

1. **Never rely only on reported earnings.** OCF always validates.
2. **Cash Flow is truth. P&L is an opinion.** When they diverge, trust the cash.
3. **Governance overrides growth.** A fraudulent fast-grower is worth zero.
4. **Multiple small flags may indicate a major structural problem.** 3 Medium flags = treat as 1 High flag.
5. **Transparency increases confidence.** Companies that explain their numbers proactively score higher.
6. **Consistency matters.** A company that changes accounting policies frequently is hiding something.
7. **Never assume errors are honest mistakes.** Investigate first, conclude later.
8. **Auditor emphasis of matter is never routine.** Read it with maximum suspicion.

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Indian Equity Research Lab*
*This skill integrates with: Skill 01 (Master Research), Skill 09 (Risk Auditor), Skill 15 (Pre-Investment Checklist)*
# Forensic Accounting Skill — Missing Red Flags Addendum v_0.0

**Paste Target:** AI_Forensic_Accounting_Skill.md — insert as new "Analysis Module 7D" after the existing "Analysis Module 7C — Inter-Statement Reconciliation Table," before "Red Flag Master Register"

**Scope check:** The existing skill already covers Revenue Quality, Profit Quality, Cash Flow, Balance Sheet, Auditor/Governance, Promoter/Pledge, and Related Party Transactions in depth. The four flags below are the ones genuinely absent — not a re-statement of what's already there.

---

## Analysis Module 7D — Capital Allocation & Structural Red Flags

### Flag 1 — Empire Building

**Detection:**
```
□ Net Block + CWIP growing faster than Sales over a 3-year window
□ ROCE flat or declining despite the above capex growth
□ Large acquisitions completed with no visible integration progress
  (stagnant combined-entity margins 2+ years post-acquisition)
```
**Meaning:** Management is expanding the asset base without translating it into earnings — a sign capital is being deployed for scale rather than shareholder value.
**Severity:** High
**AI Action:** Reduce Capital Allocation score (per Skill scoring framework); flag explicitly in output rather than let strong revenue growth mask it.

### Flag 2 — Customer/Supplier Concentration

**Detection:** Requires annual report disclosure — not derivable from standard screener fields.
```
□ Single customer >25% of revenue, OR top-3 customers >50% of revenue
□ Single supplier >30% of raw material/input purchases with no disclosed alternative
```
**Meaning:** Revenue or margin resilience depends on a small number of relationships outside the company's control.
**Severity:** Medium (High if the concentrated counterparty is itself financially stressed)
**AI Action:** Flag as a monitoring item; state explicitly if annual report data needed for this check was not provided.

### Flag 3 — Capacity Utilisation Risk

**Detection:**
```
□ Large capex cycle completed (per Flag 1 pattern) but Sales growth has not
  followed within 2 years of capacity coming online
□ Asset Turnover Ratio declining post-capex
```
**Meaning:** New capacity isn't finding demand — a leading indicator that the growth thesis behind the capex may not materialize.
**Severity:** Medium, escalates to High if capacity has been idle >2 years
**AI Action:** Cross-reference with the relevant sector's demand cycle (see sector-specific knowledge domain) before concluding — some sectors have long capacity-ramp lead times by nature.

### Flag 4 — Frequent Equity Dilution

**Detection:**
```
□ Number of Equity Shares increasing year-over-year without a
  corresponding acquisition or growth justification
□ EPS growth materially weaker than PAT growth (the gap is the dilution effect)
```
**Meaning:** Existing shareholders' claim on future earnings is being diluted, often to fund losses or growth that isn't self-funding.
**Severity:** Medium (High if dilution is recurring, annual, and unexplained)
**AI Action:** Always compute EPS growth alongside PAT growth — never report PAT growth as the growth headline without checking whether EPS confirms it.

---

## Self-Audit

- ✓ No overlap with existing Modules 1–7C (Revenue, Profit, Cash Flow, Balance Sheet, Auditor/Governance, Promoter/Pledge, RPT already cover their respective areas)
- ✓ These 4 flags specifically address capital allocation and structural risk, which the existing skill touches only indirectly (via Balance Sheet Forensics' capex quality check) without naming them as standalone flags

---

**Document:** Forensic_Accounting_Missing_Flags_Addendum_v_0.0.md
**Paste Into:** AI_Forensic_Accounting_Skill.md (new Module 7D, before Red Flag Master Register)

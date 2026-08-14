<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Fundamental Analysis Core Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Fundamental Analysis Core Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Core Toolkit — Reusable Ratio & Financial-Statement Analysis Engine

---

## CRITICAL AI INSTRUCTION

Every other skill in this library that says "check ROE," "assess margins," or "review the balance sheet" is implicitly relying on a consistent definition of how that ratio is calculated and interpreted — and inconsistency here silently corrupts every downstream skill. This skill exists to define, once, exactly how each core ratio is calculated, what a good/average/poor reading looks like BY SECTOR TYPE (a 12% ROE is poor for FMCG and excellent for a commodity cyclical at trough), and which ratios must always be read together rather than in isolation. A ratio without sector context is close to meaningless — Claude must never state "ROE of 15% is good" without stating good relative to what.

---

## Purpose

Provide a single, consistent, sector-aware toolkit of core fundamental ratios and statement-analysis conventions — profitability, returns, leverage, liquidity, efficiency, and growth-quality metrics — with explicit calculation formulas, sector-calibrated interpretation bands, and mandatory cross-ratio pairing rules, so every other skill in the library reads fundamental evidence the same way.

---

## Pre-Flight Requirements

```
□ Minimum 3-5 years of financial statements (P&L, balance sheet, cash flow)
□ Sector classification of the company (required before any ratio is
  interpreted — see Module 1's sector calibration tables)
□ Standalone vs. consolidated figures clearly identified and used
  consistently (never mix standalone P&L with consolidated balance sheet
  ratios, or vice versa)
□ Any exceptional/one-time items identified and available to be excluded
  for "adjusted" ratio calculations, run alongside the "reported" figures
```

---

## Analysis Module 1 — Profitability & Returns Ratios (Sector-Calibrated)

```
GROSS MARGIN = (Revenue − COGS) / Revenue
EBITDA MARGIN = EBITDA / Revenue
NET (PAT) MARGIN = PAT / Revenue

ROE (Return on Equity) = PAT / Average Shareholders' Equity
ROCE (Return on Capital Employed) = EBIT / (Total Assets − Current Liabilities)
  → Preferred over ROE for cross-company/cross-leverage comparison, since
    ROE can be inflated by leverage alone without genuine operating improvement

SECTOR-CALIBRATED "GOOD" BANDS (illustrative — always cross-check against
the specific sector specialist skill, e.g., AI_Chemical_Analysis_Skill,
AI_Banking_Analysis_Skill, for a finer-grained band):

  Sector Type          | EBITDA Margin | ROCE (Good)  | ROE (Good)
  ---------------------|----------------|--------------|------------
  FMCG / Consumer       | 15-25%         | >20%         | >20%
  Specialty Chemicals    | 20-40%         | >18%         | >18%
  Commodity/Cyclical     | 8-15%          | >12% (peak)  | >12% (peak)
  IT Services             | 20-28%         | >25%         | >25%
  Auto Ancillaries        | 12-18%         | >15%         | >15%
  Pharma (Formulations)   | 18-25%         | >15%         | >15%
  Infrastructure/EPC       | 8-14%          | >12%         | >12%
  BFSI                    | N/A (use NIM/ROA/ROE — see AI_Banking_Analysis_
                            Skill / AI_NBFC_Analysis_Skill for the correct
                            metric set; P&L margin ratios do not apply)

MANDATORY PAIRING: ROE must always be read alongside Debt/Equity (Module 3)
— a high ROE driven primarily by high leverage rather than high ROCE is a
materially weaker quality signal and must be labeled as such, not reported
as unqualified "strong profitability."

DUPONT DECOMPOSITION (use when ROE quality needs to be tested):
  ROE = Net Margin × Asset Turnover × Equity Multiplier (leverage)
  → Decompose whenever ROE is unusually high or a key input to a
    conviction rating, to identify whether it is margin-driven,
    efficiency-driven, or leverage-driven
```

---

## Analysis Module 2 — Growth Quality Ratios

```
REVENUE CAGR (n-year) = (Ending Revenue / Beginning Revenue)^(1/n) − 1
PAT CAGR (n-year) = same formula applied to PAT

GROWTH QUALITY CROSS-CHECKS (mandatory, not optional):
  □ Is PAT CAGR > Revenue CAGR? (Positive operating leverage — margins
    expanding as the business scales — a higher-quality growth signal
    than revenue growth alone)
  □ Is Revenue growth being driven by Volume, Price, or Mix? Decompose
    where segment data allows — volume-driven growth is generally
    higher-quality/more sustainable than pure price-driven growth,
    which can reverse quickly if pricing power is not durable
  □ Is growth CONSISTENT (similar CAGR year-on-year) or LUMPY (one strong
    year distorting the multi-year average)? State both the CAGR and the
    year-by-year figures — never present a smoothed CAGR without the
    underlying volatility being visible
  □ Cross-reference growth composition against AI_Future_Growth_Skill's
    tiering (Contracted/Probable/Speculative) when forward growth,
    rather than historical growth, is being assessed
```

---

## Analysis Module 3 — Leverage & Solvency Ratios

```
DEBT/EQUITY = Total Debt / Shareholders' Equity
NET DEBT = Total Debt − Cash & Equivalents − Liquid Investments
INTEREST COVERAGE RATIO = EBIT / Interest Expense
DEBT/EBITDA = Total Debt / EBITDA (particularly relevant for capital-
  intensive and infrastructure-type businesses)

INTERPRETATION BANDS (non-BFSI; BFSI uses CAR/CRAR — see AI_Banking_
Analysis_Skill / AI_NBFC_Analysis_Skill):
  Debt/Equity < 0.5x         → Conservative
  Debt/Equity 0.5x–1.5x       → Moderate, generally manageable
  Debt/Equity 1.5x–3x          → Elevated — requires strong, stable cash
                                   flows to justify; flag if cash flows are volatile
  Debt/Equity > 3x              → High — requires explicit justification
                                   (e.g., regulated utility with contracted
                                   cash flows) or should be treated as a
                                   material risk factor

  Interest Coverage > 5x        → Comfortable
  Interest Coverage 2-5x          → Adequate but worth monitoring trend
  Interest Coverage < 2x           → Weak — debt servicing capacity at risk
                                       if earnings decline further

MANDATORY PAIRING: Debt/Equity must always be read alongside the TREND
(rising/falling over the last 3 years) and the PURPOSE of the debt
(growth capex vs. working capital stress vs. refinancing) — an identical
Debt/Equity ratio means something very different in each of these contexts.
```

---

## Analysis Module 4 — Liquidity & Efficiency Ratios

```
CURRENT RATIO = Current Assets / Current Liabilities
QUICK RATIO = (Current Assets − Inventory) / Current Liabilities

RECEIVABLE DAYS = (Average Receivables / Revenue) × 365
INVENTORY DAYS = (Average Inventory / COGS) × 365
PAYABLE DAYS = (Average Payables / COGS) × 365
CASH CONVERSION CYCLE = Receivable Days + Inventory Days − Payable Days

INTERPRETATION:
  Current Ratio 1.2x–2x    → Generally healthy (context-dependent by sector;
                               asset-light services businesses can run lower)
  Current Ratio < 1x         → Potential near-term liquidity stress, requires
                               explanation (e.g., a bank/NBFC's structure is
                               fundamentally different — exclude from this check)

  Cash Conversion Cycle:
    Shortening trend           → Improving working capital efficiency
    Lengthening trend           → Deteriorating — check specifically whether
                                    receivable days are the driver (a common
                                    early sign of channel stuffing or
                                    deteriorating customer payment discipline
                                    — hand off to Forensic Accounting Skill
                                    if receivable days rise materially
                                    faster than revenue growth)

MANDATORY PAIRING: Rising receivable days alongside strong reported revenue
growth is one of the single most important early-warning combinations in
all of fundamental analysis — always check this pairing explicitly and
flag it, do not report revenue growth and receivable days as separate,
unrelated data points.
```

---

## Analysis Module 5 — Cash Flow Quality Cross-Check

```
OCF/PAT RATIO = Operating Cash Flow / PAT
  > 100%    → Earnings fully or more-than-fully cash-backed (high quality)
  80-100%   → Generally healthy
  50-80%    → Caution — investigate working capital or accrual drivers
  < 50%     → Material earnings quality concern — hand off explicitly to
              the Forensic Accounting Skill before this ratio is allowed
              to stand alone in a conviction rating

FREE CASH FLOW = Operating Cash Flow − Capital Expenditure
  FCF Yield = FCF / Market Capitalization
  → A company with strong reported PAT growth but persistently negative
    or deteriorating FCF is deploying more cash into the business than it
    is generating — this is not automatically bad (can reflect a genuine
    growth investment phase) but must be explicitly reconciled against
    the Future Growth Skill's Tier 1/2 evidence that the capex is
    generating a proportionate future return, not simply assumed

MANDATORY PAIRING: PAT growth is never reported as a standalone quality
signal without the accompanying OCF/PAT ratio for the same period.
```

---

## Analysis Module 6 — Capital Allocation Track Record

```
□ Reinvestment Rate = Capex / (Depreciation + Capex above maintenance level)
□ Return on Incremental Capital Employed (RoICE) = Change in EBIT /
  Change in Capital Employed over the same period — the single best
  test of whether NEW capital deployed is actually earning an adequate return
□ Dividend Payout Ratio = Dividends / PAT — assess appropriateness given
  the company's growth stage (a high-growth Stage 1-2 company per
  AI_Multibagger_Discovery_Skill retaining most earnings for reinvestment
  is healthy; the same payout ratio for a mature, low-growth company
  hoarding cash without productive reinvestment is a capital allocation concern)
□ M&A track record: has past M&A been value-accretive (measurable via
  post-acquisition RoICE) or value-destructive (write-downs, integration
  failures)? State specific historical examples where available, not a
  general impression
```

---

## Analysis Module 7 — Contingent Liabilities and Other Income Quality (Upgrade — Previously Missing)

```
Two off-P&L-ratio blind spots the original module set did not cover:

□ Contingent Liabilities: extract disclosed contingent liabilities
  (tax disputes, guarantees given, pending litigation) as a % of net
  worth — a ratio above ~25-30% of net worth warrants explicit flagging
  even if none have yet crystallized, since a single adverse ruling can
  materially impair the balance sheet without appearing in any standard
  ratio until it happens
□ Other Income Quality: separate RECURRING other income (interest on
  surplus cash, treasury operations) from NON-RECURRING (asset sale
  gains, one-time insurance settlements, forex gains). PAT growth driven
  materially by non-recurring other income must be flagged and excluded
  from any "adjusted" growth-quality read in Module 2 — this is a common,
  easily-missed way reported PAT growth overstates operating performance
```

## Analysis Module 7 — Enterprise Value Bridge and Contingent Liability Treatment (v1.1 Addition)

```
EV-TO-EQUITY VALUE BRIDGE (Missing Link Between EV/EBITDA Multiples and
Per-Share Value):
  Enterprise Value (EV) = Market Capitalization + Total Debt + Minority
    Interest + Preference Capital - Cash & Cash Equivalents - Liquid
    Investments

  This bridge matters because EV/EBITDA multiples (used throughout Skill 07
  and the sector specialist skills) value the OPERATING business, not the
  equity directly - two companies with identical EV/EBITDA can have very
  different per-share equity value if their net debt positions differ
  materially. Always walk the bridge explicitly when EV/EBITDA is the
  primary valuation method:

    EV (from multiple x EBITDA)          = ₹[X] Cr
    Less: Total Debt                      = (₹[X] Cr)
    Less: Minority Interest                = (₹[X] Cr)
    Add: Cash & Liquid Investments          = +₹[X] Cr
    = Equity Value                          = ₹[X] Cr
    / Shares Outstanding                     = ₹[X] per share (Implied Fair Value)

CONTINGENT LIABILITY AND OFF-BALANCE-SHEET ADJUSTMENT:
  Standard ratios (Modules 1-6) are calculated from the balance sheet as
  reported, but several liabilities do not appear on it directly and must
  be factored into leverage and solvency reads:

  □ Contingent liabilities (tax disputes, legal claims, guarantees given
    on behalf of group companies) - disclosed in notes to accounts, not
    the balance sheet itself. As a rule of thumb, if contingent liabilities
    exceed 25% of net worth, treat the reported Debt/Equity ratio as
    understating true leverage risk and flag this explicitly
  □ Operating lease commitments (for lease-heavy models - retail, logistics,
    aviation) - under Ind AS 116 these are now largely on-balance-sheet as
    right-of-use assets/liabilities, but verify this is correctly reflected
    rather than assumed
  □ Corporate guarantees extended to related parties or joint ventures -
    cross-reference against the Related Party Transactions section of the
    Forensic Accounting Skill; a guarantee extended to a stressed group
    entity is a specific, checkable early-warning combination
  □ Letters of credit and bank guarantees outstanding (relevant for
    EPC/infrastructure and trading businesses) - can represent a material
    contingent draw on liquidity not visible in the standard Current Ratio

  MANDATORY RULE: Any company where contingent liabilities exceed 25% of
  net worth must have this stated explicitly alongside the standard
  Debt/Equity and Interest Coverage ratios in Module 3 - the reported
  leverage ratios alone are insufficient in this case.
```


## Red Flag Summary — Fundamental Analysis Context

### CRITICAL Flags
```
❗ A ratio (especially ROE) reported as "strong" without disclosing whether
  it is leverage-driven (via DuPont decomposition) or genuine operating strength
❗ Revenue growth reported without the mandatory receivable-days pairing
  from Module 4 — one of the most common ways deteriorating growth quality
  is missed
❗ OCF/PAT ratio below 50% not flagged and handed off to the Forensic
  Accounting Skill
❗ A ratio interpreted against a generic "good/bad" threshold without
  sector calibration (e.g., judging a commodity cyclical's margin against
  an FMCG benchmark)
```

### HIGH Flags
```
⚠️ PAT CAGR reported without the accompanying Revenue CAGR comparison
  (masks whether growth is margin-driven, and if so, whether that is
  sustainable)
⚠️ Debt/Equity reported as a single snapshot without the 3-year trend and
  stated purpose of the debt
⚠️ RoICE not calculated for a company with significant recent capex/M&A,
  leaving capital allocation quality unassessed
```

---

## Output Format

```
FUNDAMENTAL RATIO ANALYSIS
Company: [Name] | Ticker: [NSE] | Sector: [Sector — calibration band applied]
Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

PROFITABILITY & RETURNS:
  Gross / EBITDA / Net Margin:  [X]% / [X]% / [X]% — vs sector band: [Assessment]
  ROE:                            [X]% — DuPont: Margin [X] × Turnover [X] ×
                                    Leverage [X] — [Genuine/Leverage-driven]
  ROCE:                           [X]% — vs sector band: [Assessment]

GROWTH QUALITY:
  Revenue CAGR (n-yr):            [X]% | PAT CAGR: [X]% — [PAT > Rev: Yes/No]
  Growth Driver:                   [Volume/Price/Mix — decomposed where possible]
  Consistency:                     [Consistent/Lumpy] — year-by-year: [list]

LEVERAGE & SOLVENCY:
  Debt/Equity:                    [X]x (3-yr trend: [X]) — Purpose: [Growth/
                                    Working Capital/Refinancing]
  Interest Coverage:               [X]x — [Comfortable/Adequate/Weak]

LIQUIDITY & EFFICIENCY:
  Current Ratio:                   [X]x
  Cash Conversion Cycle:            [X days] (trend: [Shortening/Lengthening])
  Receivable Days vs Revenue Growth: [Paired check — flag if diverging]

CASH FLOW QUALITY:
  OCF/PAT:                         [X]% — [Pass/Caution/Forensic Handoff Required]
  FCF Yield:                        [X]% — Trend: [X]

CAPITAL ALLOCATION:
  RoICE (incremental):              [X]% vs WACC [X]% — [Value-accretive/Destructive]
  Dividend Payout:                   [X]% — [Appropriate for growth stage: Yes/No]
  M&A Track Record:                  [Value-accretive/Destructive/None recent]

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]

OVERALL FUNDAMENTAL QUALITY READ: [Strong/Adequate/Weak — sector-adjusted]
HANDOFF: [Forensic Accounting Skill if OCF/PAT or receivable-day flags
  triggered; AI_Future_Growth_Skill if forward growth assumptions need tiering]
```

---

## Rules (Non-Negotiable)

```
1. No ratio is interpreted against a generic threshold — sector calibration
   (Module 1 table or the relevant sector specialist skill) is mandatory.
2. ROE is never reported without its DuPont decomposition when it is a
   material input to a conviction rating.
3. Revenue growth is never reported without the paired receivable-days check.
4. OCF/PAT below 50% triggers a mandatory handoff to the Forensic Accounting
   Skill before the ratio set is used in a conviction rating.
5. PAT growth is never reported as a standalone quality signal without the
   accompanying OCF/PAT ratio for the same period.
6. Standalone and consolidated figures are never mixed within one ratio calculation.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Core Toolkit — Fundamental Analysis*
*Integrates with: Skill 01 (Master Research, Step 6), Forensic Accounting Skill, AI_Future_Growth_Skill,
AI_Banking_Analysis_Skill, AI_NBFC_Analysis_Skill, AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill*

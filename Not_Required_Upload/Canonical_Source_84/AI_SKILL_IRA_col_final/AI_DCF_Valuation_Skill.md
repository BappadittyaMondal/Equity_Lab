<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI DCF Valuation Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI DCF Valuation Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Valuation — Applies when intrinsic value estimation is required

---

## CRITICAL AI INSTRUCTION

This skill executes when a fundamental intrinsic value is required for any company. A DCF output is **not a price target** — it is a range of fair values under defined assumptions. All assumptions must be stated, challenged, and stress-tested. False precision is more dangerous than honest uncertainty. Always produce a **Reverse DCF** alongside the forward DCF.

---

## Purpose

Build a rigorous, assumption-transparent Discounted Cash Flow valuation model for Indian-listed companies. Produce a defensible intrinsic value range, identify the key value drivers, and perform a reverse DCF to understand what the market is already pricing in.

---

## Pre-Flight Requirements

```
□ Minimum 5 years of historical financials (P&L, Balance Sheet, Cash Flow)
□ Latest 4 quarters of results for TTM calculation
□ Industry growth rate benchmarks
□ Peer valuation multiples (for cross-validation)
□ Company's own guidance or management commentary on growth
□ CapEx guidance (maintenance vs. growth split)
□ Working capital trend (to estimate NWC changes)
□ Effective tax rate (use 5-year average, not single year)
□ Debt schedule (for FCFE or EV bridge)
□ Beta estimate (or sector beta for unlisted comparable)
```

If historical cash flows are unavailable: Use EBIT-based approximation, flag as lower confidence.

---

## Analysis Module 1 — Business Quality Pre-Assessment

Before running numbers, assess:

### Step 1.1 — Business Predictability Score
```
High Predictability (Score 3):
→ Recurring revenue model (subscription, annuity)
→ Long-term contracts (3+ years)
→ Essential service / regulated business

Medium Predictability (Score 2):
→ Consumer staples, utility-adjacent
→ Business with visible order book (1–2 years)

Low Predictability (Score 1):
→ Cyclical business (commodities, capital goods)
→ Project-based revenue
→ New/unproven business model
```

**DCF Discount Rule:** Low predictability businesses should use higher WACC and lower terminal growth rate. A cyclical business valued at peak earnings is a valuation error.

### Step 1.2 — Competitive Moat Assessment
```
Wide Moat → Use 10-year explicit period + high terminal value confidence
Narrow Moat → Use 7-year explicit period + moderate terminal value
No Moat → Use 5-year explicit period + minimal terminal value reliance
         → Terminal value should be <40% of total enterprise value
```

---

## Analysis Module 2 — Free Cash Flow Calculation

### Step 2.1 — FCFF (Free Cash Flow to Firm)
```
FCFF = EBIT × (1 − Tax Rate)
       + Depreciation & Amortisation
       − Capital Expenditure (Total)
       − Change in Net Working Capital

Where:
→ EBIT: use adjusted EBIT (exclude one-time items)
→ Tax Rate: use 5-year average effective rate (not statutory 25.17%)
→ CapEx: include maintenance + growth CapEx
→ NWC Change = Change in (Current Assets − Cash − Current Liabilities + Short-term Debt)
```

### Step 2.2 — Historical FCFF Analysis (5 Years)
```
Build table:
Year    | Revenue | EBIT | NOPAT | D&A | CapEx | ΔNWC | FCFF | FCF Margin
FY2021  |         |      |       |     |       |      |      |
FY2022  |         |      |       |     |       |      |      |
FY2023  |         |      |       |     |       |      |      |
FY2024  |         |      |       |     |       |      |      |
FY2025  |         |      |       |     |       |      |      |
5yr Avg |         |      |       |     |       |      |      |

Key Checks:
□ Is FCFF consistently positive? (Negative FCF businesses need special treatment)
□ Is FCF margin expanding or contracting?
□ CapEx intensity: CapEx/Revenue ratio trend
□ Reinvestment Rate: how much of NOPAT is reinvested?
   Reinvestment Rate = (CapEx − D&A + ΔNWC) / NOPAT
```

### Step 2.3 — FCFE (Free Cash Flow to Equity) — Optional
```
FCFE = Net Profit
       + Depreciation & Amortisation
       − Capital Expenditure
       − Change in Net Working Capital
       + Net Borrowing (New Debt − Repayments)

Use FCFE for equity valuation directly.
Use FCFF → EV → subtract debt → Equity value approach otherwise.
Consistency rule: FCFF discounted at WACC; FCFE discounted at Cost of Equity.
```

---

## Analysis Module 3 — WACC Calculation

### Step 3.1 — Cost of Equity (Ke) — CAPM
```
Ke = Rf + β × (Rm − Rf) + Additional Premiums

Where:
→ Rf (Risk-Free Rate): Use current 10-year G-Sec yield
   [As of analysis date — always use current, not historical]
→ β (Beta): Use 3-year weekly beta vs. Nifty 50
   → If stock is too small/illiquid: use sector unlevered beta + relevered for target structure
→ Rm − Rf (Equity Risk Premium): India ERP = 6.0–7.5% (use 7%)
→ Additional Premiums:
   Liquidity Premium (small/micro cap): +1.0% to +2.5%
   Country Premium (if significant foreign operations): adjust
   Company-Specific Premium (fraud/governance risk): +0.5% to +2.0%

Typical range for Indian equities:
→ Large cap blue chip: 10–12%
→ Mid cap quality: 12–14%
→ Small cap: 14–18%
→ Microcap / speculative: 18–22%
```

### Step 3.2 — Cost of Debt (Kd)
```
Kd (post-tax) = (Total Interest Expense / Average Debt) × (1 − Tax Rate)
→ Use actual interest from P&L, not headline rate
→ If interest coverage < 2x: Kd may understate true credit risk
→ Include lease liabilities (IND-AS 116) as debt if material
```

### Step 3.3 — Capital Structure and WACC
```
WACC = (E/V) × Ke + (D/V) × Kd

Where:
→ E = Market Capitalisation
→ D = Total Financial Debt (book value acceptable for stable businesses)
→ V = E + D

Note: Use target/normalised capital structure for stable businesses,
      not current structure if company is in debt-reduction mode.

WACC Sanity Check:
→ Must exceed inflation rate
→ Must be credible vs. sector benchmarks
→ Report WACC to 1 decimal place only — false precision beyond this
```

---

## Analysis Module 4 — Projection Framework

### Step 4.1 — Three-Stage Projection Model

**Stage 1: Explicit Forecast Period (Years 1–5)**
```
Build revenue and margin projections bottom-up:
→ Volume growth + Pricing growth = Revenue growth
→ Operating leverage: margin expansion per 100bps revenue growth
→ CapEx: maintenance + growth (use management guidance if available)
→ Working capital: use trend-adjusted days

Sources for assumptions:
→ Company management guidance (Tier 1, but verify with track record)
→ Industry association reports
→ Government data (PLI targets, infrastructure pipeline)
→ Peer company performance
```

**Stage 2: Transition Period (Years 6–10, if using 10-year model)**
```
→ Growth rate tapers from Stage 1 rate toward terminal growth
→ ROIC converges toward WACC as competitive advantages erode
→ CapEx intensity normalises
```

**Stage 3: Terminal Value**
```
Terminal Value = FCFF (Year N+1) / (WACC − g)

Where g = Long-term terminal growth rate
→ Conservative: g = India's long-term nominal GDP growth × 0.5
   (Company cannot grow faster than economy forever)
→ Typical range: 4–6% for India
→ Use lower g for: cyclicals, declining industries, governance-risk businesses
→ Use higher g for: regulated utilities, essential services, deep moat businesses

CRITICAL: Terminal Value should ideally be <70% of total enterprise value.
If TV >80%: model is too sensitive to terminal assumptions — use higher WACC
           or shorten explicit period.
```

### Step 4.2 — Three Scenarios (Mandatory)
```
BEAR CASE:
→ Revenue growth at -30% of base case
→ Margins compress to 5-year lows
→ WACC +200bps
→ Terminal growth -1%

BASE CASE:
→ Revenue growth at management-guided or industry-average rate
→ Margins at 5-year trend
→ WACC at calculated value
→ Terminal growth at India LT GDP growth rate

BULL CASE:
→ Revenue growth at historical peak or addressable market expansion
→ Margins at best-in-class peer level
→ WACC −50bps (execution premium)
→ Terminal growth +0.5%
```

---

## Analysis Module 5 — Reverse DCF (Always Run)

### Step 5.1 — Reverse Engineering Market Expectations
```
What growth rate does the current market price imply?

Process:
1. Start with Current Market Cap (= current enterprise value + net cash − debt)
2. Use company's actual FCFF margin and WACC
3. Solve for Revenue CAGR that yields the current EV
4. Compare implied growth to historical growth and analyst consensus

Output question: "At CMP of ₹X, the market is pricing in Y% revenue CAGR 
                 for the next N years. Is this achievable?"
```

### Step 5.2 — Market Expectation Assessment
```
Implied growth rate vs. reality:
→ Implied growth < historical average: Stock may be UNDERVALUED
→ Implied growth = historical average: Stock is FAIRLY VALUED
→ Implied growth > historical average: Stock may be OVERVALUED
   → BUT: Is there a genuine step-change catalyst? If yes, justify premium.

This is more useful than DCF alone because it anchors the analysis 
to what is priced in, not just what the model predicts.
```

---

## Analysis Module 6 — Valuation Cross-Check

### Step 6.1 — Multiple-Based Cross Validation
```
After DCF, cross-check with:

Method 1 — P/E based:
  Fair Value = Normalised EPS × Justified P/E
  Justified P/E = Based on ROE, growth, and peer comparison

Method 2 — EV/EBITDA based:
  Fair EV = EBITDA × Sector median EV/EBITDA
  Equity Value = Fair EV − Net Debt

Method 3 — Price/Book based:
  Useful for: Banks, NBFCs, asset-heavy businesses
  Fair P/B = ROE / Ke (Gordon Growth Model)
  
Method 4 — Dividend Discount Model (DDM):
  Useful for: High-dividend, stable businesses
  Fair Value = D1 / (Ke − g)

Coherence Check:
→ All methods should point to roughly similar ranges (+/− 20%)
→ Wide divergence = model assumption error or market mispricing
```

---

## Analysis Module 6A — India Sector WACC Reference Table

Use as sanity check after calculating WACC from first principles:

```
SECTOR                          TYPICAL WACC RANGE    NOTES
─────────────────────────────────────────────────────────────────
Consumer Staples (large cap)     10–12%               Low beta, stable
IT Services (large cap)          11–13%               Low debt, high ROE
Private Banks                    12–14%               Regulatory moat
Pharmaceuticals                  12–15%               Diversified, USFDA risk
NBFCs (quality)                  13–15%               Funding risk premium
Consumer Discretionary           12–15%               Cyclical premium
Capital Goods / Engineering      13–16%               Long-cycle, capex risk
Specialty Chemicals              13–16%               RM volatility
Auto Ancillaries                 13–16%               OEM dependency
Renewable Energy (project-level)  8–10%               Near-certain PPA CF
Regulated Utilities (NTPC type)   9–11%               Quasi-sovereign
Defence (PSU)                    10–12%               Government backing
Realty / Developers              15–19%               Execution + regulatory risk
Microcap / Early stage           18–24%               Illiquidity + governance
MFI / High-risk NBFC             16–20%               Asset quality volatility

RULE: If your calculated WACC falls outside ±200bps of sector range, 
      re-examine beta, risk-free rate, and capital structure assumptions.
```

## Analysis Module 6B — Negative FCF Company Protocol

When company has negative or near-zero FCF (common: early-stage, growth-capex phase):

```
Step 1 — Diagnose the reason:
Type A: Growing too fast (CapEx > OCF temporarily) → Acceptable
  Signal: OCF positive and rising, CapEx for proven demand
Type B: Business generating no cash despite profits → Investigate
  Signal: PAT positive, OCF negative = working capital trap or manipulation
Type C: Structurally unprofitable → Avoid unless turnaround thesis
  Signal: Operating loss, no path to profitability

Step 2 — For Type A only: use forward FCF model
→ Project when CapEx normalises (capacity commissions)
→ Use "normalised FCF" = current OCF × (1 + growth) − maintenance CapEx
→ Discount back at appropriate WACC
→ Apply higher WACC (+200bps) to reflect uncertainty on timing

Step 3 — Negative FCF runway check:
Cash + Undrawn Lines / Monthly Cash Burn = Months of Runway
→ < 12 months: Dilution or debt raise imminent = near-term shareholder risk
→ 12–24 months: Monitor
→ > 24 months: Adequate buffer

Step 4 — Terminal value reliability:
→ For negative FCF companies, TV is often >90% of EV
→ This makes DCF extremely fragile
→ ALWAYS cross-check with: (a) peer EV/Revenue, (b) scenario where FCF 
  positive date slips 2 years → what is value impact?
```

## Analysis Module 6C — Reinvestment Efficiency

```
Reinvestment Rate = (Net CapEx + ΔNWC) / NOPAT
  Where Net CapEx = CapEx − Depreciation

ROIC = NOPAT / Invested Capital

Value creation requires: ROIC > WACC

Reinvestment Return = ROIC × Reinvestment Rate = Sustainable Growth Rate
  Example: ROIC 20%, Reinvestment Rate 50% → Sustainable growth = 10%

Cross-check: Does DCF-assumed growth rate ≤ sustainable growth rate?
  If DCF assumes 15% growth but sustainable growth is 10% → Overoptimistic model

Companies with ROIC >> WACC and low reinvestment rate:
→ Compounders: high-quality but limited reinvestment opportunity
→ Value to shareholders via dividends/buybacks
→ Value in DCF = high terminal value relative to explicit period

Companies with ROIC < WACC but high reinvestment:
→ Destroying value with every rupee reinvested
→ Growth is a negative in DCF when ROIC < WACC
→ Management should return capital, not reinvest
```

## Margin of Safety Framework

```
Business Quality → Minimum Required Margin of Safety

Wide Moat, Strong Governance:    Buy if CMP < 85% of Bear Case Value (15% MoS)
Narrow Moat, Good Governance:    Buy if CMP < 75% of Base Case Value (25% MoS)
No Moat or Governance Concern:   Buy if CMP < 60% of Base Case Value (40% MoS)
Cyclical at Trough Earnings:     Buy if EV/EBITDA < 5x trough EBITDA

Valuation Exit Signal:
→ CMP > 120% of Bull Case Value: consider reducing position
→ CMP > Bear Case Value only by 10%: exit or tight stop
```

---

## Final DCF Output Format

```
DCF VALUATION REPORT
Company: [Name] | Ticker: [NSE/BSE] | CMP: ₹[X]
Analysis Date: [DD/MM/YYYY] | Model: [FCFF/FCFE/DDM]
═══════════════════════════════════════════════════════════════════

KEY ASSUMPTIONS:
  Risk-Free Rate:     [%] (10-yr G-Sec as of [date])
  Beta:               [X.XX] ([3-year weekly vs. Nifty 50])
  Cost of Equity:     [%]
  Cost of Debt:       [%] (post-tax)
  WACC:               [%]
  Terminal Growth:    [%]
  Forecast Period:    [N] years
  Model Confidence:   [High / Medium / Low] — [reason]

─────────────────────────────────────────────
SCENARIO ANALYSIS:
                     Bear     Base     Bull
Revenue CAGR (5yr): [%]      [%]      [%]
EBITDA Margin:      [%]      [%]      [%]
Intrinsic Value:   ₹[X]    ₹[X]    ₹[X]
Upside/Downside:   [%]     [%]     [%]
Terminal Value %:   [%]     [%]     [%]

REVERSE DCF:
  Implied Revenue CAGR (at CMP ₹[X]):  [%]
  This vs. Historical CAGR:             [%] (5yr historical)
  Assessment:  [Underpriced / Fairly priced / Overpriced]
  Embedded Expectation: [What must happen for CMP to be justified]

─────────────────────────────────────────────
MULTIPLE CROSS-CHECK:
  P/E Based Value:        ₹[X] (at [X]x on ₹[Y] normalised EPS)
  EV/EBITDA Based Value:  ₹[X] (at [X]x on ₹[Y]Cr EBITDA)
  Price/Book Based Value: ₹[X] (at [X]x P/B justified by [X]% ROE)
  Coherence Check:        [All methods aligned / Divergent — reason]

─────────────────────────────────────────────
VALUATION CONCLUSION:
  Intrinsic Value Range:  ₹[Bear Value] — ₹[Bull Value]
  Base Case Fair Value:   ₹[Base Value]
  CMP:                    ₹[X]
  Margin of Safety:       [%] — [Adequate / Insufficient / Strong]
  Required MoS for this business: [%]
  
  BUY ZONE:     ₹[Lower] – ₹[Upper] (offers required margin of safety)
  FAIR VALUE:   ₹[X]
  EXPENSIVE:    Above ₹[X]
  
  KEY VALUE DRIVERS (in order of impact):
  1. [Assumption X — what it does to value if changes ±1%]
  2. [Assumption Y]
  3. [Assumption Z]
  
  WHAT COULD BE WRONG WITH THIS MODEL:
  → [Key assumption that is most uncertain]
  → [Data limitation that reduces confidence]
  
  VALUATION RECOMMENDATION:
  → [ATTRACTIVE — Strong Buy Zone | FAIR — Hold/Accumulate | 
     EXPENSIVE — Reduce | SIGNIFICANTLY OVERVALUED — Exit]
```

---

## Universal Rules — DCF Valuation

1. **Terminal value dependency >70% = model is fragile.** Increase explicit forecast period or use conservative TV.
2. **Never value a cyclical at peak earnings.** Use mid-cycle normalised earnings.
3. **Always run the Reverse DCF.** Market expectation analysis is more honest than model precision.
4. **Assumptions kill DCFs, not arithmetic.** State every assumption and challenge it.
5. **WACC below 10% for Indian equities = almost certainly wrong.** Minimum floor: 10%.
6. **A model that always gives the answer you expected is not a model — it is confirmation bias.**
7. **Range is more honest than point estimate.** Always output bear/base/bull.
8. **Cross-check with multiples.** If all methods disagree, find out why before concluding.

---

*Skill Version 1.0 | IERL Specialist Skill Library | Indian Equity Research Lab*
*This skill integrates with: Skill 01 (Master Research), Skill 07 (Valuation Comparator), Skill 15 (Pre-Investment Checklist)*

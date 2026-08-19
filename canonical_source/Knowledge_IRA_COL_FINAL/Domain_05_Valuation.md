<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Valuation  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 5 — Valuation
Version: 1.0 | Status: Production Ready

---

## Purpose
Valuation translates business fundamentals into an estimate of intrinsic worth. This domain covers the major methodologies, their assumptions, appropriate use cases, and limitations. Multiple methods should always be triangulated rather than relying on a single approach.

---

## Core Methods

### 1. Discounted Cash Flow (DCF)
- Principle: Intrinsic value = Present value of all future free cash flows.
- Key inputs: Revenue growth assumptions, margin trajectory, capex/working capital needs, Weighted Average Cost of Capital (WACC), terminal growth rate.
- Strength: Grounded in fundamental cash generation, not market sentiment.
- Weakness: Highly sensitive to terminal value and discount rate assumptions — small input changes create large valuation swings.
- Best suited for: Companies with predictable, stable cash flows.

### 2. Price-to-Earnings (P/E)
- Formula: Market Price per Share / Earnings per Share.
- Use: Quick relative valuation vs. peers, sector, and historical average.
- Weakness: Distorted by one-off items, accounting differences, and does not work for loss-making companies.

### 3. Price-to-Book (P/B)
- Formula: Market Price per Share / Book Value per Share.
- Use: Especially relevant for asset-heavy businesses (banks, NBFCs, capital-intensive manufacturers).
- Weakness: Book value can be distorted by historical cost accounting, intangibles, and impairments.

### 4. EV/EBITDA (Enterprise Value to EBITDA)
- Formula: (Market Cap + Debt – Cash) / EBITDA.
- Use: Capital-structure-neutral comparison, useful across companies with different leverage levels.
- Strength: Removes distortion from depreciation policy and financing choices.

### 5. PEG Ratio
- Formula: P/E Ratio / Expected Earnings Growth Rate.
- Use: Adjusts P/E for growth — a lower PEG suggests better value relative to growth prospects.
- Weakness: Highly dependent on the reliability of the growth estimate used.

### 6. Dividend Discount Model (DDM)
- Principle: Intrinsic value = Present value of expected future dividends.
- Best suited for: Mature, stable dividend-paying companies (utilities, established banks).
- Weakness: Not applicable to companies that reinvest heavily and pay minimal/no dividends.

### 7. Residual Income Model
- Principle: Value = Book Value + Present value of future residual income (Net Income – Equity Charge).
- Use: Useful when free cash flows are volatile or negative but accounting profits are meaningful (e.g., financial institutions).

### 8. Sum of the Parts (SOTP)
- Principle: Value each business segment/subsidiary separately using the most appropriate method, then aggregate.
- Best suited for: Diversified conglomerates or companies with distinct segments deserving different valuation multiples.

### 9. Asset Value (Net Asset Value / Liquidation Value)
- Principle: Value based on the fair value of net assets, assuming orderly sale or liquidation.
- Best suited for: Asset-heavy companies, real estate, holding companies, distressed situations.

### 10. Replacement Cost
- Principle: Value based on the cost to recreate the company's assets/capacity from scratch.
- Use: Useful floor-value check, especially for capital-intensive industries (cement, steel, power) and as a takeover/M&A reference point.

---

## Application Framework for Research
1. Select methods appropriate to the business type — do not apply DDM to a non-dividend payer, or DCF to a highly cyclical company without cycle-adjusted assumptions.
2. Use at least two to three methods and triangulate — a wide divergence between methods signals the need for deeper assumption review.
3. Always state key assumptions explicitly (growth rate, discount rate, terminal value) so conclusions are auditable.
4. Compare resulting valuation to current market price and historical valuation bands to assess relative attractiveness.

---

## Red Flags / Cautions
- Terminal growth rate assumptions exceeding long-term nominal GDP growth without justification.
- Using peer multiples without adjusting for differences in growth, margin, and leverage profile.
- Ignoring cyclicality when applying trailing multiples to cyclical businesses.
- Presenting a single-point valuation without a sensitivity range.

---

## Universal Rule Applied to This Domain
Valuation output is an estimate, not a fact. Always disclose the method(s) used, key assumptions, and the resulting sensitivity/range rather than a false-precision single number.

---

## Worked Example
DCF sanity check: FCF₀ = ₹500cr, growth 10% for 5 years then 4% terminal, WACC = 12%. Rough terminal value = FCF₅ × (1+g)/(WACC-g) = FCF₅ × 1.04/0.08 = FCF₅ × 13x. If FCF₅ ≈ ₹805cr, terminal value ≈ ₹10,465cr — this typically dominates 60-70% of total DCF value, which is exactly why terminal growth assumptions deserve the most scrutiny, not the explicit forecast period.

## AI Trigger Keywords
DCF, fair value, intrinsic value, P/E multiple, EV/EBITDA, target price, WACC, terminal value, SOTP, sum of parts, replacement cost, is it overvalued/undervalued.

## Cross-Domain Links
→ Domain 4 (input ratios) · Domain 6 (quality inputs to growth/margin assumptions) · Domain 9 (Valuation Risk) · Domain 21 (factor-based value screens).

## Conflict Rule
If DCF and relative multiples diverge >30%, trust relative multiples for near-term price action, DCF for long-term fair value — state both, don't average them.

---

## Method Selection Matrix — Which Valuation to Use When

Derived exclusively from the 10 methods and their stated strengths, weaknesses, and use-case notes already in this domain.

| Method | Best For | NOT Suitable For | Key Risk to Watch |
|---|---|---|---|
| **DCF** | Stable, predictable free cash flow businesses | Highly cyclical companies (swings distort terminal value) | Terminal value dominates 60–70% of total value — small assumption changes create large swings |
| **P/E** | Quick relative valuation vs. peers, sector, historical average | Loss-making companies; distorted by one-off items | One-off items can inflate or deflate EPS dramatically, creating false cheapness/richness |
| **P/B** | Asset-heavy businesses: banks, NBFCs, capital-intensive manufacturers | Asset-light, IP-driven, or software businesses | Historical cost accounting distorts book value; intangibles often understated |
| **EV/EBITDA** | Capital-structure-neutral peer comparison; cross-leverage comparisons | Start-ups and pre-EBITDA companies | Different capex intensities make EBITDA non-comparable without adjustment |
| **PEG** | Growth-adjusted cheapness screen; comparing fast-growers | Mature or slow-growing companies with low growth denominator | Entirely dependent on reliability of the growth estimate used |
| **DDM** | Mature, stable dividend-paying companies: utilities, established banks | Companies that reinvest heavily with minimal/no dividends | Not applicable where dividend policy is absent or erratic |
| **Residual Income** | Financial institutions where FCF is volatile but accounting profits are meaningful | Asset-light or non-financial businesses with simple capital structures | Requires reliable equity charge (cost of equity) assumption |
| **SOTP** | Diversified conglomerates with multiple distinct business segments | Single-business pure-play companies | Holding company discount is frequently ignored, overstating total SOTP value |
| **NAV / Liquidation** | Holding companies, real estate, distressed situations | Operating businesses with significant intangible/franchise value | Liquidation assumption may be unrealistic for a going-concern business |
| **Replacement Cost** | Capital-intensive industries (cement, steel, power) as a floor valuation | Businesses where IP, brand, or processes create value beyond asset cost | Ignores profitability — a business with high asset value but poor returns on those assets can still be a bad investment |

**Selection Rule:** Use at least 2–3 methods and triangulate. A wide divergence between methods (>30%) signals the need for deeper assumption review — see Conflict Resolution Protocol below.

---

## Valuation Sensitivity Reference — DCF Terminal Value Sensitivity

Using ONLY the worked example already in this domain (FCF₀ = ₹500 Cr, revenue growth = 10% for 5 years, terminal growth = 4%, WACC = 12%), this table shows how the terminal value multiple changes as WACC and terminal growth rate vary. Formula used: `Terminal Value Multiple = (1 + g) / (WACC – g)` (as stated in the worked example).

**FCF at Year 5 (FCF₅):** At 10% growth over 5 years, FCF₅ ≈ ₹500 Cr × (1.10)⁵ ≈ ₹805 Cr.

**Terminal Value Multiple = FCF₅ × (1+g) / (WACC – g):**

| | **Terminal Growth = 3%** | **Terminal Growth = 4%** | **Terminal Growth = 5%** |
|---|---|---|---|
| **WACC = 11%** | 805 × (1.03/0.08) = **~10,365 Cr** | 805 × (1.04/0.07) = **~11,966 Cr** | 805 × (1.05/0.06) = **~14,088 Cr** |
| **WACC = 12%** | 805 × (1.03/0.09) = **~9,212 Cr** | 805 × (1.04/0.08) = **~10,465 Cr** | 805 × (1.05/0.07) = **~12,079 Cr** |
| **WACC = 13%** | 805 × (1.03/0.10) = **~8,292 Cr** | 805 × (1.04/0.09) = **~9,302 Cr** | 805 × (1.05/0.08) = **~10,566 Cr** |

**Key Insight (from the existing worked example):** At the base case (WACC=12%, g=4%), terminal value ≈ ₹10,465 Cr. But moving from WACC=11% to WACC=13% while holding g=4% changes the terminal value from ₹11,966 Cr to ₹9,302 Cr — a swing of nearly ₹2,700 Cr (26%) from a 2-percentage-point discount rate change alone. This is exactly why the worked example notes that terminal value "typically dominates 60-70% of total DCF value" and deserves the most scrutiny.

**Practical Rule:** Always present a minimum 3x3 sensitivity table (WACC × terminal growth) with any DCF output. A single-point DCF valuation without a sensitivity range is a red flag per this domain's existing Universal Rule.

---

## Valuation Conflict Resolution Protocol — 4-Step Process

Derived from the existing Conflict Rule in this domain (line 102): *"If DCF and relative multiples diverge >30%, trust relative multiples for near-term price action, DCF for long-term fair value — state both, don't average them."*

**Step 1 — Identify the divergence:**
Calculate the percentage gap between the DCF intrinsic value and the current market price implied by relative multiples (P/E × EPS, or EV/EBITDA × peers). If gap < 15%: no conflict, both methods broadly agree. If gap 15–30%: note the difference, state assumptions. If gap > 30%: activate this protocol.

**Step 2 — Determine the horizon:**
Per the existing Conflict Rule — if the decision horizon is near-term (0–12 months), relative multiples have higher weight because they reflect current market pricing and sentiment. If the horizon is long-term (3–7 years), DCF has higher weight because it reflects the fundamental earnings power trajectory.

**Step 3 — Identify the source of divergence:**
The gap is almost always in one of 3 places: (a) WACC / discount rate assumption in DCF vs. market's implied cost of equity; (b) terminal growth rate in DCF vs. implied perpetual growth in the current multiple; (c) near-term earnings estimate differences. Name the specific driver of divergence explicitly — do not leave it as a vague "models disagree."

**Step 4 — Report both, never average:**
Per the existing Conflict Rule: state both valuations and their assumptions side by side. Do NOT mathematically average DCF and relative multiple outputs into a "blended target price" — averaging conceals the divergence rather than resolving it. Reducing confidence is the appropriate response to unresolved divergence, not false precision.

---
End of Document — Domain 5

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
End of Document — Domain 5

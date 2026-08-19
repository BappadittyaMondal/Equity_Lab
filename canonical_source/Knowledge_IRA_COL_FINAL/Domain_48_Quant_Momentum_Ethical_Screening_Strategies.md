<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Quant Momentum Ethical Screening Strategies  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 48 — Quant Momentum & Screening Strategies

Version: 1.0 | Status: Production Ready (Canonical Expert Strategy)  
Expert Origin: Mr. Rohan Mehta (Quant Fund Manager)

## Purpose
This domain codifies data-driven quantitative momentum strategies, multi-factor profit-price filters, risk-based position sizing algorithms, and ethical ESG screening filters.

---

## 15. Quant Momentum Investing (All-Time High Strategy)
- **Concept:** Systematic, rule-based quantitative strategy buying stocks exclusively when they break out to All-Time High (ATH) prices.
- **Behavioral & Technical Edge:** Rejects "buy low, sell high" in favor of mathematical momentum. An All-Time High eliminates overhead supply (no trapped buyers waiting to break even), signaling maximum fundamental/narrative strength.
- **Empirical Validation:** 17 years of historical Indian equity market backtest data proves Momentum factor consistently outperforming Value, Quality, and Low-Volatility factors by significant margins.

### Pre-Execution Requirements — Strategy 15
```
□ Historical all-time price high data for target stock (user must provide)
□ Daily volume check confirming ATH breakout (minimum 1.5x average volume)
□ 50-day and 200-day EMA trend alignment
```

### Failure Modes & Hard Stop Rules — Strategy 15
```
❗ False ATH breakout where price closes back below ATH line on breakout day
❗ Market-wide regime crash (broad index drawdown >10% invalidates momentum long positions)
❗ Overhead resistance remaining from stock splits/adjustments not factored into data
```

### Worked Numerical Example — Strategy 15
```
Quant Momentum ATH Breakout Setup:
- Stock Historical Peak: ₹500 (established 3 years ago).
- Breakout Action: Stock price closes at ₹505 on 2.0x average daily volume.
- Momentum Logic: At ₹505, zero shareholders are in a loss position; zero overhead supply.
- Execution: Initiate buy position at ₹505; set trailing stop loss at 200-day EMA (₹430).
```

---

## 16. Triple-Filter Quant Momentum Strategy
- **Concept:** Strict systematic multi-factor model merging price momentum with core trailing profitability to eliminate speculative bubble stocks.
- **The 3 Mandatory Filters:**
  1. **Price Filter:** Stock actively trading at its All-Time High (ATH) price.
  2. **Fundamental Filter:** Trailing Twelve Month (TTM) Profit After Tax (PAT) at All-Time High.
  3. **Relative Strength Filter:** Stock actively outperforming both Nifty 500 Index and its Sector Index over a 52-week rolling window.
- **Empirical Win Rate:** Elevates 1-year forward positive return probability from 66% (single-factor price ATH) to 82%.

### Pre-Execution Requirements — Strategy 16
```
□ All-Time High (ATH) price check status (user must provide)
□ TTM PAT historical quarterly data to verify TTM Profit is at ATH
□ 52-week rolling Relative Strength score vs Nifty 500 and Sector Index
```

### Failure Modes & Hard Stop Rules — Strategy 16
```
❗ Stock price at ATH but TTM PAT is declining (speculative narrative bubble)
❗ Stock outperforming benchmark index but underperforming its sector peer index
❗ Discontinuation of PAT growth due to one-off extraordinary accounting items
```

### Worked Numerical Example — Strategy 16
```
Triple-Filter Quant Momentum Execution:
- Filter 1 (Price ATH): Current Stock Price = ₹1,200 (Previous ATH was ₹1,150) → PASS.
- Filter 2 (Profit ATH): TTM PAT = ₹450 Cr (Previous Peak TTM PAT was ₹380 Cr) → PASS.
- Filter 3 (Relative Strength): 52-Week RS vs Nifty 500 = +34% Outperformance; RS vs Sector Index = +12% → PASS.
- Win Rate Upgrade: 3/3 Passed → 82% 1-year forward positive return probability (vs 66% single ATH).
```

---

## 17. Risk-Based Position Sizing & Pre-Decided Exits
- **Concept:** Systematic portfolio construction where position size is dynamically calculated using a hard pre-decided exit price (e.g. 200-day EMA).
- **Position Sizing Formula:**
  $$\text{Portfolio Allocation \%} = \frac{\text{Max Allowed Risk \% of Total Portfolio}}{\text{Percentage Distance between Entry Price and Exit Price}}$$
  $$\text{Percentage Distance \%} = \frac{\text{Entry Price} - \text{Exit Price}}{\text{Entry Price}} \times 100$$
- **Worked Case Example:**
  - Portfolio Capital: ₹1,00,00,000 | Max Risk per Stock: 1.2% (₹1,20,000).
  - Scenario A: Entry ₹100, 200 EMA Exit ₹80 -> Distance = 20%.
    - Allocation % = $1.2\% / 20\% = 6.0\%$ (Position = ₹6,00,000).
  - Scenario B: Entry ₹100, 200 EMA Exit ₹70 -> Distance = 30%.
    - Allocation % = $1.2\% / 30\% = 4.0\%$ (Position = ₹4,00,000).

### Pre-Execution Requirements — Strategy 17
```
□ Total Portfolio Capital amount (user must provide)
□ Maximum Allowed Risk % per trade (default = 1.2% of portfolio capital)
□ Target Stock Entry Price and 200-day EMA Exit Price
```

### Failure Modes & Hard Stop Rules — Strategy 17
```
❗ Over-allocating beyond the mathematically calculated position size due to high conviction
❗ Moving or waiving the 200-day EMA exit price down when price approaches the exit
❗ Gap-down open below 200 EMA exit causing slippage beyond max allowed 1.2% risk
```

### Worked Numerical Example — Strategy 17
```
Position Sizing Calculation:
- Total Portfolio: ₹1,00,00,000 | Max Risk Cap: 1.2% (₹1,20,000 max loss).
- Scenario A (Tight Stop): Entry Price = ₹100 | 200 EMA Exit = ₹80.
  - Distance % = (100 - 80) / 100 * 100 = 20%.
  - Allocation % = 1.2% / 20% = 6.0% of Portfolio (Position Size = ₹6,00,000 / 6,000 shares).
- Scenario B (Wide Stop): Entry Price = ₹100 | 200 EMA Exit = ₹70.
  - Distance % = (100 - 70) / 100 * 100 = 30%.
  - Allocation % = 1.2% / 30% = 4.0% of Portfolio (Position Size = ₹4,00,000 / 4,000 shares).
```

---

## 18. "Saatvik" (Ethical/Sin-Free) Quant Filter
- **Concept:** Structural ESG and ethical exclusion screening filter based on humanitarian and Jain principles applied prior to quantitative evaluation.
- **The 6 Sin Business Exclusion Categories:**
  1. **Animal Slaughter & Processing:** Meat processing, abattoirs, leather raw materials.
  2. **Liquor & Alcohol:** Distilleries, breweries, liquor distribution.
  3. **Tobacco & Cigarettes:** Cigarette manufacturing, gutkha, pan masala.
  4. **Leather Goods:** Tanning, leather apparel, leather footwear.
  5. **Casinos & Gambling:** Gaming platforms, betting, casino resorts.
  6. **Hotels & Hospitality:** Hotels deriving majority revenue from non-vegetarian dining and alcohol sales.

### Pre-Execution Requirements — Strategy 18
```
□ Company Annual Report revenue breakdown by business segment (user must provide)
□ Product portfolio verification against the 6 Sin Business Categories
□ Subsidiary and joint-venture revenue line audit
```

### Failure Modes & Hard Stop Rules — Strategy 18
```
❗ Any revenue derived from Animal Slaughter, Alcohol, Tobacco, Leather, Gambling, or Sin Hospitality
❗ Concealed sin business revenue inside "Other Operating Income" or JV accounts
❗ Immediate Hard Exit: Tagged as FAIL; excluded from all further financial/technical screening
```

### Worked Numerical Example — Strategy 18
```
Saatvik Filter Audit Execution:
- Candidate Company: Diversified Conglomerate.
- Segment Audit: Segment A (FMCG Foods) = 60% Revenue; Segment B (Paperboards) = 25% Revenue; Segment C (Cigarettes/Tobacco) = 15% Revenue.
- Filter Evaluation: Segment C hits Sin Category #3 (Tobacco & Cigarettes).
- Audit Result: FAIL (Immediate Hard Disqualification). Company is purged from universe regardless of financial or momentum scores.
```

---
End of Document — Domain 48

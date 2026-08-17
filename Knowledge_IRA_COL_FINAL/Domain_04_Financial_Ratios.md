# Domain 4 — Financial Ratios
Version: 1.0 | Status: Production Ready

---

## Purpose
Ratios convert raw financial statement data into comparable, standardized metrics for assessing performance, health, and value across time periods and peer companies.

---

## Ratio Categories

### 1. Profitability Ratios
- Gross Margin = Gross Profit / Revenue
- EBITDA Margin = EBITDA / Revenue
- Net Profit Margin = PAT / Revenue
- Return on Equity (ROE) = PAT / Average Shareholders' Equity
- Return on Capital Employed (ROCE) = EBIT / Capital Employed
- Use: Measures how efficiently a company converts revenue and capital into profit.

### 2. Liquidity Ratios
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio (Acid-Test) = (Current Assets – Inventory) / Current Liabilities
- Cash Ratio = Cash & Equivalents / Current Liabilities
- Use: Assess short-term solvency and ability to meet near-term obligations.

### 3. Leverage (Solvency) Ratios
- Debt-to-Equity = Total Debt / Shareholders' Equity
- Debt-to-EBITDA = Total Debt / EBITDA
- Interest Coverage Ratio = EBIT / Interest Expense
- Net Debt = Total Debt – Cash & Equivalents
- Use: Measures financial risk and capacity to service debt obligations.

### 4. Efficiency (Activity) Ratios
- Asset Turnover = Revenue / Average Total Assets
- Inventory Turnover = COGS / Average Inventory
- Receivables Turnover = Revenue / Average Trade Receivables
- Days Sales Outstanding (DSO), Days Inventory Outstanding (DIO), Days Payables Outstanding (DPO)
- Use: Measures how efficiently assets and working capital are utilized to generate revenue.

### 5. Cash Flow Ratios
- Operating Cash Flow Margin = CFO / Revenue
- Free Cash Flow Yield = FCF / Market Capitalization
- Cash Conversion Ratio = CFO / EBITDA
- Use: Validates whether reported profit is backed by actual cash generation.

### 6. Growth Ratios
- Revenue CAGR, EBITDA CAGR, EPS CAGR (typically 3-year / 5-year / 10-year)
- Use: Measures historical growth trajectory; must be paired with quality assessment (organic vs. inorganic, volume vs. price).

### 7. Valuation Ratios
- Price-to-Earnings (P/E) = Market Price / EPS
- Price-to-Book (P/B) = Market Price / Book Value per Share
- EV/EBITDA = Enterprise Value / EBITDA
- Price/Sales (P/S), PEG Ratio = P/E / Earnings Growth Rate
- Dividend Yield = Dividend per Share / Market Price
- Use: Assesses relative cheapness/expensiveness versus peers, history, and growth.

### 8. Return Ratios
- Return on Assets (ROA) = PAT / Average Total Assets
- Return on Invested Capital (ROIC) = NOPAT / Invested Capital
- Use: Measures capital efficiency; ROIC vs. Cost of Capital (WACC) spread indicates value creation or destruction.

### 9. Coverage Ratios
- Interest Coverage, Debt Service Coverage Ratio (DSCR) = (Net Operating Income) / (Total Debt Service)
- Fixed Charge Coverage Ratio
- Use: Assesses cushion available to service fixed financial obligations, critical for leveraged companies.

### 10. Quality Ratios
- Accruals Ratio = (PAT – CFO) / Total Assets
- Earnings Quality = CFO / PAT
- Use: Detects potential earnings manipulation; persistently low CFO/PAT ratio is a warning sign.

---

## Application Framework for Research
1. Never evaluate a ratio in isolation — always compare against (a) company's own historical trend, (b) peer average, (c) industry benchmark.
2. Combine categories: a high ROE driven purely by leverage (not profitability/efficiency) is lower quality than one driven by margins.
3. Use DuPont Analysis to decompose ROE = Net Margin × Asset Turnover × Financial Leverage.
4. Pair valuation ratios with growth and quality ratios — cheap on P/E but poor ROIC may be a value trap.

---

## Red Flags / Cautions
- Rising ROE driven mainly by increasing leverage rather than improving margins or efficiency.
- Declining receivables/inventory turnover alongside reported revenue growth.
- Valuation ratios compared without adjusting for accounting differences across peers (e.g., lease accounting).
- Using trailing ratios without considering forward-looking business changes.

---

## Universal Rule Applied to This Domain
Present ratios with the underlying formula and source data used, and explicitly flag when peer or industry benchmark data is unavailable rather than estimating it.

---

## Worked Example
Company A: ROE = 24%, Debt/Equity = 1.8x. Company B: ROE = 22%, Debt/Equity = 0.3x. DuPont breakdown shows Company A's ROE is leverage-driven (Net Margin 6% × Asset Turnover 1.1x × Leverage 3.6x), while Company B's is margin/efficiency-driven (Net Margin 14% × Asset Turnover 1.2x × Leverage 1.3x). Conclusion: Company B's ROE is structurally higher quality despite the lower headline number.

## AI Trigger Keywords
ROE, ROCE, P/E ratio, debt-to-equity, current ratio, margin, DuPont, valuation multiple, financial ratio, benchmark, peer comparison, quick ratio, interest coverage.

## Cross-Domain Links
→ Domain 2 (raw statement inputs) · Domain 5 (Valuation multiples) · Domain 6 (Business quality corroboration) · Domain 12 (Industry-specific benchmarks).

## Conflict Rule
Quality/Cash Flow ratios outrank Growth/Valuation ratios when they conflict — a cheap, fast-growing but low-quality number is a trap, not a signal.

---
End of Document — Domain 4

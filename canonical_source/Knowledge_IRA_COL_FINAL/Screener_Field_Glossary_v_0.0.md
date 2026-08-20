# Screener Field Glossary v_0.0

**Purpose:** A compact reference so the AI correctly interprets whatever screener.in-style data you paste in — field names only, no new logic. Not a new engine, not a new skill — just vocabulary.

**Paste Target:** Standalone reference file — no merge needed, upload as-is.

---

## How To Use This

When you paste raw data (a screener export, a table of ratios, an annual report snippet) that uses any of these field names, the AI should map them directly to the terms already used throughout the Knowledge/Skill Library — no re-interpretation needed, no asking "what does this field mean."

---

## Core Fundamentals
Sales, OPM, Net Profit (PAT), Market Cap, Quarterly Sales, Quarterly PAT, YoY Quarterly Sales Growth, YoY Quarterly Profit Growth, P/E, Dividend Yield, P/B, ROCE, ROA, Debt/Equity, ROE, EPS, Debt, Promoter Holding, Change in Promoter Holding, Earnings Yield, Pledged %, Industry PE, Sales Growth, Profit Growth, CMP, Price/Sales, Price/FCF, EV/EBITDA, Enterprise Value, Current Ratio, Interest Coverage, PEG, Returns (3M/6M/1Y/3Y/5Y/7Y/10Y)

## Growth Metrics
Sales/Profit/EBITDA/EPS Growth over 3/5/7/10 years (and their medians), Operating Profit Growth

## Profitability Metrics
Average ROE / ROCE over 3/5/7/10 years, ROE 5Y Growth, ROA 3Y/5Y, OPM 5Y/10Y average, Average Earnings/EBIT 5Y/10Y

## P&L Line Items (Annual + Quarterly + Preceding Period variants)
Operating Profit, Other Income, EBITDA, Depreciation, EBIT, Interest, PBT, Tax, PAT, Extraordinary Items, Net Profit, Dividend, Material Cost, Employee Cost, OPM, NPM, GPM, EPS — each may appear tagged "Last Year," "Latest Quarter," "Preceding Quarter," or "Preceding Year Quarter." Treat all four period-tags the same way Domain 2 (Financial Statements) treats period-over-period comparison.

## Balance Sheet
Equity Capital, Preference Capital, Reserves, Secured/Unsecured Loan, Balance Sheet Total, Gross/Net Block, Revaluation Reserve, Accumulated Depreciation, CWIP, Investments, Current Assets/Liabilities, Contingent Liabilities, Total Assets, Working Capital, Lease Liabilities, Inventory, Trade Receivables/Payables, Face Value, Cash Equivalents

## Cash Flow
Cash from Operations (CFO), Free Cash Flow (FCF), Cash from Investing, Cash from Financing, Net Cash Flow, Cash Beginning/End of period — all available as Last Year, Preceding Year, and 3/5/7/10-year aggregates

## Valuation
Book Value (current + historical), Industry P/BV, Historical PE (3/5/7/10Y), Graham Number, Earning Power

## Ownership
FII/DII/Public Holding (+ change, + 3-year change), Unpledged Promoter Holding, Number of Shareholders (current + historical)

## Efficiency
Inventory Turnover, Asset Turnover, Debtor Days, Working Capital Days, Cash Conversion Cycle, Days Payable/Receivable/Inventory Outstanding — each with historical (3/5/7/10Y back) variants

## Advanced Quality
Piotroski Score, Financial Leverage, ROIC, Credit Rating, Exports % (current + historical)

## Technical
Volume (+ 1W/1M/1Y average), High/Low Price (+ all-time), Returns (1D/1W/1M), DMA 50/200 (+ previous day), RSI, MACD (+ Signal, + previous day)

## Forecast
Expected Quarterly Sales/Operating Profit/Net Profit/EPS, Expected Quarterly Sales Growth

## Dates
TTM Result Date, Last Annual Result Date, Last Result Date

## Flags
Is SME / Is Not SME

---

## Mapping Rule

If pasted data uses a field name from this glossary, treat it as equivalent to the corresponding term already used in:
- `Domain_04_Financial_Ratios.md` and `Domain_02_Financial_Statements.md` for standard metrics
- `AI_Multibagger_Discovery_Skill.md` Module 0 (Quick Screen) for screening thresholds
- `AI_Forensic_Accounting_Skill.md` for quality/red-flag detection

No new calculation logic is introduced by this glossary — it exists purely so raw pasted data doesn't need manual translation before analysis begins.

---

**Document:** Screener_Field_Glossary_v_0.0.md
**Version:** v_0.0
**Action:** Upload as standalone file — no merge required

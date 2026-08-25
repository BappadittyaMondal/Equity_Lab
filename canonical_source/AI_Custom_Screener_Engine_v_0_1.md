<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Custom Screener Engine (Dynamic Universal AST Engine)
> **Role:** Dynamic quantitative parameter screening and relative expression parser
> **Use when:** Screening equities using complex relative fundamentals, cash flow ratios, parenthetical disjunctions, and moving averages.
> **Evidence rule:** Execute AST expression trees strictly against point-in-time observations without synthetic fallbacks.

# AI Custom Screener Engine Specification

**Version:** v_0.1  
**Status:** Production Ready (Canonical)  
**Category:** Screening & Selection Engine  
**Module ID:** SCR-003  

---

## 1. Executive Summary & Purpose

The AI Custom Screener Engine (`CustomScreenerEngine`) provides a dynamic, Abstract Syntax Tree (AST) based query evaluation framework supporting 180+ Screener.in parameter aliases across 14 financial categories. It allows quantitative analysts and portfolio managers to write natural expression queries using field-to-field comparisons, mathematical multipliers, moving average volume thresholds, and cash-flow confirmation rules.

---

## 2. Query DSL Grammar & Syntax

The Screener Domain Specific Language (DSL) parses incoming text strings into nested boolean expression trees.

### Syntax Grammar Rules

1. **Conjunctions & Disjunctions:**
   - Primary clauses are joined by `AND` (case-insensitive).
   - Parenthetical disjunctions use `OR` inside clauses: `(ConditionA OR ConditionB)`.

2. **Operators Supported:**
   - Comparison: `>=`, `<=`, `>`, `<`, `==`, `=`
   - Arithmetic Multipliers: `*` on right-hand-side terms (e.g., `FieldA >= FieldB * 1.2`)
   - Division / Percentage Ratios: `100 * ((High price - Current price) / High price) < 35`

3. **Field Alias Resolution:**
   - Case-insensitive string matching across 180+ registered financial metrics.
   - Fallback substring matching for normalized financial terms.

---

## 3. Worked Query Examples

### Example 1: Strategic Growth & Cash Flow Quality Confirmation
```text
EPS growth 3Years >= Sales growth 3Years * 1.2 AND Cash from operations last year > Net profit last year * 1.2
```
- **Explanation:** Ensures EPS growth outpaces sales growth by at least 20% (operating leverage) and operating cash flow exceeds net profit by 20% (high cash conversion quality).

### Example 2: Asset Expansion & CWIP Reinvestment Disjunction
```text
(Net block > Net block 3Years back * 1.9) OR ((Net block + Capital work in progress) > 1.9 * (Net block preceding year + Capital work in progress preceding year))
```
- **Explanation:** Surfaces aggressive capex capacity expansion where gross fixed assets or work-in-progress has expanded by 90%+ over the baseline period.

### Example 3: Momentum & Institutional Volume Accumulation Screen
```text
100 * ((High price - Current price) / High price) < 35 AND 100 * (Current price / Low price - 1) > 40 AND Volume > Volume 1year average * 4.5 AND Volume 1week average > Volume 1year average * 2.5
```
- **Explanation:** Selects stocks trading within 35% of 52-week highs, up 40%+ from 52-week lows, with daily volume exceeding 4.5x the 1-year average and weekly volume 2.5x the 1-year average.

---

## 4. Comprehensive Parameter Dictionary (180+ Aliases across 14 Categories)

### Category 1: Core Fundamentals
- `Sales`, `Sales growth`, `OPM`, `OPM Latest`, `Profit after tax`, `PAT`, `Market Capitalization`, `Market Cap`, `Sales Latest Quarter`, `PAT Latest Quarter`, `YOY Quarterly Sales Growth`, `YOY Quarterly Profit Growth`, `Price to Earning`, `PE`, `Dividend Yield`, `Price to Book Value`, `Return on Capital Employed`, `ROCE`, `Return on Assets`, `Debt to Equity`, `Return on Equity`, `ROE`, `EPS`, `Debt`, `Promoter Holding`, `Change in Promoter Holding`, `Earnings Yield`, `Pledged Percentage`, `Industry PE`, `Current Price`, `CMP`.

### Category 2: Growth Metrics
- `Sales growth 3 years`, `Sales growth 5 years`, `Sales growth 7 years`, `Sales growth 10 years`, `Profit growth 3 years`, `Profit growth 5 years`, `Profit growth 7 years`, `Profit growth 10 years`, `EBITDA growth 3 years`, `EBITDA growth 5 years`, `EPS growth 3 years`, `EPS growth 5 years`, `Operating profit growth`.

### Category 3: Profitability & Return Ratios
- `Average return on equity 3 years`, `Average return on equity 5 years`, `Average return on capital employed 3 years`, `Average return on capital employed 5 years`, `OPM 5 year`, `OPM 10 year`.

### Category 4: Cash Flow & Quality
- `Cash from operations last year`, `Net profit last year`, `Free cash flow last year`, `Free cash flow 3 years`, `Free cash flow 5 years`, `Free cash flow 7 years`, `Free cash flow 10 years`, `Operating cash flow 3 years`, `Operating profit`.

### Category 5: Balance Sheet & Capex
- `Net block`, `Net block 3 years back`, `Net block preceding year`, `Capital work in progress`, `CWIP`, `CWIP preceding year`, `Working capital 3 years back`.

### Category 6: Technical & Price Action Metrics
- `Piotroski score`, `High price`, `Low price`, `Volume`, `Volume 1 week average`, `Volume 1 month average`, `Volume 1 year average`.

---

## 5. Error-Handling Behavior

1. **Unknown Term Fallback:** Unrecognized metrics default to `0.0` with a warning log, ensuring non-blocking AST execution.
2. **Missing Observations:** If a company lacks historical observations for a required metric, the clause evaluates safely as `False` without halting universe scanning.
3. **Division by Zero Protection:** All ratio divisions (e.g. Price/Low or High-Price percentage calculations) enforce explicit `> 0` checks on denominators to prevent ZeroDivisionError exceptions.

---

## 6. Machine Interface & Contract Schema

### HTTP Endpoint
`POST /api/v1/data/custom-screen`

### Request Schema
```json
{
  "query": "EPS growth 3Years >= Sales growth 3Years * 1.2 AND Cash from operations last year > Net profit last year * 1.2"
}
```

### Response Schema
```json
{
  "query_string": "string",
  "total_universe_scanned": 412,
  "total_results_found": 15,
  "results": [
    {
      "symbol": "RELIANCE",
      "name": "Reliance Industries Ltd",
      "current_price": 2850.5,
      "market_cap_cr": 1925000.0,
      "opm_pct": 18.5,
      "volume_1d": 4500000,
      "vol_1w_avg": 3800000,
      "vol_1y_avg": 2500000,
      "roe_latest": 14.2,
      "roce_latest": 12.8,
      "eps_latest": 85.4,
      "cfo_last_year": 115000.0,
      "net_block": 650000.0
    }
  ]
}
```

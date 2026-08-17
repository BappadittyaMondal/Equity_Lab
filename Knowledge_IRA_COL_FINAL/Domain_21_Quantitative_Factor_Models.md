# Domain 21 — Quantitative & Factor Models
Version: 1.0 | Status: Production Ready

## Purpose
Systematic, data-driven frameworks for evaluating and screening securities based on statistically persistent factors — complementing fundamental and technical analysis with a rules-based lens.

## Core Concepts

**1. Value Factor**
- Definition: Preference for statistically cheap securities relative to fundamentals (low P/E, P/B, EV/EBITDA).
- Use: Screen for undervaluation candidates; must be combined with quality checks to avoid value traps.

**2. Quality Factor**
- Definition: Preference for companies with strong profitability, low leverage, and earnings stability.
- Common metrics: High ROE/ROIC, low debt-to-equity, low earnings volatility, high accruals quality (see Domain 4).
- Use: Historically associated with more resilient performance through market cycles.

**3. Momentum Factor**
- Definition: Preference for securities with strong recent relative price performance, based on the tendency for trends to persist over medium-term horizons.
- Use: Often combined with quality/value factors to avoid chasing purely speculative momentum ("quality momentum").

**4. Size Factor**
- Definition: Historical tendency for smaller-capitalization companies to generate different risk-return characteristics than large-caps.
- Use: Informs market-cap segment allocation (large/mid/small-cap) within portfolio construction (see Domain 10).

**5. Low Volatility Factor**
- Definition: Preference for securities exhibiting lower historical price volatility.
- Use: Associated with more defensive positioning; relevant for risk-budget-conscious portfolio construction.

**6. Multi-Factor Models**
- Definition: Combining two or more factors (e.g., Quality + Value, or Value + Momentum) to improve robustness versus single-factor exposure.
- Use: Reduces the risk of single-factor drawdowns (e.g., pure value underperforming for extended periods).

**7. Factor Screening Process**
- Steps: Define universe → apply factor filters/rankings → apply sector/liquidity constraints → validate top candidates with fundamental research.
- Research use: Quantitative screening should generate a candidate shortlist, not a final investment decision — always followed by fundamental due diligence (Domains 1-9).

**8. Statistical Concepts**
- Correlation and R-squared: Measuring relationship strength between variables/factors.
- Standard Deviation: Measure of volatility/dispersion of returns.
- Sharpe Ratio: Risk-adjusted return measure = (Return – Risk-free rate) / Standard Deviation.
- Sortino Ratio: Similar to Sharpe but penalizes only downside volatility.
- Maximum Drawdown: Largest peak-to-trough decline, a key risk metric for strategy evaluation.

**9. Backtesting Principles**
- Definition: Testing a factor/strategy against historical data to assess hypothetical performance.
- Cautions: Survivorship bias (excluding delisted/failed companies skews results), look-ahead bias (using data not actually available at the time), overfitting (excessive parameter tuning to historical data).

## Application Framework
1. Use factor screens to narrow a large universe into a research-worthy shortlist efficiently.
2. Always validate quantitative shortlist candidates with fundamental analysis (Domains 2-9) before drawing conclusions — factors identify statistical patterns, not causal business quality.
3. Disclose backtesting limitations (survivorship bias, look-ahead bias) whenever historical factor performance is cited.

## Red Flags / Cautions
- Presenting backtested returns without disclosing survivorship bias or transaction cost assumptions.
- Over-optimizing factor parameters to historical data (curve-fitting) without out-of-sample validation.
- Treating a factor screen result as a standalone investment recommendation without fundamental corroboration.

## Universal Rule Applied
Quantitative outputs are statistical starting points, not investment conclusions — always disclose methodology limitations and combine with evidence-based fundamental verification.

---

## Worked Example
A pure low-P/E screen surfaces a stock at 5x earnings — statistically "cheap." Adding a quality filter (ROE > 15%, Debt/Equity < 0.5) removes it because ROE is 6% and leverage is 2.1x — the low P/E reflected genuine business weakness (value trap), not a mispricing. Multi-factor screening caught what single-factor screening missed.

## AI Trigger Keywords
screener, factor investing, quant model, backtest, Sharpe ratio, low volatility stocks, momentum stocks.

## Cross-Domain Links
→ Domain 4 (ratio inputs to factors) · Domain 5 (value factor ties to valuation) · Domain 6 (fundamental validation of screen output).

## Conflict Rule
Factor screen results are always subordinate to fundamental verification (Domains 1-9) — never output a factor score as a standalone conclusion.

---
End of Document — Domain 21

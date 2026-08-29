# Equity Lab — Institutional Strategy Backtest Report

**Generated:** 2026-08-29 17:46 UTC  
**Covered Period:** 2018-01-01 to 2026-08-28  
**Universe:** NSE Top 500 & Microcap High Conviction  
**Point-In-Time Enforced:** Yes (Zero Lookahead)  

---

## 1. Executive Summary

| Metric | Value |
|---|---|
| **Best Performing Strategy** | Institutional Multibagger Screener (E18) |
| **Average Annualized CAGR** | 26.77% |
| **Average Sharpe Ratio** | 1.71 |
| **Tested Strategies** | 6 |
| **Total Backtested Trades** | 1367 |

---

## 2. Strategy Performance Matrix

| Strategy | CAGR (%) | Sharpe Ratio | Max Drawdown (%) | Win Rate (%) | Total Trades |
|---|---|---|---|---|---|
| **Institutional Multibagger Screener (E18)** | 34.2% | 1.85 | -14.2% | 68.5% | 142 |
| **Growth Arbitrage Engine (E1)** | 28.6% | 1.62 | -16.8% | 64.1% | 210 |
| **Turnaround & Dislocation Engine (E2)** | 31.4% | 1.48 | -21.4% | 59.2% | 98 |
| **Growth Market Gap Evaluator (E3)** | 24.1% | 1.51 | -15.1% | 62.8% | 185 |
| **Forensic Quality & Accounting Gate (D18)** | 22.8% | 1.74 | -11.6% | 71.0% | 320 |
| **Options Volatility & Arbitrage (A2)** | 19.5% | 2.05 | -8.4% | 76.4% | 412 |

---

## 3. Methodology & Risk Control Notes
- **Point-In-Time Filtering:** All historical balance sheets, cash flow statements, and quarterly announcements are timestamp-indexed (`available_at`) to strictly prevent lookahead bias.
- **Transaction Costs & Slippage:** Modelled at 25 bps per round-trip trade.
- **Survivor Bias Remediation:** Includes delisted and suspended historical stocks.

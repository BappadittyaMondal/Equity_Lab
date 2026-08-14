# Technical Analysis — Data Input Template (Addendum v_0.0)

**Paste Target:** AI_Technical_Analysis_Master_Skill_v_0_0.md — insert as new "Pre-Flight Data Requirements" section, right after the existing "Pre-Flight Requirements"

---

## Why This Addendum Exists

This skill already has full indicator logic (Moving Averages, RSI, MACD, Bollinger Bands, OBV, ADX, Fibonacci — Modules 1–8). What it never specified was **exactly what data the user needs to paste in** for the AI to actually compute these — without a live price feed, the AI can only be as good as the numbers it's given. This addendum closes that gap. It does not add new indicator logic; it makes the existing logic usable.

---

## Minimum Data Required (Paste This In Before Requesting Technical Analysis)

For a **single-timeframe** analysis (e.g., daily chart only), provide:

```
Stock: [Name/Ticker]
Timeframe: [Daily / Weekly / Intraday]
Date Range: [At least 60 trading periods — 200+ preferred for 200-DMA]

OHLCV data (one row per period), minimum:
Date | Open | High | Low | Close | Volume

Example:
2026-07-01 | 1420 | 1435 | 1415 | 1428 | 3,200,000
2026-07-02 | 1428 | 1440 | 1422 | 1432 | 2,850,000
...
```

**Minimum period counts needed per indicator** (so the AI can tell you if your data is insufficient before running an incomplete analysis):

| Indicator | Minimum Periods Needed |
|---|---|
| 20-DMA / 50-DMA | 50 (for 50-DMA to be valid) |
| 200-DMA | 200 |
| RSI (14) | 15 |
| MACD (12,26,9) | 35 |
| Bollinger Bands (20,2) | 20 |
| ADX (14) | 28 (needs a warm-up period beyond the base 14) |
| Fibonacci Retracement | 1 clear swing high + 1 clear swing low (no minimum count, but must be visually/numerically identifiable in the data provided) |

**Rule:** If the data provided is shorter than an indicator's minimum, the AI states explicitly "insufficient data for [indicator] — need at least N periods" rather than computing an unreliable value silently.

---

## For Multi-Timeframe Confluence (Module 6B — Timeframe Conflict Resolution)

Provide OHLCV for **each** timeframe being compared (e.g., both Daily and Weekly), clearly labeled. The AI cannot infer a weekly trend from daily data alone with full reliability — always provide each timeframe's data separately if multi-timeframe analysis is requested.

---

## Where To Get This Data

This skill does not fetch data itself. Common sources: your broker's historical data export (Zerodha Kite, Upstox, etc.), NSE/BSE historical data downloads, or a financial data site's CSV export. Paste the relevant rows directly into the chat, or upload as a CSV/spreadsheet file.

---

## What This Does Not Fix

This addendum makes the existing indicator modules usable with pasted historical data. It does **not** provide live/real-time price updates, live order book depth, or automatic data retrieval — those require a connected market-data source (broker API or data connector), which is outside what any document in this project can do on its own.

---

## Self-Audit

- ✓ No new indicator logic added — Modules 1–8 remain the single source of truth for calculation methodology
- ✓ Does not overstate capability — explicitly states the live-data limitation rather than implying it's solved
- ✓ Gives the user a concrete, actionable template rather than a vague "provide price data" instruction

---

**Document:** Technical_Analysis_Data_Input_Template_v_0.0.md
**Version:** v_0.0
**Paste Into:** AI_Technical_Analysis_Master_Skill_v_0_0.md (after Pre-Flight Requirements)

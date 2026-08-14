<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Rule Based Options Systematic Strategies  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 45 — Rule-Based Options & Systematic Strategies

Version: 1.0 | Status: Production Ready (Canonical Expert Strategy)  
Expert Origin: Mr. Ankit Rai (Self-taught System Developer)

## Purpose
This domain establishes institutional, rule-based derivative and systematic trading methodologies covering non-directional arbitrage, probability option selling, mechanical time-based straddles, and trend-following delta hedging.

---

## 1. Option Arbitrage & Spreads Strategy
- **Concept:** Non-directional trading approach that exploits short-lived pricing inefficiencies, implied volatility skew distortions, or synthetic parity dislocations between options and futures without taking delta direction risk.
- **Execution Architecture:**
  - Standard structures: Iron Butterfly, Long/Short Butterfly spreads, Ratio Spreads (Front Ratio 1x2, Back Ratio 2x3).
  - Morning Panic Window Execution: Exploits market open gap-up/gap-down sessions between 09:15:00 AM and 09:15:30 AM (10-to-30-second window). When retail or institutional panic orders hit market depth with illiquidity, systems capture wide bid-ask spreads and mispriced legs.
- **Yield Evolution & HFT Impact:**
  - Historical returns: 30% to 40% annual yields in low-latency/pre-HFT market regimes.
  - Current market reality: High-Frequency Trading (HFT) and institutional co-location speed up efficiency, narrowing arbitrage margins to 12% to 14% annual yields.

### Pre-Execution Requirements — Strategy 1
```
□ Option Chain data: IV skew, bid-ask depth, strike price grid (user must provide)
□ Intraday timestamp confirmation: morning panic window (09:15:00 AM – 09:15:30 AM)
□ Co-location / execution latency & slippage tolerance metrics
```

### Failure Modes & Hard Stop Rules — Strategy 1
```
❗ Execution slippage exceeding expected spread width (erodes 12%–14% yield margin)
❗ HFT algorithmic liquidity absorption prior to order fill
❗ Leg execution failure (one side fills, second leg fails to execute)
```

### Worked Numerical Example — Strategy 1
```
Intraday 09:15:15 AM Morning Panic Window:
- Market open gap-down triggers retail panic order flow into Nifty option chain.
- Setup: Front Ratio Spread 1x2 (Buy 1 ATM Call, Sell 2 OTM Calls).
- Target Yield: 12% to 14% annualized net of slippage (down from historical 30%–40% pre-HFT).
- Execution Rule: If bid-ask slippage erodes captured spread below 12% annualized, cancel unexecuted legs immediately.
```

---

## 2. Range-Bound Probability Option Selling
- **Concept:** Systematic selling of high implied volatility options based on historical spot index range distribution for Nifty 50 and Bank Nifty.
- **Statistical Foundation:**
  - Base index trades in a range-bound environment 70% to 90% of trading sessions.
  - 5-year historical spot analysis reveals Nifty zero-DTE (days to expiration) average intraday range is ~187 points.
- **Quantitative Execution Rule:**
  - Calculate opening spot price at 09:16 AM.
  - Sell Out-of-the-Money (OTM) Call and Put options priced at 250+ points away from current spot price on zero-DTE session.
- **Probability & Win Rate:** Statistical probability of expiry worthless is 87% to 90%.

### Pre-Execution Requirements — Strategy 2
```
□ Current Nifty 50 spot price at 09:16 AM (user must provide)
□ Available zero-DTE weekly expiry Call and Put option chain (user must provide)
□ Confirmation that today is a weekly expiry session
□ Confirmation that India VIX is below 20 (regime check)
```

### Failure Modes & Hard Stop Rules — Strategy 2
```
❗ Spot price moves >200 points toward sold strike within first 2 hours of trading
❗ Intraday index expansion exceeding 300+ point outlier threshold
❗ Spike in India VIX > 25 signaling catastrophic trend expansion
```

### Worked Numerical Example — Strategy 2
```
Nifty Zero-DTE Expiry Session Setup:
- Opening Spot Price (09:16 AM): 19,000 points.
- 5-Year Intraday Avg Range Benchmark: 187 points.
- Sell 250+ Pt OTM Call Strike: 19,250 CE.
- Sell 250+ Pt OTM Put Strike: 18,750 PE.
- Win Rate Expectation: 87% to 90% probability of expiry worthless.
- Hard Stop Exit Trigger: If Nifty spot crosses 19,200 (+200 pts), exit position immediately to avoid outlier 300+ pt gap move.
```

---

## 3. Time-Based Straddle Selling
- **Concept:** Pure mechanical intraday theta decay collection by selling At-The-Money (ATM) Call and Put options simultaneously at precise pre-determined timestamps.
- **Execution Timestamps:** 09:20 AM, 09:25 AM, or 09:30 AM without relying on technical indicators or market direction predictions.
- **Regime Shift & Tail Risk Warning:**
  - Massive regime shift in modern option markets due to algo participation.
  - Mechanical time entry without directional stop-loss or delta hedge faces severe drawdown risk during strong trend days, gap extensions, or sudden volatility spikes.

### Pre-Execution Requirements — Strategy 3
```
□ Intraday entry timestamp confirmation (09:20 AM, 09:25 AM, or 09:30 AM)
□ Current ATM Call and ATM Put option premium prices (user must provide)
□ Pre-defined directional stop-loss or delta hedge parameters
```

### Failure Modes & Hard Stop Rules — Strategy 3
```
❗ Gap extension or trend day breakout without delta hedge
❗ Sudden volatility spike expanding ATM option premiums rapidly
❗ Algo participation triggering consecutive stop-loss hunting spikes
```

### Worked Numerical Example — Strategy 3
```
Intraday Time-Based Straddle Setup:
- Entry Timestamp: Exactly 09:20 AM.
- Action: Sell Nifty 19,000 ATM Call @ ₹80 + Sell Nifty 19,000 ATM Put @ ₹80 (Combined Premium = ₹160).
- Historical Win Rate: 65% to 75% theta decay capture.
- Stop-Loss Rule: Combined premium expansion to ₹208 (+30%) triggers hard stop exit to prevent trend day drawdown.
```

---

## 4. Trend-Following with Futures / Synthetic Futures
- **Concept:** High-delta directional trend strategy designed to capture large index breakouts (300 to 500+ points) and offset option selling drawdowns.
- **Execution Mechanism:** Uses Index Futures, Synthetic Futures (Long Call + Short Put), or high-delta options.
- **Trigger Indicator:** SuperTrend (e.g. 10,3 parameters).
  - SuperTrend Green / Buy signal -> Go long Futures / Synthetic Futures.
  - SuperTrend Red / Sell signal -> Short Futures / Synthetic Futures.
  - Let profits run without capping upside while maintaining trailing stop losses.

### Pre-Execution Requirements — Strategy 4
```
□ SuperTrend (10,3) indicator status on Nifty/Bank Nifty Futures (user must provide)
□ High-delta instrument selection (Index Futures or Synthetic Long Call + Short Put)
□ Pre-established trailing stop-loss level
```

### Failure Modes & Hard Stop Rules — Strategy 4
```
❗ SuperTrend whipsaw in sideways, low-volatility consolidation regime (win rate drops to 40%–50%)
❗ Failure of price to sustain 300–500 point trend expansion after breakout
```

### Worked Numerical Example — Strategy 4
```
Nifty Futures Trend-Following Setup:
- Signal: SuperTrend (10,3) turns Green on daily/hourly chart.
- Instrument: Synthetic Futures (Long 19,000 Call @ Delta 0.50 + Short 19,000 Put @ Delta 0.50).
- Target: Capture 300 to 500+ point trend expansion.
- Exit Rule: Hold position as long as SuperTrend remains Green; execute exit immediately when SuperTrend turns Red.
```

---

## Integrated Strategy Matrix
| Strategy | Direction | Primary Alpha Source | Typical Win Rate | Risk Profile | Key Failure Mode |
|---|---|---|---|---|---|
| Option Arbitrage | Non-Directional | Mispricing / Panic Spreads | High (>90%) | Low | Latency / Execution Slippage |
| Range Option Selling | Range-Bound | Statistical OTM Decay | 87% - 90% | Moderate | 300+ Pt Sudden Outlier Move |
| Time Straddle Selling | Neutral | Intraday Theta Decay | 65% - 75% | High | Unhedged Directional Spikes |
| Trend Futures | Directional | Trend Breakout Delta | 40% - 50% | Controlled | Choppy Range Volatility |

---
End of Document — Domain 45

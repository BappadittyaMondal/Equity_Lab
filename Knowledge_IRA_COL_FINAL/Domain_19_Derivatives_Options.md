# Domain 19 — Derivatives & Options
Version: 1.0 | Status: Production Ready

## Purpose
Derivatives provide hedging, risk transfer, and market sentiment signals relevant to research and portfolio risk management. This domain covers core instruments and their analytical use — not speculative trading strategy.

## Core Concepts

**1. Futures**
- Definition: Standardized contract to buy/sell an underlying asset at a predetermined price on a future date.
- Use in research: Futures premium/discount to spot price (basis) signals market sentiment; rising open interest with rising price suggests fresh bullish positioning.

**2. Options — Basics**
- Call Option: Right (not obligation) to buy underlying at strike price before/on expiry.
- Put Option: Right (not obligation) to sell underlying at strike price before/on expiry.
- Premium: Price paid for the option, comprising intrinsic value + time value.

**3. Option Greeks**
- Delta: Sensitivity of option price to underlying price movement.
- Theta: Time decay — rate at which option value erodes as expiry approaches.
- Vega: Sensitivity to implied volatility changes.
- Gamma: Rate of change of delta itself.
- Use: Understanding Greeks helps interpret institutional hedging behavior and risk positioning, relevant for market structure analysis.

**4. Implied Volatility (IV)**
- Definition: Market's expectation of future volatility, derived from option prices.
- India VIX: Benchmark implied volatility index for Nifty options — elevated levels signal market-wide risk aversion/uncertainty.
- Use: IV spikes around events (earnings, elections, budget) reflect anticipated uncertainty, useful as a sentiment gauge.

**5. Open Interest (OI)**
- Definition: Total number of outstanding derivative contracts not yet settled.
- Use: OI buildup patterns (long buildup, short buildup, long unwinding, short covering) help interpret positioning shifts, often used alongside price action for sentiment reads.

**6. Put-Call Ratio (PCR)**
- Definition: Ratio of put option volume/OI to call option volume/OI.
- Use: Extreme readings (very high or very low) are sometimes used as contrarian sentiment indicators, though reliability varies and should not be used in isolation.

**7. Hedging Applications**
- Portfolio hedging: Using index puts to protect against broad market downside.
- Covered calls: Writing calls against existing holdings to generate income, capping upside.
- Protective puts: Buying puts against holdings to limit downside while retaining upside.

**8. Corporate Use of Derivatives**
- Currency hedging: Companies with import/export exposure hedge forex risk via forwards/options.
- Commodity hedging: Companies hedge raw material cost volatility (e.g., oil, metals) via futures/swaps.
- Research use: Assess hedging policy disclosure — unhedged exposure in volatile input costs or currency is a risk factor (see Domain 9).

## Application Framework
1. Use derivatives data (OI, IV, PCR) as a supplementary sentiment/positioning indicator alongside fundamental and technical analysis — not as a standalone investment signal.
2. When assessing a company, review disclosed hedging policy in notes to accounts/MD&A for currency and commodity exposure management.
3. Avoid recommending specific speculative options strategies; focus on risk-management applications relevant to research and portfolio context.

## Red Flags / Cautions
- Companies using derivatives for speculative purposes beyond stated hedging policy (a governance and risk red flag).
- Treating short-term derivatives positioning data as a reliable long-term investment signal.
- Ignoring counterparty risk in over-the-counter (OTC) derivative exposures disclosed in notes.

## Universal Rule Applied
Derivatives content should support risk understanding and hedging context — never presented as speculative trading advice, and always distinguished from core fundamental investment merit.

---

## Worked Example
Ahead of results, a stock shows high call OI buildup at the 5% OTM strike alongside elevated IV — market pricing in an anticipated positive surprise. If results miss, both direction (delta) and volatility (vega) collapse simultaneously, often causing a sharper-than-expected fall — a pattern useful for interpreting post-results volatility, not for predicting direction beforehand.

## AI Trigger Keywords
options, futures, F&O, open interest, PCR, India VIX, implied volatility, hedge, derivatives.

## Cross-Domain Links
→ Domain 7 (sentiment corroboration with technicals) · Domain 9 (hedging as risk mitigant) · Domain 20 (corporate currency/commodity hedging).

## Conflict Rule
Derivatives sentiment data never overrides fundamental or governance conclusions — treat as short-term corroboration only.

---
End of Document — Domain 19

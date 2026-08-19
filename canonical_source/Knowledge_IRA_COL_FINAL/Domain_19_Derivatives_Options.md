<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Derivatives Options  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

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

## Option Greeks — Execution Reference Table

The 4 Greeks already defined above (Delta, Theta, Vega, Gamma) have direct practical relevance for the Category A derivative strategies in Domain 45. This table maps each Greek to its strategy-level execution meaning.

| Greek | Measures | ATM Typical Range | OTM Typical Range | Practical Meaning for Expert Strategies |
|---|---|---|---|---|
| **Delta** | Option price sensitivity to underlying price move | 0.45–0.55 | 0.10–0.35 | High-Delta (>0.70) instruments used in A4 Synthetic Futures to behave like directional futures. OTM options in A2 have low delta — their value decays, not tracks price. |
| **Theta** | Time decay per day (erosion of time value) | Highest near expiry | Lower for far-OTM | Core alpha source in A2 (range selling OTM options for theta decay) and A3 (ATM straddle selling for intraday theta). Theta accelerates rapidly in the final hours of 0-DTE sessions. |
| **Vega** | Sensitivity to Implied Volatility (IV) change | High for ATM | Moderate for OTM | Sell when IV is elevated (as in A2/A3); vega works in favour of sellers when IV subsequently drops. If IV spikes post-entry (e.g., news event), vega loss erodes P&L even if price stays flat. |
| **Gamma** | Rate of change of Delta itself | Highest near ATM at expiry | Low for OTM | Highest near ATM at expiry — accelerates directional risk in A3 (ATM straddle) if a strong trend develops. Gamma risk is the primary reason A3 requires a directional stop-loss or delta hedge. |

**Key Interaction Rule:** On 0-DTE sessions (relevant for A2 and A3), Theta and Gamma both accelerate rapidly toward market close. Theta benefits sellers; Gamma punishes them if a sharp directional move occurs in the final hour.

---

## India VIX — Regime Interpretation Framework

India VIX (the Nifty options implied volatility benchmark) determines the appropriate operating regime for all Category A derivative strategies. This framework uses ONLY the India VIX reference already defined in this domain.

| VIX Level | Regime | Implication for Category A Strategies |
|---|---|---|
| **VIX < 13** | Low Volatility | Option premiums compressed. A2 (Range Selling) and A3 (Straddle Selling) collect less premium. Win probability high but absolute yield reduced. A4 (Trend Futures) low volatility = fewer 300–500 pt breakouts. Overall: Low-reward environment. |
| **VIX 13–20** | Normal Regime | Optimal operating environment. This is the historical base for A2's 87%–90% win rate. Premiums are adequate, volatility is predictable, and 0-DTE range behaviour is closest to the ~187 pt historical average from Domain 45. |
| **VIX 20–25** | Elevated — Caution Zone | Premium income is higher (beneficial for sellers) but tail risk increases. A2's 250+ point OTM strike distance may be insufficient. A3 (Straddle) becomes higher risk. Apply additional strike buffer; reduce position size. Reference: A2 regime check gate in Domain 45. |
| **VIX > 25** | Hard Stop — Do Not Sell Options | This directly triggers the Hard Stop invalidation rules for both A2 (Range Option Selling) and A3 (Time Straddle Selling) as defined in Domain 45. Probability of 300+ pt outlier moves escalates sharply. Category A selling strategies are suspended in this regime. A4 (Trend Futures) may be the only viable Category A strategy in VIX > 25 environments. |

**Regime Monitoring Rule:** Check India VIX at 09:10 AM before executing any Category A strategy. If VIX has crossed 25 since the previous close, suspend option-selling strategies for the session.

---

## Open Interest + Price Action — 4-Scenario Combination Matrix

Using ONLY the 4 OI positioning patterns already defined in this domain (Long Buildup, Short Buildup, Long Unwinding, Short Covering), this matrix provides the analytical interpretation for each combination:

| OI Trend | Price Trend | Signal Name | Interpretation | Reliability |
|---|---|---|---|---|
| **Rising OI** | **Rising Price** | Long Buildup | Fresh bullish positioning — new participants entering long. Confirms upward price move with conviction. | Moderate |
| **Rising OI** | **Falling Price** | Short Buildup | Fresh bearish positioning — new participants entering short. Confirms downward move with conviction. | Moderate |
| **Falling OI** | **Rising Price** | Long Unwinding | Existing longs booking profits. Price rise is driven by short covering or position lightening, not fresh conviction. | Low |
| **Falling OI** | **Falling Price** | Short Covering | Existing shorts exiting (buying back). Price fall may decelerate as bearish positioning closes. Not a bullish signal — just exhaustion of an existing short position. | Low |

**Critical Reminder (from Application Framework, already stated above):** All OI + price combination signals are supplementary sentiment/positioning indicators. They must be used alongside fundamental analysis and technical context — never as a standalone investment signal, and never to override a forensic or governance gate finding. Reliability is inherently limited: OI data reflects positioning at a point in time and can reverse rapidly on news or macro events.

---
End of Document — Domain 19

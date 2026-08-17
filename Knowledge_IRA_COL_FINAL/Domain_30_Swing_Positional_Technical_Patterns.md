# Domain 30 — Swing & Positional Technical Patterns
Version: 1.0 | Status: Production Ready (New Domain)

## Purpose
Domain 7 covers general technical analysis; this domain provides the specific pattern vocabulary and timeframe discipline for 2-day to 10-day swing trades and 1-week to 2-month positional trades — the holding periods this library is built around.

## Core Distinction by Holding Period

**Swing (2-10 days):** Focus on short-term momentum ignition, volume spikes, and tight consolidation breakouts. Entries are more time-sensitive; exits are rule-based (target/stop), not thesis-based.

**Positional (1 week - 2 months):** Focus on base-building patterns, sustained accumulation, and early-stage trend formation. Allows more room for normal volatility; exits tied to trend continuation/breakdown, not just a fixed target.

## Core Patterns

**1. Volume Dry-Up Before Breakout**
- Price consolidates in a tight range with progressively declining volume over 2-4 weeks — signals seller exhaustion.
- A subsequent volume spike (2x+ average) breaking the range top is a higher-quality signal than a breakout without this prior dry-up.

**2. Base-Building Pattern**
- Extended sideways consolidation (often 4-12 weeks) after a decline, with price stabilizing in a defined range — forms the "base" from which a positional move can launch.
- Higher-quality bases show progressively narrowing range (volatility contraction) rather than continued wide swings.

**3. Momentum Ignition**
- Sharp, high-volume move breaking out of a base or consolidation, often on a specific news/results trigger.
- Distinguish genuine ignition (sustained follow-through over subsequent sessions) from a single-day spike that reverses (common in illiquid small-caps — cross-reference Domain 29).

**4. Sudden Volume Spike Interpretation**
- Volume spike + price up + closing near day's high = bullish accumulation signal.
- Volume spike + price up + closing near day's low (long upper wick) = distribution/selling into strength, a caution signal despite the "up" day.
- Volume spike with no clear direction (doji-like) after a sustained move = potential exhaustion/reversal signal.

**5. Delivery Percentage Confirmation**
- In Indian markets, delivery % (shares actually taken for delivery vs. intraday-squared-off) rising alongside a price move signals genuine investment demand, not just speculative/intraday churn.
- A price breakout on high volume but low delivery % is a weaker, more speculative signal.

**6. Pullback-to-Support Entry (Positional)**
- After a breakout, price often pulls back toward the breakout level (now acting as support) before resuming the trend — this retest, if it holds on lower volume than the breakout, offers a lower-risk entry than chasing the initial breakout.

**7. Relative Strength vs. Sector/Index**
- A stock outperforming its sector index during a broad market pullback signals underlying strength — prioritize such names for positional entries once the broader market stabilizes.
- A stock underperforming during a sector rally is a caution signal even if the standalone chart looks acceptable.

## Application Framework — Entry/Exit Discipline
1. **Define holding-period intent before entry** — a swing setup and a positional setup have different stop-loss and target logic; don't blend them mid-trade.
2. **Require volume confirmation** for any breakout entry — price alone without volume is a weak signal, especially in small/micro-caps (Domain 29).
3. **Pre-define stop-loss and target before entry**, sized appropriately for the holding period (tighter for swing, wider for positional to allow normal volatility).
4. **Never take a technical entry that conflicts with a forensic or governance red flag** (Domain 24, Domain 8) — technical strength cannot substitute for fundamental safety, especially in swing trades where you're relying on the stock to remain tradeable through your holding period.
5. **Scale position sizing to setup quality** — a volume-dry-up + breakout + delivery confirmation setup deserves more size than a single unconfirmed signal.

## Worked Example
A stock consolidates in a ₹95-105 range for 5 weeks with declining daily volume (from 8 lakh shares/day to 3 lakh shares/day) — classic volume dry-up. It then breaks above ₹105 on volume of 18 lakh shares with delivery % rising from 25% to 48%, closing near the day's high. Two sessions later it pulls back to ₹106-108 (former resistance, now support) on volume of just 4 lakh shares before resuming upward. This sequence — dry-up, confirmed breakout, healthy pullback on low volume — is a well-formed positional entry setup, distinctly higher quality than a single-day volume spike with no prior base.

## Red Flags / Cautions
- Chasing a breakout on the first day without volume/delivery confirmation, especially in illiquid names.
- Ignoring that a "breakout" occurred on a stock already flagged for forensic or governance concerns.
- Treating every volume spike as bullish — direction of the day's close (near high vs. near low) changes the interpretation entirely.
- Applying swing-trade stop-loss discipline to a positional thesis (getting stopped out on normal volatility) or vice versa (holding a failed swing trade "positionally" after the setup has clearly failed).

## AI Trigger Keywords
breakout, swing trade setup, positional entry, volume spike, base pattern, delivery percentage, support resistance entry, is this a good entry point, momentum stock.

## Cross-Domain Links
→ Domain 7 (general technical foundation) · Domain 24/8 (mandatory safety gate before any technical entry) · Domain 29 (liquidity context for small-cap technical entries) · Domain 28 (volume story overlap for multibagger screening).

## Conflict Rule
Technical setup quality never overrides a forensic or governance red flag — a "perfect" breakout chart on a stock with fresh forensic concerns should be passed or, at minimum, sized down sharply and treated as high-risk speculation, not a core setup.

## Universal Rule Applied
Technical analysis improves timing, not business quality (per Domain 7's core rule) — this applies with extra force in swing/positional trading, where the temptation to let a good chart override fundamental caution is highest.

---
End of Document — Domain 30

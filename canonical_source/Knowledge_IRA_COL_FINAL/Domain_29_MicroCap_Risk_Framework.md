<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** MicroCap Risk Framework  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 29 — Micro/Small-Cap Risk Framework
Version: 1.0 | Status: Production Ready (New Domain)

## Purpose
Micro and small-cap investing carries structurally different risks than large-cap investing — liquidity, disclosure quality, and manipulation risk are materially higher. This domain provides risk controls specific to this market-cap segment, essential given the swing/positional trading style this library is built for.

## Core Principle
The same fundamental thesis that would be "safe enough" in a large-cap requires additional risk controls in a micro-cap purely due to structural factors — position sizing and exit discipline matter as much as stock selection here.

## Core Risk Categories

**1. Liquidity Risk**
- Average daily trading volume/value determines your realistic position size and exit speed.
- Rule of thumb: avoid taking a position that would represent more than 10-15% of a stock's average daily traded value — larger positions risk moving the price against you on exit.
- Illiquid stocks can gap down significantly on bad news with no buyers at intermediate prices — exit risk is asymmetric to entry risk.

**2. Price Manipulation / Operator Risk**
- Circular trading patterns: repeated buying/selling among a small group of connected entities to create artificial volume/price trends.
- Sudden unexplained price run-ups with no corresponding fundamental news or disclosure — check exchange surveillance actions (GSM/ASM categorization by SEBI/exchanges).
- Watch for: stocks moved to Graded Surveillance Measure (GSM) or Additional Surveillance Measure (ASM) lists — these carry trading restrictions and elevated risk.

**3. Disclosure Quality Risk**
- Small-caps often have weaker investor relations, less analyst coverage, and lower disclosure rigor than large-caps — information asymmetry is higher.
- Annual report quality varies widely; some micro-caps provide minimal MD&A detail compared to institutional-grade disclosure.
- Verify basic facts (registered office, auditor identity, related-party details) independently rather than assuming standard-quality disclosure.

**4. Promoter Concentration Risk**
- In micro-caps, business outcomes are often disproportionately dependent on a single promoter/founder's decisions and integrity — succession risk and key-person risk are elevated.
- Promoter pledge (cross-reference Domain 24) is a sharper risk signal here than in large-caps, since forced selling on pledge invocation can be a larger % of free float.

**5. Circuit Filter Risk**
- Many small/micro-caps trade with tighter daily circuit filters (2%/5%/10%) — this limits your ability to exit quickly in a falling market; a stock can be "locked" at the lower circuit with no buyers for multiple sessions.
- Factor this into position sizing: assume worst-case exit may take several sessions, not one.

**6. Corporate Action / Dilution Risk**
- Small-caps more frequently use preferential allotments, warrants, and rights issues that can dilute existing shareholders — verify whether recent/planned issuances are at fair value or favor insiders.

## Application Framework — Position Sizing & Risk Controls
1. **Cap individual micro/small-cap position size** meaningfully smaller than a large-cap position in the same portfolio — reflect the elevated single-stock risk in sizing, not just conviction.
2. **Check GSM/ASM status** before entry — avoid or heavily discount conviction on stocks under active surveillance restriction.
3. **Verify average daily traded value** covers your intended position size comfortably on both entry and likely exit.
4. **Set a hard stop-loss level before entry**, sized wider than a large-cap stop to account for circuit-filter gap risk, but still bounded — never average down into an illiquid, deteriorating position.
5. **Always run Domain 24 (Forensic) and Domain 8 (Governance) screens** — these matter more here than in any other segment.
6. **Diversify across positions** rather than concentrating — single-stock idiosyncratic risk (fraud, promoter issue, sudden delisting risk) is higher in this segment than sector or macro risk.

## Worked Example
A micro-cap trades ₹15 lakh average daily value. A trader considers a ₹3 lakh position (20% of daily value) — this exceeds the 10-15% guideline and risks meaningful slippage on both entry and exit, plus the stock has a 5% circuit filter. Sizing down to ₹1.5-2 lakh keeps the position within a realistic liquidity comfort zone, and the trader pre-defines a stop-loss level accounting for the possibility of a locked lower circuit for 1-2 sessions before an exit is achievable.

## Red Flags / Cautions
- Position sizing based purely on conviction/story attractiveness without a liquidity check.
- Ignoring GSM/ASM surveillance status because "the fundamentals look fine."
- Treating a micro-cap stop-loss the same way as a liquid large-cap stop — execution risk differs materially.
- Concentrating a large % of portfolio in a single micro-cap "high conviction" idea without diversification discipline.

## AI Trigger Keywords
micro cap risk, small cap risk, liquidity risk, GSM, ASM, circuit filter, is this stock safe, position size, how much to buy, penny stock risk, operator stock.

## Cross-Domain Links
→ Domain 24 (forensic screen — mandatory pairing) · Domain 8 (governance/promoter risk) · Domain 10 (portfolio-level position sizing rules) · Domain 14 (circuit filter/surveillance mechanics).

## Conflict Rule
Liquidity and surveillance-status risk override attractiveness of the fundamental/technical thesis when sizing a position — a great story in a GSM-flagged, illiquid stock still gets a small, risk-adjusted position, never a large one.

## Universal Rule Applied
Always disclose the liquidity profile (average daily traded value, circuit filter band, surveillance status) alongside any micro/small-cap recommendation — this context is as important as the fundamental thesis itself for this market-cap segment.

---
End of Document — Domain 29

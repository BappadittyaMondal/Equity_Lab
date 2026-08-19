<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Screening Strategies  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 40 — Screening Strategies
Version: 1.0 | Status: Production Ready (New Domain)

## Purpose
Concrete, actionable screening criteria combinations to *find* stock candidates matching each stock-finder type referenced throughout this library (multibagger, turnaround, SIP-growth, volume-story) — this domain is the practical "how do I generate a watchlist" layer that Domain 28 assumes as input.

## Core Principle
A screen generates candidates for research, never a final decision. Every screen output must pass through Domain 24 (Forensic) before further work.

## Screen 1: Early Multibagger Screen
- Market cap: micro/small-cap range (below your defined ceiling)
- Revenue/PAT CAGR (3-yr): accelerating, not just positive (latest year growth > 3-yr average growth)
- Piotroski F-Score: ≥6
- Promoter holding: stable or increasing over last 4 quarters
- Promoter pledge: nil or near-nil
- Fresh smart-money entry (Domain 27) in last 1-2 quarters: optional but high-value filter
- Debt/Equity: reasonable for the sector (not distressed)

## Screen 2: Turnaround Screen
- PAT: negative or depressed in trailing 2-3 years, now showing sequential (QoQ) improvement
- Debt trend: declining over last 3-4 quarters
- Interest coverage ratio: improving sequentially
- Management change OR clear disclosed corrective action in last 12-18 months
- New auditor/no adverse audit remarks in most recent report
- Promoter pledge: declining trend (if previously elevated) — rising pledge disqualifies

## Screen 3: SIP-Growth / Compounder Screen
- Revenue/PAT CAGR (5-yr): consistent 15-25%+, low year-to-year volatility
- ROE/ROCE: consistently >15% for 5+ years
- Debt/Equity: low, stable or declining
- Dividend payout: moderate (not near-zero, not excessive) — signals capital allocation balance (cross-reference Domain 41)
- Piotroski F-Score: ≥7
- Promoter holding: stable/increasing, pledge nil

## Screen 4: Volume Story / Uptrend Screen (Technical Overlay)
- Price: above key moving averages (e.g., 50-day and 200-day)
- Volume: recent average significantly above 3-6 month average (1.5x+)
- Delivery %: rising alongside volume (Domain 30)
- 52-week high proximity: trading within a defined % of 52-week high (momentum confirmation)
- **Must be paired with Screen 1 or 3 fundamentals** — pure technical screens without fundamental backing are higher-risk speculative trades, not investment candidates

## Screen 5: Valuation-SIP (Quality-at-Reasonable-Price) Screen
- PEG ratio: <1.5 (growth-adjusted value)
- P/E: below 5-year historical average band
- ROE: >15%
- Forensic screen: clean (mandatory)
- Sector-relative valuation: below peer average multiple despite comparable/better fundamentals (cross-reference Domain 12 industry benchmarks)

## Application Framework — Combining Screens
1. Run fundamental screens (1, 2, 3, or 5) first to generate the candidate list — never start from a pure technical/volume screen alone.
2. Apply Domain 24 (Forensic) as a mandatory second-pass filter — eliminate any candidate with 2+ red flags regardless of how well it scored on the primary screen.
3. Layer Domain 27 (Super-Investor) as a confidence booster, not a primary filter — its absence doesn't disqualify a candidate, but its presence raises research priority.
4. Apply Screen 4 (technical) only at the entry-timing stage for candidates that already passed fundamental + forensic screens — never as the primary discovery method.
5. Re-run screens periodically (quarterly, aligned with results season) — a candidate's screen status changes as new financials are disclosed.

## Worked Example
Running Screen 1 (Early Multibagger) on a watchlist of 200 small-caps yields 14 candidates with accelerating growth and clean pledge status. Applying the Domain 24 forensic filter eliminates 5 (2 with declining CFO/PAT ratio, 3 with recent auditor changes). Of the remaining 9, cross-checking Domain 27 shows 2 have fresh smart-money entries in the last quarter — these become top-priority for deep-dive fundamental research (Domain 6, Domain 28), while the other 7 remain a secondary research queue.

## Red Flags / Cautions
- Treating a screen pass as a buy signal — screens generate research candidates only.
- Over-optimizing screen thresholds to match a specific stock you already like (confirmation bias, Domain 11) rather than applying consistent criteria across the universe.
- Running only Screen 4 (technical/volume) without fundamental screening — this produces momentum-chasing candidates, not genuine multibagger/turnaround candidates.
- Not re-running screens regularly — a stock's fundamental screen status can deteriorate quickly, especially in small-caps.

## AI Trigger Keywords
stock screener, how to find multibagger, screening criteria, find turnaround stocks, stock finder, screen for growth stocks, find undervalued stocks.

## Cross-Domain Links
→ Domain 24 (mandatory forensic second-pass) · Domain 27 (smart-money confidence layer) · Domain 28 (deep-dive framework for screen output) · Domain 30 (technical entry timing for passed candidates).

## Conflict Rule
Fundamental + forensic screen results override any pure technical/volume screen signal in determining research priority — a technically exciting stock that fails the fundamental/forensic screen should not be elevated to a research candidate based on chart pattern alone.

## Universal Rule Applied
Screening criteria and thresholds should be applied consistently across the full universe being screened, not selectively adjusted to justify a pre-selected stock — disclose the exact criteria used for any screen output presented.

---
End of Document — Domain 40

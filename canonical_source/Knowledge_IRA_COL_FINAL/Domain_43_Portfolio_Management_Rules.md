<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Portfolio Management Rules  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 43 — Portfolio Management Rules (Swing/Positional Trading)
Version: 1.0 | Status: Production Ready (New Domain)

## Purpose
Domain 10 covers institutional portfolio theory (asset allocation, correlation, rebalancing concepts). This domain provides concrete, actionable rules specifically for active swing (2-10 day) and positional (1 week-2 month) trading in micro/small-cap stocks — the practical rulebook layer Domain 10 doesn't specify.

## Position Sizing Rules

**1. Maximum Single Position Size** — Cap any single swing/positional trade at a defined % of trading capital (commonly 5-10% for higher-conviction setups, 2-5% for speculative/exploratory positions) — never let one position's adverse move impair the overall capital base materially.

**2. Maximum Sector/Theme Exposure** — Cap aggregate exposure to a single sector or thematic cluster (e.g., all defence stocks, all PLI-beneficiary stocks) even if individual position sizes are within limits — correlated positions behave as one large position in a sector-wide drawdown.

**3. Liquidity-Adjusted Sizing** — Position size must respect Domain 29's liquidity guideline (not exceeding ~10-15% of average daily traded value) regardless of conviction level — conviction cannot override structural exit-risk constraints.

**4. Number of Concurrent Positions** — Define a maximum number of concurrent open swing/positional trades based on capacity to actively monitor each — over-diversification in an active trading style dilutes monitoring quality and doesn't reduce risk the way it does in a passive portfolio.

## Entry Rules

**1. Mandatory Pre-Entry Checklist** — Every entry must pass: Domain 24 (Forensic) clean/acceptable, Domain 8 (Governance) no active red-flag cluster, Domain 29 (liquidity) sized appropriately, and a defined stop-loss/target before entry, not after.

**2. Conviction-Tiered Sizing** — Higher position size only for setups with multiple corroborating signals (fundamental screen pass + forensic clean + technical confirmation + optionally smart-money corroboration) — a single-signal setup gets a smaller, exploratory position size.

**3. No Averaging Down on Broken Thesis** — If the original entry thesis (fundamental catalyst, turnaround root-cause fix, technical setup) is invalidated, do not add to the position at a lower price hoping for recovery — this is a Domain 11 (Behavioural Finance) loss-aversion trap, not a valid strategy.

## Exit Rules

**1. Stop-Loss Discipline** — Every position has a pre-defined stop-loss set at entry, sized to the holding-period type (tighter for swing, wider for positional to allow normal volatility) — honor it mechanically, don't renegotiate it emotionally mid-trade.

**2. Partial Profit-Booking Rule** — For positions reaching an initial target, consider booking partial profits (e.g., 30-50% of the position) while letting the remainder run with a trailing stop — balances profit realization with participation in extended moves.

**3. Time-Based Exit** — For swing trades specifically, define a maximum holding period even if neither stop nor target is hit — if a 2-10 day swing setup hasn't played out within its intended window, the original thesis (momentum/volume signal) has likely weakened; re-evaluate rather than holding indefinitely by default.

**4. Thesis-Invalidation Exit** — Exit immediately (independent of price/stop-loss level) if a new forensic or governance red flag emerges (Domain 24, Domain 8) — these override price-based exit rules entirely.

## Risk Budget Rules

**1. Maximum Portfolio Drawdown Trigger** — Define a portfolio-level drawdown threshold (e.g., a cumulative loss %) that triggers a mandatory reduction in position sizing/frequency until performance stabilizes — prevents compounding losses through unchanged risk-taking during a losing streak.

**2. Correlation-Aware Risk Budgeting** — When multiple open positions share a common risk factor (same sector, same macro theme, same smart-money cluster), treat them as a single risk unit for sizing purposes, per Domain 10's correlation principle, but applied at the active-trading position level.

**3. Cash Reserve Discipline** — Maintain a minimum cash/uninvested buffer at all times, sized larger during periods of elevated market-wide valuation or volatility (Domain 13 macro context) — full deployment at all times removes the flexibility to act on new opportunities and increases forced-selling risk during drawdowns.

## Application Framework
1. Every trade decision runs through: Screening (Domain 40) → Forensic/Governance gate (Domain 24, 8) → Position sizing rules (this domain) → Entry rules (this domain) → Pre-defined exit rules (this domain).
2. Review portfolio-level rules (drawdown trigger, correlation exposure, cash reserve) weekly, not just per-trade — active trading requires more frequent portfolio-level discipline checks than a passive long-term portfolio.
3. Log every rule violation (e.g., a stop-loss not honored, a position sized beyond the cap) as a discipline-tracking exercise — repeated violations signal a behavioural bias problem (Domain 11) requiring conscious correction.

## Worked Example
A trader has ₹10 lakh trading capital. Following the rules: max single position = 8% (₹80,000) for high-conviction setups, max 3 positions in the same sector cluster, max 6 concurrent positions total, minimum 15% cash reserve at all times. A new turnaround candidate (Domain 28) passes forensic screen and shows a confirmed technical breakout (Domain 30) — sized at 8% given multiple corroborating signals. A separate volume-story-only candidate (single signal, no fundamental confirmation yet) is sized at just 3% as an exploratory position with a tighter stop-loss given the higher speculative nature.

## Red Flags / Cautions
- Position sizing driven by excitement/conviction narrative rather than the pre-defined rules — this is exactly the discipline failure mode Domain 11 (Behavioural Finance) warns against.
- Ignoring correlated sector exposure across multiple "different" positions that actually share the same underlying risk factor.
- Removing or widening a stop-loss after entry because the position is "about to turn around" — this converts a disciplined trade into an undefined-risk bet.
- Zero cash reserve during high-volatility or elevated-valuation market phases, removing flexibility to act on new opportunities or absorb drawdowns.

## AI Trigger Keywords
position sizing rules, stop loss rule, how much to invest per stock, portfolio risk rules, profit booking, exit strategy, risk management rules, trading discipline.

## Cross-Domain Links
→ Domain 10 (conceptual portfolio theory foundation) · Domain 29 (liquidity-based sizing constraint) · Domain 11 (behavioural discipline failure modes) · Domain 24/8 (mandatory thesis-invalidation triggers) · Domain 40 (screening as the funnel feeding this rulebook).

## Conflict Rule
Pre-defined stop-loss and thesis-invalidation rules override in-the-moment conviction or emotional attachment to a position — no narrative development justifies abandoning a pre-set risk rule mid-trade.

## Universal Rule Applied
Portfolio rules should be defined and documented before entry, not adjusted retroactively to justify a position already held — any deviation from the stated rules must be explicitly disclosed as a deviation, not presented as the original plan.

---
End of Document — Domain 43

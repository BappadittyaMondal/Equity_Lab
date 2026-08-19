<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Financial Institution Analysis  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 26 — Financial Institution Analysis
Version: 1.0 | Status: Production Ready (New Domain)

## Purpose
Banks, NBFCs, insurers, and AMCs require a fundamentally different analytical framework than industrial companies — standard P&L/balance sheet analysis (Domain 2-5) misapplies here. This domain provides the correct statement structure, metrics, and valuation logic for financial institutions.

## Why Standard Frameworks Fail Here
- Revenue/COGS structure doesn't exist — income is interest/premium/fee-based.
- "Debt" is the raw material (deposits/borrowings), not a leverage red flag by default.
- Working capital concepts (Domain 3) don't apply.
- P/E is less useful than P/B or embedded value for parts of this sector.

## A. Banking

**Key Statement Items:** Net Interest Income (NII), Non-Interest/Fee Income, Operating Expenses, Pre-Provision Operating Profit (PPOP), Provisions, PAT.

**Core Metrics:**
- Net Interest Margin (NIM) = NII / Average Interest-Earning Assets
- Gross NPA % and Net NPA % — asset quality
- Provision Coverage Ratio (PCR) — cushion against bad loans
- Capital Adequacy Ratio (CAR) — regulatory solvency buffer
- CASA Ratio — low-cost deposit mix (higher = cheaper funding = structural advantage)
- Credit-to-Deposit Ratio — growth capacity signal
- Cost-to-Income Ratio — operating efficiency
- Return on Assets (ROA), Return on Equity (ROE)
- Slippage Ratio — fresh NPA formation rate (forward-looking asset quality signal)

**Valuation:** P/B (Price-to-Book) is primary, adjusted for ROE — higher sustainable ROE justifies higher P/B. P/E used secondarily. Compare P/B against sustainable ROE, not book value alone.

## B. NBFC (Non-Banking Financial Companies)

**Core Metrics:**
- AUM (Assets Under Management) growth
- NIM, Cost of Funds, spread over borrowing cost
- GNPA/NNPA — asset quality (often lags banks in disclosure rigor — scrutinize harder)
- Leverage (Debt/Equity) — NBFCs typically run higher leverage; assess against liability mix diversification
- Liability mix — diversified (bonds, CP, bank lines) vs. concentrated funding is a key risk differentiator
- ALM (Asset-Liability Mismatch) — critical vulnerability; short-term borrowing funding long-term assets is a red flag (2018 IL&FS-style risk)

**Valuation:** P/B adjusted for ROE, similar to banks; also P/E where earnings are stable.

## C. Insurance

**Core Metrics:**
- New Business Premium (NBP) — new sales momentum
- Value of New Business (VNB) Margin — profitability of new policies sold
- Persistency Ratio — policy renewal/retention rate (13th month, 61st month persistency commonly tracked)
- Embedded Value (EV) — PV of future profits from existing policies + net worth
- Combined Ratio (General Insurance) = (Claims + Expenses) / Premium; <100% = underwriting profit
- Solvency Ratio — regulatory capital adequacy (IRDAI mandated minimum)

**Valuation:** P/EV (Price to Embedded Value) is the primary metric for life insurers — not P/E or P/B.

## D. AMC (Asset Management Companies)

**Core Metrics:**
- AUM growth and mix (equity vs. debt — equity AUM carries higher margins)
- Yield/Revenue as % of AUM
- SIP book size and growth (recurring, sticky revenue base)
- Market share trend in active/passive segments
- Operating leverage — AMCs scale profit faster than AUM growth due to largely fixed cost base

**Valuation:** P/E on normalized earnings; also EV/AUM for relative comparison.

## Application Framework
1. Identify sub-category (bank/NBFC/insurer/AMC) before applying any metric — do not use bank NIM logic on an AMC.
2. Prioritize asset quality trend (NPA/slippage) over headline profit growth — provisioning cycles can mask true credit quality for several quarters.
3. For NBFCs, weight liability-side analysis (ALM, funding diversity) as heavily as asset-side growth — funding risk is the dominant failure mode in this sector.
4. Use P/B-vs-ROE framework for banks/NBFCs, P/EV for life insurers, EV/AUM or P/E for AMCs — never force a single valuation lens across all four sub-sectors.

## Worked Example
An NBFC shows AUM growth of 35% YoY (headline looks excellent) but funding is 70% short-term commercial paper against a loan book with average tenure of 3 years — a clear asset-liability mismatch. If CP rollover becomes difficult in a tight liquidity environment (as in 2018), this NBFC faces a funding crisis despite a "growing" loan book. Growth alone is not the signal; funding structure is.

## Red Flags / Cautions
- Rising GNPA with declining Provision Coverage Ratio simultaneously (double negative — deteriorating quality with shrinking cushion).
- NBFC funding concentrated in short-term instruments against long-tenure assets.
- Insurance persistency ratio declining while NBP is rising (indicates aggressive new sales masking poor retention/quality).
- Banks/NBFCs showing NIM expansion purely from delayed provisioning rather than genuine margin improvement.

## AI Trigger Keywords
bank stock, NBFC, NIM, NPA, CASA, insurance stock, embedded value, AMC, AUM, combined ratio, persistency, provision coverage, capital adequacy.

## Cross-Domain Links
→ Domain 2 (statement structure differs — use this domain's version) · Domain 4 (standard ratios largely don't apply here) · Domain 20 (credit market signals highly relevant for NBFC funding risk) · Domain 9 (Liquidity Risk is dominant for NBFCs).

## Conflict Rule
For financial institutions, this domain's metrics override generic Domain 4 ratio benchmarks entirely — P/E, current ratio, and standard leverage ratios from Domain 4 should not be applied to banks/NBFCs/insurers.

## Universal Rule Applied
Financial institution disclosures (asset quality, provisioning) are judgment-heavy areas prone to smoothing — always cross-check management-reported NPA figures against RBI/rating agency data where available rather than accepting company-disclosed numbers at face value.

---
End of Document — Domain 26

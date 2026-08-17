# IERL — Skills Reference
## Document 04: 25 Execution Modules — Complete Specifications (V5.1)

> **Version:** v_0.0 | **Destination:** Upload as Knowledge File in Claude Project (single file — replaces all prior versions, including all 9 standalone sector skill files) | **Last Updated:** July 2026
> **Upgrade from V5.0:** Skills 17–25 (the 9 sector analyzers) replaced with their fuller standalone-file versions, which contained deeper detail (pre-flight requirements, sector-specific red flags, worked examples) than the condensed versions previously embedded here. The 9 standalone files (`AI_Banking_Analysis_Skill.md`, `AI_NBFC_Analysis_Skill.md`, `AI_Insurance_Analysis_Skill.md`, `AI_Pharma_Analysis_Skill.md`, `AI_Defence_Analysis_Skill.md`, `AI_Manufacturing_Analysis_Skill.md`, `AI_Power_Utilities_Analysis_Skill.md`, `AI_Chemical_Analysis_Skill.md`, `AI_Microcap_Research_Skill.md`) are now retired — this file is their single source of truth.
> **Upgrade from V4.0:** 9 new Sector Analyzer skills added (Skills 17–25: Banking, NBFC, Insurance, Pharmaceutical, Defence & Aerospace, Manufacturing & Capital Goods, Power & Utilities, Chemical, and Microcap Research Protocol), each built to the same depth as Skills 01–15 (pre-flight requirements, mandatory sector-specific metrics, output templates, hard rules, and chaining). Sourced and consolidated from a 26-skill catalog; duplicate entries in that catalog (Banking/NBFC/Technical listed twice) were resolved to distinct skills only.
> **Upgrade from V3.0:** 1 new skill added (Skill 16 — Screener.in Query Integration & Saved Screens Library), plus a Master Field List constraining every screening criterion in this document to fields that actually exist on screener.in, and a Screen → Skill hand-off map closing the gap between raw screener output and deep-dive analysis.
> **Upgrade from V2.0:** 3 new skills added (Skill 13–15), all 12 original skills significantly expanded with pre-flight requirements, data inputs, failure protocols, AI execution notes, and inter-skill chaining rules.

---

## CRITICAL AI READING INSTRUCTION

When Claude reads this document, it must treat every Skill as a **mandatory Standard Operating Procedure**. Skills are not suggestions — they are enforced workflows. When a Skill is triggered:
- Execute **every step in sequence** — no steps may be skipped
- If data is unavailable for a step, document it explicitly as a gap, do not skip silently
- Apply the relevant Knowledge Files from the IERL library automatically
- Output must match the specified format exactly
- Confidence levels must be honest — never inflate conviction to appear useful

---

## Table of Contents

1. [What Is an IERL Skill?](#1-what-is-an-ierl-skill)
2. [Skill Triggering System](#2-skill-triggering-system)
3. [Skill Chaining Map](#3-skill-chaining-map)
4. [Universal Skill Failure Protocol](#4-universal-skill-failure-protocol)
5. [Skill 01 — Master Company Research](#5-skill-01--master-company-research)
6. [Skill 02 — Swing Stock Finder](#6-skill-02--swing-stock-finder)
7. [Skill 03 — Positional Opportunity Finder](#7-skill-03--positional-opportunity-finder)
8. [Skill 04 — Early Multibagger Finder](#8-skill-04--early-multibagger-finder)
9. [Skill 05 — Quarterly Results Analyzer](#9-skill-05--quarterly-results-analyzer)
10. [Skill 06 — Portfolio Auditor](#10-skill-06--portfolio-auditor)
11. [Skill 07 — Valuation Comparator](#11-skill-07--valuation-comparator)
12. [Skill 08 — Sector Rotation Analyzer](#12-skill-08--sector-rotation-analyzer)
13. [Skill 09 — Risk Auditor](#13-skill-09--risk-auditor)
14. [Skill 10 — IPO Analyzer](#14-skill-10--ipo-analyzer)
15. [Skill 11 — Turnaround Screener](#15-skill-11--turnaround-screener)
16. [Skill 12 — Watchlist Prioritizer](#16-skill-12--watchlist-prioritizer)
17. [Skill 13 — Concall & Management Commentary Analyzer](#17-skill-13--concall--management-commentary-analyzer) ⭐ NEW
18. [Skill 14 — Corporate Action Analyzer](#18-skill-14--corporate-action-analyzer) ⭐ NEW
19. [Skill 15 — Pre-Investment Master Checklist](#19-skill-15--pre-investment-master-checklist) ⭐ NEW
20. [Skill Output Quality Standards](#20-skill-output-quality-standards)
21. [Skill 17 — Banking Sector Analyzer](#21-skill-17--banking-sector-analyzer) ⭐ NEW
22. [Skill 18 — NBFC Analyzer](#22-skill-18--nbfc-analyzer) ⭐ NEW
23. [Skill 19 — Insurance Sector Analyzer](#23-skill-19--insurance-sector-analyzer) ⭐ NEW
24. [Skill 20 — Pharmaceutical Sector Analyzer](#24-skill-20--pharmaceutical-sector-analyzer) ⭐ NEW
25. [Skill 21 — Defence & Aerospace Sector Analyzer](#25-skill-21--defence--aerospace-sector-analyzer) ⭐ NEW
26. [Skill 22 — Manufacturing & Capital Goods Sector Analyzer](#26-skill-22--manufacturing--capital-goods-sector-analyzer) ⭐ NEW
27. [Skill 23 — Power & Utilities Sector Analyzer](#27-skill-23--power--utilities-sector-analyzer) ⭐ NEW
28. [Skill 24 — Chemical Sector Analyzer](#28-skill-24--chemical-sector-analyzer) ⭐ NEW
29. [Skill 25 — Microcap Research Protocol](#29-skill-25--microcap-research-protocol) ⭐ NEW
30. [Skill 16 — Screener.in Query Integration & Saved Screens Library](#30-skill-16--screenerin-query-integration--saved-screens-library)

---

## 1. What Is an IERL Skill?

A Skill is a **mandatory, structured execution module** that:

1. Defines exactly which analyst roles activate and in what sequence
2. Specifies required data inputs and how to handle missing data
3. Enforces the correct research sequence for a specific task type
4. Produces a standardized, institutional-quality output in a defined format
5. Connects to the correct IERL Knowledge Files automatically
6. Documents evidence quality and confidence for every conclusion

**Think of a Skill as:** a pre-programmed Standard Operating Procedure for a specific type of investment analysis. Just as a hospital has surgical protocols that cannot be abbreviated for convenience, IERL skills cannot be abbreviated for speed.

**Difference between a Skill and a casual analysis:**
- A casual analysis answers a question
- A Skill follows a complete process and produces an auditable output

---

## 2. Skill Triggering System

### Method 1 — By Skill Name
*"Run Skill 01 on Bajaj Finance"*

### Method 2 — By Intent (Auto-mapping)
Claude maps intent to skill automatically:

| User Says | Skill Triggered |
|-----------|----------------|
| "Analyze [Company]" / "Full report on [Company]" | Skill 01 |
| "Swing ideas" / "Short-term stocks" | Skill 02 |
| "3–6 month ideas" / "Positional opportunities" | Skill 03 |
| "Multibaggers" / "Small cap compounders" | Skill 04 |
| "Q[X] results for [Company]" | Skill 05 |
| "Audit my portfolio" / "Review my holdings" | Skill 06 |
| "Is [Company] cheap?" / "Compare [A] vs [B] valuation" | Skill 07 |
| "Which sectors to focus on?" | Skill 08 |
| "Portfolio risks" / "Risk audit" | Skill 09 |
| "Should I apply for [Company] IPO?" | Skill 10 |
| "Turnaround plays" / "Distressed recovery" | Skill 11 |
| "Prioritize my watchlist" | Skill 12 |
| "Concall analysis" / "What did management say?" | Skill 13 |
| "Buyback / bonus / rights analysis" | Skill 14 |
| "Pre-investment checklist for [Company]" | Skill 15 |

### Method 3 — By Artifact
Some artifacts auto-trigger skills when opened. See Document 05.

---

## 3. Skill Chaining Map

Skills may be chained in sequence. The output of one skill becomes the input of the next.

```
DISCOVERY CHAIN:
  Skill 08 (Sector Rotation)
      → Skill 02 (Swing Finder) [short term]
      → Skill 03 (Positional Finder) [medium term]
      → Skill 04 (Multibagger Finder) [long term]

DEEP RESEARCH CHAIN:
  Skill 01 (Master Research)
      → Skill 07 (Valuation Comparator) [if valuation is borderline]
      → Skill 15 (Pre-Investment Checklist) [mandatory before entry]

MONITORING CHAIN:
  Skill 05 (Quarterly Results)
      → Skill 13 (Concall Analyzer) [if management call available]
      → Skill 12 (Watchlist Prioritizer) [update status post-results]

RISK CHAIN:
  Skill 09 (Risk Auditor)
      → Skill 06 (Portfolio Auditor) [full portfolio context]
      → Skill 05 (Quarterly Results) [for high-risk holdings]

IPO CHAIN:
  Skill 10 (IPO Analyzer)
      → Skill 15 (Pre-Investment Checklist) [if applying]
      → Skill 07 (Valuation Comparator) [vs listed peers]

SECTOR DEEP-DIVE CHAIN:
  Skill 01 (Master Research) or Skill 08 (Sector Rotation)
      → Matching Sector Analyzer [17–25, based on company's sector]
      → Skill 09 (Risk Auditor) [sector-specific risk weighting]
      → Skill 07 (Valuation Comparator) [sector-appropriate valuation lens —
        e.g. P/B for banks, P/EV for life insurers, EBITDA/kg for chemicals]

  Sector routing:
    Bank                        → Skill 17
    NBFC / Housing Finance / MFI → Skill 18
    Insurance                   → Skill 19
    Pharma / API / Biosimilar   → Skill 20
    Defence / Aerospace         → Skill 21
    Manufacturing / Capital Goods / Auto Ancillary → Skill 22
    Power / Renewables / Utilities → Skill 23
    Specialty / Agro Chemicals  → Skill 24
    Any company with Market Cap ₹100–2,000 Cr → Skill 25 (runs FIRST,
      as a governance gate, before any other skill proceeds)
```

**When chaining:** Claude must explicitly state which skills are being chained and in what sequence before starting.

---

## 4. Universal Skill Failure Protocol

When any skill encounters insufficient data, Claude must follow this protocol:

### Tier 1 — Minor Gap (1–2 data points missing)
- Flag the gap clearly in the output
- State what would change if the gap were filled
- Continue with reduced confidence level
- Label affected sections as [DATA INCOMPLETE]

### Tier 2 — Moderate Gap (a full analytical category missing)
- State which category of analysis is blocked
- Explain what would be needed to complete it
- Provide partial output with explicit section: **⚠️ ANALYSIS INCOMPLETE — MISSING: [what is missing]**
- Reduce overall confidence by one level (High → Medium, Medium → Low)

### Tier 3 — Critical Gap (core financial data unavailable)
- Do not fabricate estimates to fill gaps
- Output a Data Requirements List before proceeding
- State explicitly: "This analysis cannot be completed to IERL standards without: [list]"
- Offer partial qualitative analysis only, labeled clearly as incomplete

### Never Permitted
- Proceeding as if data exists when it does not
- Using stale data (>12 months) without flagging it as stale
- Generating financial estimates without a stated basis
- Outputting a CIO Decision when Tier 3 gaps exist

---

## 5. Skill 01 — Master Company Research

**Version:** v_0.0 | **Estimated Depth:** Full institutional research report

### Triggers
- "Analyze [Company]"
- "Full research on [Company]"
- "Complete IERL report on [Company]"
- "Skill 01 on [Company]"

### Pre-Flight Requirements
Before beginning, Claude must confirm or request:
```
□ Company name and NSE/BSE ticker
□ Is this a financial company? (Bank / NBFC / Insurance / AMC)
  → If YES: activate KF-09 (Financial Institution Analysis) in Step 6
□ User's existing position? (None / Holding / Considering entry)
  → Affects emphasis in output (new research vs. thesis update)
□ Investment horizon preference? (Tactical / 1–3 years / 3+ years)
  → Affects valuation weight and risk framing
```

### Research Sequence (15 Steps — All Mandatory)

```
STEP 1 — Macro Economist
Inputs: KF-02 (Macroeconomic Framework)
Task:   Assess current macro environment's relevance to this company.
Output: Macro tailwind / headwind / neutral + 2–3 sentence justification

STEP 2 — Policy Analyst
Inputs: KF-03 (Policy & Regulatory Framework)
Task:   Identify government policies, budget allocations, and regulatory
        developments that directly affect this company or its sector.
Output: Policy exposure rating (Positive / Neutral / Negative / Uncertain)
        + specific policies named and their direction

STEP 3 — Sector Analyst
Inputs: KF-05 (Sector Intelligence Library)
Task:   Assess industry dynamics: structure, growth rate, competition,
        pricing power, disruption risk, regulatory complexity.
Output: Sector attractiveness rating + competitive structure summary
        + 3 key sector-level risks

STEP 4 — Business Analyst
Inputs: KF-06 (Business Quality Analysis)
Task:   Analyze business model, revenue streams, customer concentration,
        management quality, promoter track record, capital allocation history.
Output: Business Quality Score (0–10) + management assessment
        + key business model risks

STEP 5 — Governance Analyst
Inputs: KF-07 (Corporate Governance Framework)
Task:   Evaluate promoter behavior, board independence, related-party
        transactions, pledge levels, disclosure quality, audit history.
Output: Governance Score (0–10) + red flag count (0 = clean)
        + any disqualifying issues (if found, flag before proceeding)

⚠️ GOVERNANCE GATE: If Governance Score < 4 or any disqualifying issue found,
output a GOVERNANCE WARNING and seek explicit user direction before continuing.

STEP 6 — Financial Analyst
Inputs: KF-08 (Financial Statement Analysis)
        KF-09 (if financial company)
Task:   Full 5-year analysis of P&L, balance sheet, cash flow.
        Compute: Revenue CAGR, PAT CAGR, EBITDA margin trend, ROCE,
        ROE, FCF conversion rate, Debt/Equity trend, Working Capital cycle.
Output: Financial Quality Score (0–10) + 5-year financial trend summary
        + key financial ratios table

STEP 7 — Forensic Accountant
Inputs: KF-10 (Financial Quality & Forensic Accounting)
Task:   Scrutinize earnings quality: CFO vs PAT ratio, revenue recognition
        policies, contingent liabilities, audit qualifications, related-party
        fund flows, receivable velocity, inventory build patterns.
Output: Forensic Quality Score (0–10) + forensic red flag list
        + earnings quality verdict: Reliable / Questionable / Unreliable

⚠️ FORENSIC GATE: If Forensic Score < 4 or earnings quality = Unreliable,
output a FORENSIC WARNING. Do not proceed to valuation without user acknowledgment.

STEP 8 — Competitive Advantage Analyst
Inputs: KF-11 (Competitive Advantage & Moat Analysis)
Task:   Identify and rate the company's economic moat: type, width,
        durability, widening signals vs. erosion signals.
Output: Moat Type + Moat Width (Wide / Narrow / None / Eroding)
        + Moat Durability (years estimate) + top 3 moat risks

STEP 9 — Capital Allocation Analyst
Inputs: KF-06, KF-08
Task:   Evaluate historical capital allocation: ROCE trend, M&A track
        record, reinvestment rate vs. return on incremental capital,
        dividend policy, buyback history.
Output: Capital Allocation Rating (Excellent / Good / Average / Poor)
        + specific evidence for the rating

STEP 10 — Valuation Analyst
Inputs: KF-12A (Fundamental Valuation), KF-12B (Market Psychology)
Task:   Compute intrinsic value using minimum 2 methods.
        Required: DCF or Earnings Power Value (primary)
        Required: Peer relative valuation (secondary)
        Optional: Asset-based or SOTP (if applicable)
        Compute margin of safety at current price.
Output: Intrinsic Value range (Bull / Base / Bear)
        + Current valuation vs. historical band
        + Margin of Safety % + Verdict (Overvalued / Fair / Undervalued)

STEP 11 — Technical Analyst
Inputs: KF-13 (Technical Analysis & Market Structure)
Task:   Assess trend, momentum, and institutional activity.
        Identify: primary trend, key support/resistance, volume pattern,
        RSI reading, institutional buying/selling signals.
Output: Technical bias (Bullish / Neutral / Bearish)
        + entry zone from technical perspective
        + technical invalidation level

STEP 12 — Risk Analyst
Inputs: KF-14 (Portfolio Construction & Risk Management)
Task:   Build a risk register with all identified risks.
        For each risk: name, category, probability (H/M/L),
        impact (H/M/L), and mitigation/monitoring trigger.
Output: Risk Register (minimum 5 risks) + Overall Risk Rating (Low/Med/High/Very High)

STEP 13 — Behavioural Analyst
Inputs: KF-15 (Behavioral Finance)
Task:   Audit the research process itself for cognitive biases.
        Run the mandatory 8-point Behavioral Bias Audit Checklist.
Output: Bias Audit Report + any detected biases + conviction adjustment if needed

STEP 14 — Investment Committee
Task:   Structured debate between bull and bear case.
        Bull Advocate presents the 3 strongest reasons to invest.
        Bear Advocate presents the 3 strongest reasons to avoid.
        Synthesis: what would make each case right?
Output: Committee Vote (Buy / Hold / Pass / Strong Pass)
        + Key Debate Points + Areas of Uncertainty

STEP 15 — CIO Final Decision
Task:   Produce final recommendation in the mandatory 13-field format.
        Apply the 10 CIO Decision Rules.
        No recommendation without completing Steps 1–14.
Output: Full CIO Decision (see output format below)
```

### Output Format (Mandatory Structure)

```
═══════════════════════════════════════════════════
IERL MASTER RESEARCH REPORT
Company: [Name] | Ticker: [NSE/BSE] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════

SECTION 1 — EXECUTIVE SUMMARY
[250–300 words maximum. Must answer: What does this business do?
Is it a good business? Is it available at a good price? What is the
key risk? What is the CIO decision?]

SECTION 2 — ANALYST FINDINGS
  2.1 Macro & Policy Assessment
  2.2 Sector Dynamics
  2.3 Business Quality Analysis
  2.4 Corporate Governance Assessment
  2.5 Financial Analysis (5-Year)
  2.6 Forensic Accounting Review
  2.7 Competitive Advantage Assessment
  2.8 Capital Allocation Review
  2.9 Valuation Analysis
  2.10 Technical Context
  2.11 Risk Register

SECTION 3 — SCORES SUMMARY
  Business Quality Score:   [0–10]
  Governance Score:         [0–10]
  Financial Quality Score:  [0–10]
  Forensic Score:           [0–10]
  Moat Width:               [Wide/Narrow/None/Eroding]
  Capital Allocation:       [Excellent/Good/Average/Poor]
  Overall 100-Point Score:  [0–100]

SECTION 4 — INVESTMENT THESIS
  Bull Case: [What must happen for best outcome]
  Base Case: [Most probable scenario]
  Bear Case: [What could go wrong]

SECTION 5 — VALUATION SUMMARY
  Method 1:           [Name] → ₹[value]
  Method 2:           [Name] → ₹[value]
  Intrinsic Value:    ₹[low] – ₹[high]
  Current Price:      ₹[CMP]
  Margin of Safety:   [%]
  Verdict:            [Overvalued / Fair / Undervalued / Cheap]

SECTION 6 — BEHAVIORAL AUDIT
  Biases Checked:     [8-point list]
  Biases Detected:    [List or "None detected"]
  Conviction Impact:  [Unchanged / Downgraded by one level]

SECTION 7 — INVESTMENT COMMITTEE
  Bull Case Summary:  [3 strongest reasons to invest]
  Bear Case Summary:  [3 strongest reasons to avoid]
  Committee Vote:     [Buy / Hold / Pass / Strong Pass]

SECTION 8 — CIO FINAL DECISION
  Field 1  — Action:            [Buy / Accumulate / Hold / Reduce / Sell / Pass]
  Field 2  — Conviction:        [High / Medium / Low]
  Field 3  — CIO Confidence:    [%]
  Field 4  — Entry Price Range: ₹[X] – ₹[Y]
  Field 5  — Target Price:      ₹[Z] (Base Case, [timeframe])
  Field 6  — Stop-Loss:         ₹[A]
  Field 7  — Holding Period:    [months / years]
  Field 8  — Position Size:     [% of portfolio]
  Field 9  — Expected CAGR:     [X%–Y%]
  Field 10 — Key Assumption:    [The single most important thing that must be true]
  Field 11 — Key Risk:          [The single biggest risk to the thesis]
  Field 12 — Monitoring Trigger:[What would cause thesis review]
  Field 13 — Exit Trigger:      [What would cause immediate exit]

SECTION 9 — MONITORING CHECKLIST
  □ Next review date:
  □ Quarterly metric to watch:
  □ Governance event to watch:
  □ Valuation alert price:

SECTION 10 — EVIDENCE QUALITY
  Primary Sources Used:   [List]
  Data Freshness:         [Most recent data date]
  Missing Data:           [What was unavailable]
  Evidence Quality Rating:[Tier 1–3 per Evidence Hierarchy]
═══════════════════════════════════════════════════
```

### Special Branch — BFSI Companies
If company is a Bank, NBFC, Insurance company, or AMC:
- Step 6 MUST use KF-09 in addition to KF-08
- Additional metrics required: NIM, GNPA, NNPA, PCR, CAR, CD Ratio (for banks)
- For NBFCs: AUM growth, Cost of Funds, Net Interest Spread, Asset Quality
- For Insurance: Combined Ratio, Embedded Value, Persistency
- Valuation: P/Book is primary, not P/E

---

## 6. Skill 02 — Swing Stock Finder

**Version:** v_0.0 | **Timeframe:** 5–30 days | **Strategy:** Technical momentum with fundamental floor

### Triggers
- "Find swing trading opportunities"
- "Swing stocks for this week / month"
- "Short-term breakout ideas"

### Pre-Flight Requirements
```
□ Market regime check (MANDATORY before any ideas)
  → If Nifty 50 is below 200 DMA: output market warning, no swing ideas
  → If India VIX > 22: output volatility warning, reduce idea count to 2
□ User's risk appetite confirmed? (Default: moderate)
□ Timeframe preference? (5–10 days / 10–20 days / 20–30 days)
```

### Market Regime Filter (Must Pass Before Proceeding)
```
MARKET REGIME ASSESSMENT:
□ Nifty 50 trend:          Above 200 DMA = OK | Below = STOP
□ Market breadth:          >60% stocks above 50 DMA = OK | <40% = STOP
□ India VIX:               <18 = Ideal | 18–22 = Caution | >22 = STOP
□ FII activity (last 5d):  Net buying = Positive | Heavy selling = Caution
Regime Verdict: [Favorable / Caution / Not Favorable]
```

### Activation Sequence

```
① MACRO CONTEXT CHECK
   → Is broad market in uptrend? (200 DMA check)
   → Market breadth reading
   → VIX reading
   → If regime not favorable: output warning, stop here

② SECTOR RELATIVE STRENGTH
   → Which sectors are showing relative strength vs. Nifty?
   → Focus swing ideas within top 2–3 sectors only
   → Avoid weak sectors even if individual stock looks good

③ TECHNICAL SCREENING CRITERIA (All must pass)
   Required:
   □ Price above 20 EMA AND 50 EMA
   □ Volume: current day/week > 1.5x 20-day average
   □ RSI: 50–70 range (momentum building, not overbought)
   □ No major overhead resistance within 5% of entry price
   Optional (one or more):
   □ Breakout from consolidation (flat base, flag, triangle)
   □ New 52-week high with volume expansion
   □ Institutional accumulation signals in delivery %

④ LIQUIDITY FILTER
   → Minimum daily average volume: ₹5 Cr (NSE)
   → Avoid stocks where a single day's suggested position = >5% daily volume
   → Bid-ask spread must be reasonable (<0.5% for liquid stocks)

⑤ FUNDAMENTAL QUALITY FLOOR
   (Prevents swing trading in fundamentally broken companies)
   □ No active governance investigation / SEBI action
   □ Company not loss-making for 3+ consecutive years
   □ Debt/Equity < 3x (unless financial sector)
   □ No auditor qualification in last 2 years

⑥ RISK/REWARD CALCULATION
   → Define entry price (breakout level or support zone)
   → Define stop-loss (below key support, 5–8% maximum)
   → Define Target 1 (next resistance / 1:2 R:R minimum)
   → Define Target 2 (extended target / 1:3 R:R)
   → If R:R < 2:1, reject the idea regardless of setup quality
```

### Output per Idea (Maximum 5 ideas per run)

```
SWING IDEA #[N]
═══════════════════════════════════════════
Company:         [Name] | Ticker: [NSE]
Sector:          [Sector] | Market Cap: ₹[X] Cr
Setup Type:      [Breakout / Pullback / Range Breakout / 52W High]

ENTRY ZONE:      ₹[X] – ₹[Y]
STOP-LOSS:       ₹[Z] (% below entry)
TARGET 1:        ₹[A] (Risk/Reward: [X]:1)
TARGET 2:        ₹[B] (Risk/Reward: [Y]:1)
HOLDING PERIOD:  [X–Y days]

TECHNICAL SETUP: [2–3 sentence description of the chart pattern]
VOLUME SIGNAL:   [Volume trend description]
RSI:             [Current reading and trend]

FUNDAMENTAL NOTE: [1 sentence — why this is not a fundamentally broken stock]
LIQUIDITY:       [Daily avg volume in ₹ Cr — is it sufficient?]

KEY RISK:        [Single biggest risk to this specific trade]
CONVICTION:      [High / Medium / Low] — [reason in one sentence]
EXIT RULE:       [Exactly what triggers exit: price level or event]
═══════════════════════════════════════════
```

### Rules (Non-Negotiable)
- Minimum risk/reward: 2:1 always
- Maximum stop-loss: 8% from entry
- Maximum ideas: 5 per run
- Never recommend in unfavorable market regime
- Always include liquidity check
- Never recommend a company with active SEBI enforcement action

---

## 7. Skill 03 — Positional Opportunity Finder

**Version:** v_0.0 | **Timeframe:** 3–6 months | **Strategy:** Earnings catalyst + business quality + technical confirmation

### Triggers
- "Find positional ideas"
- "3–6 month opportunities"
- "Medium-term investment ideas"

### Pre-Flight Requirements
```
□ Minimum holding intention: 3 months confirmed
□ Risk appetite: Moderate (can handle 15–20% drawdown during hold)
□ Sector preferences or restrictions?
□ Market cap preference? (Large / Mid / Small / Any)
```

### Activation Sequence

```
① EARNINGS CYCLE POSITIONING
   → Where are we in the quarterly earnings cycle?
   → Which sectors are entering their seasonally strong quarter?
   → Which companies have upcoming result dates within 4–8 weeks?

② BUSINESS QUALITY FILTER
   Minimum thresholds (all required):
   □ ROE > 15% (last 3 years average)
   □ Revenue growth > 15% YoY (last 2 quarters)
   □ Debt/Equity manageable (< 1.5x for non-BFSI)
   □ Promoter holding stable or increasing

③ CATALYST CLASSIFICATION
   Catalyst must exist from one of these categories:
   Type A — Earnings Catalyst: upcoming results expected to beat estimates
   Type B — Order/Contract Catalyst: recently announced large order/contract
   Type C — Policy Catalyst: government spending / PLI / sectoral policy benefit
   Type D — Expansion Catalyst: capacity addition coming online
   Type E — Turnaround Catalyst: margins recovering after cyclical trough
   Type F — Management Catalyst: new CEO / promoter strategy shift
   
   → Identify catalyst type and expected timing

④ FINANCIAL TREND CHECK
   → Is revenue growth accelerating or decelerating?
   → Is EBITDA margin expanding or compressing?
   → Is PAT growth > Revenue growth? (operating leverage positive?)
   → FCF positive and growing?

⑤ VALUATION SANITY CHECK
   → Is the company trading below its 3-year average P/E?
   → Is PEG ratio < 1.5x given near-term earnings?
   → Institutional consensus: is estimate revision trend positive?

⑥ TECHNICAL CONFIRMATION
   → Primary trend: upward or basing?
   → Is price above 50 EMA?
   → Is relative strength vs. Nifty improving?
   → No major resistance within 10% of entry

⑦ RISK ASSESSMENT
   → What is the key risk to catalyst materialization?
   → What would invalidate this 3–6 month thesis?
   → Downside scenario price if thesis fails
```

### Output per Idea (Maximum 5 ideas)

```
POSITIONAL IDEA #[N]
═══════════════════════════════════════════
Company:          [Name] | Ticker: [NSE]
Sector:           [Sector] | Market Cap: ₹[X] Cr

INVESTMENT THESIS: [3–5 sentence description of WHY this stock NOW]

CATALYST:
  Type:           [A/B/C/D/E/F — see classification above]
  Description:    [Specific catalyst in one sentence]
  Expected Timing:[Month/Quarter when catalyst expected to materialize]
  Confidence:     [High / Medium / Low]

FINANCIAL PROFILE:
  Revenue Growth (YoY): [%]
  EBITDA Margin Trend:  [Expanding / Stable / Compressing]
  ROE:                  [%]
  Valuation:            [P/E vs. sector average]

TECHNICALS:
  Trend:          [Uptrend / Basing / Recovering]
  Entry Zone:     ₹[X] – ₹[Y]
  Stop-Loss:      ₹[Z] (thesis invalidation level)

TARGETS:
  3-Month Target: ₹[A] — Upside: [%]
  6-Month Target: ₹[B] — Upside: [%]

KEY RISKS:
  Primary Risk:   [Most important risk to this thesis]
  Exit Trigger:   [Exactly what would cause immediate exit]

CONVICTION:       [High / Medium / Low]
EVIDENCE BASIS:   [Primary sources used for this assessment]
═══════════════════════════════════════════
```

---

## 8. Skill 04 — Early Multibagger Finder

**Version:** v_0.0 | **Timeframe:** 3–10 years | **Strategy:** Structural growth + emerging moat + management quality

### Triggers
- "Find early multibagger stocks"
- "Small cap compounders"
- "Long-term wealth creation ideas"
- "Identify potential 5x / 10x stocks"

### Pre-Flight Requirements
```
□ Long-term conviction confirmed (minimum 3 years)
□ Can tolerate high volatility (30–50% drawdowns possible)
□ Position sizing understanding: max 3–5% per name
□ Market cap range preference: default <₹5,000 Cr
```

### Stage Gate Assessment (NEW in V3.0)
Before any multibagger analysis, classify the candidate into a stage:

```
STAGE CLASSIFICATION:
Stage 1 — Pre-Proof:    Revenue <₹100 Cr, ROCE improving but not yet excellent
                        → Highest risk, smallest position (1–2%)
Stage 2 — Early Proof:  Revenue ₹100–500 Cr, ROCE >12%, moat emerging
                        → High risk, small position (2–3%)
Stage 3 — Growing:      Revenue ₹500–2000 Cr, ROCE >15%, moat clear
                        → Moderate risk, normal small cap position (3–5%)
Stage 4 — Scaling:      Revenue >₹2000 Cr, ROCE >20%, moat solidifying
                        → Lower risk, full conviction position (5–7%)
```

### Quality Filters (Mandatory — All Must Pass for Stage 2+ Recommendation)

```
FINANCIAL QUALITY GATES:
□ Revenue growing >20% CAGR (minimum 3 years of data)
□ ROCE trend: improving (must be trending toward or above 15%)
□ FCF positive or turning positive within visible horizon
□ Debt: low or reducing (Debt/EBITDA < 3x)
□ Working capital discipline: receivable days not expanding unusually

MANAGEMENT QUALITY GATES:
□ Promoter ownership >40% (skin in the game)
□ No promoter pledge >20% of holdings
□ Concall quality: management gives guidance, then delivers
□ Capital allocation history: rational use of cash, no value-destructive M&A
□ Promoter background: relevant industry experience, no criminal proceedings

MARKET OPPORTUNITY GATES:
□ Total Addressable Market (TAM): >₹10,000 Cr preferred
□ Market penetration of the sector: <40% (underpenetrated)
□ Company's current market share: small (room to grow 5–10x)
□ Structural tailwind: policy, demographics, technology, income growth

COMPETITIVE ADVANTAGE GATES:
□ Evidence of emerging moat: pricing power, customer stickiness, cost advantage
□ Brand or relationship advantage visible
□ Network effect or platform dynamics (where applicable)
□ Switching cost evidence (customer reorder rates, retention)

GOVERNANCE GATES:
□ Clean audit history (no qualifications in 3 years)
□ Related-party transactions reasonable and disclosed
□ Board quality: at least 2 credible independent directors
□ No active SEBI/enforcement investigation
```

### Multibagger Scoring (0–100)

| Category | Max Points | What It Measures |
|----------|-----------|-----------------|
| Revenue Growth Quality | 20 | CAGR consistency, not just one year |
| Moat Stage & Strength | 20 | Emerging / Narrow / Wide + evidence |
| Management Track Record | 15 | Delivery vs. guidance, capital discipline |
| Market Opportunity | 15 | TAM size × penetration gap |
| Financial Quality | 15 | ROCE, FCF, balance sheet strength |
| Governance Quality | 10 | Clean history, board quality |
| Valuation | 5 | Not overvalued for its stage |

### Output per Idea

```
MULTIBAGGER CANDIDATE #[N]
═══════════════════════════════════════════
Company:          [Name] | Ticker: [NSE]
Stage:            [1 / 2 / 3 / 4]
Sector:           [Sector] | Market Cap: ₹[X] Cr

MULTIBAGGER SCORE:  [0–100]

TAM ASSESSMENT:
  TAM Size:       ₹[X] Cr
  Penetration:    [%] currently — [room for X% more]
  Growth Rate:    [% per year expected]

MANAGEMENT RATING: [Excellent / Good / Average / Poor]
  Key Evidence:   [Specific track record examples]

MOAT ASSESSMENT:
  Stage:          [Emerging / Narrow / Wide]
  Type:           [What kind of advantage]
  Durability:     [Estimated years]
  Erosion Risk:   [Main threat to moat]

GROWTH RUNWAY:
  Revenue Target: ₹[X] Cr in [Y] years (at [Z]% CAGR)
  ROCE Target:    [%] in [Y] years
  Return Potential: [X]x in [Y] years (base case)

CAPITAL ALLOCATION TRACK RECORD:
  [Key decisions made in last 3 years and their quality]

KEY RISKS (Multibagger-Specific):
  1. [Execution risk]
  2. [Competition risk]
  3. [Governance risk]
  4. [Valuation risk if narrative breaks]

POSITION SIZING:
  Stage-Based Max: [%]
  Recommended Entry: [%]
  Build-Up Strategy: [How to add if thesis proves out]

⚠️ MANDATORY WARNING: This is a high-uncertainty, long-duration bet.
Position size per IERL rules: never exceed [X]% at initial entry.
═══════════════════════════════════════════
```

---

## 9. Skill 05 — Quarterly Results Analyzer

**Version:** v_0.0 | **Purpose:** Assess quarterly performance + update thesis status

### Triggers
- "Analyze [Company] Q[X] FY[XX] results"
- "Review quarterly results for [Company]"
- "Skill 05 on [Company] results"

### Pre-Flight Requirements
```
□ Results data provided (P&L at minimum, balance sheet preferred)
□ Previous quarter's data for comparison
□ Year-ago quarter's data for YoY comparison
□ Original investment thesis available for thesis status update
□ Is this a seasonal business? (construction, agri, retail)
  → If YES: activate seasonal normalization (see below)
□ Has the company issued guidance or is it a no-guidance company?
```

### Seasonal Normalization (NEW in V3.0)
For seasonal businesses, raw YoY comparison can mislead:
```
Seasonal Sectors: Cement, FMCG Rural, Agri Input, Hospitality, Retail, Infrastructure
→ For these: compare to 2-year average of the same quarter
→ Flag whether this is a seasonally strong or weak quarter before analysis
→ Weight QoQ analysis more carefully for seasonal patterns
```

### Activation Sequence

```
① FINANCIAL ANALYST — HEADLINE NUMBERS
   Revenue:
   → Growth vs. last year same quarter (YoY)
   → Growth vs. last quarter (QoQ) [flag if seasonal]
   → Beat / In-line / Miss vs. estimates (if available)
   → Volume growth vs. price/mix growth (if separable)

   Margins:
   → Gross Margin % (current vs. YoY vs. 5-quarter trend)
   → EBITDA Margin % (same analysis)
   → PAT Margin % (same analysis)
   → Flag if margin compression or expansion is structural vs. one-time

   Cash Flow:
   → Operating Cash Flow vs. PAT (earnings quality check)
   → FCF = OCF – Capex (positive or negative?)
   → Working capital movement: did receivables or inventory spike?

   Balance Sheet:
   → Net Debt change (up or down vs. last quarter)
   → Any major asset or liability change worth noting?

② SECTOR ANALYST — COMPETITIVE CONTEXT
   → How did this company perform vs. sector peers this quarter?
   → Market share movement (if data available from segment disclosures)
   → Industry-level volume data to cross-check company's numbers
   → Is this an industry-wide trend or company-specific?

③ GOVERNANCE ANALYST — MANAGEMENT COMMENTARY
   Evaluate the investor presentation / concall transcript / press release:
   → Tone: Confident / Cautious / Defensive / Evasive?
   → Did management deliver on previous quarter's guidance?
   → New guidance given: is it credible given past delivery?
   → Any one-time items being called "non-recurring"?
   → Red flags: blame language, excessive qualifications, new accounting policies?
   → Related-party transactions disclosed this quarter?

④ FORENSIC CHECK — ONE-TIME ITEMS
   → Identify all one-time items in P&L
   → Calculate "adjusted PAT" (excluding one-time items)
   → Is the market being distracted by headline PAT vs. operational reality?
   → Write off or impairment charges: disclosed upfront or buried?

⑤ MONITORING DIVISION — THESIS STATUS UPDATE
   Compare current results against original investment thesis:
   
   □ Is the core growth driver of the thesis still intact?
   □ Are margins tracking per thesis expectations?
   □ Is the competitive position unchanged or better/worse?
   □ Are any of the original key risks materializing?
   
   THESIS STATUS (mandatory update, one of four):
   ⬆️ STRENGTHENED: Results exceeded thesis assumptions
   ➡️ UNCHANGED: Results consistent with thesis
   ⬇️ WEAKENED: One or more thesis elements not tracking
   ✗ INVALIDATED: Core thesis assumption has broken

⑥ VALUATION ANALYST — ESTIMATE REVISION
   → If results materially different from expectations: revise full-year estimate
   → Update target price if warranted
   → State: "No change to target" or provide revised target with reasoning
```

### Output Format

```
QUARTERLY RESULTS ANALYSIS
Company: [Name] | Quarter: Q[X] FY[XX] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════

HEADLINE RESULTS TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric          Q[X] FY[XX]   Q[X] FY[XX-1]  QoQ         YoY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revenue         ₹[X] Cr       ₹[Y] Cr        [+/-]%      [+/-]%
EBITDA          ₹[X] Cr       ₹[Y] Cr        [+/-]%      [+/-]%
EBITDA Margin   [X]%          [Y]%            [+/-] bps   [+/-] bps
PAT             ₹[X] Cr       ₹[Y] Cr        [+/-]%      [+/-]%
EPS             ₹[X]          ₹[Y]            [+/-]%      [+/-]%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EARNINGS QUALITY:
  OCF vs PAT:           [OCF as % of PAT — healthy: >80%]
  One-Time Items:       [List and adjusted PAT]
  Working Capital:      [Receivable / Inventory change]

SECTOR COMPARISON:
  [Company] vs sector average: [Better / In-line / Lagging]
  Estimated market share:       [Change if identifiable]

MANAGEMENT COMMENTARY:
  Guidance:     [Previous guidance vs. delivery]
  New Guidance: [What was said about next quarter / full year]
  Tone:         [Confident / Cautious / Defensive]
  Red Flags:    [Any concerning statements or omissions]

THESIS STATUS UPDATE:
  Previous Status: [Status from last review]
  Current Status:  ⬆️ STRENGTHENED / ➡️ UNCHANGED / ⬇️ WEAKENED / ✗ INVALIDATED
  Reason:          [Specific evidence for this status change]

ESTIMATE REVISION:
  Full-Year Revenue: [Revised up / Unchanged / Revised down by X%]
  Full-Year PAT:     [Revised up / Unchanged / Revised down by X%]
  Target Price:      ₹[X] [Unchanged / Revised from ₹Y to ₹X]

RECOMMENDED ACTION: [Hold / Add on dip / Trim / Exit]
Reason:             [One sentence]
```

---

## 10. Skill 06 — Portfolio Auditor

**Version:** v_0.0 | **Purpose:** Complete portfolio health assessment and governance review

### Triggers
- "Audit my portfolio"
- "Review my holdings"
- "Portfolio health check"

### Pre-Flight Requirements
```
□ Holdings list with allocation % (required)
□ Purchase prices (preferred — enables return calculation)
□ Purchase dates (preferred — enables CAGR calculation)
□ Portfolio total size in ₹ (preferred — enables absolute sizing checks)
□ Tax status: Long-term (>12 months) vs. short-term positions?
   → Material for exit decisions (LTCG vs. STCG implications)
```

### Activation Sequence

```
① PORTFOLIO GOVERNANCE LAYER
   DIVERSIFICATION CHECK:
   □ Any single stock > 10%? (Flag — requires documented justification)
   □ Any single sector > 30%? (Flag — concentration risk)
   □ Market cap balance: what % is Large / Mid / Small?
   □ Geographic concentration (listed in India only, or global ETFs?)
   
   OVERLAP ANALYSIS:
   □ Are any companies in the same supply chain? (Hidden concentration)
   □ Are any companies driven by the same macro factor?
     (e.g., 3 IT companies = high INR/USD sensitivity concentration)
   □ Correlation estimate between holdings (qualitative)

② RISK ANALYST
   INDIVIDUAL HOLDING RISK:
   For each holding, rate:
   □ Financial Quality Risk (based on latest financials)
   □ Governance Risk (promoter/board issues)
   □ Valuation Risk (is it materially overvalued?)
   □ Thesis Status (Strengthened / Unchanged / Weakened / Invalidated)
   
   PORTFOLIO STRESS TEST:
   □ Nifty drops 20%: estimate portfolio impact
   □ Sector-specific decline of 30%: most affected holdings?
   □ Interest rate rise scenario: debt-heavy holdings most vulnerable?

③ VALUATION ANALYST
   □ Flag positions trading > 50% above their intrinsic value estimate
   □ Flag positions offering additional upside > 30%
   □ Identify position where upside/downside is least attractive

④ TAX EFFICIENCY REVIEW (NEW in V3.0)
   □ Identify positions crossing 12-month mark soon (LTCG threshold)
   □ Flag positions with large unrealized gains (exit has tax consequence)
   □ Flag positions with unrealized losses (tax loss harvesting opportunity)
   □ If any Weakened / Invalidated thesis positions have large gains:
     note the tax-adjusted exit price

⑤ MONITORING DIVISION
   □ Which holdings have not been reviewed in > 3 months? (Flag)
   □ Which holdings have upcoming results within 4 weeks?
   □ Any holdings with thesis invalidation trigger reached?
   □ Any holdings with governance events pending (AGM, promoter actions)?
```

### Output Format

```
PORTFOLIO AUDIT REPORT
Date: [DD/MM/YYYY] | Holdings Count: [N] | Total Value: ₹[X] Cr (if provided)
═══════════════════════════════════════════════════════════════════════

PORTFOLIO SCORE: [0–100]
  Diversification Score: [0–25]
  Risk Management Score: [0–25]
  Quality Score:         [0–25]
  Monitoring Score:      [0–25]

HOLDINGS OVERVIEW TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company | Sector | Alloc% | Buy Price | Return% | Thesis Status | Risk
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONCENTRATION MAP:
  Top 3 Holdings:     [Names] = [X]% combined
  Top 3 Sectors:      [Names] = [X]% combined
  Market Cap Split:   Large [%] | Mid [%] | Small [%]

STRESS TEST RESULTS:
  Nifty -20% scenario:  Portfolio estimated impact: [-%]
  Worst sector decline: [Sector] at -30% → Portfolio impact: [-%]

TAX CONSIDERATIONS:
  LTCG eligible soon (within 60 days): [Holdings list]
  Large unrealized gains (exit has cost): [Holdings list]
  Tax loss harvesting candidates:       [Holdings list]

TOP 3 STRENGTHS:
  1. [Specific strength with evidence]
  2. [Specific strength with evidence]
  3. [Specific strength with evidence]

TOP 3 WEAKNESSES:
  1. [Specific weakness with evidence]
  2. [Specific weakness with evidence]
  3. [Specific weakness with evidence]

URGENT ACTIONS (Immediate):
  1. [Action — reason]

RECOMMENDED CHANGES (This Month):
  1. [Action — reason]
  2. [Action — reason]

MONITORING ALERTS:
  Results Due:          [Holdings with results in next 4 weeks]
  Review Overdue:       [Holdings not reviewed in >3 months]
  Thesis Alert:         [Holdings with Weakened/Invalidated status]
```

---

## 11. Skill 07 — Valuation Comparator

**Version:** v_0.0 | **Purpose:** Multi-method valuation with peer comparison

### Triggers
- "Compare valuation of [A] vs [B]"
- "Is [Company] cheap / expensive?"
- "Valuation check on [Company]"

### Pre-Flight Requirements
```
□ Company name + current market price (required)
□ Is this a conglomerate / holding company?
  → If YES: activate SOTP valuation method
□ Is this asset-heavy (steel, cement, real estate) or asset-light (software, FMCG)?
  → Affects which multiples are primary
□ Is this a BFSI company?
  → P/Book is primary, not P/E
□ Listed peer group provided or should Claude identify peers?
```

### Valuation Framework by Company Type

```
STANDARD COMPANIES:
  Primary:    P/E vs. historical + sector average
              EV/EBITDA vs. historical + sector peers
  Secondary:  Price/FCF (quality-adjusted)
              PEG Ratio (growth-adjusted P/E)
  Check:      Reverse DCF — what growth is priced in at current price?

ASSET-HEAVY COMPANIES (Steel, Cement, Mining, Real Estate):
  Primary:    EV/EBITDA (replacement cost of assets matters more)
              EV/tonne (for steel/cement)
              P/Book
  Secondary:  P/E (less relevant, more cyclical)

BFSI COMPANIES:
  Primary:    P/Book vs. historical + peer average
              Price/Adjusted Book (excluding GNPA)
  Secondary:  P/E (use with caution)
              Embedded Value (for insurance)

CONGLOMERATES / HOLDING COMPANIES:
  Primary:    SOTP (Sum of Parts) — value each segment separately
  Discount:   Apply 20–30% holding company discount to SOTP value
  Check:      How much is the holdco discount vs. historical?
```

### Methods Applied

```
METHOD 1 — P/E Analysis
  Current P/E:         [X]x
  5-Year Avg P/E:      [Y]x
  Sector Avg P/E:      [Z]x
  Premium/Discount:    Trading at [X]% premium/discount to historical avg

METHOD 2 — EV/EBITDA Analysis
  Current EV/EBITDA:   [X]x
  5-Year Avg:          [Y]x
  Peer Range:          [Low]x – [High]x
  Verdict:             Cheap / Fair / Expensive vs. history and peers

METHOD 3 — Price/FCF (Asset-Light Focus)
  Current P/FCF:       [X]x
  Quality-adjusted:    [Why higher/lower multiple justified?]

METHOD 4 — PEG Ratio
  P/E:                 [X]x
  Expected EPS Growth: [Y]%
  PEG:                 [X/Y]
  Interpretation:      < 1 = Potentially undervalued | > 2 = Expensive

METHOD 5 — Reverse DCF
  At current price of ₹[X], the market is pricing in [Y]% earnings growth
  for [Z] years. Is this assumption reasonable or aggressive?

METHOD 6 — SOTP (For Conglomerates Only)
  Segment A:   ₹[X] Cr at [Y]x [multiple]
  Segment B:   ₹[X] Cr at [Y]x [multiple]
  Net Cash:    ₹[X] Cr
  Gross SOTP:  ₹[Total] Cr = ₹[Per Share]
  Holdco Disc: [20–30]%
  Net SOTP:    ₹[Per Share]
```

### Output Format

```
VALUATION COMPARATOR REPORT
Company: [Name] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════

VALUATION SUMMARY TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Method           Current    Historical Avg   Verdict
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P/E              [X]x       [Y]x             [Cheap/Fair/Expensive]
EV/EBITDA        [X]x       [Y]x             [Cheap/Fair/Expensive]
Price/FCF        [X]x       [Y]x             [Cheap/Fair/Expensive]
PEG              [X]        —                [< or > 1]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PEER COMPARISON: [Company] vs. [Peer 1] vs. [Peer 2]
[Table comparing key multiples and growth rates]

REVERSE DCF INSIGHT:
  At ₹[CMP], market prices in [Y]% EPS CAGR for [Z] years.
  Our estimate: [A]% CAGR is achievable.
  Conclusion: [Market too optimistic / Pessimistic / About right]

HISTORICAL VALUATION BAND:
  5-Year P/E Range: [Low]x – [High]x
  Current P/E [X]x is at the [X]th percentile of historical range

WHAT MUST BE TRUE AT CURRENT PRICE:
  [Specific growth and margin assumptions the stock is pricing in]

OVERALL VERDICT: [Very Cheap / Cheap / Fairly Valued / Expensive / Very Expensive]
Intrinsic Value Range: ₹[Low] – ₹[High]
Margin of Safety at CMP: [%]
```

---

## 12. Skill 08 — Sector Rotation Analyzer

**Version:** v_0.0 | **Purpose:** Identify which sectors to over / underweight given current cycle

### Triggers
- "Which sectors to focus on now?"
- "Sector rotation analysis"
- "Where should I deploy capital?"

### Activation Sequence

```
① ECONOMIC CYCLE POSITIONING
   Using KF-04 (Economic Cycle & Sector Rotation):
   → Current GDP growth trajectory: accelerating / stable / decelerating?
   → Interest rate cycle: rising / peaked / falling?
   → Inflation trajectory: rising / peaked / falling?
   → Credit growth: expanding / contracting?
   → Cycle Classification: Early / Mid / Late / Recessionary

② POLICY & BUDGET ANALYSIS
   → Current budget allocation priorities (which sectors are recipients?)
   → PLI scheme beneficiaries: are they in ramp-up or delivery phase?
   → RBI policy stance and its sector-level implications
   → State government capex: infrastructure, housing, agriculture?

③ EARNINGS MOMENTUM BY SECTOR
   → Which sectors have had 2+ quarters of earnings upgrades?
   → Which sectors are facing earnings downgrades?
   → Which sectors have consensus estimates that are too low? (Positive surprise potential)

④ TECHNICAL RELATIVE STRENGTH
   → Each major sector's performance vs. Nifty 50 (6 months)
   → Sector momentum: improving or deteriorating?
   → Which sectors are making new highs vs. underperforming?

⑤ INSTITUTIONAL FLOW ANALYSIS
   → FII net buying/selling by sector (3-month trend)
   → DII net buying/selling by sector (3-month trend)
   → High-quality mutual fund portfolio changes (sector weights)

⑥ GLOBAL LINKAGE CHECK (NEW in V3.0)
   → Commodity cycles: relevant to metals, chemicals, energy, agri
   → Global IT spending: relevant to Indian IT sector
   → China demand: relevant to specialty chemicals, pharma APIs
   → USD/INR: relevant to IT (positive), importers (negative)
   → US interest rates: relevant to FII flows into India
```

### Output Format

```
SECTOR ROTATION ANALYSIS
Date: [DD/MM/YYYY] | Cycle Phase: [Early / Mid / Late / Recessionary]
═══════════════════════════════════════════════════════════════════════

ECONOMIC CYCLE CONTEXT:
  Phase:          [Early / Mid / Late / Recessionary]
  Duration:       Estimated [X] months into this phase
  Next Phase:     Expected transition in [X–Y] months
  Key Signal:     [The most important indicator confirming this phase]

GLOBAL LINKAGE:
  Commodity Cycle:  [Bullish / Neutral / Bearish]
  USD Trend:        [Strengthening / Stable / Weakening] — Impact: [which sectors]
  FII Risk Appetite:[Rising / Stable / Declining]

SECTOR RANKINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERWEIGHT (Increase Allocation):
  1. [Sector] — Reason: [Earnings + Policy + Technical + Institutional]
  2. [Sector] — Reason: [Same]
  3. [Sector] — Reason: [Same]

NEUTRAL (Hold Current Allocation):
  [Sectors list with brief reasoning]

UNDERWEIGHT (Reduce Allocation):
  1. [Sector] — Reason: [Why reducing makes sense]
  2. [Sector] — Reason: [Same]

CONTRARIAN WATCH (Not yet acting, but monitoring):
  [Sector] — Contrarian Thesis: [Why this hated sector might inflect]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECTOR DEEP DIVES (Top 2 Overweight Sectors):
  [For each: earnings catalyst, best-positioned companies, risks]

KEY RISKS TO THIS ROTATION CALL:
  [What could make this analysis wrong]
```

---

## 13. Skill 09 — Risk Auditor

**Version:** v_0.0 | **Purpose:** Comprehensive portfolio and position risk assessment

### Triggers
- "What are the risks in my portfolio?"
- "Audit portfolio risks"
- "Risk assessment on [Company]"

### Risk Categories (Expanded in V3.0)

```
MARKET RISKS:
□ Beta / directional risk (correlation to Nifty)
□ Sector beta (correlation to sector index)
□ Volatility risk (recent price swings vs. historical)

FUNDAMENTAL RISKS:
□ Governance risk (promoter-related concerns, board issues)
□ Financial quality risk (forensic flags, earnings reliability)
□ Business model risk (disruption, competitive erosion)
□ Management execution risk (delivery vs. guidance history)

VALUATION RISKS:
□ Downside if P/E contracts to historical average
□ Downside if earnings estimate revised down 20%
□ Combined scenario: earnings down + multiple compression

MACRO RISKS:
□ Interest rate sensitivity (debt-heavy companies)
□ Inflation sensitivity (input cost exposure)
□ INR/USD sensitivity (importer vs. exporter)
□ GDP cyclicality (discretionary vs. defensive)

EXTERNAL RISKS:
□ Regulatory risk (new rules, license dependency)
□ Commodity price risk (input or output commodity)
□ Geopolitical risk (supply chain, export markets)
□ China competition risk (sectors exposed to Chinese imports)

PORTFOLIO RISKS:
□ Concentration risk (single stock or sector)
□ Correlation risk (hidden links between holdings)
□ Liquidity risk (ability to exit position quickly)
□ Drawdown risk (estimated max portfolio decline)
```

### Drawdown Estimation (NEW in V3.0)
```
For each holding, estimate:
  Base Case Drawdown:   What % fall if earnings miss by 10%?
  Stress Case Drawdown: What % fall in a market correction (-20% Nifty)?
  Thesis-Break Drawdown: What % fall if core thesis invalidated?

Portfolio-level:
  Weighted average of stress case drawdowns
  Correlation adjustment (correlated holdings amplify drawdown)
  Portfolio Max Drawdown Estimate (stress scenario)
```

### Output Format
```
RISK AUDIT REPORT
Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════

HOLDING-LEVEL RISK SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company | Alloc% | Governance | Financial | Valuation | Overall | Drawdown Est
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PORTFOLIO-LEVEL RISK:
  Overall Risk Rating:    [Low / Moderate / Elevated / High]
  Estimated Max Drawdown: [%] in Nifty -20% scenario
  Concentration Score:    [Low / Moderate / Concentrated]

TOP 3 HIDDEN RISKS (Non-Obvious):
  1. [Risk description + which holdings it affects]
  2. [Risk description + which holdings it affects]
  3. [Risk description + which holdings it affects]

RISK REDUCTION RECOMMENDATIONS:
  Immediate:  [Action + specific holding]
  Near-term:  [Action + specific holding]
  Watch list: [Events that could escalate risks]
```

---

# Risk Auditor (Skill 09) — Missing Market/Ownership/Valuation Flags Addendum v_0.0

**Paste Target:** `04_Skills_Reference_v_0.0.md` — insert as a new subsection immediately after the "## 13. Skill 09 — Risk Auditor" content block

**Scope check:** Skill 09 already covers balance-sheet and earnings-quality risk (overlapping with Forensic Accounting) and portfolio-level risk aggregation. The four flags below are ownership-flow and valuation-behavior risks that weren't previously named.

---

## Additional Risk Checks — Ownership Flow & Valuation Behavior

### Flag 1 — Smart Money Exit

**Detection:**
```
□ FII Holding decreasing for 2+ consecutive quarters
□ DII Holding also decreasing (not offsetting FII exit)
□ Public Holding increasing over the same period
```
**Meaning:** Informed institutional capital is reducing exposure while retail ownership share rises — worth flagging even when price action hasn't reflected it yet.
**Severity:** Medium (High if the trend persists 3+ quarters with no disclosed institutional reason)
**AI Action:** Cross-check against Domain 25 (Geo-Economic Impact) Section 4 — a broad FII outflow across the market is a macro event, not company-specific; only flag as company-specific risk if the stock underperforms peers during the same period.

### Flag 2 — Retail Euphoria

**Detection:**
```
□ Number of Shareholders rising rapidly (e.g., >50% growth in 12 months)
□ Valuation (PE or P/B) at or near multi-year highs
□ Underlying fundamentals (growth, ROCE) not accelerating at a matching pace
```
**Meaning:** Retail interest is outpacing fundamental improvement — a classic late-cycle sentiment signal.
**Severity:** Medium
**AI Action:** Flag as a valuation/sentiment risk, not a business-quality risk — keep this separate from forensic/governance flags in the output.

### Flag 3 — PEG Trap

**Detection:**
```
□ PEG ratio rising primarily because forward growth estimates are being
  revised down (not because price is falling)
□ PE remains elevated relative to Industry PE despite the growth
  deceleration
```
**Meaning:** A stock that looked reasonably priced on trailing growth becomes expensive once growth decelerates — the "cheap growth stock" thesis breaking down.
**Severity:** Medium
**AI Action:** Always state whether PEG is improving because of price decline or growth improvement — never report PEG as a static number without this direction.

### Flag 4 — Price-to-Sales Bubble

**Detection:**
```
□ Price/Sales materially above the stock's own 5-year historical range
□ Margins flat or declining over the same period (i.e., the market is
  paying more per rupee of revenue without margin justification)
```
**Meaning:** Common in high-growth or narrative-driven stocks where valuation has decoupled from profitability.
**Severity:** Medium (High if combined with Flag 2 — Retail Euphoria)
**AI Action:** Cross-reference with the Multibagger Quick Screen (Module 0) — a stock failing the ROCE/CAGR gates while showing this pattern should be flagged as narrative-driven, not fundamentals-driven.

---

## Self-Audit

- ✓ No overlap with Skill 09's existing balance-sheet/earnings-quality coverage
- ✓ No overlap with `AI_Forensic_Accounting_Skill.md` (that file covers accounting-statement-level risk; these four are ownership-flow and market-valuation-behavior risk)
- ✓ Flags 3 and 4 explicitly cross-reference the Multibagger Quick Screen rather than duplicating its thresholds

---

**Document:** Risk_Auditor_Missing_Flags_Addendum_v_0.0.md
**Paste Into:** `04_Skills_Reference_v_0.0.md`, Skill 09 section

---

## 14. Skill 10 — IPO Analyzer

**Version:** v_0.0 | **Purpose:** Comprehensive IPO evaluation — business quality to listing strategy

### Triggers
- "Should I apply for [Company] IPO?"
- "Analyze [Company] IPO"
- "IPO quality check on [Company]"

### Pre-Flight Requirements
```
□ DRHP (Draft Red Herring Prospectus) or IPO details provided
□ Price band provided
□ Listing date (or approximate) known
□ Is this a fresh issue, OFS, or mixed? (Affects fund use and selling pressure)
```

### Activation Sequence

```
① BUSINESS ANALYST
   → Business model: what does this company actually do?
   → Revenue sources: how diversified?
   → Growth history: 3-year revenue and profit trend
   → Competitive position: leader / challenger / niche player?
   → Why is this company going public now? (Favorable: expansion; Unfavorable: PE exit)

② GOVERNANCE ANALYST
   PROMOTER ASSESSMENT:
   → Promoter background: relevant industry experience?
   → Promoter stake pre-IPO and post-IPO (dilution signal)
   → Any criminal proceedings or SEBI actions against promoters?
   
   USE OF PROCEEDS:
   → Fresh issue: where is the money going? (Capex = productive; debt repayment = defensive; unspecified = flag)
   → OFS portion: who is selling? PE exit? Promoter reducing? (Flag if large)
   → Related-party loans to be repaid with IPO proceeds: FLAG

③ ANCHOR INVESTOR ANALYSIS (NEW in V3.0)
   → Which institutions are anchor investors?
   → Quality of anchors: Tier 1 domestic MFs / FIIs = positive signal
   → Anchor lock-in expiry: 30 days post-listing = potential selling pressure
   → Anchor oversubscription: strong demand at institutional level?

④ FINANCIAL ANALYST
   → Revenue trend (3 years): growing consistently?
   → EBITDA margin: improving or declining?
   → PAT: profitable, or losses expected to continue?
   → Cash flow: OCF positive? Or just accounting profit?
   → Debt level: manageable post-IPO (considering fresh issue proceeds)?
   → Working capital: any unusual receivables spike pre-IPO?

⑤ FORENSIC CHECK
   → Restatement of accounts in last 3 years?
   → Auditor change in last 2 years without explanation?
   → Related-party transactions higher than peer average?
   → Revenue recognition policies: aligned with industry standard?

⑥ GREY MARKET PREMIUM CONTEXT (NEW in V3.0)
   → Note any available GMP (with explicit caveat: GMP is not a valuation tool)
   → Use only as a sentiment indicator, not a reason to apply
   → If GMP very high: increased listing day volatility likely
   → State clearly: "GMP reflects speculative demand, not fundamental value"

⑦ VALUATION ANALYST
   → IPO price vs. intrinsic value (DCF or earnings-based)
   → IPO price vs. listed peers on P/E and EV/EBITDA
   → Is the company pricing itself at a premium or discount to peers?
   → "What growth rate does the IPO price assume?" (Reverse DCF)

⑧ RISK ANALYST
   → Lock-in expiry risk: when do PE investors and pre-IPO shareholders unlock?
   → Business risk: is there a single client / product / geography concentration?
   → Regulatory risk: is this a regulated sector with license risk?
   → Market cycle risk: is this IPO in a hot market where pricing is aggressive?

⑨ CIO DECISION — IPO SPECIFIC
   Three possible outcomes:
   → APPLY: Business quality + valuation + governance all acceptable
   → SKIP: Any one of the three is unacceptable
   → WATCH POST-LISTING: Good business but IPO price too high; buy at discount
```

### Output Format

```
IPO ANALYSIS REPORT
Company: [Name] | Price Band: ₹[Low]–₹[High] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

IPO QUALITY SCORE: [0–100]
  Business Quality:   [0–30]
  Governance Quality: [0–25]
  Financial Quality:  [0–25]
  Valuation:          [0–20]

OFFER STRUCTURE:
  Fresh Issue:        ₹[X] Cr ([%] of total)
  OFS:                ₹[X] Cr ([%] of total)
  Primary Sellers:    [List who is selling and stake reduction]
  Use of Proceeds:    [Specific allocation]

ANCHOR INVESTOR QUALITY: [Tier 1 / Mixed / Weak]
  Top 3 Anchors:      [Names]
  Anchor Lock-in End: [Date] — Watch for selling pressure

BUSINESS VERDICT:      [Strong / Good / Average / Weak]
GOVERNANCE VERDICT:    [Clean / Caution / Red Flag]
FINANCIAL VERDICT:     [Improving / Stable / Declining]
VALUATION VERDICT:     [Attractive / Fair / Expensive / Very Expensive]

GMP (if available):    ₹[X] — SENTIMENT ONLY, not a valuation input

RECOMMENDATION:        [APPLY / SKIP / WATCH POST-LISTING]
Reason:               [2–3 sentence justification]
Post-Listing Watch:   ₹[X] — Price at which to reconsider if watching
Exit if Applied:      [Listing day partial exit strategy if speculative]
```

---

## 15. Skill 11 — Turnaround Screener

**Version:** v_0.0 | **Purpose:** Identify genuine turnarounds vs. value traps

### Triggers
- "Find turnaround opportunities"
- "Distressed recovery plays"
- "Which beaten-down stocks might recover?"

### Turnaround Stage Assessment (NEW in V3.0)
Before analysis, classify where in the turnaround the company is:

```
STAGE T0 — DISTRESS PEAK:
  Company is at worst point. Losses, debt concerns, management crisis.
  → Do not invest yet. Monitor for T1 signals.
  → Risk: could worsen further; equity could be diluted or wiped out.

STAGE T1 — STABILIZATION:
  Losses narrowing, debt not rising further, new management appointed,
  operational bleeding stopped.
  → Initial small position possible (1–2% maximum).
  → High uncertainty; this is speculative.

STAGE T2 — EARLY RECOVERY:
  Revenue growing, margins recovering (2+ quarters), debt reducing,
  management demonstrating delivery.
  → Building position justified (2–3%).
  → Evidence-based but still uncertain.

STAGE T3 — RECOVERY CONFIRMED:
  Business profitable, balance sheet healing, competitive position clearer.
  → Full conviction possible (3–5% position).
  → Risk now is valuation (market may have already priced recovery).

→ Classify company's turnaround stage BEFORE completing any analysis.
→ Position size must match stage.
```

### Turnaround Signals vs. Traps

```
GENUINE TURNAROUND SIGNALS (Evidence Required, Not Just Claims):
□ New management with documented turnaround track record (not just promises)
□ Debt/EBITDA declining for 2+ consecutive quarters
□ Gross margin recovering (not just cost cuts)
□ Order book rebuilding (for capital goods, infra companies)
□ Working capital improvement (receivables reducing)
□ Promoter buying shares at current price (own money, not pledged buyback)
□ Industry cycle turning (cyclical companies only)
□ Regulatory overhang formally resolved (not just "expected to resolve")
□ Auditor providing clean opinion after qualification
□ Related-party exposures being wound down with evidence

TURNAROUND TRAPS — EXIT OR AVOID IF PRESENT:
□ Revenue declining while management claims "restructuring"
□ Debt rising despite turnaround narrative
□ Promoter selling shares or increasing pledge during "recovery"
□ Repeated management changes (3+ in 3 years = structural problem)
□ Auditor resignation without satisfactory public explanation
□ Rights issue / QIP at steep discount (desperation signal)
□ New related-party transactions during financial stress
□ Loss-making quarters blamed exclusively on "one-time items" (every quarter)
□ Guidance consistently missed despite "conservative" guidance claims
```

### Output Format

```
TURNAROUND ANALYSIS
Company: [Name] | Stage: T[0/1/2/3] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════

STAGE ASSESSMENT: T[X] — [DISTRESS PEAK / STABILIZATION / EARLY RECOVERY / CONFIRMED]
Stage Evidence: [Specific metrics justifying this stage classification]

GENUINE SIGNAL COUNT:  [X]/10
TRAP SIGNAL COUNT:     [X]/10
NET SIGNAL SCORE:      [Signals – Traps]

FINANCIAL RECOVERY TRACK:
  Revenue:     [Last 4 quarters trend]
  EBITDA:      [Last 4 quarters trend]
  Debt:        [Last 4 quarters trend]
  Promoter Buy/Sell: [Last 12 months]

MANAGEMENT ASSESSMENT:
  Current Team:    [Background and turnaround credentials]
  Promise vs. Delivery: [Last 4 quarters guidance vs. actual]
  
WHAT WOULD CONFIRM SUCCESS:
  [Specific metrics and milestones that would confirm recovery]
  
WHAT WOULD INVALIDATE THIS:
  [Specific triggers that would suggest value trap]

RECOMMENDATION:       [Avoid / Watch / Speculative Position / Build Position]
Stage-Based Max Position: [1–5% per stage guidelines]
Re-rating Trigger:    [What would justify increasing position]
```

---

## 16. Skill 12 — Watchlist Prioritizer

**Version:** v_0.0 | **Purpose:** Prioritize watchlist by current attractiveness and readiness

### Triggers
- "Prioritize my watchlist"
- "Which watchlist stock is most attractive now?"
- "Watchlist update"

### Pre-Flight Requirements
```
□ Current watchlist provided (company names + any notes)
□ Last research date for each company (to flag stale research)
□ Target buy prices set previously (if available)
□ Current market prices (user to provide or Claude to note as unavailable)
```

### Status System (Expanded in V3.0)

| Status | Emoji | Criteria | Action |
|--------|-------|----------|--------|
| Buy Now | 🟢 | Price at attractive entry; thesis intact; strong evidence | Buy at stated size |
| Accumulate | 🔵 | Slightly above ideal price; quality justifies gradual entry | Buy in tranches |
| Watch — Near Buy | 🟡+ | Within 10% of target buy price | Set alert |
| Watch — Wait | 🟡 | Good business; price not yet attractive | No action |
| Under Research | ⚪ | Not yet analyzed to IERL standard | Run Skill 01 |
| Hold | 🟤 | Already own; thesis intact | No new buys |
| Reduce | 🟠 | Thesis weakening OR valuation excessive | Partial exit |
| Exit | 🔴 | Thesis broken OR governance crisis | Full exit |
| Avoid — Temporary | ⛔ | Fundamental concerns; may revisit in 6–12 months | Delist for now |
| Avoid — Permanent | 🚫 | Governance disqualification; never buy | Remove from list |

### Staleness Protocol (NEW in V3.0)
```
Research Date > 6 months ago: Flag as [STALE — REFRESH NEEDED]
Research Date > 12 months ago: Flag as [STALE — RUN SKILL 01 BEFORE ACTION]
No research date on record: Flag as [UNRESEARCHED — DO NOT ACT WITHOUT SKILL 01]
```

### Output Format

```
WATCHLIST PRIORITIZER
Date: [DD/MM/YYYY] | Total Companies: [N]
═══════════════════════════════════════════════════════════════════

IMMEDIATE ACTION REQUIRED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company | Status | Score | Target Price | CMP | Gap% | Last Research | Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FULL WATCHLIST STATUS:
[Complete table with all holdings]

TOP 3 MOST ACTIONABLE RIGHT NOW:
  1. [Company] — [Status] — [Why most actionable, specific reason]
  2. [Company] — [Status] — [Why second most actionable]
  3. [Company] — [Status] — [Why third]

APPROACHING BUY PRICE (Within 10%):
  [List companies and their gap to target price]

STALE RESEARCH REQUIRING REFRESH:
  [Companies where research is >6 months old]

REMOVE FROM WATCHLIST (Thesis broken or governance issue):
  [Companies to cull from list + reason]
```

---

## 17. Skill 13 — Concall & Management Commentary Analyzer ⭐ NEW

**Version:** v_0.0 | **Purpose:** Extract signal from management calls; detect confidence vs. evasion

### Triggers
- "Analyze [Company] concall"
- "What did management say in the concall?"
- "Concall transcript analysis for [Company]"
- "Management commentary review"

### Why This Skill Exists
Management commentary contains information not in the financial statements: forward guidance, strategic intent, tone changes, evasiveness on important questions, and early signals of problems or acceleration. This skill separates signal from noise in concall transcripts.

### Pre-Flight Requirements
```
□ Concall transcript or summary provided (required)
□ Previous concall summary available for comparison? (Strongly preferred)
□ Previous guidance stated on last call (to measure delivery)
□ Questions asked by analysts (the questions reveal what concerns the market)
```

### Activation Sequence

```
① DELIVERY AUDIT — PRIOR GUIDANCE VS. ACTUAL
   → What did management guide for last quarter?
   → What actually happened?
   → Delivery Score: Beat / Met / Missed / Significantly Missed
   → Track record: how many of last 4 guidance points were delivered?

② TONE ANALYSIS
   POSITIVE SIGNALS:
   □ Management speaks in specifics, not generalities
   □ Gives quantitative guidance with reasoning
   □ Acknowledges challenges directly and explains plan
   □ Gives credit to team and operational factors, not just market tailwinds
   □ Takes questions directly without deflection
   
   NEGATIVE SIGNALS:
   □ Blames external factors for every shortfall (never internal)
   □ Uses vague language ("broadly on track", "improving trajectory")
   □ Avoids specific questions with general statements
   □ Changes subject or gives long preamble before answering
   □ Management tone changed vs. prior calls (sudden caution?)
   □ Key executive absent from call without explanation

③ FORWARD GUIDANCE EXTRACTION
   → What specific guidance was given?
   → Volume targets? Margin guidance? Revenue growth?
   → Capex plans? Capacity additions? Timelines?
   → New product launches or market entries?
   → Hiring / headcount plans (leading indicator of confidence)

④ KEY MANAGEMENT STATEMENTS — VERBATIM CAPTURE
   → Quote 3–5 most important statements (positive or negative)
   → Flag any statement that contradicts previous guidance
   → Flag any unusual disclosures made almost in passing

⑤ ANALYST Q&A REVIEW
   → What were the 3 most important questions analysts asked?
   → Were these questions answered directly or deflected?
   → What questions were NOT asked that should have been?
   → Did management give more information than required on any topic?
     (Over-disclosure can be a positive signal of confidence)

⑥ RED FLAG DETECTION
   Linguistic Red Flags in Concalls:
   → "We are monitoring the situation" (used for a known risk = evasion)
   → "One-time" items mentioned for 2+ consecutive calls = not one-time
   → "As you know" before a new negative development = downplaying
   → Promoter not present on call for major strategic question = concern
   → Numbers sound too round (all guidance in exact round numbers = scripted)

⑦ THESIS STATUS UPDATE
   → Does this concall strengthen, maintain, weaken, or invalidate the thesis?
   → What specific statement most impacted this assessment?
```

### Output Format

```
CONCALL ANALYSIS REPORT
Company: [Name] | Quarter: Q[X] FY[XX] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════

DELIVERY SCORECARD (Prior Guidance vs. Actual):
  Revenue:        Guided [X]% → Achieved [Y]% → [Beat/Met/Missed]
  EBITDA Margin:  Guided [X]% → Achieved [Y]% → [Beat/Met/Missed]
  [Other specific guidance points]
  Delivery Score: [X/N guidance points met]
  Track Record (last 4 calls): [X/4 guidance points delivered]

TONE ASSESSMENT:
  Overall Tone:    [Confident / Cautious / Defensive / Evasive]
  Tone vs. Last Q: [More positive / Same / More cautious]
  Specificity:     [High (specifics given) / Medium / Low (vague answers)]

FORWARD GUIDANCE EXTRACTED:
  [Table of all specific guidance items: metric, guidance, basis given]

KEY MANAGEMENT STATEMENTS:
  1. [Most important quote — paraphrased + significance]
  2. [Second most important]
  3. [Third most important]
  ⚠️ [Any statement contradicting prior guidance — flagged explicitly]

ANALYST Q&A HIGHLIGHTS:
  Most Important Q: [Question + How well was it answered?]
  Key Deflection:   [Question that was deflected, if any]
  Unanswered:       [What should have been asked but wasn't]

RED FLAGS DETECTED:
  [List each red flag with specific evidence from transcript]
  OR: "No linguistic or substantive red flags detected"

THESIS STATUS:
  Previous Status:  [Strengthened / Unchanged / Weakened / Invalidated]
  Post-Concall:     [Updated status]
  Primary Driver:   [What in this call changed the status]

RECOMMENDED ACTION: [No change / Monitor more closely / Reduce / Exit]
```

---

## 18. Skill 14 — Corporate Action Analyzer ⭐ NEW

**Version:** v_0.0 | **Purpose:** Assess the investment implications of corporate actions

### Triggers
- "Analyze [Company] buyback"
- "What does the bonus issue mean for [Company]?"
- "Rights issue analysis for [Company]"
- "QIP impact on [Company]"
- "Dividend analysis for [Company]"

### Corporate Actions Covered

```
ACTION 1 — BUYBACK
  WHAT IT SIGNALS:
  ✅ Positive: Management believes stock is undervalued; strong cash position;
              promoter confidence; EPS accretive if below intrinsic value
  ❌ Negative: Buyback at high P/E (capital misallocation); funded by debt
              (signals desperation); used to artificially inflate EPS;
              reduces cash needed for growth capex
  
  ANALYSIS STEPS:
  → Price offered vs. CMP vs. intrinsic value estimate
  → Buyback size as % of market cap (>5% = meaningful)
  → Source of funds: cash on books or borrowing?
  → Management credibility: do they typically buy when it's cheap?
  → Offer price: is there alpha above CMP for tendering?

ACTION 2 — BONUS ISSUE
  WHAT IT SIGNALS:
  → Cosmetic: no change in economic value (only price adjusts)
  → Sometimes positive signal: management comfortable with stock liquidity
  → Does NOT increase wealth — only number of shares increases
  
  ANALYSIS:
  → Post-bonus share count and adjusted EPS
  → Does bonus improve liquidity? (Only if stock was very illiquid)
  → Investor action: adjust target prices downward by bonus ratio

ACTION 3 — STOCK SPLIT
  Similar to bonus: cosmetic event improving liquidity, not value.
  → Adjust all price targets by split ratio
  → Note: splits sometimes increase retail participation; small sentiment boost

ACTION 4 — RIGHTS ISSUE
  WHAT IT SIGNALS:
  ✅ Positive: Growth capex funding; expansion of capacity
  ❌ Negative: Distress funding; balance sheet repair; unable to borrow more
  
  ANALYSIS:
  → Subscription price vs. CMP (rights discount)
  → Use of proceeds (growth vs. debt repayment vs. general corporate purposes)
  → Is promoter participating? (If not: major red flag)
  → Dilution impact: how much does EPS decline post-rights?
  → IERLS decision: Subscribe / Sell rights / Do not subscribe

ACTION 5 — QIP (Qualified Institutional Placement)
  WHAT IT SIGNALS:
  ✅ Positive: Large institutions buying at premium = confidence signal
  ❌ Negative: Company needs cash urgently; promoter avoiding dilution at low price
  
  ANALYSIS:
  → QIP price vs. CMP (premium or discount?)
  → Quality of investors in QIP (Tier 1 domestic/foreign = positive)
  → Dilution: how much does promoter % fall?
  → Use of proceeds
  → Post-QIP institutional holding: does it rise materially?

ACTION 6 — DIVIDEND / SPECIAL DIVIDEND
  ANALYSIS:
  → Dividend yield: is it sustainable (FCF supports it)?
  → Payout ratio: is company returning too much (growth capital needed)?
  → Special dividend: one-time cash return signal (asset sale, exceptional year?)
  → Impact on book value and growth investment capacity
```

### Output Format

```
CORPORATE ACTION ANALYSIS
Company: [Name] | Action Type: [Buyback/Bonus/Split/Rights/QIP/Dividend]
Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

ACTION DETAILS:
  Type:        [Action Type]
  Size/Terms:  [Specific terms of the action]
  Announced:   [Date] | Record/Expiry Date: [Date]

SIGNAL INTERPRETATION:
  Primary Signal: [Positive / Neutral / Negative]
  Reasoning:      [Why this specific action sends this signal]

FINANCIAL IMPACT:
  EPS Impact:      [Accretive / Dilutive / Neutral]
  Book Value:      [Change per share]
  Promoter Stake:  [Change post-action]

PRICE TARGET ADJUSTMENT:
  Pre-Action Target: ₹[X]
  Adjusted Target:   ₹[Y] (reason for adjustment)

RECOMMENDED INVESTOR ACTION:
  [For buybacks: Tender / Don't Tender / Partial Tender]
  [For rights: Subscribe / Sell Rights / Ignore]
  [For QIP: Note as positive signal / Concern flag]
  [For bonus/split: Adjust price targets only]
  Reason: [2–3 sentence justification]
```

---

## 19. Skill 15 — Pre-Investment Master Checklist ⭐ NEW

**Version:** v_0.0 | **Purpose:** Final mandatory gate before committing capital

### Triggers
- "Pre-investment checklist for [Company]"
- "Final check before buying [Company]"
- "Investment gate check on [Company]"

### When to Use
This skill is the FINAL GATE before any capital is committed. It should always be triggered after Skill 01 (Master Research) or after a thesis has been formed through other skills. No capital should be committed without passing this checklist.

### The 5-Gate System

```
GATE 1 — THESIS QUALITY
□ Can I explain why I'm buying this in 3 sentences? (If not: thesis unclear, stop)
□ Is the thesis based on evidence (Tier 1–3 sources) or opinion?
□ Would an intelligent skeptic find this thesis reasonable?
□ Is there one clear "why now" reason for current entry?
□ What would make this thesis wrong? (If I can't answer: I don't understand it)

GATE 2 — GOVERNANCE CHECK
□ No active SEBI enforcement action or court proceedings against promoter
□ Auditor has not resigned or been changed without explanation in 2 years
□ Promoter pledge < 25% of holdings
□ No material related-party fund flows flagged
□ Board has at least 2 credible independent directors
→ If any item above fails: STOP. Do not invest regardless of financial quality.

GATE 3 — FINANCIAL QUALITY
□ Company is not loss-making in all of last 3 years
□ OCF/PAT ratio > 60% (earnings are cash-backed)
□ Debt/Equity < 3x (non-BFSI) or CAR adequate (BFSI)
□ No revenue growing while CFO declining (potential earnings fabrication signal)
□ No more than 2 forensic flags in the last 12 months of analysis
→ If 2+ items fail: STOP or escalate to expert review.

GATE 4 — VALUATION DISCIPLINE
□ Margin of Safety > minimum threshold for this business quality:
   Wide Moat: MoS > 15% | Narrow Moat: MoS > 25% | No Moat: MoS > 40%
□ Entry price within the defined entry zone from Skill 01 output
□ Am I paying a fair price for quality, not a high price for excitement?
□ Reverse DCF: does the implied growth rate seem achievable?

GATE 5 — BEHAVIORAL AUDIT (Final)
□ Confirmation Bias: Have I actively sought evidence AGAINST this thesis?
□ FOMO: Am I buying because the stock has gone up and I fear missing out?
□ Anchoring: Am I anchored to a previous price or a "cheap" label?
□ Narrative Bias: Am I buying a story rather than a proven business?
□ Recency Bias: Am I extrapolating recent good quarters into perpetuity?
□ Overconfidence: Is my position size appropriate for my actual certainty?
□ Social Proof: Am I buying because someone I trust recommended it?
□ Loss Aversion: Am I NOT buying a good stock because of a previous loss?
```

### Output Format

```
PRE-INVESTMENT CHECKLIST
Company: [Name] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

GATE 1 — THESIS QUALITY:     [PASS / FAIL]
  3-Sentence Thesis:          [Written out]
  Evidence Basis:             [Tier rating]
  "Why Now":                  [Stated]
  If Thesis Wrong:            [Stated]

GATE 2 — GOVERNANCE:         [PASS / CAUTION / FAIL]
  Items checked:              [5/5 listed with result]
  Any Hard Fails:             [Yes / No — details]

GATE 3 — FINANCIAL QUALITY:  [PASS / CAUTION / FAIL]
  Items checked:              [5/5 listed with result]
  Any Hard Fails:             [Yes / No — details]

GATE 4 — VALUATION:          [PASS / CAUTION / FAIL]
  Margin of Safety:           [%] — Required: [%]
  Entry Price vs. Zone:       [Within zone / Above zone]
  Implied Growth (Rev DCF):   [%] — Achievable? [Yes/Stretch/No]

GATE 5 — BEHAVIORAL AUDIT:   [PASS / CAUTION / FAIL]
  Biases Checked:             [8 items]
  Biases Detected:            [List or "None"]
  Conviction Adjustment:      [None / Downgraded to Medium]

FINAL VERDICT:
  All Gates Passed:           [YES → Proceed | NO → Do Not Invest]
  
  ✅ CLEARED FOR INVESTMENT:  [Position size] at [entry zone]
  OR
  ❌ BLOCKED: Gate [X] failed — reason: [specific issue]
     Required Action before reinvestment: [specific fix needed]
```

---

## 20. Skill Output Quality Standards

Every skill output — regardless of skill type — must satisfy these standards:

| Standard | Requirement |
|----------|-------------|
| **Evidence Basis** | Every factual claim must cite its source tier (KF reference or data source) |
| **Confidence Level** | High / Medium / Low stated explicitly with reason |
| **Key Assumptions** | What must be true for the conclusion to hold |
| **What Could Be Wrong** | Honest assessment of weaknesses in the analysis |
| **Missing Information** | What data would improve the analysis — stated explicitly |
| **Data Freshness** | Most recent data date used must be stated |
| **Bias Disclosure** | Any detected analytical bias must be disclosed |
| **Action Clarity** | Every output must end with a clear, actionable next step |

### The Anti-Vagueness Rule
Claude must never produce output containing these phrases without immediate specifics:
- "broadly positive" → must quantify what specifically is positive
- "manageable risk" → must define what "manageable" means with a threshold
- "attractive valuation" → must state the specific multiple and historical comparison
- "strong management" → must give specific evidence (guidance delivery, capital allocation decision)

### The Honesty Rule
When evidence is insufficient for a conclusion, Claude must say so explicitly. Providing a low-confidence opinion labeled as analysis is a violation of IERL standards. "Insufficient data to conclude" is always a valid and honest output.

---

## 21. Skill 17 — Banking Sector Analyzer

**Merged from standalone file `AI_Banking_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Banks (Private, Public Sector, Small Finance, Payments)

---

## CRITICAL AI INSTRUCTION

Banking analysis uses a **completely different framework** from non-financial companies. Standard metrics (Debt/Equity, EBITDA, OCF/PAT) do NOT apply. Debt is a bank's raw material. Profit quality in banks is assessed through **asset quality, NIM sustainability, capital adequacy, and provision coverage**. Activate this skill for ALL bank analysis — do not use general financial analysis frameworks.

**Governance and asset quality override everything. A bank with clean books and weak growth is safer than a fast-growing bank with hidden NPAs.**

---

## Purpose

Deliver institutional-grade analysis of listed Indian banks covering asset quality, earnings quality, capital strength, liability franchise, management credibility, and regulatory positioning. Identify banks with durable competitive advantages and flag those with hidden stress.

---

## Pre-Flight Requirements

```
□ Latest Annual Report (full — including Schedule 9, 17, 18 notes)
□ Last 8 quarters of financial results
□ RBI disclosures / Pillar 3 report
□ Investor presentation (for AUM/segment breakdown)
□ Credit rating reports (for subordinated debt rating)
□ Management commentary / concall transcript (last 2 quarters)
□ Sector data: RBI banking sector statistics for peer comparison
```

---

## Analysis Module 1 — Business Model and Liability Franchise

### Step 1.1 — Bank Type Classification
```
Private Sector Bank (Large): HDFC, ICICI, Axis, Kotak, IndusInd
  → Focus: NIM sustainability, growth vs. asset quality balance, fee income
  
Private Sector Bank (Mid/Small): DCB, Karur Vysya, City Union, South Indian
  → Focus: Regional franchise, concentration risk, succession planning

Public Sector Bank (PSB): SBI, Bank of Baroda, PNB, Canara
  → Focus: NPA resolution progress, credit culture reform, political interference risk

Small Finance Bank (SFB): AU, Equitas, Ujjivan, Jana, ESAF
  → Focus: Transition from NBFC, deposit franchise building, micro-segment asset quality

Payments Bank / Niche: Airtel Payments, India Post Payments
  → Focus: Revenue model viability, regulatory moat, deposit constraints
```

### Step 1.2 — Liability Franchise Quality (THE MOST IMPORTANT MOAT)
```
CASA Ratio Analysis:
→ CASA = (Current Account + Savings Account) / Total Deposits
→ Benchmark: >40% = Strong | 30–40% = Adequate | <30% = Weak
→ Direction of CASA: Improving or declining?
→ Savings rate strategy: rate cuts hurt CASA if rate-sensitive

Cost of Deposits:
→ Total interest expense / Average deposits
→ Lower = better NIM potential
→ Trend: rising (competition for deposits) or stable?

Deposit Growth vs. Credit Growth:
→ Loan-to-Deposit (CD) Ratio: >85% = stretched | 70–80% = healthy
→ Wholesale funding dependence: >30% = vulnerability to liquidity stress
→ Retail deposit stickiness: % of retail vs. institutional deposits

Term Deposit Concentration:
→ % of deposits repricing in next 12 months
→ ALM (Asset Liability Mismatch) exposure at short end
```

---

## Analysis Module 2 — Net Interest Margin (NIM)

### Step 2.1 — NIM Calculation and Decomposition
```
NIM = Net Interest Income / Average Interest-Earning Assets

Decompose into:
→ Yield on Advances: Interest income from loans / Average loans
→ Yield on Investments: Interest on investments / Average investments
→ Cost of Funds: Total interest expense / Average interest-bearing liabilities
→ Spread = Yield on Advances − Cost of Deposits

Benchmark NIMs (FY2025):
→ Small Finance Banks: 7–9%
→ Private Banks (large): 4–5%
→ Private Banks (mid): 3.5–4.5%
→ Public Sector Banks: 2.8–3.5%
```

### Step 2.2 — NIM Sustainability Assessment
```
NIM Drivers to Track:
□ Repo rate environment: rising rates → NIM expansion (initially) → peaks → compression
□ Loan mix shift: high-yield retail vs. lower-yield corporate
□ Fixed vs. floating rate book composition
□ MCLR/RLLR-linked loan repricing lag
□ Investment portfolio yield (G-Sec exposure at what yield?)

NIM Risk Flags:
⚠️ NIM expanded >50bps in one year without clear mix-shift reason
⚠️ NIM compression >30bps quarter-on-quarter
⚠️ CD ratio rising fast without CASA growth = borrowing to lend (expensive)
⚠️ Significant CRR/SLR holding (idle capital reducing earning asset yield)
```

---

## Analysis Module 3 — Asset Quality (CORE MODULE)

### Step 3.1 — NPA Pyramid
```
GROSS NPA RATIO = Gross NPAs / Gross Advances
  → <1.5%: Excellent | 1.5–3%: Good | 3–5%: Elevated | >5%: Stressed

NET NPA RATIO = Net NPAs / Net Advances
  → <0.5%: Excellent | 0.5–1.5%: Good | >2%: Concern | >3%: Serious concern

Provision Coverage Ratio (PCR):
  → PCR = Provisions Made / Gross NPAs
  → >70%: Conservative (good) | 60–70%: Adequate | <60%: Aggressive (risk)
  → Higher PCR = better protection against future losses

Restructured Book:
  → Any restructured accounts that haven't slipped to NPA yet?
  → Post-COVID restructuring: how much remains under moratorium or watchlist?
```

### Step 3.2 — Slippage and Credit Cost Analysis
```
Slippage Ratio = Fresh NPAs added in quarter / Opening standard advances
  → <1%: Excellent | 1–2%: Normal | >2%: Elevated | >3%: Stress signal

Credit Cost = Provisions charged to P&L / Average Advances
  → Benchmark: 0.5–1.0% for quality banks
  → Rising credit cost → future earnings pressure
  → Falling credit cost with rising NPAs = UNDER-PROVISIONING FLAG

Recovery and Upgrades:
→ What % of NPAs was recovered vs. written off?
→ Write-off trend: banks often write off instead of recovering — verify
→ Technical write-offs: still claimed from borrower? Or permanently lost?
```

### Step 3.3 — Sector and Segment Concentration Risk
```
Portfolio Concentration:
□ Top 20 borrowers as % of total advances
□ Single borrower limit compliance (RBI: 15% of capital funds)
□ Group exposure limits
□ Sector concentration: real estate, infrastructure, MSME, retail

Stress Segment Analysis:
→ MSME book: % under emergency credit lines (ECLGS), stress therein
→ Agricultural portfolio: % under waiver risk, seasonal NPA patterns
→ Retail portfolio: personal loans, credit cards — delinquency trend
→ Real estate: under-construction exposure, builder loan NPA
→ MFI/Microfinance: overleveraging in rural markets
```

---

## Analysis Module 4 — Capital Adequacy

### Step 4.1 — Capital Ratios
```
Capital Adequacy Ratio (CAR / CRAR):
  Regulatory Minimum: 11.5% (including capital conservation buffer)
  → >16%: Well-capitalised | 13–16%: Comfortable | 11.5–13%: Adequate | <11.5%: BREACH

Tier 1 Capital Ratio:
  → Common Equity Tier 1 (CET1): >10% is conservative | <8% = concern
  → AT1 (Additional Tier 1): Perpetual bonds — callable risk, write-down trigger risk

Leverage Ratio:
  → Tier 1 Capital / Total Exposure: Minimum 4% (Basel III)
  
Risk Weighted Assets (RWA) Density:
  → RWA / Total Assets: rising density = riskier mix
  → Rising unsecured retail → higher RWA density
```

### Step 4.2 — Capital Requirement Forecast
```
□ Expected loan growth × RWA density = Capital consumption
□ Internal capital generation: ROTE × (1 − payout ratio)
□ Will the bank need to raise equity in next 18 months?
   If YES: Dilution risk → adjust per-share valuation
□ AT1 write-down risk: check trigger CET1 levels
```

---

## Analysis Module 5 — Profitability

### Step 5.1 — Return on Assets (ROA)
```
ROA = Net Profit / Average Total Assets
  → >1.5%: Excellent | 1.0–1.5%: Good | 0.7–1.0%: Adequate | <0.7%: Weak

ROA Decomposition (DuPont for Banks):
  NIM + Non-Interest Income/Assets
  − Operating Cost Ratio (Cost/Assets)
  − Credit Cost (Provisions/Assets)
  − Tax Rate
  = ROA

Each component reveals where value is created or destroyed.
```

### Step 5.2 — Return on Equity (ROE)
```
ROE = Net Profit / Average Equity
  → >15%: Excellent | 12–15%: Good | 10–12%: Adequate | <10%: Weak

ROE = ROA × Equity Multiplier (Assets/Equity)
  → High leverage can inflate ROE — verify quality of ROA first

Cost-to-Income Ratio (Efficiency Ratio):
  → C/I = Operating Costs / Operating Income (NII + Fee Income)
  → <45%: Excellent | 45–55%: Efficient | 55–65%: Average | >65%: Inefficient
  → Rising C/I = Cost growth outpacing income growth (margin pressure ahead)
```

### Step 5.3 — Fee Income Quality
```
Non-Interest Income Sources:
□ Transaction fees (payment processing, trade finance): RECURRING — Positive
□ Distribution income (insurance, MF): RECURRING but regulation-sensitive
□ Treasury gains: ONE-TIME — Exclude from core earnings
□ FX income: RECURRING but volatile
□ Recovery from written-off accounts: ONE-TIME

Core Fee Income Ratio = (Non-interest income − Treasury gains) / Total Income
→ Higher = more diversified, less NIM-dependent
```

---

## Analysis Module 6 — Management and Governance

### Step 6.1 — Track Record Assessment
```
□ NPA guidance: did management predict slippage accurately?
□ Loan growth guidance: delivered or consistently missed?
□ NIM guidance: within 10bps of actual = credible management
□ Credit cost guidance: has management ever guided low then reported high?
□ Capital raise: was timing forced (stress) or proactive (growth)?
□ Related-party lending: any connected lending irregularities (IL&FS, DHFL type)?
```

### Step 6.2 — Regulatory Compliance
```
□ RBI corrective actions: any PCA (Prompt Corrective Action) history?
□ RBI audit remarks: available in annual report or RBI publications
□ SEBI compliance: timely disclosures, no manipulation cases
□ CEO/MD tenure: >5 years = institutional continuity
□ CEO change: voluntary retirement or forced exit? (Key risk signal)
□ Branch licence, digital banking licence status
```

---

## Analysis Module 6A — Digital Banking and Technology Metrics

```
Digital Acquisition:
□ % of new accounts opened digitally (savings, FD, loan)
   → >50% digital: modern, cost-efficient
   → <20% digital: lagging, will face cost pressure vs. peers
□ Cost of digital acquisition vs. branch acquisition: ratio trend
□ Mobile banking MAU (Monthly Active Users) / Total customers
□ UPI transaction market share (reflects ecosystem engagement)
□ Digital loan disbursements as % of total: rising = operating leverage

Technology Risk:
□ Core banking system: age and vendor (CBS upgrade = execution risk)
□ Outage incidents in last 2 years: RBI fine risk + customer attrition
□ Cybersecurity incidents disclosed: increasing frequency = systemic risk
□ IT expense as % of operating expenses: rising = future-proofing

Fintech Partnership / Competition:
□ Co-lending active (with NBFCs / fintechs): volume, NIM impact
□ Digital lending app integration: BNPL, personal loan API partnerships
□ Account aggregator ecosystem participation: consent-based data sharing
□ Any material fintech threatening core product (payments, credit)?
```

## Analysis Module 6B — Co-Lending Framework Assessment

RBI co-lending model (CLM): Bank partners with NBFC — 80:20 structure.
Bank takes 80% of loan on books; NBFC retains 20%.

```
For Banks Participating in Co-Lending:
□ Volume of co-lending book (₹Cr): growing or pilot stage?
□ NIM on co-lending vs. own-originated loans: is it accretive?
□ Credit risk allocation: who bears first loss?
   → Standard: NBFC bears first loss on their 20% tranche
□ NBFC partner quality: if NBFC fails, what happens to bank's 80%?
□ Regulatory treatment: co-lent book counts toward bank's PSL targets?
□ Reporting: Is bank disclosing co-lending NPA separately?
Red Flag: Rapid co-lending growth with weak NBFC partners = hidden NPA risk
```

## Analysis Module 6C — Rate Cycle NIM Sensitivity Map

```
Rate Environment vs. NIM Impact:

RISING RATE CYCLE (RBI hiking):
Phase 1 (first 3 months): NIM EXPANDS
  → Floating rate loans reprice immediately
  → Deposits reprice slowly (fixed-term deposits)
  → Net: yield up faster than cost → NIM expansion
Phase 2 (6–12 months): NIM PEAKS, then stabilises
  → Deposits begin repricing higher
  → CASA deposits shift to term (CASA ratio falls)
  → Net: cost catches up to yield
Phase 3 (12–24 months): NIM COMPRESSES if rates stable/fall
  → Competition for deposits intensifies
  → New loan growth at peak rates, existing book repricing done

FALLING RATE CYCLE (RBI cutting):
Phase 1 (0–6 months): NIM COMPRESSES IMMEDIATELY
  → Floating loans reprice down quickly (RLLR-linked)
  → Fixed deposits take time to reprice
Phase 2 (6–18 months): NIM stabilises
  → Deposits also reprice lower → cost of funds falls
  → Competition for quality borrowers intensifies

WHAT TO CHECK NOW (July 2025 context):
□ Where is India in the rate cycle? (Check latest MPC stance)
□ What % of loan book is floating vs. fixed?
□ What % of deposits are CASA vs. term? (Repricing profile)
□ Management NIM guidance for next 2 quarters: credible?
```

## Analysis Module 6D — PSB Reform Tracker (For Public Sector Banks Only)

```
If analysing SBI, Bank of Baroda, PNB, Canara, Union, Indian Bank, etc.:

Credit Culture Reform:
□ GNPA trend: peak NPA year was FY2018 (most PSBs). Recovery since?
□ Slippage ratio: converging to private bank levels (<1.5%) or stuck high?
□ Recovery from NCLT/IBC cases: actual cash recovered vs. claims

Capital Efficiency:
□ ROA trend: >1% = significant reform success | Still <0.7% = structural issue
□ Cost-to-Income: PSBs typically 50–60% | Falling toward private bank levels?

Government Influence Risk:
□ Priority sector lending targets: forcing below-market-rate lending?
□ Government directed lending (Jan Dhan, mudra, PM schemes): NPA track record
□ Merger integration (Bank of Baroda-Vijaya-Dena): fully integrated?
□ Political interference in credit decisions: management commentary on autonomy

Valuation Discount Justification:
PSBs trade at structural P/B discount to private banks.
Discount is justified by: lower ROE, governance risk, political interference
Discount narrowing signal: ROA convergence to >1%, GNPA < 3%, CAR comfortable
```

## Valuation Framework for Banks

### Preferred Method: Price-to-Book (P/B)
```
Justified P/B = ROE / Cost of Equity

Example: ROE = 16%, Ke = 13% → Justified P/B = 1.23x
         ROE = 20%, Ke = 13% → Justified P/B = 1.54x
         ROE = 10%, Ke = 13% → Justified P/B = 0.77x (deserves discount to book)

Adjust Justified P/B for:
+Premium: Strong CASA, wide NIM moat, clean book, rising ROE trajectory
−Discount: High NPA, RBI action, management credibility concern, capital shortfall
```

### P/E for Banks
```
Normalised P/E = Price / Normalised EPS (using mid-cycle credit cost)
→ Using current low credit cost overestimates earnings (cycle will turn)
→ Using current high credit cost underestimates recovery potential
→ Benchmark: 10–15x P/E for PSBs, 15–25x for private, 25–35x for premium private
```

---

## Red Flag Summary — Banking

### CRITICAL Flags
```
❗ Net NPA >3% with PCR <60%
❗ Slippage ratio >3% for 2+ consecutive quarters
❗ CAR below regulatory minimum
❗ CASA ratio declining >500bps over 2 years
❗ CEO exit under regulatory pressure
❗ RBI PCA (Prompt Corrective Action) imposed
❗ Related-party lending detected in audit
❗ AT1 bond write-down trigger approached (CET1 near 5.5%)
```

### HIGH Flags
```
⚠️ Credit cost rising while management guides for stability
⚠️ CD ratio >90% (liquidity stretched)
⚠️ Wholesale funding >40% of liabilities
⚠️ Real estate + infrastructure >30% of loan book
⚠️ Restructured book >3% of advances
⚠️ C/I ratio rising for 3+ consecutive quarters
⚠️ ROA <0.7% for 2+ years
```

---

## Banking Analysis Output Format

```
BANKING SECTOR ANALYSIS
Bank: [Name] | Ticker: [NSE/BSE] | CMP: ₹[X]
Type: [Private Large / Private Mid / PSB / SFB]
Analysis Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

ASSET QUALITY:
  Gross NPA:        [%]  → [Excellent/Good/Elevated/Stressed]
  Net NPA:          [%]  → [Assessment]
  PCR:              [%]  → [Conservative/Adequate/Aggressive]
  Slippage Ratio:   [%]  → [Assessment]
  Credit Cost:      [%]  → [Assessment]
  Watchlist/SMA-2:  [₹Cr or %] — [Disclosed? Y/N]

PROFITABILITY:
  NIM:              [%]  → [vs. peers + trend]
  ROA:              [%]  → [Assessment]
  ROE:              [%]  → [Assessment]
  C/I Ratio:        [%]  → [Assessment]
  Fee Income %:     [%]  → [Core vs. treasury split]

LIABILITY FRANCHISE:
  CASA Ratio:       [%]  → [Strong/Adequate/Weak]
  Cost of Deposits: [%]  → [Competitive?]
  CD Ratio:         [%]  → [Comfortable/Stretched]

CAPITAL:
  CAR:              [%]  → [Well-capitalised/Adequate/Concern]
  CET1:             [%]  → [Assessment]
  Capital Raise Risk: [Yes/No/Watch]

MANAGEMENT:
  Track Record:     [Strong/Adequate/Weak]
  NPA Guidance Accuracy: [Reliable/Mixed/Poor]
  RBI Issues:       [None/Historical/Active]

─────────────────────────────────────────────
VALUATION:
  Current P/B:      [X]x | Justified P/B: [X]x
  Current P/E:      [X]x | Normalised P/E: [X]x
  Verdict:          [Attractive/Fair/Expensive]

CRITICAL FLAGS:     [Count + list]
HIGH FLAGS:         [Count + list]

OVERALL VERDICT:
  Investment Case:  [Strong Buy / Buy / Hold / Reduce / Avoid]
  Key Risk:         [Single biggest risk]
  Key Catalyst:     [Single biggest upside driver]
  Monitoring Points: [Quarterly metrics to watch]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Banking Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 22. Skill 18 — NBFC Analyzer

**Merged from standalone file `AI_NBFC_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Non-Banking Financial Companies (NBFCs)

---

## CRITICAL AI INSTRUCTION

NBFCs are NOT banks. They cannot accept demand deposits, do not have access to RBI's LAF (Liquidity Adjustment Facility), and operate with higher funding cost and regulatory flexibility. Analysis must focus on **AUM quality, ALM (Asset-Liability Management), cost of borrowing, and collection efficiency**. The 2018 IL&FS and 2019–2020 NBFC crisis demonstrated that liquidity risk can destroy even fundamentally sound NBFCs overnight. **Funding stability analysis is non-negotiable.**

---

## Purpose

Deliver specialist analysis of Indian NBFCs covering all sub-segments: Housing Finance Companies (HFCs), Microfinance Institutions (MFIs), Vehicle Finance NBFCs, Gold Loan NBFCs, Consumer Finance NBFCs, and Diversified Lending NBFCs. Identify differentiated business models with sustainable NIMs, strong asset quality, and robust funding access.

---

## Pre-Flight Requirements

```
□ Latest Annual Report + last 8 quarters of investor presentations
□ Securitisation and co-lending disclosures
□ ALM (Asset-Liability Maturity) gap statement (RBI mandated)
□ Collection efficiency data (monthly if published)
□ Portfolio quality by segment / geography
□ Borrowing profile: bank lines, NCDs, ECB, commercial paper composition
□ Credit rating reports (critical for funding access)
□ Management concall transcripts (last 4 quarters)
□ Regulatory filings with RBI (Scale Based Regulation compliance tier)
```

---

## Analysis Module 1 — Business Model Classification

### Step 1.1 — NBFC Sub-Segment Identification
```
HOUSING FINANCE COMPANY (HFC):
  Focus: LTV ratios, property type mix, affordable vs. premium housing
  Regulator: NHB + RBI dual oversight
  Key metric: GNPA on home loans vs. project loans

MICROFINANCE INSTITUTION (MFI):
  Focus: Collection efficiency, geography concentration, overleveraging
  Regulator: RBI (NBFC-MFI licence)
  Key metric: PAR-30 (Portfolio at Risk >30 days)

VEHICLE FINANCE (CV/Two-Wheeler/PV):
  Focus: Vehicle type mix, used vs. new, repossession capability
  Regulator: RBI
  Key metric: Delinquency bucket movement

GOLD LOAN NBFC:
  Focus: LTV on gold, auction risk, gold price sensitivity
  Key metric: Yield on advances, LTV discipline

CONSUMER/PERSONAL FINANCE:
  Focus: Credit bureau penetration, underwriting quality
  Key metric: Bureau score distribution, DPD trends

DIVERSIFIED (Bajaj Finance type):
  Focus: Product mix, cross-sell, digital capabilities
  Key metric: EMI card base, RoE sustainability
```

### Step 1.2 — Business Quality Drivers
```
Rate of Return on AUM = Interest Yield − Credit Cost − Operating Cost
  → Sustainable positive spread = viable NBFC
  → Spread compression over 3 years = structural stress

Credit Substitution Power:
  → Can this NBFC serve customers banks cannot? (MSME, informal, rural)
  → If YES: defensible niche with pricing power
  → If NO: competing directly with banks at a cost disadvantage
```

---

## Analysis Module 2 — AUM (Assets Under Management)

### Step 2.1 — AUM Growth Quality
```
AUM Growth Rate:
  → >25% CAGR: Aggressive — verify asset quality is not sacrificed
  → 15–25% CAGR: Healthy growth
  → <10% CAGR: Stagnant — competitive issue or deliberate consolidation?

AUM Composition:
□ On-balance-sheet loans (full risk retained)
□ Off-balance-sheet (securitised, co-lending) — risk transferred?
□ Managed AUM: assets originated but sold → fee income model

Note: Companies reporting "AUM" growth while balance sheet is flat may be
      improving capital efficiency OR hiding stressed assets through sell-downs.
      Verify the quality of off-book assets.
```

### Step 2.2 — Disbursement Analysis
```
Disbursement vs. AUM:
→ Monthly/Quarterly disbursements: growing or declining?
→ Ticket size trend: increasing (product mix up-migration) or falling?
→ New customer vs. existing customer split (existing = lower risk, lower yield)
→ Geographic expansion: entering new states = higher risk initially

Disbursement Quality Red Flags:
⚠️ Rapid disbursement growth into new, unproven segments
⚠️ Disbursements concentrated in year-end quarter (window dressing)
⚠️ Average ticket size falling sharply in non-MFI segments (churning)
⚠️ Top 20 borrowers representing >30% of AUM (concentration in retail NBFC)
```

---

## Analysis Module 3 — Asset Quality

### Step 3.1 — NPA Metrics (Standard + Specific)
```
Gross NPA Ratio: Gross NPAs / Gross Loan Book
  → Benchmark varies by segment:
     Home Loans: <1.5% Excellent | <3% Good | >5% Stressed
     Vehicle Finance: <3% Excellent | 5% Good | >7% Stressed
     MFI: <3% Excellent | <5% Acceptable | >8% Critical
     Consumer Finance: <2% Excellent | <4% Good | >6% Stressed

Net NPA and PCR: Same methodology as banking analysis (see Banking Skill)

Stage Classification (IND-AS 109):
□ Stage 1: <30 DPD (days past due) — performing
□ Stage 2: 30–89 DPD — under-watch (significant increase in credit risk)
□ Stage 3: >90 DPD — NPA equivalent
→ Rising Stage 2 is the LEADING INDICATOR of future NPA increase
→ Check Stage 2 as % of total book quarterly
```

### Step 3.2 — Collection Efficiency
```
Collection Efficiency = Actual Collections / Due Collections × 100%

→ 98–100%: Excellent (benchmark for secured lending)
→ 95–98%: Good
→ 90–95%: Moderate concern
→ <90%: Serious collection stress

MFI-Specific:
→ PAR-30: Portfolio at Risk (balance with >30 DPD) / Total AUM
→ PAR-60 and PAR-90 for deeper stress assessment
→ COVID impact benchmark: CE fell to 70–80% in 2020; recovery took 6 quarters

Regional Stress Analysis:
□ Is collection stress concentrated in specific states?
□ Political risk: loan waiver announcements from state governments
□ Natural disaster impact on agricultural/rural portfolio
```

### Step 3.3 — Credit Cost Analysis
```
Credit Cost = Provisions (P&L) / Average AUM
  → Normalised credit cost = mid-cycle expectation
  → Current credit cost below normalised: UNDER-PROVISIONING risk
  → Current credit cost above normalised: Over-provisioning (positive for future earnings)

ECL (Expected Credit Loss) Buffer:
→ Stage 1 provision: 0.5–1% typical
→ Stage 2 provision: 5–25% depending on segment
→ Stage 3 provision: 50–100% depending on security
→ Total ECL / Total AUM: adequacy benchmark
```

---

## Analysis Module 4 — Funding and Liquidity (CRITICAL)

### Step 4.1 — Borrowing Profile
```
Sources of Funds:
□ Bank Borrowings: % of total — typically cheapest but relationship-dependent
□ Non-Convertible Debentures (NCDs): % — market access-dependent
□ Commercial Paper (CP): % — SHORT TERM, HIGH RISK if >15% of borrowings
□ External Commercial Borrowing (ECB): % — currency risk
□ Securitisation proceeds: % — liquidity improvement but ongoing servicing
□ Co-lending arrangements: % — partnerships with banks

Concentration Risk:
→ Top 3 lenders as % of total borrowings > 30% = HIGH dependency risk
→ Mutual fund CP dependency: post-IL&FS risk amplifier
→ Any single bank >15% of borrowings = key relationship risk
```

### Step 4.2 — ALM (Asset-Liability Mismatch) Assessment
```
ALM Gap = Assets Maturing in Period − Liabilities Maturing in Period

Critical Check:
□ 0–3 month gap: negative = refinancing risk
□ 3–12 month cumulative gap: should be positive (assets > liabilities)
□ 1–3 year gap: benchmark vs. industry

NBFC Structural Risk:
→ NBFCs borrow short (CP, 1-yr NCDs) but lend long (3–7 year loans)
→ NEGATIVE GAP at short end = must constantly refinance
→ If market seizes up (IL&FS event): NBFC faces existential liquidity crisis

Liquidity Buffer:
□ Liquid assets (G-Secs, FDs, cash) / Total liabilities due in 30 days
→ >100%: Comfortable | 50–100%: Adequate | <50%: Vulnerability
```

### Step 4.3 — Cost of Funds
```
Cost of Borrowings = Total Interest Expense / Average Borrowings
  → Compare vs. peers in same segment
  → Lower cost of funds = COMPETITIVE MOAT (pricing power + margin)
  → Factors driving lower cost: strong credit rating, large bank relationships, capital market access

Credit Rating Impact:
→ AAA: lowest borrowing cost, widest lender base
→ AA: moderate cost, most institutional lenders accessible
→ A or below: limited institutional lenders, higher CP rates
→ Rating downgrade: IMMEDIATE FUNDING CRISIS RISK
```

---

## Analysis Module 5 — NIM and Profitability

### Step 5.1 — Net Interest Margin
```
NIM = Net Interest Income / Average AUM

Benchmarks by Segment:
→ HFC (affordable): 3–4%
→ HFC (developer/project): 3.5–5%
→ Vehicle Finance: 5–8%
→ MFI: 9–12% (high credit cost offsets high yield)
→ Gold Loan: 10–14%
→ Consumer Finance (diversified): 9–13%

NIM Compression Drivers:
→ Competition from banks (lower cost lenders entering NBFC segment)
→ Rising borrowing costs passed through to customers only partially
→ Product mix shift toward lower-yield secured lending
```

### Step 5.2 — Operating Leverage and Efficiency
```
Cost-to-Income Ratio: Operating Costs / Net Total Income
→ <30%: Very efficient | 30–45%: Efficient | >55%: Inefficient

OpEx as % of AUM:
→ <2%: Efficient | 2–3%: Moderate | >4%: High cost structure

Employee per ₹100Cr of AUM: (Efficiency benchmark, segment-specific)
Technology Investment: Rising technology capex = future efficiency gain
Branch count trajectory: physical expansion (good for collections) vs. digital
```

### Step 5.3 — Return on Assets and Equity
```
ROA (Net Profit / Average AUM):
→ MFI: 3–5% (high risk, high yield)
→ Vehicle Finance: 2–3%
→ HFC: 1.5–2.5%
→ Diversified (Bajaj Finance): 3–4%

ROE (Net Profit / Average Equity):
→ >18%: Excellent | 14–18%: Good | 10–14%: Adequate | <10%: Weak
→ ROE = ROA × Leverage (Assets/Equity)
→ Leverage >7x in NBFC = high risk if asset quality deteriorates
```

---

## Analysis Module 5A — MFI-Specific Stress Framework

Only activate for NBFC-MFIs (Arohan, Spandana, Fusion, Asirvad, Muthoot Micro, etc.):

```
Overleveraging Detection (THE PRIMARY MFI RISK):
□ Average loans per borrower in district: RBI cap = ₹2 lakh total MFI exposure
□ Number of active MFI lenders per borrower: >4 lenders = overleveraging zone
   Data source: credit bureau (Equifax, CRIF, Experian for MFI)
□ Average borrower income vs. EMI: EMI > 50% of income = distress trigger
□ State-wise heat map: which states have rising active borrower-to-population ratio?
   HIGH RISK states historically: Andhra Pradesh, Telangana, Tamil Nadu (2010 crisis)
   CURRENT RISK states (monitor): UP, Bihar, Maharashtra rural

Waiver Risk Assessment:
□ State election calendar: waiver announcements cluster near elections
□ Pre-election year in key MFI states = elevated provisioning prudence
□ Historical waivers: which MFIs had highest exposure in waiver states?
□ Regulatory response: RBI typically issues circular post-waiver clarifying rights

Portfolio at Risk (PAR) Buckets:
PAR-0:  Any overdue → early signal (not NPA but watch)
PAR-30: > 30 DPD balance / AUM → Key metric
PAR-60: > 60 DPD balance / AUM → Slippage risk
PAR-90: = GNPA threshold

Healthy benchmarks: PAR-30 < 2% | PAR-60 < 1% | PAR-90 < 0.5%
Post-COVID normalisation: most MFIs back to benchmark by FY2023
2024-25 stress: monitor UP, Bihar, Maharashtra RMF segment carefully
```

## Analysis Module 5B — Co-Lending Impact Assessment

RBI Co-Lending Model (CLM) — understanding NBFC's position:

```
Structure: Bank (80% on book) + NBFC (20% on book) → joint origination
NBFC role: Customer acquisition, underwriting, collection
Bank role: 80% of funding at lower cost (beneficial for NBFC's NIM)

For NBFCs participating in co-lending:
□ % of disbursements via co-lending: rising = funding cost optimization
□ NIM on co-lending vs. own-book: typically lower by 100–200bps but
  lower credit cost (first-loss structure) improves risk-adjusted return
□ Bank partner quality: PSB vs. private bank → private bank partners
  have stricter underwriting (better portfolio quality)
□ FLDG (First Loss Default Guarantee): NBFC provides guarantee to bank
  → Cap at 5% per RBI rules; amounts above = regulatory violation
□ Off-book exposure via co-lending: reported in AUM but not balance sheet
  → Can mask true asset quality (co-lent book NPAs may not be captured)

Red Flag: Very rapid co-lending growth + off-book NPA data not disclosed
Positive: Co-lending growing for MFI/affordable housing = smart liability mgmt
```

## Analysis Module 5C — Technology-Driven Disruption Risk

```
Jio Financial Services (JFS) + BigTech NBFC Risk:
□ Which NBFC segments is JFS targeting? (Consumer lending, insurance, brokerage)
□ Digital-first NBFC: does incumben have tech moat or distribution moat?
□ Distribution moat: physical + relationship (durable) vs. purely digital (at risk)

Fintech NBFC Competition:
□ Personal loan segment: most disrupted (Navi, CASHe, MoneyView)
□ MSME lending: growing disruption (Flexiloans, Lendingkart)
□ Embedded finance: e-commerce NBFCs (Bajaj Finserv's Bajaj Pay, PayU Credit)
□ Gold loan: Rupeek (digital gold loan) pressuring traditional players

Incumbent NBFC Response Assessment:
□ Has NBFC built digital loan journey? (From application to disbursement)
□ Mobile app rating: App Store / Play Store rating > 4.0 = reasonable UX
□ API integration with third parties: ecosystem vs. walled garden
□ Data analytics for credit scoring: bureau + alternative data usage
→ NBFCs with strong physical network + improving digital: BEST POSITION
→ NBFCs with only physical + no digital investment: MEDIUM-TERM RISK
→ Pure digital NBFCs: scalable but asset quality untested in downturn
```

## Analysis Module 6 — Regulatory Position

### Step 6.1 — RBI Scale-Based Regulation (SBR) Tier
```
Base Layer: AUM < ₹1,000Cr — lighter regulation
Middle Layer: AUM ₹1,000Cr–₹500Cr + complex NBFCs
Upper Layer: Systemically important NBFCs (identified by RBI)
Top Layer: NBFCs needing bank-like regulation (effectively conversion)

Higher tier = more regulatory burden but also more credibility
Regulatory capital adequacy (Tier 1 minimum) for Upper Layer: 10%
```

### Step 6.2 — Compliance Monitoring
```
□ SARFAESI access: large NBFCs can now use SARFAESI for recovery
□ Co-lending norms compliance
□ Concentration norms: single borrower limit
□ Fair practice code compliance: RBI observations
□ Priority sector lending targets (for NBFC-MFIs)
□ Any RBI show-cause notice or corrective directive?
```

---

## Red Flag Summary — NBFC

### CRITICAL Flags
```
❗ Credit rating downgrade (especially A → BBB or below)
❗ CP rollover refused by any major mutual fund
❗ ALM gap negative at 0–3 month bucket with no liquid assets
❗ Promoter pledging NBFC shares to meet company obligations
❗ Auditor resignation or qualified opinion
❗ RBI enforcement action or regulatory directive
❗ GNPA >10% in retail segments
❗ Collection efficiency below 85% for 2+ consecutive quarters
```

### HIGH Flags
```
⚠️ CP as % of borrowings >20%
⚠️ Top 3 lenders >40% of total borrowings
⚠️ AUM growing >40% while asset quality deteriorating
⚠️ Stage 2 book rising sharply (>8% of book)
⚠️ Credit cost doubling from prior year without management explanation
⚠️ NIM compression >100bps in one year
⚠️ Leverage (Debt/Equity) >8x
⚠️ Management exodus (CFO, CRO change)
```

---

## NBFC Valuation Framework

```
Primary Method: P/B (Price-to-Book)
  Justified P/B = ROE / Cost of Equity (same as banking)

Adjust for:
+Premium for: AAA rating, diversified funding, wide NIM moat, tech advantage
−Discount for: concentration risk, CP-heavy funding, governance concern, MFI segment

Secondary Method: P/AUM
  → Bajaj Finance: 10–15x P/AUM (exceptional franchise)
  → Quality HFC: 3–5x P/AUM
  → Vehicle Finance: 2–4x P/AUM
  → MFI: 1.5–3x P/AUM
  → Gold Loan: 2–4x P/AUM
  
P/E Method:
→ Normalise EPS using mid-cycle credit cost
→ 20–30x for premium NBFCs | 10–15x for mid-quality | <10x for stressed
```

---

## NBFC Analysis Output Format

```
NBFC SECTOR ANALYSIS
Company: [Name] | Segment: [HFC/MFI/Vehicle/Gold/Consumer/Diversified]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

AUM QUALITY:
  AUM (Total):          ₹[X]Cr | Growth: [%] YoY
  On-Book / Off-Book:   [%] / [%]
  Disbursements (Qtr):  ₹[X]Cr | Growth: [%] YoY
  Stage 2 Book:         [%] of AUM → [Rising/Stable/Falling]

ASSET QUALITY:
  GNPA:                 [%] → [Assessment]
  Net NPA:              [%]
  PCR:                  [%]
  Collection Efficiency:[%] → [Assessment]
  Credit Cost (Ann.):   [%] → [vs. normalised [%]]

FUNDING:
  Cost of Borrowings:   [%]
  CP as % of Funding:   [%] → [Safe/Caution/Risk]
  Top 3 Lender %:       [%] → [Concentration OK/Concern]
  Credit Rating:        [AAA/AA+/AA/etc.]
  ALM Gap (0–3 month):  [Positive/Negative — ₹Cr]

PROFITABILITY:
  NIM:                  [%] → [vs. segment benchmark]
  ROA:                  [%] → [Assessment]
  ROE:                  [%]
  Cost-to-Income:       [%]

CAPITAL:
  Tier 1 Capital Ratio: [%] → [RBI requirement: 10%]
  Leverage (D/E):       [X]x

CRITICAL FLAGS:         [Count + list]
HIGH FLAGS:             [Count + list]

VALUATION:
  P/B (Current):        [X]x | Justified: [X]x
  P/E (Normalised):     [X]x
  Verdict:              [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Investment Case:      [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:             [Single biggest risk]
  Key Catalyst:         [Single biggest upside driver]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | NBFC Sector*
*Integrates with: Banking Analysis Skill, Forensic Accounting Skill, DCF Valuation Skill*

## 23. Skill 19 — Insurance Sector Analyzer

**Merged from standalone file `AI_Insurance_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Life Insurance, General Insurance, Health Insurance, Reinsurance

---

## CRITICAL AI INSTRUCTION

Insurance companies are unique financial businesses where **revenue (premiums) is collected upfront but costs (claims) are paid later** — sometimes years later. This creates both an opportunity (float investing) and a danger (reserve inadequacy). Standard P&L analysis misleads. Focus on **Embedded Value (for life), Combined Ratio (for general), Solvency Ratio, VNB margin, and persistency**. Never judge an insurer by headline net profit alone — it is heavily influenced by actuarial assumptions.

---

## Purpose

Deliver institutional-grade analysis of Indian insurance companies across life, general, and health insurance segments. Assess underwriting profitability, reserve adequacy, investment performance, distribution strength, and long-term franchise value using insurance-specific metrics.

---

## Pre-Flight Requirements

```
□ Annual Report including Actuarial Report and Embedded Value Report
□ IRDAI regulatory filing and annual statistics disclosure
□ Quarterly investor presentation with VNB data
□ Last 8 quarters of financial results
□ Persistency data (13th month, 25th month, 37th month, 61st month)
□ Claims ratio by product line (for general/health)
□ Solvency ratio trend (quarterly)
□ Reinsurance arrangement disclosures
□ Investment portfolio composition and yield
□ Channel mix: agency, bancassurance, direct, online
```

---

## Analysis Module 1 — Business Model Classification

### Step 1.1 — Insurance Segment Type
```
LIFE INSURANCE:
  Products: Term, ULIP, Participating, Non-Participating, Annuity, Group
  Regulator: IRDAI
  Key Metrics: APE, VNB, VNB Margin, EV, EVOP, Persistency
  Revenue driver: New Business Premium + Renewal Premium
  Profitability driver: VNB Margin × APE Growth

GENERAL INSURANCE:
  Products: Motor, Property, Marine, Liability, Engineering, Crop
  Regulator: IRDAI
  Key Metrics: Gross Written Premium (GWP), Combined Ratio, Loss Ratio
  Revenue driver: GWP growth across segments
  Profitability driver: Combined Ratio <100% = underwriting profit

HEALTH INSURANCE (Standalone):
  Products: Individual, Group, Government schemes
  Regulator: IRDAI
  Key Metrics: Loss Ratio, Renewal Rate, Claim Settlement Ratio
  Key Challenge: Medical inflation, claims severity, underwriting accuracy

REINSURANCE:
  GIC Re: Only Indian reinsurer
  Key: Retention ratio, catastrophe exposure, international book
```

---

## Analysis Module 2 — Life Insurance Specific Metrics

### Step 2.1 — Premium Metrics
```
Annualised Premium Equivalent (APE):
  APE = Regular Premium + Single Premium × 10%
  → Normalises comparison between regular and single premium products
  → APE growth: >15% CAGR = strong momentum

New Business Premium (NBP):
  → First-year premium only
  → Single vs. regular premium mix matters (regular = sticky, recurring)
  
Renewal Premium:
  → Directly linked to past business quality (persistency)
  → Renewal premium / Total premium ratio: >60% = mature, sticky book
  
Product Mix:
  → Term: high VNB margin (protection), lower ticket
  → ULIP: low VNB margin (market-linked), higher ticket
  → Participating: medium margin, with-profits sharing
  → Non-Participating: high margin (especially non-PAR savings)
  → Annuity: low margin, long-duration (ALM risk)
  → Group: low margin, volatile
  
High VNB margin mix = Non-PAR + Term dominant
Low VNB margin mix = ULIP + Group dominant
```

### Step 2.2 — Embedded Value (EV) — THE CORE METRIC FOR LIFE INSURANCE
```
Embedded Value = Adjusted Net Worth + Value of In-Force Business (VIF)

Where:
→ Adjusted Net Worth (ANW): Market value of shareholder-owned assets
→ VIF: Present value of future profits from existing in-force policies

VNB (Value of New Business):
→ VNB = Present value of future profits from NEW business written in a period
→ VNB Margin = VNB / APE × 100%

VNB Margin Benchmarks:
→ >25%: Excellent (protection-heavy, efficient distribution)
→ 20–25%: Good
→ 15–20%: Average
→ <15%: Weak (ULIP-heavy or high-cost distribution)

Operating Embedded Value Earnings (EVOP):
→ Expected return on EV (normal) + VNB (new business) + Operating variances
→ EVOP / Opening EV > 10% = value accretion

EV Growth = EVOP + Market variances + Capital actions
→ If EV is not growing faster than cost of capital: franchise is destroying value
```

### Step 2.3 — Persistency Analysis (CRITICAL FOR LIFE INSURANCE)
```
Persistency = % of policies that renew at each anniversary

13th Month Persistency: % renewing after Year 1
  → <70%: Poor | 70–80%: Moderate | >80%: Good | >85%: Excellent
25th Month Persistency: % still active after Year 2
61st Month Persistency: 5-year retention

Why It Matters:
→ Low persistency = policies lapsing before recouping acquisition cost
→ Lapse = loss of future VIF; damages VNB margin projections
→ High lapse = mis-selling indicator (customers bought wrong product)

Red Flag:
→ 13th month persistency <70% signals systemic mis-selling or poor product fit
→ Bancassurance channel often has lower persistency than agency
```

---

## Analysis Module 3 — General Insurance Specific Metrics

### Step 3.1 — Gross Written Premium (GWP) Analysis
```
GWP = Total premium written before ceding to reinsurer
Net Written Premium = GWP − Reinsurance Ceded

GWP Growth by Segment:
□ Motor OD (Own Damage): vehicle sales linked
□ Motor TP (Third Party): mandatory, price-regulated by IRDAI
□ Health: fastest growing, claims-intensive
□ Property: large industrial risks, catastrophe exposure
□ Crop: government-backed (PMFBY), margins thin, lumpy

Preferred Segment Mix:
→ Higher retail health + motor OD = more predictable, higher margin
→ Heavy crop/government = low margin, dependent on government
→ Industrial/property concentration = lumpy results, catastrophe risk
```

### Step 3.2 — Combined Ratio (THE CORE METRIC)
```
Combined Ratio = Loss Ratio + Expense Ratio

Loss Ratio = Net Incurred Claims / Net Earned Premium × 100%
  → <65%: Excellent | 65–75%: Good | 75–85%: Average | >90%: Underwriting loss risk

Expense Ratio = Operating Expenses / Net Written Premium × 100%
  → <25%: Efficient | 25–35%: Average | >35%: High cost

Combined Ratio Interpretation:
→ <100%: Underwriting PROFIT — core insurance business is profitable
→ 100–105%: Underwriting at cost — depends on investment income for profit
→ >110%: Underwriting LOSS — investment income must offset (unsustainable if prolonged)

India Benchmarks (FY2025):
→ Best-in-class private general insurer: 95–100% combined ratio
→ PSU general insurers: often 105–115% (underwriting losses)
→ Health-focused standalone: 100–108% (claims inflation driving up)
```

### Step 3.3 — Claims Analysis
```
□ Claim Settlement Ratio: % of claims settled / claims reported
   → >95%: Good | 85–95%: Average | <85%: Poor (customer trust issue)
□ Claims Repudiation Ratio: % rejected — too high = regulatory risk
□ Average Claims Settlement Time: regulatory maximum 30 days
□ Large Claims / Catastrophe Events: any one-time spikes?
□ Medical Inflation Impact (health): CPI medical inflation typically 10–15% pa
□ Reserving Adequacy: IBNR (Incurred But Not Reported) reserves — conservative?
```

---

## Analysis Module 4 — Solvency and Capital

### Step 4.1 — Solvency Ratio
```
Solvency Ratio = Available Solvency Margin / Required Solvency Margin

Regulatory Minimum: 1.5x (150%)
→ <150%: CRITICAL — regulatory breach imminent
→ 150–175%: Adequate but thin buffer
→ 175–200%: Comfortable
→ >200%: Well-capitalised

Solvency Trends:
→ Declining solvency: fast premium growth consuming capital faster than profits
→ Rising solvency: strong profits or capital infusion
→ Public market listing often improves solvency (IPO proceeds)
```

### Step 4.2 — Investment Portfolio Quality
```
Life Insurance Float:
→ % in G-Secs (mandatory portion, ~50%+ for traditional products)
→ % in equities (higher for ULIPs — full risk to policyholder)
→ % in corporate bonds: credit quality distribution
→ Investment yield: [Total investment income / Average investments]

General Insurance Float:
→ Shorter duration (claims pay faster than life)
→ More liquid: T-bills, short-duration bonds, money market
→ Investment income often makes up for underwriting losses

Float Quality Check:
→ Any downgraded corporate bonds in portfolio?
→ Related-party investments in insurer portfolio?
→ Equity portfolio concentrated in promoter's other companies?
```

---

## Analysis Module 5 — Distribution and Growth

### Step 5.1 — Channel Mix
```
Agency (Individual Agents):
  → Highest persistency, highest VNB margin potential
  → Scalability limited by agent recruitment and productivity
  → Productive agent count trend: key leading indicator

Bancassurance:
  → High volume, lower VNB margin (bank takes large cut)
  → Exclusive bancassurance = concentration risk
  → Bank partner quality matters (reach + customer base)

Online / Direct:
  → Lowest cost, fast growing (especially term insurance)
  → Customer self-selection = better risk profile typically

Group:
  → Low margin, high volume, volatile (employer changes)
  → Government schemes: high volume, very low margin

Preferred Mix:
→ Agency + Online > Bancassurance + Group = Higher VNB margin
```

### Step 5.2 — Market Share and Competitive Position
```
Life Insurance Market Share (by APE / NBP):
→ LIC: ~60% + (declining slowly)
→ SBI Life, HDFC Life, ICICI Pru, Max Life: 5–10% each
→ Mid-size: 1–5% each

General Insurance Market Share (by GWP):
→ New India: ~15% (PSU)
→ Private leaders: 8–12% each

Market Share Trajectory:
→ Gaining in high-margin segments = positive
→ Losing share due to rational underwriting = not necessarily negative
→ Gaining share by underpricing = RED FLAG
```

---

## Analysis Module 5A — IRDAI 2024–25 Regulatory Changes (Critical Updates)

```
IRDAI New Surrender Value Norms (Effective 2024):
→ Insurers must pay higher guaranteed surrender values from Year 1 onwards
→ Impact: Reduces the "lock-in" advantage of traditional policies
→ Impact on insurers: Higher strain on new business (upfront cost)
→ Impact on VNB margin: Compression expected 100–300bps for non-PAR segment
□ Has management quantified the VNB margin impact?
□ Has product mix been shifted to offset (more pure term, less long-term savings)?
□ Is new business strain rising? (OCF temporarily negative = acceptable)

IRDAI Bima Sugam (Insurance Digital Platform):
→ Universal insurance marketplace: compare, buy, service online
→ Risk to bancassurance channel: customers may bypass bank distribution
→ Opportunity for tech-savvy insurers: direct acquisition at lower cost
□ Is insurer participating? Digital capability assessment

IRDAI Composite License (Proposed):
→ Single entity may offer both life and general insurance
→ Current law: separate entities required
→ If approved: M&A activity + capital efficiency for large groups
→ Companies to watch: HDFC Life + Ergo, Tata Life + Tata AIG type synergies

Risk-Based Capital (RBC) Framework (Proposed):
→ Moving from current factor-based solvency to risk-sensitive model
→ Companies with volatile portfolios may need more capital
→ Companies with conservative portfolios benefit
□ Management commentary on RBC readiness
```

## Analysis Module 5B — Health Insurance Specific Deep Dive

Only activate for: Star Health, Niva Bupa, Care Health, ICICI Lombard Health segment:

```
Health Insurance Unique Metrics:
□ Incurred Claims Ratio (ICR) = Claims Incurred / Net Earned Premium
   → Individual health: 60–75% acceptable | >85% = underwriting concern
   → Group health: 80–90% typical (lower margin by design)
   → Government schemes (Ayushman Bharat): 95–105% (volume play, low margin)

□ Claim Settlement Ratio: % of claims settled vs. filed
   → >95%: Customer trust | <90%: IRDAI action risk

□ Renewal Rate (Retention):
   → Individual: >85% renewal = sticky book
   → < 75%: Customer dissatisfaction or churning due to premium hike

□ Hospital Network Size: cashless hospitalisation reach
   → > 10,000 hospitals: broad access | < 5,000: limited reach

Medical Inflation Impact:
→ India medical inflation: 12–15% annually
→ Premium increase allowed: IRDAI approval required; typically 10–15%/year
→ If medical inflation > premium increase: margin compression unavoidable
→ Underwriting discipline: focus on healthier cohorts, better claims management

Fraud Control:
□ Claims fraud rate as % of total claims: >3% = systemic issue
□ Anti-fraud technology investment: AI-based claim scrubbing
□ Field investigation unit coverage: % of claims investigated before payment
```

## Analysis Module 5C — Embedded Value Sensitivity Analysis (Life Insurance)

```
EV is not just a number — it is highly sensitive to assumptions.
Always check WHAT assumptions the actuary used:

Key EV Assumption Sensitivities:
Assumption           | Direction | Impact on EV
─────────────────────────────────────────────────────────
Discount Rate +100bps| Higher    | EV falls (present value of future profits reduces)
Lapse Rate +100bps   | Higher    | EV falls (more policies lapsing)  
Mortality +5%        | Higher    | Term life: EV FALLS | Annuity: EV RISES
Investment return −1%| Lower     | EV falls (non-PAR returns depend on investment yield)
Expense overrun +10% | Higher    | EV falls

Sensitivity Disclosure Check:
□ Does the company publish a sensitivity table in their EV report? (SHOULD)
□ If EV change from -1% discount rate > 20%: model is fragile
□ If lapse sensitivity is large: persistency improvements can significantly unlock EV

Actuarial Assumption Red Flags:
⚠️ Discount rate lowered (boosts EV without real business improvement)
⚠️ Lapse rate assumption improved suddenly without corresponding persistency data
⚠️ Operating variances consistently negative (actuary over-estimated new business quality)
⚠️ EV growth from investment return only (no EVOP = no new value created)
```

## Analysis Module 6 — Management Quality and Regulation

### Step 6.1 — Management Assessment
```
□ VNB margin trend: improving consistently = disciplined underwriting
□ Product mix strategy: protection push (higher margin) = shareholder-friendly
□ Agent productivity: increasing over time = scalable model
□ Claims handling reputation: customer complaints ratio to IRDAI
□ Investment returns: benchmark vs. stated return assumptions in actuarial reports
□ CEO tenure and succession: long-tenured leaders with clear succession
```

### Step 6.2 — Regulatory Environment
```
□ IRDAI product approval timelines: faster for compliant companies
□ Expense ratio regulations: IRDAI caps expenses — compliance
□ Surrender charge regulations: IRDAI reducing lock-in → persistency risk
□ Health insurance regulation: TPA (Third Party Administrator) norms
□ Solvency norm updates: IRDAI moving toward risk-based solvency (RBS)
□ Foreign ownership limit: 74% FDI allowed (investment thesis for M&A plays)
```

---

## Valuation Framework — Insurance

### Life Insurance: P/EV (Price-to-Embedded Value)
```
Intrinsic Value = EV + (VNB × VNB Multiplier)

VNB Multiplier benchmarks:
→ >25x VNB: Premium franchise (HDFC Life quality)
→ 20–25x: Quality franchise
→ 15–20x: Average
→ <15x: Value / distressed

P/EV Ratio:
→ >3x: Premium (strong VNB growth, persistency, brand)
→ 2–3x: Fair
→ <2x: Value territory (check for quality issues)
→ <1x: Distressed / deep value (investigate before buying)
```

### General Insurance: P/GWP or P/B
```
P/GWP:
→ Quality private: 3–5x GWP
→ Average private: 1.5–3x GWP
→ PSU: 0.5–1.5x GWP (discount for structural inefficiency)

P/B:
→ Profitable (CR <100%): 3–5x book
→ Break-even (CR ~100%): 1.5–3x book
→ Underwriting loss: <1.5x book
```

---

## Red Flag Summary — Insurance

### CRITICAL Flags
```
❗ Solvency ratio approaching 150% minimum
❗ 13th month persistency <65%
❗ Combined ratio >115% for 2+ consecutive years
❗ IRDAI enforcement action / show-cause notice
❗ Auditor qualification on reserve adequacy
❗ VNB margin declining for 4+ consecutive quarters
❗ Embedded value falling (negative EVOP)
❗ Claim settlement ratio <80%
```

### HIGH Flags
```
⚠️ Loss ratio rising >500bps year-on-year
⚠️ Single bancassurance partner >50% of new business
⚠️ GWP growth via deep discounting in motor/health
⚠️ Investment portfolio: >10% in below-AA rated bonds
⚠️ Agent count declining
⚠️ Reinsurance cession rising sharply (capacity issue or poor underwriting)
⚠️ Actuarial assumption changes flattering EV (read EV report footnotes)
```

---

## Insurance Analysis Output Format

```
INSURANCE SECTOR ANALYSIS
Company: [Name] | Segment: [Life/General/Health/Reinsurance]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

[FOR LIFE INSURANCE]
BUSINESS QUALITY:
  APE Growth (YoY):     [%]  | New Business:  ₹[X]Cr
  VNB:                  ₹[X]Cr | VNB Margin:  [%] → [vs. prior year]
  Product Mix:          [Protection [%] | ULIP [%] | NonPAR [%] | PAR [%]]
  Persistency (13M):    [%] → [Good/Average/Poor]
  Embedded Value:       ₹[X]Cr | EVOP: [%] of opening EV

[FOR GENERAL INSURANCE]
BUSINESS QUALITY:
  GWP Growth (YoY):     [%]
  Segment Mix:          [Motor [%] | Health [%] | Property [%] | Other [%]]
  Combined Ratio:       [%] → [Underwriting: Profit/Loss/Breakeven]
  Loss Ratio:           [%]
  Expense Ratio:        [%]

SOLVENCY:               [X]x → [Well-capitalised/Adequate/Concern]
Investment Yield:       [%]

DISTRIBUTION:
  Channel Mix:          [Agency [%] | Banca [%] | Online [%] | Group [%]]
  Key Observations:     [Any concentration / shift]

CRITICAL FLAGS:         [Count + list]
HIGH FLAGS:             [Count + list]

VALUATION:
  P/EV:                [X]x (Life only — justified [X]x)
  P/GWP or P/B:        [X]x → [Assessment]
  Verdict:             [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Investment Case:     [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:            [Biggest risk]
  Key Catalyst:        [Biggest upside driver]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Insurance Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 24. Skill 20 — Pharmaceutical Sector Analyzer

**Merged from standalone file `AI_Pharma_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Pharmaceuticals, Biotech, API, CDMO, Medical Devices

---

## CRITICAL AI INSTRUCTION

Pharma analysis requires simultaneous understanding of science, regulation, and business. A company with an excellent product pipeline can be destroyed by a single USFDA Warning Letter. A commodity API manufacturer can transform into a high-value specialty player. **Never assess pharma purely on P&L multiples — always assess regulatory standing, pipeline depth, R&D quality, and geographic mix first.** USFDA compliance is non-negotiable for any US-facing pharma.

---

## Purpose

Deliver specialist analysis of Indian pharmaceutical companies covering domestic branded generics, US generics, API manufacturing, specialty/innovator, CDMO/CMO, and biosimilars. Identify regulatory risks, pipeline quality, market position, and sustainable competitive advantages.

---

## Pre-Flight Requirements

```
□ Annual Report (last 3 years)
□ USFDA inspection history (FDA website: fda.gov/FOIA, 483 letters, Warning Letters)
□ ANDA filing and approval status (FDA Orange Book data)
□ Domestic market share data (IQVIA/AIOCD market data if available)
□ R&D pipeline disclosures from investor presentations
□ Geographic revenue breakdown (India / US / Europe / Emerging Markets / API)
□ Management concall transcripts (last 4 quarters)
□ Patent filing and expiry data (for innovator-facing plays)
□ Capex plan for facility expansion / new facilities
□ CDSCO (India regulator) and EMA (Europe) compliance status
```

---

## Analysis Module 1 — Business Model Classification

### Step 1.1 — Pharma Sub-Segment Identification
```
DOMESTIC BRANDED GENERICS (India-focused):
  Companies: Mankind, Abbott India, Ipca, Eris Lifesciences
  Revenue driver: Prescription volume + price indexation
  Key metric: IQVIA market growth vs. company growth, MR productivity
  Risk: Price control (NLEM), generic substitution

US GENERICS:
  Companies: Sun Pharma, Dr Reddy's, Cipla, Lupin, Aurobindo
  Revenue driver: ANDA approvals, first-to-file (FTF) exclusivity, price erosion
  Key metric: ANDA pipeline strength, market share in key molecules
  Risk: Price erosion, USFDA compliance, channel consolidation

API (Active Pharmaceutical Ingredient):
  Companies: Divi's, Laurus Labs, Hikal, Aarti Pharmalab
  Revenue driver: Volume × realisation, new molecule ramp-up
  Key metric: EBITDA/kg, customer concentration, regulatory filings
  Risk: China competition, raw material volatility, single-customer dependency

CDMO (Contract Development and Manufacturing):
  Companies: Divi's, Laurus, Syngene, Piramal Pharma
  Revenue driver: Long-term contracts with global innovators
  Key metric: Order book, customer stickiness, technology capability
  Risk: Client concentration, IP confidentiality risk

SPECIALTY / INNOVATOR:
  Companies: Sun Pharma (Ilumya, Winlevi), Biocon (biosimilars)
  Revenue driver: Proprietary products in regulated markets
  Key metric: Product revenue, pipeline milestones, patent life
  Risk: Clinical trial failure, competition, pricing pressure

HOSPITAL / DIAGNOSTICS (adjacent):
  Companies: Narayana, Apollo, Thyrocare, Metropolis
  Covered under separate Healthcare Skill — refer if needed.
```

---

## Analysis Module 2 — Regulatory Framework (Tier 1 Priority)

### Step 2.1 — USFDA Compliance Assessment
```
Facility Inspection Outcomes (most recent):
□ VAI (Voluntary Action Indicated): CLEAN — proceed normally
□ OAI (Official Action Indicated): CONCERN — remediation needed
□ Warning Letter: CRITICAL — shipment ban risk, major remediation
□ Import Alert / Application Integrity Policy: CRITICAL — near-total business halt

Check for EACH manufacturing facility:
→ Last inspection date
→ Inspection outcome
→ Any 483 observations (observations ≠ failure but indicate issues)
→ Warning Letter: is it resolved? Timeline?
→ Consent Decree: most severe — company under FDA supervision

CRITICAL RULE: A Warning Letter for a US-facing facility = 30–50% revenue risk.
Never assume resolution until FDA issues EIR (Establishment Inspection Report).
```

### Step 2.2 — USFDA Pipeline Assessment
```
ANDA (Abbreviated New Drug Application) Pipeline:
□ Total ANDAs filed
□ Total ANDAs approved (vs. total filed = approval conversion rate)
□ ANDAs pending (backlog size)
□ First-to-File (FTF) / Paragraph IV applications: highest value
□ Final Para IV exclusivity remaining (180-day first-to-market)

ANDA Value Assessment:
→ Para IV with 180-day exclusivity + large market size = significant upside
→ Commodity generic (10+ competitors): minimal value
→ Complex generics (injectables, inhalers, derma): higher barriers, better margins
→ Abbreviated New Drug Applications for specialty = rare opportunity

Pipeline Priority Score:
→ FTF Para IV filings × Market size = Revenue opportunity
→ Complex generics in pipeline = margin expansion potential
```

### Step 2.3 — Other Regulatory Compliance
```
CDSCO (India):
□ Manufacturing licence compliance
□ New drug approvals in India
□ Drug recall history (serious = RED FLAG)

EMA (Europe):
□ EU-GMP compliance status for all facilities
□ CEP (Certificate of Suitability) for API exports

WHO-GMP and TGA (Australia), PMDA (Japan):
□ Relevant for emerging market exports and regulated markets
□ WHO pre-qualification: required for UN procurement contracts

Facility Count and Compliance Map:
Build: [Plant Name → Location → Regulator → Last Inspection → Status]
```

---

## Analysis Module 3 — Domestic Business (India)

### Step 3.1 — India Market Position
```
Domestic Formulations Business:
→ Revenue from domestic branded generics
→ Chronic vs. Acute therapy split:
   Chronic (Cardiac, Diabetes, CNS, Derma): recurring prescriptions, sticky
   Acute (Anti-infective, Pain): seasonal, doctor discretion

Therapy Area Leadership:
□ Market share in key therapies (IQVIA data)
□ Rank in therapy: #1 or #2 = pricing power | #5+ = follower, margin pressure
□ Top 10 brands as % of domestic revenue (concentration vs. diversification)

IQVIA India Pharma Market (IPM) Growth Benchmark:
→ India pharma market growing ~10–12% CAGR
→ Company growing faster than IPM = gaining share (positive)
→ Company growing slower than IPM = losing share (negative)

Medical Representative (MR) Productivity:
→ Total domestic revenue / MR headcount
→ Rising productivity = efficient field force | Falling = churning issue
```

### Step 3.2 — NLEM (National List of Essential Medicines) Risk
```
□ What % of domestic revenue is from NLEM products?
→ NLEM products: price controlled by NPPA
→ Price hike for NLEM: limited to WPI inflation (annual index)
→ Non-NLEM: free pricing (10% hike per year maximum)
→ High NLEM % = lower pricing power

NLEM revision risk:
→ New products added to NLEM = revenue/margin impact for company
→ Monitor: NPPA announcements, NLEM revision proposals
```

---

## Analysis Module 4 — US Business

### Step 4.1 — US Revenue Quality
```
US Revenue Composition:
□ Base business: existing generic portfolio (price erosion typically 5–15% annual)
□ New launches: ANDAs approved in current year launching
□ Specialty: differentiated products (higher margin, lower volume)
□ Para IV exclusivities: time-limited but high-value

US Price Erosion Management:
→ Price erosion in commoditised generics: -5% to -15% per year
→ Offsetting: new approvals, specialty mix-up, volume gains
→ Net US growth = Volume growth + New launches − Price erosion
→ Declining US revenue with no new approvals = structural problem

Key US Buyers:
→ Big 3 distributors: McKesson, Cardinal Health, AmerisourceBergen
→ GPOs (Group Purchasing Organizations) control formulary access
→ Concentration risk: >60% to one distributor = pricing vulnerability
```

### Step 4.2 — US Profitability
```
US EBITDA Margin:
→ Specialty/FTF products: 40–60% EBITDA margin
→ Standard generics: 15–25% EBITDA margin
→ Commoditised: <15%

US Business Contribution:
→ For most top-tier Indian pharma: US = 30–50% of revenue but 50–70% of profit
→ US business leverage: one successful FTF = significant earnings jump
```

---

## Analysis Module 5 — R&D Quality Assessment

### Step 5.1 — R&D Spending
```
R&D Expense as % of Revenue:
→ <3%: Low R&D intensity (generics-focused, commodity risk)
→ 3–8%: Moderate (generics + some specialty pipeline)
→ 8–15%: High (specialty/innovator aspirations)
→ >15%: Very high (innovator pipeline, check returns on investment)

R&D Capitalisation Policy:
→ Companies that capitalise R&D inflate assets and reduce expense charge
→ Check: R&D expense in P&L vs. total R&D spend (per annual report notes)
→ Capitalisation rate >30% = aggressive; verify with auditor's KAM

R&D ROI Assessment:
→ Historical R&D spend vs. new product revenues generated
→ Clinical trial success rate (for specialty pipeline)
→ ANDA filing rate per ₹100Cr of R&D spend
```

### Step 5.2 — Pipeline Quality Framework
```
Stage-Gate Assessment:
Pre-Clinical → Phase 1 → Phase 2 → Phase 3 → Regulatory Filing → Launch

Higher the stage, higher the probability of success and value.
Generic pipeline:
  → ANDA filed = 70–80% probability of eventual approval
  → Complex generics: 50–60% (higher technical barrier)
  → Specialty NDA (innovator): 20–40% from Phase 3

Biosimilars (High-Value Emerging Segment):
→ Reference biologic identified → Development → Clinical studies → Approval
→ Cost of development: ₹150–400Cr per biosimilar
→ Market opportunity: $100B+ in global biologics going off-patent by 2030
→ Indian players: Biocon, Dr Reddy's, Cipla, Sun Pharma → assess pipeline depth
```

---

## Analysis Module 5A — Domestic Pharma: Price-Volume Decomposition

```
India Formulations Revenue = Volume Growth + Price Realisation Change + Mix Shift

Data Source: IQVIA (IMS) Monthly Market Report — key reference

Step 1: IQVIA MAT (Moving Annual Total) Growth vs. Company India Growth
→ IQVIA MAT India Pharma Market growth (typically 9–12%)
→ Company India growth vs. IQVIA: outperforming = gaining share
→ Price component vs. volume component in IQVIA data
   → FY2025 context: Price growth ~3-4% | Volume growth ~6-7%

Step 2: Therapy-wise decomposition (if company discloses)
→ Chronic (Cardiac, Diabetes, CNS) vs. Acute (Anti-infectives, Pain)
   Chronic share rising = better recurring revenue quality
   Acute share high = seasonal volatility in revenue

Step 3: Brand rank analysis
→ Top 10 brands: total revenue share; rank movement (IQVIA Brand Rankings)
→ No. 1 or 2 brand in therapy: pricing power, doctor loyalty
→ Falling brand rank: generic substitution or competitive loss

Medical Representative (MR) Productivity:
□ MR count (from headcount disclosures or management commentary)
□ India formulations revenue / MR count = Revenue per MR
   → Benchmark: ₹35–55 lakh per MR per year (varies by therapy)
   → Rising productivity = field force efficiency improving
   → Falling productivity = churn, wrong therapy focus, or saturation
□ MR attrition rate: >20% annual = instability | >30% = serious concern
□ Specialty MR vs. general MR: specialty MRs (Oncology, Derma) are 
  more productive but costlier and harder to retain
```

## Analysis Module 5B — Para IV First-to-File Economics

Para IV = Challenge to innovator patent; first filer gets 180-day US marketing exclusivity.

```
Economic Model of a Para IV FTF:
Market Size (US):            $X million (branded drug sales)
Market Share (180-day excl): 25–50% (only filer, no competition)
Price discount to brand:     20–30% (still far above generic commodity)
Duration:                    180 days (typically ≈ 3 quarters of revenue)
Incremental margin:          70–85% gross margin during exclusivity

Value Calculation:
Para IV value ≈ US Market Size × 35% market share × 75% price × 3/4 year × 75% GM
→ $100M branded market → approx $15–20M incremental contribution to Indian pharma

Check:
□ Company's Para IV pipeline: total number, value of target markets
□ Any court settlements (which often give the filer a delayed exclusivity date)
□ At-risk launch: company launched before patent case resolved — litigation risk
□ Authorised generic: innovator may launch own generic on first day → halves filer's share

Para IV Value at Risk:
→ Invalidation of patent: filer loses exclusivity entirely
→ Multiple Para IV filers: 180-day exclusivity shared (reduces value)
→ Innovator settlement: often converts Para IV to licensed generic (monetised, lower risk)
```

## Analysis Module 5C — Biosimilar Analysis Framework

```
Biosimilar Development Stage Assessment:
Stage              | Time      | Investment | Risk
───────────────────────────────────────────────────────────
Reference Selection| Year 0    | Low        | Low  
Development        | Yr 1–3   | Medium     | Medium
Clinical Studies   | Yr 3–5   | HIGH       | Medium-High
Regulatory Filing  | Yr 5–6   | Medium     | Low (if data clean)
Approval & Launch  | Yr 6–7   | High       | Low

Key Biosimilar Markets:
□ US: FDA 351(k) pathway — interchangeability designation = formulary advantage
□ Europe: EMA biosimilar = simpler extrapolation accepted; strong Biocon track record
□ Emerging markets: Easier approval but lower pricing

Indian Biosimilar Leaders:
→ Biocon: Most advanced; partnerships with Viatris for global markets
→ Dr Reddy's: Rituximab, Pegfilgrastim in EU
→ Cipla / Sun Pharma: Early stage biosimilar pipelines

Reference Biologic Market Sizes (patent expiry opportunity):
→ Adalimumab (Humira): $21B annual sales — massive biosimilar market
→ Bevacizumab (Avastin): $8B — Biocon has product
→ Trastuzumab (Herceptin): $7B — multiple Indian biosimilars
→ Insulin glargine: significant emerging market opportunity

Biosimilar Margin Profile:
→ US biosimilar launch: 30–45% gross margin (vs. 60–70% for novel drug)
→ Partner royalty structure reduces net margin
→ Volume is the game: high volume at 30–40% GM = substantial earnings
```

## Analysis Module 6 — Financial Quality — Pharma Specific

### Step 6.1 — Revenue Quality
```
Geographic Diversity Score:
→ India + US + Emerging Markets + Europe = diversified (lower risk)
→ India only: domestic regulatory risk + NLEM
→ US only: USFDA compliance + price erosion

Revenue Concentration Risk:
□ US % of revenue: >50% = USFDA concentration risk
□ Single product >15% of revenue: patent cliff / competition risk
□ Single customer >20%: pricing vulnerability
□ Government tender dependency >20%: lumpy, low-margin
```

### Step 6.2 — Margin Analysis
```
EBITDA Margin Benchmarks:
→ CDMO/API (specialty): 25–40%
→ US specialty + domestic branded: 25–35%
→ Diversified Indian pharma (large): 20–28%
→ Pure US generics: 15–22%
→ API commodity: 10–18%

Gross Margin:
→ Branded generics (India): 65–75%
→ US generics: 55–65%
→ API: 40–55%
→ CDMO: 50–65%

Margin Risk:
→ Raw material (RM) cost as % of revenue: rising RM = margin pressure
→ API backward integration: reduces RM dependency (competitive advantage)
→ China API imports: reliance on China for intermediates = supply chain risk
```

### Step 6.3 — Cash Flow and Capital Allocation
```
□ OCF/PAT ratio: >70% = quality earnings (verify vs. forensic accounting skill)
□ R&D intensity vs. FCF: can the company fund R&D from cash flows?
□ CapEx for capacity: new facility = growth CapEx (monitor returns)
□ Working capital: pharma typically has long inventory cycles (60–90 days)
□ Debtor days for domestic: government hospitals can be 120–180+ days
□ Acquisition track record: value-accretive or value-destructive M&A?
```

---

## Red Flag Summary — Pharma

### CRITICAL Flags
```
❗ USFDA Warning Letter on key US-facing facility
❗ Import Alert (shipment ban) from USFDA
❗ Drug recall (Class I) from CDSCO or USFDA
❗ Application Integrity Policy / Data Integrity Issue
❗ Consent Decree imposed
❗ Core product patent invalidated or successful ANDA challenge by competitor
❗ Clinical trial failure for pipeline product representing >15% of implied value
```

### HIGH Flags
```
⚠️ Multiple OAI observations across 2+ facilities
⚠️ US revenue declining >15% YoY without clear price erosion explanation
⚠️ No new ANDA approvals for 3+ quarters
⚠️ R&D spend declining while business is growing (cutting investment in future)
⚠️ Single product >20% of US revenue facing Para IV challenge
⚠️ Domestic market share loss in key therapies for 2+ years
⚠️ Gross margins falling >300bps due to API cost inflation
⚠️ MR attrition >25% annually (field force instability)
```

---

## Pharma Valuation Framework

```
Primary Method: EV/EBITDA
  → Specialty/CDMO: 25–35x
  → Diversified quality pharma: 18–25x
  → Generic-heavy: 12–18x
  → API commodity: 10–14x
  → Stressed/compliance issues: 6–10x

P/E Method:
  → Use normalised earnings (adjust for one-time R&D, legal settlements)
  → Specialty: 35–45x | Diversified: 20–28x | Generics: 15–20x

Pipeline Valuation (risk-adjusted NPV):
  → Para IV FTF: (Market size × Market share × Margin × Duration) / WACC
    Probability adjustment: 70–80% for ANDA filed
  → Specialty NDA: Phase 3 success rate × (NPV of product)
  → Add rNPV of pipeline to base business EV

PEG Ratio:
  → Pharma that is growing earnings: PEG < 1.2 = reasonable
  → PEG > 2: Growth priced in fully
```

---

## Pharma Analysis Output Format

```
PHARMA SECTOR ANALYSIS
Company: [Name] | Segment: [India Branded/US Generics/API/CDMO/Specialty]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

REGULATORY STATUS:
  USFDA Compliance:    [CLEAN (VAI) / CONCERN (OAI) / CRITICAL (Warning Letter)]
  Facilities:          [List of key facilities + last inspection + status]
  ANDA Pipeline:       [Total filed | Approved | Pending | FTF count]
  Other Regulators:    [CDSCO / EMA / WHO-GMP status]

BUSINESS MIX:
  India:               [%] of revenue | IQVIA growth vs. IPM growth
  US:                  [%] of revenue | Price erosion + new launches net
  Emerging Markets:    [%] of revenue
  API/CDMO:            [%] of revenue

R&D:
  R&D as % Revenue:   [%] | Capitalisation rate: [%]
  Pipeline Highlights: [Top 3 pipeline assets with status]
  Biosimilar Pipeline: [List or N/A]

FINANCIALS:
  Revenue Growth:      [%] | EBITDA Margin: [%]
  OCF/PAT:             [%]
  Net Debt/EBITDA:     [X]x

CRITICAL FLAGS:        [Count + list]
HIGH FLAGS:            [Count + list]

VALUATION:
  EV/EBITDA:          [X]x → Sector benchmark: [X]x
  P/E (Normalised):   [X]x
  Pipeline rNPV:       ₹[X] per share
  Verdict:             [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Investment Case:    [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:           [Regulatory/Pipeline/Competition/Pricing]
  Key Catalyst:       [ANDA approval/Launch/Compliance resolution]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Pharma Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 25. Skill 21 — Defence & Aerospace Sector Analyzer

**Merged from standalone file `AI_Defence_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Defence, Aerospace, Space, Strategic Electronics

---

## CRITICAL AI INSTRUCTION

Defence is unlike any other sector. Revenue is lumpy (large order execution), growth is government-policy-dependent, and competitive moat is often regulatory (not market-driven). **Order Book is the single most important leading indicator.** Indigenisation policy, DRDO partnerships, and DPP (Defence Procurement Policy) changes are non-financial catalysts that have outsized impact. Never value defence companies purely on historical earnings — always project from order book.

---

## Purpose

Analyse Indian defence and aerospace companies through the lens of order book visibility, indigenisation opportunity, government policy tailwinds, execution capability, and technology positioning. Identify companies best placed to benefit from India's ₹6+ lakh crore annual defence budget and the Make in India Defence policy.

---

## Pre-Flight Requirements

```
□ Annual Report + last 8 quarters of investor presentations
□ Order Book disclosure (segment-wise if available)
□ L1 (lowest bidder) status disclosures for recent tenders
□ DRDO collaboration and technology transfer agreements
□ iDEX (Innovation for Defence Excellence) participation
□ Defence Ministry approvals: DAP (Defence Acquisition Procedure)
□ DPP/DAP policy changes affecting the company's product categories
□ JV and foreign partnership agreements
□ Export authorisation and current exports
□ DPSU (Defence PSU) vs. Private comparison in same segment
```

---

## Analysis Module 1 — Business Model Classification

### Step 1.1 — Defence Sub-Segment
```
DEFENCE PSUs (Public Sector Undertakings):
  HAL (Hindustan Aeronautics): Aircraft, helicopters, engines
  BEL (Bharat Electronics): Electronic warfare, radar, communications
  BEML: Mining/defence vehicles, metro coaches
  BDL (Bharat Dynamics): Missiles, torpedoes
  Ordnance Factory Board (OFBIL listed entities)
  
PRIVATE SECTOR DEFENCE:
  L&T Defence: Artillery, shipbuilding, armoured vehicles
  Bharat Forge: Artillery, defence forgings
  Tata Advanced Systems: Aerospace structures, UAVs
  Data Patterns: Electronics, avionics
  MTAR Technologies: Precision components (space + defence)
  Paras Defence: Optics, defence electronics
  DCX Systems: Cable harnesses, kits for Boeing/Airbus

SPACE TECH:
  ISRO-linked: Antrix, IN-SPACe ecosystem
  Private: Agnikul, Skyroot, Dhruva Space (unlisted)
  Listed plays: MTAR (ISRO components), Centum Electronics

SHIPBUILDING:
  Cochin Shipyard, Mazagon Dock, GRSE, Garden Reach

AMMUNITION / EXPLOSIVES:
  Solar Industries, Premier Explosives, Astra Microwave
```

### Step 1.2 — Moat Assessment for Defence Companies
```
Moat Types in Defence:
1. Regulatory Moat: Only approved vendor for specific category (BEL, HAL)
2. Technology Moat: Proprietary capability (Data Patterns, Paras Defence)
3. Relationship Moat: Long-term customer relationship with MoD / DRDO
4. Cost Moat: Lowest cost producer for standard components
5. IP Moat: Patent-protected defence product

Strongest Moat Combination: Regulatory + Technology + Long-term relationship
→ These companies command highest valuations and most stable order books
```

---

## Analysis Module 2 — Order Book Analysis (MOST CRITICAL)

### Step 2.1 — Order Book Fundamentals
```
Total Order Book = Unexecuted portion of all secured orders

Order Book to Revenue Ratio (OB/TTM Revenue):
→ >4x: Excellent visibility (4+ years of current revenue secured)
→ 3–4x: Good visibility
→ 2–3x: Adequate
→ <2x: Thin pipeline — growth dependent on fresh orders

Order Book Quality:
□ Domestic orders vs. export orders (domestic = more certain, export = lumpy)
□ Government orders (MoD, MHA, DRDO) vs. commercial: government = reliable payer
□ Product vs. maintenance/service orders: product = lumpy, service = recurring
□ Fixed-price vs. cost-plus contracts (fixed-price = margin risk if costs rise)
□ Large single orders (concentration risk) vs. diversified small orders
```

### Step 2.2 — Order Inflow Analysis
```
Fresh Order Inflows (quarterly):
→ Compare vs. revenue: Inflow > Revenue = Order Book growing (positive)
→ Inflow < Revenue = Order Book depleting (negative — pipeline concern)
→ Order inflow CAGR: 3-year trend

L1 Status (Lowest Bidder):
→ L1 = awarded the contract (pending final signing)
→ L1 in pipeline: future order book addition
→ Companies that disclose L1 status provide better forward visibility

Order Pipeline (Tender Participation):
→ Tenders participated (total value)
→ Success rate: orders won / tenders bid
→ Conversion timeline: L1 to formal order (can be 6–18 months for MoD)
```

### Step 2.3 — Revenue from Order Book Execution
```
Order Execution Timeline:
→ Simple electronics/systems: 6–18 months delivery
→ Complex platforms (ships, aircraft): 3–10 years
→ Missiles / advanced systems: 2–5 years

Execution Risk Assessment:
□ Are milestone payments being received on schedule?
□ Any orders cancelled or stalled (government budget cuts)?
□ DRDO delays (technology development behind schedule)?
□ Supply chain constraints (imported components, single-source parts)?
□ Manpower and manufacturing capacity sufficient for order book?

Revenue Recognition Method:
→ Percentage-of-completion (most defence companies)
→ Milestone-based (some contracts)
→ Ensure revenue recognition is conservative and backed by milestones
```

---

## Analysis Module 3 — Indigenisation and Policy Tailwinds

### Step 3.1 — Indigenisation Content Assessment
```
iDEX and DAP Positive Impact:
→ DAP 2020 mandates minimum Indian Content (IC) in all defence procurement
→ IC requirements: 50–65% for most categories (rising over time)
→ Companies with high IC capability = preferred vendors

Category Assessment:
□ What categories does this company operate in?
□ What is the minimum IC requirement in each category?
□ Can the company meet the IC requirement without foreign dependency?
□ Has the company obtained any indigenisation certificates from DRDO?

Indigenisation Opportunity Matrix:
→ Category notified for import ban (Positive List) = captive domestic market
→ Current imports being substituted = medium-term revenue opportunity
→ New technology indigenisation = long gestation but large eventual market
```

### Step 3.2 — Government Policy Assessment
```
Key Policy Levers:
□ DAP (Defence Acquisition Procedure): governs procurement; amendments impact companies
□ FDI in Defence: 74% auto route, 100% government route (impacts JV structure)
□ OFB Corporatisation: legacy ordnance factories converting to companies
□ Defence Industrial Corridors: UP and Tamil Nadu corridors — land + infrastructure
□ DRDO R&D Budget: rising allocation = more DRDO-to-industry technology transfer
□ Defence Export Target: India targeting $5B+ exports by 2025 — opportunities for exporters

Budget Analysis:
→ MoD Capital Budget (procurement) vs. Revenue Budget (operations)
→ Capital budget utilisation rate: low utilisation = execution pressure on companies
→ Committed liabilities (LC contracts): these are essentially secured orders

Export Policy:
→ END-USE certificate requirements for defence exports
→ Export clearance: DGFT + MoD clearance required
→ Strategic partnership model: Indian company + global OEM + MoD
```

---

## Analysis Module 4 — Financial Quality — Defence Specific

### Step 4.1 — Revenue and Margin Pattern
```
Revenue Lumpiness Assessment:
→ Defence revenue is naturally lumpy due to large order deliveries
→ Do not use single-quarter P&L to judge performance
→ Use trailing 12-month (TTM) or annual comparison

EBITDA Margin by Segment:
→ Defence Electronics (BEL, Data Patterns): 20–30%
→ Shipbuilding (Cochin, Mazagon): 10–18%
→ Aerospace components (HAL, MTAR): 15–25%
→ Defence PSUs (broad-based): 15–22%
→ Private precision components: 18–28%
→ Ammunition: 15–22%

Working Capital — Defence Specific:
□ Government advance payments: positive for working capital
□ Milestone billing: revenue recognition may lag cash receipt
□ DRDO development delays: can freeze working capital
□ Unbilled revenue: check if large and growing (execution delays)
□ Retention money: customer withholds 5–10% until project completion
```

### Step 4.2 — R&D and Technology Investment
```
R&D Spend in Defence:
→ Self-funded R&D: indicative of technology ambition
→ DRDO co-development cost sharing: reduces own R&D cost
→ iDEX grants: government funding for defence innovation

Technology Tier Assessment:
Tier 1: System integrator (HAL, L&T, TATA) — highest complexity, highest margin
Tier 2: Subsystem manufacturer (Data Patterns, BEL) — specialized, strong IP
Tier 3: Component/parts manufacturer (MTAR, Paras) — precision required
Tier 4: Raw material / general fabrication — commodity, lowest margin

Moving up the tier = margin expansion thesis
```

### Step 4.3 — Capital Allocation
```
CapEx Analysis:
□ Capacity expansion: new lines for priority product categories
□ Technology investments: ERP, testing equipment, clean rooms (avionics)
□ Land and facilities: Defence Industrial Corridor investments

Return on Capital Employed:
→ Defence has long gestation (order to revenue can be 2–5 years)
→ ROCE may look low during build phase; normalise for order book cycle
→ Steady state ROCE for quality defence companies: 18–28%

Cash Conversion:
→ Government as customer: pays reliably but sometimes slowly
→ Working capital cycle can be 6–18 months for complex systems
→ FCF may be negative during capacity/technology build phase — evaluate strategy vs. execution
```

---

## Analysis Module 4A — Offset Policy and Export Ecosystem

```
Defence Offset Policy (DAP 2020):
→ Foreign vendors with contracts >₹2,000 Cr must invest 30% of contract value
  in Indian defence R&D, manufacturing, or services (as offset)
→ Offset Banking: companies can earn Offset Credits (OCs) from Indian vendors
  and bank them for future use

Impact on Indian Companies:
□ Is this company a registered Offset Discharge Agent (ODA)?
□ OC earnings: revenue from manufacturing components for foreign vendors
□ Technology transfer via offset: has company received any foreign technology?
□ Offset obligation fulfillment by client: reduces company's execution risk
→ Companies that are ODA partners of Lockheed, Boeing, Thales: strong international validation

Defence Exports:
□ Current export revenue: ₹Cr
□ Key export products: (Artillery shells, Naval systems, software, components?)
□ Approved export destinations: MoD clearance required per country
□ DTTI (Defence Technology and Trade Initiative) India-US: bilateral framework
   Companies benefiting: L&T, Tata, Mahindra Defence, Bharat Forge
□ Israel, France, Russia partnerships: technology co-development opportunities
□ India's defence export target: ₹35,000 Cr by FY2025 → Track achievement

iDEX (Innovation for Defence Excellence) Participation:
□ Number of DISC (Defence India Startup Challenge) grants received
□ Grant amount: up to ₹1.5 Cr per challenge (seed for prototype)
□ DISC to production pipeline: prototype → user trial → production order
→ iDEX graduates with production orders = emerging defence tech companies worth watching
```

## Analysis Module 4B — DRDO Technology Readiness Level (TRL) System

```
TRL Scale for Defence Technology Evaluation:
TRL 1–3: Basic research → Lab demonstration (very early, high risk)
TRL 4–5: Component validation → System prototype in laboratory
TRL 6:   Prototype demonstration in relevant environment → DRDO milestone
TRL 7:   System prototype in operational environment → User trials
TRL 8:   System complete and qualified → Ready for production
TRL 9:   Actual system proven in operational environment → PRODUCTION

For Each DRDO-Partnered Product:
□ Current TRL level: where is this technology on the scale?
□ Expected time from current TRL to TRL 9: typically 2–5 years per stage
□ User trial status: MoD user trial cleared = near production stage
□ TOT (Transfer of Technology): DRDO licensed technology to company?
   → ToT is highest validation: DRDO's IP, company's manufacturing
□ DRDO co-development cost share: % borne by company vs. DRDO grant

Success Rate Benchmark:
→ DRDO self-stated 30-40% of projects reach TRL 9
→ Simple electronics/communications: higher success
→ Complex propulsion/weapons systems: lower, longer cycle
→ Assess portfolio probability-weighted revenue from DRDO pipeline
```

## Analysis Module 4C — Private vs. PSU Performance Comparison

```
Systematic comparison when evaluating private defence company vs. DPSU:

METRIC              | PRIVATE (L&T/Tata/Bharat Forge) | DPSU (HAL/BEL/BHEL)
─────────────────────────────────────────────────────────────────────────────
Order Book Growth   | Market-driven, competitive      | Often captive allocation
Execution Speed     | Typically faster                | Bureaucratic delays
EBITDA Margin       | 10–20%                          | 15–25% (cost-plus structure)
R&D Investment      | Self-funded, aggressive         | Mixed (DRDO funded mostly)
Technology Source   | JV + own development            | DRDO transfer + JV
Export Capability   | Building rapidly                | HAL: growing; BEL: some
Capital Return      | Higher ROE target               | Dividend to government
Governance          | Corporate; SEBI oversight       | Government; lower accountability
Valuation           | Higher (growth premium)         | Lower (structural discount)

Key Insight: Private players benefit from CPSE's inability to serve all demand
             They are NOT replacing DPSUs — they are GROWING the pie.
             Best thesis: Both private + certain DPSUs can coexist and grow.
```

## Analysis Module 5 — Management and Execution Quality

### Step 5.1 — Management Track Record
```
Order Book to Revenue Conversion:
→ What % of the order book from 3 years ago has been executed?
→ Revenue / (Opening Order Book 3 years ago): >75% = strong executor

Guidance Delivery:
→ Did management deliver on revenue and margin guidance?
→ Order inflow guidance: achieved or missed?
→ Project commissioning: any delays in complex projects?

DRDO Relationships:
□ Has the company successfully completed DRDO co-development programs?
□ Has DRDO certified the company's products?
□ Any technology transfer received from DRDO?

Partnership Quality:
□ Global OEM partnerships (Boeing, Airbus, Lockheed, Thales, Rafael)
□ JV structure: equity split, technology sharing terms
□ Offset obligations fulfilled by foreign OEMs through this company?
```

### Step 5.2 — Competitive Positioning
```
Approved Vendor List (AVL) Status:
→ MoD approved vendor for specific product categories = Regulatory moat
→ Single-source vs. multi-source approval

Peer Comparison:
□ Order book vs. peers (same category)
□ EBITDA margin vs. peers
□ Order inflow market share in tendered opportunities
□ Technology capability rating (DRDO assessment)
□ Export track record vs. peers
```

---

## Red Flag Summary — Defence

### CRITICAL Flags
```
❗ Order cancellation by MoD (policy reversal or quality failure)
❗ DRDO technology development failure affecting company's primary order
❗ Corruption/vigilance case against company management (MoD blacklisting)
❗ Loss of "Qualified Vendor" status for core category
❗ Foreign JV partner withdrawing (technology + contract risk)
❗ Major project cost overrun requiring government renegotiation
❗ Revenue from order book declining despite large order book (execution failure)
```

### HIGH Flags
```
⚠️ Order inflows declining for 2+ consecutive years
⚠️ Order Book / Revenue below 2x
⚠️ Unbilled revenue growing >50% YoY without new project explanation
⚠️ DRDO program delays pushing revenue recognition by 2+ years
⚠️ High government receivables (>180 days) with no collection update
⚠️ EBITDA margins compressing despite growing revenue
⚠️ Single customer (MoD arm) >80% of revenue without diversification plan
⚠️ JV partner changing or foreign OEM shifting India partner
```

---

## Defence Valuation Framework

```
Primary Method: EV/EBITDA with Order Book Visibility Premium
  → Strong OB (>4x), DRDO-certified: 35–50x EBITDA
  → Good OB (3–4x), quality franchise: 25–35x EBITDA
  → Average OB (2–3x), execution concerns: 15–25x EBITDA

P/E Method:
  → HAL, BEL equivalent quality: 35–50x earnings
  → Mid-tier private players: 25–40x
  → Component manufacturers: 20–30x
  → WARNING: High P/E for defence = market pricing in order book execution
              If execution fails, de-rating is severe and rapid

DCF with Order Book:
  → Revenue from committed order book is near-certain (>85%)
  → Apply lower WACC for PSU defence (government backing)
  → Apply sector-specific terminal growth (India defence budget CAGR)

Order Book-Based Valuation:
  → Enterprise Value / Order Book Ratio
  → Premium franchise (BEL, HAL): 0.8–1.2x Order Book
  → Good private player: 0.5–0.8x Order Book
  → This method gives reality check on market expectation
```

---

## Defence Analysis Output Format

```
DEFENCE SECTOR ANALYSIS
Company: [Name] | Segment: [Electronics/Aerospace/Shipbuilding/Ammunition/Space]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

ORDER BOOK:
  Total Order Book:     ₹[X]Cr
  OB/Revenue Ratio:     [X]x → [Excellent/Good/Adequate/Thin]
  L1 Status (Pipeline): ₹[X]Cr
  Order Inflow (TTM):   ₹[X]Cr | vs. Revenue: [Book Burning/Growing]

INDIGENISATION POSITION:
  Key Categories:       [List of approved categories]
  Import Substitution:  [Active opportunities being pursued]
  iDEX/DRDO Programs:  [Active co-development programs]
  Export Status:        ₹[X]Cr exports | [Countries/programs]

FINANCIAL QUALITY:
  Revenue Growth:       [%] YoY (Note: lumpiness)
  EBITDA Margin:        [%] → [vs. segment benchmark]
  Working Capital Days: [X] days → [vs. prior year]
  Unbilled Revenue:     ₹[X]Cr → [Growing/Stable/Concern]
  ROCE:                 [%]

TECHNOLOGY TIER:        [Tier 1/2/3/4 — System Integrator/Subsystem/Component]
JV/PARTNERSHIP:         [Key global partners + program name]

CRITICAL FLAGS:         [Count + list]
HIGH FLAGS:             [Count + list]

VALUATION:
  EV/EBITDA:           [X]x → Benchmark: [X]x
  P/E:                 [X]x
  EV/Order Book:       [X]x → Benchmark: [X]x
  Verdict:             [Attractive/Fair/Expensive]

POLICY TAILWINDS:       [Top 2 policy catalysts for this company]

OVERALL VERDICT:
  Investment Case:     [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:            [Order/Execution/Policy/Competition]
  Key Catalyst:        [Next significant order/delivery milestone]
  Monitoring Points:   [Order inflow, OB/Revenue, key DRDO milestone]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Defence Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 26. Skill 22 — Manufacturing & Capital Goods Sector Analyzer

**Merged from standalone file `AI_Manufacturing_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Industrial Manufacturing, Capital Goods, Auto Ancillaries, Consumer Durables, Engineering

---

## CRITICAL AI INSTRUCTION

Manufacturing analysis requires understanding of both the **demand cycle** (what drives order inflows) and the **supply cycle** (capacity utilisation, cost structure, working capital). Manufacturing businesses are fundamentally volume × margin businesses. Price-volume-mix decomposition of every revenue line is mandatory. Never accept "strong growth" without decomposing it. **Capacity utilisation is the single best leading indicator of margin and earnings direction.**

---

## Purpose

Analyse Indian manufacturing companies across capital goods, auto and auto ancillaries, consumer durables, industrial products, and engineering sectors. Assess competitive positioning, capacity cycle, cost structure, working capital efficiency, and capex returns.

---

## Pre-Flight Requirements

```
□ Annual Report (last 3 years) + 8 quarters of results
□ Product-wise revenue breakdown
□ Capacity utilisation data (if disclosed — management commentary)
□ CapEx plan: maintenance vs. expansion breakdown
□ Raw material cost breakdown (RM% of revenue trend)
□ Order book / backlog (for capital goods / project-based)
□ Customer concentration data
□ Competition and market share data (if publicly available)
□ PLI (Production Linked Incentive) scheme participation details
□ Export revenue proportion and key geographies
□ Concall transcripts (last 4 quarters)
```

---

## Analysis Module 1 — Business Classification

### Step 1.1 — Manufacturing Sub-Segment
```
CAPITAL GOODS / HEAVY ENGINEERING:
  Companies: L&T, ABB India, Siemens, Thermax, BHEL, Cummins India
  Revenue driver: Project orders, capex cycle in end-industries
  Key metric: Order book, execution rate, EBITDA/order
  Cycle: 3–7 year capex cycles in power, infrastructure, metals

AUTO ANCILLARIES:
  Companies: Motherson, Bosch, Minda, Sona BLW, Fiem, Endurance
  Revenue driver: Vehicle production volumes of OEMs
  Key metric: Content per vehicle, OEM wallet share, EV readiness
  Risk: OEM concentration, EV transition (some products at risk)

CONSUMER DURABLES / HOME APPLIANCES:
  Companies: Havells, Voltas, Blue Star, Whirlpool, Dixon, Amber
  Revenue driver: Household income growth, premiumisation, cooling demand
  Key metric: Market share per product category, distribution reach
  Seasonality: AC/cooling = Q4/Q1 heavy

INDUSTRIAL PRODUCTS / SPECIALTY:
  Companies: Cera, Kajaria, Astral Poly, Prince Pipes, Supreme Industries
  Revenue driver: Real estate activity, renovation spending, infra
  Key metric: Volume growth + realisation per unit

ENGINEERING EXPORTS:
  Companies: Precision castparts, Greaves, Bharat Forge
  Revenue driver: Global industrial production, oil & gas capex
  Key metric: Order mix between domestic and export, currency impact

PLI BENEFICIARIES (Across Manufacturing):
  Check: Is the company registered? Incentive eligibility? Revenue threshold for PLI?
```

---

## Analysis Module 2 — Volume and Capacity Analysis

### Step 2.1 — Price-Volume-Mix Decomposition
```
Revenue Growth Decomposition:
  Revenue Growth = Volume Growth + Realisation (Price) Change + Product Mix Shift

For EACH major product line:
□ Volume sold (units, tonnes, meters) — YoY change
□ Average realisation per unit — YoY change
□ Mix shift: higher-value products gaining share?

Assessment:
→ Volume growth + stable/rising realisation = QUALITY growth
→ Price growth only (volumes flat) = pricing power OR demand stagnation
→ Volume growth + falling realisation = commodity pressure, competition
→ Revenue growth from mix-up = sustainable quality improvement
```

### Step 2.2 — Capacity Utilisation
```
Utilisation Rate = Actual Production / Installed Capacity × 100%

Threshold Analysis:
→ <60% utilisation: High fixed cost dilution, low margins, need volume growth
→ 60–75% utilisation: Normal operating range, margins building
→ 75–85% utilisation: Efficient, margins healthy, capacity expansion being planned
→ >85% utilisation: Near full capacity = imminent capacity addition needed OR 
                     lost orders/growth cap

Capacity Expansion Decision:
□ At what utilisation does management plan capacity expansion? (Usually 75–80%)
□ Lead time for capacity addition: 12–24 months for most manufacturing
□ Announced capacity: when will it be commissioned?
□ CWIP (Capital Work in Progress): evidence of under-construction capacity
□ Cost of new capacity: ₹/tonne or ₹/unit — return on capital assessment

Operating Leverage Calculation:
→ How much do margins expand for every 10% increase in volume?
→ High fixed cost businesses: 3–4x operating leverage (margin moves 30–40% of revenue move)
→ Low fixed cost (outsourced): minimal operating leverage
```

---

## Analysis Module 3 — Cost Structure Analysis

### Step 3.1 — Raw Material Analysis
```
RM Cost as % of Revenue:
→ Highly RM-intensive: Metals, plastics, chemicals (RM = 60–75% of revenue)
→ Moderate RM: Auto parts, consumer goods (RM = 40–60%)
→ Low RM / high value-add: Electronics, specialty engineering (RM = 20–40%)

Key Raw Materials to Track (company-specific):
□ Identify top 3 raw materials by cost
□ Price trend in those commodities (globally and domestically)
□ Company's ability to pass through cost: immediate (commodity) vs. lagged (long-term contracts)
□ Inventory strategy: just-in-time vs. strategic stockholding
□ Hedging policy: forward contracts for key RM inputs?

Gross Margin Sensitivity:
→ 10% rise in RM price × RM as % of revenue = gross margin impact
→ Example: RM = 60% of revenue, 10% RM rise = 600bps gross margin fall
→ Can pricing offset this? Check historical instances.

China Exposure:
□ What % of RM is sourced from China?
□ Supply chain diversification underway (China+1 beneficiary or still dependent)?
□ PLI incentive to reduce China dependency in this category?
```

### Step 3.2 — Employee and Other Cost Analysis
```
Employee Cost Efficiency:
□ Revenue per employee: rising (productivity improving) or falling?
□ Employee cost as % of revenue: benchmark vs. automation level
□ Headcount: growing faster than revenue = efficiency concern

Other Manufacturing Overheads:
□ Power and fuel as % of revenue: energy-intensive sectors (cement, glass, metals)
   → Rising power cost without tariff pass-through = margin risk
   → Captive power plant: protects against grid tariff hikes
□ Freight and logistics: distance from customers/suppliers
   → Port proximity advantage for export-heavy companies
```

---

## Analysis Module 4 — Working Capital Analysis

### Step 4.1 — Working Capital Efficiency
```
Key Working Capital Days:
→ Debtor Days (DSO): Trade receivables / Revenue × 365
   Benchmark: 30–45 days (B2C or standard B2B) | 60–90 days (Government) | 90–120 days (export)
   Rising DSO = collection stress or channel stuffing

→ Inventory Days (DIO): Inventory / COGS × 365
   Benchmark: 30–60 days (fast-moving consumer goods) | 60–90 days (industrial) | 90–120 days (capital goods)
   Rising DIO = demand slowdown or raw material stockpiling

→ Payable Days (DPO): Trade payables / COGS × 365
   Benchmark: 30–60 days for large companies | <30 days for small/MSME suppliers
   Falling DPO = losing bargaining power with suppliers

Cash Conversion Cycle = DSO + DIO − DPO
   → Shorter CCC = better working capital efficiency
   → Lengthening CCC = cash trapped, funding pressure
```

### Step 4.2 — Working Capital as % of Revenue
```
Net Working Capital / Revenue: (Trend over 5 years)
→ Declining NWC% = improving efficiency
→ Rising NWC% = more capital trapped, lower FCF quality

Stress Signals:
□ Receivables growing faster than revenue → channel stuffing / billing but not collecting
□ Inventory rising during revenue slowdown → demand concern
□ Trade payables falling → supplier relationship under stress
□ Advance from customers falling → demand pipeline weakening
```

---

## Analysis Module 5 — CapEx and Return Analysis

### Step 5.1 — CapEx Classification
```
Maintenance CapEx:
→ Required to keep existing capacity running (replace worn equipment)
→ Approximate: = Depreciation charge (for a steady-state business)
→ FCF = OCF − Maintenance CapEx

Growth CapEx:
→ New capacity, new plant, new technology
→ Generates revenue only after commissioning
→ Period between spend and revenue = cash drain

Asset Turnover:
→ Revenue / Average Fixed Assets
→ Rising AT = same assets generating more revenue (positive)
→ Falling AT = new assets not yet productive OR demand falling

Return on Capital Employed (ROCE):
→ EBIT / (Equity + Debt − Cash)
→ Target: ROCE > WACC = value creation
→ Benchmark for quality Indian manufacturers: 18–25% normalised ROCE

Greenfield vs. Brownfield:
→ Brownfield expansion (existing site): faster, cheaper, lower risk
→ Greenfield (new site): higher CapEx, longer gestation, higher execution risk
→ Management preference for brownfield over greenfield = capital discipline
```

### Step 5.2 — PLI (Production Linked Incentive) Assessment
```
If company is a PLI beneficiary:
□ Which PLI scheme? (Electronics, Auto, Pharma, Specialty Chemicals, Textiles, Food Processing)
□ Incremental production threshold to qualify
□ Incentive rate (% of incremental sales)
□ Period of incentive (typically 5–7 years)
□ Capex required to reach PLI thresholds
□ Probability of meeting thresholds: management track record assessment
□ PLI income as % of EBITDA: how dependent?

PLI valuation note: PLI incentives are real cash income but are time-limited.
  Do not capitalise PLI income at full multiple — separate base business from PLI.
```

---

## Analysis Module 5A — EV Transition Impact Framework (Auto Ancillaries)

THIS IS THE MOST CRITICAL STRUCTURAL RISK IN MANUFACTURING. Applies whenever company has auto exposure.

```
Step 1 — Product Classification: EV-Safe vs. EV-At-Risk

EV-SAFE Products (survive ICE→EV transition):
✅ Wheels, tyres, brake systems
✅ HVAC systems (EVs need thermal management)
✅ Seating, interiors, glass
✅ Electrical harnesses (EVs have MORE wiring, not less)
✅ Sensors, cameras (ADAS systems grow with EV)
✅ Structural components (body, chassis)
✅ Battery thermal management components (new opportunity)
✅ Rubber seals, gaskets (EVs still need these)

EV-AT-RISK Products (reduced demand in EV):
⚠️ Internal combustion engine (ICE) components — block, piston, crankshaft
⚠️ Exhaust systems, catalytic converters, mufflers
⚠️ Fuel injection systems, carburettors
⚠️ Transmission parts (EVs have simpler/single-speed)
⚠️ Radiators (ICE specific)
⚠️ Alternators (replaced by motor-generator units)
⚠️ Clutch plates, gear-box components

Step 2 — Revenue at Risk Calculation:
□ What % of revenue comes from EV-at-risk products?
□ Of that at-risk revenue, what is the EV penetration timeline?
   India EV 2-wheeler penetration FY2025: ~5% | Target FY2030: 30–40%
   India EV 4-wheeler penetration FY2025: ~2% | Target FY2030: 8–12%
□ Revenue at risk = At-risk product revenue × EV penetration forecast

Step 3 — EV Opportunity Assessment:
□ Has company developed EV-specific products? (Motor components, BMS parts)
□ Is company an approved supplier to Ola Electric, Tata EV, MG, BYD India?
□ R&D investment in EV components: specific disclosure?
□ New customer acquisition from EV OEMs
□ Content per EV vehicle vs. ICE vehicle: often HIGHER for electrical components

Step 4 — Timeline Risk Management:
□ EV transition is GRADUAL — 5–10 year window (not cliff-edge)
□ ICE volumes will grow in absolute terms until ~FY2028 even with EV share rising
□ Companies with 3–5 years of ICE revenue + active EV product pivot = MANAGEABLE
□ Companies with NO EV products AND high ICE-specific revenue exposure (>50%) 
  in 2025 = LONG-TERM STRUCTURAL SHORT

EV Transition Scorecard:
AT-RISK revenue %:     [X%]
EV product revenues:   [₹Cr or zero]
EV customer approvals: [Yes/No/In progress]
EV R&D spend:          [₹Cr]
Timeline judgment:     [Safe >3yr | Moderate risk 2-3yr | High risk <2yr]
```

## Analysis Module 5B — Energy Cost and ESG Compliance for Manufacturers

```
Energy Cost Analysis:
□ Power and fuel as % of net revenues: (from P&L cost breakdown)
   → Energy-intensive: Cement, glass, steel, electrochemicals: 15–25%
   → Moderate: Auto ancillaries, general manufacturing: 5–10%
   → Low: Assembly, labour-intensive: 2–5%
□ Captive power: % of total power from own generation
   → Higher captive = protected from grid tariff hikes
□ Renewable energy sourcing: % of power from solar/wind
   → Rising RE % = both cost reduction AND ESG improvement
□ Energy efficiency: revenue/unit of energy consumed (trend)

Green Manufacturing Requirements:
□ BIS, ISO 14001 (Environment), ISO 50001 (Energy) certifications
□ Carbon footprint disclosure: requested by global auto OEMs now
   → No carbon data = cannot be supplier to European OEMs after 2025
□ Water recycling: zero liquid discharge for chemical-adjacent plants
□ Supplier ESG audit: large auto OEMs conducting supply chain carbon audits
   → Non-compliant supplier = at risk of de-listing from approved vendor list

ESOP for manufacturing companies:
□ ESOPs granted as % of total shares: >5% = meaningful dilution
□ ESOPs granted to production workforce (unusual) vs. management (standard)
```

## Analysis Module 6 — Competitive Positioning

### Step 6.1 — Market Share Analysis
```
Domestic Market Share:
□ Company's revenue / Total industry revenue
□ Trend: gaining or losing market share?
□ Market share in premium vs. standard segment
□ Distribution reach: dealer network size, geographic coverage

Export Position:
□ Export as % of revenue
□ Key geographies and end-markets
□ Is the company a Tier 1 or Tier 2 supplier to global OEMs?
□ Currency risk management (hedge vs. natural hedge)

Competitive Advantage Checklist:
□ Technology differentiation: proprietary process or product?
□ Brand premium: higher realisation vs. competitors?
□ Cost advantage: cheaper location, backward integration, scale?
□ Distribution advantage: exclusive channel relationships?
□ Customer lock-in: certified supplier, high switching cost?
```

### Step 6.2 — Industry Structure
```
Consolidated vs. Fragmented Market:
→ Consolidated (2–4 players control >60%): pricing power, sustainable margins
→ Fragmented (many players, no leader >15%): price competition, margin pressure

Capital Intensity vs. Competition:
→ High capex requirement = natural barrier to new entrants
→ Low capex = easy competition from new and Chinese players

Import Competition:
□ Anti-dumping duties protecting this segment?
□ BIS certification requirements (protecting from substandard imports)?
□ PLI creating domestic supply where imports dominated?
□ Chinese competition: direct (same product) or indirect (customer switching)?
```

---

## Red Flag Summary — Manufacturing

### CRITICAL Flags
```
❗ Capacity utilisation falling below 50% for 2+ consecutive years
❗ CWIP stuck without commissioning for 3+ years
❗ Major customer (>20% of revenue) reducing or ending purchases
❗ Raw material cost rise >15% with no pricing power evidence
❗ Working capital blowing out: CCC >200 days for industrial company
❗ Debt rising sharply during revenue decline (distress borrowing)
❗ Management abandoning announced CapEx (capex discipline failure)
```

### HIGH Flags
```
⚠️ Volume growth negative for 2+ years in non-cyclical segment
⚠️ EBITDA margin compressing >300bps without RM explanation
⚠️ Inventory days rising >30 days from historical norm
⚠️ Large customer moving to competitor (market share loss signal)
⚠️ New Chinese entrant entering product category with 30%+ price discount
⚠️ Asset turnover declining for 3+ consecutive years
⚠️ PLI threshold achievement appearing unlikely from current trajectory
```

---

## Manufacturing Valuation Framework

```
Primary Method: EV/EBITDA
  Cyclical (at trough): 8–12x
  Cyclical (mid-cycle): 12–18x
  Industrial compounder (non-cyclical): 20–30x
  Consumer durables (branded): 25–35x
  Specialty engineering (high moat): 30–45x

P/E Method:
  → Normalise earnings for cycle position
  → Capital goods at peak cycle: never use peak EPS; use mid-cycle
  → Consumer durables compounders: 25–45x sustainable earnings

EV/Revenue: Less useful except for early-stage / high-growth manufacturers
  Quality industrial: 3–5x revenue
  Consumer brands: 4–8x revenue

Asset-Based (for asset-heavy, struggling companies):
  Fair value = Replacement cost of assets × Utilisation discount
```

---

## Manufacturing Analysis Output Format

```
MANUFACTURING SECTOR ANALYSIS
Company: [Name] | Segment: [Capital Goods/Auto Anc/Consumer Durables/Engineering]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

VOLUME AND CAPACITY:
  Capacity Utilisation:  [%] → [Operating Range Assessment]
  Volume Growth (YoY):   [%] | Realisation Change: [%]
  Revenue Mix Shift:     [Product/geography change noted]
  New Capacity:          [Under construction — ₹[X]Cr, commissioning [timeline]]

COST STRUCTURE:
  RM as % of Revenue:    [%] | Key RM: [Top 2-3 raw materials + trend]
  Gross Margin:          [%] → [vs. 5-yr avg: [%]]
  EBITDA Margin:         [%] → [vs. 5-yr avg + vs. peers]
  Operating Leverage:    [High/Medium/Low]

WORKING CAPITAL:
  Debtor Days:           [X] days → [vs. prior year: [X] days]
  Inventory Days:        [X] days → [vs. prior year: [X] days]
  CCC:                   [X] days → [Improving/Stable/Deteriorating]

CAPEX AND RETURNS:
  CapEx (TTM):           ₹[X]Cr | Growth CapEx / Maintenance: [split]
  ROCE:                  [%] → [vs. WACC [%]]
  Asset Turnover:        [X]x → [Rising/Stable/Falling]
  PLI Status:            [Participating/Not / Incentive earned: ₹[X]Cr]

COMPETITIVE POSITION:
  Market Share:          [%] → [Gaining/Stable/Losing]
  Export:                [%] of revenue
  Key Customers:         [Top customer concentration]

CRITICAL FLAGS:          [Count + list]
HIGH FLAGS:              [Count + list]

VALUATION:
  EV/EBITDA:            [X]x → [Trough/Mid/Peak cycle: [X]x / [X]x / [X]x]
  P/E (Normalised):     [X]x
  Verdict:              [Attractive/Fair/Expensive + cycle position note]

OVERALL VERDICT:
  Investment Case:      [Strong Buy/Buy/Hold/Reduce/Avoid]
  Cycle Position:       [Trough / Early Recovery / Mid-Cycle / Late Cycle / Peak]
  Key Risk:             [Biggest risk]
  Key Catalyst:         [Volume uptick / capacity commissioning / new order]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Manufacturing Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 27. Skill 23 — Power & Utilities Sector Analyzer

**Merged from standalone file `AI_Power_Utilities_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Power Generation, Transmission, Distribution, Renewables, Green Energy

---

## CRITICAL AI INSTRUCTION

Power and utilities operate in a **heavily regulated, government-influenced environment**. Returns are determined as much by regulatory orders (CERC/SERC tariff decisions) as by operational performance. Renewable energy companies are valued on capacity pipeline and PPA quality, NOT on traditional P&L metrics. Thermal power companies must be assessed on fuel security and tariff pass-through rights. **Never assess a power company without understanding its regulatory framework and PPA (Power Purchase Agreement) quality first.**

---

## Purpose

Analyse Indian power sector companies across thermal generation, renewable energy (solar, wind, hydro), transmission, distribution, and green hydrogen. Assess regulatory framework, asset quality, capacity pipeline, fuel security, PPA coverage, and financial sustainability.

---

## Pre-Flight Requirements

```
□ Annual Report (last 3 years)
□ PPA (Power Purchase Agreement) copies / summaries for major projects
□ CERC/SERC tariff orders (available on CERC website)
□ PLF (Plant Load Factor) data — monthly/quarterly
□ Fuel supply agreements (coal/gas linkage) for thermal
□ Regulatory filings and Annual Performance Review data
□ Renewable capacity: commissioned vs. under-construction vs. pipeline
□ Transmission / Distribution: AT&C loss data, DISCOM health
□ DISCOM payment track record (how reliable are their PPAs?)
□ Management concall transcripts (last 4 quarters)
□ Debt structure: project-level vs. corporate-level, refinancing schedule
```

---

## Analysis Module 1 — Business Model Classification

### Step 1.1 — Power Sector Sub-Segment
```
THERMAL POWER GENERATION:
  Companies: NTPC, Tata Power, Adani Power, Torrent Power, JSW Energy
  Revenue driver: PLF × Capacity × Tariff per unit
  Key risk: Fuel cost pass-through, coal availability, environment regulation
  Regulatory: CERC (central) / SERC (state) for tariff setting

RENEWABLE ENERGY GENERATION:
  Companies: Adani Green, Greenko, ReNew Power, NTPC Renewable, Torrent Power
  Revenue driver: CUF (Capacity Utilisation Factor) × Capacity × PPA rate
  Key risk: PPA quality (which DISCOM?), capacity addition timeline, financing cost
  Trend: Fastest growing; Government target 500GW by 2030

POWER TRANSMISSION:
  Companies: Power Grid Corp, IndiGrid (InvIT), KEC International (EPC)
  Revenue model: Regulated ROE on approved capital (PGCIL)
  Or: EPC contracts for transmission lines
  Key metric: Asset base growth, regulated ROE, stranded asset risk

POWER DISTRIBUTION (DISCOM):
  State DISCOMs: Generally loss-making (subsidy-dependent)
  Private DISCOMs: Tata Power Delhi, CESC, Torrent (Ahmedabad/Surat)
  Key metric: AT&C losses, tariff revision frequency, receivable days

POWER EQUIPMENT:
  Transformers, cables, switchgear: ABB, Siemens, Transformer companies
  Generator equipment: BHEL, Siemens, Toshiba JSW
  Covered under Manufacturing Skill + this sector module

GREEN HYDROGEN / STORAGE:
  Emerging: NTPC, Adani Green, Greenko (unlisted plays or EPC linked)
  Very early stage — value largely speculative; use pipeline + cost curve data
```

---

## Analysis Module 2 — Thermal Power Analysis

### Step 2.1 — Plant Load Factor (PLF)
```
PLF = Actual Units Generated / Maximum Possible Units × 100%

Benchmarks:
→ >85%: Excellent — demand > capacity (merchant power opportunity)
→ 75–85%: Good operating efficiency
→ 60–75%: Normal for PPA-tied plants (demand matches)
→ <60%: Concern — excess capacity, low demand, fuel issues

PLF Drivers:
□ Grid demand in region
□ Fuel availability (coal supply, gas availability)
□ Plant age and efficiency (newer plants run at higher PLF)
□ Merchant vs. PPA: merchant power PLF driven by market demand

PLF Sensitivity:
→ Every 5% PLF change ≈ 5–8% revenue change for fixed-tariff plants
→ Variable cost recovery linked to PLF in many tariff structures
```

### Step 2.2 — Fuel Security Assessment
```
For Thermal / Coal-Based Plants:
□ Coal linkage: Fuel Supply Agreement (FSA) with Coal India or MCL?
   → FSA ensures 75–85% of requirement at regulated price
   → E-auction / spot market coal: 15–25% at market price (volatile cost)
□ Pit-head vs. non-pit-head plant: distance from coal mines = freight cost
□ Coal stock days: inventory at plant vs. normative 30 days
□ Imported coal dependency: subject to international coal prices + currency risk

For Gas-Based Plants:
□ Domestic gas allocation: priority sector gets regulated price
□ LNG import dependency: highly price-volatile
□ Gas availability issue: many Indian gas plants stranded due to gas shortfall

Fuel Cost Pass-Through:
→ Regulated plants (CERC/SERC): fuel cost pass-through built into tariff
→ Merchant plants: no pass-through — bear full fuel risk
→ PPA tariff structure: two-part (fixed + variable) = full fuel pass-through
```

### Step 2.3 — Tariff Analysis for Thermal
```
Tariff Types:
1. Regulated Tariff (Cost-Plus): Guaranteed ROE on approved capital (NTPC model)
   → Most predictable; CERC sets allowed ROE (currently 15.5% on equity)
   → Risk: Regulatory disallowance of capital or costs

2. Long-term PPA (Competitive Bid): Fixed tariff for 25 years
   → Predictable revenue; risk = fuel cost not fully covered in older PPAs
   → Most Indian IPPs (Independent Power Producers) are in this category

3. Short-term / Merchant: Market price at power exchange
   → High risk, high reward; depends on real-time demand-supply
   → Suitable for surplus grid situations; falling merchant rates trend in India

Key Tariff Determination Bodies:
→ CERC: Central Electricity Regulatory Commission (interprovincial, central projects)
→ SERC: State Electricity Regulatory Commissions (each state)
→ Tariff revision timeliness: delays hurt recoveries
```

---

## Analysis Module 3 — Renewable Energy Analysis

### Step 3.1 — Capacity and Pipeline
```
Commissioned Capacity (Operational):
□ Solar: MW/GW commissioned
□ Wind: MW commissioned (onshore vs. offshore)
□ Hydro: MW commissioned
□ Storage (BESS): MWh/GWh commissioned
□ Total commissioned capacity: [MW / GW]
□ CUF (Capacity Utilisation Factor):
   → Solar: 22–26% typical in India
   → Wind: 28–38% (site dependent)
   → Hybrid (solar + wind): 35–50% improved profile

Under-Construction Capacity:
□ MW under construction
□ Expected commissioning timeline (risk: delay = deferred revenue)
□ Capital cost per MW: reducing trend for solar (now ₹4–5 Cr/MW)
□ Financing: tied to specific project (project finance) or corporate level?

Pipeline:
□ MW in pipeline (bid submitted / L1 / LOA received / financial close pending)
□ Order book to current capacity ratio (pipeline depth)
□ Bid intensity: competitive pressure on tariff (falling L1 tariffs = margin risk)
```

### Step 3.2 — PPA Quality Assessment
```
PPA Quality Matrix — For Each Major PPA:

Counterparty Quality:
→ SECI (Solar Energy Corporation of India): HIGHEST — government backed
→ NTPC (CPSU buying): HIGH — government corporation
→ Large state DISCOMs (Gujarat, Maharashtra Urja, Tata Power DSM): MEDIUM-HIGH
→ Weak state DISCOMs (UP DISCOM, TN GENCO, historical): MEDIUM-LOW
→ C&I (Commercial & Industrial) direct: variable

PPA Terms:
□ Tariff: fixed for duration? Escalating? Merchant?
□ Duration: 25 years (standard for solar) or shorter?
□ Payment security: Letter of Credit from DISCOM? (reduces payment risk)
□ Force majeure clauses: natural disasters, regulatory change protection?
□ Change in law: tariff protection if regulations change?

DISCOM Payment Track Record:
□ Days receivable from each DISCOM (benchmark: <90 days is acceptable)
□ Any historical payment defaults or DISCOM insolvency risk?
□ UDAY scheme health: state DISCOM financial position (Ministry of Power data)
```

### Step 3.3 — Renewable Valuation Metrics
```
For Renewable Companies:
→ EV per MW commissioned: industry benchmark for solar/wind
   → Large solar IPP (with SECI PPA): ₹6–8 Cr/MW EV
   → Wind (with good CUF): ₹7–9 Cr/MW EV
   → This gives quick sanity check on valuation vs. market price

EV/EBITDA for Renewables:
→ Operating renewable: 12–18x EBITDA
→ Growth renewable (large pipeline): 20–30x EBITDA (paying for future capacity)

WACC for Renewable Projects:
→ Typically 8–10% project IRR target (low but near-certain cash flows)
→ Corporate cost of equity: 12–14%
→ Levered IRR for equity: 14–18% for quality projects

Capacity Addition Pace:
→ Target CAGR of capacity addition: is it achievable?
→ Track record: has company historically delivered capacity on time?
→ Land, grid connectivity, approval delays = common bottlenecks
```

---

## Analysis Module 4 — Transmission Analysis

### Step 4.1 — Power Grid Corporation / Transmission Regulator Model
```
For PGCIL-type businesses:
→ ROE model: 15.5% allowed ROE on approved equity (CERC)
→ Revenue growth tied to new transmission asset addition (CAPEX)
→ Asset base (Rate Base) growth = revenue growth
→ Dividend policy: high dividend payer (regulated utility = stable cash flows)

Key Metrics:
□ Transmission system availability: >99% required; >99.5% is excellent
□ Capital addition: new lines commissioned vs. planned
□ Regulatory asset base (RAB): total approved capital × allowed equity %
□ Order book (for EPC arms): future capacity expansion visibility
□ Inter-state vs. Intra-state mix (CERC vs. SERC tariff)
```

### Step 4.2 — Private Transmission (InvITs)
```
IndiGrid, Sterlite Power's InvIT:
→ Infrastructure Investment Trust: similar to REIT for transmission assets
→ Revenue: long-term annuity (35 years) from ISTS (Inter-State Transmission)
→ Distribution Yield: InvIT distributes 90% of cash flows
→ Assessment: Distribution yield sustainability, DSCR, asset quality, pipeline

Key Metrics:
□ DSCR (Debt Service Coverage Ratio): >1.2x comfortable
□ Distribution per unit (DPU) sustainability
□ Available vs. contracted transmission: availability ≥ 98%
□ Asset acquisition pipeline: NAV per unit growth depends on accretive acquisitions
```

---

## Analysis Module 5 — Financial Analysis — Power Specific

### Step 5.1 — Debt Structure (Critical for All Power Companies)
```
Power companies are inherently debt-heavy (capital-intensive).
Focus on debt QUALITY, not just quantity.

Debt Analysis:
□ Project-level debt vs. corporate debt:
   Project debt: non-recourse (lender has claim on project, not parent)
   Corporate debt: recourse to parent (risk at parent level)
□ Weighted Average Cost of Debt: benchmark 7–9% for quality utilities
□ Debt Maturity Profile: any refinancing cliff in next 3 years?
□ Refinancing Risk: can new capacity serviced from PPA cash flows?

Debt/EBITDA:
→ Thermal IPP: 3–5x is sustainable (stable cash flows)
→ Renewable IPP: 4–7x acceptable (near-zero fuel cost = predictable cash)
→ >8x: Stress territory unless being refinanced proactively

Interest Coverage (EBIT/Interest):
→ >2.5x: Comfortable | 1.5–2.5x: Moderate | <1.5x: Stress
```

### Step 5.2 — Receivables from DISCOMs
```
DISCOM Receivable Days:
□ < 90 days: Acceptable
□ 90–180 days: Elevated — monitor
□ >180 days: HIGH RISK — cash flow stress
□ >365 days: CRITICAL — may require provisioning or legal action

Payment Security Mechanisms:
□ Letter of Credit (LC): bank guaranteed payment
□ Payment Security Fund (government-backed)
□ Tripartite Agreement (TPA): revenue sharing with state government
□ Late Payment Surcharge (LPS): CERC regulation protecting generators

DISCOM Financial Health Check:
→ State power distribution companies' annual revenue gap
→ State government willingness to subsidise (political risk)
→ RDSS (Revamped Distribution Sector Scheme) progress in key states
```

---

## Analysis Module 5A — Battery Energy Storage (BESS) Assessment

```
Why BESS matters now: Intermittency of solar/wind requires storage.
India BESS target: 47GWh by 2030 (National Electricity Plan).

BESS Business Model:
1. Merchant: Sell stored power at peak price (buy at off-peak solar price)
   → Revenue depends on price arbitrage spread: grid stability income
2. PPA-backed: Contracted storage (round-the-clock RE tenders with storage)
   → More predictable; SECI tenders specify storage component
3. Ancillary services: Grid frequency regulation for POSOCO
   → Stable, small revenue; first mover advantage

Key BESS Metrics:
□ BESS capacity (MWh or GWh): announced vs. commissioned
□ Duration: 2-hour vs. 4-hour system (longer = higher capital, higher revenue)
□ Chemistry: Lithium Iron Phosphate (LFP) = preferred for India (thermal safety)
□ Cost trajectory: $200/kWh (2023) → target $100/kWh by 2030
□ Project IRR with current costs: typically 10–14% for contracted BESS

Listed companies with BESS exposure:
→ Adani Green (large scale integrated solar+storage)
→ JSW Energy (largest private BESS ambition in India)
→ Greenko (pumped hydro + BESS hybrid)
→ Waaree Energies, Premier Energies (solar + storage EPC)
```

## Analysis Module 5B — Green Hydrogen Economics

```
Green Hydrogen (GH2): Electrolysis of water using renewable electricity
India National Green Hydrogen Mission: 5 MMT production by 2030

Economic Viability Check:
GH2 Cost = (Electrolyser Cost + RE cost + OPEX) / Hydrogen produced (kg)
→ Current India GH2 cost: $4–6/kg (not competitive vs. grey H2 at $1.5–2/kg)
→ Target viable cost: <$2/kg (requires cheap RE + cheap electrolysers)
→ Timeline to viability: optimistic 2027–2030 | realistic 2030–2035

Electrolyser Cost Learning Curve:
→ Current: $600–1,000 per kW | Target: $200/kW
→ Indian manufacturers: Thermax, L&T, John Cockerill JV, BHEL
→ Electrolyser localisation = India cost advantage (PLI potential)

Who benefits from GH2 ecosystem:
□ Hydrogen producers: Adani (AGEL), Greenko, NTPC, Torrent
□ Electrolyser manufacturers: Thermax, L&T, BHEL (listed)
□ Hydrogen storage/transport: Finolex pipes, other infrastructure
□ Industrial consumers (offtake): refineries, fertiliser, steel

CAUTION for investors: GH2 is pre-revenue for most Indian companies.
Do not value GH2 ambitions at full EV unless specific contracted offtake exists.
Apply high probability discount: 20–30% probability-weighted NPV at best.
```

## Analysis Module 5C — Coal Plant Stranded Asset Risk

```
Thermal Coal Plants Face Structural Headwinds Post-2030:
□ India's NDC (Nationally Determined Contribution): net-zero by 2070
□ 2030 interim target: 50% power from non-fossil; coal share declining
□ Stranded asset risk: coal plants with >20 years of remaining life

Assessment Framework:
□ Age of thermal assets: plants commissioned pre-2000 = fully depreciated
   → Fully depreciated plant = sunk cost; marginal cost = fuel + O&M only
   → At low marginal cost, old plants can still be profitable for years
□ Plants commissioned post-2015 with 25-year PPA: lower stranded asset risk
   (PPA cashflows extend well into future; regulatory change risk moderate)
□ Merchant coal plants with no long-term PPA: highest stranded asset risk
□ Efficient (supercritical, ultra-supercritical) vs. subcritical plants:
   → Subcritical: older technology, higher emissions, first retirement targets
   → Supercritical: higher efficiency, lower emissions, last to retire
□ Proximity to CEA's (Central Electricity Authority) retirement list:
   CEA has identified 24GW of sub-critical plants for accelerated retirement

How to value stranded asset risk:
→ Remaining PPA life determines cash flow certainty
→ Post-PPA residual value: significant haircut if RE is cheaper by then
→ Apply 15–25% discount to DCF for plants with >15 year remaining life
   in merchant or spot-market revenue model
```

## Red Flag Summary — Power / Utilities

### CRITICAL Flags
```
❗ DISCOM PPA counterparty defaulting on payments (>6 months receivable)
❗ Fuel supply disruption causing PLF <40% for 2+ consecutive quarters
❗ CERC/SERC adverse tariff order (disallowing capital or cost recovery)
❗ Regulatory approval for tariff increase refused for 3+ years
❗ Project-level DSCR <1.0x (cash insufficient to service project debt)
❗ Under-construction project delayed >18 months (massive financing cost overrun)
❗ Land acquisition failure blocking large renewable project
❗ Grid curtailment >20% (renewable energy being asked to back down despite PPA)
```

### HIGH Flags
```
⚠️ Coal stock <15 days at thermal plant (fuel supply risk)
⚠️ PLF declining from >80% to <70% without clear demand explanation
⚠️ DISCOM receivables >180 days from major off-taker
⚠️ Corporate debt rising faster than new capacity commissioned
⚠️ Capacity addition behind target by >20% for 2 consecutive years
⚠️ Merchant power revenue >30% of total (highly volatile component)
⚠️ Government policy reversal on renewable tariff support (rare but possible)
```

---

## Power Utilities Valuation Framework

```
THERMAL POWER:
Primary: EV/EBITDA
  → Fully regulated (NTPC): 8–12x EBITDA (bond-like, stable)
  → Long-term PPA IPP: 6–10x EBITDA
  → Merchant exposure: 5–8x EBITDA (volatile discount)
Secondary: P/B (useful for regulated utilities)
  → Allowed ROE 15.5% → justified P/B = 1.2–1.5x for regulated book

RENEWABLE ENERGY:
Primary: EV per MW commissioned (quick check)
Secondary: EV/EBITDA (with pipeline premium)
  → Pure operating: 12–15x
  → High-growth pipeline: 20–30x (paying for future)
Note: DCF on renewable cash flows most rigorous — 25-year PPA makes DCF tractable

TRANSMISSION:
  → P/B for regulated: similar to NTPC methodology
  → Yield-based for InvIT: (DPU / Unit Price) vs. comparable fixed income

DISTRIBUTION (Private):
  → P/E with regulatory risk discount
  → ROE vs. allowed SERC ROE (premium if company earns above allowed)
```

---

## Power Utilities Analysis Output Format

```
POWER UTILITIES ANALYSIS
Company: [Name] | Segment: [Thermal/Renewable/Transmission/Distribution]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

CAPACITY:
  Total Installed:       [MW/GW] | Thermal: [MW] | Renewable: [MW]
  Under Construction:    [MW] | Expected Commissioning: [Timeline]
  Pipeline:              [MW]

OPERATING PERFORMANCE:
  PLF / CUF:             [%] → [Excellent/Good/Adequate/Concern]
  [Thermal only] Coal stock: [X] days | Fuel supply: [FSA secured: [%]]
  [Renewable only] Grid curtailment: [%]

PPA QUALITY:
  % Revenue from PPAs:   [%] | Average PPA tariff: ₹[X]/unit
  Key counterparties:    [SECI/NTPC/Strong DISCOM/Weak DISCOM + amounts]
  DISCOM receivables:    [X] days → [Assessment]

FINANCIAL:
  Revenue Growth:        [%]
  EBITDA Margin:         [%]
  Net Debt / EBITDA:     [X]x → [Sustainable/Elevated/Concern]
  Interest Coverage:     [X]x
  DSCR (Project Level):  [X]x → [Comfortable/Adequate/Stress]

REGULATORY:
  Tariff Structure:      [Regulated/PPA Fixed/Merchant mix]
  Key Regulatory Risk:   [CERC/SERC pending orders or concerns]

CRITICAL FLAGS:          [Count + list]
HIGH FLAGS:              [Count + list]

VALUATION:
  EV/EBITDA:            [X]x → Benchmark: [Thermal: X]x | [Renewable: X]x
  EV/MW:                ₹[X]Cr per MW → Benchmark: ₹[X]Cr
  Verdict:              [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Investment Case:      [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:             [Fuel/PPA/Regulatory/Financial]
  Key Catalyst:         [Capacity addition / tariff order / debt refinancing]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Power & Utilities Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 28. Skill 24 — Chemical Sector Analyzer

**Merged from standalone file `AI_Chemical_Analysis_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Sector Specialist — Specialty Chemicals, Agrochemicals, Dyes, Pigments, Fluorochemicals, CRAMS, API Intermediates

---

## CRITICAL AI INSTRUCTION

The Indian chemical sector is highly heterogeneous. A specialty chemical company with 35% EBITDA margin and a commodity chemical company with 8% margin exist in the same "chemicals" sector. **Always classify the company on the specialty-commodity spectrum first before applying any metric or multiple.** The China+1 opportunity is real but lumpy — assess which specific customers, categories, and geographies are driving it for this specific company. Never generalise the China+1 thesis without company-level evidence.

---

## Purpose

Deliver specialist analysis of Indian chemical companies across the specialty-commodity spectrum, covering agrochemicals, dyes and pigments, fluorochemicals, performance chemicals, CRAMS (Contract Research and Manufacturing Services), and API intermediates. Identify companies with sustainable differentiation, captive customers, and strong China+1 positioning.

---

## Pre-Flight Requirements

```
□ Annual Report (last 3 years) with product-wise revenue if available
□ Investor presentations with customer/end-market breakdown
□ R&D pipeline disclosures and new product launches
□ Export vs. domestic revenue split by product
□ Raw material composition and sourcing (China dependency)
□ CRAMS/CDMO customer contract details (if disclosed)
□ Environmental compliance and ESG disclosures
□ Capacity expansion and technology investment plans
□ Agrochemical: CIBRC registration data, patent expiries in pipeline
□ Fluorochemicals: Quota / HFC regulation compliance
□ Management concall transcripts (last 4 quarters)
```

---

## Analysis Module 1 — Specialty vs. Commodity Classification

### Step 1.1 — The Spectrum Assessment
```
SPECIALTY CHEMICALS (High Value — Target these):
Definition: Products with limited competitors, custom specifications, high technical barrier
Characteristics:
  → EBITDA margin: 20–40%+
  → Customer-specific: made to spec, not interchangeable
  → Pricing power: price leader or price taker based on IP
  → R&D intensity: >3% of revenue
  → Customer lock-in: long qualification cycles (6–24 months)
  → Examples: Agrochemical actives, fluoropolymers, performance chemicals

MID-SPECIALTY (Medium Value):
Definition: Standardised but technical products; some differentiation
  → EBITDA margin: 15–25%
  → Multiple qualified suppliers but not many
  → Examples: Pigments, dyes, specific pharmaceutical intermediates

COMMODITY CHEMICALS (Low Value — Avoid at high multiples):
Definition: Standardised product, interchangeable, price-driven market
  → EBITDA margin: 8–15%
  → Chinese competition direct
  → Examples: Caustic soda, basic intermediates, standard petrochemicals
  → Only buy at distressed valuations or turnaround plays

Classification Test for Company Under Review:
→ Can the customer switch supplier without major qualification effort? (YES = commodity)
→ Does the company know its customers by name and share revenue with them? (YES = specialty)
→ Is price the primary competition criterion? (YES = commodity)
→ Is there an R&D team developing new molecules? (YES = specialty direction)
```

---

## Analysis Module 2 — China+1 Opportunity Assessment

### Step 2.1 — Category-Level Analysis
```
China's share of global chemical production by category:
→ Agrochemical Intermediates: 70–80% (China dominant)
→ Dyes and Pigments: 60–70% (China dominant)
→ Fluorochemicals: 70%+ (China dominant but regulations helping India)
→ Specialty Pharma Intermediates: 50–70%
→ Specialty Performance Chemicals: 20–40% (less dominated)

India's Competitive Position:
→ Where India wins: Complex synthesis, multi-step chemistry, EHS-compliant capacity
→ Where India struggles: Continuous process chemicals, petrochemical-derived basics
→ Key advantage: Chemist talent pool, English communication, IP respect

China+1 Evidence Check (Company-Level):
□ Has the company added new customers from US/Europe in last 3 years?
□ Has export revenue to non-China markets grown >20% CAGR?
□ Are global agrochemical/pharma companies qualifying Indian source?
□ Has the company disclosed any customer-specific capacity addition?
□ New product development specifically for global customer requirements?
```

### Step 2.2 — Customer Quality and Stickiness
```
CRAMS / CDMO Model (Highest Quality):
→ Long-term supply agreements (3–5 year contracts)
→ Customer-specific molecules (customer IP, India manufacturing)
→ Revenue visibility: order book + annuity supply agreements
→ Price: cost-plus or agreed fixed margin (not spot market)
→ Leading Indian CRAMS: Divi's, PI Industries, Syngene, Laurus

Non-CRAMS Specialty:
→ Sell to multiple global customers
→ Product standardised but with high technical qualification barrier
→ Price set by global market + India cost advantage
→ Examples: SRF (fluorochemicals), Navin Fluorine, Aarti Industries

Customer Concentration:
□ Top 3 customers as % of revenue: >50% = concentration risk (but also depth)
□ Contract tenure: spot (high risk) vs. multi-year (lower risk)
□ Customer diversification trend: improving (more customers) or not?
□ Geographic diversification: US + Europe + Japan + Domestic = safer
```

---

## Analysis Module 3 — Agrochemical Specific Analysis

### Step 3.1 — Agrochemical Business Model
```
Types within Agrochemicals:
1. Technical (Active Ingredient): highest value, most complex synthesis
2. Formulations: blending actives with carriers/solvents; lower margin
3. Generic vs. Patent-Protected:
   → Patent-protected (in-licensing): regulated market entry, high margin
   → Post-patent generic: open competition, commodity pricing
   → New molecule (own discovery): very rare, very high value

Key Agrochemical Markets:
□ India domestic: 150 million+ farm families; depends on monsoon, crop prices
□ US market: Registration required (EPA); long cycle but high value
□ Europe: Most stringent (EFSA); highest value if approved
□ Latin America: Brazil + Argentina = large opportunity; deregulated, fast
□ Rest of World: Africa, Southeast Asia = growing

CIBRC Registration (India):
→ CIBRC = Central Insecticides Board and Registration Committee
→ New molecule registration: 3–5 years, significant investment
→ Registered molecule = 9-year data exclusivity (protection from generics)

Patent Pipeline Assessment:
→ List major global agrochemical molecules going off-patent in 2025–2030
→ Which Indian company has filed regulatory applications for these?
→ First-mover after patent expiry = 2–3 years of limited competition window
```

### Step 3.2 — Agrochemical Financial Metrics
```
Seasonality Pattern:
→ India: Kharif season (June-September) = Q1/Q2 heavy
→ Global: Northern hemisphere = Q1/Q2 (pre-summer crop protection)
→ Never assess single-quarter agrochemical results without seasonality context

Inventory Destocking Risk:
→ 2022–2023 taught us: post-COVID channel overstocking = 2–3 years of destocking
→ Check: channel inventory levels (management commentary)
→ Check: ordering patterns from global agrochemical innovators (Syngenta, Bayer)
→ Restocking cycle: typically follows after 6–8 quarters of destocking

Price Realisations:
→ Molecule-level price trends: check if Chinese competition is driving down prices
→ Volume growth offsetting price compression = volume story, not value story
→ Margin impact of realisations: EBITDA/kg trend more revealing than ₹ EBITDA
```

---

## Analysis Module 4 — Fluorochemicals Analysis

### Step 4.1 — Fluorochemical Value Chain
```
Value Chain (ascending complexity/margin):
Fluorspar → HF (Hydrofluoric Acid) → HFCs/HFOs → Fluoropolymers → Specialty Fluorine Chemicals

India's Position:
→ HF: commodity, some India production
→ HFCs: India limited; Chinese dominant
→ Fluoropolymers: SRF (PTFE), Navin Fluorine — growing
→ Specialty Fluorine (Pharma/Agro): highest value — PI Industries, Navin Fluorine, Halocarbon

HFC Phase-Down (Kigali Amendment):
→ HFCs (refrigerants) being phased out globally by 2040
→ Replacement: HFOs (Hydrofluoro-Olefins) — higher tech, higher margin
→ Indian companies transitioning to HFOs = significant opportunity
→ But HFO patents held by Honeywell and Chemours — licensing needed

Fluorspar Security:
→ India depends on China/Mexico for fluorspar (raw material)
→ Company with fluorspar security = competitive advantage
→ Check: does the company have long-term fluorspar supply contracts?
```

---

## Analysis Module 5 — Financial Quality — Chemicals Specific

### Step 5.1 — Revenue Quality
```
Price × Volume Decomposition:
□ Volume growth: actual capacity utilisation increase
□ Price realisation: per tonne/kg/litre trend
□ Product mix: higher-value products gaining share?
→ Sustainable earnings come from volume + mix improvement
→ Price-driven earnings at commodity peaks are not sustainable

Export vs. Domestic Mix:
→ Export > 50% = global competitiveness; subject to USD/INR
→ Domestic > 70% = protected (less China impact) but lower margin
→ Ideal: 40–60% export with global customer diversity

New Products as % of Revenue (Innovation Index):
→ Revenue from products launched in last 5 years / Total revenue
→ >20%: Active innovation pipeline
→ <5%: Mature portfolio, limited new growth without external acquisition
```

### Step 5.2 — Margin Analysis
```
Gross Margin:
→ Specialty: 45–65%
→ Mid-specialty: 30–45%
→ Commodity: 15–25%

EBITDA Margin:
→ Specialty CRAMS: 25–40%
→ Specialty non-CRAMS: 20–30%
→ Mid-specialty: 15–22%
→ Commodity: 8–14%

Raw Material (RM) Analysis:
□ RM as % of COGS: 50–70% typical
□ China-sourced RM: risk of supply disruption, price volatility
□ India RM availability: backward integration reducing dependency?
□ Forward/backward integration: how much of value chain is owned?

R&D Investment:
□ R&D as % of revenue: specialty target >3%, CRAMS target >5%
□ New molecule pipeline: patent filings, tech licensing
□ R&D CAPEX vs. revenue R&D: capitalisation policy (check forensic skill)
```

### Step 5.3 — Environmental Compliance
```
Chemical sector has significant ESG risk:
□ Zero Liquid Discharge (ZLD): mandatory for most chemical plants in India
□ Effluent Treatment Plant (ETP) compliance
□ Air emission control: stack emissions under CPCB norms
□ Hazardous waste management: manifest system compliance
□ REACH compliance (Europe): required for chemical exports to EU
□ EPA compliance for US exports (if applicable)

Non-compliance Risk:
→ CPCB/State PCB closure orders have shut multiple chemical plants
→ NGT (National Green Tribunal) orders: rapid escalation possible
→ Reputational risk with global customers (mandatory ESG audits)

Due Diligence:
□ Any CPCB closure notice in last 5 years?
□ Any NGT litigation pending?
□ Customer sustainability audit passed?
□ ETP capacity matching production capacity?
```

---

## Analysis Module 5A — Anti-Dumping Duty (ADD) Landscape

```
China chemical dumping is a double-edged threat and opportunity for Indian companies:

For Import Substitution plays (ADD = POSITIVE):
→ ADD imposed on Chinese imports = price umbrella for Indian producers
□ Is this company's product protected by anti-dumping duty?
□ If ADD is in place: what is the ADD rate? What is the sunset review date?
   (ADD typically lasts 5 years; can be extended on review)
□ Companies to benefit: those producing for domestic market in protected category
□ Risk: ADD removal or reduction on sunset review = price competition returns

Key ADD categories relevant to Indian chemicals (check DGTR website):
→ Caustic soda, soda ash: some protection
→ Specific dyes and pigments: case-by-case
→ Certain agrochemical intermediates
→ Polyester fibre, PVC, specific polymers

For Export-Oriented Specialty Chemicals (ADD = NEGATIVE):
→ Indian speciality chemical companies selling to China-ADD protected markets
→ If India is treated as developing country: reduced ADD rates
→ But if India grows market share significantly: counter-ADD risk on Indian exports

Anti-subsidy (CVD) actions:
□ Any countervailing duty investigations against this company's exports
  in key markets (US, EU)? → Google: "[company name] CVD investigation"
```

## Analysis Module 5B — Agrochemical Monsoon and Kharif/Rabi Sensitivity

```
Agrochemical demand is directly linked to crop cycles:

Kharif Season (June–October):
→ Key crops: Rice, Cotton, Sugarcane, Soybean, Maize
→ Agrochemical demand peak: April–August (pre-planting + growing)
→ Company revenue peak: Q1 (Apr-Jun) and Q2 (Jul-Sep)

Rabi Season (November–March):
→ Key crops: Wheat, Mustard, Pulses, Vegetables
→ Agrochemical demand peak: October–January
→ Company revenue: Q3 (Oct-Dec) higher for rabi-focused companies

Monsoon Impact Assessment:
□ Normal monsoon (>96% of LPA): Positive — farmers spend more on crop protection
□ Drought (< 90% of LPA): Negative — farmers defer spending
□ Excess rainfall/flood: Mixed — some diseases increase demand, but logistics disrupted
□ El Niño year: Higher drought probability → selective demand

IMD (India Meteorological Department) Forecast:
→ Always check IMD's southwest monsoon forecast for current year
→ First-half vs. second-half distribution matters (kharif vs. rabi setup)

Key indicators to monitor:
□ Reservoir levels (40 major reservoirs): water availability for rabi irrigation
□ Rabi sowing progress (Ministry of Agriculture weekly data)
□ Farmer MSP and procurement: affects farmer income and hence agrochem spending
□ State-wise crop patterns: companies with regional concentration face localised risk

Channel Inventory Check:
→ Post-COVID (2022–23): massive channel overstocking; destocking lasted 6–8 quarters
→ Current (2025): verify if channel inventory is normalized
→ Primary vs. secondary sales: company reports primary (to channel) 
  not secondary (to farmer); need to validate channel health via mgmt commentary
```

## Analysis Module 5C — PFAS and Fluorochemical Regulation Risk

```
PFAS (Per- and Polyfluoroalkyl Substances) Regulatory Landscape:

What are PFAS?
→ Long-chain fluorochemicals used in: non-stick coatings, firefighting foam, 
  industrial applications, performance fabrics
→ Known as "forever chemicals" — do not biodegrade

Global Regulatory Risk:
□ US EPA: proposed rules to limit PFAS in drinking water, industrial discharge
□ EU REACH: blanket restriction on PFAS substances proposed (2023 proposal)
□ If EU PFAS ban passes: ₹500-2000Cr revenue at risk for Indian exporters
  depending on product specifics

Which Indian Companies Affected:
→ SRF, Navin Fluorine, Gujarat Fluorochemicals: check product portfolio
→ Long-chain PFAS (C8, C10): MOST at risk for regulatory action
→ Short-chain PFAS and fluoropolymers (PTFE): LOWER risk but watch
→ HFOs and pharmaceutical fluorine: NOT PFAS; minimal regulatory risk

Risk Assessment Per Company:
□ Does the product portfolio include long-chain PFAS for EU/US markets?
   → YES: High regulatory risk; assess % of revenue
   → NO: Lower risk; may benefit as substitute supplier
□ Is company developing non-PFAS alternatives? (Green chemistry pivot)
□ EU PFAS customer communication: have EU customers requested alternatives?

Transition Opportunity:
→ PFAS restriction creates demand for substitute chemistries
→ Indian specialty chemical companies with green fluorine tech = opportunity
→ Watch: companies announcing PFAS-free product lines (positive ESG + business signal)
```

## Analysis Module 6 — CapEx and Return Analysis

### Step 6.1 — CapEx Quality
```
CapEx for Specialty Chemicals:
□ New synthesis capabilities: R&D + pilot + scale-up
□ Capacity expansion for existing products (demand-pulled = good)
□ New molecule / new customer capacity (spec-built = quality)
□ Backward integration (lower RM cost = EBITDA margin improvement)

CapEx Red Flags:
⚠️ CapEx announced for commodity products in competitive market
⚠️ Greenfield site in non-chemical hub (access to chemists, utilities, logistics?)
⚠️ Very long CWIP (>3 years for chemical plants) — execution concern
⚠️ CapEx financed by high-cost debt without confirmed customer demand

Return Metrics:
□ ROCE target for new capacity: >18% in 3rd year of operation
□ Revenue per ₹ of CapEx: benchmark ₹1.5–2.5 of revenue per ₹1 of CapEx (year 3)
□ EBITDA/tonne for new capacity vs. existing: expansion value-accretive?
```

---

## Red Flag Summary — Chemicals

### CRITICAL Flags
```
❗ CPCB / State PCB plant closure order (immediate revenue stoppage)
❗ Loss of major global customer (CRAMS contract termination)
❗ Chinese competitor entering key product category at 30%+ price discount
❗ R&D pipeline failure: key molecules failing regulatory qualification
❗ Fluorspar / key RM supply disruption lasting >3 months
❗ Environmental contamination affecting community or water source
❗ Debt rising while EBITDA margin compressing (distress borrowing)
```

### HIGH Flags
```
⚠️ EBITDA margin falling >500bps without clear RM cost explanation
⚠️ Export revenue stagnant for 2+ years (China+1 thesis not materialising)
⚠️ Customer concentration: top customer >40% of revenue at risk
⚠️ Inventory days rising >60 days from 2-year average (demand slowdown)
⚠️ R&D spend declining (innovation pipeline drying up)
⚠️ CWIP as % of assets >25% for >2 years (execution risk)
⚠️ Regulatory approval delays for key products (CIBRC / EPA / EFSA)
⚠️ Volume growth flat while revenue growth = only price (unsustainable)
```

---

## Chemical Sector Valuation Framework

```
Primary Method: EV/EBITDA (most common for chemicals)

Specialty CRAMS / Top-tier: 30–45x EBITDA
  (Divi's, PI Industries quality)
Quality Specialty (broad portfolio): 20–30x EBITDA
Mid-Specialty: 14–20x EBITDA
Commodity with specialty aspiration: 10–15x EBITDA
Pure commodity: 6–10x EBITDA

EBITDA/tonne or EBITDA/kg:
  → More insightful than ₹ EBITDA for volume-driven businesses
  → Expanding EBITDA/kg = value creation regardless of volumes

P/E Method:
  → Specialty: 30–50x | Mid-specialty: 20–30x | Commodity: 10–15x

EV/Revenue: 
  → Specialty: 5–10x | Mid: 3–5x | Commodity: 1–2x

Important: Adjust for cycle position in commodity/mid-specialty companies.
```

---

## Chemical Sector Analysis Output Format

```
CHEMICAL SECTOR ANALYSIS
Company: [Name] | Classification: [Specialty/Mid-Specialty/Commodity]
Sub-segment: [Agrochemical/Fluorochemical/Dyes/CRAMS/API Intermediate/Other]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

BUSINESS QUALITY:
  Classification:       [Specialty/Mid/Commodity — justification]
  Revenue Mix:          [Export [%] | Domestic [%] | Product A [%] | Product B [%]]
  CRAMS Revenue:        [₹Cr / [%] of total]
  Customer Quality:     [Top 3 customers, contract type, stickiness]
  China+1 Evidence:     [Specific new customers/programs — not generic thesis]

R&D AND INNOVATION:
  R&D as % Revenue:    [%] | New product revenue (<5yrs): [%]
  Key pipeline:        [Top 2–3 programs in development]
  Regulatory status:   [CIBRC / EPA / EFSA — key filings]

FINANCIAL QUALITY:
  Revenue Growth:      [%] | Volume growth: [%] | Price change: [%]
  Gross Margin:        [%] → [vs. 5yr avg: [%] vs. peer benchmark]
  EBITDA Margin:       [%] → [Assessment]
  EBITDA/tonne:        [₹/kg or ₹/MT — trend]
  RM Sourcing:         [China dependency: [%] of key inputs]

ESG / COMPLIANCE:
  Environmental:       [CPCB/PCB status — any notices?]
  ZLD Compliance:      [Yes/No/In progress]
  Global Audits:       [REACH / Customer sustainability audits: Pass/Pending]

CAPITAL ALLOCATION:
  CapEx (TTM):         ₹[X]Cr | Purpose: [New capacity/Integration/Maintenance]
  CWIP:                ₹[X]Cr | Status: [On track/Delayed]
  ROCE:                [%] → [vs. WACC [%]]

CRITICAL FLAGS:        [Count + list]
HIGH FLAGS:            [Count + list]

VALUATION:
  EV/EBITDA:          [X]x → Benchmark for this tier: [X]x
  P/E:                [X]x
  Cycle Position:     [Commodity cycle: Trough/Mid/Peak — if applicable]
  Verdict:            [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Investment Case:    [Strong Buy/Buy/Hold/Reduce/Avoid]
  Key Risk:           [Environmental/Customer/RM/China competition/Regulation]
  Key Catalyst:       [New product launch / capacity / global qualification]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Chemical Sector*
*Integrates with: Forensic Accounting Skill, DCF Valuation Skill, Skill 01 (Master Research)*

## 29. Skill 25 — Microcap Research Protocol

**Merged from standalone file `AI_Microcap_Research_Skill.md` (fuller depth version) — v_0.0 merge.**

**Version:** v_0.0 | **Status:** Production Ready | **Last Updated:** July 2025
**Category:** Investment Style — Microcap and Small Company Analysis (Market Cap < ₹2,000 Cr)

---

## CRITICAL AI INSTRUCTION

Microcaps carry risks that simply do not exist in large or midcaps: **illiquidity, information asymmetry, governance opacity, and operator manipulation**. The upside can be extraordinary — but the base rate of permanent loss is also far higher. This skill enforces a **much stricter discipline than standard analysis**. Every positive signal must be doubly verified. Every governance concern is disqualifying until proven otherwise. **When in doubt about a microcap, the answer is always: do not invest.**

---

## Purpose

Evaluate Indian microcap companies (market cap ₹100–2,000 Cr) with a framework that balances the extraordinary wealth-creation potential of this segment with appropriate protection against fraud, governance failures, liquidity traps, and management incompetence.

---

## Pre-Flight Requirements

```
□ Annual Report (minimum last 3 years) — file on MCA website if not on BSE/NSE
□ Management background: promoter's history, education, other businesses
□ Shareholding pattern (last 8 quarters): FII, DII, promoter, public breakdown
□ Related party transaction disclosures in detail
□ Auditor identity: Big 4 / Top 10 / Small regional firm?
□ BSE/NSE announcement history (last 2 years): any unusual events?
□ News search: promoter name + company name (find any controversies)
□ MCA (Ministry of Corporate Affairs) filings: director DIN history
□ SEBI action search: is the company or promoter in any SEBI watchlist?
□ Industry contacts / DRHP (if recently listed): additional color
```

---

## Analysis Module 1 — Governance and Promoter Assessment (First Gate)

### Step 1.1 — Promoter Background Investigation
```
Mandatory Checks:
□ Promoter name search on MCA: how many other companies?
   → >20 companies = shell network concern
   → Related companies borrowing from this listed entity = RED FLAG
□ SEBI enforcement: searchable at sebi.gov.in (enforcement actions)
□ ROC filing history: any NCLT / insolvency proceedings on related companies?
□ News search: [Promoter name] + fraud / defaulter / bank recovery / arrest
□ Past listed company track record: did previous listed ventures end well?
□ Education and domain expertise: does promoter understand the business?
□ Age: succession planning for older promoters in capital-intensive businesses

Promoter Holding Quality:
→ >60%: Strong alignment | 45–60%: Good | 30–45%: Moderate | <30%: Concern
→ Promoter buying from open market (last 12 months): Positive signal
→ Promoter consistently selling: Red Flag regardless of stated reason
→ Creeping acquisition attempt: significant positive signal of conviction
```

### Step 1.2 — Auditor Quality for Microcaps
```
Auditor Tier Assessment:
→ Big 4 or Top 10 (B S R, SRBC, Walker Chandiok, etc.): SIGNIFICANT POSITIVE for microcap
→ Mid-tier regional firm: Acceptable if reputation is known
→ Unknown small firm with one or two partners auditing a ₹500Cr revenue company: RED FLAG

Audit Report:
□ Any qualifications? (For microcap, even minor qualification = serious concern)
□ Any observations on internal financial controls?
□ CARO observations: any adverse remarks?
□ Auditor changed recently? (For microcaps: very suspicious)

Non-audit fees to auditor:
→ >20% of audit fee for a microcap = potential independence concern
```

### Step 1.3 — Board Quality
```
□ Number of independent directors: SEBI requires ≥2 or 1/3 of board
□ Are they genuinely independent? (Check professional background, relationship)
□ Audit committee: financially literate independent director as chairman?
□ Whistle-blower policy: explicitly stated in annual report?
□ Board meeting frequency: minimum 4 per year; very low attendance = governance concern
□ CEO/MD remuneration vs. PAT: >5% of PAT = excessive for microcap
□ Family members on payroll: how many, at what salaries?
```

---

## Analysis Module 2 — Business Quality Assessment

### Step 2.1 — Business Model Clarity Test
```
Three Questions That Must Be Answered in 3 Sentences Each:
1. What does this company do? (Product/service, who pays them)
2. Why is this company better than alternatives? (Competitive advantage)
3. Why will it still be relevant in 5 years? (Sustainability)

If you cannot answer all three clearly from publicly available information:
→ DO NOT INVEST. Information asymmetry is too high.

Business Model Green Flags for Microcaps:
□ Clear, simple, understandable product or service
□ Niche market leadership (even if small niche)
□ Repeat/recurring customer base
□ Hard-to-replicate capability (specialized knowledge, certifications, geography)
□ Operating in growing industry with multiple tailwinds
□ Domestic market focus initially (easier to verify than export claims)
```

### Step 2.2 — Niche Market Leadership Assessment
```
Microcap investing is about finding:
→ Category leaders in SMALL, GROWING niches
→ NOT second-place players in large markets

Evidence of Niche Leadership:
□ Market share in defined product category: is it >20% in its niche?
□ Customer testimonials or long-term relationships (if verifiable)
□ Long-standing certifications or approvals (NABL, ISO, DRDO, BIS, etc.)
□ Pricing premium vs. competitors: can they charge more?
□ Repeat order rate from key customers: long-standing relationships?

Beware "Market Leader" Claims:
→ Many microcaps claim market leadership without evidence
→ Verify: what is total market size? What is company revenue vs. stated market size?
→ If claimed market size seems inflated: promoter credibility concern
```

---

## Analysis Module 3 — Financial Quality — Microcap Specific

### Step 3.1 — Cash Flow Verification (Non-Negotiable)
```
For microcaps: OCF verification is MORE important than for large caps.
Fraudulent financials are far easier to execute and hide in small companies.

Critical Cash Flow Tests:
□ OCF/PAT ratio: >70% minimum | <50% for >2 years = serious concern
□ Cash balance at bank: verify vs. cash flow statement (auditor confirmation)
□ Capital expenditure: is there physical evidence? (Site visit advisable)
□ Bank statements: some companies voluntarily provide copies; request if possible
□ Bank borrowings: can cross-check against stated debt in balance sheet

Revenue Verification Methods:
□ Cross-check with GST returns (visible in some sectors through industry data)
□ Export revenue: verify with DGFT data / shipping bill records (public database)
□ Customer names disclosed: are these real, identifiable companies?
□ Industry channel checks: distributors/dealers confirm demand
```

### Step 3.2 — Key Financial Thresholds
```
Minimum Standards for Microcap Investment:
□ Revenue > ₹100 Cr (below this: too small to have institutional oversight)
□ Profitable for at least 3 of last 5 years
□ Not in loss for last 2 consecutive years
□ Debt/Equity < 1.5x (high debt in microcap = distress amplifier)
□ Interest coverage > 3x (low coverage = one bad quarter = distress)
□ Promoter pledge = 0% (any pledge in microcap = serious red flag)
□ ROCE > 15% (business is creating value above cost of capital)
□ OCF positive for at least 3 of last 5 years

Revenue and Profit Growth:
□ Revenue CAGR > 15% over 3 years (microcaps need to justify illiquidity premium)
□ Earnings CAGR > 20% over 3 years
□ Growth must be fundamental (volume + customer expansion) not just price
```

### Step 3.3 — Working Capital Quality
```
Working Capital for Microcaps:
□ Receivable days: <90 days for B2B | <45 days for B2C (stretched receivables = cash crisis risk)
□ Customer advances: positive sign (customers paying ahead = demand strength)
□ Trade payables: are suppliers being paid on time? (Very small companies sometimes stretch payables dangerously)
□ Related party receivables: any amount owed to company by promoter entities? (Serious governance flag)

Cash at Bank vs. Claimed:
□ Idle cash should be earning: FD interest income should appear
□ Cash shown but no interest income = suspicious
□ Cash invested in related-party ICDs (Inter-Corporate Deposits): RED FLAG
```

---

## Analysis Module 3A — GST and Income Tax Cross-Verification

```
GST Cross-Check (Most Powerful Revenue Verification Tool):
□ GSTR-1 (Outward supplies): company files monthly/quarterly → total taxable supplies
□ GSTR-3B (Summary return): net GST paid
□ Available via: GSTIN lookup portals, some states publish GSTIN-level data
→ Cross-check: GSTR-1 turnover vs. Annual Report revenue
   If Annual Report revenue >> GSTR-1 supplies: company may be inflating
   (Exports are zero-rated — deduct export revenue before comparing)

How to access:
→ Master GSTIN from company's invoices or RoC filing
→ Some aggregators (Tofler, Tracxn, IndiaFilings) show GSTIN-level data
→ Direct check: GST.gov.in GSTIN verification
   (Shows registration status, filing regularity — if company not filing → serious concern)

Income Tax Cross-Check:
□ Advance Tax payments: large companies disclose quarterly advance tax paid
   Cross-check against P&L tax expense — material divergence = concern
□ Form 26AS (Tax Credit Statement): not publicly available but company should
   be able to confirm TDS deducted matches what customers declare
□ I-T Assessment status: any pending tax demands (disclosed in contingent liabilities)?
   → Large unexplained I-T demand = either aggressive tax positions or income concealment

TDS on revenues:
→ TDS deducted by customers appears in Form 26AS
→ TDS credit claimed in ITR must match TDS in P&L (income)
→ For microcap: ask management for TDS credit (Form 16A) as revenue verification
   (Reputable management should have no issue sharing this in investor call)

Practical Application:
Step 1: Note company's reported revenue (Annual Report)
Step 2: Look up GSTIN → check GSTR-1 aggregate value if available
Step 3: Check if advance tax disclosures match P&L
Step 4: Flag any >15% discrepancy for investigation
```

## Analysis Module 3B — First-Generation vs. Second-Generation Promoter Framework

```
Promoter generation significantly impacts risk profile:

FIRST-GENERATION PROMOTER (Founder):
Strengths:
+ Deep domain knowledge; built the business from scratch
+ Skin in the game: personal wealth = business value
+ Often very frugal with capital; high ROCE culture
+ Long-term thinking: legacy motivation
Risks:
− Succession planning unclear: what happens if promoter is unable to lead?
− Centralised decision-making: company cannot function without founder
− Family disputes if multiple promoter family members
− May resist governance improvement (used to running privately)

Assessment:
□ Age of founder: <55 = lower succession concern | 65+ = active succession needed
□ Next-gen family in business: groomed and capable?
□ Professional management: strong independent C-suite alongside promoter?
□ Has company scaled despite promoter's limited time? (Institutional processes)

SECOND-GENERATION PROMOTER:
Strengths:
+ Often better educated (MBA/CA); more investor-friendly
+ Comfortable with governance, analyst meetings, disclosure
+ May bring fresh strategy (expansion, diversification, tech adoption)
Risks:
− May not have founder's hustle or cost-consciousness
− Rapid business changes post-succession: strategy risk
− Family disputes in transition: multiple heirs with different agendas
− May prioritise lifestyle over reinvestment

Assessment:
□ Has second-gen maintained ROCE at founder levels?
□ Has business vision changed significantly? For better or worse?
□ Any inter-family dispute signals (company splits, asset transfers)?
□ Did second-gen take over in crisis or in growth phase?

PROFESSIONAL MANAGEMENT (Non-promoter CEO):
Strengths:
+ Institutional accountability (board can fire them)
+ ESOP-aligned incentives
+ Corporate governance culture
Risks:
− May prioritise short-term earnings over long-term investment
− High turnover can disrupt strategy
− Less conviction than promoter-owned business in downturn

BEST COMBINATION FOR MICROCAP: Founding promoter actively involved +
professional CFO + independent board + clear family succession plan
```

## Analysis Module 4 — Liquidity and Trading Assessment

### Step 4.1 — Market Liquidity
```
Liquidity Thresholds:
□ Average daily volume (30-day): > ₹1 Cr for meaningful liquidity
□ Average daily volume (30-day): > ₹5 Cr for comfortable trading
□ Market impact: position size / 30-day ADV: should not exceed 20%
   Example: Want to buy ₹20 lakh → ADV should be ₹1 Cr+

Float (Free Float) Assessment:
□ Promoter holding + strategic holding vs. total shares
□ Free float: shares available for trading
□ Low free float (<20%) = easy to manipulate
□ Operator stocks: rising on very low volumes with no fundamental reason = manipulation

Circuit Breaker Risk:
□ Microcaps frequently hit upper or lower circuit (5–10% limit)
□ Exit during crisis may take days or weeks (circuit breakers)
□ Never size position beyond your ability to hold through illiquidity
```

### Step 4.2 — Operator vs. Fundamental Price Action
```
Warning Signs of Operator-Driven Stocks:
⚠️ Stock up 100–300% in 6 months with no disclosed financial improvement
⚠️ Volume spike 10x+ on no news
⚠️ Multiple WhatsApp/Telegram "tips" about this specific stock
⚠️ Sudden change from boring IR communications to aggressive investor relations
⚠️ Large retail interest spike without institutional interest
⚠️ Promoter selling into the rally

Healthy Fundamental Price Action:
✅ Price up after strong quarterly results
✅ Price up after institutional investor buying (FII/DII entry in filing)
✅ Price up after contract/order announcement
✅ Price recovery after broad market selloff (fundamental buyers using opportunity)
```

---

## Analysis Module 4A — Operator Pump-and-Dump Pattern Recognition

```
Operator Activity is endemic in Indian microcaps. Recognise it to avoid being the exit.

Classic Pump Phase Signs:
□ Price rises 80–200% in 4–8 weeks with no disclosed fundamental catalyst
□ Volume spikes 5–20x average WITHOUT institutional buying in shareholding data
□ BSE/NSE circular about surveillance (ASM/GSM lists): CHECK IMMEDIATELY
   → ASM (Additional Surveillance Measure): price + volume based
   → GSM (Graded Surveillance Measure): earnings quality based
   → Company on GSM Stage 3/4/5: DO NOT INVEST
□ WhatsApp/Telegram circuits: company name starts appearing in "multibagger" groups
□ Social media suddenly discovers a 10-year-old company that "nobody knows"
□ Sudden shift to aggressive, retail-targeted investor relations without history
□ Story perfectly fits a trending theme: suddenly company is "EV play" / "defence play"
   without product disclosure to support it

Distribution Phase Signs:
□ Promoter/director selling quietly in multiple small tranches
□ "Promoter buying" disclosed but stock price not moving up on the news
□ Institutional buying reported but same institutions quietly exiting in next quarter
□ Volume suddenly drops sharply after 4–6 months of high volume = operator exiting
□ PR articles appearing in financial media with no analyst backing the story
□ Management starts giving vague "big announcement coming" without specifics

Dump Phase Signs:
□ Stock falls 30–60% on no news (operator exit complete)
□ Shareholding changes: FIIs exited | Retail holding exploded (retail = operator exit)
□ Company goes quiet: no concalls, no presentations
□ Promoter selling disclosed retrospectively

Protection Protocol:
→ NEVER buy on price momentum alone in microcaps
→ ALWAYS check if stock is on ASM/GSM list BEFORE any analysis
→ If retail shareholding > 40%: be cautious (high retail = late stage of pump)
→ Institutional entry from known quality fund is the BEST validation against operators
→ If you cannot find a single buy-side fund owning the stock: RED FLAG
```

## Analysis Module 5 — Institutional and Analyst Coverage

### Step 5.1 — Institutional Interest as Validation Signal
```
Institutional Holding Trajectory:
□ Has any mutual fund taken a position in last 4 quarters?
□ Is FII / DII holding increasing from zero base? (Validation signal)
□ Respected investor or PMS entering: qualitative positive signal
□ But: institutional interest ≠ fundamental quality — do independent analysis

Microcap Fund Ownership:
→ Presence in microcap/smallcap fund portfolio = another set of eyes
→ But: never rely solely on this; fund may be wrong or have different risk tolerance

Research Coverage:
→ If covered by credible independent research firm: use as data point
→ If covered ONLY by brokers with equity underwriting relationship: discount heavily
→ No coverage: common for microcaps; do not penalise if fundamentals are good
```

### Step 5.2 — Management Accessibility and Communication Quality
```
Quality of Investor Communication:
□ Do they hold quarterly concalls? (Positive for microcap)
□ Is the MD available for investor meetings?
□ Do they provide detailed investor presentations?
□ Have they attended and presented at investor conferences?
□ Are their disclosures on BSE/NSE timely and complete?

Communication Red Flags:
⚠️ No concall, no investor presentation, minimal disclosures
⚠️ MD refuses to discuss specific financial line items
⚠️ Vague answers to specific financial questions
⚠️ Sudden PR push without corresponding financial improvement
⚠️ Discrepancy between what management says and what financials show
```

---

## Analysis Module 6 — Position Sizing Discipline

### Step 6.1 — Microcap Position Sizing Rules
```
Portfolio Allocation Rules:
□ Single microcap position: Maximum 3–5% of total portfolio
□ Total microcap allocation: Maximum 15–20% of total portfolio
□ Entry in tranches: Never full position at once (cost averaging on illiquid stocks)

Entry Strategy:
→ Phase 1: 1/3rd position at initial thesis confirmation
→ Phase 2: 1/3rd position after first quarterly results confirm thesis
→ Phase 3: Final 1/3rd after 2nd positive quarterly results

Conviction Override:
→ Even at highest conviction, maximum 7% in single microcap
→ Position concentration in illiquid stock = permanent loss risk

Hold Period:
→ Microcap minimum hold: 2–3 years (thesis needs time to play out)
→ Do not exit because of short-term volatility
→ DO exit if any of the governance flags are confirmed
```

### Step 6.2 — Exit Triggers (Mandatory Action)
```
Immediate Exit (Within 1 Month):
❗ Auditor resignation unexplained
❗ Promoter arrested or named in FIR
❗ SEBI enforcement action against company
❗ Large related party transaction without board approval
❗ Unexplained management exodus (CFO + CEO leaving)

Exit Within 1 Quarter:
⚠️ Revenue declining >20% without disclosed reason
⚠️ Promoter selling >5% stake without public explanation
⚠️ Major customer (>20% of revenue) not renewing / switching
⚠️ Working capital blowing out (receivables >2x revenue/4)
⚠️ Cash balance falling rapidly without CapEx or debt repayment explanation
```

---

## Microcap Valuation Approach

```
Primary Method: P/E on Forward Earnings
  → Use conservative forward earnings (base case, not bull case)
  → Apply microcap discount to peer valuation: 20–30% discount
  → Benchmark P/E to listed peers in same segment

PEG Ratio:
  → PEG < 0.75 = significantly undervalued for growing business
  → PEG < 1.0 = reasonably valued
  → PEG > 1.5 = fully priced; illiquidity premium not justified

EV/EBITDA:
  → Microcap with strong growth: 10–18x EBITDA
  → Stable microcap: 7–12x EBITDA
  → Distressed microcap: <7x (but governance risk premium required)

Market Cap to Revenue:
  → Quality microcap: 1–3x Revenue
  → Great quality microcap: 3–5x Revenue
  → >5x Revenue for microcap: justified only with extraordinary growth evidence

Intrinsic Value Safety Net:
  → Never pay more than 15x normalised PE for a microcap with any governance concern
  → Illiquidity discount: deduct 15–20% from peer valuation
```

---

## Red Flag Summary — Microcap

### Disqualifying Flags (Immediate Eliminate)
```
❗ Any SEBI enforcement action (even historical, investigate thoroughly)
❗ Promoter pledge > 0% of promoter holding
❗ Unknown/suspicious auditor for company with revenue > ₹100 Cr
❗ Related-party ICDs given to promoter entities
❗ Cash in books not earning any interest income
❗ Any NCLT or insolvency filing against promoter's other companies
❗ Stock rising 200%+ in 6 months with no fundamental explanation
```

### HIGH Flags (Deep Investigation Required)
```
⚠️ OCF/PAT < 50% for 2+ years
⚠️ No institutional ownership at all (not even token MF position)
⚠️ Promoter selling in open market
⚠️ Debt/Equity > 1.5x
⚠️ Revenue concentration: single customer >40%
⚠️ No concall, no investor presentation, bare minimum disclosures
⚠️ Employee cost surprisingly low for stated headcount
⚠️ High other income as % of PAT (>30%)
```

---

## Microcap Analysis Output Format

```
MICROCAP RESEARCH ANALYSIS
Company: [Name] | Market Cap: ₹[X]Cr | Sector: [Sector]
Ticker: [NSE/BSE] | CMP: ₹[X] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

GOVERNANCE GATE (Must Pass Before Proceeding):
  Promoter Check:       [CLEAN / CONCERN / DISQUALIFY]
    Holding: [%] | Pledge: [%] | Trend: [Buying/Stable/Selling]
  Auditor Check:        [Big 4 / Mid-tier / Unknown — Assessment]
  SEBI Clean:           [YES / NO — details if NO]
  Related Party:        [Clean / Concerns — details]
  Board Quality:        [Strong / Adequate / Weak]
  GOVERNANCE VERDICT:   [PASS / CONDITIONAL / DISQUALIFY]

BUSINESS QUALITY:
  Business Clarity:     [3-sentence description]
  Niche Leadership:     [YES (evidence) / NO / UNCLEAR]
  Moat:                 [Type of competitive advantage]
  Market Size vs. Co:   [Addressable market vs. company revenue]

FINANCIAL QUALITY:
  Revenue CAGR 3yr:     [%] | PAT CAGR 3yr: [%]
  OCF/PAT:              [%] → [Quality assessment]
  ROCE:                 [%]
  Debt/Equity:          [X]x
  Promoter Pledge:      [0% / X%]

LIQUIDITY:
  Market Cap:           ₹[X]Cr
  30-day ADV:           ₹[X]Cr → [Adequate / Illiquid]
  Float:                [%]
  Institutional Interest:[FII/MF holding — trend]

CRITICAL FLAGS:         [Count + list]
HIGH FLAGS:             [Count + list]

VALUATION:
  P/E (Forward):        [X]x | Peer P/E: [X]x | Microcap discount: [%]
  PEG:                  [X]
  Market Cap/Revenue:   [X]x
  Verdict:              [Attractive/Fair/Expensive]

OVERALL VERDICT:
  Governance Gate:      [PASS / FAIL]
  Investment Case:      [STRONG BUY / BUY / WATCH / AVOID]
  Suggested Allocation: [% of portfolio — maximum]
  Entry Strategy:       [Tranche 1: ₹X at ₹Y | Tranche 2 trigger: [event]]
  Exit Triggers:        [Non-negotiable exit signals]
  Monitoring:           [What to watch every quarter]
```

---

*Skill Version v_0.0 | IERL Specialist Skill Library | Microcap Research*
*Integrates with: Forensic Accounting Skill, Skill 01 (Master Research), Skill 15 (Pre-Investment Checklist)*
*Special Note: Always apply the Forensic Accounting Skill with MAXIMUM scrutiny for microcaps.*

## 30. Skill 16 — Screener.in Query Integration & Saved Screens Library

**Version:** v_0.0 | **Purpose:** Validate, store, name, and execute screener.in-style filter queries as permanent, reusable IERL skills.

### Why This Skill Exists

You have exactly one screening data source: **screener.in's custom query filters**. That means two things the rest of this document never states explicitly:

1. **Claude may only reference a metric in a screen if it exists, by exact name, in the Master Field List below.** If a skill's criterion has no matching field, that criterion cannot be screened — it must be flagged as a manual/qualitative overlay applied *after* the screen returns results, not silently invented or approximated.
2. **Every filter query you paste is a durable asset**, not a one-off. It should be captured once, named, validated, and reusable by name forever after ("run my Capex Breakout Compounder screen") rather than re-explained each time.

This skill governs both, and its Master Field List constrains the screenable criteria referenced throughout Skills 02, 04, 09, and 11 above to what screener.in can actually filter on.

### Triggers
- User pastes a filter query in screener.in syntax (`AND`, `OR`, field comparisons)
- "Add this as a skill"
- "Save this screen as [Name]"
- "Run my [Name] screen"
- "Update the [Name] screen with [new condition]"

### Pre-Flight Requirements
```
□ Query text provided (raw filter conditions)
□ Proposed name for the screen (ask if not given — do not auto-name silently)
□ Category tag: Multibagger / Swing / Positional / Turnaround / Risk-Screen / Custom
□ Which downstream skill should results chain into? (default mapping in Section 5)
```

### Activation Sequence

```
① FIELD VALIDATION (Mandatory — runs before anything else)
   → Parse every field name referenced in the pasted query
   → Cross-check each one against the Master Field List (Section 2)
   → For each field, one of three outcomes:
        ✅ VALID — exact match found, proceed
        ⚠️ NEAR-MATCH — likely typo or alias (e.g. "ROCE" → "Return on Capital
           Employed") — confirm the mapping explicitly, do not silently assume
        ❌ NOT AVAILABLE — no equivalent field exists on screener.in
           → Flag it. Do NOT drop it silently and do NOT invent a proxy without
             saying so. State: "This condition cannot be screened on screener.in;
             recommend applying manually after the screen returns results."
   → A query is only "clean" once every field is ✅ or explicitly resolved as ⚠️/❌

② LOGICAL STRUCTURE CHECK
   → Confirm AND/OR nesting is unambiguous (screener.in evaluates left to right
     within a single query box; flag any condition that needs parentheses
     screener.in doesn't support, and restructure or split into two screens)
   → Confirm units are consistent with screener.in's own defaults (e.g. Market
     Capitalization and Debt are in ₹ Cr; ratios are unitless; growth/return
     figures are %)

③ CLASSIFICATION & NAMING
   → Assign Category tag (see Section 4 taxonomy)
   → Assign a short, memorable Screen Name (title case, no special characters)
   → Assign a Screen ID (sequential: SCR-001, SCR-002, ...)

④ REGISTRATION (Saved Screens Library entry)
   → Store using the exact template in Section 3
   → Record: date added, field validation result, chain target skill

⑤ EXECUTION HAND-OFF
   → State clearly that Claude cannot query screener.in live (no API/browser
     access to screener.in's authenticated custom-screen backend) — the user
     runs the query on screener.in and pastes back the resulting stock list
     (ticker + key columns), OR uploads the exported CSV
   → Once results are pasted/uploaded, Claude applies any ❌ NOT AVAILABLE
     manual-overlay conditions from Step ① before finalizing the shortlist
   → Chain the finalized shortlist into the mapped downstream skill
     (Section 5) for deep-dive analysis — never end at a raw ticker list
     if a deeper skill applies
```

### Output Format (on registering a new screen)

```
SCREEN REGISTERED
═══════════════════════════════════════════════════
Screen ID:        SCR-[NNN]
Name:              [Name]
Category:          [Multibagger / Swing / Positional / Turnaround / Risk / Custom]
Date Added:        [DD/MM/YYYY]

FIELD VALIDATION RESULT:
  ✅ Valid fields:        [count] — [list]
  ⚠️ Near-match resolved: [count] — [original → resolved field]
  ❌ Not screenable:      [count] — [field/condition] → [manual overlay note]

FINAL QUERY (screener.in-ready):
[clean query block, only ✅/resolved-⚠️ fields, ❌ items removed with a
 footnote listing what to check manually]

CHAINS TO:          [Downstream skill for shortlist deep-dive]
MANUAL OVERLAY CHECKLIST (apply after results returned):
  □ [❌ item 1]
  □ [❌ item 2]
═══════════════════════════════════════════════════
```

### Rules (Non-Negotiable)
- Never present a query as "ready to run" if it contains unresolved ❌ fields without a manual overlay note attached.
- Never silently rename or "improve" a user's threshold values (e.g. changing `ROCE > 18` to `ROCE > 15`) — only field *names* are validated/mapped, not the user's chosen thresholds.
- Every registered screen must state which downstream skill its results feed into — a screen is a filter, not an endpoint.
- Claude cannot execute screener.in queries directly (no live access) — always state this rather than implying real-time execution.

---

### Master Field List (Approved Screenable Fields)

Only fields in this list may be referenced in a screener.in query. This is the exact set from your screener.in Custom Query filter panel — organized by category for lookup speed.

**Core Fundamentals:** Sales, OPM, Profit after Tax, Market Capitalization, Sales Latest Quarter, Profit after Tax Latest Quarter, YOY Quarterly Sales Growth, YOY Quarterly Profit Growth, Price to Earning, Dividend Yield, Price to Book Value, Return on Capital Employed, Return on Assets, Debt to Equity, Return on Equity, EPS, Debt, Promoter Holding, Change in Promoter Holding, Earnings Yield, Pledged Percentage, Industry PE, Sales Growth, Profit Growth, Current Price, Price to Sales, Price to Free Cash Flow, EV/EBITDA, Enterprise Value, Current Ratio, Interest Coverage Ratio, PEG Ratio, Return over 3 Months, Return over 6 Months, Return over 1 Year, Return over 3 Years, Return over 5 Years, Return over 7 Years, Return over 10 Years

**Growth Metrics:** Sales Growth 3Years, Sales Growth 5Years, Sales Growth 7Years, Sales Growth 10Years, Sales Growth 5Years Median, Sales Growth 10Years Median, Profit Growth 3Years, Profit Growth 5Years, Profit Growth 7Years, Profit Growth 10Years, EBITDA Growth 3Years, EBITDA Growth 5Years, EBITDA Growth 7Years, EBITDA Growth 10Years, EPS Growth 3Years, EPS Growth 5Years, EPS Growth 7Years, EPS Growth 10Years, Operating Profit Growth

**Profitability Metrics:** Average Return on Equity 3Years, Average Return on Equity 5Years, Average Return on Equity 7Years, Average Return on Equity 10Years, Average Return on Capital Employed 3Years, Average Return on Capital Employed 5Years, Average Return on Capital Employed 7Years, Average Return on Capital Employed 10Years, Return on Equity 5Years Growth, Return on Assets 3Years, Return on Assets 5Years, OPM 5Year, OPM 10Year, Average Earnings 5Year, Average Earnings 10Year, Average EBIT 5Year, Average EBIT 10Year

**Annual P&L Metrics:** Sales Last Year, Operating Profit Last Year, Other Income Last Year, EBITDA Last Year, Depreciation Last Year, EBIT Last Year, Interest Last Year, Profit Before Tax Last Year, Tax Last Year, Profit After Tax Last Year, Extraordinary Items Last Year, Net Profit Last Year, Dividend Last Year, Material Cost Last Year, Employee Cost Last Year, OPM Last Year, NPM Last Year, EPS Last Year

**Quarterly Metrics:** Operating Profit Latest Quarter, Other Income Latest Quarter, EBITDA Latest Quarter, Depreciation Latest Quarter, EBIT Latest Quarter, Interest Latest Quarter, Profit Before Tax Latest Quarter, Tax Latest Quarter, Extraordinary Items Latest Quarter, Net Profit Latest Quarter, GPM Latest Quarter, OPM Latest Quarter, NPM Latest Quarter, Equity Capital Latest Quarter, EPS Latest Quarter, Sales 2Quarters Back, Sales 3Quarters Back, Operating Profit 2Quarters Back, Operating Profit 3Quarters Back, Net Profit 2Quarters Back, Net Profit 3Quarters Back

**Previous Quarter Metrics:** Sales Preceding Quarter, Operating Profit Preceding Quarter, Other Income Preceding Quarter, EBITDA Preceding Quarter, Depreciation Preceding Quarter, EBIT Preceding Quarter, Interest Preceding Quarter, Profit Before Tax Preceding Quarter, Tax Preceding Quarter, Profit After Tax Preceding Quarter, Extraordinary Items Preceding Quarter, Net Profit Preceding Quarter, OPM Preceding Quarter, NPM Preceding Quarter, Equity Capital Preceding Quarter, EPS Preceding Quarter

**Previous Year Quarter Metrics:** Sales Preceding Year Quarter, Operating Profit Preceding Year Quarter, Other Income Preceding Year Quarter, EBITDA Preceding Year Quarter, Depreciation Preceding Year Quarter, EBIT Preceding Year Quarter, Interest Preceding Year Quarter, Profit Before Tax Preceding Year Quarter, Tax Preceding Year Quarter, Profit After Tax Preceding Year Quarter, Extraordinary Items Preceding Year Quarter, Net Profit Preceding Year Quarter, OPM Preceding Year Quarter, NPM Preceding Year Quarter, Equity Capital Preceding Year Quarter, EPS Preceding Year Quarter

**Balance Sheet Metrics:** Equity Capital, Preference Capital, Reserves, Secured Loan, Unsecured Loan, Balance Sheet Total, Gross Block, Revaluation Reserve, Accumulated Depreciation, Net Block, Capital Work in Progress, Investments, Current Assets, Current Liabilities, Book Value of Unquoted Investments, Market Value of Quoted Investments, Contingent Liabilities, Total Assets, Working Capital, Lease Liabilities, Inventory, Trade Receivables, Face Value, Cash Equivalents, Advance from Customers, Trade Payables

**Historical Balance Sheet Metrics:** Debt 3Years Back, Debt 5Years Back, Debt 7Years Back, Debt 10Years Back, Working Capital 3Years Back, Working Capital 5Years Back, Working Capital 7Years Back, Working Capital 10Years Back, Net Block 3Years Back, Net Block 5Years Back, Net Block 7Years Back, Gross Block Preceding Year, Net Block Preceding Year, Capital Work in Progress Preceding Year, Working Capital Preceding Year, Debt Preceding Year, Number of Equity Shares Preceding Year

**Cash Flow Metrics:** Cash from Operations Last Year, Free Cash Flow Last Year, Cash from Investing Last Year, Cash from Financing Last Year, Net Cash Flow Last Year, Cash Beginning of Last Year, Cash End of Last Year, Free Cash Flow Preceding Year, Cash from Operations Preceding Year, Cash from Investing Preceding Year, Cash from Financing Preceding Year, Net Cash Flow Preceding Year, Cash Beginning of Preceding Year, Cash End of Preceding Year, Free Cash Flow 3Years, Free Cash Flow 5Years, Free Cash Flow 7Years, Free Cash Flow 10Years, Operating Cash Flow 3Years, Operating Cash Flow 5Years, Operating Cash Flow 7Years, Operating Cash Flow 10Years, Investing Cash Flow 3Years, Investing Cash Flow 5Years, Investing Cash Flow 7Years, Investing Cash Flow 10Years, Cash 3Years Back, Cash 5Years Back, Cash 7Years Back

**Valuation Metrics:** Book Value, Book Value 3Years Back, Book Value 5Years Back, Book Value 10Years Back, Book Value Preceding Year, Industry PBV, Historical PE 3Years, Historical PE 5Years, Historical PE 7Years, Historical PE 10Years, Graham Number, Earning Power

**Ownership Metrics:** FII Holding, Change in FII Holding, Change in FII Holding 3Years, DII Holding, Change in DII Holding, Change in DII Holding 3Years, Public Holding, Unpledged Promoter Holding, Number of Shareholders, Number of Shareholders Preceding Quarter, Number of Shareholders 1Year Back

**Efficiency Metrics:** Inventory Turnover Ratio, Inventory Turnover Ratio 3Years Back, Inventory Turnover Ratio 5Years Back, Inventory Turnover Ratio 7Years Back, Inventory Turnover Ratio 10Years Back, Asset Turnover Ratio, Debtor Days, Debtor Days 3Years Back, Debtor Days 5Years Back, Average Debtor Days 3Years, Working Capital Days, Average Working Capital Days 3Years, Cash Conversion Cycle, Days Payable Outstanding, Days Receivable Outstanding, Days Inventory Outstanding

**Advanced Quality Metrics:** Piotroski Score, G Factor, Financial Leverage, Return on Invested Capital, Credit Rating, Exports Percentage, Exports Percentage 3Years Back, Exports Percentage 5Years Back

**Technical Metrics:** Volume, Volume 1Week Average, Volume 1Month Average, Volume 1Year Average, High Price, Low Price, High Price All Time, Low Price All Time, Return over 1Day, Return over 1Week, Return over 1Month, DMA 50, DMA 200, DMA 50 Previous Day, DMA 200 Previous Day, RSI, MACD, MACD Previous Day, MACD Signal, MACD Signal Previous Day

**Forecast Metrics:** Expected Quarterly Sales Growth, Expected Quarterly Sales, Expected Quarterly Operating Profit, Expected Quarterly Net Profit, Expected Quarterly EPS

**Dates:** TTM Result Date, Last Annual Result Date, Last Result Date

**SME Filters:** Is SME, Is Not SME

**⚠️ Notable absences (cannot be screened — must be manual overlay):** Concall tone/quality, management guidance-delivery track record, moat type/durability, TAM size, related-party transaction detail, SEBI enforcement status, board independence quality, capital allocation judgment, brand/switching-cost evidence, seasonal-business flag. These appear as qualitative gates in Skills 01, 04, 09, and 15 — they must be applied *after* a screener.in list is returned, never assumed to be pre-filterable.

---

### Saved Screen Template (use for every new screen you add)

```
### Saved Screen: [Name]
Screen ID:        SCR-[NNN]
Category:         [Multibagger / Swing / Positional / Turnaround / Risk-Screen / Custom]
Added:            [DD/MM/YYYY]
Trigger Phrases:  ["run my [Name] screen", "..."]

Query (screener.in-ready):
[query block — AND/OR conditions, only validated field names]

Field Validation Notes:
  ⚠️ Resolved:  [any near-matches and what they were mapped to]
  ❌ Excluded:  [any condition removed because no field exists — with the
                manual-overlay note explaining how to check it post-screen]

Chains To:        [Skill 01 / Skill 04 / Skill 15 / etc.]
```

To add a future filter set: paste the raw query as-is (exactly like you did with the multibagger example below) and tell Claude the name you want it saved under. Claude runs the Section 1 Activation Sequence and returns a registered entry in this format — no need to reformat anything yourself first.

---

### Screen Category Taxonomy

| Category | Typical Horizon | Chains To |
|---|---|---|
| Multibagger | 3–10 years | Skill 04 (deep dive) → Skill 15 (pre-investment gate) |
| Swing | 5–30 days | Skill 02 (technical + liquidity overlay) |
| Positional | 3–6 months | Skill 03 (catalyst classification) |
| Turnaround | 6–24 months | Skill 11 (stage assessment) |
| Risk-Screen | Ongoing | Skill 09 (portfolio risk audit) |
| Custom | User-defined | User-specified, default Skill 01 |

---

### Screen → Skill Hand-off Map (fills the gap in the Skill Chaining Map, Section 3)

```
SCREENING CHAIN (new):
  Skill 16 (Query Validation & Screen Run)
      → Raw shortlist returned by user from screener.in
      → Manual Overlay Checklist applied (❌ fields from Section 2)
      → Chains into category-matched deep-dive skill:
           Multibagger screen  → Skill 04 → Skill 15
           Swing screen        → Skill 02
           Positional screen   → Skill 03
           Turnaround screen   → Skill 11
           Risk screen         → Skill 09 → Skill 06
```

---

### Worked Example — Your Pasted Query, Registered

```
SCREEN REGISTERED
═══════════════════════════════════════════════════
Screen ID:        SCR-001
Name:              Capex Breakout Compounder
Category:          Multibagger
Date Added:        20/07/2026

FIELD VALIDATION RESULT:
  ✅ Valid fields (13):
     Market Capitalization, Return on Capital Employed, Return on Equity,
     Sales Growth 5Years, Profit Growth 5Years, EPS Growth 5Years, EPS,
     Average Return on Capital Employed 3Years, Promoter Holding,
     Debt to Equity, Interest Coverage Ratio, Free Cash Flow 3Years* ,
     Cash from Operations 3Years*, PEG Ratio, Net Block, Capital Work in
     Progress, Net Block Preceding Year, Capital Work in Progress
     Preceding Year, Volume 1Week Average, Volume 1Year Average

  ⚠️ Near-match resolved (3):
     "ROCE3yr avg" → Average Return on Capital Employed 3Years
     "Free cash flow 3Years" → Free Cash Flow 3Years (exact match, confirmed)
     "Cash from operations 3Years" → Operating Cash Flow 3Years (screener.in's
        exact label for this metric is "Operating Cash Flow", not "Cash from
        Operations" for the multi-year field — confirm before running)

  ❌ Not screenable (0):
     None — every condition in this query maps cleanly to the Master Field
     List. This is a well-formed screener.in query as originally written.

FINAL QUERY (screener.in-ready):
Market Capitalization < 5000
AND Return on Capital Employed > 18
AND Return on Equity > 18
AND Sales Growth 5Years > 15
AND Profit Growth 5Years > 15
AND EPS Growth 5Years >= Sales Growth 5Years
AND EPS Growth 5Years >= Profit Growth 5Years
AND EPS > 12
AND Average Return on Capital Employed 3Years > 15
AND Promoter Holding > 40
AND Debt to Equity < 0.5
AND Interest Coverage Ratio > 5
AND (Free Cash Flow 3Years > 0 OR Operating Cash Flow 3Years > 0)
AND PEG Ratio < 1
AND (Net Block + Capital Work in Progress) > 2 * (Net Block Preceding Year + Capital Work in Progress Preceding Year)
AND Volume 1Week Average > Volume 1Year Average * 2

CHAINS TO:          Skill 04 (Early Multibagger Finder) → Stage Gate
                     Assessment → Skill 15 (Pre-Investment Master Checklist)
                     before any capital commitment

MANUAL OVERLAY CHECKLIST (apply after results returned — none of these are
screenable, per Section 2's notable absences):
  □ Moat evidence (pricing power, stickiness, cost advantage) — Skill 04 Gate
  □ Management capital allocation track record — Skill 04 Gate
  □ Promoter background / no criminal proceedings — Skill 04 Gate
  □ TAM size and penetration gap — Skill 04 Gate
  □ Governance: no active SEBI enforcement action — Skill 15 Gate 2
═══════════════════════════════════════════════════
```

This screen is a strong design: the capex-doubling condition (Net Block + CWIP more than doubling YoY) combined with the volume-surge condition (1-week average > 2× 1-year average) is a genuinely distinctive combination — it's looking for companies mid-expansion that the market hasn't fully priced in yet, which is exactly the "Capex Breakout" thesis. Nothing needed to be dropped or approximated.

Going forward: paste a query like this any time, tell me what to name it, and I'll run it through this same validation and register it — you don't need to reformat it into any particular style first.

---

---

*Document 04 of 16 | Version v_0.0 | Upload to Claude as a Knowledge File (single file — replaces all prior versions)*
*Improvements from V4.0: 9 new Sector Analyzer skills added (Skills 17–25) — Banking, NBFC, Insurance,
Pharmaceutical, Defence & Aerospace, Manufacturing & Capital Goods, Power & Utilities, Chemical, and
Microcap Research Protocol — each with mandatory sector-specific metrics, output templates, and hard
rules matching the depth of Skills 01–15. Sector Deep-Dive chain and sector-routing table added to the
Skill Chaining Map. Consolidated from a 26-skill catalog; 3 duplicate entries in that catalog were
resolved to avoid redundant skills.*
*Improvements from V2.0: 3 new skills (Concall Analyzer, Corporate Action Analyzer, Pre-Investment Checklist),
pre-flight requirements added to all skills, skill chaining map, failure protocol, stage assessments,
seasonal normalization, liquidity filters, BFSI branching, tax efficiency, turnaround staging,
IPO anchor analysis, GMP context, and watchlist staleness protocol.*
*Improvements from V3.0: Skill 16 added (Screener.in Query Integration & Saved Screens Library),
Master Field List constraining all screening criteria in this document to real screener.in fields,
Saved Screen template and naming convention, Screen Category Taxonomy, and a Screen → Skill hand-off
map closing the gap between raw screener output and deep-dive analysis (Skills 01, 02, 03, 04, 09, 11, 15).*

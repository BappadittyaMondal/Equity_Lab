<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Volume Delivery Analysis Skill  
> **Role:** Executable workflow skill  
> **Use when:** Use when the request matches this skill's method, then execute its stated gates and output format.  
> **Cognitive mode:** Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains.**
> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  


# AI Volume & Delivery Analysis Skill
**Version:** 1.0 | **Status:** Production Ready | **Last Updated:** July 2026
**Category:** Core Toolkit — Delivery %, Bulk/Block Deal, and Participation-Quality Analysis

---

## CRITICAL AI INSTRUCTION

Traded volume alone tells Claude how many shares changed hands — it says nothing about WHO was buying or whether the buying reflects genuine investment intent versus intraday churn. This skill exists specifically to go one layer deeper than the basic volume module in AI_Technical_Analysis_Master_Skill, using NSE/BSE delivery percentage, bulk/block deal disclosures, and shareholding pattern changes to distinguish real accumulation from noise. Claude must never treat a volume spike alone as an institutional accumulation signal — delivery percentage, and ideally a corroborating bulk/block deal or shareholding filing, is required before that specific claim is made.

---

## Purpose

Provide a dedicated toolkit for reading beneath headline traded volume — delivery percentage trends, bulk/block deal disclosures, and shareholding pattern changes — to assess whether price/volume action reflects genuine accumulation or distribution by informed participants, versus short-term speculative or intraday-driven volume that carries much lower signal value.

---

## Pre-Flight Requirements

```
□ Daily delivery volume and delivery percentage data (NSE/BSE disclose this
  separately from total traded volume — total volume includes intraday
  trades that are squared off same-day and never actually change ownership)
□ Bulk deal and block deal disclosures for the relevant period (exchange-
  mandated disclosures for large single transactions above threshold size)
□ Latest available shareholding pattern (quarterly disclosure) showing FII,
  DII, and public shareholding changes
□ Historical baseline: 20-day and 90-day average delivery % for the stock,
  to judge whether a current reading is unusual for THIS specific stock
  (delivery % baselines vary widely stock-to-stock and must never be
  compared against a fixed universal threshold alone)
```

---

## Analysis Module 1 — Delivery Percentage Analysis

```
WHAT IT MEASURES: Delivery % = (Shares actually transferred to demat
accounts / Total shares traded) × 100. A trade that is bought and sold
within the same day (intraday) is NOT delivered and does not count —
so delivery % is a proxy for how much of the day's volume reflects
genuine, held positions versus short-term trading churn.

INTERPRETATION (Always Relative to the Stock's OWN Baseline, Never a
Fixed Universal Number):
  Delivery % meaningfully ABOVE its 20/90-day average, on a day of price
  strength AND above-average total volume → Strongest combination — genuine
    accumulation signal, materially more informative than volume alone
  Delivery % meaningfully ABOVE its own average, on a day of price weakness
    → Genuine distribution/selling signal — informed participants exiting,
    a more urgent bearish signal than a price decline on low delivery %
  Delivery % BELOW its own average despite a large total volume/price move
    → The move is being driven primarily by intraday/speculative activity
    — lower-confidence signal, treat any accompanying technical breakout
    (per AI_Technical_Analysis_Master_Skill) as UNCONFIRMED until delivery
    % catches up or a retest with higher delivery volume occurs

MANDATORY PAIRING: Delivery % must always be stated alongside (a) the
stock's own historical baseline for comparison and (b) the direction of
price on that session — a delivery % figure without both of these is not
interpretable and should not be presented as a signal.
```

---

## Analysis Module 2 — Bulk & Block Deal Analysis

```
BULK DEALS: Single transactions ≥0.5% of a company's total equity in a
  day, disclosed by the exchange with buyer/seller identity (for
  registered categories) and price.
BLOCK DEALS: Large single trades executed through a separate block
  window, typically institutional, above a higher minimum threshold.

INTERPRETATION:
  □ Identify WHO is on each side where disclosed — a promoter entity, a
    known institutional investor (mutual fund, FII/FPI, insurance company),
    or an unidentified/individual counterparty — the信号 value differs
    materially by category
  □ Price relative to prevailing market price: a bulk/block deal at a
    PREMIUM to the current market price is a stronger positive signal
    (buyer paid up for size/urgency) than one executed at a discount
    (seller accepted a lower price to exit size quickly — can reflect
    either liquidity need or lower conviction from the seller)
  □ Repeated bulk deals from the SAME buyer category over successive
    sessions/weeks → Building conviction signal — a pattern is more
    informative than a single isolated deal
  □ Promoter-side bulk/block SELLING must be cross-checked against the
    Governance module in Skill 01 and the Turnaround Skill's Signal vs
    Trap checklist — promoter selling during a period the company is
    also presenting a growth or recovery narrative is a specific red
    flag combination that must be flagged explicitly, not reported as a
    neutral data point
  □ A single bulk deal, in isolation, without corroborating price/delivery
    trend (Module 1) or subsequent shareholding filing confirmation
    (Module 3), should be treated as a data point to monitor, not yet a
    standalone actionable signal
```

---

## Analysis Module 3 — Shareholding Pattern Change Analysis

```
Quarterly shareholding disclosures are the lowest-frequency but highest-
confirmation-value data source in this skill — they show actual position
changes by category, not inferred from trading activity.

□ FII/FPI holding: quarter-on-quarter change, in both percentage points
  and, where derivable, approximate share count
□ DII (domestic institutional — mutual funds, insurance, banks) holding:
  same tracking
□ Promoter holding: any change at all warrants explicit comment — even a
  small reduction should be investigated for reason (pledge-related
  forced sale, OFS participation, estate/succession-related transfer,
  or open-market sale) rather than assumed to be routine
□ Public/retail holding: a rising retail share alongside falling
  institutional share (or vice versa) is itself informative about who is
  driving recent price action, and should be stated explicitly

CROSS-CHECK AGAINST MODULES 1 & 2:
  □ Did FII/DII holding increase in a quarter that also showed elevated
    delivery % and bulk/block deals from institutional counterparties?
    → Corroborated signal, materially higher confidence than any single
      data source alone
  □ Did delivery % or bulk-deal activity suggest accumulation, but the
    subsequent shareholding filing showed NO corresponding increase in
    FII/DII holding? → The apparent accumulation may have been from a
    category not separately disclosed (e.g., domestic HNI/family office
    activity, or accumulation that occurred and partially reversed within
    the same quarter) — state this explicitly as an unresolved data point
    rather than forcing a conclusion the data doesn't fully support
```

---

## Analysis Module 4 — Pledge-Triggered Forced-Selling Cross-Check (Upgrade — Previously Missing)

```
Bulk/block promoter selling was previously flagged generically — add the
specific, higher-severity sub-case:

□ Cross-check any promoter bulk/block sale against DISCLOSED PLEDGE LEVEL
  at the most recent filing — a sale from a heavily-pledged promoter
  entity during a price decline is more likely to be a FORCED sale
  (lender invoking pledge/margin call) than a voluntary portfolio
  decision, and this distinction changes the interpretation materially:
  a forced sale is a mechanical liquidity event, not necessarily a
  conviction signal about the business, but it also frequently triggers
  further downside as the mechanism can repeat at lower prices
□ If pledge level is elevated (>25%) AND price has declined >20% from the
  pledge-creation price, treat this combination as a CRITICAL flag
  regardless of what the standalone bulk-deal read in Module 2 would
  otherwise suggest
```

## Red Flag Summary — Volume & Delivery Context

### CRITICAL Flags
```
❗ Promoter bulk/block selling during a period the company is presenting
  a growth, turnaround, or capacity-expansion narrative, without this
  being explicitly flagged and cross-referenced to Governance/Turnaround checks
❗ A "volume breakout" being reported as institutional accumulation with
  no delivery % or shareholding corroboration at all
❗ Delivery % compared against a fixed universal threshold rather than the
  stock's own historical baseline
```

### HIGH Flags
```
⚠️ Elevated total volume with delivery % below the stock's own baseline,
  on a reported "breakout" day — flagged as unconfirmed but the calling
  skill's output does not carry this caveat forward
⚠️ A single isolated bulk/block deal being treated as a standalone
  actionable signal without monitoring for repetition or corroboration
⚠️ Shareholding pattern data more than one quarter stale being used to
  support a current-period accumulation/distribution claim
```

---

## Output Format

```
VOLUME & DELIVERY ANALYSIS
Company: [Name] | Ticker: [NSE] | Date: [DD/MM/YYYY]
═══════════════════════════════════════════════════════════════════

DELIVERY PERCENTAGE:
  Current Session/Week Delivery %:  [X]%
  20-Day Baseline:                   [X]% | 90-Day Baseline: [X]%
  Reading vs. Baseline:               [Above/Below/In-line]
  Price Direction Same Session:        [Up/Down/Flat]
  Interpretation:                      [Genuine accumulation/distribution/
                                        Intraday-driven, unconfirmed]

BULK & BLOCK DEALS (Recent Period):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date | Buyer Category | Seller Category | Qty | Price vs Market | Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pattern Assessment:   [Repeated same-side activity / Isolated / None]
  Promoter-Side Activity: [None / Buying — positive / Selling — flag
                            cross-referenced to Governance & Turnaround checks]

SHAREHOLDING PATTERN CHANGE (Last Disclosed Quarter):
  FII/FPI:              [X]% → [Y]% ([+/-] pts)
  DII:                  [X]% → [Y]% ([+/-] pts)
  Promoter:              [X]% → [Y]% ([+/-] pts) — Reason if changed: [State
                          or "Not disclosed — investigate"]
  Public/Retail:          [X]% → [Y]% ([+/-] pts)

CROSS-CORROBORATION CHECK:
  Delivery/Bulk-Deal Signal vs. Shareholding Filing: [Corroborated /
    Unresolved — categories don't fully reconcile / Contradictory]

CRITICAL FLAGS: [List, or "None detected"]
HIGH FLAGS:      [List, or "None detected"]

OVERALL PARTICIPATION-QUALITY VERDICT: [High-confidence institutional
  accumulation / High-confidence distribution / Unconfirmed — insufficient
  corroboration / Neutral]

FEEDS INTO: [Which calling skill — Swing, Uptrend, Multibagger Discovery,
  Governance checks in Skill 01 — this reading supports]
```

---

## Rules (Non-Negotiable)

```
1. Delivery % is always compared against the stock's own historical
   baseline, never a fixed universal threshold.
2. A volume spike is never labeled "institutional accumulation" without
   delivery % and, where possible, bulk/block or shareholding corroboration.
3. Promoter-side bulk/block selling is always explicitly cross-referenced
   to the Governance Gate (Skill 01) and Turnaround Skill's Signal vs Trap
   checklist, never reported as a neutral data point alone.
4. A single isolated bulk/block deal is treated as a monitoring item, not
   a standalone actionable signal, until repeated or corroborated.
5. Shareholding pattern data is dated explicitly, and its staleness (time
   since last quarterly disclosure) is stated whenever used to support a
   current-period claim.
```

---

*Skill Version 1.0 | IERL Specialist Skill Library | Core Toolkit — Volume & Delivery Analysis*
*Integrates with: AI_Technical_Analysis_Master_Skill, AI_Swing_Trading_Skill, AI_Uptrend_Momentum_Stock_Skill,
Skill 01 (Master Research, Governance Gate), AI_Turnaround_Analysis_Skill, AI_Multibagger_Discovery_Skill*

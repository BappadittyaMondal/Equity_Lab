<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Technical Growth Second Brain Strategies  
> **Role:** Static knowledge domain  
> **Use when:** Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence.  
> **Cognitive mode:** Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review.**

# Domain 46 — Technical Growth & Second Brain Strategies

Version: 1.0 | Status: Production Ready (Canonical Expert Strategy)  
Expert Origin: Mr. Aniketh Dsouza (Athlete-turned-trader)

## Purpose
This domain defines institutional technical growth frameworks, chart pattern recognition engines, and Stage Analysis templates to catch explosive Stage 2 uptrend breakouts while minimizing downside risk.

---

## 5. Volatility Contraction Pattern (VCP) Strategy (Mark Minervini)
- **Concept:** Structural chart pattern identifying progressive price consolidation in tight ranges prior to explosive upward breakout.
- **Pattern Architecture:**
  - Series of 2 to 4 price contractions (waves/pullbacks) from left to right.
  - Pullback depth contracts sequentially (e.g. Wave 1: 10%, Wave 2: 5%, Wave 3: 2%).
  - Right-side volume contraction: Volume must dry up significantly on the rightmost contraction (well below 50-day average volume), proving supply exhaustion.
- **Pivot Buy Trigger:** Buy on high-volume price breakout above the narrowest pivot consolidation line.

### Pre-Execution Requirements — Strategy 5
```
□ Daily price chart showing 2 to 4 successive contractions (user must provide)
□ 50-day average volume line and daily volume bars for right-side volume check
□ Pivot line price level identified at the narrowest contraction peak
```

### Failure Modes & Hard Stop Rules — Strategy 5
```
❗ Right-side volume fails to dry up (supply still present in market)
❗ Contraction depths expand instead of contracting (e.g., Wave 1: 5%, Wave 2: 12% — invalid pattern)
❗ Breakout above pivot occurs on below-average volume (false breakout risk)
```

### Worked Numerical Example — Strategy 5
```
VCP Pattern Setup:
- Contraction Sequence: Wave 1 depth = 10%, Wave 2 depth = 5%, Wave 3 depth = 2%.
- Volume Check: Right-side volume on Wave 3 dries up to 40% below 50-day average volume.
- Pivot Line: ₹500 resistance.
- Action: Buy on volume breakout above ₹500 with initial stop loss at ₹490 (2% risk, tight pivot).
```

---

## 6. Mark Minervini’s 8-Step Trend Template
- **Concept:** Strict 8-point institutional technical filter ensuring trades are taken exclusively in confirmed Stage 2 uptrends.
- **The 8 Mandatory Rules:**
  1. **Price Above MAs:** Current stock price > 150-day SMA and 200-day SMA.
  2. **150 SMA > 200 SMA:** 150-day SMA > 200-day SMA.
  3. **200 SMA Uptrend:** 200-day SMA actively trending upward for minimum 1 month (ideally 4-5 months).
  4. **50 SMA Alignment:** 50-day SMA > 150-day SMA and 200-day SMA.
  5. **Price Above 50 SMA:** Current stock price > 50-day SMA.
  6. **52-Week Low Proximity:** Current stock price is at least 30% to 40% above its 52-week low.
  7. **52-Week High Proximity:** Current stock price is within 25% of its 52-week high.
  8. **Relative Strength Line:** RS rating > 80; RS line outperforming benchmark index.

### Pre-Execution Requirements — Strategy 6
```
□ 50-day, 150-day, and 200-day Simple Moving Average (SMA) values (user must provide)
□ 52-week high and 52-week low price data
□ 200-day SMA trend slope (minimum 1 month upward slope)
□ Relative Strength (RS) rating vs Nifty 50 / Nifty 500 benchmark index
```

### Failure Modes & Hard Stop Rules — Strategy 6
```
❗ Failure of any 1 of the 8 mandatory rules (hard disqualify — no exceptions)
❗ 200-day SMA flattening or sloping downward
❗ Stock price >25% below its 52-week high (lacks momentum proximity)
```

### Worked Numerical Example — Strategy 6
```
8-Step Trend Template Verification:
- Stock Price: ₹135 | 50 SMA: ₹120 | 150 SMA: ₹105 | 200 SMA: ₹95.
- Rule 1 & 5: ₹135 > ₹105 & ₹95 (Pass) and ₹135 > ₹120 (Pass).
- Rule 2 & 4: 150 SMA (₹105) > 200 SMA (₹95) (Pass); 50 SMA (₹120) > 150 SMA & 200 SMA (Pass).
- Rule 3: 200 SMA sloped upward for 4 months (Pass).
- Rule 6: 52-Week Low is ₹80 → ₹135 is +68.75% above low (Pass, requirement ≥30%–40%).
- Rule 7: 52-Week High is ₹145 → ₹135 is within 6.9% of high (Pass, requirement ≤25%).
- Rule 8: RS Rating = 88 vs Nifty 500 (Pass, requirement >80).
- Result: 8/8 Passed → Confirmed Stage 2 Uptrend.
```

---

## 7. Stan Weinstein’s Stage Analysis
- **Concept:** Macro technical framework categorizing stock lifecycle into four distinct structural stages.
- **Lifecycle Stages:**
  - **Stage 1 (Consolidation / Base):** Sideways price action, moving averages flatten. Institutional accumulation.
  - **Stage 2 (Advancing / Uptrend):** Price breaks above Stage 1 resistance and rising 30-week (150-day) MA on heavy volume. Sustained momentum.
  - **Stage 3 (Distribution / Top):** Volatility surges, price oscillates around flattening 30-week MA. Institutional profit booking.
  - **Stage 4 (Declining / Downtrend):** Price breaks below falling 30-week MA. Sustained downtrend.
- **Execution Rule:** Buy strictly during the transition breakout from Stage 1 to Stage 2 on heavy volume confirmation above 30-week MA.

### Pre-Execution Requirements — Strategy 7
```
□ Weekly price chart with 30-week (150-day) moving average (user must provide)
□ Weekly volume bars to verify Stage 1 -> Stage 2 breakout volume spike
□ Multi-month historical price range to classify current stage (Stage 1, 2, 3, or 4)
```

### Failure Modes & Hard Stop Rules — Strategy 7
```
❗ Buying in Stage 3 (distribution) or Stage 4 (downtrend below falling 30-week MA)
❗ Stage 1 -> Stage 2 breakout occurs on weak or below-average weekly volume
❗ Price falls back below 30-week MA post-breakout (false breakout exit trigger)
```

### Worked Numerical Example — Strategy 7
```
Stage Analysis Setup:
- Stage 1 Base: Stock trades sideways between ₹80 and ₹100 for 8 months; 30-week MA flattens at ₹90.
- Stage 2 Breakout Trigger: Price surges to ₹105 above ₹100 resistance; 30-week MA begins upward slope.
- Volume Confirmation: Weekly volume jumps 2.5x above 20-week average volume.
- Action: Initiate buy position at ₹105; set trailing stop loss just below 30-week MA (₹90).
```

---

## 8. Specific Entry Point Analysis (SEPA) Strategy (Mark Minervini)
- **Concept:** Multi-dimensional strategy blending structural chart setups (VCP / Trend Template) with fundamental earnings acceleration catalysts.
- **SEPA 4-Phase System:**
  1. **Structural Base Filter:** Verify VCP or tight consolidation pattern.
  2. **Fundamental Catalyst:** Identify earnings acceleration (TTM EPS growth >25-50%), margin expansion, or industry structural shift.
  3. **Low-Risk Pivot Point:** Determine exact entry price where risk is mathematically minimized (stop loss set tight at 3-7%).
  4. **Post-Entry Risk Management:** Trailing stop loss, taking partial profits into strength, cutting losses immediately if pivot breaks.

### Pre-Execution Requirements — Strategy 8
```
□ Confirmed VCP pattern or Stage 2 Trend Template alignment (user must provide)
□ Trailing Twelve Month (TTM) EPS growth rate data (minimum >25%–50% requirement)
□ Identified pivot entry price and pre-calculated 3%–7% stop-loss level
```

### Failure Modes & Hard Stop Rules — Strategy 8
```
❗ EPS growth decelerates below 25% or turns negative despite technical setup
❗ Pivot buy execution fails and price drops >7% below entry (mandatory cut loss)
❗ Lack of fundamental earnings driver (pure narrative without financial proof)
```

### Worked Numerical Example — Strategy 8
```
SEPA Strategy Setup:
- Phase 1 (Base): VCP pattern formed with 3 contractions (12% -> 6% -> 2%) above rising 50-day SMA.
- Phase 2 (Fundamental Catalyst): TTM EPS growth accelerates +42% YoY; EBITDA margin expands 250 bps.
- Phase 3 (Pivot Entry): Pivot buy trigger at ₹300; set stop loss at ₹285 (5% risk).
- Phase 4 (Risk Management): Stock advances to ₹360 (+20%); trim partial profit, trail stop loss to ₹315.
```

---
End of Document — Domain 46

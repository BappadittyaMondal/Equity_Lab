<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Institutional Multibagger Engine (27-Engine Synthesis)
> **Role:** Multi-dimensional early multibagger discovery, archetype classification, and risk penalty audit engine
> **Use when:** Identifying early-stage 3x–10x multibagger compounders across fundamental quality, cash flow, institutional footprint, technical relative strength, and catalyst triggers.
> **Evidence rule:** Evaluate all 27 engines independently and enforce hard risk penalties on missing or red-flagged observations.

# AI Institutional Multibagger Engine Specification

**Version:** v_0.1  
**Status:** Production Ready (Canonical)  
**Category:** Multibagger Discovery & Synthesis Engine  
**Module ID:** SCR-004  

---

## 1. Executive Summary & Purpose

The AI Institutional Multibagger Engine (`InstitutionalMultibaggerEngine`) synthesizes 27 quantitative and qualitative analytical sub-engines to identify high-conviction early-stage multibaggers in the Indian capital markets. Rather than relying on simple static filters, the engine evaluates multidimensional business acceleration, capital reinvestment intensity, institutional footprints, management commentary sentiment, alt-data signals, and technical market structure.

---

## 2. Enumeration of the 27 Analytical Sub-Engines

### Engine 1: Sales Growth Acceleration Engine
- Evaluates YoY quarterly and 3-year CAGR sales acceleration trends to detect demand expansion.

### Engine 2: Operating Margin Expansion Engine
- Measures OPM expansion trajectories to confirm pricing power and scale economies.

### Engine 3: PAT Outperformance Engine
- Tracks net profit growth relative to revenue growth to measure bottom-line expansion.

### Engine 4: Cash Flow Conversion Quality Engine
- Validates that Cash Flow from Operations (CFO) exceeds Net Profit by at least 1.2x.

### Engine 5: Free Cash Flow Yield Engine
- Calculates FCF yield relative to enterprise value to measure cash generation sustainability.

### Engine 6: Operating Leverage Engine
- Measures EPS growth acceleration multiplier against sales growth.

### Engine 7: Capital Work in Progress Expansion Engine
- Detects multi-year CWIP deployment preceding major revenue commissioning.

### Engine 8: Net Block Reinvestment Engine
- Identifies gross fixed asset expansion and capacity doubling trajectories.

### Engine 9: Asset Turnover Efficiency Engine
- Tracks asset turnover ratio improvements post-capex commissioning.

### Engine 10: ROCE Trajectory Engine
- Evaluates Return on Capital Employed expansion towards institutional 20%+ thresholds.

### Engine 11: ROE Quality Engine
- Measures Return on Equity purity, excluding leverage-driven artificial inflation.

### Engine 12: Debt Reduction Trajectory Engine
- Monitors debt-to-equity de-leveraging trajectories toward net-zero status.

### Engine 13: Interest Coverage Safety Engine
- Validates EBIT interest coverage ratios to prevent debt service stress.

### Engine 14: Working Capital Compression Engine
- Identifies cash conversion cycle reductions and inventory turnover gains.

### Engine 15: Promoter Skin in the Game Engine
- Tracks promoter shareholding levels and net open-market share purchases.

### Engine 16: Promoter Pledge Elimination Engine
- Enforces strict penalties for promoter pledge increases and rewards pledge reduction.

### Engine 17: Institutional Accumulation Engine
- Measures consecutive quarter FII and DII stake accumulation streaks.

### Engine 18: FII DII Net Inflow Engine
- Tracks mutual fund and foreign institutional net capital flows into candidate equities.

### Engine 19: Relative Strength Leadership Engine
- Evaluates 6-month and 12-month Mansfield Relative Strength against Nifty 500.

### Engine 20: Volatility Contraction Pattern Engine
- Detects VCP base structures and narrow range volatility compression setups.

### Engine 21: Volume Accumulation Multiplier Engine
- Measures relative volume (RVOL) and weekly delivery volume spikes during up-weeks.

### Engine 22: Piotroski F-Score Hardiness Engine
- Computes 9-point Piotroski fundamental financial health score.

### Engine 23: Valuation Margin of Safety Engine
- Determines DCF intrinsic value upside and price-to-fair-value margin of safety.

### Engine 24: PEG Ratio Growth Valuation Engine
- Evaluates PE-to-Growth ratios to ensure high-growth businesses are reasonably priced.

### Engine 25: Scuttlebutt Alt-Data Momentum Engine
- Integrates GST e-way bills, Vahan registrations, and EPFO hiring data.

### Engine 26: Management Concall NLP Sentiment Engine
- Parses transcript sentiment, guidance clarity, and tone shifts across earnings calls.

### Engine 27: Policy Catalyst Corporate Action Engine
- Evaluates PLI scheme eligibility, import tariff barriers, and corporate actions.

---

## 3. Archetype Classification Logic

Candidates passing the 27-engine evaluation are categorized into one of 4 institutional investment archetypes:

1. **EARLY_GROWTH:** Small-to-mid cap companies entering aggressive revenue and capacity expansion cycles.
2. **OPERATIONAL_TURNAROUND:** Companies transitioning from loss-making or low-margin states to positive cash flow profitability.
3. **HIGH_QUALITY_COMPOUNDER:** Established market leaders exhibiting steady 20%+ ROCE and high cash conversion.
4. **DEEP_VALUE_REATING:** Undervalued assets undergoing corporate restructuring or regulatory catalyst re-ratings.

---

## 4. Risk-Penalty Audit Rules

The engine applies strict mandatory risk penalties before issuing final rankings:

- **Pledge Penalty:** If promoter pledge exceeds 15%, deduct 25 points from composite score.
- **Cash Flow Divergence Penalty:** If CFO < 0.5 * Net Profit for 2 consecutive years, deduct 30 points.
- **Audit Qualification Penalty:** Any auditor qualification or governance red flag results in immediate hard-gate disqualification.

---

## 5. Machine Interface & Contract Schemas

### Endpoint 1: Universal Ranking
`POST /api/v1/multibagger/institutional-rank`

**Request Query Parameter:** `min_score` (default: `50.0`)

**Response Schema:**
```json
{
  "total_candidates": 412,
  "min_score_filter": 50.0,
  "rankings": [
    {
      "symbol": "TATAMOTORS",
      "company_name": "Tata Motors Ltd",
      "composite_score": 88.5,
      "multibagger_tier": "TIER_1_HIGH_CONVICTION",
      "archetype": "OPERATIONAL_TURNAROUND",
      "hard_gates_status": "PASS",
      "hard_gate_reasons": []
    }
  ]
}
```

### Endpoint 2: Single-Stock Deep Scorecard
`GET /api/v1/multibagger/institutional-score/{symbol}`

**Response Schema:**
```json
{
  "symbol": "TATAMOTORS",
  "company_name": "Tata Motors Ltd",
  "composite_score": 88.5,
  "archetype": "OPERATIONAL_TURNAROUND",
  "dimension_scores": {
    "business_growth": 92.0,
    "cash_flow_quality": 85.0,
    "capital_reinvestment": 90.0,
    "institutional_footprint": 86.0
  },
  "risk_penalties_applied": [],
  "passed_hard_gates": true
}
```

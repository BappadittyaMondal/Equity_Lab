# IERL Brain Upgrade — Master Prompt

> **Purpose**: Upload this document at the start of any AI coding session working on the IERL Equity Intelligence OS. It contains the honest current state, the 100/100 target definition, and the phased execution plan for all 14 core intelligence layers.

> **Pipeline Law**: Every upgrade must respect the canonical intelligence chain:
> `DATA → RESEARCH → REASONING → DEBATE → PREDICTION → CONVICTION → OUTCOME → LEARNING`
> Never skip upstream layers. Never let downstream layers invent what upstream layers should provide.

---

## Repository Context

- **Repo**: `Equity_Lab` (rebranded baseline, version 0.0.0)
- **Stack**: Python 3.14 / FastAPI / SQLite / Pydantic V2
- **Backend**: `app/` — services, models, API routes, tests
- **Knowledge Corpus**: `CONSOLIDATED_9_FILE_SYSTEM/` — 9 markdown files (~1.4 MB) encoding domain skills, analytical frameworks, and market knowledge
- **Strategy Registry**: 18 modules (A1–A3, B4–B8, C9–C14, D15–D18) + 5 research engines (E1–E5)
- **Key Services**: `market_data.py`, `research_data.py`, `arbiter.py`, `data_synthesizer.py`, `orchestrator.py`, `probability.py`, `llm.py`, `prediction_ledger.py`, `score_calibration.py`, `lifecycle_engine.py`

---

## Current State — Honest Layer Scoring

| # | Layer | Current Score | Key Gap |
|---|-------|:---:|---------|
| 1 | World & Market Knowledge | **70** | Rich in 9-file corpus but not queryable by code; no regime model connected to live VIX/macro |
| 2 | Research & Evidence Engine | **55** | Schema is excellent (point-in-time, sourced); database is empty — zero real financial observations ingested |
| 3 | Data Intelligence Layer | **45** | Provider fallback chain exists; P0 mock-default fixed; but no real ingestion pipeline populates the cache or DB |
| 4 | Fundamental Analysis Engine | **40** | Growth Inflection (E1), Turnaround (E2), Growth Gap (E3) exist but consume mock/synthetic data, not real financials from ResearchDataStore |
| 5 | Valuation Engine | **35** | Reverse DCF (C9) exists; no forward DCF, no relative valuation, no PEG, no scenario analysis |
| 6 | Technical/Price-Action Engine | **50** | VCP (B5), SEPA (B8), ATH Breakout (D15), Dual Momentum (D16) exist; depend on yfinance which may fail; no delivery volume analysis |
| 7 | Forensic & Governance Engine | **45** | Governance Quality (C13), Saatvik (D18) exist; Beneish M-Score is metadata-only, no actual 8-variable calculation; no related-party detection |
| 8 | Multi-Strategy Intelligence | **55** | 18 modules registered; but 10 of 18 return hardcoded `diagnostic_score: 82.5` via the else-branch fallback |
| 9 | Contradiction & Debate Engine | **30** | `ContradictionReport` schema exists; `generate_contradiction_report()` does simple positive/negative split — no structured Bull vs Bear debate |
| 10 | Prediction Engine | **35** | `probability.py` does empirical return distribution; no catalyst modeling, no scenario trees, no time-horizon expected return |
| 11 | Conviction/Arbitration Engine | **40** | Arbiter exists; but logic is binary (`passed_gates → Buy, else → Avoid`); no weighted scoring, no per-engine confidence, governance veto threshold exists but untested with real data |
| 12 | Learning & Calibration Engine | **25** | `prediction_ledger.py` and `score_calibration.py` exist as schemas; no automated outcome tracking, no recalibration loop |
| 13 | AI Research Reasoning Layer | **20** | `llm.py` sends a basic prompt to Gemini with minimal context injection; no structured reasoning, no evidence grounding, no challenge protocol |
| 14 | Explainability/Audit Layer | **30** | `MetaHeader` provides source/timestamp; `ConvictionCall` has `primary_thesis` and `contributing_engines`; but no "why", no invalidation conditions, no confidence decomposition |

**Composite Brain Score: ~39/100**

---

## Phase Definitions

### PHASE 1 — DATA FOUNDATION (Layers 1, 2, 3)
**Goal**: Real data flows through the system. No analysis runs on synthetic/mock data in production.

#### Layer 1: World & Market Knowledge Model → 100/100

**Current**: 9-file knowledge corpus is static markdown. `get_market_regime()` in `market_data.py` returns VIX-based regime but isn't connected to strategy execution.

**Upgrade tasks**:
1. **Connect regime to arbiter**: `Arbiter._collect_engine_outputs()` must pass current regime (`CALM`/`ELEVATED`/`VOLATILE`/`CRISIS`) to each strategy. Strategies should adapt thresholds by regime.
2. **Create `app/services/knowledge/regime_engine.py`**: Deterministic regime classifier using India VIX (from live data), Nifty 200DMA distance, FII flow direction (from ownership snapshots), and sector rotation signals.
3. **Create `app/services/knowledge/sector_model.py`**: Map each company symbol to sector/industry. Provide sector-relative metrics (P/E vs sector median, growth vs sector average). Use data from `companies` table + `financial_observations`.
4. **Macro context struct**: Create a `MacroContext` Pydantic model with fields: `vix_level`, `regime`, `nifty_level`, `nifty_200dma_distance_pct`, `fii_net_flow_30d`, `rbi_repo_rate`, `usd_inr`. Populate from live sources or manual override.

**Definition of 100/100**: Every analysis call receives a `MacroContext` and `RegimeClassification`. Strategy thresholds adapt. Sector-relative comparisons are available. The system knows "what environment are we in" before analyzing any stock.

---

#### Layer 2: Research & Evidence Engine → 100/100

**Current**: `research_data.py` (502 lines) has excellent schema — `financial_observations`, `business_events`, `corporate_actions`, `ownership_snapshots`, `document_metadata`, `market_daily_snapshots`. All append-only, point-in-time, sourced. But the database is **empty**.

**Upgrade tasks**:
1. **Create `app/services/ingestion/screener_ingester.py`**: Scrape or API-pull quarterly financials (Revenue, PAT, EPS, Operating Margin, ROCE, D/E, FCF) from Screener.in for any symbol. Transform into `FinancialObservationIn` records with `source_name="Screener.in"`, `source_url`, `published_at`, `confidence=0.85`.
2. **Create `app/services/ingestion/bse_filing_ingester.py`**: Ingest BSE/NSE filing announcements as `BusinessEventIn` records. Track board meetings, results announcements, insider trades.
3. **Create `app/services/ingestion/ownership_ingester.py`**: Quarterly shareholding pattern data (promoter %, FII %, DII %, mutual fund %, pledge %) → `OwnershipSnapshotIn`.
4. **Bulk seed command**: `python -m app.services.ingestion.seed_watchlist` — for every symbol on watchlist, run all ingesters and populate the research database with 3–5 years of historical quarterly data.
5. **Source credibility scoring**: Each `FinancialObservationIn` has a `confidence` field (0.0–1.0). Define rules: BSE filing = 1.0, Screener.in = 0.85, news article = 0.6, AI-generated = 0.3.

**Definition of 100/100**: For any watchlist symbol, the system has ≥12 quarters of real financial observations, ownership history, and corporate events — all sourced, timestamped, and queryable via `get_timeline()`. No strategy engine needs to fabricate input data.

---

#### Layer 3: Data Intelligence Layer → 100/100

**Current**: `market_data.py` has provider fallback chain + SQLite cache. P0 fixed mock default. But live providers (yfinance) are unreliable and no automated daily ingestion exists.

**Upgrade tasks**:
1. **Reliable provider chain**: yfinance → Alpha Vantage → cached → explicit error (never silent mock). Each response tagged with `data_mode: LIVE|CACHED|STALE|ERROR`.
2. **Daily OHLCV ingestion cron**: `app/services/ingestion/daily_price_ingester.py` — for all watchlist symbols, fetch daily OHLCV and store in `market_daily_snapshots` table. Run via scheduler or manual trigger.
3. **Data freshness enforcement**: Add `max_staleness_hours` config. If cached quote is older than threshold, tag as `STALE` and log warning. Never serve stale data as fresh.
4. **Corporate action adjustment**: When `corporate_actions` table has a stock split or bonus, compute `adjustment_factor` and apply to historical prices in `market_daily_snapshots`.
5. **Data quality assertions**: Before any strategy runs, validate: price > 0, volume > 0, PE ratio is sane (0.1–500), 52-week range is internally consistent.

**Definition of 100/100**: Every price quote has a provenance tag. Historical data is adjusted for corporate actions. Stale data is never silently served as fresh. Data quality gates prevent garbage-in.

---

### PHASE 2 — ANALYTICAL ENGINES (Layers 4, 5, 6, 7)
**Goal**: Each engine consumes real data from Phase 1 and produces scored, evidenced conclusions.

#### Layer 4: Fundamental Analysis Engine → 100/100

**Current**: E1 (Growth Inflection), E2 (Turnaround), E3 (Growth Gap) exist but read from `financial_observations` which is empty, causing them to return defaults.

**Upgrade tasks**:
1. **Wire E1/E2/E3 to ResearchDataStore**: Each engine should call `store.get_timeline(symbol)` and extract real quarterly revenue, PAT, EPS, margins, ROCE, FCF series. No synthetic fallbacks.
2. **Add missing fundamental metrics**: Create calculation functions for: ROE decomposition (DuPont), working capital trend, operating leverage, capital allocation efficiency (ROCE vs WACC), cash conversion ratio.
3. **Quarterly sequential analysis**: For each metric, compute QoQ change, YoY change, 4-quarter trailing average, acceleration (change of change). Flag inflection points.
4. **Quality scoring composite**: Create `FundamentalQualityScore` — weighted composite of: earnings quality (CFO/PAT > 1.0), margin stability (std dev of OPM over 8 quarters), balance sheet strength (D/E trend), capital efficiency (ROCE trend).
5. **Evidence trail**: Every score must include `evidence: List[str]` showing exactly which data points drove it. Example: `"Revenue grew 23% YoY in Q2FY25 (₹4,521 Cr vs ₹3,675 Cr, source: BSE Filing)"`.

**Definition of 100/100**: Given any symbol with ≥8 quarters of data, the engine produces a multi-dimensional fundamental score with full evidence trail, using only real sourced observations.

---

#### Layer 5: Valuation Engine → 100/100

**Current**: Only Reverse DCF (C9) exists — calculates market-implied growth rate from P/E.

**Upgrade tasks**:
1. **Forward DCF model**: `app/services/strategies/dcf_forward.py` — 3-stage DCF using: (a) explicit 3-year FCF projections from growth trend, (b) fade period, (c) terminal value. Inputs from fundamental engine. Sensitivity table for discount rate ± 1%.
2. **Relative valuation**: Compare P/E, P/B, EV/EBITDA, PEG vs (a) own 5-year median, (b) sector median, (c) Nifty 50 median. Output: `ValuationZone` enum: `DEEPLY_UNDERVALUED | UNDERVALUED | FAIR | OVERVALUED | EXTREMELY_OVERVALUED`.
3. **PEG ratio with growth source**: PEG = P/E ÷ forward earnings growth %. Growth rate must come from fundamental engine's computed EPS CAGR, not hardcoded.
4. **Scenario analysis**: Bull / Base / Bear cases with different growth rate and multiple assumptions. Output probability-weighted expected value.
5. **Margin of safety calculation**: `intrinsic_value` vs `current_price` → margin of safety %. Flag if < 0% (overvalued).

**Definition of 100/100**: For any symbol, the system produces intrinsic value from 3+ methods (DCF, relative, reverse DCF), a margin-of-safety percentage, and a scenario matrix with probability-weighted expected return.

---

#### Layer 6: Technical/Price-Action Engine → 100/100

**Current**: VCP (B5), SEPA (B8), ATH Breakout (D15) implemented. Others are metadata-only.

**Upgrade tasks**:
1. **Implement remaining technical modules**: B4 (Volume Price Analysis), B6 (RS Rating), B7 (Pocket Pivot), D16 (Dual Momentum), D17 (Mean Reversion) — each must have actual calculation logic, not the else-branch fallback.
2. **Delivery volume analysis**: Use `delivery_pct` from `market_daily_snapshots` to distinguish genuine accumulation from speculative volume.
3. **Multi-timeframe trend assessment**: Weekly + daily + monthly trend alignment. Output: `TrendAlignment` enum: `ALL_BULLISH | MIXED | ALL_BEARISH`.
4. **Stage analysis**: Weinstein/Mansfield stage classification (Stage 1: Basing, Stage 2: Advancing, Stage 3: Topping, Stage 4: Declining) using 30-week MA slope and price position.

**Definition of 100/100**: All 8 technical modules (B4–B8, D15–D17) execute real calculations on real price data. Each produces a normalized 0–100 score with evidence. Stage and trend alignment are available for every symbol.

---

#### Layer 7: Forensic & Governance Engine → 100/100

**Current**: C13 (Governance Quality) has promoter pledge check. D18 (Saatvik) screens sin stocks. Beneish M-Score is registered but not calculated.

**Upgrade tasks**:
1. **Implement Beneish M-Score calculation**: 8-variable model using real financial data from ResearchDataStore. Variables: DSRI, GMI, AQI, SGI, DEPI, SGAI, TATA, LVGI. Flag if M-Score > -1.78.
2. **Implement Altman Z-Score (C12)**: 5-ratio distress model using balance sheet data. Zone classification: Safe (> 2.99), Grey (1.81–2.99), Distress (< 1.81).
3. **Implement Piotroski F-Score (C11)**: 9-point binary scoring from YoY balance sheet changes. Data source: consecutive `financial_observations`.
4. **Related-party transaction detection**: Flag companies where related-party transactions exceed 10% of revenue (from annual report document metadata).
5. **Promoter behaviour scoring**: Track promoter holding trend (increasing/decreasing), pledge trend, insider buying/selling from `ownership_snapshots` and `business_events`.
6. **Governance veto integration**: If governance score < `GOVERNANCE_VETO_SCORE` (30), the arbiter must cap conviction at 30 regardless of other signals. This exists in code but needs real governance data to trigger.

**Definition of 100/100**: Beneish, Altman, Piotroski all compute from real data. Promoter behaviour is tracked longitudinally. Governance veto fires on real red flags, not hypothetical thresholds.

---

### PHASE 3 — INTELLIGENCE & REASONING (Layers 8, 9, 13)
**Goal**: Strategies interact, contradict each other, and the AI reasons about evidence rather than generating opinions.

#### Layer 8: Multi-Strategy Intelligence → 100/100

**Current**: 18 modules registered but 10 use the else-branch fallback returning `diagnostic_score: 82.5`. Strategy scores are not normalized. No regime adaptation.

**Upgrade tasks**:
1. **Eliminate the else-branch fallback**: Every module ID in `run_strategy_module()` must route to a real implementation. If a module genuinely cannot run (missing data), return `status: "data_insufficient"` with explanation, not fake scores.
2. **Normalize all strategy scores to 0–100**: Create `NormalizedStrategyOutput` with fields: `engine_id`, `score_0_100`, `verdict`, `confidence_pct`, `evidence`, `data_quality_grade`. Every engine outputs this.
3. **Regime-adaptive thresholds**: VCP breakout threshold should be stricter in `VOLATILE` regime. Growth inflection should weight FCF higher in `CRISIS` regime. Pass `MacroContext` to each engine.
4. **Strategy independence verification**: No engine should read another engine's output directly. Each produces independent scores. Only the Arbiter combines them.

**Definition of 100/100**: All 18+ modules execute real calculations. Each outputs a normalized 0–100 score with evidence and data quality grade. Thresholds adapt to market regime. No fake fallback scores.

---

#### Layer 9: Contradiction & Debate Engine → 100/100

**Current**: `generate_contradiction_report()` splits engines into positives/negatives. No structured debate.

**Upgrade tasks**:
1. **Structured Bull vs Bear case**: For each symbol, generate: `BullCase` (top 3 supporting engines + their evidence) and `BearCase` (top 3 contradicting engines + their evidence). Each case must cite specific data points.
2. **Thesis attack protocol**: For each bull point, auto-generate the strongest possible counter-argument. Example: Bull says "Revenue growing 25% YoY" → Bear responds "But operating margin declining 300bps, growth is unprofitable".
3. **Contradiction severity scoring**: Not all contradictions are equal. Fundamental vs Technical disagreement = LOW. Fundamental vs Forensic disagreement = HIGH (governance concern overrides growth signal). Assign severity: `LOW | MEDIUM | HIGH | CRITICAL`.
4. **Falsification conditions**: For every conviction call, generate 2–3 specific conditions that would invalidate the thesis. Example: "Thesis invalidated if: (1) Q3 revenue growth < 10%, (2) promoter pledge exceeds 25%, (3) D/E ratio exceeds 1.5x".
5. **Update schema**: Enhance `ContradictionReport` with: `bull_case`, `bear_case`, `falsification_conditions`, `contradiction_severity`, `net_evidence_balance`.

**Definition of 100/100**: Every conviction call includes a structured Bull vs Bear debate with cited evidence, severity-weighted contradictions, and explicit falsification conditions.

---

#### Layer 13: AI Research Reasoning Layer → 100/100

**Current**: `llm.py` sends a basic prompt with minimal market context. No structured reasoning, no evidence grounding, no RAG.

**Upgrade tasks**:
1. **Evidence-grounded prompting**: Before any LLM call, assemble a `ResearchContext` from the database: latest 4 quarters of financials, ownership changes, corporate events, current price vs intrinsic value, governance flags. Inject this as structured data, not prose.
2. **Structured reasoning protocol**: LLM prompt must enforce: (a) Cite specific numbers from the provided data, (b) Identify what is known vs uncertain, (c) Flag any claim that cannot be verified from the data, (d) Never generate fake financial numbers.
3. **Challenge mode**: After initial analysis, send a second prompt: "Now argue against your own conclusion. What evidence contradicts it? What assumptions could be wrong?" Combine both into the final response.
4. **LLM as synthesis layer, not intelligence layer**: The LLM should NEVER be the primary source of financial data. Its role is: (a) Synthesize existing engine outputs into readable narrative, (b) Compare contradictory evidence, (c) Explain complex relationships. The deterministic engines remain the source of truth.
5. **RAG from knowledge corpus**: Index the 9-file knowledge base. When the LLM needs domain knowledge (e.g., "what is SEPA methodology?"), retrieve the relevant section from the corpus rather than relying on the LLM's training data.

**Definition of 100/100**: LLM never invents data. Every LLM response is grounded in real engine outputs and database records. The AI investigates and challenges rather than generates opinions.

---

### PHASE 4 — PREDICTION & CONVICTION (Layers 10, 11, 14)
**Goal**: The system makes probabilistic predictions with full audit trails, not binary recommendations.

#### Layer 10: Prediction Engine → 100/100

**Current**: `probability.py` does historical empirical return distribution. No catalyst modeling.

**Upgrade tasks**:
1. **Multi-horizon expected return**: Calculate probability-weighted expected return for 3M, 6M, 1Y, 2Y, 5Y horizons. Combine: (a) empirical distribution from `probability.py`, (b) fundamental-based return estimate (earnings growth × multiple expansion potential), (c) mean reversion tendency from valuation gap.
2. **Catalyst timeline**: List upcoming known catalysts from `business_events` (earnings date, AGM, policy announcements) with estimated impact direction and magnitude.
3. **Scenario tree**: Generate 3 scenarios (Bull/Base/Bear) with probability weights, expected price targets, and key drivers for each. Probabilities must sum to 100%.
4. **Risk quantification**: Max drawdown estimate from historical volatility. Probability of >20% loss in each time horizon. Risk-adjusted return (Sortino-like ratio).
5. **Confidence decomposition**: Break confidence into: data quality confidence (how good is our data?), model confidence (how well does this model type work historically?), thesis confidence (how strong is the fundamental case?).

**Definition of 100/100**: For any symbol, the system outputs multi-horizon expected returns with scenario probabilities, catalyst timelines, risk estimates, and decomposed confidence — all traceable to specific data and models.

---

#### Layer 11: Conviction/Arbitration Engine → 100/100

**Current**: Arbiter logic is binary: `passed_gates → Buy, else → Avoid`. No weighted scoring. Confidence = `data_confidence_score` (always ~1.0 for single provider).

**Upgrade tasks**:
1. **Weighted multi-engine scoring**: Replace binary logic with weighted composite. Each engine category gets a weight: Fundamental (30%), Valuation (20%), Technical (15%), Forensic (15%), Macro/Regime (10%), Prediction (10%). Weights should be configurable.
2. **Per-engine confidence integration**: Each engine's score is multiplied by its `data_quality_grade` (0.0–1.0). An engine running on 12 quarters of real data gets weight 1.0. An engine running on 2 quarters gets 0.5. An engine with no data gets 0.0 and is excluded.
3. **Governance veto enforcement**: If any forensic engine flags `CRITICAL` (Beneish M-Score > -1.78, or promoter pledge > 40%, or Altman Z < 1.81), cap conviction score at 30 and set verdict to `"Watch"` or `"Avoid"` regardless of other scores.
4. **Verdict granularity**: Use all 5 verdicts meaningfully: `Strong Buy` (score ≥ 85, no forensic flags), `Buy` (70–84), `Accumulate` (55–69), `Watch` (40–54), `Avoid` (< 40 or governance veto).
5. **Thesis generation**: `primary_thesis` should be auto-generated from the top 2 contributing engines' evidence, not a boilerplate string.

**Definition of 100/100**: Conviction score is a transparent weighted composite of real engine outputs. Governance veto fires on real data. Verdict maps to clear score ranges. Thesis cites specific evidence.

---

#### Layer 14: Explainability/Audit Layer → 100/100

**Current**: `MetaHeader` has source + timestamp. `ConvictionCall` has `primary_thesis` and engine lists. No deeper explainability.

**Upgrade tasks**:
1. **Decision audit trail schema**: Create `DecisionAuditTrail` model with: `symbol`, `timestamp`, `engine_outputs[]` (full scored output from each engine), `macro_context`, `contradiction_report`, `prediction_summary`, `final_score`, `final_verdict`, `governance_veto_applied`, `falsification_conditions[]`.
2. **"Why this verdict?" explainer**: For every conviction call, auto-generate a structured explanation: "Verdict is BUY because: (1) Fundamental score 78/100 — Revenue grew 23% YoY with expanding margins [source: BSE Q2FY25 filing]. (2) Valuation score 72/100 — Trading at 15% discount to DCF intrinsic value. (3) No governance red flags."
3. **"What could invalidate this?" section**: Every call includes 2–3 specific, measurable invalidation conditions from the Contradiction Engine.
4. **Data lineage**: For every number in the output, trace back to: source (BSE/Screener/yfinance), timestamp (when was it published?), ingestion timestamp (when did we fetch it?), confidence (how reliable is this source?).
5. **Persist audit trail**: Store complete `DecisionAuditTrail` in SQLite. Enable historical comparison: "What did we say about RELIANCE 6 months ago? What changed?"

**Definition of 100/100**: Every conclusion answers: Why? Based on what data? From what source? When? How confident? What would invalidate it? Full audit trail is persisted and queryable.

---

### PHASE 5 — LEARNING LOOP (Layer 12)
**Goal**: The system improves over time by tracking its own predictions against reality.

#### Layer 12: Learning & Calibration Engine → 100/100

**Current**: `prediction_ledger.py` can log predictions and record outcomes. `score_calibration.py` can analyze score buckets. Neither is connected to automated outcome tracking.

**Upgrade tasks**:
1. **Auto-log every conviction call**: When `Arbiter.arbitrate()` produces a `ConvictionCall`, automatically log to `prediction_ledger` with: symbol, score, verdict, reference_price, thesis, model_version.
2. **Scheduled outcome checker**: `app/services/monitoring/outcome_checker.py` — for each logged prediction, fetch current price at 1M, 3M, 6M, 12M intervals. Compute actual return. Store in `outcome_ledger`.
3. **Calibration report generation**: Monthly auto-run of `ScoreCalibrator.calibrate()` on all predictions with outcomes. Output: hit rate by score bucket, false positive/negative list, strategy attribution.
4. **Score monotonicity enforcement**: If calibration reveals that score bucket 70–79 outperforms 80–89, flag for investigation. The system should exhibit monotonicity: higher scores → higher returns.
5. **Recalibration recommendations**: If a strategy consistently over/under-contributes, output a recommendation to adjust its weight in the arbiter. Require human sign-off before applying.
6. **Model versioning**: Every change to arbiter weights or strategy thresholds increments `model_version`. All predictions are tagged with the version that produced them. Compare accuracy across versions.

**Definition of 100/100**: Every prediction is logged. Outcomes are tracked automatically. Calibration reports reveal accuracy by bucket. Weight adjustments are data-driven with human sign-off. The system measurably improves over time.

---

## Execution Rules

1. **Never skip a phase**. Phase 2 engines need Phase 1 data. Phase 3 reasoning needs Phase 2 scores. Phase 4 prediction needs Phase 3 debate output.
2. **Test at every phase boundary**. Before starting Phase N+1, all Phase N tests must pass. Write tests that verify real data flows through each layer.
3. **No synthetic data in production paths**. If real data is unavailable for a symbol, the engine must return `status: "data_insufficient"` with explanation — never fabricate numbers.
4. **Evidence over opinion**. Every score, verdict, and thesis must cite specific data points with source and date. If a claim cannot be grounded in data, it must be flagged as `"unverified_hypothesis"`.
5. **Human-in-the-loop for calibration**. The system can recommend weight changes; only a human can approve and apply them.

---

## Session Usage Instructions

When starting a new AI coding session, upload this document and say:

> "We are upgrading IERL Brain Layer [N]. The current state is [score]/100. The target is 100/100. Here is the repository. Execute the upgrade tasks for Layer [N] as defined in the master prompt. Follow the execution rules. Write tests for every new capability."

For multi-layer sessions:

> "Execute Phase [1–5] of the IERL Brain Upgrade. Complete all layers in this phase. Verify with tests before reporting completion."

---

## Success Criteria

The brain upgrade is complete when:

- [ ] All 14 layers score ≥ 90/100 in independent audit
- [ ] Zero synthetic/mock data flows through any production analysis path
- [ ] Every conviction call has a full audit trail answering Why/What/When/Confidence/Invalidation
- [ ] Prediction ledger has ≥ 50 logged predictions with tracked outcomes
- [ ] Calibration report shows score monotonicity (higher scores → higher returns)
- [ ] Bull vs Bear debate is generated for every conviction call with cited evidence
- [ ] LLM never generates financial data — only synthesizes engine outputs
- [ ] Full test suite passes with ≥ 85% coverage on intelligence layers

# Project Scope & Architecture Boundary — `v0.0.0`

> **Document Type**: Architecture & Governance Declaration  
> **Target Version**: `v0.0.0` (Public Release Baseline)  
> **Status**: APPROVED  
> **Authority**: System Governance Lead & Quantitative Engineering Lead  

---

## 1. Executive Summary

`v0.0.0` represents the canonical release candidate baseline of **Equity Lab** (formerly `Equity_final_claude_v_0.3`). This document explicitly defines what capabilities are included in `v0.0.0`, what capabilities are deferred to future major releases (`v0.1` / `v0.2`), and how internal metric outputs (specifically confidence scores) must be interpreted by frontend UI developers and API consumers.

---

## 2. Baseline Status (`v0.0.0`)

### What `v0.0.0` IS:
1. **Deterministic Quantitative Decision-Support Engine**: A robust, rule-based screening and evaluation framework tailored for Indian equities.
2. **25 Strategy & Research Modules**: Active implementation covering Growth Inflection (E1), Turnaround Stage (E2), Growth Market Gap (E3), Multibagger Screener (E4), Expectation Gap (E7), Reverse DCF (C9), Beneish M-Score (C10), Piotroski F-Score (C11), Altman Z-Score (C12), Governance Quality (C13), Saatvik Ethical Filter (D18), VCP Breakout (B5), SEPA (B8), ATH Breakout (D15), Dual Momentum (D16), options arbitrage (A1–A3), and related modules.
3. **Point-In-Time Integrity Protection**: Full point-in-time data isolation via `PointInTimeReplayEngine` and `ResearchDataStore` to guarantee zero look-ahead bias during historical replay.
4. **Multi-Engine Arbitration & Thesis Debate**: Arbiter engine supporting weighted composite scoring, hard governance veto gates (e.g. promoter pledge, accounting red flags), and structured Bull vs. Bear debate synthesis.

### What `v0.0.0` IS NOT:
1. **NOT a Statistical Machine Learning / XGBoost Classifier**: The engine does NOT currently load or execute trained gradient-boosted trees (XGBoost / LightGBM / CatBoost) for return probability estimation.
2. **NOT a Vector DB / Retrieval-Augmented Generation (RAG) System**: The engine does NOT currently query a vector store (e.g., ChromaDB / Qdrant) for unstructured SEC/BSE PDF filing retrieval.
3. **NOT an Automated Live Outcome Calibration Loop**: While prediction ledgers exist, automatic real-time calibration loops are deferred.

---

## 3. Governance Rule: Interpretation of Confidence Scores

> [!IMPORTANT]  
> All fields named `heuristic_confidence`, `confidence_score`, `confidence_pct`, or `conviction_score` across `v0.0.0` API endpoints and strategy schemas are **deterministic, rule-based heuristic conviction weights**. They are **NOT** statistically calibrated ML probabilities or empirical win rates.

### Mandatory Guidance for Frontend UI / Product Engineers:
- **UI Labeling**: Any user interface built on top of `v0.0.0` endpoints **MUST** display these metrics as **"Conviction Levels"** or **"Heuristic Conviction Score"** (on a 0–100 scale).
- **Prohibited UI Terminology**: Frontend components **MUST NOT** present these values as "Win Probability", "Calibrated Odds", "Statistical Probability", or "ML Confidence Rate".
- **Risk Prevention**: This boundary prevents misleading end-users or institutional investors into misinterpreting deterministic rule-matching scores as statistically validated probability distributions.

---

## 4. Architectural Roadmap (v0.1 / v0.2)

When machine learning calibration and unstructured document search are introduced in future phases:

| Feature Layer | `v0.0.0` (Current) | `v0.1.0` (Target) | `v0.2.0` (Target) |
|---|---|---|---|
| **Strategy Engine** | 25 Deterministic Rules | 25 Deterministic Rules | Hybrid Quant + ML |
| **Confidence Field** | `heuristic_confidence` | `heuristic_confidence` | `heuristic_confidence` + `ml_calibrated_probability` |
| **Filing Search** | Structured Metadata | Structured Metadata | Vector RAG (PDF Filings) |
| **Model Ingest** | Hardcoded Gates & Rules | Calibrated Rule Weights | Trained XGBoost Models |

By introducing explicit `ml_calibrated_probability` fields in future releases alongside `heuristic_confidence`, API backwards compatibility will be strictly preserved.

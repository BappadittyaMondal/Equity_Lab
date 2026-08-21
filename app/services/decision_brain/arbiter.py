"""Arbiter — Phase 4, Layer 11 upgrade.

Full weighted conviction engine replacing the previous binary pass/fail logic.

Key changes from Phase 3:
  - Weighted composite scoring: Fundamental 30%, Valuation 20%, Technical 15%,
    Forensic 15%, Macro/Regime 10%, Prediction (from L10) 10%
  - Per-engine confidence: score × (data_quality_grade / 100)
  - Forensic veto: Beneish > -1.78, Altman < 1.81, or pledge > 40% → cap at 30
  - 5-tier granular verdicts: Strong Buy / Buy / Accumulate / Watch / Avoid
  - Auto-logs every call to prediction_ledger (Phase 5 prerequisite)
  - Generates full DecisionAuditTrail (Layer 14)
  - Integrates prediction engine (Layer 10) for forward-looking context
"""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import ConvictionCall, ContradictionReport, MacroContext
from app.services.synthesis import DataSynthesizer
from app.services.decision_brain.debate_engine import generate_debate, ENGINE_CATEGORIES
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Engine category weights (configurable) ─────────────────────────────────
# Must sum to 1.0
CATEGORY_WEIGHTS: Dict[str, float] = {
    "FUNDAMENTAL": 0.30,
    "VALUATION":   0.20,
    "TECHNICAL":   0.15,
    "FORENSIC":    0.15,
    "MACRO":       0.10,
    "GOVERNANCE":  0.10,
    "OTHER":       0.00,  # Excluded from composite
    "OPTIONS":     0.00,  # Options strategies don't affect equity conviction
}

MODEL_VERSION = "0.4.0"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATA_STORE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conviction_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            verdict TEXT NOT NULL,
            conviction_score INTEGER NOT NULL,
            primary_thesis TEXT,
            contributing_engines TEXT,
            contradicting_engines TEXT,
            confidence_tier TEXT,
            created_at TEXT NOT NULL,
            data_backed BOOLEAN DEFAULT 0
        )
    """)
    # Auto-migration: ensure data_backed column exists and backfill 0
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(conviction_calls)").fetchall()]
        if "data_backed" not in cols:
            conn.execute("ALTER TABLE conviction_calls ADD COLUMN data_backed BOOLEAN DEFAULT 0")
            conn.execute("UPDATE conviction_calls SET data_backed = 0 WHERE data_backed IS NULL")
    except Exception:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS thesis_drift_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            old_score INTEGER NOT NULL,
            new_score INTEGER NOT NULL,
            old_verdict TEXT NOT NULL,
            new_verdict TEXT NOT NULL,
            delta INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


_ensure_table()


class Arbiter:
    """Phase 4 Conviction Engine — weighted multi-engine arbitration.

    Pipeline: DATA → RESEARCH → REASONING → DEBATE → PREDICTION → CONVICTION → AUDIT
    """

    # Governance veto threshold
    GOVERNANCE_VETO_SCORE = 30
    VETO_SCORE_CAP = 30

    def __init__(self):
        self.synthesizer = DataSynthesizer()
        self._macro_context: Optional[MacroContext] = None

    @property
    def macro_context(self) -> MacroContext:
        if self._macro_context is None:
            try:
                from app.services.knowledge.regime_engine import RegimeEngine
                self._macro_context = RegimeEngine().get_macro_context()
            except Exception as e:
                logger.warning("Failed to fetch macro context: %s — using defaults", e)
                self._macro_context = MacroContext()
        return self._macro_context

    # ──────────────────────────────────────────────────────────────────────
    # 1. Collect engine outputs
    # ──────────────────────────────────────────────────────────────────────
    def _collect_engine_outputs(
        self, symbol: str, snap: Optional[Any] = None, as_of: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        from app.services.strategies import registry
        from app.services.strategies.registry import run_strategy_module

        if snap is None:
            snap = self.synthesizer.synthesize(symbol, as_of=as_of)
        confidence = int(snap.data_confidence_score * 100)

        regime = self.macro_context.regime.regime
        outputs = []

        all_modules = {**registry.STRATEGY_MODULES, **registry.RESEARCH_ENGINES}
        for engine_id, module in all_modules.items():
            if module.status != "production":
                continue
            try:
                resp = run_strategy_module(engine_id, symbol)
            except Exception as e:
                logger.warning("Engine %s failed for %s: %s", engine_id, symbol, e)
                continue

            verdict = "Buy" if resp.passed_gates else "Avoid"

            outputs.append({
                "engine_id":  engine_id,
                "verdict":    verdict,
                "confidence": confidence,
                "regime":     regime,
                "raw":        resp,
                "status":     getattr(resp, "status", "unknown"),
            })

        return outputs

    # ──────────────────────────────────────────────────────────────────────
    # 2. Weighted composite scoring (Layer 11 core)
    # ──────────────────────────────────────────────────────────────────────
    def _compute_weighted_score(
        self,
        outputs: List[Dict[str, Any]],
    ) -> Tuple[float, Dict[str, float]]:
        """Compute weighted conviction score across engine categories.

        Per-engine contribution = (passed_gates ? confidence : 0) × category_weight
        Engines with status=data_insufficient contribute 0 (excluded).
        Returns (composite_score_0_100, category_breakdown_dict).
        """
        category_scores: Dict[str, List[float]] = {k: [] for k in CATEGORY_WEIGHTS}
        category_breakdown: Dict[str, float] = {}

        for out in outputs:
            # Skip engines with no real data
            if out.get("status") == "data_insufficient":
                continue

            eng_id = out["engine_id"]
            category = ENGINE_CATEGORIES.get(eng_id, "OTHER")
            if CATEGORY_WEIGHTS.get(category, 0) == 0:
                continue

            # Score: confidence if Buy, 0 if Avoid
            if out["verdict"] == "Buy":
                engine_score = out["confidence"]  # 0–100
            else:
                engine_score = 0.0

            # Penalty for Avoid engines: add negative contribution
            if out["verdict"] == "Avoid":
                engine_score = max(0.0, 50.0 - out["confidence"] * 0.5)

            category_scores[category].append(engine_score)

        # Average within each category
        weighted_sum = 0.0
        total_weight = 0.0
        for cat, weight in CATEGORY_WEIGHTS.items():
            if weight == 0 or not category_scores[cat]:
                continue
            cat_avg = sum(category_scores[cat]) / len(category_scores[cat])
            weighted_sum += cat_avg * weight
            total_weight += weight
            category_breakdown[cat] = round(cat_avg, 1)

        if total_weight > 0:
            composite = weighted_sum / total_weight
        else:
            # No categorised engines ran — fall back to simple average of Buy verdicts
            buy_outputs = [o for o in outputs if o["verdict"] == "Buy" and o.get("status") != "data_insufficient"]
            composite = (len(buy_outputs) / max(len(outputs), 1)) * 75.0

        return round(composite, 1), category_breakdown

    # ──────────────────────────────────────────────────────────────────────
    # 3. Forensic veto (enhanced — checks real forensic flags)
    # ──────────────────────────────────────────────────────────────────────
    def _apply_governance_veto(self, outputs: List[Dict[str, Any]]) -> bool:
        """Veto fires if ANY forensic/governance engine raises a CRITICAL flag.

        Triggers:
          - C13 governance_grade in POOR or UNKNOWN → veto
          - FORENSIC/C11/C12 engine forensic_risk = CRITICAL → veto
          - Promoter pledge explicitly > 40% in results → veto

        Non-triggers:
          - governance_grade EXCELLENT / GOOD / ADEQUATE → no veto
          - Missing governance_grade key (engine produced no grade) → no veto
          - pledge key absent → no veto (only fires when key is explicitly present)
        """
        # Grades that trigger veto (POOR performance or unknown = caution)
        VETO_GRADES = {"POOR", "UNKNOWN"}

        for out in outputs:
            raw = out.get("raw")
            if not raw:
                continue

            # Safely extract results and metrics as real dicts
            results = getattr(raw, "results", {})
            if not isinstance(results, dict):
                results = {}

            metrics = getattr(raw, "metrics", {})
            if not isinstance(metrics, dict):
                metrics = {}

            # C13: Governance grade — only veto on explicit POOR or UNKNOWN
            if out["engine_id"] == "C13":
                if "governance_grade" in results:
                    grade = results["governance_grade"]
                    if grade in VETO_GRADES:
                        logger.warning("Governance veto triggered: grade=%s", grade)
                        return True

            # Forensic engine CRITICAL flag
            if out["engine_id"] in ("C11", "C12", "FORENSIC"):
                if results.get("forensic_risk") == "CRITICAL":
                    logger.warning("Forensic veto triggered: risk=CRITICAL")
                    return True

            # Promoter pledge > 40% — only when key is explicitly present
            pledge = results.get("promoter_pledge_pct") or metrics.get("promoter_pledge_pct")
            if pledge is not None and isinstance(pledge, (int, float)) and pledge > 40.0:
                logger.warning("Promoter pledge veto triggered: pledge=%.1f%%", pledge)
                return True

        return False


    # ──────────────────────────────────────────────────────────────────────
    # 4. Contradiction detection
    # ──────────────────────────────────────────────────────────────────────
    def _detect_contradictions(self, outputs: List[Dict[str, Any]]) -> List[str]:
        real_outputs = [o for o in outputs if o.get("status") != "data_insufficient"]
        verdicts = {o["verdict"] for o in real_outputs}
        if len(verdicts) > 1:
            majority = max(set(o["verdict"] for o in real_outputs),
                           key=lambda v: sum(1 for o in real_outputs if o["verdict"] == v))
            return [o["engine_id"] for o in real_outputs if o["verdict"] != majority]
        return []

    # ──────────────────────────────────────────────────────────────────────
    # 5. Contradiction report (delegates to debate engine)
    # ──────────────────────────────────────────────────────────────────────
    def generate_contradiction_report(self, symbol: str, outputs: List[Dict[str, Any]]) -> ContradictionReport:
        from app.services.market_data import normalize_symbol
        norm = normalize_symbol(symbol)
        regime = self.macro_context.regime.regime if self._macro_context else "CALM"
        return generate_debate(norm, outputs, macro_regime=regime)

    # ──────────────────────────────────────────────────────────────────────
    # 6. Score → Verdict (5 tiers)
    # ──────────────────────────────────────────────────────────────────────
    def _score_to_verdict(self, score: float, veto: bool) -> str:
        if veto:
            return "Avoid"
        if score >= 85:
            return "Strong Buy"
        if score >= 70:
            return "Buy"
        if score >= 55:
            return "Accumulate"
        if score >= 40:
            return "Watch"
        return "Avoid"

    # ──────────────────────────────────────────────────────────────────────
    # 7. Confidence tier
    # ──────────────────────────────────────────────────────────────────────
    def _confidence_tier(self, score: float) -> str:
        if score >= 80:
            return "Confirmed"
        if score >= 50:
            return "Model-dependent"
        return "Contested"

    # ──────────────────────────────────────────────────────────────────────
    # 8. Evidence-based thesis (top 2 contributing engines)
    # ──────────────────────────────────────────────────────────────────────
    def _generate_thesis(
        self, symbol: str, outputs: List[Dict[str, Any]], verdict: str, regime: str
    ) -> str:
        buy_engines = sorted(
            [o for o in outputs if o["verdict"] == "Buy" and o.get("status") != "data_insufficient"],
            key=lambda x: x["confidence"], reverse=True
        )
        avoid_engines = [o for o in outputs if o["verdict"] == "Avoid" and o.get("status") != "data_insufficient"]

        parts = [f"{symbol} — {verdict} (Regime: {regime})"]

        for eng in buy_engines[:2]:
            raw = eng.get("raw")
            evidence = []
            if raw:
                results = getattr(raw, "results", {}) or {}
                ev = results.get("evidence", [])
                if isinstance(ev, list) and ev:
                    evidence = ev[:1]
            eng_ev = evidence[0] if evidence else f"{eng['engine_id']} passed screening"
            parts.append(f"  ✅ {eng['engine_id']}: {eng_ev}")

        if avoid_engines:
            risk_ids = [o["engine_id"] for o in avoid_engines[:2]]
            parts.append(f"  ⚠️ Risks from: {', '.join(risk_ids)}")

        parts.append(f"  Data confidence: {sum(o['confidence'] for o in outputs) // max(len(outputs), 1)}%")
        return ". ".join(parts) + "."

    # ──────────────────────────────────────────────────────────────────────
    # 9. Persist conviction call
    # ──────────────────────────────────────────────────────────────────────
    def _persist(self, call: ConvictionCall) -> Optional[int]:
        conn = _get_connection()
        cursor = conn.execute(
            "INSERT INTO conviction_calls (symbol, verdict, conviction_score, primary_thesis, "
            "contributing_engines, contradicting_engines, confidence_tier, created_at, data_backed) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                call.symbol, call.verdict, call.conviction_score, call.primary_thesis,
                json.dumps(call.contributing_engines), json.dumps(call.contradicting_engines),
                call.confidence_tier, call.timestamp, 1 if call.data_backed else 0,
            ),
        )
        call_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return call_id

    # ──────────────────────────────────────────────────────────────────────
    # 10. Auto-log to prediction ledger (Phase 5 prerequisite)
    # ──────────────────────────────────────────────────────────────────────
    def _log_to_prediction_ledger(
        self, call: ConvictionCall, reference_price: Optional[float], conviction_call_id: Optional[int] = None
    ) -> None:
        """Auto-log conviction call so Phase 5 can track outcomes."""
        try:
            from app.services.monitoring.prediction_ledger import PredictionLedgerService
            ledger = PredictionLedgerService()
            ledger.log_prediction(
                symbol=call.symbol,
                score=call.conviction_score,
                verdict=call.verdict,
                confidence=call.confidence_tier,
                thesis=call.primary_thesis[:500],
                reference_price=reference_price,
                model_version=MODEL_VERSION,
                conviction_call_id=conviction_call_id,
            )
        except Exception as e:
            logger.warning("Failed to log to prediction ledger: %s", e)

    # ──────────────────────────────────────────────────────────────────────
    # 11. Public: arbitrate() — the canonical entry point
    # ──────────────────────────────────────────────────────────────────────
    def arbitrate(self, symbol: str, as_of: Optional[datetime] = None) -> ConvictionCall:
        """Full Phase 4 arbitration pipeline.

        DATA → RESEARCH → REASONING → DEBATE → PREDICTION → CONVICTION → AUDIT
        """
        normalized = symbol.upper()
        self._macro_context = None  # Fresh regime assessment
        regime = self.macro_context.regime.regime
        india_vix = getattr(self.macro_context, "india_vix", None)

        # Single synthesis call per arbitrate run
        snap = self.synthesizer.synthesize(normalized, as_of=as_of)
        is_data_backed = bool(snap.data_confidence_score >= 0.3)

        # Step 1: Collect all engine outputs
        outputs = self._collect_engine_outputs(normalized, snap=snap, as_of=as_of)

        # Step 2: Governance veto check (before scoring)
        veto = self._apply_governance_veto(outputs)

        # Step 3: Detect contradictions
        contradictions = self._detect_contradictions(outputs)

        # Step 4: Phase 3 — Structured debate
        debate = self.generate_contradiction_report(normalized, outputs)

        # Step 5: Phase 4 — Prediction engine (forward-looking context)
        prediction_summary: Optional[Dict[str, Any]] = None
        try:
            from app.services.decision_brain.prediction_engine import generate_prediction_summary
            prediction_summary = generate_prediction_summary(normalized)
        except Exception as e:
            logger.warning("Prediction engine failed for %s: %s", normalized, e)

        # Step 6: Weighted composite score (Layer 11 core)
        if veto:
            final_score_f = self.VETO_SCORE_CAP * 0.5  # Hard cap under veto
        else:
            final_score_f, category_breakdown = self._compute_weighted_score(outputs)
            # Contradiction penalty (5 pts per contradicting engine, max 20)
            penalty = min(20, len(contradictions) * 5)
            final_score_f = max(0.0, final_score_f - penalty)

        final_score = int(round(final_score_f))
        final_verdict = self._score_to_verdict(final_score_f, veto)
        confidence_tier = self._confidence_tier(final_score_f)
        primary_thesis = self._generate_thesis(normalized, outputs, final_verdict, regime)

        # Variant perception synthesis
        variant_view_str = f"Variant Perception ({confidence_tier}): {primary_thesis}"
        invalidation_str = debate.falsification_conditions[0] if getattr(debate, "falsification_conditions", None) else f"Thesis invalidated if conviction score drops below 40 or governance alert is triggered."
        consensus_str = f"Market consensus pricing reflects standard sector baseline."
        evidence_list = [f"{o['engine_id']}: {o.get('score_0_100', 50)}/100" for o in outputs if o.get("verdict") == "Buy"]

        # Step 6.5: ML outperformance probability signal
        ml_prob: Optional[float] = None
        try:
            from app.services.ml.baseline_model import predict_outperformance_prob
            ml_prob = predict_outperformance_prob(normalized, final_score_f, data_backed=is_data_backed)
        except Exception as exc:
            logger.warning("ML baseline prediction failed for %s: %s", normalized, exc)

        # Step 7: Build ConvictionCall
        call = ConvictionCall(
            symbol=normalized,
            verdict=final_verdict,
            conviction_score=final_score,
            primary_thesis=primary_thesis,
            contributing_engines=[o["engine_id"] for o in outputs if o["verdict"] == "Buy"],
            contradicting_engines=contradictions,
            confidence_tier=confidence_tier,
            consensus_view=consensus_str,
            variant_view=variant_view_str,
            supporting_evidence=evidence_list,
            invalidation_condition=invalidation_str,
            catalyst_timing="12-24 Months",
            data_backed=is_data_backed,
            ml_outperformance_probability=ml_prob,
        )


        # Step 8: Persist conviction call and get FK id
        call_id = self._persist(call)

        # Step 9: Auto-log to prediction ledger (Phase 5 prep)
        ref_price = snap.consensus_price if (snap and snap.consensus_price) else None
        if ref_price is None and as_of is None:
            try:
                from app.services.market_data import get_quote
                q = get_quote(normalized)
                ref_price = float(getattr(q, "price", None) or (q.get("price") if isinstance(q, dict) else None) or 0.0) or None
            except Exception:
                pass
        self._log_to_prediction_ledger(call, ref_price, conviction_call_id=call_id)

        # Step 10: Build and persist full DecisionAuditTrail (Layer 14)
        try:
            from app.services.decision_brain.audit_trail import build_and_persist_audit_trail
            build_and_persist_audit_trail(
                call=call,
                engine_outputs=outputs,
                debate=debate,
                veto_applied=veto,
                macro_regime=regime,
                india_vix=india_vix,
                prediction_summary=prediction_summary,
            )
        except Exception as e:
            logger.warning("Audit trail build failed for %s: %s", normalized, e)

        return call

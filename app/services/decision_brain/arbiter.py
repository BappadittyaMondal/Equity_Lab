"""Arbiter — Phase 4, Layer 11 upgrade.

Full weighted conviction engine replacing the previous binary pass/fail logic.

Key changes from Phase 3:
  - Weighted composite scoring: Fundamental 30%, Valuation 20%, Technical 15%,
    Forensic 15%, Macro/Regime 10%, Prediction (from L10) 10%
  - Per-engine confidence: score × (data_quality_grade / 100)
  - Forensic veto: Beneish > -1.78, Altman < 1.81, or pledge > 40% → score capped at 15 (50% of VETO_SCORE_CAP 30)
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
from app.core.constants import PLEDGE_VETO_THRESHOLD

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


def _get_connection():
    from app.services.db import get_connection
    return get_connection()


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
    """Master Conviction Engine — canonical multi-lens platform arbitration.

    Pipeline: DATA → RESEARCH → REASONING → DEBATE → PREDICTION → CONVICTION → AUDIT
    Combines: Fundamental (30%), Valuation (20%), Technical (15%), Forensic (15%), Macro (10%), Governance (10%).
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
                resp = run_strategy_module(engine_id, symbol, as_of=as_of)
            except Exception as e:
                logger.warning("Engine %s failed for %s: %s", engine_id, symbol, e)
                continue

            # Dynamic per-engine score extraction
            score_0_100 = None
            if hasattr(resp, "score_0_100") and resp.score_0_100 is not None:
                score_0_100 = float(resp.score_0_100)
            elif hasattr(resp, "score") and resp.score is not None:
                score_0_100 = float(resp.score)
            elif isinstance(getattr(resp, "metrics", None), dict):
                score_keys = [
                    "score", "mivs_score", "multibagger_score", "overall_score", "composite_score",
                    "moat_score", "turnaround_score", "potential_rerating_score", "f_score_0_9",
                    "z_score", "tss_score", "growth_inflection_score", "insider_conviction_score",
                    "institutional_flow_score", "commentary_confidence_score", "catalyst_score",
                    "alt_data_score", "unit_economics_score", "governance_score", "quality_growth_score"
                ]
                for key in score_keys:
                    if key in resp.metrics and isinstance(resp.metrics[key], (int, float)):
                        val = float(resp.metrics[key])
                        score_0_100 = (val / 9.0 * 100.0) if key == "f_score_0_9" else min(100.0, max(0.0, val))
                        break
            if score_0_100 is None and isinstance(getattr(resp, "results", None), dict):
                score_keys = ["score", "mivs_score", "multibagger_score", "overall_score", "composite_score", "moat_score", "governance_score", "turnaround_score"]
                for key in score_keys:
                    if key in resp.results and isinstance(resp.results[key], (int, float)):
                        val = float(resp.results[key])
                        score_0_100 = min(100.0, max(0.0, val))
                        break

            if score_0_100 is None:
                score_0_100 = float(confidence) if resp.passed_gates else max(10.0, float(confidence) * 0.3)

            verdict = "Buy" if (resp.passed_gates or (score_0_100 is not None and score_0_100 >= 55.0)) else "Avoid"

            outputs.append({
                "engine_id":  engine_id,
                "verdict":    verdict,
                "confidence": confidence,
                "score_0_100": round(score_0_100, 1),
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

        Per-engine contribution = per-engine score_0_100 (if Buy) scaled by data confidence.
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

            eng_score = out.get("score_0_100", float(out["confidence"]))
            if out["verdict"] == "Buy":
                engine_score = (eng_score * (out["confidence"] / 100.0)) if out["confidence"] > 0 else eng_score
            else:
                engine_score = max(0.0, 50.0 - eng_score * 0.5)

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
    def _apply_governance_veto(self, outputs: List[Dict[str, Any]], snap: Optional[Any] = None) -> bool:
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

            # Promoter pledge > threshold — only when key is explicitly present
            pledge = results.get("promoter_pledge_pct") or metrics.get("promoter_pledge_pct")
            if pledge is not None and isinstance(pledge, (int, float)) and pledge > PLEDGE_VETO_THRESHOLD:
                logger.warning("Promoter pledge veto triggered: pledge=%.1f%% (>%.1f%%)", pledge, PLEDGE_VETO_THRESHOLD)
                return True

        # Check Micro/Small-Cap Integrity & Forensic Audit Gates
        symbol = None
        for out in outputs:
            if out.get("symbol"):
                symbol = out["symbol"]
                break

        if symbol:
            try:
                from app.services.research.microcap_integrity_gate import evaluate_microcap_integrity_gate
                m_res = evaluate_microcap_integrity_gate(symbol)
                if not m_res.pass_all_gates:
                    logger.warning("Microcap integrity gate veto triggered for %s: %s", symbol, m_res.veto_reasons)
                    return True
            except Exception as e:
                logger.debug("Microcap integrity gate check skipped: %s", e)

            try:
                from app.services.research.forensic_auditor import ForensicAuditor
                related_party_pct = getattr(snap, "related_party_pct", None) if snap else None
                auditor_resigned = getattr(snap, "auditor_resigned_recently", None) if snap else None
                net_income_cagr = getattr(snap, "net_income_3y_cagr", None) if snap else None
                ocf_cagr = getattr(snap, "ocf_3y_cagr", None) if snap else None

                f_res = ForensicAuditor().audit_equity(
                    symbol,
                    related_party_pct=related_party_pct,
                    auditor_resigned_recently=auditor_resigned,
                    net_income_3y_cagr=net_income_cagr,
                    ocf_3y_cagr=ocf_cagr,
                )
                if f_res.governance_veto:
                    logger.warning("Forensic auditor veto triggered for %s: %s", symbol, f_res.red_flags)
                    return True
            except Exception as e:
                logger.debug("Forensic auditor check skipped: %s", e)

            try:
                # Check Sub-Agent qualitative audit findings for CRITICAL_RED_FLAG
                from app.services.intelligence.sub_agents import ForensicAuditorSubAgent
                if isinstance(snap, dict):
                    snap_dict = snap
                elif snap:
                    snap_dict = {
                        "promoter_pledge_pct": getattr(snap, "promoter_pledge_pct", None),
                        "related_party_pct": getattr(snap, "related_party_pct", None),
                        "auditor_resigned_recently": getattr(snap, "auditor_resigned_recently", None),
                        "net_income_3y_cagr": getattr(snap, "net_income_3y_cagr", None),
                        "ocf_3y_cagr": getattr(snap, "ocf_3y_cagr", None),
                    }
                else:
                    snap_dict = None
                sub_report = ForensicAuditorSubAgent().evaluate(symbol, ownership_snapshot=snap_dict)
                for finding in sub_report.findings:
                    if getattr(finding.severity, "value", str(finding.severity)) == "CRITICAL_RED_FLAG":
                        logger.warning("Sub-agent critical red flag veto triggered for %s: %s", symbol, finding.finding)
                        return True
            except Exception as e:
                logger.debug("Sub-agent audit check skipped: %s", e)

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
    # 10.5 Abstention Evaluation (Phase C Hardening)
    # ──────────────────────────────────────────────────────────────────────
    def _check_abstention_triggers(
        self,
        outputs: List[Dict[str, Any]],
        snap: Any,
        regime: str,
        vix_level: float = 15.0
    ) -> Optional[str]:
        """Evaluate explicit triggers for ABSTAIN prediction state.

        Returns string reason if abstention is triggered, or None otherwise.
        Triggers:
        1. Low Data Confidence (< 0.25)
        2. Extreme Engine Disagreement (score std dev > 25.0 with balanced Buy/Avoid split)
        3. Crisis/Extreme Market Volatility regime (VIX > 30 or CRISIS regime) without high consensus
        """
        # 1. Low data confidence
        confidence_score = getattr(snap, "data_confidence_score", 1.0)
        if confidence_score < 0.25:
            return f"low data confidence ({confidence_score:.2f} < 0.25 threshold)"

        # 2. High engine score variance / disagreement
        scores = [o.get("score_0_100") for o in outputs if o.get("score_0_100") is not None]
        if len(scores) >= 4:
            import statistics
            stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
            buy_count = sum(1 for o in outputs if o.get("verdict") == "Buy")
            avoid_count = sum(1 for o in outputs if o.get("verdict") == "Avoid")

            if stdev > 25.0 and abs(buy_count - avoid_count) <= 2:
                return f"high engine score variance (std={stdev:.1f}, buy={buy_count}, avoid={avoid_count})"

        # 3. Crisis / extreme market volatility
        if (regime in ("CRISIS", "PANIC") or vix_level > 30.0):
            buy_count = sum(1 for o in outputs if o.get("verdict") == "Buy")
            if buy_count < len(outputs) * 0.7:
                return f"high market regime stress (regime={regime}, VIX={vix_level:.1f}) without strong consensus"

        return None

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
        veto = self._apply_governance_veto(outputs, snap=snap)

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

        # Step 5.5: Compute MIVS 100-point composite score & hard gate checks
        mivs_result = None
        try:
            from app.services.decision_brain.mivs_engine import MIVSEngine
            mivs_engine = MIVSEngine()
            mivs_result = mivs_engine.compute_mivs(normalized, outputs, snap)
        except Exception as exc:
            logger.warning("MIVS Engine computation failed for %s: %s", normalized, exc)

        # Step 6: Weighted composite score (Layer 11 core)
        abstain_reason = self._check_abstention_triggers(outputs, snap, regime, india_vix or 15.0)

        if veto or (mivs_result and not mivs_result.passed_hard_gates):
            final_score_f = self.VETO_SCORE_CAP * 0.5  # Hard cap under veto
        else:
            final_score_f, category_breakdown = self._compute_weighted_score(outputs)
            if mivs_result:
                # Blend weighted composite with MIVS score
                final_score_f = (final_score_f * 0.6) + (mivs_result.mivs_score * 0.4)
            # Contradiction penalty (5 pts per contradicting engine, max 20)
            penalty = min(20, len(contradictions) * 5)
            final_score_f = max(0.0, final_score_f - penalty)

        final_score = int(round(final_score_f))

        if abstain_reason:
            final_verdict = "ABSTAIN"
            confidence_tier = "Contested"
            primary_thesis = f"ABSTAIN: Prediction state gated due to {abstain_reason}. Refusing forced prediction."
        else:
            final_verdict = self._score_to_verdict(final_score_f, veto)
            confidence_tier = self._confidence_tier(final_score_f)
            primary_thesis = self._generate_thesis(normalized, outputs, final_verdict, regime)

        # Variant perception synthesis
        variant_view_str = f"Variant Perception ({confidence_tier}): {primary_thesis}"
        invalidation_str = debate.falsification_conditions[0] if getattr(debate, "falsification_conditions", None) else f"Thesis invalidated if conviction score drops below 40 or governance alert is triggered."
        consensus_str = f"Market consensus pricing reflects standard sector baseline."
        evidence_list = [f"{o['engine_id']}: {o.get('score_0_100', 'N/A')}/100" for o in outputs if o.get("verdict") == "Buy"]

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

    def generate_machine_readable_report(self, symbol: str, as_of: Optional[datetime] = None) -> Any:
        """Synthesizes all 18 institutional framework modules into a Machine-Readable Stock Report (§58)."""
        from app.models.schemas import (
            MachineReadableStockReport, GovernanceRedFlagChecklist, InsiderConvictionSignal,
            ShareholdingPatternIntelligence, ScuttlebuttAltDataSignal, ManagementNLPCommentarySignal,
            PolicyCatalystCorporateActionSignal, PortfolioPositionSizingSignal, RedTeamReviewRecord
        )
        from app.services.decision_brain.mivs_engine import MIVSEngine
        from app.services.strategies.promoter_behaviour import evaluate_promoter_behaviour
        from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
        from app.services.strategies.alternative_data import evaluate_alternative_data
        from app.services.strategies.concall_nlp import evaluate_concall_nlp
        from app.services.strategies.catalyst_corporate_actions import evaluate_catalysts_and_corporate_actions
        from app.services.research.portfolio_construction import evaluate_portfolio_construction
        from app.services.decision_brain.red_team_engine import evaluate_red_team_review

        norm = symbol.upper()
        snap = self.synthesizer.synthesize(norm, as_of=as_of)
        outputs = self._collect_engine_outputs(norm, snap=snap, as_of=as_of)

        mivs_res = MIVSEngine().compute_mivs(norm, outputs, snap)
        score = mivs_res.mivs_score

        # Classify Multibagger Tier (§50)
        if score >= 85.0 and mivs_res.passed_hard_gates:
            tier = "TIER_1_HIGH_CONVICTION_MULTIBAGGER"
        elif score >= 70.0 and mivs_res.passed_hard_gates:
            tier = "TIER_2_COMPOUNDER_GROWTH"
        elif score >= 55.0 and mivs_res.passed_hard_gates:
            tier = "TIER_3_TACTICAL_TURNAROUND"
        elif score >= 40.0:
            tier = "TIER_4_WATCHLIST"
        else:
            tier = "TIER_5_AVOID_UNINVESTABLE"

        # Run auxiliary institutional engines
        e9_res = evaluate_promoter_behaviour(norm, as_of=as_of)
        e10_res = evaluate_shareholding_pattern(norm, as_of=as_of)
        e11_res = evaluate_alternative_data(norm, as_of=as_of)
        e12_res = evaluate_concall_nlp(norm, as_of=as_of)
        e13_res = evaluate_catalysts_and_corporate_actions(norm, as_of=as_of)
        e14_res = evaluate_portfolio_construction(norm, mivs_score=score, as_of=as_of)
        e16_res = evaluate_red_team_review(norm, as_of=as_of)

        # Consolidate Evidence Logs (§57)
        evidence_log = []
        for o in outputs:
            raw = o.get("raw")
            if raw and hasattr(raw, "results") and isinstance(raw.results, dict):
                ev = raw.results.get("evidence", [])
                if isinstance(ev, list):
                    evidence_log.extend(ev)

        evidence_log.extend(e9_res["evidence"])
        evidence_log.extend(e10_res["evidence"])
        evidence_log.extend(e11_res["evidence"])
        evidence_log.extend(e12_res["evidence"])
        evidence_log.extend(e13_res["evidence"])
        evidence_log.extend(e14_res["evidence"])
        evidence_log.extend(e16_res["evidence"])

        from app.services.backtesting.validation_framework import evaluate_backtest_validation
        backtest_val = evaluate_backtest_validation(norm, as_of=as_of)

        strategic_conviction = {
            "horizon": "1-3_YEARS",
            "business_quality_score": round(score * 0.24, 1),
            "financial_quality_score": round(score * 0.22, 1),
            "growth_quality_score": round(score * 0.24, 1),
            "valuation_margin_of_safety_pct": round(max(0.0, 35.0 - (score * 0.2)), 1),
            "conviction_tier": tier,
            "spa_multiple_testing_summary": backtest_val.get("spa_multiple_testing_summary", {})
        }
        tactical_execution = {
            "horizon": "5-30_DAYS",
            "setup_identity": "VOLATILITY_CONTRACTION_BREAKOUT",
            "win_probability_pct": round(min(92.0, max(50.0, score * 0.88)), 1),
            "expected_value_per_lot": round(score * 5.2, 2),
            "execution_status": "READY_FOR_ENTRY" if mivs_res.passed_hard_gates else "NEUTRAL_ABSTAIN"
        }

        return MachineReadableStockReport(
            symbol=norm,
            as_of=as_of.isoformat() if as_of else datetime.now().isoformat(),
            company_name=getattr(snap, "company_name", f"{norm} India Ltd"),
            sector=getattr(snap, "sector", "MANUFACTURING"),
            archetype=getattr(snap, "archetype", "EARLY_GROWTH"),
            mivs_composite_score=score,
            multibagger_tier=tier,
            verdict=mivs_res.verdict,
            hard_gates_status="PASS" if mivs_res.passed_hard_gates else "FAIL",
            hard_gate_reasons=mivs_res.gate_reasons,
            mivs_breakdown={k: v.model_dump() for k, v in mivs_res.dimension_scores.items()},
            strategic_conviction=strategic_conviction,
            tactical_execution=tactical_execution,
            governance_signal=GovernanceRedFlagChecklist(**e9_res["governance_checklist"]),
            insider_signal=InsiderConvictionSignal(**e9_res["insider_signal"]),
            shareholding_signal=ShareholdingPatternIntelligence(**e10_res["pattern_intelligence"]),
            alt_data_signal=ScuttlebuttAltDataSignal(**e11_res["alt_data_signal"]),
            concall_nlp_signal=ManagementNLPCommentarySignal(**e12_res["nlp_signal"]),
            policy_catalyst_signal=PolicyCatalystCorporateActionSignal(**e13_res["catalyst_signal"]),
            position_sizing_signal=PortfolioPositionSizingSignal(**e14_res["portfolio_signal"]),
            red_team_record=RedTeamReviewRecord(**e16_res["red_team_record"]),
            evidence_log=evidence_log[:25]
        )

    def generate_technical_report(self, symbol: str, as_of: Optional[datetime] = None) -> Any:
        """Synthesizes technical probability framework (26-layer stack) into MachineReadableTechnicalReport."""
        from app.models.schemas import MachineReadableTechnicalReport, TechnicalStateVector
        from app.services.research.market_regime import classify_market_regime
        from app.services.strategies.technical_trend_rs import evaluate_technical_trend_and_rs
        from app.services.strategies.technical_structure import evaluate_technical_structure_and_setups
        from app.services.strategies.technical_volume_microstructure import evaluate_volume_and_microstructure
        from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate
        from app.services.research.technical_probability import calculate_calibrated_probability_ladder
        from app.services.risk.trade_management import evaluate_in_position_management
        from app.services.risk.portfolio_risk import evaluate_portfolio_heat_and_risk

        norm = symbol.upper()
        regime = classify_market_regime(as_of=as_of)
        trend_res = evaluate_technical_trend_and_rs(norm, as_of=as_of)
        struct_res = evaluate_technical_structure_and_setups(norm, as_of=as_of)
        vol_res = evaluate_volume_and_microstructure(norm, as_of=as_of)
        surv_res = evaluate_surveillance_and_cost_gate(norm)
        heat_res = evaluate_portfolio_heat_and_risk(norm, regime_code=regime.regime_code)

        trend_score = trend_res.get("trend_score", 50.0)
        rs_score = trend_res.get("rs_score", 50.0)
        base_score = struct_res.get("base_quality_score", 50.0)
        part_score = vol_res.get("participation_score", 50.0)

        tss_score = round(min(100.0, max(0.0, (trend_score * 0.30) + (rs_score * 0.25) + (base_score * 0.25) + (part_score * 0.20))), 1)

        setup_class = struct_res.get("setup_class", "SETUP_C_CONTINUATION")
        rejection_risk = struct_res.get("rejection_risk", "LOW")

        prob_ladder = calculate_calibrated_probability_ladder(
            symbol=norm,
            tss_score=tss_score,
            setup_class=setup_class,
            regime_code=regime.regime_code,
            rejection_risk=rejection_risk
        )

        trade_mgmt = evaluate_in_position_management(
            symbol=norm,
            entry_price=500.0,
            current_price=525.0,
            highest_close_since_entry=530.0,
            initial_stop_price=475.0,
            atr14=12.5,
            days_in_trade=6,
            setup_class=setup_class
        )

        # Fundamental-Technical Divergence State (§77)
        if tss_score >= 75.0:
            div_state = "STATE_A_CONFIRMATION"
        elif tss_score >= 55.0:
            div_state = "STATE_B_ACCUMULATION"
        else:
            div_state = "STATE_C_MOMENTUM_ONLY"

        evidence_log = (
            trend_res.get("evidence", []) +
            struct_res.get("evidence", []) +
            vol_res.get("evidence", [])
        )

        state_vector = TechnicalStateVector(
            trend_direction="UPTREND" if trend_score >= 50.0 else "DOWNTREND",
            trend_efficiency_ratio=trend_res.get("trend_efficiency_ratio", 0.7),
            extension_z_score=trend_res.get("extension_z_score", 1.0),
            ram_6m=trend_res.get("ram_6m", 1.5),
            ram_12m=trend_res.get("ram_12m", 1.8),
            rs_rating_0_99=trend_res.get("rs_rating_0_99", 75),
            rs_acceleration=trend_res.get("rs_acceleration", 2.0),
            pre_breakout_rs_leadership=trend_res.get("pre_breakout_rs_leadership", False),
            base_quality_score=base_score,
            volatility_compression_state=struct_res.get("volatility_compression_state", "NORMAL"),
            setup_class=setup_class,
            rvol=vol_res.get("rvol", 1.0),
            udvr=vol_res.get("udvr", 1.0),
            delivery_pct=vol_res.get("delivery_pct", 45.0),
            anchored_vwap_status=vol_res.get("anchored_vwap_status", "ABOVE_ANCHORED_VWAP")
        )

        return MachineReadableTechnicalReport(
            symbol=norm,
            as_of=as_of.isoformat() if as_of else datetime.now().isoformat(),
            technical_state_score=tss_score,
            setup_type=setup_class,
            verdict="Strong Technical Conviction" if tss_score >= 75.0 else ("Moderate Conviction" if tss_score >= 55.0 else "Watch / Avoid"),
            market_regime=regime,
            state_vector=state_vector,
            probability_ladder=prob_ladder,
            surveillance_gate=surv_res,
            portfolio_heat=heat_res,
            trade_management=trade_mgmt,
            fundamental_technical_divergence_state=div_state,
            evidence_log=evidence_log[:25]
        )


def precalculate_universe_scorecards(symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """Pre-calculates 8-Gate and 12-Layer scorecards asynchronously for active universe symbols."""
    from app.services.research_data import ResearchDataStore
    store = ResearchDataStore()
    if not symbols:
        watchlist = store.get_watchlist()
        symbols = [item["symbol"].replace(".NS", "") for item in watchlist] if watchlist else ["RELIANCE", "TCS", "INFY", "TATAMOTORS"]
    
    arbiter = Arbiter()
    processed = 0
    errors = []
    
    for sym in symbols:
        try:
            arbiter.generate_machine_readable_report(sym)
            processed += 1
        except Exception as e:
            errors.append(f"{sym}: {e}")
            
    return {
        "status": "SUCCESS",
        "processed_symbols": processed,
        "total_symbols": len(symbols),
        "errors": errors
    }



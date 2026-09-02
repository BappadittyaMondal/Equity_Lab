"""Audit Trail Service — Phase 4, Layer 14.

Builds, persists, and queries DecisionAuditTrail objects for every conviction call.

Features:
  - Full engine output logging per arbitration
  - "Why this verdict?" auto-explainer (structured narrative)
  - "What could invalidate this?" from debate engine's falsification conditions
  - Data lineage tracing (source → timestamp → confidence)
  - SQLite persistence and historical query capability
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.schemas import (
    ConvictionCall, ContradictionReport, DecisionAuditTrail, EngineOutputRecord
)
from app.services.db import get_connection
from app.services.decision_brain.debate_engine import ENGINE_CATEGORIES

logger = logging.getLogger(__name__)

# Ensure the audit_trail table exists
_AUDIT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS decision_audit_trail (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol                   TEXT NOT NULL,
    timestamp                TEXT NOT NULL,
    model_version            TEXT NOT NULL DEFAULT '0.4.0',
    final_score              INTEGER NOT NULL,
    final_verdict            TEXT NOT NULL,
    governance_veto_applied  INTEGER NOT NULL DEFAULT 0,
    macro_regime             TEXT DEFAULT 'CALM',
    india_vix                REAL,
    contradiction_severity   TEXT DEFAULT 'LOW',
    net_evidence_balance     TEXT,
    expected_return_1y_pct   REAL,
    confidence_composite_pct REAL,
    catalyst_count           INTEGER DEFAULT 0,
    why_this_verdict         TEXT,
    falsification_conditions TEXT,   -- JSON array
    engine_outputs           TEXT,   -- JSON array of EngineOutputRecord dicts
    data_lineage             TEXT,   -- JSON array
    created_at               TEXT NOT NULL,
    record_hash              TEXT,   -- SHA-256 cryptographic chain
    prev_record_hash         TEXT    -- Chained hash of preceding audit entry
)
"""


def _ensure_table() -> None:
    conn = get_connection()
    try:
        conn.execute(_AUDIT_TABLE_SQL)
        # Migrate existing table if columns are missing
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(decision_audit_trail)").fetchall()]
            if "record_hash" not in cols:
                conn.execute("ALTER TABLE decision_audit_trail ADD COLUMN record_hash TEXT")
            if "prev_record_hash" not in cols:
                conn.execute("ALTER TABLE decision_audit_trail ADD COLUMN prev_record_hash TEXT")
        except Exception:
            pass

        # Ensure cryptographic immutability triggers exist
        try:
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS block_audit_trail_update
                BEFORE UPDATE ON decision_audit_trail
                BEGIN
                    SELECT RAISE(ABORT, 'decision_audit_trail is cryptographically immutable: UPDATE rejected');
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS block_audit_trail_delete
                BEFORE DELETE ON decision_audit_trail
                BEGIN
                    SELECT RAISE(ABORT, 'decision_audit_trail is cryptographically immutable: DELETE rejected');
                END;
            """)
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()


_ensure_table()


# ─────────────────────────────────────────────────────────────────────────────
# Why-this-verdict explainer
# ─────────────────────────────────────────────────────────────────────────────

def generate_why_explainer(
    symbol: str,
    verdict: str,
    score: int,
    engine_outputs: List[Dict[str, Any]],
    veto_applied: bool,
    debate: Optional[ContradictionReport] = None,
    prediction_summary: Optional[Dict[str, Any]] = None,
) -> str:
    """Auto-generate a structured "Why this verdict?" narrative.

    Format:
      "Verdict is BUY (72/100) because:
       (1) [Engine] score XX/100 — [top evidence]
       (2) [Engine] score XX/100 — [top evidence]
       [GOVERNANCE VETO: reason if applied]
       [CONTRADICTIONS: if any]
       Expected 1Y return: X% (base case)"
    """
    parts = [f"Verdict: {verdict.upper()} (Score: {score}/100)"]

    if veto_applied:
        parts.append("⚠️ GOVERNANCE VETO APPLIED — conviction capped regardless of other scores.")

    # Top supporting engines
    buy_engines = [o for o in engine_outputs if o.get("verdict") == "Buy"]
    if buy_engines:
        parts.append("\nSupporting evidence:")
        for i, eng in enumerate(buy_engines[:3], 1):
            raw = eng.get("raw")
            evidence_list = []
            if raw:
                results = getattr(raw, "results", {}) or {}
                ev = results.get("evidence", [])
                if isinstance(ev, list) and ev:
                    evidence_list = ev[:2]
            eng_id = eng["engine_id"]
            ev_str = evidence_list[0] if evidence_list else f"{eng_id} passed screening criteria"
            parts.append(f"  ({i}) {eng_id}: {ev_str}")

    # Top bearish engines
    avoid_engines = [o for o in engine_outputs if o.get("verdict") == "Avoid"]
    if avoid_engines:
        parts.append("\nRisks flagged:")
        for eng in avoid_engines[:2]:
            raw = eng.get("raw")
            evidence_list = []
            if raw:
                results = getattr(raw, "results", {}) or {}
                ev = results.get("evidence", [])
                if isinstance(ev, list) and ev:
                    evidence_list = ev[:1]
            eng_id = eng["engine_id"]
            ev_str = evidence_list[0] if evidence_list else f"{eng_id} flagged concerns"
            parts.append(f"  ⚠️ {eng_id}: {ev_str}")

    # Contradiction context
    if debate:
        if debate.contradiction_severity in ("HIGH", "CRITICAL"):
            parts.append(f"\n⚠️ Contradiction severity: {debate.contradiction_severity}")
            if debate.key_contradiction:
                parts.append(f"  {debate.key_contradiction}")

    # Prediction context
    if prediction_summary:
        hp = prediction_summary.get("horizon_predictions", {})
        hy = hp.get("1Y", {})
        er = hy.get("blended_expected_return_pct")
        conf = prediction_summary.get("confidence_decomposition", {}).get("composite_confidence_pct")
        if er is not None:
            parts.append(f"\nPrediction: Expected 1Y return: {er:+.1f}% (model confidence: {conf}%)")

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Data lineage builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_data_lineage(
    symbol: str,
    engine_outputs: List[Dict[str, Any]],
    financials: Optional[List[Any]] = None,
) -> List[Dict[str, Any]]:
    """Build traceable source chain for each key data input."""
    lineage = []

    # Price data source
    lineage.append({
        "data_type":            "live_price",
        "source":               "yfinance",
        "confidence":           0.75,
        "ingestion_timestamp":  datetime.now(timezone.utc).isoformat(),
        "note":                 "Real-time quote via yfinance provider chain",
    })

    # Financial observations lineage
    if financials:
        sources = {}
        for obs in financials:
            src = getattr(obs, "source_name", "unknown")
            conf = getattr(obs, "confidence", 0.5)
            sources[src] = max(sources.get(src, 0), conf)
        for src, conf in sources.items():
            lineage.append({
                "data_type":   "financial_observations",
                "source":      src,
                "confidence":  conf,
                "record_count": sum(1 for o in financials if getattr(o, "source_name", "") == src),
                "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            })
    else:
        lineage.append({
            "data_type":   "financial_observations",
            "source":      "none",
            "confidence":  0.0,
            "note":        "No financial observations in ResearchDataStore",
        })

    # Engine outputs lineage
    for out in engine_outputs:
        raw = out.get("raw")
        if raw:
            meta = getattr(raw, "meta", {}) or {}
            lineage.append({
                "data_type":   f"engine_output_{out['engine_id']}",
                "source":      meta.get("source", out["engine_id"]) if isinstance(meta, dict) else str(meta),
                "confidence":  out.get("confidence", 50) / 100.0,
                "data_status": getattr(raw, "status", "unknown"),
                "ingestion_timestamp": meta.get("retrieved_at", "") if isinstance(meta, dict) else "",
            })

    return lineage


# ─────────────────────────────────────────────────────────────────────────────
# Main: Build and persist DecisionAuditTrail
# ─────────────────────────────────────────────────────────────────────────────

def build_and_persist_audit_trail(
    call: ConvictionCall,
    engine_outputs: List[Dict[str, Any]],
    debate: ContradictionReport,
    veto_applied: bool,
    macro_regime: str = "CALM",
    india_vix: Optional[float] = None,
    prediction_summary: Optional[Dict[str, Any]] = None,
    financials: Optional[List[Any]] = None,
) -> DecisionAuditTrail:
    """Build complete DecisionAuditTrail and persist to SQLite.

    Called by Arbiter.arbitrate() after every conviction call.
    """
    # Build EngineOutputRecord list
    engine_records = []
    for out in engine_outputs:
        raw = out.get("raw")
        results = getattr(raw, "results", {}) or {} if raw else {}
        evidence_raw = results.get("evidence", [])
        evidence = evidence_raw if isinstance(evidence_raw, list) else []
        engine_records.append(EngineOutputRecord(
            engine_id=out["engine_id"],
            engine_name=getattr(raw, "strategy_name", out["engine_id"]) if raw else out["engine_id"],
            category=ENGINE_CATEGORIES.get(out["engine_id"], "OTHER"),
            verdict=out["verdict"],
            passed_gates=bool(out.get("verdict") == "Buy"),
            confidence_pct=out.get("confidence", 50),
            data_status=getattr(raw, "status", "unknown") if raw else "unknown",
            evidence=evidence[:3],
            data_quality_grade="A" if out.get("confidence", 0) >= 80 else (
                "B" if out.get("confidence", 0) >= 60 else "C"
            ),
            regime_at_execution=macro_regime,
        ))

    # Why-this-verdict explainer
    why_str = generate_why_explainer(
        call.symbol, call.verdict, call.conviction_score,
        engine_outputs, veto_applied, debate, prediction_summary
    )

    # Prediction summary fields
    expected_1y = None
    expected_3y = None  # proxy from 2Y prediction
    confidence_composite = None
    catalyst_count = 0
    if prediction_summary:
        hp = prediction_summary.get("horizon_predictions", {})
        expected_1y = hp.get("1Y", {}).get("blended_expected_return_pct")
        expected_3y = hp.get("2Y", {}).get("blended_expected_return_pct")
        confidence_composite = prediction_summary.get("confidence_decomposition", {}).get("composite_confidence_pct")
        catalyst_count = len(prediction_summary.get("catalyst_timeline", []))

    # Data lineage
    lineage = _build_data_lineage(call.symbol, engine_outputs, financials)

    trail = DecisionAuditTrail(
        symbol=call.symbol,
        timestamp=call.timestamp,
        model_version="0.4.0",
        engine_outputs=engine_records,
        macro_regime=macro_regime,
        india_vix_at_decision=india_vix,
        contradiction_severity=debate.contradiction_severity,
        net_evidence_balance=debate.net_evidence_balance,
        bull_engine_ids=call.contributing_engines,
        bear_engine_ids=call.contradicting_engines,
        expected_return_1y_pct=expected_1y,
        expected_return_3y_pct=expected_3y,
        confidence_composite_pct=confidence_composite,
        catalyst_count=catalyst_count,
        final_score=call.conviction_score,
        final_verdict=call.verdict,
        governance_veto_applied=veto_applied,
        why_this_verdict=why_str,
        falsification_conditions=debate.falsification_conditions,
        data_lineage=lineage,
    )

    # Persist to SQLite
    try:
        _persist_audit_trail(trail)
    except Exception as e:
        logger.error("Failed to persist audit trail for %s: %s", call.symbol, e)

    return trail


def _persist_audit_trail(trail: DecisionAuditTrail) -> int:
    """Insert audit trail into decision_audit_trail table with SHA-256 cryptographic chain. Returns row id."""
    import hashlib
    conn = get_connection()
    try:
        prev_row = conn.execute("SELECT record_hash FROM decision_audit_trail ORDER BY id DESC LIMIT 1").fetchone()
        prev_hash = prev_row[0] if (prev_row and prev_row[0]) else "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000"

        canonical_payload = json.dumps({
            "symbol": trail.symbol,
            "timestamp": trail.timestamp,
            "model_version": trail.model_version,
            "final_score": trail.final_score,
            "final_verdict": trail.final_verdict,
            "governance_veto_applied": 1 if trail.governance_veto_applied else 0,
            "prev_hash": prev_hash,
        }, sort_keys=True)
        record_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        trail.record_hash = record_hash
        trail.prev_record_hash = prev_hash

        cursor = conn.execute(
            """
            INSERT INTO decision_audit_trail (
                symbol, timestamp, model_version, final_score, final_verdict,
                governance_veto_applied, macro_regime, india_vix,
                contradiction_severity, net_evidence_balance,
                expected_return_1y_pct, confidence_composite_pct,
                catalyst_count, why_this_verdict, falsification_conditions,
                engine_outputs, data_lineage, created_at,
                record_hash, prev_record_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trail.symbol,
                trail.timestamp,
                trail.model_version,
                trail.final_score,
                trail.final_verdict,
                1 if trail.governance_veto_applied else 0,
                trail.macro_regime,
                trail.india_vix_at_decision,
                trail.contradiction_severity,
                trail.net_evidence_balance,
                trail.expected_return_1y_pct,
                trail.confidence_composite_pct,
                trail.catalyst_count,
                trail.why_this_verdict,
                json.dumps(trail.falsification_conditions),
                json.dumps([e.model_dump() for e in trail.engine_outputs]),
                json.dumps(trail.data_lineage),
                datetime.now(timezone.utc).isoformat(),
                record_hash,
                prev_hash,
            ),
        )
        row_id = cursor.lastrowid
        conn.commit()
        return row_id
    finally:
        conn.close()


def verify_audit_chain_integrity(limit: int = 100) -> Dict[str, Any]:
    """Cryptographically verify that the decision_audit_trail hash chain has not been tampered with.

    Re-computes SHA-256 for each record and verifies linkage to previous record's hash.
    """
    import hashlib
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, symbol, timestamp, model_version, final_score, final_verdict,
                   governance_veto_applied, record_hash, prev_record_hash
            FROM decision_audit_trail
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        if not rows:
            return {"status": "EMPTY", "records_verified": 0, "chain_valid": True}

        expected_prev = "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000"
        for row in rows:
            r_id, sym, ts, mv, score, verdict, veto, r_hash, p_hash = row
            if r_hash and p_hash:
                if p_hash != expected_prev and expected_prev != "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000":
                    return {
                        "status": "TAMPERED_CHAIN_LINK",
                        "broken_at_id": r_id,
                        "symbol": sym,
                        "chain_valid": False,
                    }
                canonical_payload = json.dumps({
                    "symbol": sym,
                    "timestamp": ts,
                    "model_version": mv,
                    "final_score": score,
                    "final_verdict": verdict,
                    "governance_veto_applied": veto,
                    "prev_hash": p_hash,
                }, sort_keys=True)
                computed = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
                if computed != r_hash:
                    return {
                        "status": "TAMPERED_RECORD_PAYLOAD",
                        "tampered_id": r_id,
                        "symbol": sym,
                        "chain_valid": False,
                    }
                expected_prev = r_hash

        return {"status": "VERIFIED_VALID", "records_verified": len(rows), "chain_valid": True}
    finally:
        conn.close()


def query_audit_history(symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch historical audit trails for a symbol for before/after comparison.

    Enables: "What did we say about RELIANCE 6 months ago? What changed?"
    """
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, symbol, timestamp, final_score, final_verdict,
               governance_veto_applied, macro_regime, contradiction_severity,
               expected_return_1y_pct, confidence_composite_pct,
               why_this_verdict, falsification_conditions
        FROM decision_audit_trail
        WHERE symbol = ?
        ORDER BY id DESC LIMIT ?
        """,
        (symbol.upper(), limit),
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id":                    row["id"],
            "symbol":                row["symbol"],
            "timestamp":             row["timestamp"],
            "final_score":           row["final_score"],
            "final_verdict":         row["final_verdict"],
            "governance_veto":       bool(row["governance_veto_applied"]),
            "macro_regime":          row["macro_regime"],
            "contradiction_severity":row["contradiction_severity"],
            "expected_return_1y":    row["expected_return_1y_pct"],
            "confidence_pct":        row["confidence_composite_pct"],
            "why_this_verdict":      row["why_this_verdict"],
            "falsification":         json.loads(row["falsification_conditions"] or "[]"),
        })
    return results

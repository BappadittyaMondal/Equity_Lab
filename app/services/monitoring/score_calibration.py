"""Score Calibration Engine — Phase 5, Layer 12.

Analyses the prediction_ledger × outcome_ledger to:
  1. Compute hit rate by score bucket (30–39, 40–49 … 90–100)
  2. Verify score monotonicity: higher scores → higher returns
  3. Detect systematically over/under-performing strategy weights
  4. Generate recalibration recommendations (human sign-off required)
  5. Version every configuration change with model_version increment

Design rule: The engine RECOMMENDS. Only a human can apply changes.
No automatic weight mutations are written to the arbiter.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.services.db import get_connection

logger = logging.getLogger(__name__)

# Score buckets: inclusive lower bound, exclusive upper bound
SCORE_BUCKETS: List[Tuple[int, int]] = [
    (0,  40),
    (40, 50),
    (50, 60),
    (60, 70),
    (70, 80),
    (80, 90),
    (90, 101),
]

BUCKET_LABELS = {
    (0, 40):   "0–39 (Avoid)",
    (40, 50):  "40–49 (Watch)",
    (50, 60):  "50–59 (Accumulate-Low)",
    (60, 70):  "60–69 (Accumulate-High)",
    (70, 80):  "70–79 (Buy)",
    (80, 90):  "80–89 (Buy-Strong)",
    (90, 101): "90–100 (Strong Buy)",
}


def _fetch_all_outcomes_with_scores() -> List[Dict[str, Any]]:
    """Join prediction_ledger + outcome_ledger for calibration analysis."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            p.id         AS prediction_id,
            p.symbol,
            p.score,
            p.verdict,
            p.model_version,
            p.timestamp  AS prediction_timestamp,
            o.horizon_months,
            o.actual_return_pct,
            o.benchmark_return_pct,
            o.excess_return_pct,
            o.outcome_class,
            o.recorded_at,
            o.pre_fix_unverified,
            COALESCE(c.data_backed, 0) AS data_backed
        FROM prediction_ledger p
        JOIN outcome_ledger o ON p.id = o.prediction_id
        LEFT JOIN conviction_calls c ON p.conviction_call_id = c.id
        WHERE (p.pre_fix_unverified IS NULL OR p.pre_fix_unverified = 0)
          AND (o.pre_fix_unverified IS NULL OR o.pre_fix_unverified = 0)
          AND p.symbol NOT LIKE 'FILTX%'
          AND (p.symbol IS NULL OR UPPER(p.symbol) NOT LIKE '%TEST%')
          AND (p.thesis IS NULL OR (UPPER(p.thesis) NOT LIKE '%TEST%' AND UPPER(p.thesis) NOT LIKE '%DUMMY%'))
        ORDER BY p.score ASC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def compute_calibration_report(
    horizon_months: int = 12,
    min_samples_per_bucket: int = 3,
) -> Dict[str, Any]:
    """Generate full calibration report for a specific outcome horizon.

    Args:
        horizon_months: Which horizon to analyse (1 / 3 / 6 / 12).
        min_samples_per_bucket: Skip buckets with fewer samples.

    Returns:
        Dict with:
          - bucket_stats: Per-bucket hit rate, median return, sample count
          - monotonicity_check: Whether higher scores → higher returns
          - violations: Buckets where monotonicity is broken
          - overall_hit_rate_pct: Global outperformance rate
          - recalibration_recommendations: List of weighted recommendations
          - generated_at: ISO timestamp
    """
    all_outcomes = _fetch_all_outcomes_with_scores()
    # Filter to selected horizon
    outcomes = [o for o in all_outcomes if o["horizon_months"] == horizon_months]

    if not outcomes:
        return {
            "status":        "NO_DATA",
            "horizon_months": horizon_months,
            "message":       f"No outcome data for {horizon_months}M horizon. Run outcome_checker first.",
            "generated_at":  datetime.now(timezone.utc).isoformat(),
        }

    # ── Per-bucket statistics ─────────────────────────────────────────────
    bucket_stats: Dict[str, Any] = {}
    for lo, hi in SCORE_BUCKETS:
        label = BUCKET_LABELS[(lo, hi)]
        bucket_outcomes = [o for o in outcomes if lo <= o["score"] < hi]

        if len(bucket_outcomes) < min_samples_per_bucket:
            bucket_stats[label] = {
                "sample_count":        len(bucket_outcomes),
                "status":              "INSUFFICIENT_SAMPLES",
                "hit_rate_pct":        None,
                "median_return_pct":   None,
                "median_excess_pct":   None,
            }
            continue

        rets = [o["actual_return_pct"] for o in bucket_outcomes]
        excess = [o["excess_return_pct"] for o in bucket_outcomes]
        hits = sum(1 for e in excess if e > 0)
        hit_rate = (hits / len(bucket_outcomes)) * 100.0
        median_ret = sorted(rets)[len(rets) // 2]
        median_exc = sorted(excess)[len(excess) // 2]

        bucket_stats[label] = {
            "sample_count":      len(bucket_outcomes),
            "hit_rate_pct":      round(hit_rate, 1),
            "median_return_pct": round(median_ret, 2),
            "median_excess_pct": round(median_exc, 2),
            "status":            "OK",
        }

    # ── Monotonicity check ────────────────────────────────────────────────
    valid_buckets = [
        (BUCKET_LABELS[k], v)
        for k, v in zip(SCORE_BUCKETS, [bucket_stats[BUCKET_LABELS[k]] for k in SCORE_BUCKETS])
        if v.get("hit_rate_pct") is not None
    ]

    monotonicity_ok = True
    violations = []
    for i in range(len(valid_buckets) - 1):
        label_lo, stats_lo = valid_buckets[i]
        label_hi, stats_hi = valid_buckets[i + 1]
        if stats_hi["hit_rate_pct"] < stats_lo["hit_rate_pct"]:
            monotonicity_ok = False
            violations.append({
                "lower_bucket":        label_lo,
                "higher_bucket":       label_hi,
                "lower_hit_rate_pct":  stats_lo["hit_rate_pct"],
                "higher_hit_rate_pct": stats_hi["hit_rate_pct"],
                "severity":            "HIGH" if (stats_lo["hit_rate_pct"] - stats_hi["hit_rate_pct"]) > 20 else "MEDIUM",
            })

    # ── Overall hit rate ──────────────────────────────────────────────────
    total_hits = sum(1 for o in outcomes if o["excess_return_pct"] > 0)
    overall_hit_rate = round((total_hits / len(outcomes)) * 100.0, 1)

    # ── False positive analysis (high conviction, bad outcome) ────────────
    false_positives = [
        {
            "symbol":        o["symbol"],
            "score":         o["score"],
            "verdict":       o["verdict"],
            "actual_return": o["actual_return_pct"],
            "excess_return": o["excess_return_pct"],
        }
        for o in outcomes
        if o["score"] >= 70 and o["excess_return_pct"] < -10
    ]

    # ── Recalibration recommendations (human sign-off required) ───────────
    recommendations = _generate_recalibration_recommendations(
        bucket_stats, violations, false_positives, overall_hit_rate
    )

    # ── Brier score calibration ───────────────────────────────────────────
    from app.services.ml.baseline_model import numpy_brier_score
    targets = [1 if o["excess_return_pct"] > 0 else 0 for o in outcomes]
    probs = [min(1.0, max(0.0, float(o["score"]) / 100.0)) for o in outcomes]
    brier_val = round(numpy_brier_score(targets, probs), 4)

    return {
        "status":           "OK",
        "horizon_months":   horizon_months,
        "total_outcomes":   len(outcomes),
        "overall_hit_rate_pct": overall_hit_rate,
        "brier_calibration_score": brier_val,
        "bucket_stats":     bucket_stats,
        "monotonicity_check": {
            "is_monotonic":      monotonicity_ok,
            "violations":        violations,
            "status":            "VERIFIED_MONOTONIC" if monotonicity_ok else "MONOTONICITY_VIOLATED",
        },
        "false_positives_high_conviction": false_positives[:10],
        "recalibration_recommendations":   recommendations,
        "human_approval_required":  len(recommendations) > 0,
        "generated_at":     datetime.now(timezone.utc).isoformat(),
    }


def _generate_recalibration_recommendations(
    bucket_stats: Dict,
    violations: List[Dict],
    false_positives: List[Dict],
    overall_hit_rate: float,
) -> List[Dict[str, Any]]:
    """Generate data-driven weight adjustment recommendations.

    IMPORTANT: These are recommendations only. The arbiter.py weights
    MUST NOT be changed without explicit human approval.
    """
    recommendations = []

    # Overall underperformance
    if overall_hit_rate < 50.0:
        recommendations.append({
            "type":        "SYSTEM_ALERT",
            "severity":    "HIGH",
            "description": f"Overall hit rate {overall_hit_rate}% < 50%. System is underperforming benchmark.",
            "action":      "Review all engine weights and data quality. Consider temporary halt of live conviction calls.",
            "human_action_required": True,
        })

    # Monotonicity violations
    for v in violations:
        recommendations.append({
            "type":        "MONOTONICITY_VIOLATION",
            "severity":    v["severity"],
            "description": (
                f"Score bucket '{v['higher_bucket']}' hit rate {v['higher_hit_rate_pct']}% "
                f"is LOWER than '{v['lower_bucket']}' at {v['lower_hit_rate_pct']}%."
            ),
            "action":      "Investigate if high-score engines are over-contributing. "
                           "Consider reducing weight of engines most active in the high-score bucket.",
            "human_action_required": True,
        })

    # High false positive rate
    if len(false_positives) > 5:
        top_verdicts = [fp["verdict"] for fp in false_positives]
        recommendations.append({
            "type":        "HIGH_FALSE_POSITIVE_RATE",
            "severity":    "MEDIUM",
            "description": f"{len(false_positives)} high-conviction calls (score≥70) underperformed by >10% excess.",
            "action":      "Review FORENSIC and GOVERNANCE engine sensitivity. "
                           "Consider raising the minimum conviction score threshold for 'Buy' verdict.",
            "suggested_threshold_change": {
                "current_buy_threshold":    70,
                "suggested_buy_threshold":  75,
                "requires_human_approval":  True,
            },
            "human_action_required": True,
        })

    return recommendations


# ─────────────────────────────────────────────────────────────────────────────
# Model versioning
# ─────────────────────────────────────────────────────────────────────────────

def register_model_version(
    version: str,
    configuration: Dict[str, Any],
    human_approved_by: str,
    backtest_summary: Optional[str] = None,
) -> Dict[str, Any]:
    """Register a new model version in the model_versions table.

    Called when arbiter weights or strategy thresholds change.
    Requires human_approved_by to be non-empty — enforces human-in-loop.

    Returns the registered version record.
    """
    if not human_approved_by or human_approved_by.strip() == "":
        raise ValueError(
            "human_approved_by cannot be empty. Weight changes require human sign-off."
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO model_versions (version, released_at, configuration_json, backtest_summary, human_approved_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (version, now_iso, json.dumps(configuration), backtest_summary, human_approved_by),
        )
        conn.commit()
    except Exception as e:
        # Version already exists
        logger.warning("Model version %s already registered: %s", version, e)
    finally:
        conn.close()

    return {
        "version":           version,
        "released_at":       now_iso,
        "configuration":     configuration,
        "human_approved_by": human_approved_by,
        "status":            "REGISTERED",
    }


def get_model_versions() -> List[Dict[str, Any]]:
    """Fetch all registered model versions."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT version, released_at, configuration_json, backtest_summary, human_approved_by "
        "FROM model_versions ORDER BY released_at DESC"
    ).fetchall()
    conn.close()
    return [
        {
            "version":           row["version"],
            "released_at":       row["released_at"],
            "configuration":     json.loads(row["configuration_json"]),
            "backtest_summary":  row["backtest_summary"],
            "human_approved_by": row["human_approved_by"],
        }
        for row in rows
    ]


def score_monotonicity_status() -> Dict[str, Any]:
    """Quick monotonicity check across all available horizon data.

    Returns HEALTHY / VIOLATED / INSUFFICIENT_DATA.
    """
    all_outcomes = _fetch_all_outcomes_with_scores()
    if not all_outcomes:
        return {"status": "INSUFFICIENT_DATA", "message": "No outcomes recorded yet."}

    # Use 12M horizon for primary check
    outcomes_12m = [o for o in all_outcomes if o["horizon_months"] == 12]
    if len(outcomes_12m) < 10:
        return {
            "status":  "INSUFFICIENT_DATA",
            "message": f"Only {len(outcomes_12m)} 12M outcomes — need ≥10 for meaningful check.",
        }

    report = compute_calibration_report(horizon_months=12)
    mono = report.get("monotonicity_check", {})
    return {
        "status":     mono.get("status", "UNKNOWN"),
        "violations": mono.get("violations", []),
        "total_12m_outcomes": len(outcomes_12m),
    }

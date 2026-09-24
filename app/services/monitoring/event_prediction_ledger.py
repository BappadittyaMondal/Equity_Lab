"""Closed-Loop Geopolitical Event Prediction Ledger & Dynamic Self-Learning Engine — Phase 140.

Tracks pre-event geopolitical predictions, weak signal imminence scores, PDLR classifications,
and post-event market realizations. Automatically executes recursive Bayesian Kalman updates
on sector shock betas (β_geo) with mathematically enforced drift guards (max ±0.05 step).
"""

import json
import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.services.db import get_connection
from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research.geopolitical_engine import _GEO_SHOCK_BETA_MATRIX, _DEFAULT_GEO_BETA

logger = logging.getLogger(__name__)

# Failsafe bounded learning constraints
MAX_KALMAN_DRIFT_STEP = 0.05       # Max ±5% single-event beta adjustment
DEFAULT_PRIOR_VARIANCE = 0.04      # Prior variance sigma^2 (0.2 std dev)
DEFAULT_OBSERVATION_VARIANCE = 0.16 # Observation noise variance (0.4 std dev)
MIN_SHOCK_MAGNITUDE = 0.05         # Minimum 5% shock required to avoid division-by-noise


class GeopoliticalEventRecord(BaseModel):
    """Container for a logged geopolitical shock prediction and its outcome."""
    id: Optional[int] = None
    event_id: str
    title: str
    event_type: str
    theater: str = "GLOBAL"
    status: str = "PENDING_OUTCOME"  # PENDING_OUTCOME, CALIBRATED, ARCHIVED
    pews_probability: float = 0.50
    pdlr_ratio: float = 0.50
    pdlr_classification: str = "ELEVATED_FRICTION_RISK"
    shock_vector: Dict[str, float] = Field(default_factory=dict)
    predicted_betas: Dict[str, float] = Field(default_factory=dict)
    realized_shock: Optional[Dict[str, float]] = None
    empirical_asset_returns: Optional[Dict[str, float]] = None
    calibrated_betas: Optional[Dict[str, float]] = None
    kalman_gain: Optional[float] = None
    brier_score: Optional[float] = None
    notes: Optional[str] = None
    created_at: str = ""
    calibrated_at: Optional[str] = None


class EventPredictionLedgerService:
    """Service managing persistent geopolitical predictions and closed-loop self-learning."""

    @classmethod
    def log_geopolitical_event(
        cls,
        event_id: str,
        title: str,
        event_type: str,
        theater: str = "GLOBAL",
        pews_probability: float = 0.50,
        pdlr_ratio: float = 0.50,
        pdlr_classification: str = "ELEVATED_FRICTION_RISK",
        shock_vector: Optional[Dict[str, float]] = None,
        predicted_betas: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None,
    ) -> GeopoliticalEventRecord:
        """Log a new pre-event prediction into the geopolitical event ledger."""
        now_iso = datetime.now(timezone.utc).isoformat()
        sv = shock_vector or {"crude": 0.0, "maritime": 0.0, "china_dump": 0.0, "grid_hw": 0.0, "us_rate": 0.0}
        
        # If predicted_betas omitted, snapshot current baseline betas for relevant sectors
        pb = predicted_betas or {}
        if not pb:
            for sec, bdict in _GEO_SHOCK_BETA_MATRIX.items():
                # Dominant shock beta
                pb[sec] = bdict.get("maritime" if "SHIPPING" in sec else "crude", 0.0)

        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT INTO geopolitical_event_ledger (
                    event_id, title, event_type, theater, status,
                    pews_probability, pdlr_ratio, pdlr_classification,
                    shock_vector_json, predicted_betas_json, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    title,
                    event_type,
                    theater,
                    "PENDING_OUTCOME",
                    float(pews_probability),
                    float(pdlr_ratio),
                    pdlr_classification,
                    json.dumps(sv),
                    json.dumps(pb),
                    notes or "",
                    now_iso,
                ),
            )
            conn.commit()
        except Exception as e:
            # Fallback update if already exists
            conn.execute(
                """
                UPDATE geopolitical_event_ledger SET
                    title = ?, event_type = ?, theater = ?, pews_probability = ?,
                    pdlr_ratio = ?, pdlr_classification = ?, shock_vector_json = ?,
                    predicted_betas_json = ?, notes = ?
                WHERE event_id = ?
                """,
                (
                    title, event_type, theater, float(pews_probability),
                    float(pdlr_ratio), pdlr_classification, json.dumps(sv),
                    json.dumps(pb), notes or "", event_id
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return GeopoliticalEventRecord(
            event_id=event_id,
            title=title,
            event_type=event_type,
            theater=theater,
            status="PENDING_OUTCOME",
            pews_probability=pews_probability,
            pdlr_ratio=pdlr_ratio,
            pdlr_classification=pdlr_classification,
            shock_vector=sv,
            predicted_betas=pb,
            notes=notes,
            created_at=now_iso,
        )

    @classmethod
    def record_event_market_realization(
        cls,
        event_id: str,
        realized_shock: Dict[str, float],
        empirical_asset_returns: Dict[str, float],
        event_occurred: bool = True,
        benchmark_symbol: str = "^NSEI",
    ) -> Dict[str, Any]:
        """Record empirical post-event price moves and execute Bayesian Kalman calibration.
        
        Args:
            event_id: Unique event identifier previously logged.
            realized_shock: Dict with actual shock magnitudes, e.g. {"crude": 0.22, "maritime": 0.75}
            empirical_asset_returns: Realized % return per asset during the event window.
            event_occurred: Whether the physical event actually occurred (for Brier calibration).
            benchmark_symbol: Benchmark to compute abnormal excess returns.
        """
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM geopolitical_event_ledger WHERE event_id = ?",
            (event_id,),
        ).fetchone()

        if not row:
            conn.close()
            raise ValueError(f"Geopolitical event '{event_id}' not found in event ledger.")

        pews_prob = float(row["pews_probability"])
        predicted_betas = json.loads(row["predicted_betas_json"]) if row["predicted_betas_json"] else {}
        bmark_ret = empirical_asset_returns.get(benchmark_symbol, 0.0)

        # 1. Compute Brier score on event occurrence prediction
        target_val = 1.0 if event_occurred else 0.0
        brier_score = round((pews_prob - target_val) ** 2, 4)

        # 2. Dynamic Bayesian Kalman Filter Beta Update
        # Find dominant shock key
        dominant_shock_key = max(realized_shock.keys(), key=lambda k: abs(realized_shock[k])) if realized_shock else "crude"
        shock_magnitude = realized_shock.get(dominant_shock_key, 0.0)

        calibrated_betas: Dict[str, float] = {}
        kalman_gain = 0.0

        if abs(shock_magnitude) >= MIN_SHOCK_MAGNITUDE:
            # Kalman gain = Prior_Var / (Prior_Var + Obs_Var)
            kalman_gain = round(DEFAULT_PRIOR_VARIANCE / (DEFAULT_PRIOR_VARIANCE + DEFAULT_OBSERVATION_VARIANCE), 4)

            for sector_or_sym, ret in empirical_asset_returns.items():
                if sector_or_sym == benchmark_symbol:
                    continue
                excess_ret = (ret - bmark_ret) / 100.0  # Decimal excess return
                
                # Empirical realized beta = excess_return / shock_magnitude
                empirical_beta = max(-1.5, min(1.5, excess_ret / shock_magnitude))

                # Prior beta
                prior_beta = predicted_betas.get(sector_or_sym)
                if prior_beta is None:
                    # Look up from base matrix
                    sec_clean = sector_or_sym.upper()
                    prior_beta = _GEO_SHOCK_BETA_MATRIX.get(sec_clean, _DEFAULT_GEO_BETA).get(dominant_shock_key, 0.0)

                # Raw Kalman step
                raw_step = kalman_gain * (empirical_beta - prior_beta)
                
                # Enforce failsafe drift guard (bounded adjustment ±0.05)
                bounded_step = max(-MAX_KALMAN_DRIFT_STEP, min(MAX_KALMAN_DRIFT_STEP, raw_step))
                new_beta = round(max(-1.0, min(1.0, prior_beta + bounded_step)), 4)

                calibrated_betas[sector_or_sym] = new_beta
        else:
            calibrated_betas = predicted_betas.copy()

        calibrated_at = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """
            UPDATE geopolitical_event_ledger SET
                status = 'CALIBRATED',
                realized_shock_json = ?,
                empirical_asset_returns_json = ?,
                calibrated_betas_json = ?,
                kalman_gain = ?,
                brier_score = ?,
                calibrated_at = ?
            WHERE event_id = ?
            """,
            (
                json.dumps(realized_shock),
                json.dumps(empirical_asset_returns),
                json.dumps(calibrated_betas),
                kalman_gain,
                brier_score,
                calibrated_at,
                event_id,
            ),
        )
        conn.commit()
        conn.close()

        return {
            "event_id": event_id,
            "status": "CALIBRATED",
            "brier_score": brier_score,
            "kalman_gain": kalman_gain,
            "dominant_shock_key": dominant_shock_key,
            "shock_magnitude": shock_magnitude,
            "prior_betas": predicted_betas,
            "calibrated_betas": calibrated_betas,
            "drift_guard_applied": True,
            "max_drift_step": MAX_KALMAN_DRIFT_STEP,
            "calibrated_at": calibrated_at,
            "meta": create_meta_header(source=f"Phase 140 BayesianKalmanCalibrator ({event_id})")
        }

    @classmethod
    def get_calibrated_beta_matrix(cls) -> Dict[str, Dict[str, float]]:
        """Fetch base beta matrix merged with latest empirical Bayesian learnings."""
        matrix = {k: v.copy() for k, v in _GEO_SHOCK_BETA_MATRIX.items()}

        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT calibrated_betas_json, realized_shock_json 
                FROM geopolitical_event_ledger 
                WHERE status = 'CALIBRATED' AND calibrated_betas_json IS NOT NULL
                ORDER BY id DESC LIMIT 20
                """
            ).fetchall()
        except Exception:
            rows = []
        finally:
            conn.close()

        # Replay calibrated updates in chronological order
        for r in reversed(rows):
            c_betas = json.loads(r["calibrated_betas_json"]) if r["calibrated_betas_json"] else {}
            r_shock = json.loads(r["realized_shock_json"]) if r["realized_shock_json"] else {}
            dominant_shock = max(r_shock.keys(), key=lambda k: abs(r_shock[k])) if r_shock else "crude"

            for sec, beta_val in c_betas.items():
                if sec in matrix and dominant_shock in matrix[sec]:
                    matrix[sec][dominant_shock] = beta_val

        return matrix

    @classmethod
    def get_event_history(cls, limit: int = 50) -> List[GeopoliticalEventRecord]:
        """Retrieve recent historical geopolitical events and calibration records."""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM geopolitical_event_ledger ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        except Exception:
            rows = []
        finally:
            conn.close()

        records = []
        for r in rows:
            records.append(
                GeopoliticalEventRecord(
                    id=r["id"],
                    event_id=r["event_id"],
                    title=r["title"],
                    event_type=r["event_type"],
                    theater=r["theater"],
                    status=r["status"],
                    pews_probability=r["pews_probability"],
                    pdlr_ratio=r["pdlr_ratio"],
                    pdlr_classification=r["pdlr_classification"],
                    shock_vector=json.loads(r["shock_vector_json"]) if r["shock_vector_json"] else {},
                    predicted_betas=json.loads(r["predicted_betas_json"]) if r["predicted_betas_json"] else {},
                    realized_shock=json.loads(r["realized_shock_json"]) if r["realized_shock_json"] else None,
                    empirical_asset_returns=json.loads(r["empirical_asset_returns_json"]) if r["empirical_asset_returns_json"] else None,
                    calibrated_betas=json.loads(r["calibrated_betas_json"]) if r["calibrated_betas_json"] else None,
                    kalman_gain=r["kalman_gain"],
                    brier_score=r["brier_score"],
                    notes=r["notes"],
                    created_at=r["created_at"],
                    calibrated_at=r["calibrated_at"],
                )
            )
        return records

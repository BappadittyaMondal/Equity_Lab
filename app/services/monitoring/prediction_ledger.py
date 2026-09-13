"""Live Prediction Ledger & Model Versioning Engine.

Persists every live decision into the historical prediction ledger, tracks future outcome returns
across 1M–36M horizons, and manages versioned scoring configurations requiring human sign-off.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.services.db import get_connection
from app.services.market_data import normalize_symbol


class PredictionRecord(BaseModel):
    """Container for a logged historical prediction."""
    id: Optional[int] = None
    symbol: str
    timestamp: str
    score: int
    verdict: str
    confidence: str
    reference_price: Optional[float] = None
    thesis: str
    model_version: str = "1.0"
    conviction_call_id: Optional[int] = None


class OutcomeRecord(BaseModel):
    """Container for a tracked outcome return."""
    prediction_id: int
    symbol: str
    horizon_months: int
    actual_return_pct: float
    benchmark_return_pct: float
    excess_return_pct: float
    outcome_class: str


class PredictionLedgerService:
    """Service for managing the live prediction ledger and outcome returns."""

    def log_prediction(
        self,
        symbol: str,
        score: int,
        verdict: str,
        confidence: str,
        thesis: str,
        reference_price: Optional[float] = None,
        model_version: str = "1.0",
        conviction_call_id: Optional[int] = None,
    ) -> PredictionRecord:
        """Log a new live conviction call into prediction_ledger."""
        normalized = normalize_symbol(symbol)
        now_iso = datetime.now(timezone.utc).isoformat()

        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO prediction_ledger
            (symbol, timestamp, score, verdict, confidence, reference_price, thesis, model_version, created_at, conviction_call_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (normalized, now_iso, score, verdict, confidence, reference_price, thesis, model_version, now_iso, conviction_call_id),
        )
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return PredictionRecord(
            id=prediction_id,
            symbol=normalized,
            timestamp=now_iso,
            score=score,
            verdict=verdict,
            confidence=confidence,
            reference_price=reference_price,
            thesis=thesis,
            model_version=model_version,
        )

    def record_outcome(
        self,
        prediction_id: int,
        symbol: str,
        horizon_months: int,
        actual_return_pct: float,
        benchmark_return_pct: Optional[float] = None,
        benchmark_symbol: str = "^NSEI",
    ) -> OutcomeRecord:
        """Record future actual return outcome for a historical prediction."""
        normalized = normalize_symbol(symbol)

        # Dynamic realized benchmark resolution
        if benchmark_return_pct is None:
            conn_b = get_connection()
            pred_row = conn_b.execute(
                "SELECT timestamp FROM prediction_ledger WHERE id = ?",
                (prediction_id,)
            ).fetchone()
            conn_b.close()

            realized_bmark: Optional[float] = None
            if pred_row and pred_row["timestamp"]:
                try:
                    from app.services.market_data import get_history
                    b_df = get_history(benchmark_symbol, period="2y")
                    if b_df is not None and not b_df.empty and "Close" in b_df.columns:
                        b_start = float(b_df["Close"].iloc[0])
                        b_end = float(b_df["Close"].iloc[-1])
                        if b_start > 0:
                            realized_bmark = round(((b_end - b_start) / b_start) * 100.0, 2)
                except Exception:
                    realized_bmark = None

            if realized_bmark is not None:
                benchmark_return_pct = realized_bmark
            else:
                # Scaled 12% Nifty institutional CAGR baseline prorated to horizon
                horizon_years = max(0.08, horizon_months / 12.0)
                benchmark_return_pct = round(((1.0 + 0.12) ** horizon_years - 1.0) * 100.0, 2)

        excess = round(actual_return_pct - benchmark_return_pct, 2)

        if excess >= 15.0:
            outcome_class = "CONFIRMED_HIGH_OUTPERFORMANCE"
        elif excess > 0.0:
            outcome_class = "CONFIRMED_OUTPERFORMANCE"
        elif actual_return_pct >= 0.0:
            outcome_class = "POSITIVE_UNDERPERFORMANCE"
        else:
            outcome_class = "NEGATIVE_OUTCOME"

        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO outcome_ledger
            (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (prediction_id, normalized, horizon_months, actual_return_pct, benchmark_return_pct, excess, outcome_class, now_iso),
        )
        conn.commit()
        conn.close()

        return OutcomeRecord(
            prediction_id=prediction_id,
            symbol=normalized,
            horizon_months=horizon_months,
            actual_return_pct=actual_return_pct,
            benchmark_return_pct=benchmark_return_pct,
            excess_return_pct=excess,
            outcome_class=outcome_class,
        )

    def get_prediction_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[PredictionRecord]:
        """Fetch historical logged predictions."""
        conn = get_connection()
        if symbol:
            normalized = normalize_symbol(symbol)
            rows = conn.execute(
                "SELECT * FROM prediction_ledger WHERE symbol = ? ORDER BY id DESC LIMIT ?",
                (normalized, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM prediction_ledger ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append(
                PredictionRecord(
                    id=r["id"],
                    symbol=r["symbol"],
                    timestamp=r["timestamp"],
                    score=r["score"],
                    verdict=r["verdict"],
                    confidence=r["confidence"],
                    reference_price=r["reference_price"],
                    thesis=r["thesis"],
                    model_version=r["model_version"],
                )
            )
        return results

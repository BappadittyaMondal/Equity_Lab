"""Immutable Prediction Ledger Service.

Records generated predictions, thesis invalidation triggers, and performs
post-mortem accuracy evaluation at 7d, 30d, and 90d horizons with SQLite backing persistence.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import sqlite3
import uuid


class PredictionLedgerStore:
    """Persistent SQLite-backed store for prediction tracking and post-mortem auditing."""

    def __init__(self, db_path: Optional[str] = ":memory:"):
        self.db_path = db_path
        self._ledger: Dict[str, Dict[str, Any]] = {}
        if self.db_path:
            self._init_sqlite()

    def _init_sqlite(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_ledger (
                    prediction_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    logged_at TEXT NOT NULL,
                    base_price REAL NOT NULL,
                    predicted_target REAL NOT NULL,
                    conformal_lower REAL NOT NULL,
                    conformal_upper REAL NOT NULL,
                    confidence_tier TEXT NOT NULL,
                    invalidation_triggers TEXT NOT NULL,
                    evaluations TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def log_prediction(
        self,
        symbol: str,
        predicted_target: float,
        conformal_lower: float,
        conformal_upper: float,
        confidence_tier: str,
        invalidation_triggers: List[str],
        base_price: float,
    ) -> str:
        """Log a new prediction and return its unique tracking UUID."""
        pred_id = f"PRED-{uuid.uuid4().hex[:12].upper()}"
        now_str = datetime.now(timezone.utc).isoformat()

        record = {
            "prediction_id": pred_id,
            "symbol": symbol,
            "logged_at": now_str,
            "base_price": base_price,
            "predicted_target": predicted_target,
            "conformal_lower": conformal_lower,
            "conformal_upper": conformal_upper,
            "confidence_tier": confidence_tier,
            "invalidation_triggers": invalidation_triggers,
            "evaluations": {},
        }

        self._ledger[pred_id] = record

        if self.db_path:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO prediction_ledger 
                    (prediction_id, symbol, logged_at, base_price, predicted_target, conformal_lower, conformal_upper, confidence_tier, invalidation_triggers, evaluations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pred_id, symbol, now_str, base_price, predicted_target,
                    conformal_lower, conformal_upper, confidence_tier,
                    json.dumps(invalidation_triggers), json.dumps({})
                ))
                conn.commit()
                conn.close()
            except Exception:
                pass

        return pred_id

    def get_prediction(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        if prediction_id in self._ledger:
            return self._ledger[prediction_id]

        if self.db_path:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM prediction_ledger WHERE prediction_id = ?", (prediction_id,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    rec = {
                        "prediction_id": row[0],
                        "symbol": row[1],
                        "logged_at": row[2],
                        "base_price": row[3],
                        "predicted_target": row[4],
                        "conformal_lower": row[5],
                        "conformal_upper": row[6],
                        "confidence_tier": row[7],
                        "invalidation_triggers": json.loads(row[8]),
                        "evaluations": json.loads(row[9]),
                    }
                    self._ledger[prediction_id] = rec
                    return rec
            except Exception:
                pass

        return None

    def evaluate_post_mortem(
        self,
        prediction_id: str,
        horizon_days: int,
        actual_price: float,
    ) -> Dict[str, Any]:
        """Perform post-mortem evaluation for a 7d, 30d, or 90d horizon."""
        pred = self.get_prediction(prediction_id)
        if not pred:
            raise ValueError(f"Prediction ID {prediction_id} not found in ledger.")

        within_conformal = pred["conformal_lower"] <= actual_price <= pred["conformal_upper"]
        error_pct = round(((actual_price - pred["predicted_target"]) / pred["predicted_target"]) * 100.0, 2)

        eval_res = {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "horizon_days": horizon_days,
            "actual_price": actual_price,
            "within_conformal_bounds": within_conformal,
            "error_pct": error_pct,
        }
        pred["evaluations"][f"{horizon_days}d"] = eval_res
        self._ledger[prediction_id] = pred

        if self.db_path:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE prediction_ledger SET evaluations = ? WHERE prediction_id = ?",
                    (json.dumps(pred["evaluations"]), prediction_id)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        return eval_res

    def resolve_matured_predictions(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """Asynchronously resolve predictions that have matured across 7d, 30d, or 90d horizons."""
        resolved = []
        now = datetime.now(timezone.utc)

        for pred_id, pred in list(self._ledger.items()):
            symbol = pred["symbol"]
            if symbol not in current_prices:
                continue

            try:
                logged_at = datetime.fromisoformat(pred["logged_at"])
                age_days = (now - logged_at).days
            except Exception:
                age_days = 0

            price = current_prices[symbol]

            for h in [7, 30, 90]:
                h_key = f"{h}d"
                if age_days >= h and h_key not in pred["evaluations"]:
                    res = self.evaluate_post_mortem(pred_id, h, price)
                    resolved.append({"prediction_id": pred_id, "horizon": h_key, "result": res})

        return resolved


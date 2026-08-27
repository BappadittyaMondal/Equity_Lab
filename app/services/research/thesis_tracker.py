"""Thesis Lifecycle & Invalidation / Kill-Condition Engine.

STORAGE_ROLE = "PRODUCTION_PERSISTENCE"

Tracks investment theses over time across state lifecycles:
NEW -> VALIDATING -> CONFIRMED -> STRETCHED -> BROKEN / REJECTED

Evaluates automated financial and market kill-conditions (e.g. CFO/EBITDA deterioration,
promoter pledge spikes, unexpected quarterly earnings misses) to automatically re-test theses.
"""

import os
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.config import settings


@dataclass
class KillCondition:
    condition_id: str
    metric_name: str
    operator: str  # "<", ">", "<=", ">=", "=="
    threshold_value: float
    description: str


@dataclass
class InvestmentThesis:
    thesis_id: str
    symbol: str
    primary_thesis: str
    status: str  # "NEW", "VALIDATING", "CONFIRMED", "STRETCHED", "BROKEN", "REJECTED"
    confidence_score: float
    created_at: str
    last_evaluated_at: str
    kill_conditions: List[KillCondition] = field(default_factory=list)
    invalidation_reason: Optional[str] = None


class ThesisTracker:
    """SQLite-backed thesis lifecycle manager and invalidation monitor."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATA_STORE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        db_url = os.getenv("DATABASE_URL")
        if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
            from app.services.db import get_connection
            return get_connection()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS investment_theses (
                thesis_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                primary_thesis TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                created_at TEXT NOT NULL,
                last_evaluated_at TEXT NOT NULL,
                kill_conditions_json TEXT NOT NULL,
                invalidation_reason TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_thesis_symbol ON investment_theses(symbol)")
        conn.commit()
        conn.close()

    def create_thesis(
        self,
        symbol: str,
        primary_thesis: str,
        confidence_score: float = 75.0,
        kill_conditions: Optional[List[KillCondition]] = None
    ) -> InvestmentThesis:
        """Create a new investment thesis with explicit kill conditions."""
        sym_clean = symbol.upper()
        now_iso = datetime.now(timezone.utc).isoformat()
        thesis_id = f"THESIS-{sym_clean}-{int(datetime.now(timezone.utc).timestamp())}"
        
        default_kills = kill_conditions or [
            KillCondition("KC1", "cfo_ebitda_ratio", "<", 0.65, "CFO/EBITDA ratio drops below 0.65"),
            KillCondition("KC2", "promoter_pledge_pct", ">", 20.0, "Promoter pledge exceeds 20.0%"),
            KillCondition("KC3", "quarterly_revenue_growth_pct", "<", 0.0, "Quarterly revenue contracts YoY")
        ]

        thesis = InvestmentThesis(
            thesis_id=thesis_id,
            symbol=sym_clean,
            primary_thesis=primary_thesis,
            status="NEW",
            confidence_score=confidence_score,
            created_at=now_iso,
            last_evaluated_at=now_iso,
            kill_conditions=default_kills
        )

        conn = self._get_connection()
        conn.execute("""
            INSERT INTO investment_theses 
            (thesis_id, symbol, primary_thesis, status, confidence_score, created_at, last_evaluated_at, kill_conditions_json, invalidation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            thesis.thesis_id,
            thesis.symbol,
            thesis.primary_thesis,
            thesis.status,
            thesis.confidence_score,
            thesis.created_at,
            thesis.last_evaluated_at,
            json.dumps([asdict(k) for k in thesis.kill_conditions]),
            None
        ))
        conn.commit()
        conn.close()
        return thesis

    def evaluate_thesis(self, thesis_id: str, current_metrics: Dict[str, float]) -> InvestmentThesis:
        """Evaluate a thesis against current metrics to check kill conditions."""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM investment_theses WHERE thesis_id = ?", (thesis_id,)).fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Thesis ID {thesis_id} not found.")

        kills_data = json.loads(row["kill_conditions_json"])
        kill_conditions = [KillCondition(**k) for k in kills_data]
        new_status = row["status"]
        invalidation_reason = row["invalidation_reason"]

        for kc in kill_conditions:
            val = current_metrics.get(kc.metric_name)
            if val is not None:
                triggered = False
                if kc.operator == "<" and val < kc.threshold_value:
                    triggered = True
                elif kc.operator == ">" and val > kc.threshold_value:
                    triggered = True
                elif kc.operator == "<=" and val <= kc.threshold_value:
                    triggered = True
                elif kc.operator == ">=" and val >= kc.threshold_value:
                    triggered = True
                elif kc.operator == "==" and val == kc.threshold_value:
                    triggered = True

                if triggered:
                    new_status = "BROKEN"
                    invalidation_reason = f"Kill condition triggered: {kc.description} (Actual: {val})"
                    break

        if new_status != "BROKEN" and new_status in ["NEW", "VALIDATING"]:
            new_status = "CONFIRMED"

        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE investment_theses 
            SET status = ?, last_evaluated_at = ?, invalidation_reason = ?
            WHERE thesis_id = ?
        """, (new_status, now_iso, invalidation_reason, thesis_id))
        conn.commit()
        conn.close()

        return InvestmentThesis(
            thesis_id=row["thesis_id"],
            symbol=row["symbol"],
            primary_thesis=row["primary_thesis"],
            status=new_status,
            confidence_score=row["confidence_score"],
            created_at=row["created_at"],
            last_evaluated_at=now_iso,
            kill_conditions=kill_conditions,
            invalidation_reason=invalidation_reason
        )

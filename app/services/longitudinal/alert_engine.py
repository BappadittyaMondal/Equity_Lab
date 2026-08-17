"""Event-Driven Alert Engine.

Monitors score changes, lifecycle stage transitions, thesis weakening/broken events,
and governance warnings, emitting structured system alerts to SQLite and JSON outputs.
"""

import json
import sqlite3
from typing import List, Optional
from datetime import datetime, timezone

from app.models.schemas import SystemAlert
from app.services.db import get_connection


class AlertEngine:
    """Publishes and queries event-driven system alerts."""

    def __init__(self, db: Optional[sqlite3.Connection] = None):
        self.db = db or get_connection()

    def emit_alert(self, symbol: str, event_type: str, severity: str, details: str) -> SystemAlert:
        """Persist a new system alert."""
        alert = SystemAlert(
            symbol=symbol.upper(),
            event_type=event_type,
            severity=severity,
            details=details,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        cursor = self.db.execute(
            """
            INSERT INTO system_alerts (symbol, event_type, severity, details, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (alert.symbol, alert.event_type, alert.severity, alert.details, alert.created_at),
        )
        self.db.commit()
        alert.id = cursor.lastrowid
        return alert

    def get_recent_alerts(self, limit: int = 50, symbol: Optional[str] = None) -> List[SystemAlert]:
        """Fetch recent alerts with optional symbol filtering."""
        if symbol:
            rows = self.db.execute(
                "SELECT * FROM system_alerts WHERE symbol = ? ORDER BY id DESC LIMIT ?",
                (symbol.upper(), limit),
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM system_alerts ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()

        alerts = []
        for r in rows:
            r_dict = dict(r)
            alerts.append(
                SystemAlert(
                    id=r_dict["id"],
                    symbol=r_dict["symbol"],
                    event_type=r_dict["event_type"],
                    severity=r_dict["severity"],
                    details=r_dict["details"],
                    created_at=r_dict["created_at"],
                )
            )
        return alerts

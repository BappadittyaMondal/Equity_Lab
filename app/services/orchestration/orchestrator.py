import os
import json

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.models.schemas import ConvictionCall, ThesisDriftEvent, PortfolioSnapshot
from app.services.decision_brain.arbiter import Arbiter
from app.services.llm import LLMService
from app.services.db import get_connection, _ensure_tables
from app.core.config import settings
from app.services.research_data import ResearchDataStore

class Orchestrator:
    """Stateful orchestration layer for conviction calls and portfolio view.

    - Caches ConvictionCall records for a configurable TTL.
    - Logs thesis drift events when conviction_score changes > 15 points or verdict changes.
    - Provides aggregated portfolio snapshot.
    - Generates LLM narrative for a symbol.
    """

    CACHE_TTL = int(os.getenv('ORCHESTRATION_TTL_SECONDS', '3600'))  # seconds
    DRIFT_THRESHOLD = 15

    def __init__(self):
        self.db = get_connection()
        self.arbiter = Arbiter()
        self.llm = LLMService()
        # Ensure any required tables exist (drift events)
        _ensure_tables()
        self.watchlist_store = ResearchDataStore()

    def _load_latest(self, symbol: str) -> Optional[ConvictionCall]:
        row = self.db.execute(
            "SELECT * FROM conviction_calls WHERE symbol = ? ORDER BY id DESC LIMIT 1",
            (symbol,)
        ).fetchone()
        if not row:
            return None
        row_dict = dict(row)
        if isinstance(row_dict.get("contributing_engines"), str):
            try:
                row_dict["contributing_engines"] = json.loads(row_dict["contributing_engines"])
            except Exception:
                row_dict["contributing_engines"] = []
        if isinstance(row_dict.get("contradicting_engines"), str):
            try:
                row_dict["contradicting_engines"] = json.loads(row_dict["contradicting_engines"])
            except Exception:
                row_dict["contradicting_engines"] = []
        return ConvictionCall.model_validate(row_dict)

    # ------------------------------------------------------------------
    def get_conviction(self, symbol: str, force_refresh: bool = False) -> ConvictionCall:
        """Return a ConvictionCall, using cache if fresh unless forced."""
        cached = self._load_latest(symbol)
        if cached and not force_refresh:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(cached.timestamp)
            if age.total_seconds() < self.CACHE_TTL:
                return cached
        # Fresh arbitration
        fresh = self.arbiter.arbitrate(symbol)
        # Arbiter already persisted the fresh call to DB.
        if cached:
            self._log_drift_if_needed(cached, fresh)
        return fresh

    # ------------------------------------------------------------------
    def _log_drift_if_needed(self, old: ConvictionCall, new: ConvictionCall) -> None:
        delta = new.conviction_score - old.conviction_score
        changed_verdict = old.verdict != new.verdict
        if abs(delta) >= self.DRIFT_THRESHOLD or changed_verdict:
            event = ThesisDriftEvent(
                symbol=new.symbol,
                old_score=old.conviction_score,
                new_score=new.conviction_score,
                delta=delta,
                old_verdict=old.verdict,
                new_verdict=new.verdict,
                triggering_engines=new.contributing_engines,
            )
            self.db.execute(
                "INSERT INTO thesis_drift_events (symbol, old_score, new_score, delta, old_verdict, new_verdict, triggering_engines, created_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (
                    event.symbol,
                    event.old_score,
                    event.new_score,
                    event.delta,
                    event.old_verdict,
                    event.new_verdict,
                    json.dumps(event.triggering_engines),
                    event.timestamp,
                ),
            )
            self.db.commit()

    # ------------------------------------------------------------------
    def _watchlist_symbols(self) -> List[str]:
        """Return list of symbols from the watchlist.
        This helper is used by the nightly cron to generate the digest.
        """
        items = self.watchlist_store.get_watchlist()
        return [item["symbol"] for item in items]

    # ------------------------------------------------------------------
    def get_portfolio_snapshot(self) -> PortfolioSnapshot:
        symbols = self._watchlist_symbols()
        conv_map: Dict[str, ConvictionCall] = {sym: self.get_conviction(sym) for sym in symbols}
        scores = [c.conviction_score for c in conv_map.values()]
        avg = sum(scores) / len(scores) if scores else 0.0
        verdict_counts: Dict[str, int] = {}
        for c in conv_map.values():
            verdict_counts[c.verdict] = verdict_counts.get(c.verdict, 0) + 1
        return PortfolioSnapshot(
            average_score=avg,
            verdict_counts=verdict_counts,
            symbols=conv_map,
        )

    # ------------------------------------------------------------------
    def narrate(self, symbol: str) -> str:
        conviction = self.get_conviction(symbol)
        
        # Circuit breaker check: daily LLM usage threshold
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        try:
            row = self.db.execute(
                "SELECT COUNT(*) as cnt FROM llm_usage WHERE timestamp >= ?",
                (today_start,)
            ).fetchone()
            cnt = row["cnt"] if row else 0
        except Exception:
            cnt = 0
            
        default_limit = getattr(settings, "LLM_DAILY_CALL_LIMIT", 150)
        max_calls = int(os.getenv("MAX_DAILY_LLM_CALLS", str(default_limit)))
        if cnt >= max_calls:
            return (
                f"[{conviction.symbol}] Conviction Verdict: {conviction.verdict} (Score: {conviction.conviction_score}/100). "
                f"Primary Thesis: {conviction.primary_thesis}. "
                f"(Notice: Daily LLM narrative threshold of {max_calls} calls exceeded; fallback to structured decision)."
            )
            
        return self.llm.generate_narrative(conviction)

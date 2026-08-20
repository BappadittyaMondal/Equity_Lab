"""Point-in-Time Historical Research Replay Engine.

Replays real production Arbiter scoring at historical date T, strictly enforcing
`available_at <= T` across financial observations, corporate actions, and ownership snapshots
to prevent look-ahead bias.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.models.schemas import ConvictionCall
from app.services.decision_brain.arbiter import Arbiter
from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol


class PointInTimeSnapshot(BaseModel):
    """Container for point-in-time filtered historical state."""
    symbol: str
    as_of: datetime
    financial_count: int
    event_count: int
    corporate_action_count: int
    ownership_count: int


class HistoricalReplayResult(BaseModel):
    """Result of running production scoring at historical date T."""
    symbol: str
    analysis_date: str
    historical_score: int
    verdict: str
    confidence_tier: str
    contributing_engines: List[str]
    contradicting_engines: List[str]
    data_snapshot: PointInTimeSnapshot


class PointInTimeReplayEngine:
    """Historical replay engine running production decision logic at date T."""

    def __init__(self):
        self.arbiter = Arbiter()
        self.research_store = ResearchDataStore()

    def get_point_in_time_data(self, symbol: str, as_of: datetime) -> PointInTimeSnapshot:
        """Fetch historical timeline data filtered strictly where published_at <= as_of."""
        from fastapi import HTTPException
        normalized = normalize_symbol(symbol)
        try:
            comp, financials, events, corp_actions, ownership, docs = self.research_store.get_timeline(
                normalized, as_of=as_of
            )
            return PointInTimeSnapshot(
                symbol=normalized,
                as_of=as_of,
                financial_count=len(financials),
                event_count=len(events),
                corporate_action_count=len(corp_actions),
                ownership_count=len(ownership),
            )
        except HTTPException:
            return PointInTimeSnapshot(
                symbol=normalized,
                as_of=as_of,
                financial_count=0,
                event_count=0,
                corporate_action_count=0,
                ownership_count=0,
            )

    def replay_analysis(self, symbol: str, as_of: datetime) -> HistoricalReplayResult:
        """Replay production Arbiter conviction call for date T."""
        normalized = normalize_symbol(symbol)

        # Enforce point-in-time timeline filter
        snapshot = self.get_point_in_time_data(normalized, as_of)

        # Run real production Arbiter engine with point-in-time date T
        call = self.arbiter.arbitrate(normalized, as_of=as_of)

        return HistoricalReplayResult(
            symbol=normalized,
            analysis_date=as_of.isoformat(),
            historical_score=call.conviction_score,
            verdict=call.verdict,
            confidence_tier=call.confidence_tier,
            contributing_engines=call.contributing_engines,
            contradicting_engines=call.contradicting_engines,
            data_snapshot=snapshot,
        )

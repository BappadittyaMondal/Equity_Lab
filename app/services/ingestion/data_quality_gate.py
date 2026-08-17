"""Data Quality Gate — Validates data before any strategy engine consumes it.

Prevents garbage-in by enforcing sanity checks on market quotes, financial
observations, and data freshness. Every strategy engine should call
`validate_quote()` and `assess_data_quality()` before processing.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from app.models.schemas import DataQualityReport
from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol

logger = logging.getLogger(__name__)

# Configurable thresholds
MAX_STALENESS_HOURS = 24  # Quotes older than this are tagged STALE
PE_RATIO_MIN = 0.1
PE_RATIO_MAX = 500.0
PRICE_MIN = 0.01


class DataQualityGate:
    """Validates data quality before strategy consumption."""

    def __init__(self, store: Optional[ResearchDataStore] = None):
        self.store = store or ResearchDataStore()

    def validate_quote(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a market quote dict. Returns validated quote with warnings added.

        Checks:
        - price > 0
        - volume > 0
        - PE ratio in sane range (0.1–500)
        - 52-week range is internally consistent
        - Data freshness
        """
        warnings = []

        price = quote.get("price")
        if price is None or price <= PRICE_MIN:
            warnings.append(f"INVALID_PRICE: price={price} (must be > {PRICE_MIN})")

        volume = quote.get("volume")
        if volume is not None and volume <= 0:
            warnings.append(f"ZERO_VOLUME: volume={volume}")

        pe = quote.get("pe_ratio")
        if pe is not None:
            if pe < PE_RATIO_MIN:
                warnings.append(f"PE_TOO_LOW: pe_ratio={pe} (min={PE_RATIO_MIN})")
            elif pe > PE_RATIO_MAX:
                warnings.append(f"PE_TOO_HIGH: pe_ratio={pe} (max={PE_RATIO_MAX})")

        # 52-week range consistency
        high = quote.get("fifty_two_week_high")
        low = quote.get("fifty_two_week_low")
        if high is not None and low is not None:
            if high < low:
                warnings.append(f"52W_RANGE_INVERTED: high={high} < low={low}")
            if price is not None:
                if price > high * 1.05:  # 5% tolerance for intraday
                    warnings.append(f"PRICE_ABOVE_52W_HIGH: price={price} > high={high}")
                if price < low * 0.95:
                    warnings.append(f"PRICE_BELOW_52W_LOW: price={price} < low={low}")

        # Freshness check
        meta = quote.get("meta", {})
        retrieved_at = meta.get("retrieved_at", "")
        if retrieved_at:
            freshness = self._check_freshness(retrieved_at)
            if freshness and freshness > MAX_STALENESS_HOURS:
                warnings.append(f"STALE_DATA: {freshness:.0f}h old (max={MAX_STALENESS_HOURS}h)")
                if isinstance(meta, dict):
                    meta["stale"] = True

        # Attach warnings to quote
        quote_copy = dict(quote)
        if warnings:
            existing = quote_copy.get("data_quality_warnings", [])
            quote_copy["data_quality_warnings"] = existing + warnings
            logger.warning(
                "Data quality warnings for %s: %s",
                quote.get("symbol", "UNKNOWN"),
                "; ".join(warnings),
            )

        return quote_copy

    def assess_data_quality(self, symbol: str) -> DataQualityReport:
        """Assess the quality of research data available for a symbol.

        Checks how many quarters of financial data we have, ownership
        data availability, data freshness, and source credibility.
        """
        norm = normalize_symbol(symbol)
        warnings = []

        quarters = 0
        has_ownership = False
        has_events = False
        latest_date = None
        credibility_values = []

        try:
            company, financials, events, corp_actions, ownership, docs = (
                self.store.get_timeline(norm)
            )

            # Count unique quarters
            quarters_seen = set()
            for obs in financials:
                period = getattr(obs, "period_end", None)
                if period:
                    quarters_seen.add(str(period)[:7])  # YYYY-MM
                cred = getattr(obs, "confidence", 0.5)
                credibility_values.append(cred)
            quarters = len(quarters_seen)

            # Latest financial date
            if financials:
                dates = [str(getattr(f, "period_end", "")) for f in financials]
                dates = [d for d in dates if d]
                if dates:
                    latest_date = max(dates)

            has_ownership = len(ownership) > 0
            has_events = len(events) > 0

        except Exception as e:
            warnings.append(f"No research data found for {norm}: {e}")

        credibility_avg = (
            sum(credibility_values) / len(credibility_values)
            if credibility_values else 0.0
        )

        # Compute freshness in days
        freshness_days = None
        if latest_date:
            try:
                ld = datetime.strptime(latest_date[:10], "%Y-%m-%d")
                freshness_days = (datetime.now() - ld).days
                if freshness_days > 180:
                    warnings.append(f"DATA_OLD: Latest financial data is {freshness_days} days old")
            except Exception:
                pass

        # Compute grade
        grade = DataQualityReport.compute_grade(quarters, has_ownership, credibility_avg)

        if quarters < 4:
            warnings.append(f"INSUFFICIENT_QUARTERS: Only {quarters} quarters (need ≥4 for trend analysis)")
        if not has_ownership:
            warnings.append("NO_OWNERSHIP_DATA: Cannot assess promoter/FII behaviour")

        return DataQualityReport(
            quarters_available=quarters,
            has_ownership_data=has_ownership,
            has_corporate_events=has_events,
            latest_financial_date=latest_date,
            data_freshness_days=freshness_days,
            source_credibility_avg=round(credibility_avg, 2),
            grade=grade,
            warnings=warnings,
        )

    def _check_freshness(self, timestamp_str: str) -> Optional[float]:
        """Return hours since timestamp, or None if unparseable."""
        try:
            # Try ISO format
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - ts
            return delta.total_seconds() / 3600.0
        except Exception:
            return None


def compute_corporate_action_factor(
    action_type: str,
    ratio_numerator: float,
    ratio_denominator: float,
    amount_per_share: Optional[float] = None,
) -> float:
    """Compute price adjustment factor for a corporate action.

    Returns a factor to multiply historical prices by to adjust
    for splits, bonuses, etc.

    Examples:
        Stock split 1:5  → factor = 0.2 (old prices × 0.2 = adjusted)
        Bonus 1:1        → factor = 0.5
        No adjustment     → factor = 1.0
    """
    if ratio_denominator <= 0:
        return 1.0

    action = action_type.upper()
    if action in ("SPLIT", "STOCK_SPLIT"):
        return ratio_denominator / ratio_numerator if ratio_numerator > 0 else 1.0
    elif action in ("BONUS", "BONUS_ISSUE"):
        total_shares = ratio_numerator + ratio_denominator
        return ratio_denominator / total_shares if total_shares > 0 else 1.0
    elif action in ("RIGHTS", "RIGHTS_ISSUE"):
        return 1.0  # Rights don't directly adjust historical prices
    elif action in ("DIVIDEND",):
        return 1.0  # Dividends don't adjust close prices in most indices

    return 1.0

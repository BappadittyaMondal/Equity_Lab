"""Multi-Period Trend Analysis Engine.

Analyzes financial metric series across current, previous quarter, previous year, 3Y, and 5Y trends
and classifies the trend trajectory into deterministic categories.
"""

from typing import Dict, Any, List, Optional
from app.models.schemas import MetricTrend


def classify_metric_trend(
    metric_name: str,
    current: Optional[float],
    prev_quarter: Optional[float],
    prev_year: Optional[float],
    trend_3y: Optional[float] = None,
    trend_5y: Optional[float] = None,
) -> MetricTrend:
    """Classify the trend trajectory of a single metric."""
    if current is None:
        return MetricTrend(
            metric_name=metric_name,
            current=current,
            prev_quarter=prev_quarter,
            prev_year=prev_year,
            trend_3y=trend_3y,
            trend_5y=trend_5y,
            classification="stable",
        )

    pq = prev_quarter if prev_quarter is not None else current
    py = prev_year if prev_year is not None else pq

    # Calculate quarter-over-quarter and year-over-year growth
    qoq_change = (current - pq) / abs(pq) if pq != 0 else 0.0
    yoy_change = (current - py) / abs(py) if py != 0 else 0.0

    if qoq_change > 0.15 and yoy_change > 0.20:
        classification = "accelerating"
    elif qoq_change > 0.05 or yoy_change > 0.08:
        classification = "improving"
    elif qoq_change > -0.05 and pq < py and current > pq:
        classification = "recovering"
    elif qoq_change < -0.15 and yoy_change < -0.20:
        classification = "broken"
    elif qoq_change < -0.05 or yoy_change < -0.08:
        classification = "decelerating"
    elif yoy_change < -0.05:
        classification = "deteriorating"
    else:
        classification = "stable"

    return MetricTrend(
        metric_name=metric_name,
        current=current,
        prev_quarter=prev_quarter,
        prev_year=prev_year,
        trend_3y=trend_3y,
        trend_5y=trend_5y,
        classification=classification,
    )


class TrendAnalyzer:
    """Multi-metric trend analyzer."""

    def analyze_company_trends(self, symbol: str, financial_data: Dict[str, Any]) -> List[MetricTrend]:
        """Classify trends across core fundamental metrics."""
        metrics_to_check = [
            ("revenue", financial_data.get("revenue"), financial_data.get("prev_q_revenue"), financial_data.get("prev_y_revenue")),
            ("pat", financial_data.get("pat"), financial_data.get("prev_q_pat"), financial_data.get("prev_y_pat")),
            ("ebitda", financial_data.get("ebitda"), financial_data.get("prev_q_ebitda"), financial_data.get("prev_y_ebitda")),
            ("roce", financial_data.get("roce"), financial_data.get("prev_q_roce"), financial_data.get("prev_y_roce")),
            ("roe", financial_data.get("roe"), financial_data.get("prev_q_roe"), financial_data.get("prev_y_roe")),
            ("cfo_to_pat", financial_data.get("cfo_to_pat"), financial_data.get("prev_q_cfo_to_pat"), financial_data.get("prev_y_cfo_to_pat")),
        ]

        results = []
        for name, curr, pq, py in metrics_to_check:
            trend = classify_metric_trend(name, curr, pq, py)
            results.append(trend)
        return results

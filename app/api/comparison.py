"""Stock comparison router.
"""

from fastapi import APIRouter
from app.models.schemas import ComparisonRequest, ComparisonResponse
from app.services.comparison import compare_stocks

router = APIRouter(prefix="/api/v1", tags=["Stock Comparison"])


@router.post("/compare", response_model=ComparisonResponse)
def execute_stock_comparison(req: ComparisonRequest):
    """Executes side-by-side metric comparison across 2-5 stock tickers."""
    return compare_stocks(req)

"""Options strategy & A2 0-DTE range selling router.
"""

from fastapi import APIRouter
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.schemas import OptionsA2Request, OptionsA2Response
from app.services.strategies.options_a2 import calculate_a2_payoff

router = APIRouter(prefix="/api/v1", tags=["Options Strategy Engine"])


@router.post("/options/a2-payoff", response_model=OptionsA2Response)
def execute_a2_options_payoff(req: OptionsA2Request):
    """Calculates A2 0-DTE Short Strangle range selling payoff, EV, and risk limits."""
    if not settings.ENABLE_OPTIONS_A2:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A2 options analytics are suspended pending validated option-chain data and backtesting."
        )
    return calculate_a2_payoff(req)

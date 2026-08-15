"""Return probability analysis router.
"""

from fastapi import APIRouter
from app.models.schemas import ReturnProbabilityRequest, ReturnProbabilityResponse
from app.services.probability import calculate_return_probability

router = APIRouter(prefix="/api/v1", tags=["Return Probability Analysis"])


@router.post("/return-probability", response_model=ReturnProbabilityResponse)
def execute_return_probability(req: ReturnProbabilityRequest):
    """Calculates empirical return probability distribution over holding horizon."""
    return calculate_return_probability(req)

from fastapi import APIRouter
from app.services.orchestration import Orchestrator
from app.models.schemas import PortfolioSnapshot

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])

@router.get("/", response_model=PortfolioSnapshot)
def get_portfolio():
    orch = Orchestrator()
    return orch.get_portfolio_snapshot()

@router.get("/narrate/{symbol}", response_model=str)
def narrate(symbol: str):
    orch = Orchestrator()
    return orch.narrate(symbol)

"""
Main Turnaround Prediction Engine Entry Point (E20).

Orchestrates PIT data ingestion, feature extraction, 2-layer probability model,
lifecycle state evaluation, and returns a fully certified StrategyRunResponse.
"""

from typing import Any, Dict, Optional
import os

from app.models.schemas import StrategyRunResponse
from app.services.market_data import create_meta_header, get_ist_now_str
from app.services.turnaround.feature_engine import extract_turnaround_features
from app.services.turnaround.label_engine import evaluate_historical_damage, classify_turnaround_stage
from app.services.turnaround.lifecycle import evaluate_lifecycle_state
from app.services.turnaround.turnaround_model import predict_turnaround_probabilities


def get_mock_turnaround_financials(symbol: str) -> list[dict[str, Any]]:
    """Return mock financial history for offline testing mode."""
    return [
        {"revenue_inr": 1200.0, "opm_pct": 22.0, "pat_inr": 150.0, "cfo_inr": 160.0, "roce_pct": 24.0, "debt_inr": 300.0},
        {"revenue_inr": 900.0, "opm_pct": 11.0, "pat_inr": 50.0, "cfo_inr": 55.0, "roce_pct": 11.0, "debt_inr": 480.0},
        {"revenue_inr": 980.0, "opm_pct": 14.0, "pat_inr": 72.0, "cfo_inr": 80.0, "roce_pct": 13.5, "debt_inr": 450.0},
        {"revenue_inr": 1080.0, "opm_pct": 17.5, "pat_inr": 98.0, "cfo_inr": 110.0, "roce_pct": 17.0, "debt_inr": 390.0},
    ]


def run_turnaround_engine(symbol: str, as_of: Optional[str] = None) -> StrategyRunResponse:
    """Run E20 Turnaround Prediction Engine for given symbol."""
    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
    
    # Ingestion layer with fallback
    financials = get_mock_turnaround_financials(symbol) if is_offline else []
    if not is_offline:
        try:
            from app.services.market_data import get_company_financials
            real_fins = get_company_financials(symbol)
            if real_fins:
                financials = real_fins
        except Exception:
            pass

    if not financials:
        if not is_offline:
            meta = create_meta_header(source="Turnaround Prediction Engine (E20)")
            meta["data_mode"] = "INSUFFICIENT_DATA"
            return StrategyRunResponse(
                strategy_id="E20",
                strategy_name="Institutional Turnaround Prediction Engine",
                status="data_insufficient",
                executed_at=get_ist_now_str(),
                symbol=symbol,
                passed_gates=False,
                results={"symbol": symbol, "data_status": "insufficient_financial_observations", "turnaround_score": 0.0},
                metrics={"score": 0.0, "turnaround_score": 0.0},
                risk_warnings=["Insufficient financial observations to evaluate corporate turnaround."],
                disclaimer="Real financial observation data required for corporate turnaround evaluation.",
                meta=meta
            )
        financials = get_mock_turnaround_financials(symbol)

    quote = {"price_change_6m_pct": 12.0}
    if not is_offline:
        try:
            from app.services.market_data import get_quote
            q = get_quote(symbol)
            if q and hasattr(q, "price_change_6m_pct") and q.price_change_6m_pct is not None:
                quote = {"price_change_6m_pct": float(q.price_change_6m_pct)}
        except Exception:
            pass

    # Pipeline math execution
    features = extract_turnaround_features(financials, market_quote=quote)
    damage_info = evaluate_historical_damage(financials)
    lifecycle_info = evaluate_lifecycle_state(features)
    model_output = predict_turnaround_probabilities(features)

    stage_label = classify_turnaround_stage(
        historical_damage=damage_info["damage_state"],
        improving_quarters=features.get("improving_quarters", 0),
        cfo_pat_ratio=features.get("cfo_to_pat", 0.0),
        relapse_flags=1 if model_output["p_relapse"] > 0.6 else 0
    )

    t_score = model_output.get("turnaround_score", 0.0)
    passed = t_score >= 50.0 and model_output.get("p_recovery", 0.0) >= 0.5

    meta = create_meta_header(source="Turnaround Prediction Engine (E20)")

    results_dict = {
        "symbol": symbol,
        "turnaround_score": t_score,
        "p_recovery": model_output.get("p_recovery", 0.0),
        "p_relapse": model_output.get("p_relapse", 0.0),
        "p_outperformance": model_output.get("p_outperformance", 0.0),
        "value_trap_risk_score": model_output.get("value_trap_risk_score", 0.0),
        "turnaround_stage": stage_label.value,
        "lifecycle_state": lifecycle_info["lifecycle_state"],
        "historical_damage_state": damage_info["damage_state"],
        "fundamental_recovery_score": features.get("fundamental_recovery_score", 0.0),
        "frmr_gap_score": features.get("frmr_gap_score", 0.0),
        "improving_quarters": features.get("improving_quarters", 0),
        "cfo_to_pat": features.get("cfo_to_pat", 0.0),
    }

    metrics_dict = {
        "score": t_score,
        "turnaround_score": t_score,
        "p_recovery": model_output.get("p_recovery", 0.0),
        "value_trap_risk_score": model_output.get("value_trap_risk_score", 0.0),
    }

    return StrategyRunResponse(
        strategy_id="E20",
        strategy_name="Institutional Turnaround Prediction Engine",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=symbol,
        passed_gates=passed,
        results=results_dict,
        metrics=metrics_dict,
        risk_warnings=damage_info.get("damage_reasons", []),
        disclaimer="Institutional 2-layer turnaround probability model and expectation gap analysis.",
        meta=meta
    )

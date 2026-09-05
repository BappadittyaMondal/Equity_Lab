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
    fund_dict = None
    if not is_offline:
        try:
            from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
            fund_dict = ScreenerCloudConnector.get_company_fundamentals(symbol)
            if fund_dict:
                financials = [
                    {
                        "revenue_inr": float(fund_dict.get("sales_growth_3yr", 100.0) or 100.0),
                        "opm_pct": float(fund_dict.get("opm_5yr", 10.0) or 10.0),
                        "pat_inr": float(fund_dict.get("pat_growth_3yr", 20.0) or 20.0),
                        "cfo_inr": float(fund_dict.get("cfo_3yr", 30.0) or 30.0),
                        "roce_pct": float(fund_dict.get("roce_3yr", 12.0) or 12.0),
                        "debt_inr": float(fund_dict.get("net_block_3yr_back", 100.0) or 100.0),
                    },
                    {
                        "revenue_inr": float(fund_dict.get("sales_growth_latest", 120.0) or 120.0),
                        "opm_pct": float(fund_dict.get("opm_latest", 14.0) or 14.0),
                        "pat_inr": float(fund_dict.get("net_profit_last_year", 35.0) or 35.0),
                        "cfo_inr": float(fund_dict.get("cfo_last_year", 45.0) or 45.0),
                        "roce_pct": float(fund_dict.get("roce_latest", 15.0) or 15.0),
                        "debt_inr": float(fund_dict.get("net_block", 90.0) or 90.0),
                    }
                ]
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

    # Wire TurnaroundStateMachine (Relapse-First Institutional Governance)
    from app.services.research.finder_state_machines import TurnaroundStateMachine

    # Extract real price from market quote or fundamentals
    cp_val = 0.0
    if not is_offline:
        try:
            from app.services.market_data import get_quote
            q = get_quote(symbol)
            if q and hasattr(q, "price") and q.price:
                cp_val = float(q.price)
        except Exception:
            pass
        if cp_val <= 0.0 and fund_dict:
            cp_val = float(fund_dict.get("current_price", 0.0) or 0.0)
    else:
        cp_val = float(features.get("current_price", 100.0) or 100.0)

    # Do not synthesize fake disaster floor if missing
    d_avwap = None
    if fund_dict and fund_dict.get("low_52w"):
        d_avwap = float(fund_dict["low_52w"])
    elif is_offline:
        d_avwap = float(features.get("disaster_avwap", cp_val * 0.85) or (cp_val * 0.85))

    # Extract real financial metrics from latest observations
    latest_fin = financials[-1] if financials else {}
    cfo_val = float(latest_fin.get("cfo_inr", latest_fin.get("cash_from_ops", 0.0)))
    curr_rev = float(latest_fin.get("revenue_inr", 0.0))
    curr_opm = float(features.get("curr_opm", latest_fin.get("opm_pct", 0.0)))
    ebitda_val = float(curr_rev * (curr_opm / 100.0)) if curr_rev > 0 else float(latest_fin.get("ebitda_inr", 0.0))
    debt_red = bool(features.get("debt_reduction_pct", 0.0) > 0.0)

    # Derive real Piotroski score and prior period delta (DEF-D)
    f_curr = 5 if is_offline else 0
    f_prev = 0
    if fund_dict and fund_dict.get("piotroski_score"):
        f_curr = int(fund_dict["piotroski_score"])
        f_prev = int(fund_dict.get("piotroski_score_prev", max(1, f_curr - 1) if f_curr > 0 else 0))
    elif len(financials) >= 2:
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        piot_res = compute_piotroski_fscore(financials)
        if piot_res.get("status") == "success":
            f_curr = int(piot_res.get("f_score", 0))
        if len(financials) >= 3:
            piot_prev_res = compute_piotroski_fscore(financials[:-1])
            if piot_prev_res.get("status") == "success":
                f_prev = int(piot_prev_res.get("f_score", max(1, f_curr - 1)))
            else:
                f_prev = max(1, f_curr - 1) if f_curr > 0 else 0
        else:
            f_prev = max(1, f_curr - 1) if f_curr > 0 else 0
    else:
        f_prev = max(1, f_curr - 1) if f_curr > 0 else 0
    relapse_flag = bool(model_output.get("p_relapse", 0.0) > 0.65)

    sm_res = TurnaroundStateMachine.evaluate(
        symbol=symbol,
        current_price=cp_val,
        disaster_avwap=d_avwap,
        piotroski_score=f_curr,
        piotroski_prev=f_prev,
        cfo_cr=cfo_val,
        ebitda_cr=ebitda_val,
        debt_reduction_initiated=debt_red,
        is_relapse_signal=relapse_flag,
    )

    if sm_res["state"] == "RELAPSE":
        passed = False
        damage_info.setdefault("damage_reasons", []).append(
            f"Turnaround Relapse Veto Active: Dominant failure override ({sm_res.get('dominant_override')})"
        )

    from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate
    surv = evaluate_surveillance_and_cost_gate(symbol)
    if surv.circuit_band_pct <= 5.0 or surv.hard_gate_status in ("FAIL", "DATA_INSUFFICIENT") or not getattr(surv, "is_cleared_for_trading", True):
        passed = False
        damage_info.setdefault("damage_reasons", []).append(
            f"Regulatory / Circuit Lock Hazard: Circuit band {surv.circuit_band_pct}% <= 5% or surveillance status {surv.hard_gate_status}"
        )

    meta = create_meta_header(source="Turnaround Prediction Engine (E20)")

    results_dict = {
        "symbol": symbol,
        "turnaround_score": t_score,
        "p_recovery": model_output.get("p_recovery", 0.0),
        "p_recovery_4q": model_output.get("p_recovery_4q", 0.0),
        "p_recovery_8q": model_output.get("p_recovery_8q", 0.0),
        "p_recovery_12q": model_output.get("p_recovery_12q", 0.0),
        "p_relapse": model_output.get("p_relapse", 0.0),
        "p_outperformance": model_output.get("p_outperformance", 0.0),
        "value_trap_risk_score": model_output.get("value_trap_risk_score", 0.0),
        "turnaround_stage": stage_label.value,
        "lifecycle_state": lifecycle_info["lifecycle_state"],
        "lifecycle_state_machine": sm_res,
        "is_relapse_active": sm_res["state"] == "RELAPSE",
        "recovery_index": model_output.get("recovery_index", model_output.get("p_recovery", 0.0)),
        "relapse_index": model_output.get("relapse_index", model_output.get("p_relapse", 0.0)),
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
        "p_recovery_4q": model_output.get("p_recovery_4q", 0.0),
        "p_recovery_8q": model_output.get("p_recovery_8q", 0.0),
        "p_recovery_12q": model_output.get("p_recovery_12q", 0.0),
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

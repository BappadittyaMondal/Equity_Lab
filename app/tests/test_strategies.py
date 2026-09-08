"""Unit tests for Strategy registry and module execution.
"""

from app.services.strategies.registry import list_strategy_modules, get_strategy_module


def test_strategy_registry_count():
    modules = list_strategy_modules()
    # The IERL framework defines at least 26 core modules, but allows expansion as new strategy engines land (currently 35).
    # Enforce >= 26 to prevent regression/shrinkage while allowing module expansion.
    assert len(modules) >= 26, f"Master strategy registry must contain at least 26 IERL Modules (found {len(modules)})"


def test_strategy_production_vs_coming_soon():
    prod_ids = ["B5", "B8", "C9", "C13", "C14", "D15", "D18"]
    for sid in prod_ids:
        m = get_strategy_module(sid)
        assert m.status in ["production", "coming_soon"], f"Module {sid} should have valid status"

    all_ids = ["A1", "A2", "A3", "B4", "B6", "B7", "C10", "C11", "C12", "D16", "D17"]
    for sid in all_ids:
        m = get_strategy_module(sid)
        assert m.status in ["production", "coming_soon", "suspended"]


def test_c10_owner_earnings_execution():
    from app.services.strategies.registry import run_strategy_module
    from app.services.strategies.owner_earnings_c10 import evaluate_owner_earnings

    # 1. Direct engine invocation
    res = evaluate_owner_earnings("RELIANCE")
    assert res["strategy_id"] == "C10"
    assert "owner_earnings_inr" in res
    assert "fcf_yield_pct" in res
    assert "maintenance_capex" in res
    assert "depreciation" in res
    assert "owner_earnings_to_pat_ratio" in res
    assert "is_mock" in res
    assert "accounting_components_observed" in res
    assert "is_pure_accounting_observation" in res
    assert "accounting_integrity" in res
    assert res["status"] in ["production", "data_insufficient"]

    # 2. Registry dispatch invocation
    dispatch_res = run_strategy_module("C10", "RELIANCE")
    assert dispatch_res.strategy_id == "C10"
    assert dispatch_res.status in ["production", "data_insufficient"]
    assert "fcf_yield_pct" in dispatch_res.metrics
    assert "owner_earnings_inr" in dispatch_res.metrics


def test_d16_dual_momentum_execution():
    from app.services.strategies.registry import run_strategy_module
    from app.services.strategies.dual_momentum_d16 import evaluate_dual_momentum

    # 1. Direct engine invocation
    res = evaluate_dual_momentum("RELIANCE", benchmark="NIFTY 50")
    assert res["strategy_id"] == "D16"
    assert "absolute_momentum_12m_pct" in res
    assert "benchmark_return_12m_pct" in res
    assert "relative_momentum_spread_pct" in res
    assert "dual_momentum_signal" in res
    assert res["dual_momentum_signal"] in ["STRONG_BUY", "HOLD_CASH", "BENCHMARK_PREFERRED", "NO_SIGNAL"]

    # 2. Registry dispatch invocation
    dispatch_res = run_strategy_module("D16", "RELIANCE")
    assert dispatch_res.strategy_id == "D16"
    assert dispatch_res.status in ["production", "data_insufficient"]





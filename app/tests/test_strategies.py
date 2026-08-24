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



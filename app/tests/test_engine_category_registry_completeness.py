"""Test to guarantee 100% completeness of ENGINE_CATEGORIES in debate_engine.py.
Prevents category drop regressions across all platform strategy and research engines.
"""

import pytest
from app.services.decision_brain.debate_engine import ENGINE_CATEGORIES, _get_engine_category
from app.services.strategies.registry import STRATEGY_MODULES

VALID_CATEGORIES = {"FUNDAMENTAL", "TECHNICAL", "VALUATION", "FORENSIC", "GOVERNANCE", "OPTIONS"}


def test_all_strategy_modules_registered_in_engine_categories():
    """Verify that every strategy module defined in STRATEGY_MODULES has an explicit category."""
    registered_ids = set(ENGINE_CATEGORIES.keys())
    strategy_ids = set(STRATEGY_MODULES.keys())

    missing = strategy_ids - registered_ids
    assert not missing, f"The following strategy modules are missing from ENGINE_CATEGORIES: {sorted(missing)}"

    for mod_id in strategy_ids:
        cat = _get_engine_category(mod_id)
        assert cat in VALID_CATEGORIES, f"Module {mod_id} has invalid category {cat}"


def test_forensic_engines_explicitly_classified():
    """Verify that critical forensic modules are assigned FORENSIC or GOVERNANCE."""
    assert _get_engine_category("C10") == "FORENSIC"
    assert _get_engine_category("C11") == "FORENSIC"
    assert _get_engine_category("C12") == "FORENSIC"
    assert _get_engine_category("C13") == "FORENSIC"
    assert _get_engine_category("C14") == "FORENSIC"
    assert _get_engine_category("D18") == "GOVERNANCE"
    assert _get_engine_category("E17") == "GOVERNANCE"


def test_core_research_engines_classified():
    """Verify that all E1-E21 engines have active non-OTHER classifications."""
    for i in range(1, 22):
        eng_id = f"E{i}"
        cat = _get_engine_category(eng_id)
        assert cat != "OTHER", f"Engine {eng_id} unexpectedly classified as OTHER"
        assert cat in VALID_CATEGORIES

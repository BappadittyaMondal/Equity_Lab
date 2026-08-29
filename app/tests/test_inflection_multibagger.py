# -*- coding: utf-8 -*-
"""Test suite for Strategy Module E19: Multibagger Inflection Engine."""

import pytest
from app.services.strategies.inflection_multibagger import run_inflection_multibagger


def test_inflection_multibagger_missing_data():
    res = run_inflection_multibagger("INVALID_SYMBOL_999")
    assert res.strategy_id == "E19"
    assert res.status in ["data_insufficient", "production"]
    assert hasattr(res, "passed_gates")


def test_inflection_multibagger_valid_symbol():
    res = run_inflection_multibagger("TCS")
    assert res.strategy_id == "E19"
    assert res.strategy_name == "E19 Multibagger Inflection Engine"
    assert "inflection_signal" in res.results

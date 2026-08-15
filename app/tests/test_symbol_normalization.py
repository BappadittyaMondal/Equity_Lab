"""Unit tests for symbol normalization logic.
"""

import pytest
from app.services.market_data import normalize_symbol


def test_symbol_normalization_equities():
    assert normalize_symbol("RELIANCE") == "RELIANCE.NS"
    assert normalize_symbol("reliance") == "RELIANCE.NS"
    assert normalize_symbol("RELIANCE.NS") == "RELIANCE.NS"
    assert normalize_symbol("TCS") == "TCS.NS"
    assert normalize_symbol("INFY.BO") == "INFY.BO"


def test_symbol_normalization_indices():
    assert normalize_symbol("NIFTY") == "^NSEI"
    assert normalize_symbol("NIFTY 50") == "^NSEI"
    assert normalize_symbol("^NSEI") == "^NSEI"
    assert normalize_symbol("SENSEX") == "^BSESN"
    assert normalize_symbol("BANKNIFTY") == "^NSEBANK"
    assert normalize_symbol("INDIA VIX") == "^INDIAVIX"

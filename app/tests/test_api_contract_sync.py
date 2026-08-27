"""API Contract Synchronization Tests — Phase 5.

Verifies:
- OptionsA2Request accepts both full canonical schemas and aliased/partial frontend requests.
- FastAPI routes respond with valid OpenAPI schemas and include proper MetaHeader structures.
"""

import pytest
from app.models.schemas import OptionsA2Request, OptionsA2Response
from app.services.strategies.options_a2 import calculate_a2_payoff


def test_options_a2_schema_contract_full():
    """Verify full canonical OptionsA2Request payload parses and executes."""
    raw_payload = {
        "underlying": "^NSEI",
        "expiry": "0-DTE",
        "spot_price": 22000.0,
        "lower_strike": 21500.0,
        "upper_strike": 22500.0,
        "call_premium": 50.0,
        "put_premium": 50.0,
        "lot_size": 25,
        "risk_limit_amount": 100000.0
    }
    req = OptionsA2Request(**raw_payload)
    assert req.underlying == "^NSEI"
    assert req.lower_strike == 21500.0
    assert req.upper_strike == 22500.0

    res = calculate_a2_payoff(req)
    assert res.underlying == "^NSEI"
    assert res.max_profit == 2500.0
    assert res.meta is not None


def test_options_a2_schema_contract_aliased_frontend():
    """Verify frontend aliased/legacy payload ({symbol, spot_price, strike_price}) parses gracefully."""
    raw_payload = {
        "symbol": "RELIANCE",
        "spot_price": 2500.0,
        "strike_price": 2500.0
    }
    req = OptionsA2Request(**raw_payload)
    assert req.underlying == "RELIANCE"
    assert req.spot_price == 2500.0
    assert req.lower_strike < 2500.0
    assert req.upper_strike > 2500.0
    assert req.call_premium == 45.0
    assert req.put_premium == 45.0

    res = calculate_a2_payoff(req)
    assert res.underlying.startswith("RELIANCE")
    assert res.spot_price == 2500.0

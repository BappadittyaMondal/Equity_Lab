import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_conviction_endpoint_schema():
    # Use a known symbol from fixtures or a placeholder
    symbol = "RELIANCE"
    response = client.get(f"/api/v1/decision/{symbol}")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"
    data = response.json()
    # Required fields per ConvictionCall schema
    required_fields = [
        "symbol",
        "verdict",
        "conviction_score",
        "primary_thesis",
        "contributing_engines",
        "contradicting_engines",
        "confidence_tier",
        "timestamp",
    ]
    for field in required_fields:
        assert field in data, f"Missing field {field} in response"
    # Basic type checks
    assert isinstance(data["symbol"], str)
    assert isinstance(data["verdict"], str)
    assert isinstance(data["conviction_score"], int)
    assert isinstance(data["primary_thesis"], str)
    assert isinstance(data["contributing_engines"], list)
    assert isinstance(data["contradicting_engines"], list)
    assert isinstance(data["confidence_tier"], str)
    assert isinstance(data["timestamp"], str)

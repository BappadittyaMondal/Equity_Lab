"""Integration tests for security headers, CORS allowed origins, and rate limiting.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "providers_status" in data


def test_security_headers():
    res = client.get("/api/v1/health")
    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in headers


def test_cors_origin_restriction():
    # Hostile origin should not receive Access-Control-Allow-Origin header matching attacker
    res = client.options(
        "/api/v1/health",
        headers={"Origin": "https://attacker.example.com", "Access-Control-Request-Method": "GET"}
    )
    # FastAPI CORS middleware will omit Access-Control-Allow-Origin for unauthorized origin
    allowed_origin = res.headers.get("Access-Control-Allow-Origin")
    assert allowed_origin != "https://attacker.example.com"


def test_authentication_is_enforced_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "REQUIRE_AUTH", True)
    monkeypatch.setattr(settings, "API_KEY_SECRET", "test-secret")

    unauthenticated = client.get("/api/v1/ticker/RELIANCE")
    rejected_key = client.get("/api/v1/ticker/RELIANCE", headers={"X-API-Key": "wrong"})
    assert unauthenticated.status_code == 401
    assert rejected_key.status_code == 401


def test_api_key_authentication_on_product_endpoints(monkeypatch):
    monkeypatch.setattr(settings, "REQUIRE_AUTH", True)
    monkeypatch.setattr(settings, "API_KEY_SECRET", "valid-secret-key")

    # Unauthenticated request to decision endpoint returns 401
    res_unauth = client.get("/api/v1/decision/RELIANCE")
    assert res_unauth.status_code == 401

    # Authenticated request with valid key succeeds (status 200)
    res_auth = client.get("/api/v1/decision/RELIANCE", headers={"X-API-Key": "valid-secret-key"})
    assert res_auth.status_code == 200
    assert res_auth.json()["symbol"] in ("RELIANCE", "RELIANCE.NS")



def test_a2_endpoint_is_suspended_by_default(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_OPTIONS_A2", False)
    res = client.post("/api/v1/options/a2-payoff", json={
        "underlying": "NIFTY",
        "lower_strike": 22000,
        "upper_strike": 23000,
        "call_premium": 50,
        "put_premium": 50,
    })
    assert res.status_code == 503


def test_research_data_writes_require_separate_key(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "DATA_STORE_PATH", str(tmp_path / "research.sqlite3"))
    monkeypatch.setattr(settings, "DATA_WRITE_API_KEY", "write-key")
    payload = {"symbol": "DEMO", "legal_name": "Demo Industries Limited"}

    unauthenticated = client.post("/api/v1/data/companies", json=payload)
    authenticated = client.post("/api/v1/data/companies", json=payload, headers={"X-Data-Write-Key": "write-key"})

    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.json()["symbol"] == "DEMO.NS"

"""Unit & Integration tests for Frontend Asset Structure, API Wiring, and Auth Gate Enforcement.
"""

import os
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def _find_frontend_dir():
    curr = os.path.abspath(os.path.dirname(__file__))
    for _ in range(4):
        candidate = os.path.join(curr, "frontend_deploy")
        if os.path.exists(candidate):
            return candidate
        curr = os.path.dirname(curr)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend_deploy"))

FRONTEND_DIR = _find_frontend_dir()


def test_frontend_js_modules_exist():
    """Verify all core UI panel JS modules exist in frontend_deploy/js/."""
    js_dir = os.path.join(FRONTEND_DIR, "js")
    expected_modules = [
        "api.js",
        "bootstrap.js",
        "conviction_panel.js",
        "scorecard_panel.js",
        "cagr_matrix_panel.js",
        "swing_alerts_panel.js",
        "drift_panel.js",
        "multibagger_panel.js",
        "probability_panel.js",
        "compare_panel.js",
        "timeline_panel.js",
        "thesis_panel.js",
        "lifecycle_panel.js",
    ]
    for mod in expected_modules:
        mod_path = os.path.join(js_dir, mod)
        assert os.path.exists(mod_path), f"Missing JS module: {mod}"


def test_index_html_mount_points():
    """Verify index.html contains DOM section mount points for all panels."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    assert os.path.exists(index_path)
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    expected_ids = [
        "conviction-panel",
        "scorecard-panel",
        "cagr-matrix-panel",
        "thesis-panel",
        "lifecycle-panel",
        "timeline-panel",
        "compare-panel",
        "swing-alerts-panel",
        "watchlist-panel",
        "main-canvas",
    ]
    for sec_id in expected_ids:
        assert f'id="{sec_id}"' in html, f"Missing mount element id='{sec_id}' in index.html"


def test_api_js_endpoint_wiring():
    """Verify api.js contains fetch wrappers and apiFetch helper for all endpoints."""
    api_path = os.path.join(FRONTEND_DIR, "js", "api.js")
    assert os.path.exists(api_path)
    with open(api_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "apiFetch" in code, "apiFetch authorization wrapper missing in api.js"
    assert "X-API-Key" in code, "X-API-Key header injection missing in api.js"

    endpoints = [
        "/api/v1/research/scorecard",
        "/api/v1/research/cagr-matrix",
        "/api/v1/strategies/swing-alerts",
        "/api/v1/monitoring/drift",
        "/api/v1/research/multibagger-screener",
        "/api/v1/return-probability",
        "/api/v1/compare",
        "/api/v1/data/companies/",
        "/api/v1/research/governance-quality",
        "/api/v1/research/growth-arbitrage",
        "/api/v1/research/growth-inflection",
        "/api/v1/research/turnaround-stage",
        "/api/v1/portfolio/",
        "/api/v1/options/a2-payoff",
        "/api/v1/monitoring/strategy-health",
        "/api/v1/monitoring/prediction-ledger",
        "/api/v1/readiness",
        "/api/v1/technical/screener",
        "/api/v1/technical/regime",
        "/api/v1/research/swing-predictive",
        "/api/v1/research/walk-forward",
        "/api/v1/turnaround/rank/universe",
    ]
    for ep in endpoints:
        assert ep in code, f"Missing endpoint fetch call '{ep}' in api.js"


def test_api_auth_and_http_integration():
    """Live HTTP integration test verifying health, strategy catalog, and X-API-Key security gate."""
    client = TestClient(app)

    # 1. Health endpoint (always public)
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json().get("status") in ["healthy", "ONLINE"]

    # 2. Public endpoint access
    res_strat = client.get("/api/v1/strategies")
    assert res_strat.status_code == 200

    # 3. Auth gate enforcement test
    orig_req_auth = settings.REQUIRE_AUTH
    orig_key_secret = settings.API_KEY_SECRET

    try:
        settings.REQUIRE_AUTH = True
        settings.API_KEY_SECRET = "institutional_secret_test_key"

        # Request without X-API-Key must yield 401
        res_unauth = client.get("/api/v1/readiness")
        assert res_unauth.status_code == 401
        assert "Valid API authentication" in res_unauth.json().get("detail", "")

        # Request WITH X-API-Key must yield 200
        res_auth = client.get("/api/v1/readiness", headers={"X-API-Key": "institutional_secret_test_key"})
        assert res_auth.status_code == 200

    finally:
        settings.REQUIRE_AUTH = orig_req_auth
        settings.API_KEY_SECRET = orig_key_secret

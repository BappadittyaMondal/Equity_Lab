"""Unit tests for Frontend Asset Structure & API Integration Wiring.
"""

import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend_deploy")


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
    """Verify api.js contains fetch wrappers for newly integrated endpoints."""
    api_path = os.path.join(FRONTEND_DIR, "js", "api.js")
    assert os.path.exists(api_path)
    with open(api_path, "r", encoding="utf-8") as f:
        code = f.read()

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
    ]
    for ep in endpoints:
        assert ep in code, f"Missing endpoint fetch call '{ep}' in api.js"

"""Integration tests covering full decision pipeline:

synthesis -> arbiter -> orchestrator -> API decision endpoint -> frontend digest structure.
All tests execute fully offline without external network dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.synthesis.data_synthesizer import DataSynthesizer
from app.services.decision_brain.arbiter import Arbiter
from app.services.orchestration.orchestrator import Orchestrator

client = TestClient(app)


def test_full_pipeline_roundtrip():
    symbol = "RELIANCE"

    # Step 1: Synthesis
    synthesizer = DataSynthesizer()
    snapshot = synthesizer.synthesize(symbol)
    assert snapshot.symbol == "RELIANCE"
    assert snapshot.data_confidence_score >= 0.0

    # Step 2: Arbiter Decision
    arbiter = Arbiter()
    conviction = arbiter.arbitrate(symbol)
    assert conviction.symbol == "RELIANCE.NS" or conviction.symbol == "RELIANCE"
    assert conviction.conviction_score >= 0
    assert conviction.verdict in ["Strong Buy", "Buy", "Accumulate", "Watch", "Avoid"]

    # Step 3: Orchestration Layer
    orchestrator = Orchestrator()
    call = orchestrator.get_conviction(symbol, force_refresh=True)
    assert call.conviction_score == conviction.conviction_score

    narrative = orchestrator.narrate(symbol)
    assert len(narrative) > 0

    # Step 4: API Endpoint GET /api/v1/decision/{symbol}
    resp = client.get(f"/api/v1/decision/{symbol}")
    assert resp.status_code == 200
    data = resp.json()
    assert "verdict" in data
    assert "conviction_score" in data
    assert "primary_thesis" in data
    assert "contributing_engines" in data
    assert "contradicting_engines" in data
    assert "confidence_tier" in data


def test_watchlist_digest_endpoint():
    import sys, subprocess
    from pathlib import Path
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "nightly_watchlist_scan.py"
    digest_path = Path(__file__).resolve().parents[2] / "frontend_deploy" / "data" / "digests" / "watchlist_digest.json"
    if not digest_path.exists():
        subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)

    resp = client.get("/api/v1/digest/watchlist")
    assert resp.status_code == 200
    data = resp.json()
    assert "generated_at" in data
    assert "data" in data

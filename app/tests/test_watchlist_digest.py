import os
import json
import sys
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

# Import the FastAPI app
from app.main import app

client = TestClient(app)


def test_watchlist_digest_endpoint_exists():
    """Ensure the /api/v1/digest/watchlist endpoint returns 200 after the nightly script runs."""
    # Run the nightly script to generate the digest
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "nightly_watchlist_scan.py"
    # Execute the script in a subprocess
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Nightly script failed: {result.stderr}"

    # Now query the endpoint
    response = client.get("/api/v1/digest/watchlist")
    assert response.status_code == 200, f"Endpoint returned {response.status_code}"
    data = response.json()
    assert "generated_at" in data
    assert "data" in data
    # The data should be a dict mapping symbols to conviction payloads
    assert isinstance(data["data"], dict)


def test_watchlist_digest_file_created():
    """Directly check that the digest file exists after running the script."""
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "nightly_watchlist_scan.py"
    # Remove any existing file first
    digest_path = Path(__file__).resolve().parents[2] / "frontend_deploy" / "data" / "digests" / "watchlist_digest.json"
    if digest_path.exists():
        digest_path.unlink()
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Nightly script failed: {result.stderr}"
    assert digest_path.exists(), "Digest file was not created"
    # Load and verify JSON structure
    with open(digest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "generated_at" in data and "data" in data

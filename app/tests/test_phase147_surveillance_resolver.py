import pytest
from fastapi.testclient import TestClient
from app.services.data_ingestion.surveillance_resolver import SurveillanceResolver
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate
from app.main import app

client = TestClient(app)

def test_resolve_returns_clean_default_for_unknown_symbol():
    res = SurveillanceResolver.resolve("UNKNOWN_123")
    assert res["asm_stage"] == "CLEAN"
    assert res["circuit_band_pct"] == 20.0

def test_update_and_resolve_asm_stage():
    SurveillanceResolver.update("TEST1", asm_stage="Stage I")
    res = SurveillanceResolver.resolve("TEST1")
    assert res["asm_stage"] == "Stage I"

def test_bulk_update_multiple_records():
    records = [
        {"symbol": "TEST2", "asm_stage": "Stage II"},
        {"symbol": "TEST3", "esm_stage": "Stage I", "circuit_band_pct": 5.0}
    ]
    count = SurveillanceResolver.bulk_update(records)
    assert count == 2
    res3 = SurveillanceResolver.resolve("TEST3")
    assert res3["circuit_band_pct"] == 5.0

def test_get_all_flagged_returns_only_noclean():
    SurveillanceResolver.update("TEST4_CLEAN", asm_stage="CLEAN", circuit_band_pct=20.0)
    SurveillanceResolver.update("TEST5_FLAG", asm_stage="CLEAN", circuit_band_pct=10.0)
    flagged = SurveillanceResolver.get_all_flagged()
    symbols = [r["symbol"] for r in flagged]
    assert "TEST5_FLAG.NS" in symbols
    assert "TEST4_CLEAN.NS" not in symbols

def test_resolve_output_compatible_with_surveillance_gate():
    surv_data = SurveillanceResolver.resolve("TEST3")
    res = evaluate_surveillance_and_cost_gate(
        symbol="TEST3",
        price=100.0,
        trade_value_inr=100000.0,
        surveillance_data=surv_data
    )
    assert res.hard_gate_status != "DATA_INSUFFICIENT"

def test_surveillance_api_post_endpoint(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "DATA_WRITE_API_KEY", "testkey")
    
    resp = client.post(
        "/api/v1/data/surveillance",
        json=[{"symbol": "TEST_API", "gsm_stage": "Stage II"}],
        headers={"x-api-key": "testkey"}
    )
    assert resp.status_code == 200
    assert resp.json()["updated_count"] == 1
    
    res = SurveillanceResolver.resolve("TEST_API")
    assert res["gsm_stage"] == "Stage II"

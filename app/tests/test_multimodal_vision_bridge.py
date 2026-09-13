"""Unit tests for Phase 81: Genuine Multimodal Vision Perception Bridge."""

import pytest
import base64
from unittest.mock import patch, MagicMock
from app.services.research.multimodal_chart_reconciliation import MultimodalChartReconciliationEngine
from app.services.llm import analyze_chart_image_with_vision


def test_gemini_vision_chart_extraction_success(monkeypatch):
    """Verify analyze_chart_image_with_vision successfully parses structured JSON from Gemini."""
    dummy_b64 = base64.b64encode(b"fake_chart_image_bytes").decode("utf-8")
    mock_json_response = (
        '{\n'
        '  "spot_price": 2450.5,\n'
        '  "breakout_level": 2500.0,\n'
        '  "support_level": 2400.0,\n'
        '  "visual_pattern": "VCP_CONTRACTION",\n'
        '  "pattern_confidence": 0.88\n'
        '}'
    )

    monkeypatch.setenv("GEMINI_API_KEY", "test-valid-api-key")
    
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = mock_json_response
    mock_client.models.generate_content.return_value = mock_resp

    with patch("google.genai.Client", return_value=mock_client):
        res = analyze_chart_image_with_vision(dummy_b64)
        assert res["status"] == "SUCCESS"
        assert res["visual_price"] == 2450.5
        assert res["visual_breakout_level"] == 2500.0
        assert res["visual_support"] == 2400.0
        assert res["visual_pattern"] == "VCP_CONTRACTION"
        assert res["pattern_confidence"] == 0.88


def test_parse_chart_image_or_mock_wires_gemini_vision(monkeypatch):
    """Verify parse_chart_image_or_mock delegates to analyze_chart_image_with_vision."""
    dummy_b64 = base64.b64encode(b"fake_chart_image_bytes").decode("utf-8")
    mock_vision_payload = {
        "status": "SUCCESS",
        "visual_price": 1050.0,
        "visual_breakout_level": 1100.0,
        "visual_support": 1000.0,
        "visual_pattern": "CUP_AND_HANDLE",
        "pattern_confidence": 0.92,
    }

    monkeypatch.setenv("GEMINI_API_KEY", "test-key-12345")
    with patch("app.services.llm.analyze_chart_image_with_vision", return_value=mock_vision_payload):
        parsed = MultimodalChartReconciliationEngine.parse_chart_image_or_mock(base64_str=dummy_b64)
        assert parsed["image_received"] is True
        assert parsed["extraction_status"] == "GEMINI_VISION_EXTRACTED"
        assert parsed["visual_price"] == 1050.0
        assert parsed["visual_breakout_level"] == 1100.0
        assert parsed["visual_pattern"] == "CUP_AND_HANDLE"
        assert parsed["pattern_confidence"] == 0.92

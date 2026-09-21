"""Multimodal Watchlist Bridge — Phase 139.

Pipeline:
  1. (Optional) Gemini Vision OCR: image_base64 → OCR table extraction → list[str] symbols
  2. ScreenerCloudConnector: fetch fundamentals for each symbol
  3. InstitutionalMultibaggerEngine.evaluate_company() per symbol → verdict + risk flags
  4. MAP-Rank Pareto tournament across all audited symbols
  5. Returns MultimodalWatchlistResponse-compatible dict

Design principles:
- If raw_symbols provided, skip OCR (token-efficient).
- If image_base64 provided AND no raw_symbols, attempt Gemini Vision extraction.
- If Gemini is unavailable, log gracefully and proceed with empty symbol list.
- Never blocks the entire audit on a single symbol failure.
"""

import base64
import logging
import os
import re
from typing import Any, Dict, List, Optional

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research.map_rank_engine import build_map_rank_response

logger = logging.getLogger(__name__)


def _ocr_symbols_from_image(image_base64: str) -> List[str]:
    """Attempt Gemini Vision OCR to extract ticker symbols from a watchlist screenshot.

    Returns list of extracted NSE/BSE symbols.
    Falls back to empty list on error (never raises).
    """
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("Multimodal Watchlist Bridge: No Gemini API key found; skipping OCR.")
            return []
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        img_data = base64.b64decode(image_base64)
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(img_data))
        prompt = (
            "This is a brokerage or stock-screener watchlist screenshot. "
            "Extract all NSE/BSE stock ticker symbols visible in the image. "
            "Return ONLY a JSON array of strings, e.g.: [\"RELIANCE\", \"TCS\", \"HBLPOWER\"]. "
            "No explanations, no markdown, just the raw JSON array."
        )
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        # Parse JSON array from response
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            import json
            candidates = json.loads(match.group(0))
            return [normalize_symbol(str(s)) for s in candidates if isinstance(s, str) and s.strip()]
        return []
    except Exception as exc:
        logger.warning(f"Multimodal Watchlist Bridge OCR failed: {exc}")
        return []


def _get_fundamentals_for_symbols(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch fundamentals for each symbol using ScreenerCloudConnector.

    Returns {symbol: fund_dict}. Missing symbols get empty dict (fail-open for display).
    """
    result: Dict[str, Dict[str, Any]] = {}
    try:
        from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        if is_offline:
            # Offline mode: return minimal stubs so MAP-Rank can compute
            for sym in symbols:
                result[normalize_symbol(sym)] = {
                    "symbol": normalize_symbol(sym),
                    "sector": "DIVERSIFIED",
                    "debt_to_equity": 0.5,
                    "interest_coverage": 5.0,
                    "cfo_last_year": 100.0,
                    "net_profit_last_year": 80.0,
                    "peg_ratio": 1.2,
                    "sales_growth_3yr": 15.0,
                    "pe_ratio": None,
                }
            return result
        all_funds = ScreenerCloudConnector.get_all_fundamentals()
        sym_map = {
            item["symbol"].upper().split(".")[0]: item
            for item in all_funds if item.get("symbol")
        }
        for sym in symbols:
            norm = normalize_symbol(sym)
            fund = sym_map.get(norm) or sym_map.get(sym.upper()) or {}
            result[norm] = fund
    except Exception as exc:
        logger.warning(f"Multimodal Watchlist Bridge: fundamentals fetch failed: {exc}")
        for sym in symbols:
            result[normalize_symbol(sym)] = {}
    return result


def _arbiter_audit_symbol(symbol: str, fund: Dict[str, Any], intent: Optional[str]) -> Dict[str, Any]:
    """Run InstitutionalMultibaggerEngine on a single symbol.

    Returns WatchlistAuditEntry-compatible dict. Never raises.
    """
    try:
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        # Inject symbol into fund dict if missing
        if not fund.get("symbol"):
            fund = dict(fund)
            fund["symbol"] = symbol
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        return {
            "symbol": symbol,
            "verdict": result.get("archetype", "UNKNOWN"),
            "conviction_score": result.get("overall_score"),
            "archetype": result.get("archetype"),
            "risk_flags": result.get("risk_flags", [])[:5],
            "caqi": result.get("caqi"),
            "caqi_gate": result.get("caqi_gate", "DATA_UNAVAILABLE"),
            "deme_hr": result.get("deme_hr"),
            "deme_hr_verdict": result.get("deme_hr_verdict", "DATA_UNAVAILABLE"),
            "pareto_rank": None,
            "error": None,
        }
    except Exception as exc:
        logger.warning(f"Multimodal Watchlist Bridge: arbiter audit failed for {symbol}: {exc}")
        return {
            "symbol": symbol,
            "verdict": "ERROR",
            "conviction_score": None,
            "archetype": None,
            "risk_flags": [],
            "caqi": None,
            "caqi_gate": "DATA_UNAVAILABLE",
            "deme_hr": None,
            "deme_hr_verdict": "DATA_UNAVAILABLE",
            "pareto_rank": None,
            "error": str(exc),
        }


def audit_watchlist(
    image_base64: Optional[str] = None,
    raw_symbols: Optional[List[str]] = None,
    intent: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the full Multimodal Watchlist Bridge pipeline.

    Args:
        image_base64: Base64-encoded brokerage watchlist screenshot (PNG/JPEG). Optional.
        raw_symbols: Pre-parsed symbol list (skips OCR). Optional.
        intent: Investment archetype (MULTIBAGGER, SIP_COMPOUNDER, etc.). Optional.

    Returns:
        MultimodalWatchlistResponse-compatible dict.
    """
    ocr_detected: List[str] = []

    # Step 1: Resolve symbol list
    if raw_symbols and len(raw_symbols) > 0:
        symbols = [normalize_symbol(s) for s in raw_symbols]
    elif image_base64:
        ocr_detected = _ocr_symbols_from_image(image_base64)
        symbols = ocr_detected
    else:
        symbols = []

    if not symbols:
        return {
            "status": "NO_SYMBOLS_FOUND",
            "ocr_symbols_detected": ocr_detected,
            "total_audited": 0,
            "intent": intent,
            "audit_results": [],
            "map_rank_summary": None,
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source="Phase 139 MultimodalWatchlistBridge"),
        }

    # Step 2: Fetch fundamentals
    funds = _get_fundamentals_for_symbols(symbols)

    # Step 3: Arbiter audit per symbol
    audit_results: List[Dict[str, Any]] = []
    for sym in symbols:
        fund = funds.get(sym) or {}
        entry = _arbiter_audit_symbol(sym, fund, intent)
        audit_results.append(entry)

    # Step 4: MAP-Rank Pareto tournament
    map_rank_result = build_map_rank_response(
        symbols=symbols,
        fundamentals_lookup=funds,
        intent=intent,
    )
    ranked = map_rank_result.get("ranked", [])

    # Inject pareto_rank into audit_results
    rank_lookup = {r["symbol"]: r["pareto_rank"] for r in ranked}
    for entry in audit_results:
        entry["pareto_rank"] = rank_lookup.get(entry["symbol"])

    return {
        "status": "OK",
        "ocr_symbols_detected": ocr_detected,
        "total_audited": len(audit_results),
        "intent": intent,
        "audit_results": audit_results,
        "map_rank_summary": ranked,
        "executed_at": get_ist_now_str(),
        "meta": create_meta_header(source="Phase 139 MultimodalWatchlistBridge"),
    }

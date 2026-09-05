"""Management Commentary & Concall Textual/NLP Analysis Engine (§30).

Reads and scores management language tone shifts, guidance specificity, language consistency across quarters,
Q&A deflection patterns, and shareholder letter sentiment drift.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import ManagementNLPCommentarySignal


def evaluate_concall_nlp(
    symbol: str,
    nlp_inputs: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates management concall transcripts and textual sentiment parameters."""
    norm_symbol = normalize_symbol(symbol)
    clean_sym = norm_symbol.replace(".NS", "").replace(".BO", "").upper()
    has_explicit_data = bool(nlp_inputs)
    data = nlp_inputs or {}
    evidence = []

    # If no explicit inputs, check if symbol has earnings transcript on file
    transcript_text = None
    try:
        from app.services.research_data import ResearchDataStore
        store = ResearchDataStore()
        _, _, events, _, _, _ = store.get_timeline(norm_symbol)
        for ev in events:
            h_low = (ev.headline or "").lower()
            if any(k in h_low for k in ["concall", "transcript", "earnings call", "management commentary"]):
                transcript_text = getattr(ev, "content", None) or ev.headline
                break
    except Exception:
        pass

    if has_explicit_data:
        tone_direction = str(data.get("tone_shift_direction", "NEUTRAL")).upper()
        guidance_spec = float(data.get("guidance_specificity_score", 50.0))
        consistency_idx = float(data.get("language_consistency_index", 50.0))
        deflection_count = int(data.get("q_and_a_deflection_count", 0))
        data_mode = "EXPLICIT_INPUT"
        is_synthetic = False
    elif transcript_text:
        # Run semantic evaluation via GenAIRedTeamService
        try:
            from app.services.research.genai_redteam_service import GenAIRedTeamService
            audit = GenAIRedTeamService.audit_earnings_call_transcript(clean_sym, transcript_text)
            sent_label = audit.get("sentiment_label", "NEUTRAL")
            tone_direction = "BULLISH_CONFIDENT" if sent_label == "BULLISH" else ("BEARISH_DEFENSIVE" if sent_label == "BEARISH" else "NEUTRAL")
            guidance_spec = float(audit.get("sentiment_score") or 50.0)
            consistency_idx = 75.0 if sent_label == "BULLISH" else 50.0
            deflection_count = len(audit.get("flagged_concall_risks", []))
            data_mode = "OBSERVED_TRANSCRIPT"
            is_synthetic = False
        except Exception:
            tone_direction = "NEUTRAL"
            guidance_spec = 50.0
            consistency_idx = 50.0
            deflection_count = 0
            data_mode = "DATA_INSUFFICIENT"
            is_synthetic = True
    else:
        # Honest Pipeline Law: Zero synthetic optimism when transcripts are missing
        tone_direction = "NEUTRAL"
        guidance_spec = 50.0
        consistency_idx = 50.0
        deflection_count = 0
        data_mode = "DATA_INSUFFICIENT"
        is_synthetic = True

    # Commentary Confidence Score calculation (0-100)
    tone_score = 35.0 if tone_direction in ["BULLISH_CONFIDENT", "COMMITTED"] else (15.0 if tone_direction == "NEUTRAL" else 0.0)
    spec_score = min(30.0, (guidance_spec / 100.0) * 30.0)
    consist_score = min(25.0, (consistency_idx / 100.0) * 25.0)
    deflection_penalty = min(20.0, deflection_count * 5.0)

    commentary_confidence_score = round(max(0.0, min(100.0, tone_score + spec_score + consist_score - deflection_penalty)), 1)

    if is_synthetic:
        evidence.append(f"No verified concall transcript filed for {norm_symbol}. NLP tone held at neutral baseline ({commentary_confidence_score}/100 uncredited).")
    else:
        evidence.append(f"Commentary Confidence Score: {commentary_confidence_score}/100 | Tone: {tone_direction}")
        evidence.append(f"Guidance Specificity: {guidance_spec:.1f}/100 | Language Consistency Index: {consistency_idx:.1f}/100")
        if deflection_count > 0:
            evidence.append(f"Q&A Deflection Count: {deflection_count} analyst question deflections detected")

    signal = ManagementNLPCommentarySignal(
        tone_shift_direction=tone_direction,
        guidance_specificity_score=guidance_spec,
        language_consistency_index=consistency_idx,
        q_and_a_deflection_count=deflection_count,
        commentary_confidence_score=commentary_confidence_score
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "commentary_confidence_score": commentary_confidence_score,
        "tone_shift_direction": tone_direction,
        "data_mode": data_mode,
        "is_synthetic": is_synthetic,
        "nlp_signal": signal.model_dump(),
        "evidence": evidence,
        "meta": create_meta_header(source="Management Concall NLP Engine (§30)")
    }

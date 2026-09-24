"""Weak Signal Ingestion & Multi-Source Parser for Geopolitical PEWS Engine.

Automates the ingestion and classification of heterogeneous pre-strike weak signals:
1. LEADER_SIGNALLING_ANOMALY (symbolic attire, war room photo ops, unannounced base visits)
2. AIRSPACE_NOTAM_CLOSURE (commercial airspace closures, flight corridors)
3. AIS_TRANSPONDER_DARK (naval/tanker stealth transits in chokepoints)
4. DIPLOMATIC_SCHEDULE_COLLAPSE (embassy evacuations, summit cancellations)
5. CRUDE_CALL_SKEW_SPIKE (options market hedging surges)
6. SOVEREIGN_FX_SWAP_EMERGENCY (reserve freezes, emergency FX swaps)

Bridges unstructured OSINT/news text into strictly typed PreEventSignal objects
feeding Phase 140's Bayesian log-odds imminence formulation.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from app.services.research.geopolitical_engine import (
    PreEventSignal,
    evaluate_pre_event_weak_signals,
)
from app.models.schemas import PreEventEvaluationResponse


class ParsedWeakSignal(BaseModel):
    """Normalized structured weak signal extracted from text or feeds."""
    signal_type: str
    theater: str
    intensity: float = Field(..., ge=0.0, le=1.0)
    likelihood_ratio: float = Field(..., gt=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    age_hours: float = Field(0.0, ge=0.0)
    source_description: str
    matched_triggers: List[str] = Field(default_factory=list)
    reasoning: str


class WeakSignalParserService:
    """Service to parse, classify, and extract Bayesian signals from raw text dispatches."""

    # ── KEYWORD DICTIONARIES FOR SIGNAL DISCOVERY ──
    _SIGNAL_RULES = {
        "LEADER_SIGNALLING_ANOMALY": {
            "default_lr": 2.8,
            "patterns": [
                r"\b(white\s*cap|black\s*(jacket|vest|kurta|attire)|camo|fatigues)\b",
                r"\b(war\s*room|situation\s*room)\s*(photo|meeting|briefing|broadcast)\b",
                r"\b(unannounced|surprise|emergency)\s*(base\s*visit|military\s*inspection|command\s*center)\b",
                r"\b(bunker|national\s*security\s*council\s*emergency)\b",
                r"\b(symbolic\s*(dress|attire|signalling)|leader\s*posture)\b",
            ],
            "description": "Unusual leadership posturing, symbolic attire shifts, or command center photo releases.",
        },
        "AIRSPACE_NOTAM_CLOSURE": {
            "default_lr": 8.5,
            "patterns": [
                r"\b(notam|notice\s*to\s*airmen)\b",
                r"\b(airspace\s*(closure|closed|restriction)|no-fly\s*zone)\b",
                r"\b(fir\s*(closed|restricted)|flight\s*diversion\s*corridor)\b",
                r"\b(missile\s*(test|launch)\s*window|artillery\s*exclusion\s*zone)\b",
            ],
            "description": "Civil aviation FIR closures or airspace restrictions indicating military operations.",
        },
        "AIS_TRANSPONDER_DARK": {
            "default_lr": 6.0,
            "patterns": [
                r"\b(ais\s*(dark|disabled|off|spoofing)|transponder\s*(silent|off))\b",
                r"\b(stealth\s*(transit|convoy)|naval\s*task\s*force)\b",
                r"\b(strait\s*of\s*hormuz|bab\s*el-?mandeb|taiwan\s*strait)\s*(tankers|vessels)\b",
            ],
            "description": "Naval or maritime commercial vessels turning off AIS tracking in strategic chokepoints.",
        },
        "DIPLOMATIC_SCHEDULE_COLLAPSE": {
            "default_lr": 4.5,
            "patterns": [
                r"\b(embassy\s*evacuation|staff\s*departure|ambassador\s*recalled)\b",
                r"\b(summit\s*(cancelled|abruptly\s*ended|postponed)|bilateral\s*talks\s*collapse)\b",
                r"\b(travel\s*advisory\s*level\s*4|citizens\s*leave\s*immediately)\b",
            ],
            "description": "Sudden diplomatic mission withdrawals or abrupt top-level summit cancellations.",
        },
        "CRUDE_CALL_SKEW_SPIKE": {
            "default_lr": 5.2,
            "patterns": [
                r"\b(crude\s*call\s*skew|brent\s*call\s*skew|upside\s*call\s*buying)\b",
                r"\b(25-?delta\s*skew|call\s*premium\s*surge|oil\s*tail\s*risk\s*hedge)\b",
                r"\b(out-of-the-money\s*call\s*volume\s*spike)\b",
            ],
            "description": "Options volatility surface upside skew inversion indicating aggressive hedging.",
        },
        "SOVEREIGN_FX_SWAP_EMERGENCY": {
            "default_lr": 3.5,
            "patterns": [
                r"\b(emergency\s*swap\s*line|fx\s*swap\s*activation)\b",
                r"\b(gold\s*repatriation|reserves\s*freezing|central\s*bank\s*emergency\s*liquidity)\b",
                r"\b(capital\s*controls\s*preparedness)\b",
            ],
            "description": "Emergency central bank foreign exchange liquidity lines or reserve defense.",
        },
    }

    _THEATER_PATTERNS = {
        "MIDDLE_EAST": [r"\b(middle\s*east|iran|israel|houthi|yemen|red\s*sea|hormuz|tehran|tel\s*aviv|gulf|lebanon|syria)\b"],
        "SOUTH_ASIA": [r"\b(south\s*asia|india|pakistan|kashmir|loc|balakot|punjab\s*border|ladakh|china\s*border)\b"],
        "TAIWAN_STRAIT": [r"\b(taiwan\s*strait|taiwan|pla|beijing|taipei|south\s*china\s*sea)\b"],
        "EASTERN_EUROPE": [r"\b(eastern\s*europe|russia|ukraine|black\s*sea|crimea|nato|baltic)\b"],
    }

    @classmethod
    def detect_theater(cls, text: str) -> str:
        """Determines the geographic theater from text keywords."""
        lower_text = text.lower()
        for theater, patterns in cls._THEATER_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, lower_text):
                    return theater
        return "GLOBAL"

    @classmethod
    def parse_text_to_signals(
        cls,
        text: str,
        source: str = "OSINT_NEWS_DISPATCH",
        age_hours: float = 2.0,
    ) -> List[ParsedWeakSignal]:
        """Scans free-text dispatches, news headlines, and reports for weak Bayesian signals."""
        lower_text = text.lower()
        theater = cls.detect_theater(text)
        extracted: List[ParsedWeakSignal] = []

        for sig_type, rule in cls._SIGNAL_RULES.items():
            matched_triggers = []
            for pat in rule["patterns"]:
                matches = re.findall(pat, lower_text)
                if matches:
                    if isinstance(matches[0], tuple):
                        matched_triggers.extend([m[0] for m in matches if m[0]])
                    else:
                        matched_triggers.extend(matches)

            if matched_triggers:
                # Deduplicate triggers
                unique_triggers = sorted(list(set(matched_triggers)))
                # Intensity scales with match richness
                intensity = min(1.0, 0.65 + 0.15 * len(unique_triggers))
                confidence = min(1.0, 0.70 + 0.10 * len(unique_triggers))
                lr = rule["default_lr"]

                # If leader anomaly specifically mentions symbolic clothing/cap/vest, boost LR
                if sig_type == "LEADER_SIGNALLING_ANOMALY" and any(k in " ".join(unique_triggers) for k in ["cap", "vest", "kurta", "attire"]):
                    lr = round(lr * 1.25, 2)

                extracted.append(
                    ParsedWeakSignal(
                        signal_type=sig_type,
                        theater=theater,
                        intensity=round(intensity, 2),
                        likelihood_ratio=lr,
                        confidence=round(confidence, 2),
                        age_hours=age_hours,
                        source_description=source,
                        matched_triggers=unique_triggers,
                        reasoning=f"Detected pattern(s) {unique_triggers} matching {rule['description']}",
                    )
                )

        return extracted

    @classmethod
    def ingest_and_evaluate(
        cls,
        text: str,
        source: str = "OSINT_MONITOR",
        prior_probability: float = 0.05,
        age_hours: float = 1.0,
    ) -> Dict[str, Any]:
        """Full pipeline: Ingests raw text, extracts weak signals, and executes Bayesian imminence calculation."""
        parsed_signals = cls.parse_text_to_signals(text, source=source, age_hours=age_hours)
        theater = cls.detect_theater(text)

        if not parsed_signals:
            return {
                "status": "NO_SIGNALS_DETECTED",
                "theater": theater,
                "parsed_signals_count": 0,
                "signals": [],
                "evaluation": None,
                "summary": "No verified weak signals matching canonical geopolitical taxonomy were found in input.",
            }

        # Convert to PreEventSignal objects
        core_signals = [
            PreEventSignal(
                signal_type=s.signal_type,
                intensity=s.intensity,
                likelihood_ratio=s.likelihood_ratio,
                confidence=s.confidence,
                age_hours=s.age_hours,
                theater=s.theater,
                source_description=s.source_description,
            )
            for s in parsed_signals
        ]

        # Execute Bayesian calculation
        eval_result = evaluate_pre_event_weak_signals(
            signals=core_signals,
            prior_probability=prior_probability,
            theater=theater,
        )

        return {
            "status": "SUCCESS",
            "theater": theater,
            "parsed_signals_count": len(parsed_signals),
            "signals": [s.model_dump() for s in parsed_signals],
            "evaluation": eval_result,
            "summary": (
                f"Ingested {len(parsed_signals)} weak signal(s) in {theater}. "
                f"Posterior probability of imminence: {eval_result['pews_probability']*100:.1f}% "
                f"({eval_result['imminence_rating']})."
            ),
        }

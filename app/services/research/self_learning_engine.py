"""Autonomous Epistemic Dynamic Memory & Self-Learning Engine (Phase 142).

Enables continuous knowledge acquisition, unmapped concept detection, zero-trust
epistemic verification, and dynamic Bayesian prior adaptation without mutating
certified production code.

Stores certified facts and quarantines speculative narrative noise in
data/dynamic_knowledge/learned_rules_registry.json.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DYNAMIC_KNOWLEDGE_DIR = os.path.join("data", "dynamic_knowledge")
REGISTRY_FILE = os.path.join(DYNAMIC_KNOWLEDGE_DIR, "learned_rules_registry.json")


class KnowledgeEntity(BaseModel):
    """Normalized atomic knowledge entity stored in the dynamic registry."""
    entity_id: str
    canonical_name: str
    category: str  # MARKET_MICROSTRUCTURE, GEOPOLITICAL_CORRIDOR, CULTURAL_GRAYZONE, REGULATORY_MECHANISM, ACCOUNTING_INFLECTION
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    verification_status: str  # CERTIFIED_FACT, PROVISIONAL_OBSERVATION, SPECULATIVE_NARRATIVE_NOISE
    source_origin: str
    relevance_vector: Dict[str, float] = Field(default_factory=dict)
    bayesian_prior_modifier: Dict[str, Any] = Field(default_factory=dict)
    description: str
    sensationalism_penalty: float = Field(0.0, ge=0.0, le=1.0)
    created_at_utc: str
    last_validated_at_utc: str


class SelfLearningEngine:
    """Institutional autonomous epistemic memory and continuous self-learning engine."""

    SENSATIONALISM_PATTERNS = [
        r"\b(secretly\s*captur(e|ing)|secret\s*plan\s*to\s*invade)\b",
        r"\b(world\s*war\s*3\s*imminent|market\s*apocalypse|total\s*collapse\s*2027)\b",
        r"\b(guaranteed\s*(80x|100x|10x)|turn\s*\d+\s*into\s*\d+\s*lakh)\b",
        r"\b(100%\s*win\s*rate|zero\s*risk\s*scalping|holy\s*grail)\b",
        r"\b(they\s*don't\s*want\s*you\s*to\s*know|hidden\s*elite\s*agenda)\b",
    ]

    UNMAPPED_CANDIDATE_PATTERNS = {
        "EXCHANGE_CASS_MECHANISM": {
            "patterns": [r"\b(cass|closing\s*auction\s*session\s*system|closing\s*auction)\b"],
            "name": "Exchange Closing Auction Session System (CASS)",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Post-market multilateral closing auction establishing deterministic VWAP and dampening end-of-session volatility.",
            "relevance": {"swing_3d": 0.15, "swing_10d": 0.10, "sip_compounder": 0.0, "turnaround": 0.05},
            "modifier": {"metric": "closing_vwap_stability", "weight_delta": 0.10},
        },
        "LITHIUM_CORRIDOR_RIGI": {
            "patterns": [r"\b(lithium\s*triangle|argentina\s*lithium|rigi\s*framework)\b"],
            "name": "Lithium Triangle Strategic Resource Concessions",
            "category": "GEOPOLITICAL_CORRIDOR",
            "desc": "Bilateral foreign direct investment in South American lithium brine reserves under RIGI regulatory concessions.",
            "relevance": {"swing_3d": 0.0, "swing_10d": 0.05, "sip_compounder": 0.35, "multibagger": 0.60},
            "modifier": {"metric": "ev_battery_input_elasticity", "weight_delta": 0.15},
        },
        "NON_DOLLAR_BILATERAL_SETTLEMENT": {
            "patterns": [r"\b(rupee-?dirham\s*settlement|inr-?aed\s*trade|local\s*currency\s*clearing)\b"],
            "name": "Non-Dollar Bilateral Trade Settlement Corridor",
            "category": "REGULATORY_MECHANISM",
            "desc": "Direct bilateral central bank rupee-dirham clearing accounts bypassing SWIFT dollar conversion spreads.",
            "relevance": {"swing_3d": 0.0, "swing_10d": 0.0, "sip_compounder": 0.40, "turnaround": 0.10},
            "modifier": {"metric": "fx_pass_through_hedge", "weight_delta": 0.20},
        },
        "CULTURAL_CONSUMER_BOYCOTT_CORRIDOR": {
            "patterns": [r"\b(consumer\s*boycott\s*campaign|franchise\s*footfall\s*plunge|bds\s*movement)\b"],
            "name": "Decentralized Cultural Consumer Boycott Corridors",
            "category": "CULTURAL_GRAYZONE",
            "desc": "Organic socio-religious consumer boycotts causing asymmetric revenue drag across multinational food/retail franchises.",
            "relevance": {"swing_3d": 0.0, "swing_10d": 0.05, "positional_30d": 0.30, "sip_compounder": 0.50},
            "modifier": {"metric": "operating_margin_drag_pct", "weight_delta": -0.15},
        },
        "SOCIO_RELIGIOUS_MUHURAT_DEMAND": {
            "patterns": [r"\b(muhurat\s*trading\s*demand|dhanteras\s*gold\s*inflow|wedding\s*season\s*muhurat)\b"],
            "name": "Indic Socio-Religious Festive Demand Clustering",
            "category": "CULTURAL_GRAYZONE",
            "desc": "Concentrated auspicious buying windows driving seasonal liquidity surges across jewelry, auto, and consumer durables.",
            "relevance": {"swing_3d": 0.25, "swing_10d": 0.40, "positional_30d": 0.60, "sip_compounder": 0.15},
            "modifier": {"metric": "seasonal_q3_revenue_lift", "weight_delta": 0.12},
        },
    }

    def __init__(self, registry_file: Optional[str] = None):
        self.registry_file = registry_file or REGISTRY_FILE
        self._ensure_store()

    def _ensure_store(self) -> None:
        """Ensures persistence directory and initial registry structure exist."""
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        if not os.path.exists(self.registry_file):
            initial_data = {
                "version": "1.0.0",
                "last_updated_utc": datetime.now(timezone.utc).isoformat(),
                "entities": {},
            }
            try:
                with open(self.registry_file, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error("Failed to initialize dynamic knowledge registry: %s", e)

    def _read_registry(self) -> Dict[str, Any]:
        """Reads raw JSON registry from disk."""
        self._ensure_store()
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error reading dynamic knowledge registry: %s", e)
            return {"version": "1.0.0", "last_updated_utc": datetime.now(timezone.utc).isoformat(), "entities": {}}

    def _write_registry(self, data: Dict[str, Any]) -> bool:
        """Writes JSON registry atomically to disk."""
        self._ensure_store()
        data["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
        temp_file = f"{self.registry_file}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.registry_file)
            return True
        except Exception as e:
            logger.error("Error writing dynamic knowledge registry: %s", e)
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            return False

    def detect_sensationalism(self, text: str) -> float:
        """Computes a sensationalism penalty score [0.0, 1.0] from linguistic triggers."""
        lower = text.lower()
        matches = 0
        for pat in self.SENSATIONALISM_PATTERNS:
            if re.search(pat, lower):
                matches += 1
        return min(1.0, round(matches * 0.35, 2))

    def detect_knowledge_gaps(self, text: str) -> List[Dict[str, Any]]:
        """Scans unstructured text for unmapped entities matching canonical gap patterns."""
        lower = text.lower()
        gaps: List[Dict[str, Any]] = []

        for entity_id, meta in self.UNMAPPED_CANDIDATE_PATTERNS.items():
            matched = False
            for pat in meta["patterns"]:
                if re.search(pat, lower):
                    matched = True
                    break
            if matched:
                gaps.append({
                    "entity_id": entity_id,
                    "canonical_name": meta["name"],
                    "category": meta["category"],
                    "description": meta["desc"],
                    "default_relevance": meta["relevance"],
                    "default_modifier": meta["modifier"],
                })

        return gaps

    def evaluate_and_learn_entity(
        self,
        entity_id: str,
        text_context: str,
        source_origin: str = "INTERACTION_DIALOGUE",
        provenance_score: float = 0.80,
        corroboration_count: int = 1,
    ) -> KnowledgeEntity:
        """Evaluates an unmapped concept through zero-trust epistemic validation and persists it."""
        sensationalism = self.detect_sensationalism(text_context)
        corrob_factor = min(0.30, corroboration_count * 0.10)
        
        # Confidence formulation: Provenance (0.60) + Corroboration (0.30) - Sensationalism (0.40)
        raw_confidence = (0.60 * provenance_score) + corrob_factor - (0.40 * sensationalism)
        confidence = max(0.05, min(0.99, round(raw_confidence, 2)))

        # Classification boundary
        if sensationalism >= 0.50 or confidence < 0.40:
            status = "SPECULATIVE_NARRATIVE_NOISE"
        elif confidence >= 0.70:
            status = "CERTIFIED_FACT"
        else:
            status = "PROVISIONAL_OBSERVATION"

        # Lookup default meta if standard pattern
        meta = self.UNMAPPED_CANDIDATE_PATTERNS.get(entity_id, {})
        canonical_name = meta.get("name", entity_id.replace("_", " ").title())
        category = meta.get("category", "MARKET_MICROSTRUCTURE")
        desc = meta.get("desc", f"Learned concept: {text_context[:200]}")
        relevance = meta.get("relevance", {"general": 0.50})
        modifier = meta.get("modifier", {"status": "ACTIVE"})

        now_str = datetime.now(timezone.utc).isoformat()
        entity = KnowledgeEntity(
            entity_id=entity_id,
            canonical_name=canonical_name,
            category=category,
            confidence_score=confidence,
            verification_status=status,
            source_origin=source_origin,
            relevance_vector=relevance,
            bayesian_prior_modifier=modifier,
            description=desc,
            sensationalism_penalty=sensationalism,
            created_at_utc=now_str,
            last_validated_at_utc=now_str,
        )

        # Persist to registry
        reg = self._read_registry()
        reg["entities"][entity_id] = entity.model_dump()
        self._write_registry(reg)

        return entity

    def learn_from_text(
        self,
        text: str,
        source_origin: str = "MULTIMODAL_INGESTION",
        provenance_score: float = 0.85,
    ) -> List[KnowledgeEntity]:
        """Scans text for all knowledge gaps, validates them, and registers them."""
        gaps = self.detect_knowledge_gaps(text)
        learned: List[KnowledgeEntity] = []
        for g in gaps:
            ent = self.evaluate_and_learn_entity(
                entity_id=g["entity_id"],
                text_context=text,
                source_origin=source_origin,
                provenance_score=provenance_score,
                corroboration_count=2,
            )
            learned.append(ent)
        return learned

    def query_learned_priors(
        self,
        category: Optional[str] = None,
        min_confidence: float = 0.60,
        exclude_noise: bool = True,
    ) -> List[Dict[str, Any]]:
        """Queries verified dynamic priors for consumption by research or decision engines."""
        reg = self._read_registry()
        results: List[Dict[str, Any]] = []

        for eid, ent in reg.get("entities", {}).items():
            if exclude_noise and ent.get("verification_status") == "SPECULATIVE_NARRATIVE_NOISE":
                continue
            if ent.get("confidence_score", 0.0) < min_confidence:
                continue
            if category and ent.get("category") != category:
                continue
            results.append(ent)

        return results

    def get_learning_stats(self) -> Dict[str, Any]:
        """Returns diagnostic metrics on dynamic knowledge acquisition."""
        reg = self._read_registry()
        entities = reg.get("entities", {})
        certified = sum(1 for e in entities.values() if e.get("verification_status") == "CERTIFIED_FACT")
        provisional = sum(1 for e in entities.values() if e.get("verification_status") == "PROVISIONAL_OBSERVATION")
        noise = sum(1 for e in entities.values() if e.get("verification_status") == "SPECULATIVE_NARRATIVE_NOISE")

        categories = {}
        for e in entities.values():
            c = e.get("category", "UNKNOWN")
            categories[c] = categories.get(c, 0) + 1

        return {
            "total_entities": len(entities),
            "certified_facts": certified,
            "provisional_observations": provisional,
            "speculative_noise_quarantined": noise,
            "categories": categories,
            "last_updated_utc": reg.get("last_updated_utc"),
        }

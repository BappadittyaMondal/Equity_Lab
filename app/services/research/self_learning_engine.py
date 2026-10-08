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
        "AI_DATACENTER_OPTICAL_FIBER": {
            "patterns": [r"\b(optical\s*fiber|ofc|data\s*center\s*fiber|ai\s*cluster\s*bandwidth|optical\s*transceiver)\b"],
            "name": "AI Data Center Optical Fiber & High-Bandwidth Interconnect Supercycle",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Surge in global AI data center GPU cluster buildouts driving exponential demand for high-count Optical Fiber Cables (OFC) due to copper latency/attenuation limits.",
            "relevance": {"swing_3d": 0.10, "swing_10d": 0.25, "positional_30d": 0.50, "multibagger": 0.70, "sip_compounder": 0.40},
            "modifier": {"metric": "data_center_fiber_tailwind", "weight_delta": 0.15},
        },
        "EMS_DEFENSE_CAPEX_INFLECTION": {
            "patterns": [r"\b(ems\s*capex|defense\s*indigenization|order\s*book-?to-?bill|cwip\s*expansion|electronics\s*manufacturing\s*services)\b"],
            "name": "EMS & Defense Manufacturing Capex Inflection (2027 Supercycle)",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "Massive Capital Work-in-Progress (CWIP) conversion and order book-to-bill > 2.5x driving operating leverage ahead of quarterly earnings.",
            "relevance": {"swing_3d": 0.05, "swing_10d": 0.20, "positional_30d": 0.60, "multibagger": 0.75, "sip_compounder": 0.35},
            "modifier": {"metric": "cwip_operating_leverage_lift", "weight_delta": 0.18},
        },
        "SOVEREIGN_DEBT_FISCAL_DOMINANCE": {
            "patterns": [r"\b(sovereign\s*debt\s*to\s*gdp|debt\s*grows\s*faster\s*than\s*economy|fiscal\s*dominance|currency\s*debasement|peg\s*collapse)\b"],
            "name": "Sovereign Debt-to-GDP Escalation & Fiat Debasement Risk",
            "category": "GEOPOLITICAL_CORRIDOR",
            "desc": "National debt exceeding 80-100% of GDP with interest payments crowding out capex, necessitating monetary debasement and rewarding pricing-power equities & gold.",
            "relevance": {"swing_3d": 0.0, "swing_10d": 0.05, "positional_30d": 0.20, "sip_compounder": 0.60, "turnaround": 0.30},
            "modifier": {"metric": "macro_fiat_debasement_hedge", "weight_delta": 0.20},
        },
        "VIJAY_THAKKAR_STAGE2_MOMENTUM": {
            "patterns": [r"\b(vijay\s*thakkar|price\s*is\s*god\s*volume\s*is\s*priest|52\s*week\s*high\s*momentum|stage\s*2\s*breakout\s*investing|10\s*ema\s*trailing)\b"],
            "name": "Vijay Thakkar Stage 2 Pure Price-Volume Momentum System",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Zero lagging indicators; buying top relative-strength market leaders within 10-15% of 52W High on >= 2.5x volume expansion with 10/20 EMA trailing stops.",
            "relevance": {"swing_3d": 0.40, "swing_10d": 0.60, "positional_30d": 0.70, "multibagger": 0.50, "sip_compounder": 0.0},
            "modifier": {"metric": "price_volume_stage2_acceleration", "weight_delta": 0.20},
        },
        "SMC_ORDER_BLOCK_FVG_CONFLUENCE": {
            "patterns": [r"\b(order\s*block|fair\s*value\s*gap|fvg|liquidity\s*sweep|mitigation\s*entry|smart\s*money\s*concepts)\b"],
            "name": "Institutional Order Block & Fair Value Gap (FVG) Confluence",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Algorithmic 3-step institutional liquidity sequence: Liquidity Sweep (stop hunt) followed by impulsive displacement leaving an FVG, entered upon mitigation retest.",
            "relevance": {"swing_3d": 0.60, "swing_10d": 0.55, "positional_30d": 0.40, "multibagger": 0.30, "sip_compounder": 0.0},
            "modifier": {"metric": "institutional_order_block_confluence", "weight_delta": 0.15},
        },
        "KEDIANOMICS_WAVE_EQUILIBRIUM": {
            "patterns": [r"\b(sushil\s*kedia|kedianomics|elliott\s*wave\s*fractal|wave\s*3\s*impulse|wave\s*5\s*exhaustion|invalidation\s*level|tea\s*master)\b"],
            "name": "Sushil Kedia Kedianomics Multi-Fractal Wave Equilibrium",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Wave degree hierarchy distinguishing fresh early Wave 3 impulse breakouts from late Wave 5 exhaustion tops with exact single-tick structural invalidation price levels and 4-tier TA discipline.",
            "relevance": {"swing_3d": 0.45, "swing_10d": 0.65, "positional_30d": 0.70, "multibagger": 0.55, "sip_compounder": 0.10},
            "modifier": {"metric": "elliott_wave_structural_integrity", "weight_delta": 0.20},
        },
        "DIVIDEND_YIELD_CAPITAL_TRAP": {
            "patterns": [r"\b(dividend\s*yield\s*trap|capital\s*erosion\s*trap|high\s*dividend\s*value\s*trap|unbacked\s*dividend|psu\s*dividend\s*trap)\b"],
            "name": "High Dividend Yield Capital Erosion Trap Guard",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "High optical dividend yields (>= 8-10%) unbacked by operating cash flows (CFO/PAT < 0.50) representing return of capital and terminal capital erosion rather than true yield.",
            "relevance": {"swing_3d": 0.0, "swing_10d": 0.05, "positional_30d": 0.30, "sip_compounder": 0.70, "turnaround": 0.40, "multibagger": 0.50},
            "modifier": {"metric": "dividend_quality_cfo_backing", "weight_delta": -0.25},
        },
        "WYCKOFF_SPRING_ABSORPTION": {
            "patterns": [r"\b(wyckoff\s*spring|terminal\s*shakeout|phase\s*c\s*spring|absorption\s*volume|effort\s*vs\s*result|composite\s*operator)\b"],
            "name": "Richard Wyckoff Spring & Absorption Tape Reading Mechanics",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Institutional terminal shakeout below trading range support quickly recovered on drying volume (Spring) or high volume with tight spread at resistance (Absorption).",
            "relevance": {"swing_3d": 0.40, "swing_10d": 0.60, "positional_30d": 0.70, "multibagger": 0.65, "sip_compounder": 0.0},
            "modifier": {"metric": "wyckoff_spring_absorption_integrity", "weight_delta": 0.20},
        },
        "NISON_CANDLESTICK_CONFLUENCE": {
            "patterns": [r"\b(steve\s*nison|candlestick\s*reversal|hammer\s*candle|bullish\s*engulfing|morning\s*star|shooting\s*star|bearish\s*engulfing)\b"],
            "name": "Steve Nison Japanese Candlestick Reversal Confluence",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "High-conviction Japanese candlestick reversal triggers (Hammer, Bullish Engulfing, Morning Star) aligning strictly with key support levels.",
            "relevance": {"swing_3d": 0.65, "swing_10d": 0.55, "positional_30d": 0.40, "multibagger": 0.25, "sip_compounder": 0.0},
            "modifier": {"metric": "candlestick_reversal_confluence", "weight_delta": 0.20},
        },
        "WEINSTEIN_MANSFIELD_RS": {
            "patterns": [r"\b(stan\s*weinstein|mansfield\s*relative\s*strength|mansfield\s*rs|stage\s*2\s*breakout|30\s*week\s*ma)\b"],
            "name": "Stan Weinstein 4-Stage & Mansfield Relative Strength System",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Strict Stage 2 breakout qualification requiring rising 30-week (150/200 DMA) with positive and expanding Mansfield Relative Strength against the benchmark.",
            "relevance": {"swing_3d": 0.25, "swing_10d": 0.50, "positional_30d": 0.75, "multibagger": 0.70, "sip_compounder": 0.15},
            "modifier": {"metric": "mansfield_rs_outperformance", "weight_delta": 0.22},
        },
        "LIVERMORE_PIVOT_EXHAUSTION_GUARD": {
            "patterns": [r"\b(jesse\s*livermore|pivotal\s*point|extended\s*pivot|false\s*breakout\s*trap|line\s*of\s*least\s*resistance|pyramiding\s*rule)\b"],
            "name": "Jesse Livermore Pivotal Point & False Breakout Exhaustion Guard",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Decisive pivotal point breakout tracking with hard guard against chasing extended moves (>15% above 20 EMA) or low-volume bull traps.",
            "relevance": {"swing_3d": 0.50, "swing_10d": 0.55, "positional_30d": 0.45, "multibagger": 0.35, "sip_compounder": 0.0},
            "modifier": {"metric": "pivotal_point_breakout_integrity", "weight_delta": 0.18},
        },
        "DARVAS_BOX_GEOMETRY": {
            "patterns": [r"\b(darvas\s*box|box\s*theory|ascending\s*consolidation\s*box|edwards\s*magee\s*rectangle|triangle\s*breakout)\b"],
            "name": "Nicolas Darvas Box Theory & Classical Geometric Consolidation",
            "category": "MARKET_MICROSTRUCTURE",
            "desc": "Deterministic bounding box tracking where breakout above upper box ceiling establishes a new floor; breach of box floor triggers stop.",
            "relevance": {"swing_3d": 0.35, "swing_10d": 0.50, "positional_30d": 0.65, "multibagger": 0.50, "sip_compounder": 0.0},
            "modifier": {"metric": "darvas_box_stability", "weight_delta": 0.15},
        },
        "PENMAN_RNOA_DECOMPOSITION": {
            "patterns": [r"\b(stephen\s*penman|reformulated\s*balance\s*sheet|rnoa|operating\s*assets|net\s*operating\s*assets|noa|net\s*financial\s*obligations|nfo|financial\s*leverage|flev|debt-?inflated\s*roe)\b"],
            "name": "Stephen Penman Reformulated Financial Statement & RNOA Decomposition",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "Rigorous separation of operating vs financing activities; deconstructs ROE = RNOA + FLEV * (RNOA - NBC) to flag low-quality debt-levered earnings vs true operating engine power.",
            "relevance": {"sip_compounder": 0.85, "multibagger": 0.70, "positional_30d": 0.35, "turnaround": 0.65, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "penman_operating_spread", "weight_delta": 0.25},
        },
        "CAPITAL_CYCLE_STARVATION": {
            "patterns": [r"\b(edward\s*chancellor|capital\s*cycle|capex\s*to\s*d&a|capex\s*starvation|supply\s*side\s*consolidation|asset\s*growth\s*anomaly|marathon\s*asset)\b"],
            "name": "Edward Chancellor Capital Cycle & Capex Starvation Detector",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "Tracks industry capital cycles where high capex/asset expansion destroys future returns, while capex starvation (Capex / D&A < 0.80) signals supply consolidation and future high margins.",
            "relevance": {"turnaround": 0.80, "multibagger": 0.75, "sip_compounder": 0.50, "positional_30d": 0.30, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "capital_cycle_inflection_score", "weight_delta": 0.22},
        },
        "MAUBOUSSIN_BASE_RATE_PLAUSIBILITY": {
            "patterns": [r"\b(michael\s*mauboussin|expectations\s*investing|base\s*rate|reverse\s*dcf|implied\s*growth\s*rate|competitive\s*advantage\s*period|cap)\b"],
            "name": "Michael Mauboussin Base Rate & Reverse-DCF Expectations Filter",
            "category": "VALUATION_BASE_RATE",
            "desc": "Unpacks market expectations through Reverse-DCF and cross-references implied 5Y revenue/NOPAT CAGR against empirical Indian base rates (only 2.8% of firms sustain >30% 5Y CAGR).",
            "relevance": {"sip_compounder": 0.80, "multibagger": 0.75, "positional_30d": 0.40, "turnaround": 0.45, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "base_rate_plausibility_penalty", "weight_delta": 0.20},
        },
        "THORNDIKE_INCREMENTAL_ROIC": {
            "patterns": [r"\b(william\s*thorndike|the\s*outsiders|incremental\s*roic|reinvestment\s*rate|capital\s*allocation\s*score|share\s*buyback\s*accretion|m&a\s*discipline)\b"],
            "name": "William Thorndike Outsiders Capital Allocation & Incremental ROIC Scorer",
            "category": "CORPORATE_GOVERNANCE",
            "desc": "Measures management skill in redeploying retained earnings: Incremental ROIC (Delta NOPAT / Cumulative Reinvestment) combined with buyback opportunism and debt prudence.",
            "relevance": {"sip_compounder": 0.90, "multibagger": 0.80, "positional_30d": 0.25, "turnaround": 0.50, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "incremental_roic_capital_allocation", "weight_delta": 0.24},
        },
        "DAMODARAN_LIFE_CYCLE": {
            "patterns": [r"\b(aswath\s*damodaran|corporate\s*life\s*cycle|narrative\s*and\s*numbers|cost\s*of\s*capital|wacc|terminal\s*value\s*decay|failure\s*risk)\b"],
            "name": "Aswath Damodaran Corporate Life Cycle & Valuation Framework",
            "category": "VALUATION_BASE_RATE",
            "desc": "Maps company across Life Cycle stages (Startup, High Growth, Mature Growth, Mature Stable, Decline) to dynamically scale reinvestment rates, operating margins, and cost of capital.",
            "relevance": {"sip_compounder": 0.75, "multibagger": 0.75, "positional_30d": 0.35, "turnaround": 0.70, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "life_cycle_valuation_alignment", "weight_delta": 0.20},
        },
        "GREENWALD_EARNINGS_POWER_VALUE": {
            "patterns": [r"\b(bruce\s*greenwald|earnings\s*power\s*value|epv|asset\s*reproduction\s*cost|franchise\s*value|competition\s*demystified)\b"],
            "name": "Bruce Greenwald Earnings Power Value & Franchise Moat Deconstruction",
            "category": "VALUATION_BASE_RATE",
            "desc": "Deconstructs valuation into Asset Reproduction Cost (AV), Zero-Growth Earnings Power Value (EPV), and Franchise Value Moat multiple.",
            "relevance": {"sip_compounder": 0.85, "multibagger": 0.80, "positional_30d": 0.30, "turnaround": 0.40, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "epv_franchise_moat_multiple", "weight_delta": 0.25},
        },
        "SCHILIT_FORENSIC_SHENANIGANS": {
            "patterns": [r"\b(howard\s*schilit|financial\s*shenanigans|cwip\s*capitalization|premature\s*revenue|channel\s*stuffing|other\s*income\s*boost)\b"],
            "name": "Howard Schilit 7 Financial Shenanigans & Accounting Quality Guard",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "Forensic algorithms detecting routine opex parked in CWIP, unbilled revenue / DSO divergence, and other income profit masking.",
            "relevance": {"sip_compounder": 0.85, "multibagger": 0.80, "positional_30d": 0.40, "turnaround": 0.70, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "schilit_forensic_hygiene_score", "weight_delta": 0.25},
        },
        "MARKS_CREDIT_CYCLE_PENDULUM": {
            "patterns": [r"\b(howard\s*marks|credit\s*cycle|market\s*pendulum|risk\s*posture|tight\s*credit\s*spread|distressed\s*opportunity)\b"],
            "name": "Howard Marks Market & Credit Cycle Pendulum Scorer",
            "category": "GEOPOLITICAL_CORRIDOR",
            "desc": "Macro sentiment and credit availability positioning: oscillates between defensive risk control (euphoria/tight spreads) and aggressive capital deployment (distress).",
            "relevance": {"sip_compounder": 0.70, "multibagger": 0.65, "positional_30d": 0.50, "turnaround": 0.75, "swing_3d": 0.10, "swing_10d": 0.20},
            "modifier": {"metric": "marks_credit_cycle_posture", "weight_delta": 0.20},
        },
        "MCKINSEY_ECONOMIC_PROFIT": {
            "patterns": [r"\b(mckinsey\s*valuation|tim\s*koller|economic\s*profit|invested\s*capital|blume\s*adjusted\s*beta|roic\s*wacc\s*spread)\b"],
            "name": "McKinsey Tim Koller Economic Profit & Invested Capital Model",
            "category": "ACCOUNTING_INFLECTION",
            "desc": "Calculates real economic value creation: Invested Capital * (ROIC - WACC), with Blume mean-reverting Beta calibration.",
            "relevance": {"sip_compounder": 0.85, "multibagger": 0.75, "positional_30d": 0.25, "turnaround": 0.40, "swing_3d": 0.0, "swing_10d": 0.0},
            "modifier": {"metric": "economic_profit_creation_spread", "weight_delta": 0.22},
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

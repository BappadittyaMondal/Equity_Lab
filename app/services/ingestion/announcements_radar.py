"""BSE/NSE Regulation 30 Corporate Announcements & Material Event Radar.

Ingests, filters, and classifies high-impact exchange disclosures mandated under
SEBI (Listing Obligations and Disclosure Requirements) Regulations, 2015:
1. Mega Order Wins & Contract Awards
2. Mergers, Acquisitions, Takeovers & Amalgamations
3. Capital Actions: Preferential Warrants, QIP Dilution, Rights Issues
4. Legal & Regulatory Distress: NCLT Insolvency, SEBI Orders, Auditor Resignations
5. Credit Rating Actions: CRISIL/ICRA/CARE Upgrades & Downgrades
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research_data import ResearchDataStore

logger = logging.getLogger(__name__)

# Keyword classifiers for SEBI LODR Regulation 30 disclosures
ANNOUNCEMENT_CLASSIFIERS = {
    "MEGA_ORDER_WIN": [
        "bagged order", "award of contract", "order win", "letter of award", "loa",
        "contract worth", "supply order", "commercial order", "purchase order"
    ],
    "MERGER_ACQUISITION": [
        "scheme of arrangement", "amalgamation", "merger", "acquisition of",
        "takeover", "share purchase agreement", "joint venture agreement", "demerger"
    ],
    "PREFERENTIAL_WARRANTS": [
        "preferential issue", "convertible warrants", "allotment of equity shares",
        "qualified institutional placement", "qip", "rights issue"
    ],
    "REGULATORY_LEGAL_DISTRESS": [
        "nclt", "insolvency", "creditor petition", "sebi order", "show cause notice",
        "cbi investigation", "ed raid", "search and seizure", "auditor resignation"
    ],
    "CREDIT_RATING_ACTION": [
        "credit rating", "crisil", "icra", "care ratings", "rating upgraded",
        "rating downgraded", "outlook revised"
    ]
}


class CorporateAnnouncementsRadar:
    """Real-time Regulation 30 Corporate Disclosures Radar for Indian Equities."""

    @classmethod
    def classify_announcement_text(cls, headline: str, details: str = "") -> Dict[str, Any]:
        """Classifies corporate announcement into a material event category."""
        text = f"{headline} {details}".lower()
        matched_categories = []

        for category, patterns in ANNOUNCEMENT_CLASSIFIERS.items():
            if any(p in text for p in patterns):
                matched_categories.append(category)

        primary_cat = matched_categories[0] if matched_categories else "GENERAL_CORPORATE_ANNOUNCEMENT"

        # Extract order value if present (e.g. ₹500 Cr, 1,200 Crore)
        order_val_cr = None
        order_match = re.search(r'(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:cr|crore|crores)', text)
        if order_match:
            try:
                order_val_cr = float(order_match.group(1).replace(",", ""))
            except ValueError:
                pass

        return {
            "primary_category": primary_cat,
            "all_categories": matched_categories,
            "is_material_event": bool(matched_categories),
            "extracted_value_cr": order_val_cr
        }

    @classmethod
    def get_company_instant_announcements(
        cls,
        symbol: str,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """Retrieves and classifies recent exchange announcements for a symbol."""
        norm = normalize_symbol(symbol)
        clean_sym = norm.replace(".NS", "").replace(".BO", "").upper()

        announcements: List[Dict[str, Any]] = []
        try:
            store = ResearchDataStore()
            _, _, events, _, _, _ = store.get_timeline(norm)
            for ev in events:
                cls_info = cls.classify_announcement_text(ev.headline, getattr(ev, "content", "") or "")
                announcements.append({
                    "event_id": getattr(ev, "event_id", None),
                    "headline": ev.headline,
                    "date": str(getattr(ev, "timestamp", getattr(ev, "period_end", ""))),
                    "category": cls_info["primary_category"],
                    "is_material": cls_info["is_material_event"],
                    "order_value_cr": cls_info["extracted_value_cr"]
                })
        except Exception as e:
            logger.warning("Failed to fetch events from ResearchDataStore for %s: %s", norm, e)

        # Separate material catalysts
        order_wins = [a for a in announcements if a["category"] == "MEGA_ORDER_WIN"]
        mergers = [a for a in announcements if a["category"] == "MERGER_ACQUISITION"]
        warrants = [a for a in announcements if a["category"] == "PREFERENTIAL_WARRANTS"]
        distress = [a for a in announcements if a["category"] == "REGULATORY_LEGAL_DISTRESS"]
        ratings = [a for a in announcements if a["category"] == "CREDIT_RATING_ACTION"]

        # Derive catalyst inputs for E13 hydration
        catalyst_inputs = {
            "pli_scheme_eligibility": None,
            "tariff_customs_protection": "NEUTRAL",
            "buyback_pricing_vs_intrinsic": "NONE",
            "credit_rating_trend": "UPGRADED" if any("upgrade" in a["headline"].lower() for a in ratings) else ("DOWNGRADED" if any("downgrade" in a["headline"].lower() for a in ratings) else "STABLE"),
            "has_mega_orders": bool(order_wins),
            "has_merger_acquisition": bool(mergers),
            "has_warrant_dilution": bool(warrants),
            "has_legal_distress": bool(distress)
        }

        return {
            "symbol": clean_sym,
            "total_announcements_count": len(announcements),
            "material_catalysts": {
                "order_wins_count": len(order_wins),
                "mergers_acquisitions_count": len(mergers),
                "warrant_issues_count": len(warrants),
                "legal_distress_alerts_count": len(distress),
                "rating_actions_count": len(ratings)
            },
            "recent_announcements": announcements[-10:],
            "derived_catalyst_inputs": catalyst_inputs,
            "timestamp": get_ist_now_str(),
            "meta": create_meta_header(source=f"BSE/NSE Regulation 30 Radar ({clean_sym})")
        }

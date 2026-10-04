"""Phase 153: Daily News Intelligence Engine — T6 & T7.

Fetches market-moving headlines from free RSS/API sources, classifies
sector/ticker impact, scores direction and magnitude, and generates
a daily digest + portfolio alert overlay.

Sources: Moneycontrol RSS, ET Markets RSS, BSE Announcements (all free, no API key).
This is for equity RESEARCH — 1-3 hour delay is acceptable per project spec.

Zero conflict: entirely new module. No existing engine modification.
"""

import json
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# RSS Source Registry
# ─────────────────────────────────────────────────────────────────────────────

RSS_SOURCES = [
    {
        "name": "Moneycontrol_Markets",
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "category": "MARKET",
    },
    {
        "name": "Moneycontrol_Business",
        "url": "https://www.moneycontrol.com/rss/business.xml",
        "category": "BUSINESS",
    },
    {
        "name": "ET_Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "category": "MARKET",
    },
    {
        "name": "ET_Industry",
        "url": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
        "category": "INDUSTRY",
    },
    {
        "name": "LiveMint_Markets",
        "url": "https://www.livemint.com/rss/markets",
        "category": "MARKET",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Sector/Ticker Keyword Ontology
# ─────────────────────────────────────────────────────────────────────────────

SECTOR_KEYWORDS = {
    "POWER_ENERGY": [
        "power", "electricity", "transformer", "grid", "solar", "wind", "renewable",
        "thermal", "coal", "gas", "energy", "discom", "transmission", "substation",
        "NTPC", "Power Grid", "Adani Power", "Tata Power", "NHPC",
    ],
    "IT_TECH": [
        "IT", "software", "SaaS", "cloud", "AI", "artificial intelligence",
        "semiconductor", "chip", "data center", "cybersecurity", "digital",
        "TCS", "Infosys", "Wipro", "HCL Tech", "Tech Mahindra",
    ],
    "BANKING_FINANCE": [
        "bank", "NBFC", "RBI", "interest rate", "repo", "credit", "NPA",
        "insurance", "mutual fund", "SEBI", "stock exchange", "demat",
        "HDFC", "ICICI", "SBI", "Kotak", "Axis",
    ],
    "PHARMA_HEALTHCARE": [
        "pharma", "drug", "FDA", "USFDA", "hospital", "healthcare", "medical",
        "biotech", "vaccine", "clinical trial", "API", "formulation",
        "Sun Pharma", "Dr Reddy", "Cipla", "Lupin", "Divi's",
    ],
    "AUTO": [
        "auto", "automobile", "EV", "electric vehicle", "car", "two-wheeler",
        "Maruti", "Tata Motors", "M&M", "Bajaj Auto", "Hero Moto",
    ],
    "INFRA_REALTY": [
        "infrastructure", "real estate", "highway", "railway", "metro", "airport",
        "construction", "cement", "steel", "Vande Bharat", "bullet train",
        "L&T", "Adani Ports", "DLF", "Godrej Properties",
    ],
    "CHEMICALS_MATERIALS": [
        "chemical", "specialty chemical", "agrochemical", "fertilizer", "polymer",
        "rubber", "textile", "gelatin", "collagen", "API",
    ],
    "DEFENCE": [
        "defence", "defense", "military", "missile", "naval", "HAL",
        "BEL", "BDL", "DRDO", "ammunition", "radar",
    ],
    "TELECOM": [
        "telecom", "5G", "spectrum", "TRAI", "Jio", "Airtel", "Vodafone",
        "tower", "fiber", "broadband",
    ],
    "MACRO_POLICY": [
        "GDP", "inflation", "fiscal", "budget", "GST", "tariff", "FDI",
        "forex", "rupee", "dollar", "crude oil", "Brent", "WTI",
        "geopolitical", "sanctions", "trade war", "election",
    ],
}

IMPACT_KEYWORDS = {
    "POSITIVE": [
        "bags", "wins", "awarded", "upgrade", "launch", "expansion",
        "growth", "record", "profit", "beat", "surge", "rally",
        "approval", "clearance", "partnership", "acquisition", "deal",
        "IPO", "listing", "dividend", "buyback", "strong",
    ],
    "NEGATIVE": [
        "loss", "decline", "fall", "crash", "downgrade", "recall",
        "penalty", "fine", "fraud", "scam", "debt", "default",
        "bankruptcy", "layoff", "investigation", "ban", "restrict",
        "weak", "miss", "warning", "concern",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# T6: News Ingestion & Impact Mapper
# ─────────────────────────────────────────────────────────────────────────────

def fetch_rss_headlines(source: Dict[str, str], timeout: int = 15) -> List[Dict[str, str]]:
    """Fetch headlines from a single RSS source.

    Returns list of dicts: [{title, link, published, source_name, category}]
    """
    headlines = []
    try:
        req = Request(source["url"], headers={"User-Agent": "EquityLab/0.1 Research Bot"})
        with urlopen(req, timeout=timeout) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        # Handle both RSS 2.0 (<channel><item>) and Atom (<entry>) formats
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items[:20]:  # Cap at 20 per source to avoid token waste
            title_el = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
            link_el = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
            pub_el = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}published")

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            if not title:
                continue

            link = ""
            if link_el is not None:
                link = link_el.text or link_el.get("href", "") or ""

            published = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

            headlines.append({
                "title": title,
                "link": link.strip(),
                "published": published,
                "source_name": source["name"],
                "category": source["category"],
            })

    except (URLError, ET.ParseError, Exception) as e:
        logger.warning(f"Failed to fetch RSS from {source['name']}: {e}")

    return headlines


def classify_headline(title: str) -> Dict[str, Any]:
    """Classify a headline by sector, impact direction, and magnitude.

    Uses keyword ontology matching. No external API call needed.
    """
    title_lower = title.lower()

    # Sector classification
    matched_sectors = []
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                matched_sectors.append(sector)
                break

    if not matched_sectors:
        matched_sectors = ["GENERAL"]

    # Impact direction
    pos_count = sum(1 for kw in IMPACT_KEYWORDS["POSITIVE"] if kw.lower() in title_lower)
    neg_count = sum(1 for kw in IMPACT_KEYWORDS["NEGATIVE"] if kw.lower() in title_lower)

    if pos_count > neg_count:
        direction = "POSITIVE"
    elif neg_count > pos_count:
        direction = "NEGATIVE"
    else:
        direction = "NEUTRAL"

    # Magnitude (based on keyword density)
    total_impact = pos_count + neg_count
    if total_impact >= 3:
        magnitude = "HIGH"
    elif total_impact >= 1:
        magnitude = "MEDIUM"
    else:
        magnitude = "LOW"

    return {
        "sectors": matched_sectors,
        "direction": direction,
        "magnitude": magnitude,
    }


def generate_daily_digest(max_per_source: int = 15) -> Dict[str, Any]:
    """Fetch from all RSS sources, classify, and assemble daily digest.

    Returns a structured digest dict ready for JSON serialization.
    """
    all_headlines = []
    for source in RSS_SOURCES:
        headlines = fetch_rss_headlines(source)
        all_headlines.extend(headlines[:max_per_source])

    classified = []
    for h in all_headlines:
        classification = classify_headline(h["title"])
        classified.append({
            **h,
            **classification,
        })

    # Sort by magnitude (HIGH first) then direction (NEGATIVE first for risk alerting)
    mag_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    dir_order = {"NEGATIVE": 0, "POSITIVE": 1, "NEUTRAL": 2}
    classified.sort(key=lambda x: (mag_order.get(x["magnitude"], 3), dir_order.get(x["direction"], 3)))

    digest = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_headlines": len(classified),
        "sources_checked": len(RSS_SOURCES),
        "headlines": classified[:30],  # Top 30 most impactful
        "sector_summary": _compute_sector_summary(classified),
    }

    # Persist to disk
    _save_digest(digest)

    return digest


def _compute_sector_summary(classified: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Count headlines per sector by direction."""
    summary = {}
    for h in classified:
        for sector in h.get("sectors", ["GENERAL"]):
            if sector not in summary:
                summary[sector] = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "total": 0}
            summary[sector][h.get("direction", "NEUTRAL")] += 1
            summary[sector]["total"] += 1
    return summary


def _save_digest(digest: Dict[str, Any]) -> Path:
    """Save digest to data/news_digests/YYYY-MM-DD.json."""
    digest_dir = Path("data/news_digests")
    digest_dir.mkdir(parents=True, exist_ok=True)
    filepath = digest_dir / f"{digest['date']}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
    logger.info(f"Daily digest saved: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# T7: Portfolio Alert Overlay
# ─────────────────────────────────────────────────────────────────────────────

# Ticker → sector mapping for the user's watchlist
WATCHLIST_TICKER_SECTORS = {
    "JSLL": ["PHARMA_HEALTHCARE"],
    "DYCL": ["POWER_ENERGY"],
    "FRONTSP": ["INFRA_REALTY", "DEFENCE"],
    "NITTAGELA": ["PHARMA_HEALTHCARE", "CHEMICALS_MATERIALS"],
    "MAYURUNIQ": ["AUTO", "CHEMICALS_MATERIALS"],
}

# Direct ticker mention keywords
TICKER_KEYWORDS = {
    "JSLL": ["jeena sikho", "jsll", "jeena", "panchkarma", "ayurveda hospital"],
    "DYCL": ["dynamic cables", "dycl", "dynamic cable"],
    "FRONTSP": ["frontier springs", "frontsp", "vande bharat spring"],
    "NITTAGELA": ["nitta gelatin", "nittagela", "nitta", "gelatin india"],
    "MAYURUNIQ": ["mayur uniquoters", "mayuruniq", "mayur", "synthetic leather"],
}


def generate_portfolio_alerts(
    digest: Optional[Dict[str, Any]] = None,
    watchlist: Optional[Dict[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """Cross-reference daily digest against watchlist tickers.

    Returns list of alerts: [{ticker, headline, impact, magnitude, match_type}]
    """
    if digest is None:
        digest = generate_daily_digest()

    if watchlist is None:
        watchlist = WATCHLIST_TICKER_SECTORS

    ticker_kw = TICKER_KEYWORDS

    alerts = []
    for headline in digest.get("headlines", []):
        title_lower = headline.get("title", "").lower()
        headline_sectors = set(headline.get("sectors", []))

        for ticker, sectors in watchlist.items():
            match_type = None

            # Direct ticker mention (strongest signal)
            for kw in ticker_kw.get(ticker, []):
                if kw.lower() in title_lower:
                    match_type = "DIRECT_MENTION"
                    break

            # Sector overlap (weaker signal)
            if match_type is None and headline_sectors.intersection(set(sectors)):
                if headline.get("magnitude") in ["HIGH", "MEDIUM"]:
                    match_type = "SECTOR_OVERLAP"

            if match_type:
                alerts.append({
                    "ticker": ticker,
                    "headline": headline.get("title", ""),
                    "link": headline.get("link", ""),
                    "direction": headline.get("direction", "NEUTRAL"),
                    "magnitude": headline.get("magnitude", "LOW"),
                    "match_type": match_type,
                    "matched_sectors": list(headline_sectors.intersection(set(sectors))) or list(headline_sectors),
                    "source": headline.get("source_name", ""),
                })

    # Sort: DIRECT_MENTION first, then HIGH magnitude
    match_order = {"DIRECT_MENTION": 0, "SECTOR_OVERLAP": 1}
    mag_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    alerts.sort(key=lambda x: (match_order.get(x["match_type"], 2), mag_order.get(x["magnitude"], 3)))

    return alerts

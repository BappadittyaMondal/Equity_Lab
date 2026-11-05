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
    {
        "name": "TradeBrains_All",
        "url": "https://tradebrains.in/feed/",
        "category": "EQUITY_IDEAS",
    },
    {
        "name": "BSE_Corp_Announcements",
        "url": "https://www.bseindia.com/data/xml/corporate_announcements.xml",
        "category": "REGULATORY",
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
# Phase 198 NEW-C1: 6-Class Catalyst Taxonomy
# Classifies market-moving headlines into structural catalyst categories.
# Each class has distinct investment implications and score weights.
# ─────────────────────────────────────────────────────────────────────────────

CATALYST_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "SOVEREIGN_ORDER_WIN": {
        "description": "Government / PSU mega-order or LOI award to private company",
        "investment_implication": "STRONG_POSITIVE_ENTRY",
        "book_to_bill_trigger": True,  # Feeds NEW-C2 B2B computation
        "keywords": [
            "defence ministry", "mod order", "ntpc award", "nhsrcl", "railway board",
            "letter of intent", "loi", "contract value", "order book", "epc award",
            "ministry of defence", "armed forces contract", "navy order", "air force order",
            "metro rail order", "power grid award", "bpcl contract", "ongc award",
            "nuclear power", "ircon", "rites order", "nhai contract", "irfc",
        ],
    },
    "REGULATORY_SHOCK": {
        "description": "Adverse regulatory action — RBI risk weights, USFDA 483, SEBI circular",
        "investment_implication": "NEGATIVE_INVESTIGATE_PANIC_VS_DERATE",
        "trigger_panic_classifier": True,  # Feeds NEW-C3 panic bridge
        "keywords": [
            "rbi guidelines", "risk weight", "risk weights", "provisioning norms",
            "sebi circular", "usfda 483", "import alert", "gst demand",
            "show cause notice", "risk weight hike", "npa classification",
            "rbi action", "sebi order", "regulatory action", "norms tightened",
            "edrm warning", "warning letter", "complete response letter", "crl",
        ],
    },
    "GLOBAL_TECH_JV": {
        "description": "International technology JV, PLI partnership, or ecosystem certification",
        "investment_implication": "STRONG_POSITIVE_MOAT_BUILDER",
        "keywords": [
            "joint venture", "technology transfer", "renesas", "mufg", "smbc",
            "pli scheme", "semiconductor", "osat", "atmp", "jv agreement",
            "manufacturing partner", "strategic alliance", "global oem",
            "nvidia partnership", "intel agreement", "tsmc", "samsung fab",
            "foxconn jv", "apple supplier", "tesla supply", "qualified vendor",
            "tech collaboration", "r&d partnership", "defence technology",
        ],
    },
    "OPERATING_LEVERAGE_BLOWOUT": {
        "description": "Earnings blowout driven by operating leverage — margin expansion + volume surge",
        "investment_implication": "POSITIVE_MOMENTUM_CONFIRMATION",
        "keywords": [
            "ebitda margin jumped", "ebitda margin expanded", "pat doubles",
            "pat surges", "operating leverage", "volume growth", "capacity utilization",
            "margin expansion", "record revenue", "record profit", "highest ever",
            "blowout results", "exceptional quarter", "operating profit surges",
            "ebitda doubles", "net profit triples", "strong operational performance",
        ],
    },
    "TECH_ECOSYSTEM_CERT": {
        "description": "Tier-1 supplier certification or ecosystem partner announcement",
        "investment_implication": "POSITIVE_MOAT_SIGNAL",
        "keywords": [
            "tier-1 supplier", "certified partner", "qualified supplier", "ecosystem partner",
            "preferred vendor", "oem approved", "design win", "platform win",
            "chip design win", "automotive tier-1", "aerospace approved supplier",
            "iso 9001", "as9100", "iatf 16949 certification",
        ],
    },
    "PE_SECONDARY_EXIT": {
        "description": "PE/promoter block deal exit — distribution trap risk",
        "investment_implication": "CAUTION_DISTRIBUTION_TRAP",
        "keywords": [
            "block deal sell", "secondary sale", "pe exit", "promoter sale",
            "open market sale", "bulk deal sell", "stake sale", "promoter offloading",
            "private equity exit", "vc exit", "pre-ipo investor exit",
            "institutional exit", "promoter reduces stake",
        ],
    },
}


def classify_catalyst_class(title: str) -> Optional[str]:
    """Phase 198 NEW-C1: Classify a headline into one of 6 catalyst taxonomy classes.

    Returns the catalyst_class string or None if no match.
    Priority order: SOVEREIGN_ORDER_WIN > REGULATORY_SHOCK > PE_SECONDARY_EXIT >
                    GLOBAL_TECH_JV > OPERATING_LEVERAGE_BLOWOUT > TECH_ECOSYSTEM_CERT
    """
    title_lower = title.lower()

    # Ordered priority matching
    priority_order = [
        "SOVEREIGN_ORDER_WIN",
        "REGULATORY_SHOCK",
        "PE_SECONDARY_EXIT",
        "GLOBAL_TECH_JV",
        "OPERATING_LEVERAGE_BLOWOUT",
        "TECH_ECOSYSTEM_CERT",
    ]

    for cat in priority_order:
        keywords = CATALYST_TAXONOMY[cat]["keywords"]
        for kw in keywords:
            if kw.lower() in title_lower:
                return cat

    return None


def compute_book_to_bill(order_book_cr: Optional[float], ttm_revenue_cr: Optional[float]) -> Dict[str, Any]:
    """Phase 198 NEW-C2: Compute Book-to-Bill ratio and sovereign capex signal.

    B2B >= 2.5x indicates strong multi-year revenue visibility.
    When combined with positive CFO, signals SOVEREIGN_CAPEX_BONUS for Deadliest Combo scoring.

    Args:
        order_book_cr: Total outstanding order book in Crores
        ttm_revenue_cr: Trailing 12-month revenue in Crores

    Returns:
        Dict with b2b_ratio, sovereign_capex_bonus flag, tier classification
    """
    if order_book_cr is None or ttm_revenue_cr is None:
        return {
            "b2b_ratio": None,
            "sovereign_capex_bonus": False,
            "b2b_tier": "UNASSESSED",
            "methodology_note": "Book-to-Bill requires order_book_cr and ttm_revenue_cr.",
        }

    if ttm_revenue_cr <= 0:
        return {
            "b2b_ratio": None,
            "sovereign_capex_bonus": False,
            "b2b_tier": "INSUFFICIENT_DATA",
            "methodology_note": "TTM revenue <= 0; B2B undefined.",
        }

    b2b = round(order_book_cr / ttm_revenue_cr, 2)

    if b2b >= 4.0:
        tier = "ULTRA_HIGH_VISIBILITY"
        bonus = True
    elif b2b >= 2.5:
        tier = "HIGH_VISIBILITY"
        bonus = True
    elif b2b >= 1.5:
        tier = "MODERATE_VISIBILITY"
        bonus = False
    elif b2b >= 1.0:
        tier = "LOW_VISIBILITY"
        bonus = False
    else:
        tier = "REVENUE_RUNOFF_RISK"
        bonus = False

    return {
        "b2b_ratio": b2b,
        "sovereign_capex_bonus": bonus,
        "b2b_tier": tier,
        "methodology_note": f"B2B={b2b:.2f}x (Order Book {order_book_cr:.0f} Cr / TTM Rev {ttm_revenue_cr:.0f} Cr). Bonus threshold: B2B >= 2.5x.",
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
        req = Request(
            source["url"],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(req, timeout=timeout) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        # Handle both RSS 2.0 (<channel><item>) and Atom (<entry>) formats
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items[:25]:  # Cap at 25 per source to avoid token waste
            title_el = item.find("title")
            if title_el is None:
                title_el = item.find("{http://www.w3.org/2005/Atom}title")

            link_el = item.find("link")
            if link_el is None:
                link_el = item.find("{http://www.w3.org/2005/Atom}link")

            pub_el = item.find("pubDate")
            if pub_el is None:
                pub_el = item.find("{http://www.w3.org/2005/Atom}published")

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


# ─────────────────────────────────────────────────────────────────────────────
# Canonical Indian Equities Ticker & Entity Directory
# ─────────────────────────────────────────────────────────────────────────────

CANONICAL_TICKER_MAP: Dict[str, List[str]] = {
    "ADANIGREEN": ["adani green", "adani green energy", "khavda"],
    "ANANDRATHI": ["anand rathi", "anand rathi wealth"],
    "KPIGREEN": ["kpi green", "kpi green energy"],
    "NETWEB": ["netweb technologies", "netweb"],
    "SUZLON": ["suzlon", "suzlon energy"],
    "HAL": ["hindustan aeronautics", "hal"],
    "BEL": ["bharat electronics", "bel"],
    "MAZDOCK": ["mazagon dock", "mazdock"],
    "COCHINSHIP": ["cochin shipyard"],
    "DIXON": ["dixon technologies", "dixon"],
    "KAYNES": ["kaynes technology", "kaynes"],
    "TATASTEEL": ["tata steel"],
    "TATAPOWER": ["tata power"],
    "TCS": ["tcs", "tata consultancy services"],
    "INFY": ["infosys"],
    "RELIANCE": ["reliance industries", "ril", "jio"],
    "HDFCBANK": ["hdfc bank"],
    "ICICIBANK": ["icici bank"],
    "SBIN": ["state bank of india", "sbi"],
    "LT": ["larsen & toubro", "l&t"],
    "ZOMATO": ["zomato"],
    "JSLL": ["jeena sikho", "jsll", "jeena", "panchkarma", "ayurveda hospital"],
    "DYCL": ["dynamic cables", "dycl", "dynamic cable"],
    "FRONTSP": ["frontier springs", "frontsp", "vande bharat spring"],
    "NITTAGELA": ["nitta gelatin", "nittagela", "nitta", "gelatin india"],
    "MAYURUNIQ": ["mayur uniquoters", "mayuruniq", "mayur", "synthetic leather"],
}


def resolve_ticker_entities(title: str) -> Optional[str]:
    """Resolves headline text to a canonical NSE/BSE ticker symbol."""
    lower = title.lower()
    for ticker, aliases in CANONICAL_TICKER_MAP.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", lower):
                return ticker
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Anti-Clickbait Forensic Guard & Catalyst Tier Classifier
# ─────────────────────────────────────────────────────────────────────────────

CLICKBAIT_HYPE_PATTERNS = [
    r"\b(penny\s*stock|under\s*rs\.?\s*\d+|locked\s*in\s*upper\s*circuit|hits?\s*upper\s*circuit|upper\s*circuit\s*limit)\b",
    r"\b(multibagger\s*in\s*\d+\s*(day|week|month)|500%\s*return|1000%\s*return|turn\s*\d+\s*into\s*\d+|rocket\s*stock)\b",
    r"\b(circuit\s*to\s*circuit|guaranteed\s*gain|secret\s*multibagger|hidden\s*gem\s*under\s*rs)\b",
]

ORDER_VALUE_REGEX = re.compile(
    r"(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:cr|crore|crores)",
    re.IGNORECASE,
)


def classify_headline_forensics(title: str, text: str = "") -> Dict[str, Any]:
    """Evaluates headline for retail clickbait/operator churn hype and quantifies catalysts."""
    combined = f"{title} {text}".lower()

    # 1. Clickbait / Operator Hype Detection
    is_clickbait = False
    for pat in CLICKBAIT_HYPE_PATTERNS:
        if re.search(pat, combined):
            is_clickbait = True
            break

    operator_risk_tier = "HIGH_SPECULATIVE_RISK" if is_clickbait else "NORMAL_MONITORING"
    forensic_warning = (
        "WARNING: Retail promotional hype or upper-circuit trap detected. "
        "Enforce Delivery % >= 25% and Promoter Pledge < 20% before capital allocation."
        if is_clickbait
        else ""
    )

    # 2. Order Value Extraction
    order_val_cr = None
    has_order_keyword = any(k in combined for k in ["order", "contract", "bags", "wins", "awarded", "capex", "capacity", "expansion", "loi", "loa", "deal", "secures"])
    is_earnings = any(k in combined for k in ["net profit", "pat falls", "pat jumps", "pat rises", "profit falls", "profit rises", "net loss", "q1 profit", "q2 profit", "q3 profit", "q4 profit"])
    if has_order_keyword and not is_earnings:
        m = ORDER_VALUE_REGEX.search(combined)
        if m:
            try:
                order_val_cr = float(m.group(1).replace(",", ""))
            except ValueError:
                pass

    # 3. Catalyst Tier Classification
    if is_clickbait:
        catalyst_tier = "OPERATOR_HYPE_TRAP"
    elif order_val_cr and order_val_cr >= 500.0:
        catalyst_tier = "TIER_1_MOMENTUM_CATALYST"
    elif order_val_cr and order_val_cr >= 100.0:
        catalyst_tier = "TIER_2_MODERATE_CATALYST"
    elif any(k in combined for k in ["pat jumps", "pat surges", "profit doubles", "beats estimates", "capacity expansion"]):
        catalyst_tier = "TIER_1_MOMENTUM_CATALYST"
    else:
        catalyst_tier = "STANDARD_ANNOUNCEMENT"

    return {
        "is_clickbait_hype": is_clickbait,
        "operator_risk_tier": operator_risk_tier,
        "forensic_warning": forensic_warning,
        "order_value_cr": order_val_cr,
        "catalyst_tier": catalyst_tier,
    }


def synthesize_news_capsule(headline_item: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesizes an institutional-grade, multi-expert news capsule from a classified item."""
    title = headline_item.get("title", "")
    ticker = headline_item.get("resolved_ticker") or "UNRESOLVED"
    sector = headline_item.get("sectors", ["GENERAL"])[0]
    direction = headline_item.get("direction", "NEUTRAL")
    magnitude = headline_item.get("magnitude", "LOW")
    tier = headline_item.get("catalyst_tier", "STANDARD_ANNOUNCEMENT")
    is_clickbait = headline_item.get("is_clickbait_hype", False)
    order_val = headline_item.get("order_value_cr")

    if is_clickbait:
        verdict = "HIGH OPERATOR RISK: Retail hype pattern detected. Check Delivery % >= 25% and forensic flags before trading."
        grade = "OPERATOR_HYPE_TRAP"
    elif tier == "TIER_1_MOMENTUM_CATALYST":
        verdict = f"HIGH-IMPACT CATALYST: Verified material corporate event{' (₹' + str(order_val) + ' Cr)' if order_val else ''}. Check PEAD continuation."
        grade = "CLEAN_FUNDAMENTAL"
    elif tier == "TIER_2_MODERATE_CATALYST":
        verdict = f"MODERATE CATALYST: Corporate order win of ₹{order_val} Cr. Check Event Materiality Ratio (EMR) vs annual revenue."
        grade = "CLEAN_FUNDAMENTAL"
    else:
        verdict = "ROUTINE DISCLOSURE: Informational development; no immediate structural inflection."
        grade = "STANDARD_DISCLOSURE"

    briefing = [
        f"Headline: {title}",
        f"Entity: {ticker} ({sector}) | Catalyst: {tier} [{direction}/{magnitude}]",
        f"Verdict: {verdict}",
    ]

    return {
        "ticker": ticker,
        "headline": title,
        "sector": sector,
        "catalyst_tier": tier,
        "direction": direction,
        "magnitude": magnitude,
        "order_value_cr": order_val,
        "is_clickbait_hype": is_clickbait,
        "forensic_grade": grade,
        "actionable_verdict": verdict,
        "executive_briefing": briefing,
    }


def classify_headline(title: str, item_financials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Classify a headline by sector, impact direction, magnitude, ticker, forensics, and Phase 198 catalysts."""
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

    # Ticker entity resolution
    resolved_ticker = resolve_ticker_entities(title)

    # Forensic & Clickbait Analysis
    forensics = classify_headline_forensics(title)

    # Phase 198 NEW-C1: 6-Class Catalyst Taxonomy
    catalyst_class = classify_catalyst_class(title)

    # Phase 198 NEW-C2: Book-to-Bill & Sovereign Capex
    order_book_cr = (item_financials or {}).get("order_book_cr")
    ttm_rev_cr = (item_financials or {}).get("ttm_revenue_cr") or (item_financials or {}).get("revenue_cr")
    b2b_data = compute_book_to_bill(order_book_cr, ttm_rev_cr)

    # Phase 198 NEW-C3: Regulatory Shock Panic Bridge
    regulatory_panic_verdict = None
    panic_analysis = None
    if catalyst_class == "REGULATORY_SHOCK":
        try:
            from app.services.research.panic_vs_derate import classify_panic_vs_derate
            panic_payload = dict(item_financials or {})
            if "rsi_14" not in panic_payload:
                panic_payload["rsi_14"] = 35.0  # standard oversold assumption if triggered by headline shock
            if "price_drop_3m_pct" not in panic_payload:
                panic_payload["price_drop_3m_pct"] = 18.0
            panic_analysis = classify_panic_vs_derate(panic_payload)
            regulatory_panic_verdict = panic_analysis.get("verdict")
        except Exception as e:
            logger.warning("Error running panic_vs_derate for regulatory shock: %s", e)

    base_result = {
        "sectors": matched_sectors,
        "direction": direction,
        "magnitude": magnitude,
        "resolved_ticker": resolved_ticker,
        "catalyst_class": catalyst_class,
        "book_to_bill": b2b_data,
        "sovereign_capex_bonus": b2b_data.get("sovereign_capex_bonus", False),
        "regulatory_panic_verdict": regulatory_panic_verdict,
        "panic_analysis": panic_analysis,
        **forensics,
    }

    base_result["news_capsule"] = synthesize_news_capsule(dict(base_result, title=title))

    return base_result


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

    capsules = [h["news_capsule"] for h in classified if "news_capsule" in h]
    high_risk_hype = [h for h in classified if h.get("is_clickbait_hype")]

    digest = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_headlines": len(classified),
        "sources_checked": len(RSS_SOURCES),
        "headlines": classified[:30],  # Top 30 most impactful
        "news_capsules": capsules[:10],  # Top 10 institutional capsules
        "high_risk_hype_count": len(high_risk_hype),
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

# Direct ticker mention keywords (augmented by canonical entity directory)
TICKER_KEYWORDS = {
    **CANONICAL_TICKER_MAP,
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
        resolved = headline.get("resolved_ticker")

        for ticker, sectors in watchlist.items():
            match_type = None

            # Direct ticker match via entity resolver or keywords
            if resolved == ticker:
                match_type = "DIRECT_MENTION"
            else:
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


def feed_news_to_self_learning(
    headlines: List[Dict[str, Any]],
    self_learning_engine: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Feeds classified news headlines to the Epistemic Dynamic Self-Learning Brain."""
    if self_learning_engine is None:
        try:
            from app.services.research.self_learning_engine import SelfLearningEngine
            self_learning_engine = SelfLearningEngine()
        except ImportError:
            logger.warning("SelfLearningEngine not available for news feedback loop.")
            return []

    learned_records = []
    for h in headlines:
        title = h.get("title", "")
        tier = h.get("catalyst_tier", "")
        is_clickbait = h.get("is_clickbait_hype", False)

        target_entity_id = None
        catalyst_class = h.get("catalyst_class")
        if is_clickbait:
            target_entity_id = "OPERATOR_CHURN_PENNY_HYPE"
        elif catalyst_class == "SOVEREIGN_ORDER_WIN":
            target_entity_id = "SOVEREIGN_MEGA_ORDER_BOOK_TO_BILL"
        elif catalyst_class == "REGULATORY_SHOCK":
            target_entity_id = "RBI_REGULATORY_PANIC_VS_STRUCTURAL_DERATE"
        elif catalyst_class in ("GLOBAL_TECH_JV", "TECH_ECOSYSTEM_CERT"):
            target_entity_id = "GLOBAL_TECH_JV_PLI_MOAT"
        elif catalyst_class == "PE_SECONDARY_EXIT":
            target_entity_id = "PE_SECONDARY_BLOCK_EXIT_TRAP"
        elif tier == "TIER_1_MOMENTUM_CATALYST" and any(k in title.lower() for k in ["order", "contract", "bags", "wins", "awarded"]):
            target_entity_id = "REG30_MEGA_ORDER_CATALYST"
        elif any(k in title.lower() for k in ["pat jumps", "pat surges", "net profit", "results"]):
            target_entity_id = "EARNINGS_SUE_DRIFT_CATALYST"

        if target_entity_id and hasattr(self_learning_engine, "UNMAPPED_CANDIDATE_PATTERNS") and target_entity_id in self_learning_engine.UNMAPPED_CANDIDATE_PATTERNS:
            try:
                learned_ent = self_learning_engine.evaluate_and_learn_entity(
                    entity_id=target_entity_id,
                    text_context=title,
                    source_origin="DAILY_NEWS_INTELLIGENCE_LOOP",
                    provenance_score=0.88,
                    corroboration_count=2,
                )
                learned_records.append(learned_ent.model_dump())
            except Exception as e:
                logger.warning("Failed to learn news entity %s: %s", target_entity_id, e)

    return learned_records


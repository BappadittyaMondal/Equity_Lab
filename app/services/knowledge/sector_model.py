"""Sector Model — Sector-relative context and peer comparison.

Provides sector/industry classification for companies and computes
sector-relative valuation metrics. Used by fundamental and valuation
engines to determine whether a stock is cheap/expensive relative to peers.
"""

import logging
from typing import List, Optional

from app.models.schemas import SectorProfile
from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol

logger = logging.getLogger(__name__)

# Curated Indian equity sector classification
# Maps common sectors to standardized names
_SECTOR_NORMALIZATION = {
    "information technology": "Technology",
    "it": "Technology",
    "software": "Technology",
    "technology": "Technology",
    "financial services": "Financials",
    "banking": "Financials",
    "banks": "Financials",
    "nbfc": "Financials",
    "insurance": "Financials",
    "consumer goods": "Consumer",
    "fmcg": "Consumer",
    "consumer discretionary": "Consumer",
    "automobile": "Automobile",
    "auto": "Automobile",
    "auto components": "Automobile",
    "pharmaceutical": "Healthcare",
    "pharma": "Healthcare",
    "healthcare": "Healthcare",
    "chemicals": "Chemicals",
    "specialty chemicals": "Chemicals",
    "oil & gas": "Energy",
    "energy": "Energy",
    "power": "Energy",
    "metals": "Materials",
    "steel": "Materials",
    "mining": "Materials",
    "cement": "Materials",
    "construction": "Infrastructure",
    "infrastructure": "Infrastructure",
    "capital goods": "Infrastructure",
    "real estate": "Real Estate",
    "realty": "Real Estate",
    "telecom": "Telecom",
    "media": "Telecom",
    "textiles": "Textiles",
}

# Known peer groups for quick sector mapping
_PEER_GROUPS = {
    "Technology": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS", "COFORGE"],
    "Financials": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK", "BAJFINANCE", "BAJAJFINSV"],
    "Consumer": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO", "GODREJCP", "TATACONSUM"],
    "Energy": ["RELIANCE", "ONGC", "IOC", "BPCL", "GAIL", "ADANGREEN", "NTPC", "POWERGRID"],
    "Healthcare": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "BIOCON", "LUPIN"],
    "Automobile": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO"],
    "Materials": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "ULTRACEMCO", "SHREECEM", "AMBUJACEM"],
    "Infrastructure": ["LT", "ABB", "SIEMENS", "HAVELLS", "BEL", "HAL"],
}


class SectorModel:
    """Provides sector classification and peer comparison context."""

    def __init__(self):
        self._store = ResearchDataStore()

    def get_sector_profile(self, symbol: str) -> SectorProfile:
        """Build a SectorProfile for a given symbol.

        Looks up the company's sector from the research database,
        normalizes it, and identifies peer symbols.
        """
        norm_symbol = normalize_symbol(symbol).replace(".NS", "")

        # Try to get sector from database
        sector = None
        industry = None
        try:
            company = self._store.get_company(norm_symbol + ".NS")
            sector = company.sector
            industry = company.industry
        except Exception:
            pass

        # Normalize sector name
        normalized_sector = self._normalize_sector(sector)

        # Find peers
        peers = self._find_peers(norm_symbol, normalized_sector)

        return SectorProfile(
            sector=normalized_sector,
            industry=industry,
            peer_symbols=peers,
        )

    def _normalize_sector(self, raw_sector: Optional[str]) -> Optional[str]:
        """Normalize a sector string to a standard name."""
        if not raw_sector:
            return None
        key = raw_sector.strip().lower()
        return _SECTOR_NORMALIZATION.get(key, raw_sector.title())

    def _find_peers(self, symbol: str, sector: Optional[str]) -> List[str]:
        """Find peer symbols for a given sector."""
        if not sector:
            return []
        peers = _PEER_GROUPS.get(sector, [])
        # Exclude the symbol itself from peers
        return [p for p in peers if p.upper() != symbol.upper()][:7]

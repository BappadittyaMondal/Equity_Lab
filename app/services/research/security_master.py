# -*- coding: utf-8 -*-
"""Institutional Centralized Security Master.

Provides deterministic ticker resolution, alias mapping, ISIN/exchange cross-referencing,
and provider-specific symbol translation across NSE, BSE, and global data feeds.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SecurityRecord:
    canonical_symbol: str
    company_name: str
    exchange: str = "NSE"
    nse_symbol: Optional[str] = None
    bse_code: Optional[str] = None
    isin: Optional[str] = None
    yahoo_ticker: str = ""
    aliases: List[str] = field(default_factory=list)
    sector: Optional[str] = None
    market_cap_tier: Optional[str] = None

    def __post_init__(self):
        if not self.yahoo_ticker:
            if self.exchange == "BSE" and self.bse_code:
                self.yahoo_ticker = f"{self.bse_code}.BO"
            elif self.nse_symbol:
                self.yahoo_ticker = f"{self.nse_symbol}.NS"
            else:
                self.yahoo_ticker = f"{self.canonical_symbol}.NS"


class SecurityMaster:
    """Institutional Centralized Security Master and Alias Resolver."""

    _INDEX_MAP: Dict[str, str] = {
        "NIFTY": "^NSEI",
        "NIFTY 50": "^NSEI",
        "NIFTY50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK",
        "NIFTY BANK": "^NSEBANK",
        "FINNIFTY": "^NIFTY_FIN_SERVICE",
        "INDIA VIX": "^INDIAVIX",
        "INDIAVIX": "^INDIAVIX",
    }

    _REGISTRY: Dict[str, SecurityRecord] = {}
    _ALIAS_LOOKUP: Dict[str, str] = {}

    @classmethod
    def _clean_token(cls, token: str) -> str:
        """Strip exchange prefixes, whitespace, dots, and convert to uppercase."""
        t = token.upper().strip()
        # Strip exchange prefixes (e.g. NSE:, BSE:)
        if t.startswith("NSE:"):
            t = t[4:].strip()
        elif t.startswith("BSE:"):
            t = t[4:].strip()
        return t

    @classmethod
    def register_security(cls, record: SecurityRecord) -> None:
        """Register a security record and index all its aliases."""
        canon = record.canonical_symbol.upper().strip()
        cls._REGISTRY[canon] = record

        # Index canonical
        cls._ALIAS_LOOKUP[canon] = canon

        # Index NSE symbol
        if record.nse_symbol:
            nse_clean = record.nse_symbol.upper().strip()
            cls._ALIAS_LOOKUP[nse_clean] = canon
            cls._ALIAS_LOOKUP[f"{nse_clean}.NS"] = canon

        # Index BSE code
        if record.bse_code:
            bse_clean = record.bse_code.upper().strip()
            cls._ALIAS_LOOKUP[bse_clean] = canon
            cls._ALIAS_LOOKUP[f"{bse_clean}.BO"] = canon

        # Index ISIN
        if record.isin:
            cls._ALIAS_LOOKUP[record.isin.upper().strip()] = canon

        # Index Yahoo ticker
        if record.yahoo_ticker:
            cls._ALIAS_LOOKUP[record.yahoo_ticker.upper().strip()] = canon

        # Index custom aliases & company name
        for alias in record.aliases:
            cl_alias = cls._clean_token(alias)
            cls._ALIAS_LOOKUP[cl_alias] = canon
            # Also without spaces/dashes
            compact = re.sub(r"[^A-Z0-9]", "", cl_alias)
            if compact:
                cls._ALIAS_LOOKUP[compact] = canon

        # Index clean company name
        clean_name = re.sub(r"[^A-Z0-9]", "", record.company_name.upper())
        if clean_name:
            cls._ALIAS_LOOKUP[clean_name] = canon

    @classmethod
    def resolve_record(cls, query: str) -> Optional[SecurityRecord]:
        """Resolve a query string to a canonical SecurityRecord."""
        if not query:
            return None

        clean = cls._clean_token(query)

        # Direct index lookup
        if clean in cls._ALIAS_LOOKUP:
            return cls._REGISTRY.get(cls._ALIAS_LOOKUP[clean])

        # Try stripped of .NS / .BO
        stripped = re.sub(r"\.(NS|BO)$", "", clean)
        if stripped in cls._ALIAS_LOOKUP:
            return cls._REGISTRY.get(cls._ALIAS_LOOKUP[stripped])

        # Compact alphanumeric lookup
        compact = re.sub(r"[^A-Z0-9]", "", clean)
        if compact in cls._ALIAS_LOOKUP:
            return cls._REGISTRY.get(cls._ALIAS_LOOKUP[compact])

        return None

    @classmethod
    def resolve_symbol(cls, symbol: str) -> str:
        """Resolve any scrip alias/name into the canonical normalized ticker.

        Preserves 100% backward compatibility for indices (^NSEI) and unmapped tickers (.NS/.BO).
        """
        if not symbol:
            return ""

        clean = symbol.upper().strip()

        # Check indices first
        if clean in cls._INDEX_MAP:
            return cls._INDEX_MAP[clean]
        if clean.startswith("^"):
            return clean

        # Handle explicit exchange prefix or suffix
        exchange_override = None
        if clean.startswith("NSE:"):
            clean = clean[4:].strip()
            exchange_override = "NS"
        elif clean.startswith("BSE:"):
            clean = clean[4:].strip()
            exchange_override = "BO"
        elif clean.endswith(".BO"):
            exchange_override = "BO"
            clean = clean[:-3].strip()
        elif clean.endswith(".NS"):
            exchange_override = "NS"
            clean = clean[:-3].strip()

        # Check known registry
        rec = cls.resolve_record(clean)
        if rec:
            if exchange_override == "BO":
                if rec.bse_code and clean == rec.bse_code:
                    return f"{rec.bse_code}.BO"
                return f"{rec.canonical_symbol}.BO"
            elif exchange_override == "NS":
                if clean in (rec.canonical_symbol, rec.nse_symbol):
                    return f"{clean}.NS"
                return f"{rec.canonical_symbol}.NS"

            if clean in (rec.canonical_symbol, rec.nse_symbol):
                return f"{clean}.NS"
            return f"{rec.canonical_symbol}.NS"

        if exchange_override:
            return f"{clean}.{exchange_override}"

        return f"{clean}.NS"

    @classmethod
    def get_provider_ticker(cls, symbol: str, provider: str = "yfinance") -> str:
        """Get the specific ticker format required by a data provider."""
        rec = cls.resolve_record(symbol)
        prov = provider.lower()

        if prov in ("yfinance", "yahoodirect"):
            if rec and rec.yahoo_ticker:
                return rec.yahoo_ticker
            return cls.resolve_symbol(symbol)
        elif prov == "nse":
            if rec and rec.nse_symbol:
                return rec.nse_symbol
            clean = cls._clean_token(symbol)
            return re.sub(r"\.(NS|BO)$", "", clean)
        elif prov == "bse":
            if rec and rec.bse_code:
                return rec.bse_code
            clean = cls._clean_token(symbol)
            return re.sub(r"\.(NS|BO)$", "", clean)

        return cls.resolve_symbol(symbol)

    # ── Delisted Equities & Survivorship Bias Defense ─────────────────────

    _DELISTED_REGISTRY: Dict[str, Dict[str, Any]] = {
        "DHFL": {
            "symbol": "DHFL",
            "company_name": "Dewan Housing Finance Corporation Ltd",
            "delisted_date": "2021-06-14",
            "reason": "NCLT Resolution / Insolvency (Piramal acquisition with 100% equity wipeout)",
            "final_status": "LIQUIDATED_TOTAL_LOSS",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "NBFC / Housing Finance",
        },
        "RCOM": {
            "symbol": "RCOM",
            "company_name": "Reliance Communications Ltd",
            "delisted_date": "2021-07-16",
            "reason": "Insolvency / IBC Chapter under NCLT",
            "final_status": "LIQUIDATED_TOTAL_LOSS",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Telecom",
        },
        "SINTEX": {
            "symbol": "SINTEX",
            "company_name": "Sintex Industries Ltd",
            "delisted_date": "2023-03-27",
            "reason": "NCLT Resolution (Reliance-Acre acquisition, equity extinguished)",
            "final_status": "EQUITY_EXTINGUISHED",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Textiles",
        },
        "JETAIRWAYS": {
            "symbol": "JETAIRWAYS",
            "company_name": "Jet Airways (India) Ltd",
            "delisted_date": "2019-06-20",
            "reason": "Trading Suspension / NCLT Liquidation proceedings",
            "final_status": "SUSPENDED_NCLT",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Aviation",
        },
        "RELCAPITAL": {
            "symbol": "RELCAPITAL",
            "company_name": "Reliance Capital Ltd",
            "delisted_date": "2023-08-01",
            "reason": "NCLT resolution under RBI supervision (IndusInd acquisition)",
            "final_status": "EQUITY_EXTINGUISHED",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Financial Services",
        },
        "UNITECH": {
            "symbol": "UNITECH",
            "company_name": "Unitech Ltd",
            "delisted_date": "2020-01-20",
            "reason": "Regulatory takeover / Forensic fraud investigation",
            "final_status": "SUSPENDED_FRAUD",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Real Estate",
        },
        "GITANJALI": {
            "symbol": "GITANJALI",
            "company_name": "Gitanjali Gems Ltd",
            "delisted_date": "2018-07-02",
            "reason": "Compulsory Delisting / Banking Fraud",
            "final_status": "COMPULSORY_DELISTED_FRAUD",
            "terminal_equity_recovery_pct": 0.0,
            "sector": "Gems & Jewellery",
        },
    }

    @classmethod
    def is_security_delisted(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Checks if a given symbol is recorded in the delisted/insolvent equities registry."""
        clean = cls._clean_token(symbol)
        clean = re.sub(r"\.(NS|BO)$", "", clean)
        return cls._DELISTED_REGISTRY.get(clean)

    @classmethod
    def is_security_active_as_of(cls, symbol: str, as_of_date: str) -> bool:
        """Determines Point-in-Time viability: was this stock active on `as_of_date`?"""
        delisted_info = cls.is_security_delisted(symbol)
        if not delisted_info:
            return True
        delist_dt = delisted_info["delisted_date"]
        return as_of_date < delist_dt

    @classmethod
    def calculate_survivorship_bias_penalty(
        cls,
        backtest_years: float = 5.0,
        universe_tier: str = "ALL_CAP"
    ) -> Dict[str, Any]:
        """Calculates institutional survivorship bias alpha haircut for multi-year backtests."""
        rates = {
            "LARGE_CAP": 0.006,
            "MID_CAP": 0.014,
            "SMALL_MICRO_CAP": 0.028,
            "ALL_CAP": 0.018,
        }
        annual_rate = rates.get(universe_tier.upper(), 0.018)
        years = max(0.5, float(backtest_years))
        survivorship_drag_pct = round((1.0 - ((1.0 - annual_rate) ** years)) * 100.0, 2)
        adjusted_cagr_haircut_pct = round(annual_rate * 100.0, 2)

        return {
            "universe_tier": universe_tier.upper(),
            "backtest_years": years,
            "annual_failure_rate_pct": round(annual_rate * 100.0, 2),
            "cumulative_survivorship_drag_pct": survivorship_drag_pct,
            "annual_cagr_haircut_pct": adjusted_cagr_haircut_pct,
            "fiduciary_guidance": (
                f"For a {years:.1f}Y backtest in {universe_tier.upper()}, reported CAGR is upwardly biased by "
                f"approximately {adjusted_cagr_haircut_pct:.1f}% p.a. due to omission of delisted/liquidated constituents."
            )
        }


# ---------------------------------------------------------------------------
# Initial Canonical Seed Registry
# ---------------------------------------------------------------------------

_CANONICAL_SEEDS = [
    # Prominent Microcaps & Turnarounds
    SecurityRecord(
        canonical_symbol="APOLLO",
        company_name="Apollo Micro Systems Ltd",
        exchange="NSE",
        nse_symbol="APOLLO",
        bse_code="540879",
        isin="INE713T01028",
        yahoo_ticker="APOLLO.NS",
        aliases=["APOLLOMICR", "APOLLOMICRO", "APOLLO MICRO", "APOLLO MICRO SYSTEMS", "540879"],
        sector="Aerospace & Defense",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="DATAPATTNS",
        company_name="Data Patterns (India) Ltd",
        exchange="NSE",
        nse_symbol="DATAPATTNS",
        bse_code="543428",
        isin="INE610M01019",
        yahoo_ticker="DATAPATTNS.NS",
        aliases=["DATAPATTERN", "DATAPATTERNS", "DATA PATTERNS", "543428"],
        sector="Aerospace & Defense",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SHILCHAR",
        company_name="Shilchar Technologies Ltd",
        exchange="NSE",
        nse_symbol="SHILCTECH",
        bse_code="531201",
        isin="INE023E01014",
        yahoo_ticker="SHILCTECH.NS",
        aliases=["SHILCTECH", "SHILCHARTECH", "SHILCHAR TECHNOLOGIES", "531201"],
        sector="Electrical Equipment",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="AXISCADES",
        company_name="Axiscades Technologies Ltd",
        exchange="NSE",
        nse_symbol="AXISCADES",
        bse_code="532395",
        isin="INE555B01013",
        yahoo_ticker="AXISCADES.NS",
        aliases=["AXIS CADES", "AXISCADES ENGINEERING", "532395"],
        sector="IT Services & Consulting",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="MOSCHIP",
        company_name="MosChip Technologies Ltd",
        exchange="NSE",
        nse_symbol="MOSCHIP",
        bse_code="532407",
        isin="INE219B01015",
        yahoo_ticker="MOSCHIP.NS",
        aliases=["MOSCHIP TECH", "MOSCHIP TECHNOLOGIES", "532407"],
        sector="Semiconductors",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="IZMO",
        company_name="Izmo Ltd",
        exchange="NSE",
        nse_symbol="IZMO",
        bse_code="532341",
        isin="INE848A01014",
        yahoo_ticker="IZMO.NS",
        aliases=["IZMO LTD", "532341"],
        sector="IT Software",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TEJASNET",
        company_name="Tejas Networks Ltd",
        exchange="NSE",
        nse_symbol="TEJASNET",
        bse_code="540595",
        isin="INE010J01012",
        yahoo_ticker="TEJASNET.NS",
        aliases=["TEJAS", "TEJAS NETWORKS", "TEJASNETWORKS", "540595"],
        sector="Telecom Equipment",
        market_cap_tier="MID_CAP",
    ),
    # Core Bellwethers
    SecurityRecord(
        canonical_symbol="RELIANCE",
        company_name="Reliance Industries Ltd",
        exchange="NSE",
        nse_symbol="RELIANCE",
        bse_code="500325",
        isin="INE002A01018",
        yahoo_ticker="RELIANCE.NS",
        aliases=["RELIANCE INDUSTRIES", "RIL", "500325"],
        sector="Conglomerate / Energy",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TCS",
        company_name="Tata Consultancy Services Ltd",
        exchange="NSE",
        nse_symbol="TCS",
        bse_code="532540",
        isin="INE467B01029",
        yahoo_ticker="TCS.NS",
        aliases=["TATA CONSULTANCY SERVICES", "532540"],
        sector="IT Services",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="INFY",
        company_name="Infosys Ltd",
        exchange="NSE",
        nse_symbol="INFY",
        bse_code="500209",
        isin="INE009A01021",
        yahoo_ticker="INFY.NS",
        aliases=["INFOSYS", "500209"],
        sector="IT Services",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="HDFCBANK",
        company_name="HDFC Bank Ltd",
        exchange="NSE",
        nse_symbol="HDFCBANK",
        bse_code="500180",
        isin="INE040A01034",
        yahoo_ticker="HDFCBANK.NS",
        aliases=["HDFC BANK", "HDFC", "500180"],
        sector="Private Sector Bank",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="ICICIBANK",
        company_name="ICICI Bank Ltd",
        exchange="NSE",
        nse_symbol="ICICIBANK",
        bse_code="532174",
        isin="INE090A01021",
        yahoo_ticker="ICICIBANK.NS",
        aliases=["ICICI BANK", "532174"],
        sector="Private Sector Bank",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TATAMOTORS",
        company_name="Tata Motors Ltd",
        exchange="NSE",
        nse_symbol="TATAMOTORS",
        bse_code="500570",
        isin="INE155A01022",
        yahoo_ticker="TATAMOTORS.NS",
        aliases=["TATA MOTORS", "500570"],
        sector="Automobiles",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SBIN",
        company_name="State Bank of India",
        exchange="NSE",
        nse_symbol="SBIN",
        bse_code="500112",
        isin="INE062A01020",
        yahoo_ticker="SBIN.NS",
        aliases=["STATE BANK OF INDIA", "SBI", "STATE BANK", "500112"],
        sector="Public Sector Bank",
        market_cap_tier="LARGE_CAP",
    ),
    # High-Growth Compounders & Capital Goods Sovereignty
    SecurityRecord(
        canonical_symbol="KERNEX",
        company_name="Kernex Microsystems (India) Ltd",
        exchange="NSE",
        nse_symbol="KERNEX",
        bse_code="532686",
        isin="INE871F01019",
        yahoo_ticker="KERNEX.NS",
        aliases=['KERNEX MICRO', 'KERNEX MICROSYSTEMS', '532686'],
        sector="Railways & Electronic Safety",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="FRONTIER",
        company_name="Frontier Springs Ltd",
        exchange="NSE",
        nse_symbol="FRONTSP",
        bse_code="522195",
        isin="INE572D01014",
        yahoo_ticker="FRONTSP.NS",
        aliases=['FRONTSP', 'FRONTIER SPRINGS', 'FRONTIERSPRINGS', '522195'],
        sector="Railways & Springs",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="GENUSPOWER",
        company_name="Genus Power Infrastructures Ltd",
        exchange="NSE",
        nse_symbol="GENUSPOWER",
        bse_code="530343",
        isin="INE955D01029",
        yahoo_ticker="GENUSPOWER.NS",
        aliases=['GENUS POWER', 'GENUS', '530343'],
        sector="Smart Metering & Power Grid",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="WAAREERTL",
        company_name="Waaree Renewable Technologies Ltd",
        exchange="BSE",
        nse_symbol=None,
        bse_code="534618",
        isin="INE299N01021",
        yahoo_ticker="WAAREERTL.BO",
        aliases=['WAAREE RENEWABLES', 'WAAREE RENEWABLE', '534618'],
        sector="Solar EPC & Green Energy",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="BALUFORGE",
        company_name="Balu Forge Industries Ltd",
        exchange="NSE",
        nse_symbol="BALUFORGE",
        bse_code="531112",
        isin="INE011E01029",
        yahoo_ticker="BALUFORGE.NS",
        aliases=['BALU FORGE', '531112'],
        sector="Forging & Defence Components",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TARIL",
        company_name="Transformers & Rectifiers (India) Ltd",
        exchange="NSE",
        nse_symbol="TARIL",
        bse_code="532928",
        isin="INE763I01026",
        yahoo_ticker="TARIL.NS",
        aliases=['TRANSFORMERS AND RECTIFIERS', 'TRIL', '532928'],
        sector="Power Transmission & Transformers",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="CONCORD",
        company_name="Concord Control Systems Ltd",
        exchange="BSE",
        nse_symbol=None,
        bse_code="543620",
        isin="INE0M0N01013",
        yahoo_ticker="CNCRD.BO",
        aliases=['CNCRD', 'CONCORD CONTROL', 'CONCORD CONTROL SYSTEMS', '543620'],
        sector="Railway Electrification",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="AZAD",
        company_name="Azad Engineering Ltd",
        exchange="NSE",
        nse_symbol="AZAD",
        bse_code="544061",
        isin="INE02IJ01035",
        yahoo_ticker="AZAD.NS",
        aliases=['AZAD ENGINEERING', '544061'],
        sector="Aerospace & Defence Components",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="DYCL",
        company_name="Dynamic Cables Ltd",
        exchange="NSE",
        nse_symbol="DYCL",
        bse_code="540795",
        isin="INE600Y01019",
        yahoo_ticker="DYCL.NS",
        aliases=['DYNAMIC CABLES', 'DYNAMIC CABLE', '540795'],
        sector="Cables & Power Transmission",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="KPIGREEN",
        company_name="KPI Green Energy Ltd",
        exchange="NSE",
        nse_symbol="KPIGREEN",
        bse_code="542323",
        isin="INE542W01017",
        yahoo_ticker="KPIGREEN.NS",
        aliases=['KPI GREEN', 'KPI GREEN ENERGY', '542323'],
        sector="Solar & Wind Power IPP",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SHAKTIPUMP",
        company_name="Shakti Pumps (India) Ltd",
        exchange="NSE",
        nse_symbol="SHAKTIPUMP",
        bse_code="531431",
        isin="INE908D01010",
        yahoo_ticker="SHAKTIPUMP.NS",
        aliases=['SHAKTI PUMPS', 'SHAKTI PUMP', '531431'],
        sector="Solar Pumps & Agriculture",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="BLS",
        company_name="BLS International Services Ltd",
        exchange="NSE",
        nse_symbol="BLS",
        bse_code="540073",
        isin="INE153T01027",
        yahoo_ticker="BLS.NS",
        aliases=['BLS INTERNATIONAL', 'BLS INTL', '540073'],
        sector="Consular & Tech Citizen Services",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="MACPOWER",
        company_name="Macpower CNC Machines Ltd",
        exchange="NSE",
        nse_symbol="MACPOWER",
        bse_code="541295",
        isin="INE155Z01011",
        yahoo_ticker="MACPOWER.NS",
        aliases=['MACPOWER CNC', '541295'],
        sector="CNC Machinery & Industrial",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TEXRAIL",
        company_name="Texmaco Rail & Engineering Ltd",
        exchange="NSE",
        nse_symbol="TEXRAIL",
        bse_code="533326",
        isin="INE621L01012",
        yahoo_ticker="TEXRAIL.NS",
        aliases=['TEXMACO RAIL', 'TEXMACO', '533326'],
        sector="Railways & Wagons EPC",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="PARAS",
        company_name="Paras Defence and Space Technologies Ltd",
        exchange="NSE",
        nse_symbol="PARAS",
        bse_code="543367",
        isin="INE045601015",
        yahoo_ticker="PARAS.NS",
        aliases=['PARAS DEFENCE', 'PARAS DEFENCE & SPACE', '543367'],
        sector="Defence Optronics & Space",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="CAPLIPOINT",
        company_name="Caplin Point Laboratories Ltd",
        exchange="NSE",
        nse_symbol="CAPLIPOINT",
        bse_code="524742",
        isin="INE475E01026",
        yahoo_ticker="CAPLIPOINT.NS",
        aliases=['CAPLIN POINT', 'CAPLIN', '524742'],
        sector="Pharmaceuticals & Injectables",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SJS",
        company_name="SJS Enterprises Ltd",
        exchange="NSE",
        nse_symbol="SJS",
        bse_code="543387",
        isin="INE284S01014",
        yahoo_ticker="SJS.NS",
        aliases=['SJS ENTERPRISES', '543387'],
        sector="Auto Components & Aesthetics",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="INOXWIND",
        company_name="Inox Wind Ltd",
        exchange="NSE",
        nse_symbol="INOXWIND",
        bse_code="539083",
        isin="INE066P01011",
        yahoo_ticker="INOXWIND.NS",
        aliases=['INOX WIND', '539083'],
        sector="Wind Energy & Turbines",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="PGEL",
        company_name="PG Electroplast Ltd",
        exchange="NSE",
        nse_symbol="PGEL",
        bse_code="533569",
        isin="INE457L01011",
        yahoo_ticker="PGEL.NS",
        aliases=['PG ELECTROPLAST', '533569'],
        sector="Electronics Manufacturing Services",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="GRAVITA",
        company_name="Gravita India Ltd",
        exchange="NSE",
        nse_symbol="GRAVITA",
        bse_code="533282",
        isin="INE024L01027",
        yahoo_ticker="GRAVITA.NS",
        aliases=['GRAVITA INDIA', '533282'],
        sector="Recycling & Circular Economy",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="LTFOODS",
        company_name="LT Foods Ltd",
        exchange="NSE",
        nse_symbol="LTFOODS",
        bse_code="532783",
        isin="INE938A01021",
        yahoo_ticker="LTFOODS.NS",
        aliases=['LT FOODS', 'DAAWAT', '532783'],
        sector="Consumer Food & FMCG",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="GRWRHITECH",
        company_name="Garware Hi-Tech Films Ltd",
        exchange="NSE",
        nse_symbol="GRWRHITECH",
        bse_code="500655",
        isin="INE291A01017",
        yahoo_ticker="GRWRHITECH.NS",
        aliases=['GARWARE HI TECH', 'GARWARE', '500655'],
        sector="Specialty Films & Polymers",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="PITTIENG",
        company_name="Pitti Engineering Ltd",
        exchange="NSE",
        nse_symbol="PITTIENG",
        bse_code="513519",
        isin="INE374B01012",
        yahoo_ticker="PITTIENG.NS",
        aliases=['PITTI ENGINEERING', 'PITTI', '513519'],
        sector="Electrical Steel Laminations",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="RIR",
        company_name="RIR Power Electronics Ltd",
        exchange="BSE",
        nse_symbol=None,
        bse_code="517316",
        isin="INE029D01017",
        yahoo_ticker="RIR.BO",
        aliases=['RIR POWER', 'RIR POWER ELECTRONICS', '517316'],
        sector="Power Semiconductors",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="NEWGEN",
        company_name="Newgen Software Technologies Ltd",
        exchange="NSE",
        nse_symbol="NEWGEN",
        bse_code="540900",
        isin="INE619B01017",
        yahoo_ticker="NEWGEN.NS",
        aliases=['NEWGEN SOFTWARE', '540900'],
        sector="Enterprise AI & Software",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TAALTECH",
        company_name="TAAL Tech India Ltd",
        exchange="BSE",
        nse_symbol=None,
        bse_code="539956",
        isin="INE430R01014",
        yahoo_ticker="TAALTECH.BO",
        aliases=['TAAL TECH', '539956'],
        sector="Aerospace & ER&D Services",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="CYIENTDLM",
        company_name="Cyient DLM Ltd",
        exchange="NSE",
        nse_symbol="CYIENTDLM",
        bse_code="543933",
        isin="INE055V01018",
        yahoo_ticker="CYIENTDLM.NS",
        aliases=['CYIENT DLM', '543933'],
        sector="Aerospace & Defence EMS",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="MOLDTKPAC",
        company_name="Mold-Tek Packaging Ltd",
        exchange="NSE",
        nse_symbol="MOLDTKPAC",
        bse_code="533080",
        isin="INE893J01029",
        yahoo_ticker="MOLDTKPAC.NS",
        aliases=['MOLD TEK PACKAGING', 'MOLDTEK', '533080'],
        sector="Packaging",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="CENTUM",
        company_name="Centum Electronics Ltd",
        exchange="NSE",
        nse_symbol="CENTUM",
        bse_code="517544",
        isin="INE320B01020",
        yahoo_ticker="CENTUM.NS",
        aliases=['CENTUM ELECTRONICS', 'CENTUM', '517544'],
        sector="Defence & Space Electronics",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="HBLPOWER",
        company_name="HBL Power Systems Ltd",
        exchange="NSE",
        nse_symbol="HBLPOWER",
        bse_code="517271",
        isin="INE292B01021",
        yahoo_ticker="HBLPOWER.NS",
        aliases=['HBL POWER', 'HBL POWER SYSTEMS', 'HBLENGINE', '517271'],
        sector="Defence & Space Electronics",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="PREMIERENE",
        company_name="Premier Energies Ltd",
        exchange="NSE",
        nse_symbol="PREMIERENE",
        bse_code="544240",
        isin="INE286N01018",
        yahoo_ticker="PREMIERENE.NS",
        aliases=['PREMIER ENERGIES', 'PREMIER', '544240'],
        sector="Solar Cells & Modules",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="DIXON",
        company_name="Dixon Technologies (India) Ltd",
        exchange="NSE",
        nse_symbol="DIXON",
        bse_code="540699",
        isin="INE935N01020",
        yahoo_ticker="DIXON.NS",
        aliases=['DIXON TECH', 'DIXON TECHNOLOGIES', '540699'],
        sector="Electronics Manufacturing Services",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="LLOYDSME",
        company_name="Lloyds Metals & Energy Ltd",
        exchange="NSE",
        nse_symbol="LLOYDSME",
        bse_code="512455",
        isin="INE281B01032",
        yahoo_ticker="LLOYDSME.NS",
        aliases=['LLOYDS METALS', 'LLOYDS METAL', '512455'],
        sector="Mining & Sponge Iron",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="JWL",
        company_name="Jupiter Wagons Ltd",
        exchange="NSE",
        nse_symbol="JWL",
        bse_code="533272",
        isin="INE209L01016",
        yahoo_ticker="JWL.NS",
        aliases=['JUPITER WAGONS', '533272'],
        sector="Railways & Wagons",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TITAGARH",
        company_name="Titagarh Rail Systems Ltd",
        exchange="NSE",
        nse_symbol="TITAGARH",
        bse_code="532966",
        isin="INE615H01020",
        yahoo_ticker="TITAGARH.NS",
        aliases=['TITAGARH RAIL', 'TITAGARH WAGONS', '532966'],
        sector="Railways & Passenger Coaches",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="DYNAMATECH",
        company_name="Dynamatic Technologies Ltd",
        exchange="NSE",
        nse_symbol="DYNAMATECH",
        bse_code="505242",
        isin="INE221B01012",
        yahoo_ticker="DYNAMATECH.NS",
        aliases=['DYNAMATIC TECH', 'DYNAMATIC', '505242'],
        sector="Aerospace & Hydraulics",
        market_cap_tier="SMALL_CAP",
    ),
    SecurityRecord(
        canonical_symbol="DCXINDIA",
        company_name="DCX Systems Ltd",
        exchange="NSE",
        nse_symbol="DCXINDIA",
        bse_code="543650",
        isin="INE0KL801014",
        yahoo_ticker="DCXINDIA.NS",
        aliases=['DCX SYSTEMS', '543650'],
        sector="Defence Cable Harnesses",
        market_cap_tier="MICRO_CAP",
    ),
    SecurityRecord(
        canonical_symbol="PTCIL",
        company_name="PTC Industries Ltd",
        exchange="BSE",
        nse_symbol=None,
        bse_code="539006",
        isin="INE596F01018",
        yahoo_ticker="PTCIL.BO",
        aliases=['PTC INDUSTRIES', 'PTC', '539006'],
        sector="Titanium & Defence Castings",
        market_cap_tier="MID_CAP",
    ),
    SecurityRecord(
        canonical_symbol="POLYCAB",
        company_name="Polycab India Ltd",
        exchange="NSE",
        nse_symbol="POLYCAB",
        bse_code="542652",
        isin="INE455K01017",
        yahoo_ticker="POLYCAB.NS",
        aliases=['POLYCAB INDIA', '542652'],
        sector="Cables & Electrical Goods",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="APARINDS",
        company_name="Apar Industries Ltd",
        exchange="NSE",
        nse_symbol="APARINDS",
        bse_code="532259",
        isin="INE372A01015",
        yahoo_ticker="APARINDS.NS",
        aliases=['APAR INDUSTRIES', 'APAR', '532259'],
        sector="Conductors & Specialty Oils",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SUZLON",
        company_name="Suzlon Energy Ltd",
        exchange="NSE",
        nse_symbol="SUZLON",
        bse_code="532667",
        isin="INE040H01021",
        yahoo_ticker="SUZLON.NS",
        aliases=['SUZLON ENERGY', '532667'],
        sector="Wind Energy & Turbines",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="SOLARINDS",
        company_name="Solar Industries India Ltd",
        exchange="NSE",
        nse_symbol="SOLARINDS",
        bse_code="532725",
        isin="INE343H01029",
        yahoo_ticker="SOLARINDS.NS",
        aliases=['SOLAR INDUSTRIES', '532725'],
        sector="Explosives & Defence Munitions",
        market_cap_tier="LARGE_CAP",
    ),
    SecurityRecord(
        canonical_symbol="TRENT",
        company_name="Trent Ltd",
        exchange="NSE",
        nse_symbol="TRENT",
        bse_code="500251",
        isin="INE849A01020",
        yahoo_ticker="TRENT.NS",
        aliases=['TRENT LTD', 'WESTSIDE', 'ZUDIO', '500251'],
        sector="Retail & Fast Fashion",
        market_cap_tier="LARGE_CAP",
    ),
]

for _seed in _CANONICAL_SEEDS:
    SecurityMaster.register_security(_seed)

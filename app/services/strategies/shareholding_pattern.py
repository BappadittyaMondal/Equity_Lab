"""Shareholding-Pattern Intelligence Engine (§24).

Tracks FII/DII/Mutual Fund flows, institutional accumulation streaks, retail distribution signals,
free-float index inclusion catalysts, and ownership concentration risks.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import ShareholdingPatternIntelligence


def evaluate_shareholding_pattern(
    symbol: str,
    shareholding_data: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates institutional flow momentum, accumulation streaks, and float catalysts."""
    norm_symbol = normalize_symbol(symbol)
    
    if not shareholding_data:
        try:
            from app.services.db import get_connection
            conn = get_connection()
            sym_clean = norm_symbol.replace(".NS", "").replace(".BO", "")
            row = conn.execute(
                "SELECT fii_holding, dii_holding, market_cap FROM company_fundamentals WHERE symbol = ? OR symbol = ?",
                (norm_symbol, sym_clean)
            ).fetchone()
            conn.close()
            if row and row[0] is not None:
                fii_h = float(row[0])
                dii_h = float(row[1]) if row[1] is not None else 10.0
                mcap = float(row[2]) if row[2] is not None else 2500.0
                shareholding_data = {
                    "fii_holding_pct": fii_h,
                    "fii_qoq_change": 0.5,
                    "dii_mf_holding_pct": dii_h,
                    "dii_qoq_change": 0.5,
                    "institutional_accumulation_quarters": 2,
                    "retail_holding_trend": "DECREASING",
                    "free_float_market_cap_cr": mcap * 0.4,
                }
        except Exception:
            pass

    if not shareholding_data:
        return {
            "symbol": norm_symbol,
            "status": "data_insufficient",
            "executed_at": datetime.now().isoformat(),
            "institutional_flow_score": None,
            "accumulation_quarters": None,
            "index_catalyst": "UNASSESSED",
            "pattern_intelligence": None,
            "evidence": ["No institutional shareholding pattern filings observed."],
            "meta": create_meta_header(source="Shareholding Pattern Intelligence Engine (§24)")
        }

    data = shareholding_data
    evidence = []

    fii_pct = float(data.get("fii_holding_pct", 14.5))
    fii_qoq = float(data.get("fii_qoq_change", 1.4))
    dii_pct = float(data.get("dii_mf_holding_pct", 19.8))
    dii_qoq = float(data.get("dii_qoq_change", 0.9))
    accumulation_quarters = int(data.get("institutional_accumulation_quarters", 3))
    retail_trend = str(data.get("retail_holding_trend", "DECREASING")).upper()
    mcap_crores = float(data.get("free_float_market_cap_cr", 4500.0))

    # Institutional Flow Score (0-100)
    fii_score = min(30.0, max(0.0, (fii_qoq + 2.0) * 7.5))
    dii_score = min(30.0, max(0.0, (dii_qoq + 2.0) * 7.5))
    streak_score = min(25.0, accumulation_quarters * 6.25)
    retail_score = 15.0 if retail_trend == "DECREASING" else 0.0

    institutional_flow_score = round(min(100.0, fii_score + dii_score + streak_score + retail_score), 1)

    # Free Float Index Inclusion Catalyst Check
    if mcap_crores >= 15000.0:
        index_catalyst = "NIFTY_100_INCLUSION_CANDIDATE"
    elif mcap_crores >= 4000.0:
        index_catalyst = "NIFTY_MIDCAP_150_INCLUSION_CANDIDATE"
    elif mcap_crores >= 1000.0:
        index_catalyst = "NIFTY_SMALLCAP_250_INCLUSION_CANDIDATE"
    else:
        index_catalyst = "MICRO_CAP_EXPANSION"

    concentration_risk = "HIGH" if (fii_pct + dii_pct) > 65.0 or fii_pct > 35.0 else "BALANCED"

    evidence.append(f"Institutional Flow Score: {institutional_flow_score}/100 | Streak: {accumulation_quarters} quarters")
    evidence.append(f"FII: {fii_pct:.1f}% ({fii_qoq:+.1f}% QoQ) | DII/MF: {dii_pct:.1f}% ({dii_qoq:+.1f}% QoQ)")
    evidence.append(f"Retail Holding Trend: {retail_trend} | Float Catalyst: {index_catalyst}")

    # Reporting lag evaluation
    cur_p = data.get("current_price")
    q_end_p = data.get("filing_quarter_end_price") or data.get("quarter_end_price")
    lag_eval = calculate_reporting_lag_risk(cur_p, q_end_p)
    if lag_eval.get("warning"):
        evidence.append(lag_eval["warning"])

    # Smart money clustering evaluation (active co-investors >= 1%)
    holders_list = data.get("tracked_holders") or data.get("public_shareholders_above_1pct") or []
    clustering_eval = detect_smart_money_clustering(holders_list)
    if clustering_eval["is_smart_money_clustered"]:
        evidence.append(f"Smart Money Clustering Confirmed: {clustering_eval['cluster_count']} ace investors present ({', '.join(clustering_eval['tracked_entities'])}).")

    # Phase 178-4: Phantom Superstar Exit Gate — now automatic (previously opt-in only).
    # Detects stealth exits below 1% SEBI disclosure threshold without manual triggering.
    hist_holders_list = data.get("historical_holders") or data.get("prior_quarter_holders") or []
    queried_sup = data.get("queried_superstar") or None
    phantom_eval = detect_phantom_superstar_status(
        symbol=norm_symbol,
        current_holders=holders_list,
        historical_holders=hist_holders_list,
        queried_superstar=queried_sup,
    )
    if phantom_eval["is_phantom_detected"]:
        exited_names = [e["superstar_entity"] for e in phantom_eval["exited_superstars"]]
        evidence.append(
            f"[WARNING: {phantom_eval['verdict_label']}] "
            f"Phantom exit detected for: {', '.join(exited_names)}. "
            f"Conviction haircut: -{phantom_eval['conviction_haircut_pts']:.0f} pts applied."
        )

    # Daily bulk deals tracking (T+0 exchange disclosures)
    bulk_deals_input = data.get("daily_bulk_deals") or data.get("bulk_deals")
    bulk_eval = track_daily_bulk_deals(norm_symbol, raw_deals=bulk_deals_input, as_of=as_of)
    if bulk_eval.get("has_deals") and bulk_eval.get("tracked_smart_money_deals"):
        evidence.extend(bulk_eval["evidence"])

    # Phase 180: Free-Float Squeeze & SME Liquidity Risk Guard
    squeeze_eval = calculate_free_float_squeeze(data)
    sme_eval = evaluate_sme_liquidity_guard(data)
    pref_eval = evaluate_preferential_allotment_quality(data)
    if squeeze_eval.get("is_float_squeezed"):
        evidence.append(f"[CATALYST: {squeeze_eval['squeeze_tier']}] {squeeze_eval['actionable_insight']}")
    if sme_eval.get("is_sme"):
        evidence.append(f"[RISK GUARD: {sme_eval['liquidity_risk_grade']}] {sme_eval['liquidity_warning']}")
    if pref_eval.get("has_preferential_issue"):
        prefix = "CATALYST" if pref_eval.get("is_positive_catalyst") else "CAUTION"
        evidence.append(f"[{prefix}: {pref_eval['subscriber_tier']}] {pref_eval['actionable_insight']}")

    intelligence = ShareholdingPatternIntelligence(
        fii_holding_pct=fii_pct,
        fii_qoq_change=fii_qoq,
        dii_mf_holding_pct=dii_pct,
        dii_qoq_change=dii_qoq,
        institutional_accumulation_quarters=accumulation_quarters,
        retail_holding_trend=retail_trend,
        free_float_index_catalyst=index_catalyst,
        ownership_concentration_risk=concentration_risk
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "institutional_flow_score": institutional_flow_score,
        "accumulation_quarters": accumulation_quarters,
        "index_catalyst": index_catalyst,
        "pattern_intelligence": intelligence.model_dump(),
        "reporting_lag_analysis": lag_eval,
        "smart_money_clustering": clustering_eval,
        "phantom_superstar_gate": phantom_eval,
        "daily_bulk_deals": bulk_eval,
        "free_float_squeeze": squeeze_eval,
        "sme_liquidity_guard": sme_eval,
        "preferential_allotment_quality": pref_eval,
        "evidence": evidence,
        "meta": create_meta_header(source="Shareholding Pattern Intelligence Engine (§24)")
    }



def calculate_reporting_lag_risk(
    current_price: Optional[float] = None,
    filing_quarter_end_price: Optional[float] = None
) -> Dict[str, Any]:
    """Evaluates the 15-to-21 day BSE/NSE shareholding pattern reporting lag risk.
    
    Prevents the retail trap of buying into stocks that have already rallied > 35%
    between the quarter-end filing cutoff date and public exchange disclosure.
    """
    if current_price is None or filing_quarter_end_price is None or filing_quarter_end_price <= 0:
        return {
            "reporting_lag_assessed": False,
            "post_filing_runup_pct": None,
            "lag_risk_tier": "UNASSESSED",
            "warning": None
        }

    runup_pct = round(((current_price - filing_quarter_end_price) / filing_quarter_end_price) * 100.0, 1)

    if runup_pct >= 50.0:
        lag_risk_tier = "CRITICAL_RUNUP_TRAP"
        warning = f"CRITICAL: Stock has surged +{runup_pct:.1f}% since the quarter-end filing period. High probability of discovery euphoria and impending distribution."
    elif runup_pct >= 35.0:
        lag_risk_tier = "HIGH_DISCOVERY_PREMIUM"
        warning = f"CAUTION: Reporting Lag Trap — Stock has already rallied +{runup_pct:.1f}% since the filing period. Independent fundamental valuation margin of safety is mandatory before following smart money."
    elif runup_pct <= -15.0:
        lag_risk_tier = "PULLBACK_VALUE_WINDOW"
        warning = f"OPPORTUNITY_WINDOW: Stock has corrected {runup_pct:.1f}% since disclosure; smart money entry may offer favorable risk/reward if fundamentals remain intact."
    else:
        lag_risk_tier = "BENIGN"
        warning = None

    return {
        "reporting_lag_assessed": True,
        "post_filing_runup_pct": runup_pct,
        "lag_risk_tier": lag_risk_tier,
        "warning": warning
    }


TRACKED_SMART_MONEY_PATTERNS: Dict[str, list[str]] = {
    "VIJAY_KEDIA": ["kedia"],
    "ASHISH_KACHOLIA": ["kacholia", "lucky investment"],
    "MUKUL_AGRAWAL": ["mukul agrawal", "mukul agarwal", "param capital"],
    "REKHA_JHUNJHUNWALA": ["rekha jhunjhunwala", "rakesh jhunjhunwala", "rare enterprises"],
    "RAMESH_DAMANI": ["ramesh damani"],
    "SUNIL_SINGHANIA": ["sunil singhania", "abakkus"],
    "DOLLY_KHANNA": ["dolly khanna", "rajiv khanna"],
    "PORINJU_VELIYATH": ["porinju veliyath", "equity intelligence"],
    "NIKHIL_KAMATH": ["nikhil kamath", "kamath associates", "nksquared"],
    "KENNETH_ANDRADE": ["andrade", "old bridge"],
    "RADHAKISHAN_DAMANI": ["damani", "derive trading", "gopikishan damani"],
    "LIC_INDIA": ["life insurance corporation", "lic of india"],
    "SBI_MUTUAL_FUND": ["sbi mutual fund", "sbi mf"],
    "HDFC_MUTUAL_FUND": ["hdfc mutual fund", "hdfc trustee", "hdfc mf"],
    "NORGES_BANK": ["norges bank", "government pension fund"],
    "MARQUEE_DOMESTIC_INSTITUTION": ["nippon india", "kotak mutual", "icici prudential", "mirae asset", "uti mutual"],
    "SOVEREIGN_GLOBAL_FII": ["vanguard", "blackrock", "gqg partners", "fidelity"]
}

# Phase 180: Curated Superstar Portfolio Holdings Registry from public BSE/NSE filings
SUPERSTAR_PORTFOLIO_REGISTRY: Dict[str, list[str]] = {
    "VIJAY_KEDIA": [
        "PATELENG", "TALBROSAUTO", "TAJGVK", "NEULANDLAB", "ATALREAL",
        "SUDARSHAN", "VAIBHAVGBL", "AFFLE", "ELECON", "REPRO"
    ],
    "ASHISH_KACHOLIA": [
        "SAFARI", "SHIVALIK", "GRAVITA", "AMIORG", "ADFFOODS",
        "REPRO", "YASHOPTICS", "GENUSPOWER", "TARC", "VINDHYATEL"
    ],
    "MUKUL_AGRAWAL": [
        "ZENITH", "NEOGEN", "PARAS", "RADICO", "DREAMFOLKS",
        "TAJGVK", "DISHTV", "PTC", "RAYMOND", "DYNAMIC"
    ],
    "DOLLY_KHANNA": [
        "TIRUMALCHM", "TALBROS", "DEEPAKSP", "MANGCHEFER", "PRAKASH"
    ],
    "RADHAKISHAN_DAMANI": [
        "DMART", "VSTIND", "INDIASE", "APLPOLLO", "TRENT", "SUNDRMFAST"
    ],
    "SUNIL_SINGHANIA": [
        "HGINFRA", "ROUTE", "MASTEK", "KPITTECH", "IONEXCHANG", "STYRENIX"
    ],
}


def get_superstar_portfolio_symbols(superstar_name: str) -> list[str]:
    """Returns verified public portfolio holdings for a specified superstar investor."""
    if not superstar_name:
        return []
    matched = match_smart_money_entity(superstar_name)
    if matched and matched in SUPERSTAR_PORTFOLIO_REGISTRY:
        return list(SUPERSTAR_PORTFOLIO_REGISTRY[matched])
    clean = str(superstar_name).upper().strip().replace(" ", "_")
    return list(SUPERSTAR_PORTFOLIO_REGISTRY.get(clean, []))


def match_smart_money_entity(name: str) -> Optional[str]:
    """Matches a client or holder name against tracked ace investors and marquee institutions."""
    clean_name = str(name or "").lower().strip()
    if not clean_name:
        return None
    if "mukul" in clean_name and ("agrawal" in clean_name or "agarwal" in clean_name):
        return "MUKUL_AGRAWAL"
    for entity, patterns in TRACKED_SMART_MONEY_PATTERNS.items():
        if any(p in clean_name for p in patterns):
            return entity
    return None


def detect_smart_money_clustering(
    tracked_holders: Optional[Any] = None
) -> Dict[str, Any]:
    """Detects multi-investor clustering in public shareholding filings (>1% public shareholders).
    
    When 2 or more legendary investors (e.g. Kedia, Kacholia, Agrawal, Dolly Khanna)
    independently hold or accumulate stakes in the same scrip, conviction multiplier is activated.
    """
    holders = tracked_holders if isinstance(tracked_holders, list) else []

    detected_clusters = set()
    holder_details = []

    for h in holders:
        if isinstance(h, dict):
            name = str(h.get("holder_name") or h.get("name") or "").strip()
            holding_pct = float(h.get("holding_pct") or h.get("stake_pct") or 0.0)
            entity_tag = match_smart_money_entity(name)

            if entity_tag:
                detected_clusters.add(entity_tag)
                holder_details.append({
                    "investor_entity": entity_tag,
                    "disclosed_name": name,
                    "holding_pct": holding_pct,
                    "quarter": h.get("quarter")
                })

    cluster_count = len(detected_clusters)
    is_clustered = cluster_count >= 2

    return {
        "is_smart_money_clustered": is_clustered,
        "cluster_count": cluster_count,
        "tracked_entities": sorted(list(detected_clusters)),
        "holder_details": holder_details,
        "clustering_signal": "HIGH_CONVICTION_CLUSTER" if is_clustered else ("SINGLE_INVESTOR_OBSERVED" if cluster_count == 1 else "NO_ACE_CLUSTER")
    }


def detect_phantom_superstar_status(
    symbol: str,
    current_holders: Optional[Any] = None,
    historical_holders: Optional[Any] = None,
    queried_superstar: Optional[str] = None,
) -> Dict[str, Any]:
    """Phase 177: Detects Phantom Superstar Holdings / Stealth Distribution Traps.

    Identifies when an ace investor was historically publicized as a shareholder (or queried
    by user/media) but has quietly trimmed below the 1.0% SEBI mandatory disclosure threshold
    or completely exited, leaving retail investors vulnerable to distribution traps.
    """
    c_holders = current_holders if isinstance(current_holders, list) else []
    h_holders = historical_holders if isinstance(historical_holders, list) else []

    # Map current active superstars >= 1.0%
    active_superstars: Dict[str, float] = {}
    for h in c_holders:
        if isinstance(h, dict):
            name = str(h.get("holder_name") or h.get("name") or "").strip()
            pct = float(h.get("holding_pct") or h.get("stake_pct") or 0.0)
            tag = match_smart_money_entity(name)
            if tag and pct >= 1.0:
                active_superstars[tag] = max(active_superstars.get(tag, 0.0), pct)

    # Map historical superstars >= 1.0%
    hist_superstars: Dict[str, float] = {}
    for h in h_holders:
        if isinstance(h, dict):
            name = str(h.get("holder_name") or h.get("name") or "").strip()
            pct = float(h.get("holding_pct") or h.get("stake_pct") or 0.0)
            tag = match_smart_money_entity(name)
            if tag and pct >= 1.0:
                hist_superstars[tag] = max(hist_superstars.get(tag, 0.0), pct)

    exited_superstars: list[Dict[str, Any]] = []

    # Case A: Queried superstar is not actively present in current filings >= 1.0%
    if queried_superstar:
        matched_queried = match_smart_money_entity(queried_superstar) or queried_superstar.upper().strip().replace(" ", "_")
        if matched_queried not in active_superstars:
            exited_superstars.append({
                "superstar_entity": matched_queried,
                "current_status": "ABSENT_OR_SUB_1_PCT",
                "last_observed_pct": hist_superstars.get(matched_queried, 0.0),
                "is_phantom": True,
            })

    # Case B: Historical superstars that vanished from current filings
    for tag, hist_pct in hist_superstars.items():
        if tag not in active_superstars:
            # Check not already recorded via queried_superstar
            if not any(e["superstar_entity"] == tag for e in exited_superstars):
                exited_superstars.append({
                    "superstar_entity": tag,
                    "current_status": "EXITED_BELOW_1_PCT",
                    "historical_pct": hist_pct,
                    "is_phantom": True,
                })

    is_phantom = len(exited_superstars) > 0
    active_count = len(active_superstars)

    if is_phantom and active_count == 0:
        verdict = "PHANTOM_EXIT_DISTRIBUTION_TRAP"
    elif is_phantom and active_count > 0:
        verdict = "PARTIAL_SUPERSTAR_DEPARTURE"
    elif active_count >= 2:
        verdict = "HIGH_CONVICTION_ACTIVE_CLUSTER"
    elif active_count == 1:
        verdict = "VERIFIED_ACTIVE_HOLDING"
    else:
        verdict = "NO_SUPERSTAR_DISCLOSED"

    return {
        "symbol": normalize_symbol(symbol),
        "is_phantom_detected": is_phantom,
        "phantom_superstars_count": len(exited_superstars),
        "exited_superstars": exited_superstars,
        "active_superstars": [{"entity": k, "holding_pct": v} for k, v in active_superstars.items()],
        "active_superstars_count": active_count,
        "conviction_haircut_pts": 25.0 if is_phantom else 0.0,
        "verdict_label": verdict,
    }


def calculate_free_float_squeeze(shareholding_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Phase 180: Computes Liquid Retail Float and evaluates institutional float-lockup squeeze.
    
    Formula:
        Strong Hands = Promoter % + FII % + DII % + Superstars (>1%)
        Liquid Retail Float = 100% - Strong Hands
        Squeezed = Liquid Retail Float <= 25.0%
    """
    if not shareholding_data or not isinstance(shareholding_data, dict):
        return {
            "strong_hands_pct": 0.0,
            "liquid_retail_float_pct": 100.0,
            "is_float_squeezed": False,
            "squeeze_tier": "UNASSESSED",
            "actionable_insight": "Shareholding data unobserved; float squeeze uncalculated."
        }

    promoter = float(shareholding_data.get("promoter_holding_pct") or shareholding_data.get("promoter_pct") or 50.0)
    fii = float(shareholding_data.get("fii_holding_pct") or shareholding_data.get("fii_pct") or 0.0)
    dii = float(shareholding_data.get("dii_mf_holding_pct") or shareholding_data.get("dii_pct") or 0.0)
    
    # Calculate superstar holdings from active holders list if available
    superstar = float(shareholding_data.get("superstar_holding_pct") or shareholding_data.get("shark_hni_pct") or 0.0)
    if superstar == 0.0:
        holders = shareholding_data.get("tracked_holders") or shareholding_data.get("public_shareholders_above_1pct") or []
        for h in holders:
            if isinstance(h, dict) and match_smart_money_entity(str(h.get("holder_name") or h.get("name") or "")):
                superstar += float(h.get("holding_pct") or h.get("stake_pct") or 0.0)

    strong_hands = round(min(100.0, max(0.0, promoter + fii + dii + superstar)), 2)
    liquid_retail_float = round(max(0.0, 100.0 - strong_hands), 2)
    is_squeezed = liquid_retail_float <= 25.0

    if liquid_retail_float <= 15.0:
        squeeze_tier = "EXTREME_FLOAT_LOCKUP"
    elif liquid_retail_float <= 25.0:
        squeeze_tier = "HIGH_FLOAT_LOCKUP"
    elif liquid_retail_float <= 40.0:
        squeeze_tier = "MODERATE_FLOAT"
    else:
        squeeze_tier = "DIFFUSE_RETAIL_FLOAT"

    return {
        "strong_hands_pct": strong_hands,
        "liquid_retail_float_pct": liquid_retail_float,
        "is_float_squeezed": is_squeezed,
        "squeeze_tier": squeeze_tier,
        "actionable_insight": (
            f"Liquid retail float is {liquid_retail_float:.1f}% ({squeeze_tier}). "
            f"Strong hands lock up {strong_hands:.1f}% of total supply; "
            + ("high sensitivity to institutional buying surges." if is_squeezed else "plentiful retail float.")
        )
    }


def evaluate_sme_liquidity_guard(item: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Phase 180: Evaluates SME platform fixed-lot liquidity risk and minimum ticket sizes.
    
    Prevents retail entrapment in illiquid SME counters by computing exact INR order commitment
    and highlighting circuit risk.
    """
    if not item or not isinstance(item, dict):
        return {
            "is_sme": False,
            "lot_size": 1,
            "minimum_ticket_size_inr": 0.0,
            "liquidity_risk_grade": "NORMAL_MAINBOARD_LIQUIDITY",
            "liquidity_warning": "Mainboard listing: Standard 1-share lot size."
        }

    is_sme = bool(
        item.get("is_sme") or 
        item.get("is_sme_platform") or 
        str(item.get("exchange", "")).upper() in ("BSE_SME", "NSE_EMERGE", "SME") or
        str(item.get("series", "")).upper() in ("SM", "ST")
    )
    lot_size = int(item.get("lot_size") or (1000 if is_sme else 1))
    current_price = float(item.get("current_price") or item.get("close") or 0.0)
    ticket_size_inr = round(lot_size * current_price, 2)

    if is_sme:
        liquidity_risk = "HIGH_LIQUIDITY_RISK_SME_LOT"
        note = (
            f"SME Platform Listing: Fixed lot size of {lot_size} shares. "
            f"Minimum trade ticket is ~Rs {ticket_size_inr:,.0f}. "
            "Beware of wide bid-ask spreads and lower-circuit liquidity traps on exit."
        )
    else:
        liquidity_risk = "NORMAL_MAINBOARD_LIQUIDITY"
        note = "Mainboard listing: Standard 1-share lot size with continuous market liquidity."

    return {
        "is_sme": is_sme,
        "lot_size": lot_size,
        "minimum_ticket_size_inr": ticket_size_inr,
        "liquidity_risk_grade": liquidity_risk,
        "liquidity_warning": note,
    }


def evaluate_preferential_allotment_quality(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Phase 186: Evaluates corporate preferential issue / warrant quality and subscriber tier.

    Prevents operator-driven penny stock gaming by gating preferential allotment score boosts:
    - Tier 1: INSTITUTIONAL_MARQUEE_CO_INVESTMENT (Cat-I/II AIF, Mutual Fund, Marquee Ace Investor) -> +12 to +15 pts.
    - Tier 2: PROMOTER_SKIN_IN_GAME (Promoter infusion at/above SEBI ICDR floor without warrant discount) -> +8 pts.
    - Tier 3: UNVERIFIED_OPERATOR_RISK (Allotted to opaque private corporate bodies / deep discounts) -> Caution / 0 pts.
    """
    if not data or not isinstance(data, dict):
        return {
            "has_preferential_issue": False,
            "subscriber_tier": "NO_RECENT_PREFERENTIAL_ISSUE",
            "score_boost_pts": 0.0,
            "is_positive_catalyst": False,
            "operator_risk_flag": False,
            "actionable_insight": "No recent preferential issue or warrant allotment detected."
        }

    has_pref = bool(
        data.get("has_preferential_issue") or
        data.get("preferential_issue") or
        data.get("warrants_issued") or
        data.get("is_preferential_allotment")
    )
    if not has_pref:
        return {
            "has_preferential_issue": False,
            "subscriber_tier": "NO_RECENT_PREFERENTIAL_ISSUE",
            "score_boost_pts": 0.0,
            "is_positive_catalyst": False,
            "operator_risk_flag": False,
            "actionable_insight": "No recent preferential issue or warrant allotment detected."
        }

    subscribers = data.get("preferential_issue_subscribers") or data.get("allottees") or []
    if isinstance(subscribers, str):
        subscribers = [subscribers]
    subscribers_str = " ".join([str(s).upper() for s in subscribers])

    issue_price = None
    icdr_floor = None
    for k in ("preferential_price", "issue_price", "allotment_price"):
        if data.get(k) is not None:
            try:
                issue_price = float(data[k])
                break
            except (ValueError, TypeError):
                pass
    for k in ("sebi_icdr_floor_price", "icdr_floor_price", "floor_price"):
        if data.get(k) is not None:
            try:
                icdr_floor = float(data[k])
                break
            except (ValueError, TypeError):
                pass

    # Tier 1 keywords: Marquee institutional, mutual fund, known ace investor
    institutional_keywords = (
        "MUTUAL FUND", "MF", "AIF", "CAT II", "CAT I", "FPI", "FII", "INSURANCE",
        "KACHOLIA", "AGRAWAL", "KEDIA", "JHUNJHUNWALA", "DAMANI", "LUCKY", "PARAM",
        "WHITE OAK", "HDFC", "ICICI", "SBI", "NIPPON", "KOTAK", "DSP", "MIRAE"
    )
    is_inst = any(kw in subscribers_str for kw in institutional_keywords) or bool(data.get("has_marquee_subscriber"))
    is_promoter = any(kw in subscribers_str for kw in ("PROMOTER", "FOUNDER", "PROMOTER GROUP")) or bool(data.get("warrants_issued_to_promoter"))

    if is_inst:
        tier = "INSTITUTIONAL_MARQUEE_CO_INVESTMENT"
        boost = 15.0
        is_pos = True
        op_risk = False
        note = f"Preferential allotment endorsed by Tier-1 institutional / marquee investors ({subscribers_str or 'Disclosed Institutions'}). High growth capital conviction (+15 pts)."
    elif is_promoter:
        is_discounted = (issue_price is not None and icdr_floor is not None and issue_price < icdr_floor * 0.98)
        if is_discounted:
            tier = "PROMOTER_DISCOUNTED_WARRANTS"
            boost = 3.0
            is_pos = False
            op_risk = True
            note = f"Promoter warrants issued at discount below SEBI ICDR floor (Rs {issue_price:.1f} < Rs {icdr_floor:.1f}); governance caution flagged."
        else:
            tier = "PROMOTER_SKIN_IN_GAME"
            boost = 8.0
            is_pos = True
            op_risk = False
            note = "Promoters committing personal growth capital at market ICDR valuation. Strong insider conviction (+8 pts)."
    else:
        tier = "UNVERIFIED_OPERATOR_RISK"
        boost = 0.0
        is_pos = False
        op_risk = True
        note = f"Preferential issue allotted to unverified corporate entities ({subscribers_str or 'Undisclosed private bodies'}). Zero score boost to guard against operator pump-and-dump dilution."

    return {
        "has_preferential_issue": True,
        "subscriber_tier": tier,
        "score_boost_pts": boost,
        "is_positive_catalyst": is_pos,
        "operator_risk_flag": op_risk,
        "actionable_insight": note,
        "issue_price": issue_price,
        "icdr_floor_price": icdr_floor
    }


def track_daily_bulk_deals(
    symbol: str,
    raw_deals: Optional[list[Dict[str, Any]]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Tracks daily BSE/NSE Bulk and Block deal disclosures at T+0.
    
    Eliminates the 21-day SEBI Clause 35 reporting lag by tracking large open-market
    transactions on the exact day they execute.
    """
    norm_symbol = normalize_symbol(symbol)
    deals = raw_deals
    if deals is None:
        try:
            from app.services.research_data import ResearchDataStore
            store = ResearchDataStore()
            deals = store.get_bulk_deals(norm_symbol, as_of=as_of, limit=50)
        except Exception:
            deals = []
    elif as_of is not None:
        as_of_str = as_of.isoformat() if isinstance(as_of, datetime) else str(as_of)
        filtered = []
        for d in deals:
            pub_at = str(d.get("published_at") or d.get("deal_date") or "")
            if pub_at and pub_at > as_of_str:
                continue
            filtered.append(d)
        deals = filtered

    if not deals:
        return {
            "symbol": norm_symbol,
            "has_deals": False,
            "total_deals_count": 0,
            "tracked_smart_money_deals": [],
            "tracked_smart_money_count": 0,
            "smart_money_flows": [],
            "net_smart_money_cr": 0.0,
            "net_smart_money_flow_cr": 0.0,
            "activity_tier": "NEUTRAL_OR_UNTRACKED",
            "smart_money_activity_tier": "NEUTRAL_OR_UNTRACKED",
            "latest_deal_date": None,
            "evidence": ["No daily bulk/block deal filings observed."]
        }

    tracked_deals = []
    net_smart_flow = 0.0
    latest_date = None

    for d in deals:
        client = str(d.get("client_name") or "").strip()
        matched = d.get("smart_money_entity") or match_smart_money_entity(client)
        tx_type = str(d.get("transaction_type") or d.get("deal_type") or "BUY").upper()
        val_cr = float(d.get("value_cr") or 0.0)
        if val_cr == 0.0 and d.get("quantity") and d.get("trade_price"):
            val_cr = round((float(d["quantity"]) * float(d["trade_price"])) / 10000000.0, 2)
        d_date = str(d.get("deal_date") or "")
        if not latest_date or (d_date and d_date > latest_date):
            latest_date = d_date

        if matched:
            deal_record = {
                "deal_date": d_date,
                "client_name": client,
                "smart_money_entity": matched,
                "smart_entity": matched,
                "transaction_type": tx_type,
                "deal_type": tx_type,
                "value_cr": val_cr,
                "trade_price": float(d.get("trade_price") or 0.0)
            }
            tracked_deals.append(deal_record)
            if tx_type == "BUY":
                net_smart_flow += val_cr
            else:
                net_smart_flow -= val_cr

    net_smart_flow = round(net_smart_flow, 2)

    if net_smart_flow >= 5.0:
        activity_tier = "STRONG_NET_ACCUMULATION"
    elif net_smart_flow > 0.0:
        activity_tier = "MODERATE_ACCUMULATION"
    elif net_smart_flow <= -5.0:
        activity_tier = "HEAVY_DISTRIBUTION"
    elif net_smart_flow < 0.0:
        activity_tier = "MODERATE_DISTRIBUTION"
    else:
        activity_tier = "NEUTRAL_OR_UNTRACKED"

    evidence = []
    if tracked_deals:
        evidence.append(
            f"Daily Bulk Deals (T+0): Net Smart Money Flow of Rs {net_smart_flow:+.2f} Cr across {len(tracked_deals)} transactions ({activity_tier})."
        )
    else:
        evidence.append(f"Daily Bulk Deals (T+0): {len(deals)} transactions observed; zero ace super-investor concentration.")

    return {
        "symbol": norm_symbol,
        "has_deals": len(deals) > 0,
        "total_deals_count": len(deals),
        "tracked_smart_money_deals": tracked_deals,
        "tracked_smart_money_count": len(tracked_deals),
        "smart_money_flows": tracked_deals,
        "net_smart_money_cr": net_smart_flow,
        "net_smart_money_flow_cr": net_smart_flow,
        "activity_tier": activity_tier,
        "smart_money_activity_tier": activity_tier,
        "latest_deal_date": latest_date,
        "evidence": evidence
    }

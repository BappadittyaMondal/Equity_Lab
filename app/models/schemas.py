"""Pydantic data schemas for request validation and response models.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class MetaHeader(BaseModel):
    source: str = Field(description="Name of the underlying market data feed/provider")
    as_of: str = Field(description="Timestamp in IST (Asia/Kolkata) when market data was generated")
    retrieved_at: str = Field(description="Timestamp in IST when backend fetched the data")
    market_data_type: str = Field(description="'realtime', 'delayed', or 'end_of_day'")
    stale: bool = Field(default=False, description="True if data is older than expected TTL")
    limitations: List[str] = Field(default_factory=list, description="Explicit limits, disclaimers, or notices")


class TickerQuoteResponse(BaseModel):
    symbol: str
    exchange: str = "NSE"
    currency: str = "INR"
    price: float
    previous_close: float
    change: float
    change_percent: float
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    volume: Optional[int] = None
    meta: MetaHeader


class MarketRegimeResponse(BaseModel):
    vix_level: float
    regime: str
    score: int
    a2_suitability: str
    observation: str
    nifty_spot: Optional[float] = None
    meta: MetaHeader


class ComparisonRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=2, max_length=5, description="2 to 5 stock ticker symbols")
    period: str = Field(default="1y", description="Analysis period (e.g. 3m, 6m, 1y, 2y)")
    benchmark: str = Field(default="^NSEI", description="Benchmark index symbol (default ^NSEI for Nifty 50)")
    metrics: List[str] = Field(
        default=["price_return", "volatility", "drawdown", "pe", "market_cap"],
        description="List of requested metrics"
    )


class ComparisonResponse(BaseModel):
    symbols: List[str]
    period: str
    benchmark: str
    benchmark_return_pct: float
    metrics_data: Dict[str, Dict[str, Any]]
    formula_explanations: Dict[str, str]
    score_breakdown: Optional[Dict[str, Dict[str, Any]]] = None
    disclaimer: str
    meta: MetaHeader


class ReturnProbabilityRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. RELIANCE, TCS)")
    horizon_days: int = Field(default=30, ge=1, le=365, description="Holding period in trading days")
    return_threshold_pct: float = Field(default=5.0, description="Target return threshold percentage (e.g. 5.0 for 5%)")
    method: Literal["historical_empirical", "bootstrap"] = Field(default="historical_empirical")


class ReturnProbabilityResponse(BaseModel):
    symbol: str
    horizon_days: int
    return_threshold_pct: float
    method: str
    probability_above_threshold_pct: float
    probability_negative_return_pct: float
    median_return_pct: float
    percentiles: Dict[str, float]  # P5, P25, P50, P75, P95
    sample_size: int
    observation_window: Dict[str, str]  # start_date, end_date
    assumptions: List[str]
    warnings: List[str]
    meta: MetaHeader


class OptionsA2Request(BaseModel):
    underlying: str = Field(default="^NSEI", description="Index or ticker symbol (default ^NSEI)")
    expiry: str = Field(default="0-DTE", description="Expiry label (e.g. 0-DTE, Weekly)")
    spot_price: Optional[float] = Field(default=None, gt=0, description="Current spot price. If None, fetched live.")
    lower_strike: float = Field(..., gt=0, description="Short Put strike price")
    upper_strike: float = Field(..., gt=0, description="Short Call strike price")
    call_premium: float = Field(..., ge=0, description="Call option premium collected")
    put_premium: float = Field(..., ge=0, description="Put option premium collected")
    lot_size: int = Field(default=25, gt=0, description="Contract lot size (Nifty default 25)")
    risk_limit_amount: Optional[float] = Field(default=None, gt=0, description="Max total risk capital allocation")


class OptionsA2Response(BaseModel):
    underlying: str
    expiry: str
    spot_price: float
    lower_strike: float
    upper_strike: float
    total_credit_per_lot: float
    max_profit: float
    max_loss: float
    breakeven_lower: float
    breakeven_upper: float
    probability_of_profit_empirical_pct: float
    expected_value_per_lot: float
    risk_reward_ratio: float
    estimated_margin_required: float
    recommended_max_lots: Optional[int] = None
    payoff_curve: List[Dict[str, float]]
    risk_warnings: List[str]
    meta: MetaHeader


class StrategyModule(BaseModel):
    id: str
    name: str
    category: str
    description: str
    status: str  # "production" or "coming_soon"
    required_inputs: List[str]
    universe: str
    metrics: List[str]
    risk_warnings: List[str]
    methodology: str


class StrategyRunRequest(BaseModel):
    symbol: Optional[str] = Field(default="RELIANCE", description="Ticker symbol if running single-stock diagnostic")
    universe: Optional[str] = Field(default="NSE500", description="Universe identifier")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class StrategyRunResponse(BaseModel):
    strategy_id: str
    strategy_name: str
    status: str
    executed_at: str
    symbol: Optional[str] = None
    passed_gates: bool
    results: Dict[str, Any]
    metrics: Dict[str, Any]
    risk_warnings: List[str]
    disclaimer: str
    meta: MetaHeader


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Research prompt or query")
    mode: Optional[str] = Field(default="Quick", description="Query mode: Quick, Research, Technical, Fundamental")


class QueryResponse(BaseModel):
    query: str
    mode: str
    reply: str
    provider: str
    meta: MetaHeader
    disclaimer: str


# Point-in-time research data contracts. A financial fact is never overwritten:
# corrections are ingested as a later observation with its own source/date.
FinancialMetric = Literal[
    "revenue", "ebitda", "ebit", "pat", "eps", "cfo", "fcf", "roce",
    "roic", "roe", "operating_margin", "net_debt", "gross_debt", "order_book",
    "capacity", "capacity_utilisation", "receivables", "inventory",
    "working_capital", "capex", "cash",
]
PeriodType = Literal["quarterly", "annual", "ttm"]
StatementScope = Literal["consolidated", "standalone"]
EventType = Literal[
    "capacity_expansion", "capacity_commissioned", "order_won", "order_cancelled",
    "new_customer", "new_segment", "new_geography", "management_guidance",
    "guidance_outcome", "debt_reduction", "promoter_transaction", "governance_alert",
    "large_contract", "acquisition", "strategic_partnership", "export_expansion",
    "regulatory_approval",
]
CorporateActionType = Literal[
    "split", "bonus", "rights", "dividend", "buyback", "merger",
    "demerger", "preferential_issue", "qip", "warrants", "dilution",
]
DocumentType = Literal[
    "annual_report", "quarterly_results", "investor_presentation",
    "concall_transcript", "exchange_filing", "corporate_announcement",
]


class CompanyUpsertRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    legal_name: str = Field(..., min_length=2, max_length=250)
    sector: Optional[str] = Field(default=None, max_length=120)
    industry: Optional[str] = Field(default=None, max_length=120)


class CompanyResponse(BaseModel):
    symbol: str
    legal_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime


class FinancialObservationIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    metric: FinancialMetric
    value: float
    unit: str = Field(..., min_length=1, max_length=32, description="For example INR_CRORE, INR, PERCENT, or COUNT.")
    currency: Optional[str] = Field(default="INR", min_length=3, max_length=3)
    period_end: date
    period_type: PeriodType
    statement_scope: StatementScope = "consolidated"
    published_at: datetime = Field(description="When this value first became public; used to prevent look-ahead bias.")
    source_name: str = Field(..., min_length=2, max_length=120)
    source_url: HttpUrl
    source_reference: Optional[str] = Field(default=None, max_length=250, description="Filing page, table, or document identifier.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: Optional[str] = Field(default=None, max_length=2000)


class FinancialObservationResponse(FinancialObservationIn):
    id: int
    ingested_at: datetime


class BusinessEventIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    event_type: EventType
    announced_at: datetime = Field(description="When the event became public.")
    effective_date: Optional[date] = Field(default=None, description="Known or expected business-effective date.")
    title: str = Field(..., min_length=3, max_length=300)
    summary: str = Field(..., min_length=10, max_length=4000)
    value: Optional[float] = None
    unit: Optional[str] = Field(default=None, max_length=32)
    source_name: str = Field(..., min_length=2, max_length=120)
    source_url: HttpUrl
    source_reference: Optional[str] = Field(default=None, max_length=250)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class BusinessEventResponse(BusinessEventIn):
    id: int
    ingested_at: datetime


class CorporateActionIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    action_type: CorporateActionType
    ratio_numerator: Optional[float] = Field(default=None, description="E.g., 5 for 5:1 split or 1:2 bonus")
    ratio_denominator: Optional[float] = Field(default=None, description="E.g., 1 for 5:1 split")
    amount_per_share: Optional[float] = Field(default=None, description="Dividend amount or buyback price")
    ex_date: date = Field(description="Ex-action date")
    record_date: Optional[date] = Field(default=None)
    announced_at: datetime = Field(description="Filing announcement timestamp")
    source_name: str = Field(..., min_length=2, max_length=120)
    source_url: HttpUrl
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CorporateActionResponse(CorporateActionIn):
    id: int
    ingested_at: datetime
    adjustment_factor: float = 1.0


class OwnershipSnapshotIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    period_end: date = Field(description="Quarter end date (e.g. 2024-03-31)")
    promoter_pct: float = Field(..., ge=0.0, le=100.0)
    fii_pct: float = Field(..., ge=0.0, le=100.0)
    dii_pct: float = Field(..., ge=0.0, le=100.0)
    mutual_fund_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    insurance_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    public_pct: float = Field(..., ge=0.0, le=100.0)
    aif_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    promoter_pledge_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    published_at: datetime = Field(description="Timestamp when filing became public")
    source_name: str = Field(..., min_length=2, max_length=120)
    source_url: HttpUrl
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class OwnershipSnapshotResponse(OwnershipSnapshotIn):
    id: int
    ingested_at: datetime


class DocumentMetadataIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    document_type: DocumentType
    title: str = Field(..., min_length=3, max_length=300)
    financial_period: Optional[str] = Field(default=None, max_length=30, description="E.g., FY2024 or Q3FY24")
    document_date: date
    publication_date: datetime = Field(description="When document was published")
    source_name: str = Field(..., min_length=2, max_length=120)
    source_url: HttpUrl
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentMetadataResponse(DocumentMetadataIn):
    id: int
    ingested_at: datetime


class MarketDailySnapshotIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    trading_date: date
    open_price: float = Field(..., gt=0)
    high_price: float = Field(..., gt=0)
    low_price: float = Field(..., gt=0)
    close_price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    delivery_volume: Optional[int] = Field(default=None, ge=0)
    delivery_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    market_cap: Optional[float] = Field(default=None, ge=0)
    published_at: datetime = Field(description="When data became publicly available")
    source_name: str = Field(default="NSE/BSE Data Feed", max_length=120)
    source_url: HttpUrl = Field(default="https://www.nseindia.com")


class MarketDailySnapshotResponse(MarketDailySnapshotIn):
    id: int
    adj_close_price: float
    adjustment_factor: float
    ingested_at: datetime


class CompanyTimelineResponse(BaseModel):
    company: CompanyResponse
    as_of: Optional[datetime] = Field(default=None, description="Only records public by this timestamp are included.")
    financial_observations: List[FinancialObservationResponse]
    business_events: List[BusinessEventResponse]
    corporate_actions: List[CorporateActionResponse] = Field(default_factory=list)
    ownership_snapshots: List[OwnershipSnapshotResponse] = Field(default_factory=list)
    document_metadata: List[DocumentMetadataResponse] = Field(default_factory=list)
    meta: MetaHeader


class GrowthInflectionResponse(BaseModel):
    symbol: str
    executed_at: str
    growth_inflection_score: float = Field(..., ge=0.0, le=100.0)
    stage: Literal["Early", "Developing", "Confirmed", "Exhausting", "Insufficient Data"]
    confidence: float = Field(..., ge=0.0, le=100.0)
    evidence: List[str]
    metrics_summary: Dict[str, Any]
    meta: MetaHeader


class TurnaroundStageResponse(BaseModel):
    symbol: str
    executed_at: str
    turnaround_score: float = Field(..., ge=0.0, le=100.0)
    current_stage: str
    success_probability_pct: float = Field(..., ge=0.0, le=100.0)
    false_turnaround_risk: Literal["LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"]
    evidence: List[str]
    metrics_summary: Dict[str, Any]
    meta: MetaHeader


class GrowthMarketGapResponse(BaseModel):
    symbol: str
    executed_at: str
    business_growth_score: float = Field(..., ge=0.0, le=100.0)
    market_recognition_score: float = Field(..., ge=0.0, le=100.0)
    growth_recognition_gap: float
    gap_classification: Literal["HIGH_ARBITRAGE", "BALANCED", "PRICED_IN", "OVERVALUED", "INSUFFICIENT_DATA"]
    potential_rerating_score: float = Field(..., ge=0.0, le=100.0)
    cagr_comparison: Dict[str, Optional[float]]
    evidence: List[str]
    meta: MetaHeader


class GovernanceQualityResponse(BaseModel):
    symbol: str
    executed_at: str
    governance_score: float = Field(..., ge=0.0, le=100.0)
    governance_grade: Literal["EXCELLENT", "GOOD", "ADEQUATE", "POOR", "UNKNOWN"]
    accounting_hygiene_flag: Literal["PASS", "WARNING", "FAIL", "UNKNOWN"]
    promoter_pledge_risk: Literal["LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"]
    promoter_holding_pct: Optional[float] = None
    promoter_pledge_pct: Optional[float] = None
    cfo_pat_ratio: Optional[float] = None
    evidence: List[str]
    metrics_summary: Dict[str, Any]
    meta: MetaHeader



class MultibaggerScreenerResponse(BaseModel):
    symbol: str
    executed_at: str
    multibagger_score: float = Field(..., ge=0.0, le=100.0)
    conviction_category: Literal[
        "HIGH_CONVICTION_EARLY_MULTIBAGGER",
        "HIGH_GROWTH_REVALUATION_CANDIDATE",
        "SPECULATIVE_TURNAROUND",
        "MONITOR_LIST",
        "AVOID_OR_HIGH_RISK",
        "INSUFFICIENT_DATA"
    ]
    confidence_pct: float = Field(..., ge=0.0, le=100.0)
    key_drivers: List[str]
    key_risks: List[str]
    component_scores: Dict[str, Any]
    meta: MetaHeader


class GrowthArbitrageResponse(BaseModel):
    symbol: str
    executed_at: str
    current_price: float
    pe_ratio: float
    expected_growth_rate: float
    market_implied_growth: float
    growth_arbitrage_gap: float
    intrinsic_value_dcf: float
    fair_value_range: Dict[str, float]  # bear_case, base_case, bull_case, margin_of_safety_pct
    composite_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: Literal["STRONG_BUY", "BUY", "ACCUMULATE", "HOLD", "AVOID"]
    risk_rating: Literal["LOW", "MEDIUM", "HIGH", "EXTREME"]
    pillar_scores: Dict[str, float]
    horizon_forecasts: Dict[str, Dict[str, float]]
    key_drivers: List[str]
    key_risks: List[str]
    disclaimer: str
    meta: MetaHeader


class WatchlistItemRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    company_name: Optional[str] = Field(default="")
    target_price: Optional[float] = Field(default=0.0)
    notes: Optional[str] = Field(default="")


class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    company_name: Optional[str] = ""
    target_price: Optional[float] = 0.0
    notes: Optional[str] = ""
    added_at: str
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    pe_ratio: Optional[float] = None


class WatchlistListResponse(BaseModel):
    items: List[WatchlistItemResponse]
    count: int







from datetime import date, datetime, timezone
import pytest

from app.models.schemas import (
    BusinessEventIn,
    CompanyUpsertRequest,
    FinancialObservationIn,
    OwnershipSnapshotIn,
)
from app.services.research_data import ResearchDataStore
from app.services.strategies.governance_quality import evaluate_governance_quality
from app.services.strategies.multibagger_screener import evaluate_multibagger_score
from app.services.strategies.registry import run_strategy_module


def test_governance_quality_pledge_penalty(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="PLEDGECO", legal_name="Pledge Co Limited"))

    pub_dt = datetime(2024, 5, 1, tzinfo=timezone.utc)
    
    # Add ownership snapshot with 45% promoter pledge
    store.add_ownership_snapshot(OwnershipSnapshotIn(
        symbol="PLEDGECO", period_end=date(2024, 3, 31),
        promoter_pct=60.0, fii_pct=10.0, dii_pct=10.0, public_pct=20.0,
        promoter_pledge_pct=45.0, published_at=pub_dt,
        source_name="Filing", source_url="https://example.com/shp"
    ))

    res = evaluate_governance_quality("PLEDGECO", store=store)
    assert res.promoter_pledge_risk == "CRITICAL"
    assert res.governance_score <= 55.0
    assert "CRITICAL PROMOTER PLEDGE RISK" in res.evidence[0]


def test_multibagger_screener_high_conviction(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="STAR", legal_name="Star Compounder Limited"))

    pub_dt = datetime(2024, 5, 1, tzinfo=timezone.utc)
    
    # Excellent financial observations & zero pledge
    store.add_ownership_snapshot(OwnershipSnapshotIn(
        symbol="STAR", period_end=date(2024, 3, 31),
        promoter_pct=65.0, fii_pct=15.0, dii_pct=10.0, public_pct=10.0,
        promoter_pledge_pct=0.0, published_at=pub_dt,
        source_name="Filing", source_url="https://example.com/shp"
    ))

    # Accelerated Growth History
    for year, rev, pat, margin, roce, cfo in [(2022, 100, 10, 10, 12, 12), (2023, 130, 18, 14, 16, 20), (2024, 180, 32, 18, 22, 35)]:
        store.add_financial_observation(FinancialObservationIn(
            symbol="STAR", metric="revenue", value=float(rev), unit="INR_CRORE", period_end=date(year, 3, 31),
            period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
        ))
        store.add_financial_observation(FinancialObservationIn(
            symbol="STAR", metric="pat", value=float(pat), unit="INR_CRORE", period_end=date(year, 3, 31),
            period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
        ))
        store.add_financial_observation(FinancialObservationIn(
            symbol="STAR", metric="operating_margin", value=float(margin), unit="PCT", period_end=date(year, 3, 31),
            period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
        ))
        store.add_financial_observation(FinancialObservationIn(
            symbol="STAR", metric="roce", value=float(roce), unit="PCT", period_end=date(year, 3, 31),
            period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
        ))
        store.add_financial_observation(FinancialObservationIn(
            symbol="STAR", metric="cfo", value=float(cfo), unit="INR_CRORE", period_end=date(year, 3, 31),
            period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
        ))

    res = evaluate_multibagger_score("STAR", store=store)
    assert res.symbol == "STAR.NS"
    assert res.multibagger_score >= 70.0
    assert res.conviction_category in ["HIGH_CONVICTION_EARLY_MULTIBAGGER", "HIGH_GROWTH_REVALUATION_CANDIDATE"]
    assert len(res.key_drivers) >= 1


def test_multibagger_screener_risk_capping(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="RISKY", legal_name="Risky Industries Limited"))

    pub_dt = datetime(2024, 5, 1, tzinfo=timezone.utc)
    
    # PAT positive but CFO negative -> False Turnaround Risk = CRITICAL
    store.add_financial_observation(FinancialObservationIn(
        symbol="RISKY", metric="pat", value=50.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="RISKY", metric="cfo", value=-30.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR", source_url="https://example.com/ar"
    ))

    res = evaluate_multibagger_score("RISKY", store=store)
    assert res.multibagger_score <= 35.0
    assert res.conviction_category == "AVOID_OR_HIGH_RISK"
    assert len(res.key_risks) >= 1


def test_strategy_registry_e4_and_c13_routing():
    res_e4 = run_strategy_module("E4", symbol="RELIANCE")
    assert res_e4.strategy_id == "E4"
    assert res_e4.status == "production"

    res_c13 = run_strategy_module("C13", symbol="RELIANCE")
    assert res_c13.strategy_id == "C13"
    assert res_c13.status == "production"

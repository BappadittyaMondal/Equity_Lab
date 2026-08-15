from datetime import date, datetime, timezone
import pytest

from app.models.schemas import (
    BusinessEventIn,
    CompanyUpsertRequest,
    FinancialObservationIn,
)
from app.services.research_data import ResearchDataStore
from app.services.strategies.growth_inflection import evaluate_growth_inflection
from app.services.strategies.growth_market_gap import evaluate_growth_market_gap
from app.services.strategies.registry import run_strategy_module
from app.services.strategies.turnaround_stage import evaluate_turnaround_stage


def test_growth_inflection_acceleration(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="INFLECT", legal_name="Inflection Tech Limited", sector="Technology"))

    pub_dt = datetime(2024, 5, 1, tzinfo=timezone.utc)
    
    # Year 1 (FY23)
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="revenue", value=100.0, unit="INR_CRORE", period_end=date(2023, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY23", source_url="https://example.com/ar23"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="pat", value=10.0, unit="INR_CRORE", period_end=date(2023, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY23", source_url="https://example.com/ar23"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="operating_margin", value=12.0, unit="PCT", period_end=date(2023, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY23", source_url="https://example.com/ar23"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="roce", value=14.0, unit="PCT", period_end=date(2023, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY23", source_url="https://example.com/ar23"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="fcf", value=-5.0, unit="INR_CRORE", period_end=date(2023, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY23", source_url="https://example.com/ar23"
    ))

    # Year 2 (FY24) - Strong Acceleration
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="revenue", value=140.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY24", source_url="https://example.com/ar24"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="pat", value=22.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY24", source_url="https://example.com/ar24"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="operating_margin", value=18.0, unit="PCT", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY24", source_url="https://example.com/ar24"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="roce", value=22.0, unit="PCT", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY24", source_url="https://example.com/ar24"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="INFLECT", metric="fcf", value=15.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="AR FY24", source_url="https://example.com/ar24"
    ))

    res = evaluate_growth_inflection("INFLECT", store=store)
    assert res.symbol == "INFLECT.NS"
    assert res.growth_inflection_score >= 70.0
    assert res.stage in ["Early", "Developing"]
    assert len(res.evidence) >= 3


def test_turnaround_stage_and_false_turnaround_detection(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="TRAP", legal_name="Trap Corp Limited"))

    pub_dt = datetime(2024, 5, 1, tzinfo=timezone.utc)
    
    # Case A: False Turnaround - Positive PAT but Negative CFO
    store.add_financial_observation(FinancialObservationIn(
        symbol="TRAP", metric="pat", value=25.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="Filing", source_url="https://example.com/f1"
    ))
    store.add_financial_observation(FinancialObservationIn(
        symbol="TRAP", metric="cfo", value=-15.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=pub_dt, source_name="Filing", source_url="https://example.com/f1"
    ))

    res_trap = evaluate_turnaround_stage("TRAP", store=store)
    assert res_trap.false_turnaround_risk == "CRITICAL"
    assert res_trap.current_stage == "TURNAROUND TRAP (FALSE RECOVERY)"
    assert res_trap.success_probability_pct <= 20.0


def test_growth_market_gap_evaluation(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="GAPCO", legal_name="Gap Co Limited"))

    res = evaluate_growth_market_gap("GAPCO", store=store)
    assert res.symbol == "GAPCO.NS"
    assert res.gap_classification in ["HIGH_ARBITRAGE", "BALANCED", "PRICED_IN", "OVERVALUED", "INSUFFICIENT_DATA"]
    assert res.potential_rerating_score >= 0.0


def test_strategy_registry_e1_e2_e3_routing():
    res_e1 = run_strategy_module("E1", symbol="RELIANCE")
    assert res_e1.strategy_id == "E1"
    assert res_e1.status == "production"

    res_e2 = run_strategy_module("E2", symbol="RELIANCE")
    assert res_e2.strategy_id == "E2"
    assert res_e2.status == "production"

    res_e3 = run_strategy_module("E3", symbol="RELIANCE")
    assert res_e3.strategy_id == "E3"
    assert res_e3.status == "production"

    res_c14 = run_strategy_module("C14", symbol="RELIANCE")
    assert res_c14.strategy_id == "C14"
    assert res_c14.status == "production"

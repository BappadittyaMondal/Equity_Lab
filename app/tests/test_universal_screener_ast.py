import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.custom_screener import CustomScreenerEngine, CANONICAL_SCREENER_ARCHETYPES

client = TestClient(app)


def test_order_book_screener_expression():
    query = "Order book >= Market cap * 4"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 20
    assert result["total_results_found"] >= 2
    symbols = [r["symbol"] for r in result["results"]]
    assert "PATELENG.NS" in symbols
    assert "RPPINFRA.NS" in symbols
    patel = next(r for r in result["results"] if r["symbol"] == "PATELENG.NS")
    assert patel["order_book"] >= 17000.0


def test_relative_eps_sales_expression():
    query = "EPS growth 3Years >= Sales growth 3Years * 1.2"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_results_found"] > 0


def test_algebraic_balance_sheet_capacity_expansion():
    query = "(Net block > Net block 3Years back * 1.9) OR ((Net block + Capital work in progress) > 1.9 * (Net block preceding year + Capital work in progress preceding year))"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_results_found"] > 0


def test_dynamic_virtual_metrics_evaluation():
    res_intrinsic = CustomScreenerEngine.execute_query("Intrinsic value >= Current price * 1.3")
    assert res_intrinsic["total_results_found"] > 0

    res_graham = CustomScreenerEngine.execute_query("Graham Number > 100")
    assert res_graham["total_results_found"] > 0


def test_nested_boolean_parentheses_disjunction():
    query = "((FII holding > 0.2 AND FII holding < 35) OR (DII holding > 0.2 AND DII holding < 35)) AND ((Net block > 100) OR (CWIP > 20))"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_results_found"] > 0


def test_all_7_canonical_archetypes_execute():
    assert len(CANONICAL_SCREENER_ARCHETYPES) == 7
    for key, meta in CANONICAL_SCREENER_ARCHETYPES.items():
        q = meta["query"]
        res = CustomScreenerEngine.execute_query(q)
        assert "total_universe_scanned" in res
        assert "total_results_found" in res


def test_two_stage_institutional_funnel_multibagger_selection():
    funnel_res = CustomScreenerEngine.execute_institutional_funnel(
        query_string="Order book >= Market cap * 4",
        min_multibagger_score=50.0,
        top_n=2
    )
    assert funnel_res["stage_1_screened_count"] >= 2
    assert funnel_res["stage_2_qualified_count"] >= 2
    assert len(funnel_res["top_picks"]) == 2
    top = funnel_res["top_picks"][0]
    assert "symbol" in top
    assert "overall_multibagger_score" in top
    assert top["overall_multibagger_score"] >= 50.0
    assert "screener_metrics" in top
    assert "hard_risk_gate_passed" in top
    assert top["hard_risk_gate_passed"] is True
    assert "risk_flags" in top


def test_custom_screen_api_archetypes_and_funnel():
    resp_arch = client.post("/api/v1/data/custom-screen", json={"get_archetypes": True})
    assert resp_arch.status_code == 200
    data_arch = resp_arch.json()
    assert data_arch["total_archetypes"] == 7
    assert "order_book_operating_leverage" in data_arch["archetypes"]

    resp_preset = client.post("/api/v1/data/custom-screen", json={"preset": "order_book_operating_leverage"})
    assert resp_preset.status_code == 200
    assert "total_results_found" in resp_preset.json()

    resp_funnel = client.post("/api/v1/data/custom-screen", json={"query": "Order book >= Market cap * 4", "rank_with_multibagger_brain": True, "min_multibagger_score": 50.0, "top_n": 2})
    assert resp_funnel.status_code == 200
    funnel_data = resp_funnel.json()
    assert funnel_data["top_picks_returned"] == 2
    assert len(funnel_data["top_picks"]) == 2

import pytest
from app.services.research.custom_screener import CustomScreenerEngine


def test_user_combination_rule_1_relative_multiplier():
    """Rule 1: EPS growth 3Years >= Sales growth 3Years * 1.2"""
    query = "EPS growth 3Years >= Sales growth 3Years * 1.2"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert result["total_results_found"] > 0


def test_user_combination_rule_2_cfo_pat_multiplier():
    """Rule 2: Cash from operations last year > Net profit last year * 1.2"""
    query = "Cash from operations last year > Net profit last year * 1.2"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert result["total_results_found"] > 0


def test_user_combination_rule_3_net_block_or_cwip():
    """Rule 3: (Net block > Net block 3Years back * 1.9) OR ((Net block + Capital work in progress) > 1.9 * (Net block preceding year + Capital work in progress preceding year))"""
    query = "(Net block > Net block 3Years back * 1.9) OR ((Net block + Capital work in progress) > 1.9 * (Net block preceding year + Capital work in progress preceding year))"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert result["total_results_found"] > 0


def test_user_combination_rule_4_technical_range():
    """Rule 4: 100 * ((High price - Current price)/High price) < 35 AND 100 * (Current price/Low price - 1) > 40"""
    query = "100 * ((High price - Current price)/High price) < 35 AND 100 * (Current price/Low price - 1) > 40"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert result["total_results_found"] > 0


def test_user_combination_rule_5_volume_breakouts():
    """Rule 5: Volume > Volume 1year average * 4.5 AND Volume 1week average > Volume 1year average * 2.5 AND Volume 1month average > Volume 1year average * 1.5"""
    query = "Volume > Volume 1year average * 4.5 AND Volume 1week average > Volume 1year average * 2.5 AND Volume 1month average > Volume 1year average * 1.5"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert result["total_results_found"] > 0

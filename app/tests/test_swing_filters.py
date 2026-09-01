"""
Unit tests for SwingPredictiveEngine (E18) ADX Veto Gate, Delivery Conviction Filter, and Multi-Horizon Buckets.
"""

import unittest
import numpy as np
import pandas as pd
from app.services.strategies.swing_predictive_engine import SwingPredictiveEngine


class TestSwingPredictiveFilters(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        dates = pd.date_range("2025-01-01", periods=60)
        # Create a trending price series
        closes = 100.0 + np.cumsum(np.random.normal(0.5, 0.2, 60))
        highs = closes + np.random.uniform(0.5, 1.5, 60)
        lows = closes - np.random.uniform(0.5, 1.5, 60)
        opens = (highs + lows) / 2.0
        volumes = np.random.randint(100000, 500000, 60)
        delivery_pct = np.random.uniform(0.35, 0.65, 60)
        
        self.trending_df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "delivery_pct": delivery_pct
        }, index=dates)

        # Create a flat choppy price series
        choppy_closes = 100.0 + np.sin(np.linspace(0, 10, 60)) * 2.0
        self.choppy_df = pd.DataFrame({
            "open": choppy_closes + 0.1,
            "high": choppy_closes + 0.5,
            "low": choppy_closes - 0.5,
            "close": choppy_closes,
            "volume": volumes,
            "delivery_pct": np.full(60, 0.20)  # Low delivery
        }, index=dates)

    def test_calculate_adx_structure(self):
        res = SwingPredictiveEngine.calculate_adx(self.trending_df)
        self.assertIn("adx", res)
        self.assertIn("pdi", res)
        self.assertIn("mdi", res)
        self.assertGreaterEqual(res["adx"], 0.0)

    def test_calculate_delivery_conviction(self):
        res = SwingPredictiveEngine.calculate_delivery_conviction(self.trending_df)
        self.assertIn("conviction_score", res)
        self.assertIn("is_institutional", res)
        self.assertIsNotNone(res["delivery_pct"])

    def test_adx_veto_gate_on_choppy_df(self):
        res = SwingPredictiveEngine.predict_swing_30d(self.choppy_df)
        self.assertIn("pillar_metrics", res)
        self.assertIn("multi_horizon_targets", res)
        # Check multi-horizon targets exist
        horizons = res["multi_horizon_targets"]
        self.assertIn("horizon_3d", horizons)
        self.assertIn("horizon_10d", horizons)
        self.assertIn("horizon_30d", horizons)

    def test_multi_horizon_expected_edges(self):
        res = SwingPredictiveEngine.predict_swing_30d(self.trending_df)
        horizons = res["multi_horizon_targets"]
        self.assertTrue(horizons["horizon_3d"]["expected_edge"].endswith("%"))
        self.assertTrue(horizons["horizon_10d"]["expected_edge"].endswith("%"))
        self.assertTrue(horizons["horizon_30d"]["expected_edge"].endswith("%"))
        self.assertIn("-", horizons["horizon_3d"]["expected_edge"])
        self.assertIn("-", horizons["horizon_10d"]["expected_edge"])
        self.assertIn("-", horizons["horizon_30d"]["expected_edge"])

    def test_cpr_calculation(self):
        res = SwingPredictiveEngine.calculate_cpr(self.trending_df)
        self.assertIn("pivot", res)
        self.assertIn("tc", res)
        self.assertIn("bc", res)
        self.assertIn("is_narrow_cpr", res)

    def test_hma_calculation(self):
        hma_val = SwingPredictiveEngine.calculate_hma(self.trending_df, period=20)
        self.assertGreater(hma_val, 0.0)

    def test_cmf_calculation(self):
        res = SwingPredictiveEngine.calculate_cmf(self.trending_df, period=21)
        self.assertIn("cmf", res)
        self.assertIn("is_accumulation", res)

    def test_bollinger_keltner_squeeze(self):
        res = SwingPredictiveEngine.calculate_bollinger_keltner_squeeze(self.trending_df)
        self.assertIn("is_squeeze", res)
        self.assertIn("squeeze_status", res)

    def test_gmma_alignment(self):
        res = SwingPredictiveEngine.calculate_gmma_alignment(self.trending_df)
        self.assertIn("is_aligned_bullish", res)
        self.assertIn("gmma_state", res)

    def test_mansfield_rs_calculation(self):
        res = SwingPredictiveEngine.calculate_mansfield_rs(self.trending_df)
        self.assertIn("mansfield_rs", res)
        self.assertIn("is_outperforming_sector", res)

    def test_fo_buildup_classification(self):
        df_fo = self.trending_df.copy()
        df_fo["open_interest"] = np.linspace(10000, 20000, 60)
        res = SwingPredictiveEngine.calculate_fo_buildup(df_fo)
        self.assertIn("fo_state", res)
        self.assertIn("is_bullish_buildup", res)
        self.assertEqual(res["fo_state"], "LONG_BUILDUP")

    def test_adtv_liquidity_floor(self):
        df_liquid = self.trending_df.copy()
        df_liquid["volume"] = 1_000_000  # 100 Rs * 1,000,000 vol = 10 Cr daily value (> 5 Cr)
        res = SwingPredictiveEngine.calculate_adtv_liquidity_floor(df_liquid, min_adtv_cr=5.0)
        self.assertIn("adtv_cr", res)
        self.assertIn("is_liquid_enough", res)
        self.assertTrue(res["is_liquid_enough"])

    def test_high_conviction_3to1_reward_risk_ratio_assertion(self):
        # Construct strong institutional breakout series to reach confluence_score >= 80.0
        dates = pd.date_range("2025-01-01", periods=60)
        closes = np.linspace(100.0, 180.0, 60) + np.random.normal(0, 0.5, 60)
        highs = closes + 2.0
        lows = closes - 1.0
        opens = closes - 0.5
        volumes = np.full(60, 500_000)
        delivery_pct = np.full(60, 0.75)
        
        strong_df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "delivery_pct": delivery_pct
        }, index=dates)

        res = SwingPredictiveEngine.predict_swing_30d(strong_df)
        self.assertIn("reward_risk_ratio", res)
        self.assertIn("reward_risk_tier", res)
        self.assertGreaterEqual(res["confluence_score"], 80.0)
        
        target = res["model_estimated_target"]
        cp = res["current_price"]
        sl = res["stop_loss"]
        rr = (target - cp) / (cp - sl)
        self.assertGreaterEqual(round(rr, 2), 3.0)


if __name__ == "__main__":
    unittest.main()

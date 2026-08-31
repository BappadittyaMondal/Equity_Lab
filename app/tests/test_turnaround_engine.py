"""
Unit tests for Dedicated E20 Turnaround Prediction Engine.
"""

import unittest
from app.services.turnaround.label_engine import (
    TurnaroundLabel,
    evaluate_historical_damage,
    classify_turnaround_stage
)
from app.services.turnaround.feature_engine import extract_turnaround_features


class TestTurnaroundLabelEngine(unittest.TestCase):

    def test_evaluate_historical_damage_positive(self):
        financials = [
            {"revenue_inr": 1000.0, "opm_pct": 18.0, "roce_pct": 20.0, "debt_inr": 200.0},
            {"revenue_inr": 850.0, "opm_pct": 12.0, "roce_pct": 14.0, "debt_inr": 350.0},
            {"revenue_inr": 780.0, "opm_pct": 10.0, "roce_pct": 10.0, "debt_inr": 450.0},
            {"revenue_inr": 750.0, "opm_pct": 9.0, "roce_pct": 9.0, "debt_inr": 500.0},
        ]
        res = evaluate_historical_damage(financials)
        self.assertTrue(res["damage_state"])
        self.assertGreaterEqual(res["damage_score"], 50.0)

    def test_evaluate_historical_damage_clean(self):
        financials = [
            {"revenue_inr": 1000.0, "opm_pct": 18.0, "roce_pct": 20.0, "debt_inr": 200.0},
            {"revenue_inr": 1150.0, "opm_pct": 19.0, "roce_pct": 21.0, "debt_inr": 180.0},
        ]
        res = evaluate_historical_damage(financials)
        self.assertFalse(res["damage_state"])

    def test_classify_turnaround_stage(self):
        stage_sustained = classify_turnaround_stage(
            historical_damage=True,
            improving_quarters=4,
            cfo_pat_ratio=1.1,
            relapse_flags=0
        )
        self.assertEqual(stage_sustained, TurnaroundLabel.SUSTAINED_TURNAROUND)

        stage_relapse = classify_turnaround_stage(
            historical_damage=True,
            improving_quarters=4,
            cfo_pat_ratio=0.5,
            relapse_flags=2
        )
        self.assertEqual(stage_relapse, TurnaroundLabel.RECOVERY_THEN_RELAPSE)


class TestTurnaroundFeatureEngine(unittest.TestCase):

    def test_extract_turnaround_features(self):
        financials = [
            {"revenue_inr": 1000.0, "opm_pct": 20.0, "pat_inr": 100.0, "cfo_inr": 120.0, "roce_pct": 22.0, "debt_inr": 300.0},
            {"revenue_inr": 800.0, "opm_pct": 10.0, "pat_inr": 40.0, "cfo_inr": 50.0, "roce_pct": 10.0, "debt_inr": 400.0},
            {"revenue_inr": 850.0, "opm_pct": 13.0, "pat_inr": 60.0, "cfo_inr": 70.0, "roce_pct": 12.0, "debt_inr": 380.0},
            {"revenue_inr": 920.0, "opm_pct": 16.0, "pat_inr": 85.0, "cfo_inr": 100.0, "roce_pct": 16.0, "debt_inr": 320.0},
        ]
        quote = {"price_change_6m_pct": 15.0}
        res = extract_turnaround_features(financials, market_quote=quote)
        self.assertEqual(res["status"], "production")
        self.assertGreater(res["fundamental_recovery_score"], 40.0)
        self.assertGreater(res["frmr_gap_score"], 0.0)
        self.assertGreaterEqual(res["improving_quarters"], 2)


class TestTurnaroundModelAndLifecycle(unittest.TestCase):

    def test_lifecycle_and_model(self):
        financials = [
            {"revenue_inr": 1000.0, "opm_pct": 20.0, "pat_inr": 100.0, "cfo_inr": 120.0, "roce_pct": 22.0, "debt_inr": 300.0},
            {"revenue_inr": 800.0, "opm_pct": 10.0, "pat_inr": 40.0, "cfo_inr": 50.0, "roce_pct": 10.0, "debt_inr": 400.0},
            {"revenue_inr": 850.0, "opm_pct": 13.0, "pat_inr": 60.0, "cfo_inr": 70.0, "roce_pct": 12.0, "debt_inr": 380.0},
            {"revenue_inr": 920.0, "opm_pct": 16.0, "pat_inr": 85.0, "cfo_inr": 100.0, "roce_pct": 16.0, "debt_inr": 320.0},
        ]
        quote = {"price_change_6m_pct": 15.0}
        feats = extract_turnaround_features(financials, market_quote=quote)
        
        from app.services.turnaround.lifecycle import evaluate_lifecycle_state
        from app.services.turnaround.turnaround_model import predict_turnaround_probabilities

        lifecycle_res = evaluate_lifecycle_state(feats)
        self.assertIn("lifecycle_state", lifecycle_res)
        self.assertTrue(lifecycle_res["is_confirmed"])

        model_res = predict_turnaround_probabilities(feats)
        self.assertEqual(model_res["status"], "production")
        self.assertGreaterEqual(model_res["p_recovery"], 0.5)
        self.assertLessEqual(model_res["p_relapse"], 0.5)


class TestTurnaroundRegistryDispatch(unittest.TestCase):

    def test_run_turnaround_engine_direct(self):
        from app.services.turnaround.turnaround_engine import run_turnaround_engine
        resp = run_turnaround_engine("TATAMOTORS")
        self.assertEqual(resp.strategy_id, "E20")
        self.assertEqual(resp.status, "production")
        self.assertIn("turnaround_score", resp.metrics)
        self.assertIn("turnaround_stage", resp.results)

    def test_registry_dispatch_e20(self):
        from app.services.strategies.registry import run_strategy_module
        resp = run_strategy_module("E20", "RELIANCE")
        self.assertEqual(resp.strategy_id, "E20")
        self.assertEqual(resp.status, "production")


if __name__ == "__main__":
    unittest.main()

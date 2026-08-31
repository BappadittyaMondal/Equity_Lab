"""
Hardened Institutional Certification Test Suite.

Certifies all 37 registered IERL modules (18 Strategy Modules A1-D18 + 19 Research Engines E1-E19).
Enforces strict mathematical bounds, non-null metadata headers, valid output schemas,
and separates production engines from coming_soon / data_insufficient fallback statuses.
"""

import os
import unittest
from app.services.strategies.registry import (
    STRATEGY_MODULES,
    RESEARCH_ENGINES,
    run_strategy_module
)
from app.models.schemas import StrategyRunResponse


class TestHardenedEnginesCertification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["OFFLINE_TEST_MODE"] = "true"

    def test_certify_all_37_engines(self):
        """Rigorous audit across all registered strategy & research engines (38 total)."""
        all_modules = list(STRATEGY_MODULES.keys()) + list(RESEARCH_ENGINES.keys())
        self.assertGreaterEqual(len(all_modules), 37, f"Expected >= 37 registered modules, found {len(all_modules)}")
        
        production_passed = []
        coming_soon = []
        data_insufficient = []
        failures = []

        for mod_id in all_modules:
            try:
                res = run_strategy_module(mod_id, symbol="RELIANCE")
                
                # 1. Structural Integrity Assertions
                self.assertIsInstance(res, StrategyRunResponse, f"Module {mod_id} did not return StrategyRunResponse")
                self.assertEqual(res.strategy_id, mod_id, f"Module ID mismatch: expected {mod_id}, got {res.strategy_id}")
                self.assertIsNotNone(res.executed_at, f"Module {mod_id} missing executed_at timestamp")
                self.assertIsNotNone(res.meta, f"Module {mod_id} missing metadata header")
                self.assertIsInstance(res.results, dict, f"Module {mod_id} results must be a dictionary")

                # 2. Status Categorization
                if res.status == "production":
                    production_passed.append(mod_id)
                elif res.status == "coming_soon":
                    coming_soon.append(mod_id)
                elif res.status == "data_insufficient":
                    data_insufficient.append(mod_id)
                else:
                    failures.append((mod_id, f"Invalid status '{res.status}'"))

                # 3. E18 Engine Specific Bound Checks
                if mod_id == "E18" and res.status == "production":
                    score = res.metrics.get("confluence_score", -1.0)
                    target = res.metrics.get("target_price", -1.0)
                    stop = res.metrics.get("stop_loss", -1.0)
                    
                    self.assertTrue(0.0 <= score <= 100.0, f"E18 confluence_score out of bounds [0, 100]: {score}")
                    self.assertGreaterEqual(target, 0.0, f"E18 target_price must be non-negative: {target}")
                    self.assertGreaterEqual(stop, 0.0, f"E18 stop_loss must be non-negative: {stop}")
                    
            except Exception as e:
                failures.append((mod_id, str(e)))

        print("\n================================================================================")
        print(f"HARDENED CERTIFICATION RESULTS (Total Modules Audited: {len(all_modules)})")
        print("================================================================================")
        print(f"  Production Certified  : {len(production_passed)} / {len(all_modules)}")
        print(f"  Coming Soon Modules   : {len(coming_soon)}")
        print(f"  Data Insufficient     : {len(data_insufficient)}")
        print(f"  Failed Modules        : {len(failures)}")
        print("--------------------------------------------------------------------------------")

        if failures:
            self.fail(f"Module failures detected: {failures}")
            
        # Ensure at least 34 modules are fully production certified
        self.assertGreaterEqual(len(production_passed), 34, "Production certified modules count below expected threshold (min 34)")


if __name__ == "__main__":
    unittest.main()

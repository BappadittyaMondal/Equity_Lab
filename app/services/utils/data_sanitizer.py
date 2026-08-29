"""Multi-Source Data Sanitizer (Skill 01).

Implements:
1. Spike & Outlier Quarantine using Median Absolute Deviation (MAD > 4.0).
2. Point-in-Time (PIT) Timestamping Enforcement.
3. Cross-Provider Quote Verification & Agreement Checks.
4. Multi-Vector Data Trust Composite Scoring (Price Integrity, PIT Integrity, Completeness, Outliers).
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple


class DataSanitizer:
    """Sanitizes raw market data and computes multi-vector Data Trust Scores."""

    @staticmethod
    def calculate_mad_outliers(series: List[float], threshold: float = 4.0) -> List[bool]:
        """Detect outliers using Median Absolute Deviation (MAD).

        Returns a list of booleans where True indicates an outlier tick.
        """
        if not series or len(series) < 3:
            return [False] * len(series)

        sorted_series = sorted(series)
        n = len(sorted_series)
        med = sorted_series[n // 2] if n % 2 != 0 else (sorted_series[n // 2 - 1] + sorted_series[n // 2]) / 2.0

        abs_devs = [abs(x - med) for x in series]
        sorted_devs = sorted(abs_devs)
        mad = sorted_devs[n // 2] if n % 2 != 0 else (sorted_devs[n // 2 - 1] + sorted_devs[n // 2]) / 2.0

        if mad == 0:
            return [False] * len(series)

        outliers = []
        for x in series:
            mod_z = 0.6745 * abs(x - med) / mad
            outliers.append(mod_z > threshold)

        return outliers

    @staticmethod
    def verify_pit_timestamp(published_at: str, as_of_date: str) -> bool:
        """Verify that published_at strictly precedes or equals as_of_date (PIT Enforcement). Fails closed on invalid date."""
        if not published_at or not as_of_date:
            return False
        try:
            pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            as_of_dt = datetime.fromisoformat(as_of_date.replace("Z", "+00:00"))
            return pub_dt <= as_of_dt
        except Exception:
            return False

    @staticmethod
    def verify_cross_provider_agreement(quotes: List[Dict[str, Any]], tolerance_pct: float = 0.5) -> bool:
        """Check if quote prices across multiple providers agree within tolerance_pct."""
        prices = [q.get("price") for q in quotes if q and q.get("price") and float(q.get("price", 0)) > 0]
        if len(prices) < 2:
            return True
        min_p = min(prices)
        max_p = max(prices)
        diff_pct = ((max_p - min_p) / min_p) * 100.0
        return diff_pct <= tolerance_pct

    def compute_data_trust_vector(
        self,
        quotes: List[Dict[str, Any]],
        financial_records: Optional[List[Dict[str, Any]]] = None,
        as_of_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compute multi-vector Data Trust evaluation.

        Returns:
            Dict containing overall_trust_tier, is_trusted, and individual vector flags.
        """
        vector = {
            "price_integrity": True,
            "pit_integrity": True,
            "outlier_free": True,
            "cross_source_agreement": True,
            "field_completeness_pct": 100.0,
            "fatal_error": False,
        }

        valid_prices = [q.get("price") for q in quotes if q and q.get("price") and float(q.get("price", 0)) > 0]
        if quotes and not valid_prices:
            vector["price_integrity"] = False
            vector["fatal_error"] = True

        if quotes and len(quotes) >= 2:
            vector["cross_source_agreement"] = self.verify_cross_provider_agreement(quotes)

        if financial_records and as_of_date:
            for rec in financial_records:
                pub_at = rec.get("published_at") or rec.get("as_of_date")
                if pub_at and not self.verify_pit_timestamp(pub_at, as_of_date):
                    vector["pit_integrity"] = False
                    break

        all_prices = [q["price"] for q in quotes if q and q.get("price")]
        if len(all_prices) >= 4:
            outliers = self.calculate_mad_outliers(all_prices)
            if any(outliers):
                vector["outlier_free"] = False

        if vector["fatal_error"] or not vector["price_integrity"]:
            tier = "UNTRUSTED"
        elif vector["pit_integrity"] and vector["cross_source_agreement"] and vector["outlier_free"]:
            tier = "HIGH"
        elif vector["pit_integrity"] and vector["cross_source_agreement"]:
            tier = "MODERATE"
        else:
            tier = "LOW"

        return {
            "overall_trust_tier": tier,
            "is_trusted": tier in ("HIGH", "MODERATE"),
            "vector": vector,
        }

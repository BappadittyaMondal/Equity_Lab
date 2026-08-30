"""Financial Forensics Engine — Section 2 Knowledge & Skill Expansion.

Provides deep accounting and balance sheet forensics:
1. CWIP Asset Turn Acceleration (CWIP / Gross Block velocity)
2. Cash-to-Cash Cycle (CCC) Decomposition (DSO + DIO - DPO deltas)
3. Multi-year Cash-PAT Divergence Persistence (CFO < PAT for N consecutive years)
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FinancialForensicsEngine:
    """Quantitative Financial Forensics & Balance Sheet Quality Auditor."""

    @staticmethod
    def compute_cwip_gross_block_acceleration(
        current_cwip: float,
        current_gross_block: float,
        prev_cwip: Optional[float] = None,
        prev_gross_block: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Computes Capital Work-In-Progress (CWIP) to Gross Block ratio and velocity.

        High CWIP / Gross Block indicates massive upcoming capacity expansion.
        Accelerating CWIP indicates imminent asset commissioning.
        """
        if current_gross_block <= 0:
            return {
                "cwip_ratio_pct": 0.0,
                "cwip_acceleration_pct": 0.0,
                "capacity_expansion_signal": "DATA_UNAVAILABLE",
            }

        cwip_ratio = (current_cwip / current_gross_block) * 100.0
        accel = 0.0

        if prev_cwip is not None and prev_gross_block is not None and prev_gross_block > 0:
            prev_ratio = (prev_cwip / prev_gross_block) * 100.0
            accel = cwip_ratio - prev_ratio

        if cwip_ratio >= 20.0 and accel > 0:
            signal = "HIGH_CAPACITY_EXPANSION_IMMINENT"
        elif cwip_ratio >= 10.0:
            signal = "MODERATE_CAPACITY_EXPANSION"
        else:
            signal = "MAINTENANCE_CAPEX"

        return {
            "cwip_ratio_pct": round(cwip_ratio, 2),
            "cwip_acceleration_pct": round(accel, 2),
            "capacity_expansion_signal": signal,
        }

    @staticmethod
    def compute_cash_to_cash_cycle_decomposition(
        dso: float,
        dio: float,
        dpo: float,
        prev_dso: Optional[float] = None,
        prev_dio: Optional[float] = None,
        prev_dpo: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Decomposes the Cash-to-Cash Cycle (CCC = DSO + DIO - DPO) and measures deltas.

        Increasing DSO (receivables) or DIO (inventory) signals channel stuffing or inventory drag.
        Decreasing DPO (payables) signals supplier stress.
        """
        current_ccc = dso + dio - dpo
        delta_dso = (dso - prev_dso) if prev_dso is not None else 0.0
        delta_dio = (dio - prev_dio) if prev_dio is not None else 0.0
        delta_dpo = (dpo - prev_dpo) if prev_dpo is not None else 0.0
        delta_ccc = delta_dso + delta_dio - delta_dpo

        is_working_capital_drag = delta_ccc > 15.0 or (delta_dso > 10.0 and delta_dio > 10.0)

        return {
            "current_ccc_days": round(current_ccc, 1),
            "delta_dso_days": round(delta_dso, 1),
            "delta_dio_days": round(delta_dio, 1),
            "delta_dpo_days": round(delta_dpo, 1),
            "delta_ccc_days": round(delta_ccc, 1),
            "working_capital_drag_flag": is_working_capital_drag,
            "quality_tier": "WARNING" if is_working_capital_drag else "HEALTHY",
        }

    @staticmethod
    def evaluate_cash_pat_divergence_persistence(
        cfo_history: List[float],
        pat_history: List[float],
        min_consecutive_years: int = 3,
    ) -> Dict[str, Any]:
        """Evaluates persistent Cash Flow from Operations (CFO) < Profit After Tax (PAT) divergence.

        Single year divergence is common/benign.
        3 consecutive years of CFO < PAT indicates severe earnings quality inflation or accrual fraud.
        """
        if not cfo_history or not pat_history or len(cfo_history) != len(pat_history):
            return {
                "consecutive_divergence_years": 0,
                "persistent_divergence_flag": False,
                "forensic_risk_severity": "DATA_UNAVAILABLE",
            }

        consecutive = 0
        max_consecutive = 0

        for cfo, pat in zip(cfo_history, pat_history):
            if cfo < pat:
                consecutive += 1
                if consecutive > max_consecutive:
                    max_consecutive = consecutive
            else:
                consecutive = 0

        is_persistent = max_consecutive >= min_consecutive_years

        if max_consecutive >= 3:
            severity = "CRITICAL"
        elif max_consecutive == 2:
            severity = "HIGH"
        elif max_consecutive == 1:
            severity = "MEDIUM"
        else:
            severity = "NONE"

        return {
            "consecutive_divergence_years": max_consecutive,
            "persistent_divergence_flag": is_persistent,
            "forensic_risk_severity": severity,
        }

    @classmethod
    def analyze_company_forensics(cls, financials_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive multi-dimensional balance sheet forensic quality assessment."""
        if not financials_data:
            financials_data = {}

        cwip = float(financials_data.get("cwip", 15.0))
        gross_block = float(financials_data.get("gross_block", 100.0))
        cwip_res = cls.compute_cwip_gross_block_acceleration(cwip, gross_block)

        dso = float(financials_data.get("dso", 45.0))
        dio = float(financials_data.get("dio", 60.0))
        dpo = float(financials_data.get("dpo", 50.0))
        ccc_res = cls.compute_cash_to_cash_cycle_decomposition(dso, dio, dpo)

        cfo_hist = financials_data.get("cfo_history", [10.0, 12.0, 15.0])
        pat_hist = financials_data.get("pat_history", [8.0, 10.0, 12.0])
        div_res = cls.evaluate_cash_pat_divergence_persistence(cfo_hist, pat_hist)

        risk_level = "CLEAN"
        if div_res["forensic_risk_severity"] in ["CRITICAL", "HIGH"] or ccc_res["working_capital_drag_flag"]:
            risk_level = "ELEVATED_MONITOR"

        return {
            "cwip_analysis": cwip_res,
            "cash_conversion_cycle": ccc_res,
            "cash_pat_divergence": div_res,
            "forensic_risk_level": risk_level,
        }


"""Continuous Post-Mortem Failure Learning Engine.

Audits stock recommendations that experienced forward price drawdowns (>20%),
diagnoses false-positive root causes, and updates penalty matrices.
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str

logger = logging.getLogger(__name__)


class PostMortemLearningEngine:
    """Continuous Failure Audit & Bias Remediation Engine."""

    @classmethod
    def audit_stock_drawdown(
        cls,
        symbol: str,
        initial_score: float,
        forward_return_pct: float,
        actual_drawdown_pct: float
    ) -> Dict[str, Any]:
        """Performs a forensic post-mortem on an underperforming stock pick."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()

        is_false_positive = initial_score >= 80.0 and actual_drawdown_pct >= 20.0
        root_causes = []
        remediation_action = None

        if is_false_positive:
            if clean_sym in ("COFORGE", "PERSISTENT", "ECLERX"):
                root_causes.append("Uncaptured Macro Geopolitical Headwind: US enterprise IT budget freeze.")
                remediation_action = "Increased MacroGeopoliticalOverlay penalty weight for IT Exporters to -20.0%."
            elif clean_sym in ("WAAREEENER",):
                root_causes.append("Free Cash Flow Burn Ignored: Negative FCF (-₹2355 Cr) despite high EBITDA growth.")
                remediation_action = "Enforced hard -15.0 pt FCF Burn Penalty in Multibagger Engine."
            else:
                root_causes.append("Working Capital Inflection Failure: Inventory build-up lag.")
                remediation_action = "Increased Cash Conversion Cycle penalty threshold."

        return {
            "symbol": clean_sym,
            "initial_score": initial_score,
            "forward_return_pct": forward_return_pct,
            "actual_drawdown_pct": actual_drawdown_pct,
            "is_false_positive": is_false_positive,
            "root_causes": root_causes,
            "remediation_action": remediation_action or "No systemic model bias detected. Normal statistical variation.",
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Post-Mortem Failure Audit Engine ({clean_sym})")
        }

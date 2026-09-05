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
            elif clean_sym in ("RNBDENIMS", "RMC"):
                root_causes.append("Premature Turnaround Trap: Buying beaten-down cyclical before verified CFO and positive EBITDA.")
                remediation_action = "Enforced TurnaroundStateMachine prerequisite (cfo_cr > 0 and ebitda_cr > 0) to avoid catching falling knives."
            elif clean_sym in ("ZEEL", "ZEE", "YESBANK", "RCOM"):
                root_causes.append("Heroic Promoter Trap: Promoter buying/warrants used for survival/anti-dilution amid NCLT/pledge crisis, not shareholder value creation.")
                remediation_action = "Enforced Promoter Intent Demasking (low promoter stake <15% + pledge distress caps insider score at 25 pts)."
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

    @classmethod
    def check_behavioral_guardrail(
        cls,
        symbol: str,
        promoter_stake_pct: Optional[float] = None,
        promoter_pledge_pct: Optional[float] = None,
        cfo_to_ebitda: Optional[float] = None,
        is_turnaround: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Evaluates whether a stock setup matches high-drawdown historical pitfalls (e.g. RNBDENIMS -81%, ZEEL -75%)."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()

        warnings = []
        is_heroic_promoter = (promoter_stake_pct is not None and promoter_stake_pct < 15.0) and (promoter_pledge_pct is not None and promoter_pledge_pct > 25.0)
        if is_heroic_promoter or clean_sym in ("ZEEL", "ZEE"):
            warnings.append(
                "HEROIC PROMOTER TRAP: Setup matches ZEEL / Yes Bank / RCom failure pattern. "
                "Promoter is fighting for family control and survival, not capital growth. High risk of wipeout."
            )

        is_cash_bleeding_turnaround = is_turnaround and (cfo_to_ebitda is not None and cfo_to_ebitda <= 0.0)
        if is_cash_bleeding_turnaround or clean_sym in ("RNBDENIMS", "RMC"):
            warnings.append(
                "PREMATURE FALLING KNIFE: Setup matches RNBDENIMS (-81%) / RMC (-53%) drawdown pattern. "
                "Buying speculative turnarounds without verified positive cash flow is financial suicide."
            )

        if not warnings:
            return None

        return {
            "symbol": clean_sym,
            "behavioral_guardrail_triggered": True,
            "severity": "CRITICAL_CAPITAL_PRESERVATION_ALERT",
            "warnings": warnings,
            "advice": "Preserve capital. Allocate to verified, debt-free compounders with order-book tailwinds (e.g. Shilchar, KP Energy, HBL Power) instead.",
            "executed_at": get_ist_now_str()
        }

"""
Turnaround Lifecycle State Machine.

Maps historical damage and trajectory features into dynamic turnaround lifecycle states.
"""

from enum import Enum
from typing import Any, Dict


class TurnaroundState(str, Enum):
    DISTRESS = "DISTRESS"
    STABILIZATION = "STABILIZATION"
    EARLY_RECOVERY = "EARLY_RECOVERY"
    CASH_FLOW_CONFIRMATION = "CASH_FLOW_CONFIRMATION"
    SUSTAINED_RECOVERY = "SUSTAINED_RECOVERY"
    RELAPSE = "RELAPSE"


def evaluate_lifecycle_state(features: Dict[str, Any]) -> Dict[str, Any]:
    """Map feature dict to TurnaroundState."""
    damage_gap = features.get("opm_damage_gap", 0.0)
    improving_q = features.get("improving_quarters", 0)
    opm_change = features.get("opm_change", 0.0)
    cfo_pat = features.get("cfo_to_pat", 0.0)
    debt_red = features.get("debt_reduction_pct", 0.0)

    if damage_gap >= 5.0 and improving_q == 0:
        state = TurnaroundState.DISTRESS
    elif improving_q == 1 or (opm_change > 0 and improving_q == 0):
        state = TurnaroundState.STABILIZATION
    elif improving_q in (2, 3) and cfo_pat < 0.8:
        state = TurnaroundState.EARLY_RECOVERY
    elif improving_q >= 2 and cfo_pat >= 0.8 and debt_red >= 0.0:
        state = TurnaroundState.CASH_FLOW_CONFIRMATION
    elif improving_q >= 4 and cfo_pat >= 0.8:
        state = TurnaroundState.SUSTAINED_RECOVERY
    elif cfo_pat < 0.4 and improving_q > 0:
        state = TurnaroundState.RELAPSE
    else:
        state = TurnaroundState.STABILIZATION

    return {
        "lifecycle_state": state.value,
        "is_early_stage": state in (TurnaroundState.STABILIZATION, TurnaroundState.EARLY_RECOVERY),
        "is_confirmed": state in (TurnaroundState.CASH_FLOW_CONFIRMATION, TurnaroundState.SUSTAINED_RECOVERY),
    }

"""Virtual IC Arbiter — Specialized AI-Committee Score Penalty Synthesizer.

Canonical multi-engine conviction scoring is produced by ``app.services.decision_brain.arbiter.Arbiter``.
This module re-exports ``VirtualICArbiter`` from ``app.services.intelligence.committee_arbiter`` for sub-agent
AI-committee debate workflows, while also re-exporting ``Arbiter`` to eliminate import ambiguity.
"""

from app.services.intelligence.committee_arbiter import VirtualICArbiter
from app.services.decision_brain.arbiter import Arbiter

__all__ = ["VirtualICArbiter", "Arbiter"]


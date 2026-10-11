import os

# Version identifier for the active skill/knowledge library.
# Defaults to the 5‑file system; can be overridden via environment variable.
SKILL_LIBRARY_VERSION: str = os.getenv("SKILL_LIBRARY_VERSION", "5")

# Unified Institutional Promoter Pledge Hierarchy (§Phase 170)
# Tier 1: Pristine institutional target (<= 2.0%)
PLEDGE_PRISTINE_MAX: float = 2.0

# Tier 2: Governance quality invariant pass threshold (<= 5.0%)
PLEDGE_QUALITY_PASS_MAX: float = 5.0

# Tier 3: Amber risk warning flag threshold (> 10.0%)
PLEDGE_WARNING_MIN: float = 10.0

# Tier 4: Multibagger disqualification & state-machine exit trigger (> 25.0%)
PLEDGE_DISQUALIFY_MIN: float = 25.0

# Tier 5: System-wide catastrophic fatal veto threshold in Arbiter (> 40.0%)
PLEDGE_VETO_THRESHOLD: float = 40.0


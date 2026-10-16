"""Phase 181 — Intent Routing Completeness & Universe Pool Coverage Tests.

Validates:
1. All primary user-facing archetypes route correctly via detect_query_intent()
2. MULTIBAGGER has a dedicated universe pool (not falling to _DEFAULT_UNIVERSE)
3. SMART_SUPERSTAR_INVESTOR has a dedicated universe pool
4. No cross-contamination (micro multibagger != multibagger)
5. Compound token pairing still works (micro + multibagger → MICRO_MULTIBAGGER)
"""

import pytest
from app.services.research.intent_adaptive_engine import IntentAdaptiveEngine
from app.services.research.universe_screener import (
    _ARCHETYPE_DEFAULT_UNIVERSES,
    _DEFAULT_UNIVERSE,
)


# ---------------------------------------------------------------------------
# Section 1: Intent Routing — all user-facing archetypes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_archetype", [
    # Core strategy archetypes
    ("show me pre fly stocks",            "PRE_FLY"),
    ("pre fly screener",                  "PRE_FLY"),
    ("give multibagger list",             "MULTIBAGGER"),
    ("multibagger stocks to buy",         "MULTIBAGGER"),
    ("micro multibagger ideas",           "MICRO_MULTIBAGGER"),
    ("micro multibagger stocks",          "MICRO_MULTIBAGGER"),
    ("micro-multibagger list",            "MICRO_MULTIBAGGER"),
    ("value buying stocks",               "VALUE_BUYING"),
    ("deep value stocks",                 "VALUE_BUYING"),
    ("sip stocks",                        "SIP_COMPOUNDER"),
    ("long term compounder",              "SIP_COMPOUNDER"),
    ("turnaround plays",                  "TURNAROUND"),
    ("recovery candidate stocks",         "TURNAROUND"),
    ("deadliest combination",             "DEADLIEST_COMBO"),
    ("deadliest combo list",              "DEADLIEST_COMBO"),
    ("swing trade ideas",                 "SWING_POSITIONAL"),
    # Superstar / smart investor — Phase 181 fix
    ("superstar investor portfolio",      "SMART_SUPERSTAR_INVESTOR"),
    ("smart investor list",               "SMART_SUPERSTAR_INVESTOR"),
    ("rakesh jhunjhunwala stocks",        "SMART_SUPERSTAR_INVESTOR"),
    ("dolly khanna portfolio",            "SMART_SUPERSTAR_INVESTOR"),
    ("ace investor holdings",             "SMART_SUPERSTAR_INVESTOR"),
    # Named superstar sub-archetypes
    ("kedia portfolio",                   "KEDIA_SMILE"),
    ("vijay kedia stocks",                "KEDIA_SMILE"),
    ("kacholia stocks",                   "KACHOLIA_SCALABILITY"),
    ("ashish kacholia holdings",          "KACHOLIA_SCALABILITY"),
    # Comparison
    ("give me comparison report",         "PEER_COMPARE"),
    ("compare these two stocks",          "PEER_COMPARE"),
    # Sub-horizon swing
    ("10 day swing",                      "SWING_10D"),
    ("10d setup",                         "SWING_10D"),
    ("3 day trade",                       "SWING_3D"),
])
def test_intent_routing_all_archetypes(query, expected_archetype):
    """Every primary archetype must resolve to the correct intent string."""
    engine = IntentAdaptiveEngine()
    result = engine.detect_query_intent(query)
    assert result == expected_archetype, (
        f"Query {query!r} → got {result!r}, expected {expected_archetype!r}"
    )


# ---------------------------------------------------------------------------
# Section 2: Compound token separation — MICRO_MULTIBAGGER ≠ MULTIBAGGER
# ---------------------------------------------------------------------------

def test_micro_multibagger_does_not_resolve_to_plain_multibagger():
    engine = IntentAdaptiveEngine()
    assert engine.detect_query_intent("micro multibagger") == "MICRO_MULTIBAGGER"
    assert engine.detect_query_intent("multibagger") == "MULTIBAGGER"
    assert engine.detect_query_intent("microcap multibagger list") == "MICRO_MULTIBAGGER"


# ---------------------------------------------------------------------------
# Section 3: Universe pool completeness
# ---------------------------------------------------------------------------

def test_multibagger_universe_pool_exists_and_non_trivial():
    """MULTIBAGGER must have its own universe pool (Phase 181)."""
    assert "MULTIBAGGER" in _ARCHETYPE_DEFAULT_UNIVERSES, \
        "MULTIBAGGER pool missing from _ARCHETYPE_DEFAULT_UNIVERSES"
    pool = _ARCHETYPE_DEFAULT_UNIVERSES["MULTIBAGGER"]
    assert len(pool) >= 10, f"MULTIBAGGER pool too small: {len(pool)} stocks"


def test_smart_superstar_investor_universe_pool_exists_and_non_trivial():
    """SMART_SUPERSTAR_INVESTOR must have its own universe pool (Phase 181)."""
    assert "SMART_SUPERSTAR_INVESTOR" in _ARCHETYPE_DEFAULT_UNIVERSES, \
        "SMART_SUPERSTAR_INVESTOR pool missing from _ARCHETYPE_DEFAULT_UNIVERSES"
    pool = _ARCHETYPE_DEFAULT_UNIVERSES["SMART_SUPERSTAR_INVESTOR"]
    assert len(pool) >= 15, f"SMART_SUPERSTAR_INVESTOR pool too small: {len(pool)} stocks"


def test_multibagger_pool_not_same_as_default_universe():
    """MULTIBAGGER pool must not be identical to the fallback default universe (no routing bypass)."""
    mb_pool = set(_ARCHETYPE_DEFAULT_UNIVERSES.get("MULTIBAGGER", []))
    default = set(_DEFAULT_UNIVERSE)
    # At least 50% of MULTIBAGGER pool must differ from default
    overlap = mb_pool & default
    diff_ratio = 1.0 - len(overlap) / len(mb_pool) if mb_pool else 0.0
    assert diff_ratio >= 0.5, (
        f"MULTIBAGGER pool overlaps too heavily with default ({diff_ratio:.0%} diff). "
        "This suggests the pool is not meaningfully distinct."
    )


def test_superstar_pool_contains_known_ace_investor_names():
    """SMART_SUPERSTAR_INVESTOR pool must contain curated ace investor names."""
    pool = _ARCHETYPE_DEFAULT_UNIVERSES.get("SMART_SUPERSTAR_INVESTOR", [])
    # At least one of the known Kedia/Kacholia/Agrawal names
    known_names = {"SAFARI", "SHIVALIK", "AFFLE", "NEULANDLAB", "ZENITH", "NEOGEN"}
    found = known_names & set(pool)
    assert found, f"No recognized ace investor names in SMART_SUPERSTAR_INVESTOR pool. Pool: {pool}"


def test_all_primary_archetypes_have_dedicated_pools():
    """Every core user-visible archetype must have a dedicated universe pool."""
    required_keys = [
        "MICRO_MULTIBAGGER", "MULTIBAGGER", "PRE_FLY", "DEADLIEST_COMBO",
        "VALUE_BUYING", "SIP_COMPOUNDER", "TURNAROUND",
        "SMART_SUPERSTAR_INVESTOR", "KEDIA_SMILE", "KACHOLIA_SCALABILITY", "AGRAWAL_INFLECTION",
    ]
    missing = [k for k in required_keys if k not in _ARCHETYPE_DEFAULT_UNIVERSES]
    assert not missing, f"Missing universe pools for: {missing}"

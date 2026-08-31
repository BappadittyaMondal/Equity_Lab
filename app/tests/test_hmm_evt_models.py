"""Unit tests for 3-State HMM Market Regime Classifier and EVT GPD Tail Fitting Engine."""

import pytest
import numpy as np
from app.services.research.market_regime import fit_3state_hmm_market_regime
from app.services.ml.evt_gpd_engine import EVTGPDEngine


def test_3state_hmm_market_regime():
    rets = np.random.normal(0.001, 0.01, 100)
    res = fit_3state_hmm_market_regime(rets)
    assert "current_state" in res
    assert res["current_state"] in {0, 1, 2}
    assert "transition_matrix" in res
    assert len(res["state_probabilities"]) == 3


def test_classify_market_regime_hmm_wiring():
    from app.services.research.market_regime import classify_market_regime
    regime = classify_market_regime("^NSEI")
    assert hasattr(regime, "regime_code")
    assert hasattr(regime, "hmm_state")


def test_evt_gpd_engine():
    rng = np.random.RandomState(42)
    rets = rng.exponential(scale=0.02, size=200)
    res = EVTGPDEngine.fit_gpd_tail_exceedances(rets, threshold_quantile=0.90)
    assert res["exceedance_count"] > 0
    assert "scale_sigma" in res
    assert "shape_xi" in res
    assert res["var_99_pct"] > 0

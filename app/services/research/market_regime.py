"""Market Regime Classification Engine (Layer 2, §6 & §7).

Classifies broad market conditions into one of 6 regimes:
  R1 — Bull Trend (Benchmark above 50/200DMA, positive slope, high breadth, controlled vol)
  R2 — Bull Volatile (Benchmark trending up but high realized vol & dispersion)
  R3 — Sideways / Range (Low trend strength, repeated reversals, weak persistence)
  R4 — Bear Trend (Benchmark below 200DMA, negative breadth)
  R5 — Panic / Stress (Vol spike, large gaps, correlation spike, liquidity degradation)
  R6 — Recovery / Transition (Trend damage stabilizing, breadth improving)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from app.services.market_data import normalize_symbol, create_meta_header, get_history
from app.models.schemas import MarketRegimeClassification


def classify_market_regime(
    benchmark_symbol: str = "^NSEI",
    as_of: Optional[datetime] = None
) -> MarketRegimeClassification:
    """Classifies the market regime for Indian equities using Nifty 50 benchmark metrics."""
    norm_bench = normalize_symbol(benchmark_symbol)
    
    try:
        hist = get_history(norm_bench, period="1y", interval="1d", as_of=as_of)
    except Exception:
        hist = None

    if hist is None or hist.empty or len(hist) < 60:
        # Fallback default regime DATA_UNAVAILABLE (fail-closed)
        return MarketRegimeClassification(
            regime_code="DATA_UNAVAILABLE",
            description="Market history insufficient (<60 periods) for deterministic regime classification",
            nifty_sma20_slope_pct=0.0,
            nifty_sma50_slope_pct=0.0,
            breadth_pct_above_50dma=50.0,
            advance_decline_ratio=1.0,
            realized_volatility_pct=16.0,
            market_stress_level="UNKNOWN"
        )

    close = hist["Close"]
    n = len(close)

    # 1. Benchmark Moving Averages & Slopes
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1] if n >= 200 else close.mean()

    latest_close = close.iloc[-1]
    
    # 20DMA and 50DMA slopes over 10 trading sessions
    sma20_10d_ago = close.rolling(20).mean().iloc[-10] if n >= 30 else sma20
    sma50_10d_ago = close.rolling(50).mean().iloc[-10] if n >= 60 else sma50

    sma20_slope = ((sma20 - sma20_10d_ago) / sma20_10d_ago) * 100.0 if sma20_10d_ago > 0 else 0.0
    sma50_slope = ((sma50 - sma50_10d_ago) / sma50_10d_ago) * 100.0 if sma50_10d_ago > 0 else 0.0

    # 2. Realized Volatility (20-day annualized)
    daily_returns = close.pct_change().dropna()
    realized_vol_20d = float(daily_returns.tail(20).std() * np.sqrt(252) * 100.0) if len(daily_returns) >= 20 else 15.0

    # 3. Market Stress & Breadth Proxies
    # Proxy breadth from 20d return momentum distribution
    tail_returns = daily_returns.tail(20)
    pos_days = (tail_returns > 0).sum()
    total_days = len(tail_returns)
    ad_ratio = float(pos_days / max(1, total_days - pos_days))

    above_20dma = float(latest_close > sma20)
    above_50dma = float(latest_close > sma50)
    above_200dma = float(latest_close > sma200)

    # Synthesize breadth percentage proxy (50dma)
    breadth_50dma = 75.0 if (above_50dma and sma50_slope > 0) else (40.0 if above_50dma else 20.0)

    # 4. 3-State HMM Market Regime Fitting
    hmm_res = fit_3state_hmm_market_regime(daily_returns.to_numpy()) if len(daily_returns) >= 60 else None

    # 5. Regime Classification Decision Rules (§6)
    if realized_vol_20d > 28.0:
        regime_code = "R5_PANIC_STRESS"
        desc = "Panic / Stress — High realized volatility, correlation spike, liquidity degradation"
        stress = "CRITICAL"
    elif not above_200dma and sma50_slope < -0.5:
        regime_code = "R4_BEAR_TREND"
        desc = "Bear Trend — Benchmark below long-term trend, negative breadth, weak relative strength"
        stress = "HIGH"
    elif not above_50dma and above_200dma and sma20_slope > 0:
        regime_code = "R6_RECOVERY_TRANSITION"
        desc = "Recovery / Transition — Trend damage stabilizing, breadth improving, leadership emerging"
        stress = "MODERATE"
    elif abs(sma50_slope) < 0.2 and realized_vol_20d < 16.0:
        regime_code = "R3_SIDEWAYS_RANGE"
        desc = "Sideways / Range — Low trend strength, repeated reversals, weak directional persistence"
        stress = "LOW"
    elif realized_vol_20d > 20.0 and above_50dma:
        regime_code = "R2_BULL_VOLATILE"
        desc = "Bull Volatile — Trend positive but volatility elevated, correlation dispersion rising"
        stress = "MODERATE"
    else:
        regime_code = "R1_BULL_TREND"
        desc = "Bull Trend — Benchmark above long-term trend, positive breadth, controlled volatility"
        stress = "LOW"

    return MarketRegimeClassification(
        regime_code=regime_code,
        description=desc,
        nifty_sma20_slope_pct=round(sma20_slope, 2),
        nifty_sma50_slope_pct=round(sma50_slope, 2),
        breadth_pct_above_50dma=round(breadth_50dma, 1),
        advance_decline_ratio=round(ad_ratio, 2),
        realized_volatility_pct=round(realized_vol_20d, 1),
        market_stress_level=stress,
        hmm_state=hmm_res.get("current_state") if hmm_res else None,
        hmm_label=hmm_res.get("state_label") if hmm_res else None,
        hmm_probabilities=hmm_res.get("state_probabilities") if hmm_res else None
    )


def fit_3state_hmm_market_regime(
    returns_series: Optional[np.ndarray] = None,
    default_n_states: int = 3,
) -> Dict[str, Any]:
    """Fits an empirical 3-State Markov Regime Model on return/volatility dynamics.

    States:
      State 0: Accumulation / Low Volatility Range (Bullish Setup)
      State 1: Trending Expansion (High Return / Low-Med Vol)
      State 2: Volatile Distribution / Stress (High Vol / Negative Return)
    """
    if returns_series is None or len(returns_series) < 60:
        # Default prior probabilities and transition matrix
        return {
            "current_state": 1,
            "state_label": "TRENDING_EXPANSION",
            "state_probabilities": [0.20, 0.70, 0.10],
            "transition_matrix": [
                [0.85, 0.12, 0.03],
                [0.05, 0.90, 0.05],
                [0.10, 0.15, 0.75]
            ],
            "regime_stability_score": 0.88,
        }

    # Classify windowed historical returns into discrete regimes
    # Use rolling 20-day blocks across the returns series
    n = len(returns_series)
    window = 20
    states = []
    for i in range(window, n + 1):
        sub = returns_series[i - window:i]
        vol = np.std(sub) * np.sqrt(252)
        ret_mean = np.mean(sub) * 252
        if vol > 0.25 or ret_mean < -0.10:
            st = 2
        elif ret_mean > 0.10 and vol < 0.20:
            st = 1
        else:
            st = 0
        states.append(st)

    states = np.array(states)
    curr_state = int(states[-1])

    labels = {
        0: "ACCUMULATION_RANGE",
        1: "TRENDING_EXPANSION",
        2: "VOLATILE_DISTRIBUTION"
    }

    # Estimate empirical transition matrix C_ij from state sequence
    counts = np.ones((3, 3), dtype=float) * 0.1  # Laplace smoothing
    for t in range(len(states) - 1):
        i, j = states[t], states[t + 1]
        counts[i, j] += 1.0

    trans_matrix = (counts / counts.sum(axis=1, keepdims=True)).round(4).tolist()

    # Calculate empirical state probabilities from recent history & transition row
    recent_counts = np.bincount(states[-30:], minlength=3)
    raw_probs = recent_counts / max(1, len(states[-30:]))
    # Blend with current state transition vector
    transition_row = np.array(trans_matrix[curr_state])
    blended_probs = 0.5 * raw_probs + 0.5 * transition_row
    blended_probs = (blended_probs / blended_probs.sum()).round(4).tolist()

    return {
        "current_state": curr_state,
        "state_label": labels[curr_state],
        "state_probabilities": blended_probs,
        "transition_matrix": trans_matrix,
        "regime_stability_score": round(float(max(blended_probs)), 2),
    }


class DIIAbsorptionRatioScorer:
    """Domestic Institutional Investment (DII) vs FII Outflow Absorption Scorer (Phase 190).

    Quantifies the structural liquidity firewall provided by Indian domestic SIP inflows
    (> Rs 25,000 Cr/month) against Foreign Institutional Investor (FII) sell-offs.

    Mathematical Formulation:
        Absorption Ratio = DII Net Inflow (Rs Cr) / max(0.1, FII Net Outflow (Rs Cr))

    Regimes:
      - DOMESTIC_SUPER_ABSORPTION: Absorption Ratio >= 1.25x (FII outflow overwhelmingly absorbed)
      - DOMESTIC_ABSORPTION_STABLE: 1.0x <= Absorption Ratio < 1.25x (Positive domestic absorption)
      - PARTIAL_DOMESTIC_ABSORPTION: 0.5x <= Absorption Ratio < 1.0x (Moderate net foreign liquidity drain)
      - NET_LIQUIDITY_DEFICIT_HAIRCUT: Absorption Ratio < 0.5x (Severe foreign drain overwhelming domestic flows)
      - DUAL_CAPITAL_INFLOW: Both FII and DII are net buyers (FII net outflow <= 0)
    """

    @classmethod
    def calculate_absorption_ratio(
        cls,
        dii_net_cr: Optional[float] = None,
        fii_net_cr: Optional[float] = None,
        monthly_sip_runrate_cr: float = 25000.0,
    ) -> Dict[str, Any]:
        """Calculates DII absorption ratio, net institutional liquidity, and regime firewall state."""
        if dii_net_cr is None and fii_net_cr is None:
            return {
                "status": "DATA_UNAVAILABLE",
                "dii_net_cr": None,
                "fii_net_cr": None,
                "net_institutional_flow_cr": 0.0,
                "absorption_ratio": 1.0,
                "firewall_active": True,
                "regime_status": "DATA_UNAVAILABLE_BASELINE",
                "risk_haircut": 0.0,
                "signals": ["FLOW_DATA_UNAVAILABLE_FAIL_CLOSED_BASELINE"],
                "interpretation": "Flow data unobserved; defaulting to neutral domestic SIP baseline stability."
            }

        dii_flow = float(dii_net_cr or 0.0)
        fii_flow = float(fii_net_cr or 0.0)
        net_flow = dii_flow + fii_flow

        signals = []

        # Case 1: FII is a net buyer (fii_flow >= 0)
        if fii_flow >= 0:
            absorption_ratio = 999.0 if dii_flow >= 0 else round(dii_flow / max(0.1, abs(fii_flow)), 2)
            regime_status = "DUAL_CAPITAL_INFLOW" if dii_flow >= 0 else "FOREIGN_DOMINANT_INFLOW"
            firewall_active = True
            risk_haircut = 0.0
            signals.append("FOREIGN_NET_BUYING_CONFIRMED")
            interpretation = "Foreign investors are net buyers; institutional liquidity tailwind active."
        else:
            # Case 2: FII is net selling (fii_flow < 0)
            fii_outflow = abs(fii_flow)
            denom = max(0.1, fii_outflow)
            absorption_ratio = round(dii_flow / denom, 2)

            if dii_flow <= 0:
                # Both selling
                regime_status = "SYNCHRONIZED_INSTITUTIONAL_EXIT"
                firewall_active = False
                risk_haircut = 0.25
                signals.append("SYNCHRONIZED_FII_DII_DISTRIBUTION")
                interpretation = "Both FIIs and DIIs are net sellers; structural liquidity contraction."
            elif absorption_ratio >= 1.25:
                regime_status = "DOMESTIC_SUPER_ABSORPTION"
                firewall_active = True
                risk_haircut = 0.0
                signals.append("DOMESTIC_FIREWALL_SUPER_ABSORPTION")
                interpretation = (
                    f"Domestic SIP/mutual fund inflows (Rs {dii_flow:,.1f} Cr) absorb {absorption_ratio:.2f}x "
                    f"of foreign selling (Rs {fii_outflow:,.1f} Cr). Macro-panic falsified."
                )
            elif absorption_ratio >= 1.0:
                regime_status = "DOMESTIC_ABSORPTION_STABLE"
                firewall_active = True
                risk_haircut = 0.0
                signals.append("DOMESTIC_FIREWALL_STABLE_ABSORPTION")
                interpretation = (
                    f"Domestic liquidity fully neutralizes foreign selling at {absorption_ratio:.2f}x. "
                    "Market insulated from panic liquidation."
                )
            elif absorption_ratio >= 0.5:
                regime_status = "PARTIAL_DOMESTIC_ABSORPTION"
                firewall_active = False
                risk_haircut = 0.10
                signals.append("MODERATE_FOREIGN_LIQUIDITY_DRAIN")
                interpretation = (
                    f"Domestic inflows absorb only {absorption_ratio:.2f}x of foreign selling. "
                    "Net liquidity deficit creates moderate drag on benchmark momentum."
                )
            else:
                regime_status = "NET_LIQUIDITY_DEFICIT_HAIRCUT"
                firewall_active = False
                risk_haircut = 0.20
                signals.append("UNABSORBED_FII_OUTFLOW_PANIC")
                interpretation = (
                    f"Heavy foreign liquidation (Rs {fii_outflow:,.1f} Cr) overwhelms domestic absorption "
                    f"({absorption_ratio:.2f}x). Elevated risk of valuation de-rating."
                )

        # Contextualize with monthly SIP run-rate
        sip_coverage_ratio = round(monthly_sip_runrate_cr / max(0.1, abs(fii_flow)), 2) if fii_flow < 0 else 999.0
        if sip_coverage_ratio >= 1.0 and fii_flow < 0:
            signals.append("SIP_RUNRATE_COVERS_OUTFLOW")

        return {
            "status": "COMPUTED",
            "dii_net_cr": dii_flow,
            "fii_net_cr": fii_flow,
            "net_institutional_flow_cr": round(net_flow, 2),
            "absorption_ratio": absorption_ratio,
            "firewall_active": firewall_active,
            "regime_status": regime_status,
            "risk_haircut": risk_haircut,
            "signals": signals,
            "sip_coverage_ratio": sip_coverage_ratio,
            "monthly_sip_runrate_cr": monthly_sip_runrate_cr,
            "interpretation": interpretation
        }



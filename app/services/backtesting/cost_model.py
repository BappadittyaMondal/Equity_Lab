"""Indian Equity Transaction Cost Model — Phase 169 (P3).

Computes realistic all-in round-trip transaction cost for Indian listed equity
based on SEBI/exchange charge schedule as of FY2024-25.

Rates are stored in config (with as_of date) and must be reviewed after each
Union Budget or SEBI/exchange circular.

Cost components (delivery equity):
  STT:           0.1% on sell side only (Section 111A)
  Exchange levy: 0.00345% (NSE) per side  [verify per exchange circular]
  SEBI fees:     0.0001% per side
  Stamp duty:    0.015% on buy side only
  GST:           18% on (brokerage + exchange levy + SEBI fee)
  DP charge:     ~₹15.93 per scrip per sell (flat, CDSL/NSDL)
  Brokerage:     variable; modelled as flat 0.10% or ₹20/order cap (discount broker)

Note: Intraday/F&O rates differ — a separate IntraداyCostModel can be added.
This project is NOT for live trading; cost model is for research/backtest accuracy only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Charge schedule (FY2024-25 Indian equity delivery — review after each Budget)
# ─────────────────────────────────────────────────────────────────────────────

COST_SCHEDULE_AS_OF = "2024-04-01"
COST_SCHEDULE_REVIEW_REMINDER = "Review after Union Budget / SEBI/exchange circulars"

# Percentages expressed as decimals (0.001 = 0.1%)
_STT_SELL_RATE          = 0.001      # 0.1% on sell turnover
_EXCHANGE_LEVY_PER_SIDE = 0.0000345  # 0.00345% NSE transaction charge per side
_SEBI_FEE_PER_SIDE      = 0.000001   # 0.0001% per side
_STAMP_DUTY_BUY_RATE    = 0.00015    # 0.015% on buy side only
_GST_RATE               = 0.18       # 18% on brokerage + exchange levy + SEBI fee
_BROKERAGE_RATE         = 0.001      # 0.1% per side (discount broker flat cap model)
_DP_CHARGE_PER_SELL     = 15.93      # ₹15.93 flat per scrip on sell side (CDSL)


@dataclass
class TradeSpec:
    """Specification for a single round-trip trade."""
    trade_value: float           # Total trade value in ₹ (buy side)
    is_delivery: bool = True     # True = delivery equity, False = intraday (different rates)
    brokerage_rate: float = _BROKERAGE_RATE  # Override for specific broker model
    apply_dp_charge: bool = True  # False for intraday/F&O where no DP debit occurs


@dataclass
class CostBreakdown:
    """Detailed breakdown of all transaction cost components (₹)."""
    stt_buy: float = 0.0
    stt_sell: float = 0.0
    exchange_levy_buy: float = 0.0
    exchange_levy_sell: float = 0.0
    sebi_fee_buy: float = 0.0
    sebi_fee_sell: float = 0.0
    stamp_duty_buy: float = 0.0
    gst_buy: float = 0.0
    gst_sell: float = 0.0
    brokerage_buy: float = 0.0
    brokerage_sell: float = 0.0
    dp_charge_sell: float = 0.0

    @property
    def total_cost_inr(self) -> float:
        return (
            self.stt_buy + self.stt_sell
            + self.exchange_levy_buy + self.exchange_levy_sell
            + self.sebi_fee_buy + self.sebi_fee_sell
            + self.stamp_duty_buy
            + self.gst_buy + self.gst_sell
            + self.brokerage_buy + self.brokerage_sell
            + self.dp_charge_sell
        )

    @property
    def total_cost_pct(self) -> float:
        """Round-trip cost as % of buy-side trade value. Returns 0.0 if trade_value is 0."""
        return self._trade_value_ref and (self.total_cost_inr / self._trade_value_ref * 100.0) or 0.0

    # Internal reference set by CostModel.compute()
    _trade_value_ref: float = field(default=0.0, repr=False, compare=False)


class CostModel:
    """Computes realistic Indian equity round-trip transaction costs.

    Usage:
        model = CostModel()
        breakdown = model.compute(TradeSpec(trade_value=100_000))
        print(f"Round-trip cost: {breakdown.total_cost_pct:.4f}%")

    For backtesting, use cost_pct() for a single scalar:
        net_return = gross_return - model.cost_pct(trade_value=100_000)
    """

    def compute(self, spec: TradeSpec) -> CostBreakdown:
        """Compute full cost breakdown for one round-trip trade."""
        tv = spec.trade_value
        if tv <= 0:
            return CostBreakdown(_trade_value_ref=0.0)

        br = spec.brokerage_rate
        bd = CostBreakdown()
        bd._trade_value_ref = tv

        # ── Buy side ────────────────────────────────────────────────────
        bd.brokerage_buy      = tv * br
        bd.exchange_levy_buy  = tv * _EXCHANGE_LEVY_PER_SIDE
        bd.sebi_fee_buy       = tv * _SEBI_FEE_PER_SIDE
        bd.stamp_duty_buy     = tv * _STAMP_DUTY_BUY_RATE   # buy only
        bd.stt_buy            = 0.0                          # STT on delivery buy = 0 (abolished Apr 2023)
        bd.gst_buy            = (bd.brokerage_buy + bd.exchange_levy_buy + bd.sebi_fee_buy) * _GST_RATE

        # ── Sell side (assume sell at same trade value; approx for backtest) ──
        bd.brokerage_sell     = tv * br
        bd.exchange_levy_sell = tv * _EXCHANGE_LEVY_PER_SIDE
        bd.sebi_fee_sell      = tv * _SEBI_FEE_PER_SIDE
        bd.stt_sell           = tv * _STT_SELL_RATE          # 0.1% sell only
        bd.gst_sell           = (bd.brokerage_sell + bd.exchange_levy_sell + bd.sebi_fee_sell) * _GST_RATE
        bd.dp_charge_sell     = _DP_CHARGE_PER_SELL if spec.apply_dp_charge else 0.0

        return bd

    def cost_pct(
        self,
        trade_value: float,
        is_delivery: bool = True,
        brokerage_rate: float = _BROKERAGE_RATE,
    ) -> float:
        """Return round-trip cost as a percentage of trade value.

        This is the primary method for backtesting cost deduction:
            net_return_pct = gross_return_pct - cost_model.cost_pct(trade_value)

        For small trade values, the flat DP charge dominates; the percentage
        is higher for smaller position sizes (realistic).
        """
        spec = TradeSpec(
            trade_value=trade_value,
            is_delivery=is_delivery,
            brokerage_rate=brokerage_rate,
        )
        bd = self.compute(spec)
        return bd.total_cost_pct

    @staticmethod
    def flat_round_trip_pct(
        trade_value: float = 100_000.0,
        brokerage_rate: float = _BROKERAGE_RATE,
    ) -> float:
        """Convenience method: returns round-trip cost % for a standard trade size.

        Default trade_value=₹1L. For large trades, DP charge impact is negligible.
        Use cost_pct() for position-size-aware computation.
        """
        return CostModel().cost_pct(trade_value=trade_value, brokerage_rate=brokerage_rate)

    @property
    def schedule_as_of(self) -> str:
        return COST_SCHEDULE_AS_OF

    @property
    def review_reminder(self) -> str:
        return COST_SCHEDULE_REVIEW_REMINDER


# Module-level singleton for direct import
cost_model = CostModel()

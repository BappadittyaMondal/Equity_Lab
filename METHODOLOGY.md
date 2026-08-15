# IERL Quantitative Financial Methodology & Disclaimers

## 1. Stock Return Calculations & Risk Metrics
- **Price Return (%)**:
  $$\text{Return} = \frac{P_{\text{end}} - P_{\text{start}}}{P_{\text{start}}} \times 100$$
- **Annualized Volatility (%)**:
  $$\sigma_{\text{ann}} = \text{std}(R_{\text{daily}}) \times \sqrt{252} \times 100$$
- **Maximum Drawdown (%)**:
  $$\text{MDD} = \min_{t} \left( \frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau} \right) \times 100$$

## 2. Return Probability Analysis (Non-Parametric Empirical Distribution)
- Calculates historical rolling $N$-day horizon returns over 3 years of daily OHLCV series ($M$ samples).
- **Probability Above Threshold**:
  $$P(R \ge T) = \frac{\sum_{i=1}^M \mathbb{I}(R_i \ge T)}{M} \times 100$$
- Empirical Quantiles ($P_5, P_{25}, P_{50}, P_{75}, P_{95}$) are computed directly using non-parametric order statistics.

## 3. Options Payoff & A2 Range Selling Strategy
- **Total Credit Per Lot**:
  $$\text{Credit} = (C_{\text{prem}} + P_{\text{prem}}) \times \text{LotSize}$$
- **Breakeven Points**:
  $$\text{BE}_{\text{lower}} = K_{\text{put}} - (C_{\text{prem}} + P_{\text{prem}})$$
  $$\text{BE}_{\text{upper}} = K_{\text{call}} + (C_{\text{prem}} + P_{\text{prem}})$$
- **Expected Value (EV)**:
  $$\text{EV} = (P_{\text{win}} \times \text{MaxProfit}) - ((1 - P_{\text{win}}) \times \text{AvgLoss}_{\text{stop}})$$

## 4. SEBI Financial & Regulatory Disclaimers
- SovereignMind / IERL OS is a quantitative research software system.
- Market data is subject to exchange delay (15-minute NSE/BSE delay).
- Historical probabilities and backtested metrics do not guarantee future returns.
- This platform does NOT provide SEBI-registered personalized investment advice or actionable buy/sell orders.

## 5. Point-in-Time Research Data Standard
- Financial observations are stored append-only. A later correction is a new record, not a rewrite of the historical record.
- Every observation requires the financial period, the date it became public, a source URL/reference, and a confidence value.
- Business events such as order wins, capacity expansions, new customers, and management guidance carry their own public-announcement date and source.
- Any historical screen or backtest must query data using an `as_of` timestamp. It may use only information published on or before that time.
- Missing, conflicting, or low-confidence data must remain visible to the analytical layer; it must not be silently replaced by estimates.

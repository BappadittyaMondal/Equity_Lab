# Institutional Capital Governance & AUM Operational Envelope

## 1. Executive Summary
This document establishes the institutional capital governance boundaries, operational AUM capacity ceilings, and multi-testing noise filtering standards for **Equity Lab OS**.

---

## 2. AUM Operational Capacity Envelope

To prevent market impact, slippage expansion, and liquidity bottlenecks, strategies deployed within Equity Lab operate under strict AUM capacity envelopes:

| Strategy Tier | Target Universe | Liquidity Floor (20D ADTV) | Max Position Size | Optimal Strategy AUM Capacity |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Micro/Small-Cap Alpha** | Micro-Cap / SME / Nifty Smallcap 250 | ₹25 Lakhs / day | 10% of 20D ADTV | **₹5 Cr — ₹50 Cr** |
| **Tier 2: Mid-Cap Compounders** | Nifty Midcap 150 / Growth Leaders | ₹2 Cr / day | 10% of 20D ADTV | **₹50 Cr — ₹250 Cr** |
| **Tier 3: Institutional Large-Cap** | Nifty 100 / F&O Liquid Universe | ₹20 Cr+ / day | 5% of 20D ADTV | **₹250 Cr — ₹1,000 Cr+** |

---

## 3. Book-Level Capital Governance Controls

While individual screening engines enforce stock-level constraints, the **Portfolio Capital Governor** enforces macro risk ceilings:

1. **Gross Exposure Ceiling:** Hard max 100% long capital commitment. No leveraged borrowing or inadvertent margin exposure.
2. **Sector & Cluster Concentration Cap:** Maximum 25% allocation to any single sector or highly correlated return cluster ($r > 0.70$).
3. **Drawdown Circuit Breaker:** If portfolio trailing drawdown exceeds **8.0%**, new capital commitments are halted and capital is preserved in cash/liquid instruments.
4. **Active Drift Push Alerts:** Real-time push dispatching via webhooks (`DRIFT_ALERT_WEBHOOK_URL`) on model/strategy performance decay.

---

## 4. Multi-Testing Noise Reduction (Benjamini-Hochberg FDR)

With 46+ simultaneous quantitative and screening engines operating in parallel, raw p-values risk false discoveries. Equity Lab applies the Benjamini-Hochberg False Discovery Rate (FDR) procedure:

$$p_{\text{adjusted}} = \min\left(1.0, \, p_{(i)} \times \frac{m}{i}\right)$$

Where $m$ is the total number of evaluated hypothesis tests and $i$ is the rank of the p-value in ascending order.

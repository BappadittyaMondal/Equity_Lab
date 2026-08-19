<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Geopolitical And Macro Risk Engine
> **Role:** Point-in-time external-risk assessment
> **Use when:** Testing macro, policy, trade, commodity, currency, and geopolitical exposure.
> **Evidence rule:** Use observed research events and disclose missing triggers rather than assigning synthetic risk.

# Geopolitical And Macro Risk Engine

**Version:** v_0.0  
**Status:** Production  
**Category:** External Risk Assessment

## 1. Purpose

The engine evaluates macro-economic policy shocks, crude-oil volatility, tariff and duty changes, sanctions, foreign-exchange volatility, and geopolitical alerts that may affect an equity or its sector.

## 2. Contract

**Inputs:** normalized `symbol`, optional `as_of` cutoff, company sector data, and the point-in-time research timeline.

**Outputs:** `status`, sector, sector sensitivity profile, `macro_risk_rating`, `active_triggers`, `conviction_penalty_pct`, dated evidence, and metadata.

## 3. Method

1. Load the company and timeline at the requested cutoff.
2. Identify macro or geopolitical event types, including monetary policy, crude-oil shock, tariff change, sanctions, and FX volatility.
3. Map known sectors to their primary external sensitivity.
4. Count high or critical and moderate active triggers.
5. Apply the configured capped conviction penalty and classify risk as low, moderate, or high.

## 4. Data Availability And Limits

Return `DATA_UNAVAILABLE` when no qualifying trigger is observed. The absence of a stored trigger is not proof that geopolitical risk is absent. Sector profiles are directional sensitivities, not forecasts; the result must be reviewed with current dated evidence, company-specific exposure, and scenario analysis.

<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** Causal Analysis Engine
> **Role:** Event-impact research engine
> **Use when:** Estimating empirical post-event return relationships from historical observations.
> **Evidence rule:** Treat associations as historical evidence, not proof of causation.

# Causal Analysis Engine

**Version:** v_0.0  
**Status:** Production  
**Category:** Research And Event Attribution

## 1. Purpose

The Causal Analysis Engine measures historical lead-lag relationships between corporate events and subsequent equity returns. Supported events include earnings releases, capex announcements, governance alerts, management changes, and other events stored in the research timeline.

## 2. Contract

**Inputs:** normalized `symbol`, optional `as_of` cutoff, a research timeline, and daily close history.

**Windows:** five and twenty trading days after each alignable event.

**Outputs:** `status`, `event_causal_relationships`, `net_causal_conviction_delta`, dated evidence, risks, and metadata. Each relationship includes event date and type, title, post-5D and post-20D returns, impact direction, and conviction delta.

## 3. Method

1. Load the point-in-time event timeline.
2. Load up to five years of daily price history.
3. Align each event to its event date or the next available trading date.
4. Calculate post-event returns when the requested trading window exists.
5. Classify the five-day impact as positive, negative, or neutral using configured thresholds.
6. Aggregate non-zero deltas as the reported net causal conviction delta.

## 4. Data Availability And Limits

Return `DATA_UNAVAILABLE` when events, price history, close prices, 30 trading days, or alignable event windows are missing. Zero is an explicit unavailable-data delta, not evidence of neutrality. Historical event-return relationships can be confounded and must be combined with fundamental, valuation, technical, and macro evidence.

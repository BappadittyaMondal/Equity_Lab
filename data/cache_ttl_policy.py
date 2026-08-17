# cache_ttl_policy.py – defines TTL (in seconds) for different market data types.

CACHE_TTL = {
    "quote": 60,                # 1 minute for real‑time quote
    "fundamentals": 24 * 60 * 60,  # 24 hours
    "corporate_actions": 7 * 24 * 60 * 60,  # 7 days
}

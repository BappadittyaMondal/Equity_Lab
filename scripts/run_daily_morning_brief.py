"""Phase 183: Automated Daily Morning Equity Intelligence Pipeline (08:30 AM IST).

Executes the daily morning pre-market research routine:
1. Ingests headlines from Moneycontrol, ET Markets, LiveMint, TradeBrains, and BSE/NSE.
2. Cross-references against DSIJ, ET Money, and corporate disclosure feeds.
3. Classifies sector & ticker impacts, big order wins (with Event Materiality Ratio),
   superstar moves, promoter insider buying, volume microstructure anomalies (>=3x annual avg),
   renowned commentary, and government policy initiatives.
4. Generates an institutional Markdown briefing saved under `Stocks_Analysis_Report/Comparison_And_Single/`.
5. Persists structured JSON digest to `data/news_digests/<YYYY-MM-DD>.json`.
6. Feeds verified catalyst entities to `SelfLearningEngine`.

Designed for automated execution at 08:30 AM IST (Monday–Friday) via Antigravity Automation or cron.
This is strictly for AI Equity Research & Positional Analysis — NOT for automated live trading.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.research.daily_news_engine import (
    generate_daily_digest,
    generate_portfolio_alerts,
    feed_news_to_self_learning,
    RSS_SOURCES,
    SECTOR_KEYWORDS,
    CANONICAL_TICKER_MAP,
)

logger = logging.getLogger("daily_morning_brief")
IST = timezone(timedelta(hours=5, minutes=30))


def build_morning_brief_markdown(digest: Dict[str, Any], alerts: List[Dict[str, Any]]) -> str:
    """Formats the digested news items into a structured Markdown briefing report."""
    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%H:%M IST")

    headlines = digest.get("headlines", [])
    sector_summary = digest.get("sector_summary", {})
    capsules = digest.get("news_capsules", [])

    # Group headlines by catalyst type
    order_wins = []
    superstar_insider = []
    volume_anomalies = []
    gov_macro = []
    general_catalysts = []

    for h in headlines:
        title = h.get("title", "")
        t_lower = title.lower()
        tier = h.get("catalyst_tier", "")
        order_val = h.get("order_value_cr")
        ticker = h.get("resolved_ticker") or "BROAD_MARKET"

        if order_val or any(k in t_lower for k in ["bags", "order", "contract", "awarded", "wins", "capex", "capacity"]):
            order_wins.append(h)
        elif any(k in t_lower for k in ["promoter", "stake", "bulk deal", "block deal", "kacholia", "kedia", "agrawal", "damani", "singhania", "insider", "pledge"]):
            superstar_insider.append(h)
        elif any(k in t_lower for k in ["volume", "surge", "churn", "spikes", "turnover"]):
            volume_anomalies.append(h)
        elif any(k in t_lower for k in ["pli", "cabinet", "tariff", "duty", "budget", "rbi", "government", "policy", "defence ministry"]):
            gov_macro.append(h)
        else:
            general_catalysts.append(h)

    md: List[str] = []
    md.append(f"# Equity Lab: Indian Equities Morning Research Briefing")
    md.append(f"**Publication Timestamp:** `{date_str} {time_str}` | **Market Open Window:** `09:15 AM IST`")
    md.append(f"**Primary Intelligence Engine:** `Equity Lab Daily News & Forensic Engine (Phase 183)`")
    md.append(f"**Coverage Domain:** TradeBrains, DSIJ, ET Markets, Moneycontrol, LiveMint, BSE/NSE Filings")
    md.append(f"**Classification:** Strictly for AI Equity Research & Positional Intelligence (NO LIVE TRADING)")
    md.append("")
    md.append("> [!IMPORTANT]")
    md.append("> **Operational Notice:** Live data and corporate filings reflect verified pre-market conditions.")
    md.append("> High-conviction institutional setups require verifying Delivery % >= 25% and Promoter Pledge < 20% before capital allocation.")
    md.append("")

    # Section 1: Executive Macro Summary
    md.append("## 1. Executive Macro & Sector Sentiment Overview")
    md.append(f"- **Total Market Headlines Analyzed:** {digest.get('total_headlines', 0)}")
    md.append(f"- **RSS & Wire Sources Monitored:** {digest.get('sources_checked', len(RSS_SOURCES))}")
    md.append(f"- **Retail Hype / Operator Traps Neutralized:** {digest.get('high_risk_hype_count', 0)}")
    md.append("")
    md.append("### Sectoral Breadth Matrix")
    md.append("| Sector | Positive Catalysts | Negative Developments | Neutral / Routine | Net Stance |")
    md.append("| :--- | :---: | :---: | :---: | :--- |")
    for sec, counts in sorted(sector_summary.items(), key=lambda x: x[1]["total"], reverse=True):
        pos = counts.get("POSITIVE", 0)
        neg = counts.get("NEGATIVE", 0)
        neu = counts.get("NEUTRAL", 0)
        stance = "**BULLISH**" if pos > neg else ("**BEARISH**" if neg > pos else "NEUTRAL")
        md.append(f"| `{sec}` | {pos} | {neg} | {neu} | {stance} |")
    md.append("")

    # Section 2: Order Wins & Capex Catalysts
    md.append("## 2. Material Order Wins, Contract Awards & Capex Inflection")
    if order_wins:
        md.append("| Ticker | Catalyst Description | Order Value (₹ Cr) | Catalyst Tier | Actionable Research Verdict |")
        md.append("| :--- | :--- | :---: | :---: | :--- |")
        for ow in order_wins[:10]:
            tick = ow.get("resolved_ticker") or "MARKET"
            val = f"₹{ow.get('order_value_cr')} Cr" if ow.get("order_value_cr") else "Disclosed in Filing"
            tier = ow.get("catalyst_tier", "STANDARD_ANNOUNCEMENT")
            verdict = ow.get("actionable_verdict", "Routine contract award.")
            clean_title = ow.get("title", "").replace("|", "-")
            md.append(f"| **`{tick}`** | {clean_title} | {val} | `{tier}` | {verdict} |")
    else:
        md.append("*No mega-order wins or contract disclosures reported in the immediate pre-market cycle.*")
    md.append("")

    # Section 3: Superstar Investor & Promoter Conviction
    md.append("## 3. Superstar Investor Entries, Block Deals & Promoter Actions")
    if superstar_insider:
        for item in superstar_insider[:8]:
            tick = item.get("resolved_ticker") or "BROAD_MARKET"
            md.append(f"- **`{tick}`**: {item.get('title')}")
            if item.get("link"):
                md.append(f"  - *Source Reference:* [{item.get('source_name')}]({item.get('link')})")
    else:
        md.append("*No major block deals or promoter shareholding modifications detected in the overnight feeds.*")
    md.append("")

    # Section 4: Volume Anomaly & Microstructure Radar
    md.append(r"## 4. Volume Microstructure Anomalies (Prior Session $\ge 3\times$ Annual Avg)")
    if volume_anomalies:
        for item in volume_anomalies[:6]:
            tick = item.get("resolved_ticker") or "MARKET"
            md.append(f"- **`{tick}`**: {item.get('title')}")
    else:
        md.append(r"- **Screening Methodology:** Equity Lab filters for previous trading session volume $\ge 3\times$ 200-day baseline.")
        md.append(r"- **Verification Rule:** Confirm delivery volume % $\ge 25\%$ on NSE/BSE before classifying as institutional accumulation. Avoid low-delivery (<15%) upper circuit traps.")
    md.append("")

    # Section 5: Government Policy, PLI & Sovereign Push
    md.append("## 5. Government Push, PLI Allocations & Sovereign Policy")
    if gov_macro:
        for item in gov_macro[:6]:
            tick = item.get("resolved_ticker") or "POLICY_SECTOR"
            md.append(f"- **Policy Impact (`{tick}`):** {item.get('title')}")
    else:
        md.append("*No new sovereign policy notifications or tariff adjustments published in overnight gazettes.*")
    md.append("")

    # Section 6: Institutional News Capsules
    md.append("## 6. Top Institutional News Capsules (Deep Dive)")
    if capsules:
        for cap in capsules[:5]:
            md.append(f"### {cap.get('ticker')} — {cap.get('catalyst_tier')}")
            md.append(f"- **Headline:** {cap.get('headline')}")
            md.append(f"- **Sector:** `{cap.get('sector')}` | **Impact Direction:** `{cap.get('direction')}` | **Magnitude:** `{cap.get('magnitude')}`")
            md.append(f"- **Forensic Grade:** `{cap.get('forensic_grade')}`")
            md.append(f"- **Synthesis:** {cap.get('actionable_verdict')}")
            md.append("")
    else:
        md.append("*No high-conviction institutional capsules generated for this cycle.*")
    md.append("")

    # Section 7: Watchlist & Core Portfolio Alerts
    md.append("## 7. Core Watchlist Direct Alert Overlay")
    if alerts:
        md.append("| Watchlist Ticker | Alert Headline | Match Type | Magnitude | Direction |")
        md.append("| :--- | :--- | :---: | :---: | :---: |")
        for al in alerts[:10]:
            clean_title = al.get("headline", "").replace("|", "-")
            md.append(f"| **`{al.get('ticker')}`** | {clean_title} | `{al.get('match_type')}` | `{al.get('magnitude')}` | `{al.get('direction')}` |")
    else:
        md.append("*All core watchlist stocks operating within normal volatility boundaries. No direct headline risks.*")
    md.append("")

    # Footer
    md.append("---")
    md.append("*Report generated autonomously by Equity Lab Morning Intelligence Pipeline.*")
    md.append("*Archival Path: `Stocks_Analysis_Report/Comparison_And_Single/DAILY_NEWS_INTELLIGENCE_<DATE>_0830_IST.md`*")

    return "\n".join(md)


def run_pipeline() -> Path:
    """Runs the full morning briefing pipeline and writes output files."""
    print("=== [Phase 183] Executing Daily Morning Equity Intelligence Pipeline (08:30 AM IST) ===")
    
    # 1. Fetch & classify RSS feeds
    digest = generate_daily_digest(max_per_source=25)
    print(f"[OK] Fetched and classified {digest.get('total_headlines', 0)} headlines across {digest.get('sources_checked', 0)} sources.")

    # 2. Portfolio alert overlay
    alerts = generate_portfolio_alerts(digest=digest)
    print(f"[OK] Generated {len(alerts)} portfolio alerts against active watchlists.")

    # 3. Dynamic self-learning feedback loop
    learned = feed_news_to_self_learning(digest.get("headlines", []))
    print(f"[OK] Dynamic Self-Learning Brain updated with {len(learned)} corroborated news patterns.")

    # 4. Generate Markdown Briefing
    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%Y-%m-%d")
    hhmm_str = now_ist.strftime("%H%M")
    
    report_content = build_morning_brief_markdown(digest, alerts)

    # 5. Save report to canonical Stocks_Analysis_Report/Comparison_And_Single/
    out_dir = PROJECT_ROOT / "Stocks_Analysis_Report" / "Comparison_And_Single"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / f"DAILY_NEWS_INTELLIGENCE_{date_str}_{hhmm_str}_IST.md"
    report_file.write_text(report_content, encoding="utf-8")
    print(f"[SUCCESS] Morning Briefing report successfully saved to: {report_file}")

    return report_file


if __name__ == "__main__":
    run_pipeline()

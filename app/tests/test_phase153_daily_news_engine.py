"""Phase 153 Tests — Daily News Intelligence Engine & Portfolio Alert Overlay.

Verifies:
  T6: RSS parsing, headline classification, digest generation, sector summary.
  T7: Portfolio alert overlay matches tickers by direct mention and sector overlap.
"""

import pytest
from app.services.research.daily_news_engine import (
    classify_headline,
    generate_portfolio_alerts,
    _compute_sector_summary,
    SECTOR_KEYWORDS,
    IMPACT_KEYWORDS,
    RSS_SOURCES,
    WATCHLIST_TICKER_SECTORS,
    TICKER_KEYWORDS,
)


class TestHeadlineClassification:
    """T6: Verify keyword-based sector and impact classification."""

    def test_power_sector_detection(self):
        result = classify_headline("NTPC wins Rs 5,000 Cr solar power project in Rajasthan")
        assert "POWER_ENERGY" in result["sectors"]
        assert result["direction"] == "POSITIVE"

    def test_negative_impact_detection(self):
        result = classify_headline("Bank NPA crisis deepens as defaults surge across NBFC sector")
        assert "BANKING_FINANCE" in result["sectors"]
        assert result["direction"] == "NEGATIVE"

    def test_neutral_headline(self):
        result = classify_headline("Weather update: monsoon arrives in Kerala")
        assert result["direction"] == "NEUTRAL"
        assert "GENERAL" in result["sectors"]

    def test_multi_sector_headline(self):
        result = classify_headline("Adani Power launches AI-powered grid management using cloud software")
        sectors = result["sectors"]
        assert len(sectors) >= 2  # Should match POWER_ENERGY and IT_TECH

    def test_high_magnitude(self):
        result = classify_headline("Company wins massive deal, profit surges, record growth beats all expectations")
        assert result["magnitude"] == "HIGH"
        assert result["direction"] == "POSITIVE"


class TestSectorSummary:
    """Verify sector summary computation from classified headlines."""

    def test_sector_summary_counts(self):
        classified = [
            {"sectors": ["POWER_ENERGY"], "direction": "POSITIVE"},
            {"sectors": ["POWER_ENERGY"], "direction": "NEGATIVE"},
            {"sectors": ["IT_TECH"], "direction": "POSITIVE"},
        ]
        summary = _compute_sector_summary(classified)
        assert summary["POWER_ENERGY"]["POSITIVE"] == 1
        assert summary["POWER_ENERGY"]["NEGATIVE"] == 1
        assert summary["POWER_ENERGY"]["total"] == 2
        assert summary["IT_TECH"]["POSITIVE"] == 1


class TestPortfolioAlerts:
    """T7: Verify portfolio alert overlay against watchlist."""

    def test_direct_ticker_mention(self):
        mock_digest = {
            "headlines": [
                {
                    "title": "Dynamic Cables bags Rs 200 Cr order from PGCIL",
                    "link": "https://example.com/1",
                    "sectors": ["POWER_ENERGY"],
                    "direction": "POSITIVE",
                    "magnitude": "HIGH",
                    "source_name": "ET_Markets",
                },
            ]
        }
        alerts = generate_portfolio_alerts(digest=mock_digest)
        dycl_alerts = [a for a in alerts if a["ticker"] == "DYCL"]
        assert len(dycl_alerts) >= 1
        assert dycl_alerts[0]["match_type"] == "DIRECT_MENTION"

    def test_sector_overlap_alert(self):
        mock_digest = {
            "headlines": [
                {
                    "title": "RBI cuts repo rate by 25 bps, auto sector to benefit from cheaper loans",
                    "link": "https://example.com/2",
                    "sectors": ["AUTO"],
                    "direction": "POSITIVE",
                    "magnitude": "HIGH",
                    "source_name": "Moneycontrol_Markets",
                },
            ]
        }
        alerts = generate_portfolio_alerts(digest=mock_digest)
        mayur_alerts = [a for a in alerts if a["ticker"] == "MAYURUNIQ"]
        assert len(mayur_alerts) >= 1
        assert mayur_alerts[0]["match_type"] == "SECTOR_OVERLAP"

    def test_no_alert_for_unrelated_headline(self):
        mock_digest = {
            "headlines": [
                {
                    "title": "Lionel Messi scores hat-trick in friendly match",
                    "link": "https://example.com/3",
                    "sectors": ["GENERAL"],
                    "direction": "NEUTRAL",
                    "magnitude": "LOW",
                    "source_name": "ET_Markets",
                },
            ]
        }
        alerts = generate_portfolio_alerts(digest=mock_digest)
        assert len(alerts) == 0

    def test_alert_sorting_direct_first(self):
        mock_digest = {
            "headlines": [
                {
                    "title": "Power sector capex surges 40% YoY",
                    "sectors": ["POWER_ENERGY"],
                    "direction": "POSITIVE",
                    "magnitude": "HIGH",
                    "source_name": "MC",
                },
                {
                    "title": "Nitta Gelatin wins FDA approval for new collagen product",
                    "sectors": ["PHARMA_HEALTHCARE"],
                    "direction": "POSITIVE",
                    "magnitude": "HIGH",
                    "source_name": "MC",
                },
            ]
        }
        alerts = generate_portfolio_alerts(digest=mock_digest)
        if len(alerts) >= 2:
            direct = [a for a in alerts if a["match_type"] == "DIRECT_MENTION"]
            sector = [a for a in alerts if a["match_type"] == "SECTOR_OVERLAP"]
            if direct and sector:
                assert alerts.index(direct[0]) < alerts.index(sector[0])


class TestRSSSourceRegistry:
    """Verify RSS source configuration is complete."""

    def test_minimum_sources(self):
        assert len(RSS_SOURCES) >= 3

    def test_source_structure(self):
        for src in RSS_SOURCES:
            assert "name" in src
            assert "url" in src
            assert "category" in src
            assert src["url"].startswith("http")


class TestPhase152RegressionAfterPhase153:
    """Ensure Phase 152 return_ceiling still works."""

    def test_return_ceiling_import(self):
        from app.services.research.return_ceiling import compute_return_ceiling
        result = compute_return_ceiling(2000.0, 100.0)
        assert "base_multiple" in result
        assert "multibagger_eligible" in result

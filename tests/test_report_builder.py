import unittest
from datetime import datetime, timezone
from agents.report_builder import report_builder_node
from schemas.report import MarketMetrics, MarketAnalysis, MarketReport


class TestReportBuilder(unittest.TestCase):

    def setUp(self):
        """Prepare representative research and analysis data"""

        self.state = {
            "coin_id": "bitcoin",
            "coin_name": "Bitcoin",
            "coin_symbol": "btc",
            "period_days": 7,

            "market_data": {
                "coin": {
                    "current_price": 90000,
                    "market_cap": 1800000000000,
                    "total_volume": 35000000000,
                    "price_change_percentage_24h": 2.5,
                }
            },

            "historical_data": {
                "prices": [
                    {"timestamp": 1795600000000, "price": 85000},
                    {"timestamp": 1795686400000, "price": 87000},
                    {"timestamp": 1795772800000, "price": 88000},
                    {"timestamp": 1795859200000, "price": 90000},
                ],
                "volumes": [
                    {"timestamp": 1795600000000, "volume": 30000000000},
                    {"timestamp": 1795686400000, "volume": 32000000000},
                ],
            },

            "news_data": [
                {
                    "title": "Bitcoin reaches new price level",
                    "url": "https://example.com/bitcoin",
                    "source": "Example News",
                    "published_at": "Tue, 24 Nov 2026 10:00:00 GMT",
                },
                {
                    "title": "Bitcoin market update",
                    "url": "https://example.com/market",
                    "domain": "example.org",
                    "seendate": "20261124T120000Z",
                },
            ],

            "validation_error": None,
            "market_error": None,
            "historical_error": None,
            "news_error": None,

            "metrics": MarketMetrics(
                current_price_usd=90000,
                market_cap_usd=1800000000000,
                total_volume_24h_usd=35000000000,
                price_change_24h_pct=2.5,
                period_change_pct=5.88,
                period_high_usd=90000,
                period_low_usd=85000,
                average_price_usd=87500,
                price_volatility_pct=1.2,
                average_volume_24h_usd=31000000000,
            ),

            "analysis": MarketAnalysis(
                summary="Bitcoin increased over the analysis period.",
                key_findings=["Price increased by 5.88%."],
                risks=["The analysis covers only seven days."],
                outlook="Cautiously positive.",
                confidence="medium",
                confidence_reason="Limited historical coverage.",
            ),
        }

    def test_report_assembly(self):
        """Verify that all report sections are assembled correctly"""

        result = report_builder_node(self.state)
        report = result["final_report"]

        self.assertIsInstance(report, MarketReport)
        self.assertEqual(result["status"], "completed")

        self.assertEqual(report.coin_id, "bitcoin")
        self.assertEqual(report.period_days, 7)

        self.assertIsInstance(report.generated_at, datetime)
        self.assertEqual(report.generated_at.tzinfo, timezone.utc)

        self.assertEqual(len(report.price_history), 4)
        self.assertEqual(len(report.volume_history), 2)
        self.assertEqual(len(report.news), 2)

        self.assertEqual(report.price_history[0].price_usd, 85000)
        self.assertEqual(report.volume_history[0].volume_usd, 30000000000)

        self.assertEqual(report.news[0].source, "Example News")
        self.assertEqual(report.news[1].source, "example.org")

        self.assertEqual(report.analysis.confidence, "medium")
        self.assertEqual(report.metrics.current_price_usd, 90000)

        self.assertIn("CoinGecko", report.data_sources)
        self.assertEqual(report.limitations, [])

    def test_missing_data_and_errors(self):
        """Verify that missing research data is reported as a limitation"""

        state = self.state.copy()
        state.update({
            "market_data": None,
            "historical_data": None,
            "news_data": [],
            "market_error": "Market API unavailable",
            "historical_error": "Historical API unavailable",
            "news_error": "News provider unavailable",
        })

        result = report_builder_node(state)
        report = result["final_report"]

        self.assertEqual(report.price_history, [])
        self.assertEqual(report.volume_history, [])
        self.assertEqual(report.news, [])

        self.assertEqual(report.data_sources, [])
        self.assertTrue(
            any("Market API unavailable" in item for item in report.limitations)
        )
        self.assertTrue(
            any("News provider unavailable" in item for item in report.limitations)
        )


if __name__ == "__main__":
    unittest.main()

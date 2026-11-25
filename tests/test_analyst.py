import unittest
from agents.analyst import analyst_node
from schemas.report import MarketAnalysis, MarketMetrics


class TestAnalystNode(unittest.TestCase):

    def test_analyst_generates_structured_analysis(self):
        """Verify that the Analyst produces a valid MarketAnalysis Pydantic object"""

        state = {
            "coin_id": "bitcoin",
            "coin_name": "Bitcoin",
            "coin_symbol": "btc",
            "period_days": 7,

            "market_data": {
                "status": True,
                "coin": {
                    "current_price": 90000.0,
                    "market_cap": 1_800_000_000_000,
                    "total_volume": 35_000_000_000,
                    "price_change_percentage_24h": 2.5,
                },
            },

            "historical_data": {
                "status": True,
                "prices": [
                    {"timestamp": 1795000000000, "price": 85000.0},
                    {"timestamp": 1795086400000, "price": 87000.0},
                    {"timestamp": 1795172800000, "price": 88000.0},
                    {"timestamp": 1795259200000, "price": 90000.0},
                ],
                "volumes": [
                    {"timestamp": 1795000000000, "volume": 30_000_000_000},
                    {"timestamp": 1795086400000, "volume": 32_000_000_000},
                    {"timestamp": 1795172800000, "volume": 31_000_000_000},
                    {"timestamp": 1795259200000, "volume": 35_000_000_000},
                ],
            },

            "news_data": [
                {
                    "title": "Bitcoin rises amid increased market demand",
                    "source": "Example News",
                    "url": "https://example.com/bitcoin",
                    "published_at": "2026-11-25T10:00:00Z",
                }
            ],

            "metrics": MarketMetrics(
                current_price_usd=90000.0,
                market_cap_usd=1_800_000_000_000,
                total_volume_24h_usd=35_000_000_000,
                price_change_24h_pct=2.5,
                period_change_pct=5.88,
                period_high_usd=90000.0,
                period_low_usd=85000.0,
                average_price_usd=87500.0,
                price_volatility_pct=1.2,
                average_volume_24h_usd=32_000_000_000,
            ),

            "validation_error": None,
            "market_error": None,
            "historical_error": None,
            "news_error": None,
        }

        result = analyst_node(state)

        self.assertIn("analysis", result)

        analysis = MarketAnalysis.model_validate(result["analysis"])

        self.assertTrue(analysis.summary)
        self.assertTrue(analysis.outlook)
        self.assertIn(analysis.confidence, ["low", "medium", "high"])

        print("\nGenerated analysis:")
        print(analysis.model_dump_json(indent=2))


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.metrics import metrics_node
from schemas.report import MarketMetrics


class TestMetricsNode(unittest.TestCase):

    def setUp(self):
        """Prepare sample data matching the CoinGecko tool responses"""

        self.state = {
            "market_data": {
                "status": True,
                "coin": {
                    "current_price": 105.0,
                    "market_cap": 2_000_000,
                    "total_volume": 500_000,
                    "price_change_percentage_24h": 5.0,
                },
            },
            "historical_data": {
                "status": True,
                "prices": [
                    {"timestamp": 1000, "price": 100.0},
                    {"timestamp": 2000, "price": 110.0},
                    {"timestamp": 3000, "price": 99.0},
                ],
                "volumes": [
                    {"timestamp": 1000, "volume": 1000.0},
                    {"timestamp": 2000, "volume": 2000.0},
                    {"timestamp": 3000, "volume": 3000.0},
                ],
            },
        }


    def test_metrics_calculation(self):
        """Verify extracted and calculated market metrics"""

        result = metrics_node(self.state)
        metrics = result["metrics"]

        self.assertIsInstance(metrics, MarketMetrics)

        # Values extracted from current market data
        self.assertEqual(metrics.current_price_usd, 105.0)
        self.assertEqual(metrics.market_cap_usd, 2_000_000)
        self.assertEqual(metrics.total_volume_24h_usd, 500_000)
        self.assertEqual(metrics.price_change_24h_pct, 5.0)

        # Values calculated from historical prices
        self.assertAlmostEqual(metrics.period_change_pct, -1.0)
        self.assertEqual(metrics.period_high_usd, 110.0)
        self.assertEqual(metrics.period_low_usd, 99.0)
        self.assertAlmostEqual(metrics.average_price_usd, 103.0)

        # Returns are +10% and -10%, so population standard deviation is 10%
        self.assertAlmostEqual(metrics.price_volatility_pct, 10.0)

        # Average of the three rolling 24-hour volume observations
        self.assertAlmostEqual(metrics.average_volume_24h_usd, 2000.0)


    def test_missing_historical_data(self):
        """Verify the node handles unavailable historical data."""

        state = {
            "market_data": self.state["market_data"],
            "historical_data": {},
        }

        result = metrics_node(state)
        metrics = result["metrics"]

        self.assertIsNone(metrics.period_change_pct)
        self.assertIsNone(metrics.period_high_usd)
        self.assertIsNone(metrics.period_low_usd)
        self.assertIsNone(metrics.average_price_usd)
        self.assertIsNone(metrics.price_volatility_pct)
        self.assertIsNone(metrics.average_volume_24h_usd)


if __name__ == "__main__":
    unittest.main()

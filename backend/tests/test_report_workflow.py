import unittest
import uuid
from graphs.main_graph import build_main_graph
from schemas.report import MarketReport
from langchain_core.messages import HumanMessage



class TestReportWorkflow(unittest.TestCase):

    def test_complete_report_workflow(self):
        """Test a complete cryptocurrency report through the main graph"""

        graph, conn = build_main_graph()

        try:
            config = {
                "configurable": {
                    "thread_id": f"report-test-{uuid.uuid4()}"
                }
            }

            result = graph.invoke(
                {
                    "request": (
                        "Generate a 7-day cryptocurrency market report "
                        "for Bitcoin. Research its current price, historical "
                        "performance, and recent news."
                    ),
                    "messages": [
                        HumanMessage(
                            content=(
                                "Generate a 7-day cryptocurrency market report "
                                "for Bitcoin. Research its current price, historical "
                                "performance, and recent news."
                            )
                        )
                    ],
                    "status": "pending",
                },
                config=config,
            )

            self.assertEqual(result["intent"], "report")
            self.assertEqual(result["status"], "completed")
            self.assertIsInstance(result["final_report"], MarketReport)

            report = result["final_report"]

            print("\nReport generated successfully")
            print("Coin:", report.coin_name)
            print("Period:", report.period_days, "days")
            print("Current price:", report.metrics.current_price_usd)
            print("Price observations:", len(report.price_history))
            print("Volume observations:", len(report.volume_history))
            print("News articles:", len(report.news))
            print("Analysis confidence:", report.analysis.confidence)
            print("Data sources:", report.data_sources)
            print("Limitations:", report.limitations)
            print("\nMarket Metrics:")
            print(result["metrics"])

        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

import daily_report


class CalculateCompanyIntelligenceRowsTests(unittest.TestCase):
    def test_propagates_history_observation_window_into_company_narrative(self):
        latest_rows = [
            ("AI Engineer", "Mistral", 200, "Python and AI", "lever"),
        ]
        watchlist = {
            "Mistral": {
                "total_postings": 1,
                "ai_postings": 1,
                "ai_concentration": 100.0,
            }
        }
        history = {
            "snapshots_active": 2,
            "current_postings": 1,
            "first_postings": 1,
            "observation_window_days": 1.5,
        }

        with (
            patch.object(daily_report, "calculate_company_watchlist", return_value=watchlist),
            patch.object(daily_report, "get_company_history", return_value=history),
        ):
            rows = daily_report.calculate_company_intelligence_rows(latest_rows)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["observation_window_days"], 1.5)
        self.assertIn(
            "observation window currently spans only 1.5 days",
            rows[0]["narrative"],
        )


if __name__ == "__main__":
    unittest.main()

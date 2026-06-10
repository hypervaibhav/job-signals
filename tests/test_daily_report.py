import unittest
from unittest.mock import patch

import daily_report


class CalculateCompanyIntelligenceRowsTests(unittest.TestCase):
    def make_latest_rows(self):
        return [
            ("AI Engineer", "Mistral", 200, "Python and AI", "lever"),
        ]

    def make_watchlist(self):
        return {
            "Mistral": {
                "total_postings": 1,
                "ai_postings": 1,
                "ai_concentration": 100.0,
            }
        }

    def test_propagates_history_observation_window_into_company_narrative(self):
        latest_rows = self.make_latest_rows()
        watchlist = self.make_watchlist()
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

    def test_derives_trend_and_confidence_from_company_history(self):
        history = {
            "snapshots_active": 12,
            "current_postings": 10,
            "first_postings": 7,
            "peak_postings": 10,
            "persistence_score": 0.75,
            "observation_window_days": 30,
        }

        with (
            patch.object(
                daily_report,
                "calculate_company_watchlist",
                return_value=self.make_watchlist(),
            ),
            patch.object(daily_report, "get_company_history", return_value=history),
            patch.object(
                daily_report,
                "classify_company_trend",
                return_value="Expanding",
                create=True,
            ) as classify_trend,
            patch.object(
                daily_report,
                "classify_company_trend_confidence",
                return_value="High",
                create=True,
            ) as classify_trend_confidence,
        ):
            rows = daily_report.calculate_company_intelligence_rows(
                self.make_latest_rows()
            )

        classify_trend.assert_called_once_with(history)
        classify_trend_confidence.assert_called_once_with(history)
        self.assertIs(classify_trend.call_args.args[0], history)
        self.assertIs(classify_trend_confidence.call_args.args[0], history)
        self.assertEqual(rows[0]["trend"], "Expanding")
        self.assertEqual(rows[0]["trend_confidence"], "High")

    def test_missing_history_preserves_existing_fallback_without_trend_reconstruction(self):
        with (
            patch.object(
                daily_report,
                "calculate_company_watchlist",
                return_value=self.make_watchlist(),
            ),
            patch.object(daily_report, "get_company_history", return_value=None),
            patch.object(
                daily_report,
                "classify_company_trend",
                create=True,
            ) as classify_trend,
            patch.object(
                daily_report,
                "classify_company_trend_confidence",
                create=True,
            ) as classify_trend_confidence,
        ):
            rows = daily_report.calculate_company_intelligence_rows(
                self.make_latest_rows()
            )

        classify_trend.assert_not_called()
        classify_trend_confidence.assert_not_called()
        self.assertEqual(rows[0]["persistence"], 1)
        self.assertIsNone(rows[0]["observation_window_days"])
        self.assertEqual(rows[0]["conviction"], "Early")
        self.assertIsNone(rows[0]["trend"])
        self.assertIsNone(rows[0]["trend_confidence"])


if __name__ == "__main__":
    unittest.main()

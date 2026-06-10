import unittest
from contextlib import redirect_stdout
from io import StringIO
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

    def test_company_narrative_does_not_repeat_observation_window_warning(self):
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
        self.assertNotIn(
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
            patch.object(
                daily_report,
                "generate_company_trend_narrative",
                return_value="Trend explanation text.",
                create=True,
            ) as generate_trend_narrative,
            patch.object(
                daily_report,
                "generate_company_trend_confidence_narrative",
                return_value="Confidence explanation text.",
                create=True,
            ) as generate_trend_confidence_narrative,
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
        generate_trend_narrative.assert_called_once_with("Expanding", history)
        generate_trend_confidence_narrative.assert_called_once_with("High", history)
        self.assertEqual(rows[0]["trend_narrative"], "Trend explanation text.")
        self.assertEqual(
            rows[0]["trend_confidence_narrative"],
            "Confidence explanation text.",
        )

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
            patch.object(
                daily_report,
                "generate_company_trend_narrative",
                create=True,
            ) as generate_trend_narrative,
            patch.object(
                daily_report,
                "generate_company_trend_confidence_narrative",
                create=True,
            ) as generate_trend_confidence_narrative,
        ):
            rows = daily_report.calculate_company_intelligence_rows(
                self.make_latest_rows()
            )

        classify_trend.assert_not_called()
        classify_trend_confidence.assert_not_called()
        generate_trend_narrative.assert_not_called()
        generate_trend_confidence_narrative.assert_not_called()
        self.assertEqual(rows[0]["persistence"], 1)
        self.assertIsNone(rows[0]["observation_window_days"])
        self.assertEqual(rows[0]["conviction"], "Early")
        self.assertIsNone(rows[0]["trend"])
        self.assertIsNone(rows[0]["trend_confidence"])
        self.assertIsNone(rows[0]["trend_narrative"])
        self.assertIsNone(rows[0]["trend_confidence_narrative"])

    def test_highlights_print_trend_explanations(self):
        output = StringIO()
        row = {
            "company": "Mistral",
            "intelligence": "AI Product Expansion",
            "ai_concentration": 100.0,
            "total_postings": 10,
            "persistence": 10,
            "observation_window_days": 2.4,
            "trend": "Stable",
            "trend_narrative": "Trend explanation text.",
            "trend_confidence": "Low",
            "trend_confidence_narrative": "Confidence explanation text.",
            "conviction": "High",
            "narrative": "Company narrative text.",
        }

        with redirect_stdout(output):
            daily_report.print_company_intelligence_highlights([row])

        report = output.getvalue()
        self.assertIn("Hiring trend: Stable", report)
        self.assertIn("Trend explanation: Trend explanation text.", report)
        self.assertIn("Trend confidence: Low", report)
        self.assertIn(
            "Confidence explanation: Confidence explanation text.",
            report,
        )


if __name__ == "__main__":
    unittest.main()

import sqlite3
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import ANY, patch

import daily_report
import strategic_theme_history


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


class StrategicThemePersistenceIntegrationTests(unittest.TestCase):
    def persist_snapshot(self, conn, snapshot_time, company_intelligence_rows):
        self.assertTrue(
            hasattr(daily_report, "persist_strategic_theme_snapshot"),
            "daily_report.persist_strategic_theme_snapshot must implement "
            "the orchestration contract",
        )
        return daily_report.persist_strategic_theme_snapshot(
            conn,
            snapshot_time,
            company_intelligence_rows,
        )

    def make_intelligence_rows(self):
        return [
            {
                "company": "Mistral",
                "intelligence": "AI Commercialization / GTM Expansion",
            },
            {
                "company": "Integrate",
                "intelligence": "AI Product Expansion",
            },
        ]

    def make_complete_themes(self):
        return [
            {
                "theme": "AI Commercialization",
                "company_count": 1,
                "companies": ["Mistral"],
            },
            {
                "theme": "AI Product Expansion",
                "company_count": 1,
                "companies": ["Integrate"],
            },
            {
                "theme": "AI Research Expansion",
                "company_count": 0,
                "companies": [],
            },
        ]

    def test_persistence_helper_saves_complete_calculated_snapshot(self):
        conn = object()
        rows = self.make_intelligence_rows()
        themes = self.make_complete_themes()

        with (
            patch.object(
                daily_report,
                "calculate_theme_snapshot",
                return_value=themes,
                create=True,
            ) as calculate_snapshot,
            patch.object(
                daily_report,
                "save_theme_snapshot",
                create=True,
            ) as save_snapshot,
            patch.object(
                daily_report,
                "detect_strategic_themes",
            ) as detect_themes,
        ):
            self.persist_snapshot(conn, 123, rows)

        calculate_snapshot.assert_called_once_with(rows)
        save_snapshot.assert_called_once_with(
            conn,
            123,
            themes,
            eligible_company_count=2,
        )
        detect_themes.assert_not_called()

    def test_persistence_helper_is_idempotent_through_save_theme_snapshot(self):
        conn = sqlite3.connect(":memory:")
        self.addCleanup(conn.close)
        strategic_theme_history.initialize_strategic_theme_history(conn)
        rows = self.make_intelligence_rows()
        themes = self.make_complete_themes()

        with (
            patch.object(
                daily_report,
                "calculate_theme_snapshot",
                return_value=themes,
                create=True,
            ),
            patch.object(
                daily_report,
                "save_theme_snapshot",
                wraps=strategic_theme_history.save_theme_snapshot,
                create=True,
            ),
        ):
            self.persist_snapshot(conn, 123, rows)
            self.persist_snapshot(conn, 123, rows)

        snapshot_count = conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_snapshots"
        ).fetchone()[0]
        membership_count = conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_companies"
        ).fetchone()[0]
        self.assertEqual(snapshot_count, 3)
        self.assertEqual(membership_count, 2)

    def test_persistence_helper_does_not_swallow_save_errors(self):
        with (
            patch.object(
                daily_report,
                "calculate_theme_snapshot",
                return_value=self.make_complete_themes(),
                create=True,
            ),
            patch.object(
                daily_report,
                "save_theme_snapshot",
                side_effect=sqlite3.OperationalError("save failed"),
                create=True,
            ),
        ):
            with self.assertRaisesRegex(sqlite3.OperationalError, "save failed"):
                self.persist_snapshot(
                    object(),
                    123,
                    self.make_intelligence_rows(),
                )

    def test_report_uses_authoritative_latest_snapshot_time_for_persistence(self):
        latest = [("AI Engineer", "Mistral", 200, "AI", "lever")]
        previous = [("Engineer", "Mistral", 100, "", "lever")]
        intelligence_rows = self.make_intelligence_rows()

        with (
            patch.object(
                daily_report,
                "get_latest_two_snapshots",
                return_value=(200, 100, latest, previous),
            ),
            patch.object(
                daily_report,
                "calculate_company_intelligence_rows",
                return_value=intelligence_rows,
            ),
            patch.object(
                daily_report,
                "persist_strategic_theme_snapshot",
                create=True,
            ) as persist_snapshot,
            patch.object(daily_report, "print_market_narrative"),
            patch.object(daily_report, "print_opportunity_ranking"),
            patch.object(daily_report, "print_signal_opportunities"),
            patch.object(daily_report, "print_company_watchlist"),
            patch.object(daily_report, "print_company_memory"),
            patch.object(daily_report, "print_strategic_themes"),
            patch.object(daily_report, "print_company_intelligence_highlights"),
            redirect_stdout(StringIO()),
        ):
            daily_report.print_daily_report()

        persist_snapshot.assert_called_once_with(ANY, 200, intelligence_rows)

    def test_report_does_not_persist_when_fewer_than_two_snapshots_exist(self):
        with (
            patch.object(
                daily_report,
                "get_latest_two_snapshots",
                return_value=(100, None, [("Engineer", "Acme", 100, "", "api")], []),
            ),
            patch.object(
                daily_report,
                "persist_strategic_theme_snapshot",
                create=True,
            ) as persist_snapshot,
            redirect_stdout(StringIO()),
        ):
            daily_report.print_daily_report()

        persist_snapshot.assert_not_called()

    def test_v1_printed_strategic_theme_output_remains_unchanged(self):
        output = StringIO()
        rows = [
            {"company": "Integrate", "intelligence": "AI Product Expansion"},
            {"company": "Levelai", "intelligence": "AI Product Expansion"},
        ]

        with redirect_stdout(output):
            daily_report.print_strategic_themes(rows)

        self.assertEqual(
            output.getvalue(),
            (
                "\n--- STRATEGIC THEMES ---\n\n"
                "AI Product Expansion\n"
                "Strength: Emerging\n"
                "Companies: 2\n"
                "Representative companies:\n"
                "- Integrate\n"
                "- Levelai\n"
                "Interpretation: Companies are increasing product and "
                "engineering investment around AI-enabled offerings.\n\n"
            ),
        )


if __name__ == "__main__":
    unittest.main()

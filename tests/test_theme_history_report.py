import sqlite3
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path

import strategic_theme_history

try:
    import theme_history_report
except ModuleNotFoundError:
    theme_history_report = None


def make_theme(theme, companies):
    return {
        "theme": theme,
        "company_count": len(companies),
        "companies": companies,
    }


def make_complete_snapshot(commercialization=None, product=None, research=None):
    return [
        make_theme("AI Commercialization", commercialization or []),
        make_theme("AI Product Expansion", product or []),
        make_theme("AI Research Expansion", research or []),
    ]


def format_expected_timestamp(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M %p")


class ThemeHistoryReportTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        strategic_theme_history.initialize_strategic_theme_history(self.conn)

    def tearDown(self):
        self.conn.close()

    def report_module(self):
        self.assertIsNotNone(
            theme_history_report,
            "theme_history_report.py must implement the inspection report",
        )
        return theme_history_report

    def save_sample_history(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(
                commercialization=["Mistral"],
                product=["Integrate"],
            ),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(
                commercialization=["Mistral"],
                product=["Integrate", "Levelai"],
            ),
            eligible_company_count=3,
        )

    def test_report_prints_active_sorted_theme_history(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertEqual(
            report,
            (
                "STRATEGIC THEME HISTORY\n"
                "\n"
                "AI Product Expansion\n"
                "Lifecycle: Emerging\n"
                "Theme Confidence: Low\n"
                "Explanation: AI Product Expansion is newly detected, appearing "
                "in 2 active snapshots out of 2 eligible snapshots, which is "
                "fewer than the 3 active snapshots needed for an established "
                "lifecycle. Current coverage is 2 companies.\n"
                "Persistence: 2/2 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 2\n"
                "Peak company count: 2\n"
                f"First seen: {format_expected_timestamp(100)}\n"
                f"Latest seen: {format_expected_timestamp(200)}\n"
                "Current members: Integrate, Levelai\n"
                "\n"
                "AI Commercialization\n"
                "Lifecycle: Emerging\n"
                "Theme Confidence: Low\n"
                "Explanation: AI Commercialization is newly detected, appearing "
                "in 2 active snapshots out of 2 eligible snapshots, which is "
                "fewer than the 3 active snapshots needed for an established "
                "lifecycle. Current coverage is 1 company.\n"
                "Persistence: 2/2 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 1\n"
                "Peak company count: 1\n"
                f"First seen: {format_expected_timestamp(100)}\n"
                f"Latest seen: {format_expected_timestamp(200)}\n"
                "Current members: Mistral\n"
            ),
        )

    def test_report_includes_singletons_and_suppresses_never_detected_zero_count_themes(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Commercialization", report)
        self.assertIn("Current company count: 1", report)
        self.assertNotIn("AI Research Expansion", report)
        self.assertNotIn("Current company count: 0", report)
        self.assertNotIn("Current members: none", report)

    def test_report_suppresses_new_zero_company_themes(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            [
                make_theme("Data & Analytics Investment", []),
                make_theme("Engineering Platform Expansion", []),
            ],
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertEqual(
            report,
            (
                "STRATEGIC THEME HISTORY\n"
                "\n"
                "No active strategic themes found.\n"
            ),
        )
        self.assertNotIn("Data & Analytics Investment", report)
        self.assertNotIn("Engineering Platform Expansion", report)
        self.assertNotIn("Stable, Low confidence, 0 companies", report)

    def test_report_formats_first_seen_as_human_readable_timestamp(self):
        first_seen = 1781198700
        latest_seen = 1781202300
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            first_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            latest_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            f"First seen: {format_expected_timestamp(first_seen)}\n",
            report,
        )

    def test_report_formats_latest_seen_as_human_readable_timestamp(self):
        first_seen = 1781198700
        latest_seen = 1781202300
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            first_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            latest_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            f"Latest seen: {format_expected_timestamp(latest_seen)}\n",
            report,
        )

    def test_report_does_not_include_raw_unix_timestamp_values(self):
        first_seen = 1781198700
        latest_seen = 1781202300
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            first_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            latest_seen,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertNotIn(f"First seen: {first_seen}\n", report)
        self.assertNotIn(f"Latest seen: {latest_seen}\n", report)

    def test_report_includes_lifecycle_for_each_theme(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Emerging\n", report)
        self.assertIn("AI Commercialization\nLifecycle: Emerging\n", report)
        self.assertNotIn("AI Research Expansion\nLifecycle: Stable\n", report)

    def test_report_prints_theme_confidence_after_lifecycle(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            "AI Product Expansion\n"
            "Lifecycle: Emerging\n"
            "Theme Confidence: Low\n"
            "Explanation: AI Product Expansion is newly detected",
            report,
        )
        self.assertLess(
            report.index("Lifecycle: Emerging\n"),
            report.index("Theme Confidence: Low\n"),
        )
        self.assertLess(
            report.index("Theme Confidence: Low\n"),
            report.index("Explanation: AI Product Expansion"),
        )

    def test_report_uses_theme_confidence_helper(self):
        self.save_sample_history()
        module = self.report_module()

        with mock.patch.object(
            module,
            "classify_theme_confidence",
            return_value="Moderate",
            create=True,
        ) as classify_confidence:
            report = module.build_theme_history_report(self.conn)

        self.assertTrue(
            classify_confidence.call_args_list,
            "theme_history_report.py should call "
            "classify_theme_confidence(history, lifecycle)",
        )
        first_call = classify_confidence.call_args_list[0]
        self.assertEqual(first_call.args[0]["theme"], "AI Product Expansion")
        self.assertEqual(first_call.args[1], "Emerging")
        self.assertIn("Theme Confidence: Moderate\n", report)

    def test_report_prints_low_theme_confidence(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            "AI Commercialization\n"
            "Lifecycle: Emerging\n"
            "Theme Confidence: Low\n",
            report,
        )

    def test_report_prints_moderate_theme_confidence(self):
        for snapshot_time in [100, 200, 300, 400]:
            strategic_theme_history.save_theme_snapshot(
                self.conn,
                snapshot_time,
                make_complete_snapshot(product=["Integrate", "Levelai"]),
                eligible_company_count=3,
            )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            "AI Product Expansion\n"
            "Lifecycle: Stable\n"
            "Theme Confidence: Moderate\n",
            report,
        )

    def test_report_prints_high_theme_confidence(self):
        for snapshot_time in [100, 200, 300, 400, 500, 600]:
            strategic_theme_history.save_theme_snapshot(
                self.conn,
                snapshot_time,
                make_complete_snapshot(product=["Integrate", "Levelai"]),
                eligible_company_count=3,
            )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            "AI Product Expansion\n"
            "Lifecycle: Stable\n"
            "Theme Confidence: High\n",
            report,
        )

    def test_report_prints_lifecycle_explanation_after_lifecycle(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn(
            "AI Product Expansion\n"
            "Lifecycle: Emerging\n"
            "Theme Confidence: Low\n"
            "Explanation: AI Product Expansion is newly detected",
            report,
        )
        self.assertLess(
            report.index("Lifecycle: Emerging\n"),
            report.index("Explanation: AI Product Expansion"),
        )
        self.assertLess(
            report.index("Explanation: AI Product Expansion"),
            report.index("Persistence: 2/2 snapshots\n"),
        )

    def test_report_uses_theme_lifecycle_narrative_helper(self):
        self.save_sample_history()
        module = self.report_module()

        with mock.patch.object(
            module,
            "generate_theme_lifecycle_narrative",
            return_value="Narrative text.",
            create=True,
        ) as generate_narrative:
            report = module.build_theme_history_report(self.conn)

        self.assertTrue(
            generate_narrative.call_args_list,
            "theme_history_report.py should call "
            "generate_theme_lifecycle_narrative(lifecycle, history)",
        )
        first_call = generate_narrative.call_args_list[0]
        self.assertEqual(first_call.args[0], "Emerging")
        self.assertEqual(first_call.args[1]["theme"], "AI Product Expansion")
        self.assertIn("Explanation: Narrative text.\n", report)

    def test_report_prints_stable_lifecycle(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            300,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Stable\n", report)

    def test_report_prints_emerging_lifecycle(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Emerging\n", report)

    def test_report_prints_expanding_lifecycle(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            300,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Expanding\n", report)

    def test_report_prints_contracting_lifecycle(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            300,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Contracting\n", report)

    def test_report_prints_disappeared_lifecycle(self):
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            eligible_company_count=3,
        )
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(),
            eligible_company_count=3,
        )
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Disappeared\n", report)

    def test_lifecycle_does_not_change_sort_order(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertLess(
            report.index("AI Product Expansion\n"),
            report.index("AI Commercialization\n"),
        )

    def test_lifecycle_does_not_change_persistence_and_count_output(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("Persistence: 2/2 snapshots\n", report)
        self.assertIn("Persistence score: 100.0%\n", report)
        self.assertIn("Current company count: 2\n", report)
        self.assertIn("Peak company count: 2\n", report)

    def test_report_empty_state_is_clear(self):
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertEqual(
            report,
            (
                "STRATEGIC THEME HISTORY\n"
                "\n"
                "No strategic theme history found.\n"
            ),
        )

    def test_main_prints_report_for_supplied_database_path(self):
        module = self.report_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "jobs.db"
            conn = sqlite3.connect(db_path)
            try:
                strategic_theme_history.initialize_strategic_theme_history(conn)
                strategic_theme_history.save_theme_snapshot(
                    conn,
                    100,
                    make_complete_snapshot(product=["Integrate"]),
                    eligible_company_count=1,
                )
            finally:
                conn.close()

            output = StringIO()
            with redirect_stdout(output):
                module.main(str(db_path))

        self.assertEqual(
            output.getvalue(),
            (
                "STRATEGIC THEME HISTORY\n"
                "\n"
                "AI Product Expansion\n"
                "Lifecycle: Emerging\n"
                "Theme Confidence: Low\n"
                "Explanation: AI Product Expansion is newly detected, appearing "
                "in 1 active snapshot out of 1 eligible snapshot, which is "
                "fewer than the 3 active snapshots needed for an established "
                "lifecycle. Current coverage is 1 company.\n"
                "Persistence: 1/1 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 1\n"
                "Peak company count: 1\n"
                f"First seen: {format_expected_timestamp(100)}\n"
                f"Latest seen: {format_expected_timestamp(100)}\n"
                "Current members: Integrate\n"
                "\n"
            ),
        )


if __name__ == "__main__":
    unittest.main()

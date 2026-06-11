import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
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

    def test_report_prints_complete_sorted_theme_history(self):
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
                "Persistence: 2/2 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 2\n"
                "Peak company count: 2\n"
                "First seen: 100\n"
                "Latest seen: 200\n"
                "Current members: Integrate, Levelai\n"
                "\n"
                "AI Commercialization\n"
                "Lifecycle: Emerging\n"
                "Persistence: 2/2 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 1\n"
                "Peak company count: 1\n"
                "First seen: 100\n"
                "Latest seen: 200\n"
                "Current members: Mistral\n"
                "\n"
                "AI Research Expansion\n"
                "Lifecycle: Stable\n"
                "Persistence: 0/2 snapshots\n"
                "Persistence score: 0.0%\n"
                "Current company count: 0\n"
                "Peak company count: 0\n"
                "First seen: never\n"
                "Latest seen: never\n"
                "Current members: none\n"
            ),
        )

    def test_report_includes_singleton_and_zero_count_themes(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Commercialization", report)
        self.assertIn("Current company count: 1", report)
        self.assertIn("AI Research Expansion", report)
        self.assertIn("Current company count: 0", report)
        self.assertIn("Current members: none", report)

    def test_report_includes_lifecycle_for_each_theme(self):
        self.save_sample_history()
        module = self.report_module()

        report = module.build_theme_history_report(self.conn)

        self.assertIn("AI Product Expansion\nLifecycle: Emerging\n", report)
        self.assertIn("AI Commercialization\nLifecycle: Emerging\n", report)
        self.assertIn("AI Research Expansion\nLifecycle: Stable\n", report)

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
        self.assertLess(
            report.index("AI Commercialization\n"),
            report.index("AI Research Expansion\n"),
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
                "Persistence: 1/1 snapshots\n"
                "Persistence score: 100.0%\n"
                "Current company count: 1\n"
                "Peak company count: 1\n"
                "First seen: 100\n"
                "Latest seen: 100\n"
                "Current members: Integrate\n"
                "\n"
                "AI Commercialization\n"
                "Lifecycle: Stable\n"
                "Persistence: 0/1 snapshots\n"
                "Persistence score: 0.0%\n"
                "Current company count: 0\n"
                "Peak company count: 0\n"
                "First seen: never\n"
                "Latest seen: never\n"
                "Current members: none\n"
                "\n"
                "AI Research Expansion\n"
                "Lifecycle: Stable\n"
                "Persistence: 0/1 snapshots\n"
                "Persistence score: 0.0%\n"
                "Current company count: 0\n"
                "Peak company count: 0\n"
                "First seen: never\n"
                "Latest seen: never\n"
                "Current members: none\n"
                "\n"
            ),
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import company_intelligence
from company_intelligence import detect_hiring_archetype, generate_narrative


class DetectHiringArchetypeTests(unittest.TestCase):
    def test_expected_archetype_labels(self):
        cases = [
            (
                "AI Research Expansion",
                Counter(),
                Counter(),
                ["Research Scientist", "Research Engineer"],
                2,
            ),
            (
                "AI Commercialization / GTM Expansion",
                Counter({"Sales": 4}),
                Counter({"ai": 5}),
                ["Account Executive"],
                10,
            ),
            (
                "AI Product Expansion",
                Counter({"Engineering": 3}),
                Counter({"ai": 5}),
                ["Platform Engineer"],
                10,
            ),
            (
                "Engineering Platform Expansion",
                Counter({"Engineering": 5}),
                Counter(),
                ["Software Engineer"],
                10,
            ),
            (
                "Sales Expansion",
                Counter({"Sales": 5}),
                Counter(),
                ["Account Executive"],
                10,
            ),
            (
                "Operations Expansion",
                Counter({"Operations": 3}),
                Counter(),
                ["Operations Manager"],
                10,
            ),
            (
                "Data / Analytics Expansion",
                Counter({"Data / Analytics": 3}),
                Counter(),
                ["Data Analyst"],
                10,
            ),
            (
                "Mixed Hiring Activity",
                Counter({"Product": 2, "Marketing": 2}),
                Counter(),
                ["Product Manager", "Marketing Manager"],
                10,
            ),
        ]

        for expected, categories, skills, roles, latest_count in cases:
            with self.subTest(expected=expected):
                actual = detect_hiring_archetype(
                    categories,
                    skills,
                    roles,
                    latest_count,
                )
                self.assertEqual(actual, expected)


class GenerateNarrativeTests(unittest.TestCase):
    def test_includes_observation_window_caution_when_under_seven_days(self):
        narrative = generate_narrative(
            company_name="Acme",
            momentum=0,
            conviction="High",
            ai_concentration=50,
            top_category="Engineering",
            top_skills=[("python", 3)],
            hiring_archetype="AI Product Expansion",
            observation_window_days=6.9,
        )

        self.assertIn("observation window currently spans only 6.9 days", narrative)
        self.assertIn("long-term durability is not yet established", narrative)

    def test_does_not_include_observation_window_caution_at_seven_days(self):
        narrative = generate_narrative(
            company_name="Acme",
            momentum=0,
            conviction="High",
            ai_concentration=50,
            top_category="Engineering",
            top_skills=[("python", 3)],
            hiring_archetype="AI Product Expansion",
            observation_window_days=7,
        )

        self.assertNotIn("observation window currently spans only", narrative)


class BuildCompanyReportTests(unittest.TestCase):
    def test_uses_company_history_for_persistence_and_observation_fields(self):
        rows = [
            ("AI Engineer", "Acme", "lever", "Python and AI", 200),
            ("Account Executive", "Acme", "lever", "", 200),
            ("Old Role", "Acme", "lever", "", 100),
        ]
        history = {
            "snapshots_active": 7,
            "first_seen": 100,
            "latest_seen": 200,
            "observation_window_days": 1.5,
            "first_postings": 2,
            "current_postings": 10,
            "peak_postings": 12,
        }
        output = StringIO()

        with (
            patch.object(company_intelligence, "get_company_rows", return_value=rows),
            patch.object(company_intelligence, "get_company_history", return_value=history),
            patch.object(
                company_intelligence,
                "format_snapshot_time",
                side_effect=lambda timestamp: f"formatted-{timestamp}",
            ),
            redirect_stdout(output),
        ):
            company_intelligence.build_company_report("Acme")

        report = output.getvalue()
        self.assertIn("Latest snapshot: formatted-200", report)
        self.assertIn("First seen: formatted-100", report)
        self.assertIn("Persistence: 7 snapshots", report)
        self.assertIn("Current postings: 10", report)
        self.assertIn("Peak postings: 12", report)
        self.assertIn("Hiring momentum: Rising (+8)", report)
        self.assertIn("Conviction: High", report)
        self.assertIn("observation window currently spans only 1.5 days", report)
        self.assertNotIn("Old Role", report)

    def test_reports_missing_history_without_reconstructing_persistence(self):
        output = StringIO()

        with (
            patch.object(
                company_intelligence,
                "get_company_rows",
                return_value=[("Engineer", "Acme", "lever", "", 200)],
            ),
            patch.object(company_intelligence, "get_company_history", return_value=None),
            redirect_stdout(output),
        ):
            company_intelligence.build_company_report("Acme")

        self.assertEqual(
            output.getvalue().strip(),
            "No company history found for company: Acme",
        )


if __name__ == "__main__":
    unittest.main()

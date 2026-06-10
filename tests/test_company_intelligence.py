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
    def make_narrative(self, **overrides):
        values = {
            "company_name": "Acme",
            "momentum": 0,
            "conviction": "High",
            "ai_concentration": 50,
            "top_category": "Engineering",
            "top_skills": [("python", 3)],
            "hiring_archetype": "AI Product Expansion",
            "observation_window_days": 7,
        }
        values.update(overrides)
        return generate_narrative(**values)

    def test_does_not_repeat_observation_window_caution_when_under_seven_days(self):
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

        self.assertNotIn("observation window currently spans only", narrative)
        self.assertNotIn("long-term durability is not yet established", narrative)

    def test_does_not_include_observation_window_caution_at_seven_days(self):
        narrative = self.make_narrative()

        self.assertNotIn("observation window currently spans only", narrative)

    def test_stable_trend_with_positive_raw_momentum_does_not_claim_increasing_hiring(self):
        narrative = self.make_narrative(momentum=1)

        self.assertNotIn("appears to be increasing hiring activity", narrative)

    def test_no_skills_uses_clear_fallback_sentence(self):
        narrative = self.make_narrative(
            top_category="Sales",
            top_skills=[],
        )

        self.assertIn(
            "Current hiring is concentrated in Sales, with limited tracked skill "
            "signals.",
            narrative,
        )
        self.assertNotIn(
            "with leading signals including limited tracked skills",
            narrative,
        )

    def test_does_not_repeat_signal_conviction(self):
        narrative = self.make_narrative(conviction="High")

        self.assertNotIn("Signal conviction is", narrative)

    def test_preserves_spaces_between_narrative_words(self):
        narrative = self.make_narrative(
            ai_concentration=10,
            top_skills=[("machine learning", 2)],
            hiring_archetype="Mixed Hiring Activity",
        )

        self.assertIn("machine learning", narrative)
        self.assertIn("is not", narrative)
        self.assertIn("with leading", narrative)
        self.assertIn("multiple functions", narrative)
        for joined_word in [
            "machinelearning",
            "isnot",
            "withleading",
            "multiplefunctions",
        ]:
            with self.subTest(joined_word=joined_word):
                self.assertNotIn(joined_word, narrative)


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
            "persistence_score": 0.7,
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
                "classify_company_trend",
                return_value="Expanding",
            ) as classify_trend,
            patch.object(
                company_intelligence,
                "classify_company_trend_confidence",
                return_value="Low",
            ) as classify_trend_confidence,
            patch.object(
                company_intelligence,
                "generate_company_trend_narrative",
                return_value="Trend explanation text.",
            ) as generate_trend_narrative,
            patch.object(
                company_intelligence,
                "generate_company_trend_confidence_narrative",
                return_value="Confidence explanation text.",
            ) as generate_trend_confidence_narrative,
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
        self.assertIn("Hiring trend: Expanding", report)
        self.assertIn("Trend explanation: Trend explanation text.", report)
        self.assertIn("Trend confidence: Low", report)
        self.assertIn(
            "Confidence explanation: Confidence explanation text.",
            report,
        )
        self.assertIn("Conviction: High", report)
        self.assertNotIn("observation window currently spans only 1.5 days", report)
        self.assertNotIn("Old Role", report)
        classify_trend.assert_called_once_with(history)
        classify_trend_confidence.assert_called_once_with(history)
        generate_trend_narrative.assert_called_once_with("Expanding", history)
        generate_trend_confidence_narrative.assert_called_once_with("Low", history)

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

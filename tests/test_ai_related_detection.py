import unittest
from unittest.mock import patch

import daily_report
from strategic_themes import detect_strategic_themes


def make_row(title, company, description=""):
    return (title, company, 100, description, "test")


def make_history(current_postings):
    return {
        "snapshots_active": 3,
        "current_postings": current_postings,
        "first_postings": current_postings,
        "observation_window_days": 1.0,
    }


class CanonicalAiRelatedDetectionTests(unittest.TestCase):
    def test_multiple_ai_aliases_count_as_one_ai_related_posting(self):
        rows = [
            make_row(
                "AI Account Executive",
                "Stripe",
                "Artificial intelligence, machine learning, LLM, and GenAI.",
            ),
        ]

        watchlist = daily_report.calculate_company_watchlist(rows)

        self.assertEqual(watchlist["Stripe"]["ai_postings"], 1)
        self.assertEqual(watchlist["Stripe"]["ai_concentration"], 100.0)

    def test_three_ai_sales_postings_out_of_ten_is_thirty_percent(self):
        rows = [
            make_row(
                "Account Executive, AI Sales",
                "Stripe",
                "Artificial intelligence and machine learning.",
            )
            for _ in range(3)
        ]
        rows.extend(
            make_row("Account Executive, Enterprise", "Stripe")
            for _ in range(7)
        )

        watchlist = daily_report.calculate_company_watchlist(rows)

        self.assertEqual(watchlist["Stripe"]["ai_postings"], 3)
        self.assertEqual(watchlist["Stripe"]["ai_concentration"], 30.0)

    def test_mistral_like_company_qualifies_as_ai_commercialization(self):
        rows = [
            make_row(
                "Account Executive, AI Sales",
                "Mistral",
                "Artificial intelligence and machine learning.",
            )
            for _ in range(10)
        ]

        with patch.object(
            daily_report,
            "get_company_history",
            return_value=make_history(10),
        ):
            intelligence_rows = daily_report.calculate_company_intelligence_rows(rows)

        self.assertEqual(
            intelligence_rows[0]["intelligence"],
            "AI Commercialization / GTM Expansion",
        )

    def test_stripe_like_company_does_not_qualify_as_ai_commercialization(self):
        rows = [
            make_row(
                "Account Executive, AI Sales",
                "Stripe",
                "Artificial intelligence and machine learning.",
            )
            for _ in range(3)
        ]
        rows.extend(
            make_row("Account Executive, Enterprise", "Stripe")
            for _ in range(7)
        )

        with patch.object(
            daily_report,
            "get_company_history",
            return_value=make_history(10),
        ):
            intelligence_rows = daily_report.calculate_company_intelligence_rows(rows)

        self.assertEqual(intelligence_rows[0]["ai_concentration"], 30.0)
        self.assertEqual(intelligence_rows[0]["intelligence"], "Sales Expansion")

    def test_single_company_ai_commercialization_does_not_create_theme(self):
        intelligence_rows = [
            {
                "company": "Mistral",
                "intelligence": "AI Commercialization / GTM Expansion",
            }
        ]

        self.assertEqual(detect_strategic_themes(intelligence_rows), [])


if __name__ == "__main__":
    unittest.main()

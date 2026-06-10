import unittest

import company_intelligence


def make_history(
    *,
    first_postings=10,
    current_postings=10,
    peak_postings=10,
    snapshots_active=12,
    persistence_score=0.75,
    observation_window_days=30,
):
    return {
        "first_postings": first_postings,
        "current_postings": current_postings,
        "peak_postings": peak_postings,
        "snapshots_active": snapshots_active,
        "persistence_score": persistence_score,
        "observation_window_days": observation_window_days,
    }


class CompanyTrendNarrativeTests(unittest.TestCase):
    def assert_narrative(self, expected, trend, **history_values):
        history = make_history(**history_values)
        self.assertEqual(
            company_intelligence.generate_company_trend_narrative(trend, history),
            expected,
        )

    def test_stable_unchanged(self):
        self.assert_narrative(
            "Current postings remain at 10, matching the first observed and peak levels.",
            "Stable",
        )

    def test_stable_below_threshold_movement(self):
        self.assert_narrative(
            "Current postings are 10, compared with 9 when first observed and an "
            "observed peak of 10; the changes do not meet the material expansion "
            "or contraction thresholds.",
            "Stable",
            first_postings=9,
        )

    def test_emerging(self):
        self.assert_narrative(
            "Hiring activity is newly observed, with 1 current posting across 1 "
            "active snapshot over 0.0 days.",
            "Emerging",
            first_postings=1,
            current_postings=1,
            peak_postings=1,
            snapshots_active=1,
            persistence_score=0.1,
            observation_window_days=0,
        )

    def test_expanding(self):
        self.assert_narrative(
            "Current postings increased from 7 to 10 and remain near the observed "
            "peak of 10.",
            "Expanding",
            first_postings=7,
        )

    def test_contracting_with_zero_current_postings(self):
        self.assert_narrative(
            "No postings are present in the latest snapshot, down from 10 when "
            "first observed and an observed peak of 10.",
            "Contracting",
            current_postings=0,
        )

    def test_contracting_with_nonzero_current_postings(self):
        self.assert_narrative(
            "Current postings declined from 10 to 7 and remain below the observed "
            "peak of 10.",
            "Contracting",
            current_postings=7,
        )

    def test_missing_history_returns_none(self):
        self.assertIsNone(
            company_intelligence.generate_company_trend_narrative("Stable", None)
        )


class CompanyTrendConfidenceNarrativeTests(unittest.TestCase):
    def assert_narrative(self, expected, confidence, **history_values):
        history = make_history(**history_values)
        self.assertEqual(
            company_intelligence.generate_company_trend_confidence_narrative(
                confidence,
                history,
            ),
            expected,
        )

    def test_low_confidence_with_single_reason(self):
        self.assert_narrative(
            "Trend confidence is low because the observation window is under 7 days.",
            "Low",
            observation_window_days=6.9,
        )

    def test_low_confidence_with_multiple_reasons(self):
        self.assert_narrative(
            "Trend confidence is low because the observation window is under 7 "
            "days, there are fewer than 6 active snapshots, and persistence is "
            "below 25%.",
            "Low",
            observation_window_days=6.9,
            snapshots_active=5,
            persistence_score=0.24,
        )

    def test_medium_confidence(self):
        self.assert_narrative(
            "Trend confidence is medium: the history clears the low-confidence "
            "thresholds but does not meet all established-history thresholds of "
            "30 days, 12 active snapshots, and 75% persistence.",
            "Medium",
            observation_window_days=29.9,
        )

    def test_high_confidence(self):
        self.assert_narrative(
            "Trend confidence is high: the history spans 30.0 days across 12 "
            "active snapshots, with 75.0% persistence.",
            "High",
        )

    def test_missing_history_returns_none(self):
        self.assertIsNone(
            company_intelligence.generate_company_trend_confidence_narrative(
                "Low",
                None,
            )
        )


if __name__ == "__main__":
    unittest.main()

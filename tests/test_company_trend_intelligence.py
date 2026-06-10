import unittest

import company_history


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


class CompanyTrendClassificationTests(unittest.TestCase):
    def assert_trend(self, expected, **history_values):
        history = make_history(**history_values)
        self.assertEqual(company_history.classify_company_trend(history), expected)

    def test_active_for_one_snapshot_is_emerging(self):
        self.assert_trend("Emerging", current_postings=1, snapshots_active=1)

    def test_active_under_one_day_despite_several_snapshots_is_emerging(self):
        self.assert_trend(
            "Emerging",
            current_postings=1,
            snapshots_active=8,
            observation_window_days=0.9,
        )

    def test_growth_from_seven_to_ten_at_peak_is_expanding(self):
        self.assert_trend(
            "Expanding",
            first_postings=7,
            current_postings=10,
            peak_postings=10,
        )

    def test_growth_from_nine_to_ten_is_stable(self):
        self.assert_trend(
            "Stable",
            first_postings=9,
            current_postings=10,
            peak_postings=10,
        )

    def test_growth_below_seventy_five_percent_of_peak_is_stable(self):
        self.assert_trend(
            "Stable",
            first_postings=10,
            current_postings=12,
            peak_postings=20,
        )

    def test_current_zero_is_contracting(self):
        self.assert_trend(
            "Contracting",
            first_postings=10,
            current_postings=0,
            peak_postings=10,
        )

    def test_material_decline_from_first_and_peak_is_contracting(self):
        self.assert_trend(
            "Contracting",
            first_postings=10,
            current_postings=7,
            peak_postings=10,
        )

    def test_small_decline_is_stable(self):
        self.assert_trend(
            "Stable",
            first_postings=10,
            current_postings=9,
            peak_postings=10,
        )

    def test_current_above_first_but_below_peak_is_stable(self):
        self.assert_trend(
            "Stable",
            first_postings=1,
            current_postings=5,
            peak_postings=10,
        )

    def test_equal_first_current_and_peak_is_stable(self):
        self.assert_trend(
            "Stable",
            first_postings=10,
            current_postings=10,
            peak_postings=10,
        )

    def test_current_zero_takes_precedence_over_emerging(self):
        self.assert_trend(
            "Contracting",
            first_postings=1,
            current_postings=0,
            peak_postings=1,
            snapshots_active=1,
            observation_window_days=0,
        )


class CompanyTrendConfidenceTests(unittest.TestCase):
    def assert_confidence(self, expected, **history_values):
        history = make_history(**history_values)
        self.assertEqual(
            company_history.classify_company_trend_confidence(history),
            expected,
        )

    def test_under_seven_days_is_low_confidence(self):
        self.assert_confidence("Low", observation_window_days=6.9)

    def test_fewer_than_six_active_snapshots_is_low_confidence(self):
        self.assert_confidence("Low", snapshots_active=5)

    def test_persistence_below_twenty_five_percent_is_low_confidence(self):
        self.assert_confidence("Low", persistence_score=0.24)

    def test_high_confidence_requires_all_high_thresholds(self):
        self.assert_confidence(
            "High",
            observation_window_days=30,
            snapshots_active=12,
            persistence_score=0.75,
        )

    def test_under_thirty_days_is_medium_confidence(self):
        self.assert_confidence("Medium", observation_window_days=29.9)

    def test_under_twelve_snapshots_is_medium_confidence(self):
        self.assert_confidence("Medium", snapshots_active=11)

    def test_persistence_below_seventy_five_percent_is_medium_confidence(self):
        self.assert_confidence("Medium", persistence_score=0.74)


if __name__ == "__main__":
    unittest.main()

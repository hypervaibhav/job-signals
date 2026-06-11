import unittest

try:
    import strategic_theme_confidence
except ModuleNotFoundError:
    strategic_theme_confidence = None


def make_history(
    *,
    current_company_count=2,
    snapshots_active=3,
    total_eligible_snapshots=6,
    persistence_score=0.50,
):
    return {
        "theme": "AI Product Expansion",
        "scope": "watchlist",
        "engine_version": "v2",
        "first_detected": 100,
        "latest_detected": 600,
        "snapshots_active": snapshots_active,
        "total_eligible_snapshots": total_eligible_snapshots,
        "persistence_score": persistence_score,
        "latest_snapshot_time": 600,
        "current_company_count": current_company_count,
        "peak_company_count": max(current_company_count, 2),
        "current_companies": [],
        "snapshots": [],
    }


class StrategicThemeConfidenceTests(unittest.TestCase):
    def confidence_module(self):
        self.assertIsNotNone(
            strategic_theme_confidence,
            "strategic_theme_confidence.py must implement theme confidence "
            "classification",
        )
        return strategic_theme_confidence

    def assert_confidence(self, expected, lifecycle, history):
        module = self.confidence_module()
        self.assertEqual(
            module.classify_theme_confidence(history, lifecycle),
            expected,
        )

    def test_missing_history_is_low_confidence(self):
        self.assert_confidence("Low", "Stable", None)

    def test_zero_current_company_count_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Stable",
            make_history(current_company_count=0),
        )

    def test_disappeared_lifecycle_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Disappeared",
            make_history(current_company_count=2),
        )

    def test_single_company_theme_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Stable",
            make_history(current_company_count=1),
        )

    def test_fewer_than_two_active_snapshots_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Stable",
            make_history(snapshots_active=1),
        )

    def test_fewer_than_three_eligible_snapshots_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Stable",
            make_history(total_eligible_snapshots=2),
        )

    def test_persistence_below_twenty_five_percent_is_low_confidence(self):
        self.assert_confidence(
            "Low",
            "Stable",
            make_history(persistence_score=0.24),
        )

    def test_stable_theme_meeting_all_high_gates_is_high_confidence(self):
        self.assert_confidence(
            "High",
            "Stable",
            make_history(),
        )

    def test_expanding_theme_meeting_all_high_gates_is_high_confidence(self):
        self.assert_confidence(
            "High",
            "Expanding",
            make_history(),
        )

    def test_high_confidence_requires_stable_or_expanding_lifecycle(self):
        self.assert_confidence(
            "Moderate",
            "Contracting",
            make_history(),
        )

    def test_high_confidence_requires_at_least_three_active_snapshots(self):
        self.assert_confidence(
            "Moderate",
            "Stable",
            make_history(snapshots_active=2, persistence_score=0.50),
        )

    def test_high_confidence_requires_at_least_six_eligible_snapshots(self):
        self.assert_confidence(
            "Moderate",
            "Stable",
            make_history(total_eligible_snapshots=5, persistence_score=0.50),
        )

    def test_high_confidence_requires_persistence_at_least_fifty_percent(self):
        self.assert_confidence(
            "Moderate",
            "Stable",
            make_history(persistence_score=0.49),
        )

    def test_moderate_confidence_covers_active_multi_company_unestablished_theme(self):
        self.assert_confidence(
            "Moderate",
            "Emerging",
            make_history(
                current_company_count=2,
                snapshots_active=2,
                total_eligible_snapshots=4,
                persistence_score=0.50,
            ),
        )


if __name__ == "__main__":
    unittest.main()

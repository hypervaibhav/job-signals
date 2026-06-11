import unittest

try:
    import strategic_theme_lifecycle
except ModuleNotFoundError:
    strategic_theme_lifecycle = None


def make_snapshot(snapshot_time, company_count, companies=None):
    return {
        "snapshot_time": snapshot_time,
        "company_count": company_count,
        "eligible_company_count": 10,
        "companies": companies or [],
    }


def make_history(snapshots):
    active_snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot["company_count"] > 0
    ]
    latest_snapshot = snapshots[-1]

    return {
        "theme": "AI Product Expansion",
        "scope": "watchlist",
        "engine_version": "v2",
        "first_detected": (
            active_snapshots[0]["snapshot_time"]
            if active_snapshots
            else None
        ),
        "latest_detected": (
            active_snapshots[-1]["snapshot_time"]
            if active_snapshots
            else None
        ),
        "snapshots_active": len(active_snapshots),
        "total_eligible_snapshots": len(snapshots),
        "persistence_score": (
            len(active_snapshots) / len(snapshots)
            if snapshots
            else 0
        ),
        "latest_snapshot_time": latest_snapshot["snapshot_time"],
        "current_company_count": latest_snapshot["company_count"],
        "peak_company_count": max(
            snapshot["company_count"] for snapshot in snapshots
        ),
        "current_companies": latest_snapshot["companies"],
        "snapshots": snapshots,
    }


class StrategicThemeLifecycleTests(unittest.TestCase):
    def lifecycle_module(self):
        self.assertIsNotNone(
            strategic_theme_lifecycle,
            "strategic_theme_lifecycle.py must implement lifecycle "
            "classification",
        )
        return strategic_theme_lifecycle

    def assert_lifecycle(self, expected, history):
        module = self.lifecycle_module()
        self.assertEqual(module.classify_theme_lifecycle(history), expected)

    def test_missing_history_returns_none(self):
        self.assert_lifecycle(None, None)

    def test_never_detected_zero_count_theme_returns_stable(self):
        self.assert_lifecycle(
            "Stable",
            make_history([
                make_snapshot(100, 0),
                make_snapshot(200, 0),
            ]),
        )

    def test_single_active_snapshot_returns_emerging(self):
        self.assert_lifecycle(
            "Emerging",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
            ]),
        )

    def test_two_active_snapshots_returns_emerging(self):
        self.assert_lifecycle(
            "Emerging",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 1, ["Integrate"]),
            ]),
        )

    def test_three_active_snapshots_with_equal_counts_returns_stable(self):
        self.assert_lifecycle(
            "Stable",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 1, ["Integrate"]),
                make_snapshot(300, 1, ["Integrate"]),
            ]),
        )

    def test_growth_from_one_to_two_at_peak_returns_expanding(self):
        self.assert_lifecycle(
            "Expanding",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 1, ["Integrate"]),
                make_snapshot(300, 2, ["Integrate", "Levelai"]),
            ]),
        )

    def test_growth_below_seventy_five_percent_of_peak_returns_stable(self):
        self.assert_lifecycle(
            "Stable",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(
                    200,
                    4,
                    ["Integrate", "Levelai", "Mistral", "Ryzlabs"],
                ),
                make_snapshot(300, 2, ["Integrate", "Levelai"]),
            ]),
        )

    def test_decline_from_two_to_one_from_peak_returns_contracting(self):
        self.assert_lifecycle(
            "Contracting",
            make_history([
                make_snapshot(100, 2, ["Integrate", "Levelai"]),
                make_snapshot(200, 2, ["Integrate", "Levelai"]),
                make_snapshot(300, 1, ["Integrate"]),
            ]),
        )

    def test_latest_zero_after_prior_activity_returns_disappeared(self):
        self.assert_lifecycle(
            "Disappeared",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 0),
            ]),
        )

    def test_latest_zero_with_no_prior_activity_remains_stable(self):
        self.assert_lifecycle(
            "Stable",
            make_history([
                make_snapshot(100, 0),
                make_snapshot(200, 0),
                make_snapshot(300, 0),
            ]),
        )

    def test_disappeared_takes_precedence_over_emerging(self):
        self.assert_lifecycle(
            "Disappeared",
            make_history([
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 0),
            ]),
        )

    def test_membership_changes_with_unchanged_count_remain_stable(self):
        self.assert_lifecycle(
            "Stable",
            make_history([
                make_snapshot(100, 2, ["Integrate", "Levelai"]),
                make_snapshot(200, 2, ["Levelai", "Ryzlabs"]),
                make_snapshot(300, 2, ["Mistral", "Ryzlabs"]),
            ]),
        )


if __name__ == "__main__":
    unittest.main()

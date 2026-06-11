import unittest

try:
    import strategic_theme_narratives
except ModuleNotFoundError:
    strategic_theme_narratives = None


def make_snapshot(snapshot_time, company_count, companies=None):
    return {
        "snapshot_time": snapshot_time,
        "company_count": company_count,
        "eligible_company_count": 10,
        "companies": companies or [],
    }


def make_history(theme="AI Product Expansion", snapshots=None):
    snapshots = snapshots or [
        make_snapshot(100, 1, ["Integrate"]),
    ]
    active_snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot["company_count"] > 0
    ]
    latest_snapshot = snapshots[-1]

    return {
        "theme": theme,
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


class StrategicThemeNarrativeTests(unittest.TestCase):
    def narrative_module(self):
        self.assertIsNotNone(
            strategic_theme_narratives,
            "strategic_theme_narratives.py must implement deterministic "
            "theme lifecycle narratives",
        )
        return strategic_theme_narratives

    def assert_narrative(self, expected, lifecycle, history):
        module = self.narrative_module()
        self.assertEqual(
            module.generate_theme_lifecycle_narrative(lifecycle, history),
            expected,
        )

    def test_missing_history_returns_none(self):
        module = self.narrative_module()
        self.assertIsNone(
            module.generate_theme_lifecycle_narrative("Stable", None)
        )

    def test_unknown_lifecycle_returns_none(self):
        self.assert_narrative(
            None,
            "Accelerating",
            make_history(),
        )

    def test_emerging_explains_new_detection_under_three_active_snapshots(self):
        self.assert_narrative(
            "AI Product Expansion is newly detected, appearing in 2 active "
            "snapshots out of 4 eligible snapshots, which is fewer than the "
            "3 active snapshots needed for an established lifecycle. Current "
            "coverage is 1 company.",
            "Emerging",
            make_history(
                snapshots=[
                    make_snapshot(100, 1, ["Integrate"]),
                    make_snapshot(200, 0),
                    make_snapshot(300, 1, ["Integrate"]),
                    make_snapshot(400, 1, ["Integrate"]),
                ]
            ),
        )

    def test_expanding_explains_growth_from_first_active_count_and_near_peak(self):
        self.assert_narrative(
            "AI Product Expansion expanded from 1 company when first detected "
            "to 2 companies now, remaining near the observed peak of 2 companies "
            "across 3 eligible snapshots.",
            "Expanding",
            make_history(
                snapshots=[
                    make_snapshot(100, 0),
                    make_snapshot(200, 1, ["Integrate"]),
                    make_snapshot(300, 1, ["Integrate"]),
                    make_snapshot(400, 2, ["Integrate", "Levelai"]),
                ]
            ),
        )

    def test_stable_active_history_explains_below_threshold_movement(self):
        self.assert_narrative(
            "AI Product Expansion is stable at 2 companies, with an observed "
            "peak of 4 companies across 3 active snapshots out of 3 eligible "
            "snapshots; current movement does not meet expansion or contraction "
            "thresholds.",
            "Stable",
            make_history(
                snapshots=[
                    make_snapshot(100, 1, ["Integrate"]),
                    make_snapshot(
                        200,
                        4,
                        ["Integrate", "Levelai", "Mistral", "Ryzlabs"],
                    ),
                    make_snapshot(300, 2, ["Integrate", "Levelai"]),
                ]
            ),
        )

    def test_stable_never_detected_explains_no_matching_companies(self):
        self.assert_narrative(
            "AI Research Expansion has not matched any companies across "
            "3 eligible snapshots.",
            "Stable",
            make_history(
                theme="AI Research Expansion",
                snapshots=[
                    make_snapshot(100, 0),
                    make_snapshot(200, 0),
                    make_snapshot(300, 0),
                ],
            ),
        )

    def test_contracting_explains_decline_from_first_active_count_and_peak(self):
        self.assert_narrative(
            "AI Product Expansion contracted from 2 companies when first "
            "detected to 1 company now, below the observed peak of 2 companies "
            "across 3 eligible snapshots.",
            "Contracting",
            make_history(
                snapshots=[
                    make_snapshot(100, 2, ["Integrate", "Levelai"]),
                    make_snapshot(200, 2, ["Integrate", "Levelai"]),
                    make_snapshot(300, 1, ["Integrate"]),
                ]
            ),
        )

    def test_disappeared_explains_prior_detection_and_zero_latest_count(self):
        self.assert_narrative(
            "AI Product Expansion was previously detected in 1 active snapshot "
            "out of 2 eligible snapshots, but has 0 companies in the latest "
            "snapshot.",
            "Disappeared",
            make_history(
                snapshots=[
                    make_snapshot(100, 1, ["Integrate"]),
                    make_snapshot(200, 0),
                ]
            ),
        )

    def test_simple_pluralization_for_single_counts(self):
        self.assert_narrative(
            "AI Product Expansion is newly detected, appearing in 1 active "
            "snapshot out of 1 eligible snapshot, which is fewer than the "
            "3 active snapshots needed for an established lifecycle. Current "
            "coverage is 1 company.",
            "Emerging",
            make_history(
                snapshots=[
                    make_snapshot(100, 1, ["Integrate"]),
                ]
            ),
        )

    def test_narrative_does_not_list_current_members(self):
        history = make_history(
            snapshots=[
                make_snapshot(100, 1, ["Integrate"]),
                make_snapshot(200, 1, ["Integrate"]),
            ]
        )

        module = self.narrative_module()
        narrative = module.generate_theme_lifecycle_narrative(
            "Emerging",
            history,
        )

        self.assertNotIn("Integrate", narrative)


if __name__ == "__main__":
    unittest.main()

import unittest

try:
    import strategic_theme_membership
except ModuleNotFoundError:
    strategic_theme_membership = None


def make_snapshot(snapshot_time, companies, eligible_company_count=10):
    return {
        "snapshot_time": snapshot_time,
        "company_count": len(companies),
        "eligible_company_count": eligible_company_count,
        "companies": companies,
    }


def make_history(snapshots):
    latest_snapshot = snapshots[-1] if snapshots else None
    return {
        "theme": "AI Product Expansion",
        "current_company_count": (
            latest_snapshot["company_count"] if latest_snapshot else 0
        ),
        "current_companies": (
            latest_snapshot["companies"] if latest_snapshot else []
        ),
        "snapshots": snapshots,
    }


class StrategicThemeMembershipChangeTests(unittest.TestCase):
    def membership_module(self):
        self.assertIsNotNone(
            strategic_theme_membership,
            "strategic_theme_membership.py must implement membership changes",
        )
        return strategic_theme_membership

    def calculate(self, history):
        return self.membership_module().calculate_theme_membership_change(
            history
        )

    def test_missing_history_returns_insufficient_history(self):
        change = self.calculate(None)

        self.assertEqual(change["movement_label"], "Insufficient history")
        self.assertFalse(change["membership_changed"])
        self.assertFalse(change["meaningful_movement"])
        self.assertIsNone(change["current_snapshot_time"])
        self.assertIsNone(change["prior_snapshot_time"])

    def test_fewer_than_two_eligible_snapshots_returns_insufficient_history(self):
        history = make_history([
            make_snapshot(100, ["Integrate"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["movement_label"], "Insufficient history")
        self.assertEqual(change["current_members"], ["Integrate"])
        self.assertEqual(change["prior_members"], [])
        self.assertFalse(change["membership_changed"])

    def test_zero_eligible_snapshot_is_skipped(self):
        history = make_history([
            make_snapshot(100, ["Integrate"]),
            make_snapshot(200, [], eligible_company_count=0),
            make_snapshot(300, ["Integrate", "Levelai"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["prior_snapshot_time"], 100)
        self.assertEqual(change["current_snapshot_time"], 300)
        self.assertEqual(change["entrants"], ["Levelai"])
        self.assertEqual(change["movement_label"], "Expanded membership")

    def test_no_membership_change(self):
        history = make_history([
            make_snapshot(100, ["Integrate", "Levelai"]),
            make_snapshot(200, ["Levelai", "Integrate"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["current_members"], ["Integrate", "Levelai"])
        self.assertEqual(change["prior_members"], ["Integrate", "Levelai"])
        self.assertEqual(change["entrants"], [])
        self.assertEqual(change["exits"], [])
        self.assertEqual(change["retained_members"], ["Integrate", "Levelai"])
        self.assertEqual(change["net_company_change"], 0)
        self.assertFalse(change["membership_changed"])
        self.assertFalse(change["meaningful_movement"])
        self.assertEqual(change["movement_label"], "No membership change")

    def test_entrant_detected(self):
        history = make_history([
            make_snapshot(100, ["Integrate"]),
            make_snapshot(200, ["Integrate", "Levelai"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], ["Levelai"])
        self.assertEqual(change["exits"], [])
        self.assertEqual(change["net_company_change"], 1)
        self.assertTrue(change["membership_changed"])
        self.assertTrue(change["meaningful_movement"])
        self.assertEqual(change["movement_label"], "Expanded membership")

    def test_exit_detected(self):
        history = make_history([
            make_snapshot(100, ["Integrate", "Levelai"]),
            make_snapshot(200, ["Levelai"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], [])
        self.assertEqual(change["exits"], ["Integrate"])
        self.assertEqual(change["net_company_change"], -1)
        self.assertEqual(change["movement_label"], "Contracted membership")

    def test_retained_members(self):
        history = make_history([
            make_snapshot(100, ["Integrate", "Levelai"]),
            make_snapshot(200, ["Levelai", "Ryzlabs"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["retained_members"], ["Levelai"])

    def test_new_contributor(self):
        history = make_history([
            make_snapshot(100, ["Integrate"]),
            make_snapshot(200, ["Integrate", "Levelai"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["new_contributors"], ["Levelai"])
        self.assertEqual(change["returning_members"], [])

    def test_returning_member(self):
        history = make_history([
            make_snapshot(100, ["Ryzlabs"]),
            make_snapshot(200, ["Integrate"]),
            make_snapshot(300, ["Integrate", "Ryzlabs"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], ["Ryzlabs"])
        self.assertEqual(change["new_contributors"], [])
        self.assertEqual(change["returning_members"], ["Ryzlabs"])

    def test_rotated_membership(self):
        history = make_history([
            make_snapshot(100, ["Integrate", "Levelai"]),
            make_snapshot(200, ["Levelai", "Ryzlabs"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], ["Ryzlabs"])
        self.assertEqual(change["exits"], ["Integrate"])
        self.assertEqual(change["net_company_change"], 0)
        self.assertTrue(change["meaningful_movement"])
        self.assertEqual(change["movement_label"], "Rotated membership")

    def test_newly_active(self):
        history = make_history([
            make_snapshot(100, []),
            make_snapshot(200, ["Integrate"]),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], ["Integrate"])
        self.assertEqual(change["exits"], [])
        self.assertEqual(change["movement_label"], "Newly active")
        self.assertTrue(change["meaningful_movement"])

    def test_disappeared(self):
        history = make_history([
            make_snapshot(100, ["Integrate"]),
            make_snapshot(200, []),
        ])

        change = self.calculate(history)

        self.assertEqual(change["entrants"], [])
        self.assertEqual(change["exits"], ["Integrate"])
        self.assertEqual(change["movement_label"], "Disappeared")
        self.assertTrue(change["meaningful_movement"])


if __name__ == "__main__":
    unittest.main()

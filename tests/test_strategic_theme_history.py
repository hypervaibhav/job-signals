import sqlite3
import unittest

try:
    import strategic_theme_history
except ModuleNotFoundError:
    strategic_theme_history = None


def make_theme(theme, companies):
    return {
        "theme": theme,
        "company_count": len(companies),
        "companies": companies,
    }


def make_complete_snapshot(
    commercialization=None,
    product=None,
    research=None,
):
    return [
        make_theme("AI Commercialization", commercialization or []),
        make_theme("AI Product Expansion", product or []),
        make_theme("AI Research Expansion", research or []),
    ]


class StrategicThemeHistoryCharacterizationTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def history_module(self):
        self.assertIsNotNone(
            strategic_theme_history,
            "strategic_theme_history.py must implement the persistence contract",
        )
        return strategic_theme_history

    def initialize(self):
        module = self.history_module()
        module.initialize_strategic_theme_history(self.conn)
        return module

    def test_saves_complete_theme_snapshot_including_singletons_and_zero_counts(self):
        module = self.initialize()
        themes = make_complete_snapshot(
            commercialization=["Mistral"],
            product=["Integrate", "Levelai"],
        )

        module.save_theme_snapshot(
            self.conn,
            snapshot_time=100,
            themes=themes,
            eligible_company_count=10,
        )

        self.assertEqual(
            module.get_latest_theme_snapshot(self.conn),
            [
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2",
                    "theme": "AI Commercialization",
                    "company_count": 1,
                    "eligible_company_count": 10,
                    "companies": ["Mistral"],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2",
                    "theme": "AI Product Expansion",
                    "company_count": 2,
                    "eligible_company_count": 10,
                    "companies": ["Integrate", "Levelai"],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2",
                    "theme": "AI Research Expansion",
                    "company_count": 0,
                    "eligible_company_count": 10,
                    "companies": [],
                },
            ],
        )

    def test_exact_company_membership_is_persisted(self):
        module = self.initialize()
        themes = make_complete_snapshot(product=["Levelai", "Integrate"])

        module.save_theme_snapshot(self.conn, 100, themes, 10)

        latest = module.get_latest_theme_snapshot(self.conn)
        product = next(
            row for row in latest if row["theme"] == "AI Product Expansion"
        )
        self.assertEqual(product["companies"], ["Integrate", "Levelai"])
        self.assertEqual(product["company_count"], 2)

    def test_saving_same_snapshot_twice_is_idempotent(self):
        module = self.initialize()
        themes = make_complete_snapshot(product=["Integrate", "Levelai"])

        module.save_theme_snapshot(self.conn, 100, themes, 10)
        module.save_theme_snapshot(self.conn, 100, themes, 10)

        snapshots = self.conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_snapshots"
        ).fetchone()[0]
        memberships = self.conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_companies"
        ).fetchone()[0]
        self.assertEqual(snapshots, 3)
        self.assertEqual(memberships, 2)

    def test_resaving_snapshot_replaces_stale_membership(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            10,
        )

        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate", "Ryzlabs"]),
            10,
        )

        product = next(
            row
            for row in module.get_latest_theme_snapshot(self.conn)
            if row["theme"] == "AI Product Expansion"
        )
        self.assertEqual(product["companies"], ["Integrate", "Ryzlabs"])
        self.assertEqual(product["company_count"], 2)

    def test_scope_isolation(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Watchlist Co"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Market Co"]),
            50,
            scope="market",
        )

        watchlist = module.get_latest_theme_snapshot(self.conn)
        market = module.get_latest_theme_snapshot(self.conn, scope="market")

        self.assertEqual(watchlist[1]["companies"], ["Watchlist Co"])
        self.assertEqual(watchlist[1]["snapshot_time"], 100)
        self.assertEqual(market[1]["companies"], ["Market Co"])
        self.assertEqual(market[1]["snapshot_time"], 200)

    def test_engine_version_isolation(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["V2 Co"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["V3 Co"]),
            10,
            engine_version="v3",
        )

        v2 = module.get_theme_history(self.conn, "AI Product Expansion")
        v3 = module.get_theme_history(
            self.conn,
            "AI Product Expansion",
            engine_version="v3",
        )

        self.assertEqual(v2["current_companies"], ["V2 Co"])
        self.assertEqual(v2["latest_snapshot_time"], 100)
        self.assertEqual(v3["current_companies"], ["V3 Co"])
        self.assertEqual(v3["latest_snapshot_time"], 200)

    def test_history_calculates_detection_times_active_snapshots_and_persistence(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Integrate"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            300,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            400,
            make_complete_snapshot(),
            10,
        )

        history = module.get_theme_history(self.conn, "AI Product Expansion")

        self.assertEqual(history["first_detected"], 200)
        self.assertEqual(history["latest_detected"], 300)
        self.assertEqual(history["snapshots_active"], 2)
        self.assertEqual(history["total_eligible_snapshots"], 4)
        self.assertAlmostEqual(history["persistence_score"], 0.5)

    def test_zero_eligible_company_snapshots_do_not_reduce_persistence(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(),
            0,
        )

        history = module.get_theme_history(self.conn, "AI Product Expansion")

        self.assertEqual(history["snapshots_active"], 1)
        self.assertEqual(history["total_eligible_snapshots"], 1)
        self.assertAlmostEqual(history["persistence_score"], 1.0)

    def test_history_calculates_current_and_peak_company_counts(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(
                product=["Integrate", "Levelai", "Ryzlabs"]
            ),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            300,
            make_complete_snapshot(product=["Levelai", "Ryzlabs"]),
            10,
        )

        history = module.get_theme_history(self.conn, "AI Product Expansion")

        self.assertEqual(history["current_company_count"], 2)
        self.assertEqual(history["peak_company_count"], 3)
        self.assertEqual(history["current_companies"], ["Levelai", "Ryzlabs"])

    def test_theme_disappearance_from_latest_snapshot_is_preserved(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(commercialization=["Mistral"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(),
            10,
        )

        history = module.get_theme_history(self.conn, "AI Commercialization")

        self.assertEqual(history["first_detected"], 100)
        self.assertEqual(history["latest_detected"], 100)
        self.assertEqual(history["latest_snapshot_time"], 200)
        self.assertEqual(history["current_company_count"], 0)
        self.assertEqual(history["current_companies"], [])

    def test_membership_changes_are_preserved_when_count_is_unchanged(self):
        module = self.initialize()
        module.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Integrate", "Levelai"]),
            10,
        )
        module.save_theme_snapshot(
            self.conn,
            200,
            make_complete_snapshot(product=["Levelai", "Ryzlabs"]),
            10,
        )

        history = module.get_theme_history(self.conn, "AI Product Expansion")

        self.assertEqual(
            history["snapshots"],
            [
                {
                    "snapshot_time": 100,
                    "company_count": 2,
                    "eligible_company_count": 10,
                    "companies": ["Integrate", "Levelai"],
                },
                {
                    "snapshot_time": 200,
                    "company_count": 2,
                    "eligible_company_count": 10,
                    "companies": ["Levelai", "Ryzlabs"],
                },
            ],
        )

    def test_fresh_database_initialization_and_reads_succeed(self):
        module = self.history_module()

        module.initialize_strategic_theme_history(self.conn)
        module.initialize_strategic_theme_history(self.conn)

        self.assertEqual(module.get_latest_theme_snapshot(self.conn), [])
        self.assertIsNone(
            module.get_theme_history(self.conn, "AI Product Expansion")
        )


if __name__ == "__main__":
    unittest.main()

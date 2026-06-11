import sqlite3
import unittest
from unittest.mock import patch

import strategic_theme_history

try:
    import strategic_theme_backfill
except ModuleNotFoundError:
    strategic_theme_backfill = None


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
    revenue=None,
    engineering=None,
    data=None,
):
    return [
        make_theme("AI Commercialization", commercialization or []),
        make_theme("AI Product Expansion", product or []),
        make_theme("AI Research Expansion", research or []),
        make_theme("Revenue / GTM Expansion", revenue or []),
        make_theme("Engineering Platform Expansion", engineering or []),
        make_theme("Data & Analytics Investment", data or []),
    ]


def make_intelligence_row(company, intelligence):
    return {
        "company": company,
        "intelligence": intelligence,
    }


class StrategicThemeBackfillCharacterizationTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            """
            CREATE TABLE job_snapshots (
                snapshot_time INTEGER,
                title TEXT,
                company TEXT,
                description TEXT,
                source TEXT
            )
            """
        )

    def tearDown(self):
        self.conn.close()

    def backfill_module(self):
        self.assertIsNotNone(
            strategic_theme_backfill,
            "strategic_theme_backfill.py must implement the historical "
            "theme backfill contract",
        )
        return strategic_theme_backfill

    def insert_snapshot_row(
        self,
        snapshot_time,
        title="AI Account Executive",
        company="Mistral",
        description="AI sales",
        source="lever",
    ):
        self.conn.execute(
            """
            INSERT INTO job_snapshots (
                snapshot_time,
                title,
                company,
                description,
                source
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (snapshot_time, title, company, description, source),
        )
        self.conn.commit()

    def run_backfill(self, **kwargs):
        module = self.backfill_module()
        return module.backfill_strategic_theme_history(self.conn, **kwargs)

    def test_backfill_reads_snapshot_times_in_ascending_order(self):
        module = self.backfill_module()
        for snapshot_time in [300, 100, 200]:
            self.insert_snapshot_row(snapshot_time)

        reconstructed_snapshot_times = []
        saved_snapshot_times = []

        def reconstruct(rows):
            reconstructed_snapshot_times.append(rows[0][2])
            return [make_intelligence_row("Mistral", "AI Product Expansion")]

        def save_snapshot(conn, snapshot_time, themes, **kwargs):
            saved_snapshot_times.append(snapshot_time)

        with (
            patch.object(
                module,
                "calculate_company_intelligence_rows",
                side_effect=reconstruct,
                create=True,
            ),
            patch.object(
                module,
                "calculate_theme_snapshot",
                return_value=make_complete_snapshot(product=["Mistral"]),
                create=True,
            ),
            patch.object(
                module,
                "save_theme_snapshot",
                side_effect=save_snapshot,
                create=True,
            ),
        ):
            self.run_backfill()

        self.assertEqual(reconstructed_snapshot_times, [100, 200, 300])
        self.assertEqual(saved_snapshot_times, [100, 200, 300])

    def test_backfill_uses_historical_snapshot_time_when_saving(self):
        module = self.backfill_module()
        self.insert_snapshot_row(123)
        themes = make_complete_snapshot(product=["Mistral"])

        with (
            patch.object(
                module,
                "calculate_company_intelligence_rows",
                return_value=[
                    make_intelligence_row("Mistral", "AI Product Expansion")
                ],
                create=True,
            ),
            patch.object(
                module,
                "calculate_theme_snapshot",
                return_value=themes,
                create=True,
            ),
            patch.object(
                module,
                "save_theme_snapshot",
                create=True,
            ) as save_snapshot,
        ):
            self.run_backfill()

        save_snapshot.assert_called_once_with(
            self.conn,
            123,
            themes,
            eligible_company_count=1,
            scope="watchlist",
            engine_version="v2-backfill",
        )

    def test_backfill_calculates_theme_snapshot_not_presentation_themes(self):
        module = self.backfill_module()
        self.insert_snapshot_row(100)
        intelligence_rows = [
            make_intelligence_row(
                "Mistral",
                "AI Commercialization / GTM Expansion",
            )
        ]
        themes = make_complete_snapshot(commercialization=["Mistral"])

        with (
            patch.object(
                module,
                "calculate_company_intelligence_rows",
                return_value=intelligence_rows,
                create=True,
            ),
            patch.object(
                module,
                "calculate_theme_snapshot",
                return_value=themes,
                create=True,
            ) as calculate_snapshot,
            patch.object(
                module,
                "detect_strategic_themes",
                create=True,
            ) as detect_themes,
            patch.object(
                module,
                "save_theme_snapshot",
                create=True,
            ),
        ):
            self.run_backfill()

        calculate_snapshot.assert_called_once_with(intelligence_rows)
        detect_themes.assert_not_called()

    def test_backfill_persists_singleton_and_zero_count_themes(self):
        module = self.backfill_module()
        strategic_theme_history.initialize_strategic_theme_history(self.conn)
        self.insert_snapshot_row(100)

        with patch.object(
            module,
            "calculate_company_intelligence_rows",
            return_value=[
                make_intelligence_row("Mistral", "AI Product Expansion")
            ],
            create=True,
        ):
            self.run_backfill()

        latest = strategic_theme_history.get_latest_theme_snapshot(
            self.conn,
            engine_version="v2-backfill",
        )

        self.assertEqual(
            latest,
            [
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "AI Commercialization",
                    "company_count": 0,
                    "eligible_company_count": 1,
                    "companies": [],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "AI Product Expansion",
                    "company_count": 1,
                    "eligible_company_count": 1,
                    "companies": ["Mistral"],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "AI Research Expansion",
                    "company_count": 0,
                    "eligible_company_count": 1,
                    "companies": [],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "Data & Analytics Investment",
                    "company_count": 0,
                    "eligible_company_count": 1,
                    "companies": [],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "Engineering Platform Expansion",
                    "company_count": 0,
                    "eligible_company_count": 1,
                    "companies": [],
                },
                {
                    "snapshot_time": 100,
                    "scope": "watchlist",
                    "engine_version": "v2-backfill",
                    "theme": "Revenue / GTM Expansion",
                    "company_count": 0,
                    "eligible_company_count": 1,
                    "companies": [],
                },
            ],
        )

    def test_backfill_passes_eligible_company_count_from_intelligence_rows(self):
        module = self.backfill_module()
        self.insert_snapshot_row(100)
        intelligence_rows = [
            make_intelligence_row("Mistral", "AI Product Expansion"),
            make_intelligence_row("Levelai", "AI Product Expansion"),
        ]
        themes = make_complete_snapshot(product=["Mistral", "Levelai"])

        with (
            patch.object(
                module,
                "calculate_company_intelligence_rows",
                return_value=intelligence_rows,
                create=True,
            ),
            patch.object(
                module,
                "calculate_theme_snapshot",
                return_value=themes,
                create=True,
            ),
            patch.object(
                module,
                "save_theme_snapshot",
                create=True,
            ) as save_snapshot,
        ):
            self.run_backfill()

        self.assertEqual(
            save_snapshot.call_args.kwargs["eligible_company_count"],
            2,
        )

    def test_backfill_defaults_to_backfill_engine_version(self):
        module = self.backfill_module()
        strategic_theme_history.initialize_strategic_theme_history(self.conn)
        self.insert_snapshot_row(100)

        with patch.object(
            module,
            "calculate_company_intelligence_rows",
            return_value=[
                make_intelligence_row("Mistral", "AI Product Expansion")
            ],
            create=True,
        ):
            self.run_backfill()

        engine_versions = [
            row[0]
            for row in self.conn.execute(
                """
                SELECT DISTINCT engine_version
                FROM strategic_theme_snapshots
                ORDER BY engine_version
                """
            ).fetchall()
        ]
        self.assertEqual(engine_versions, ["v2-backfill"])

    def test_backfill_does_not_overwrite_live_v2_history_by_default(self):
        module = self.backfill_module()
        strategic_theme_history.initialize_strategic_theme_history(self.conn)
        strategic_theme_history.save_theme_snapshot(
            self.conn,
            100,
            make_complete_snapshot(product=["Live Co"]),
            eligible_company_count=1,
            engine_version="v2",
        )
        self.insert_snapshot_row(100)

        with patch.object(
            module,
            "calculate_company_intelligence_rows",
            return_value=[
                make_intelligence_row("Mistral", "AI Product Expansion")
            ],
            create=True,
        ):
            self.run_backfill()

        live_history = strategic_theme_history.get_theme_history(
            self.conn,
            "AI Product Expansion",
            engine_version="v2",
        )
        backfill_history = strategic_theme_history.get_theme_history(
            self.conn,
            "AI Product Expansion",
            engine_version="v2-backfill",
        )

        self.assertEqual(live_history["current_companies"], ["Live Co"])
        self.assertEqual(backfill_history["current_companies"], ["Mistral"])

    def test_backfill_is_idempotent_when_run_twice(self):
        module = self.backfill_module()
        strategic_theme_history.initialize_strategic_theme_history(self.conn)
        self.insert_snapshot_row(100)

        with patch.object(
            module,
            "calculate_company_intelligence_rows",
            return_value=[
                make_intelligence_row("Mistral", "AI Product Expansion")
            ],
            create=True,
        ):
            self.run_backfill()
            self.run_backfill()

        snapshot_count = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM strategic_theme_snapshots
            WHERE engine_version = 'v2-backfill'
            """
        ).fetchone()[0]
        membership_count = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM strategic_theme_companies
            WHERE engine_version = 'v2-backfill'
            """
        ).fetchone()[0]

        self.assertEqual(snapshot_count, 6)
        self.assertEqual(membership_count, 1)

    def test_empty_job_snapshots_succeeds_without_writing_theme_history(self):
        strategic_theme_history.initialize_strategic_theme_history(self.conn)

        self.run_backfill()

        snapshot_count = self.conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_snapshots"
        ).fetchone()[0]
        membership_count = self.conn.execute(
            "SELECT COUNT(*) FROM strategic_theme_companies"
        ).fetchone()[0]

        self.assertEqual(snapshot_count, 0)
        self.assertEqual(membership_count, 0)

    def test_backfill_uses_company_intelligence_rows_as_eligible_scope(self):
        module = self.backfill_module()
        self.insert_snapshot_row(
            100,
            title="AI Account Executive",
            company="Mistral",
            description="AI sales",
        )
        self.insert_snapshot_row(
            100,
            title="AI Engineer",
            company="Not Watchlisted",
            description="AI platform",
        )
        eligible_rows = [
            make_intelligence_row(
                "Mistral",
                "AI Commercialization / GTM Expansion",
            )
        ]

        with (
            patch.object(
                module,
                "calculate_company_intelligence_rows",
                return_value=eligible_rows,
                create=True,
            ) as reconstruct,
            patch.object(
                module,
                "calculate_theme_snapshot",
                return_value=make_complete_snapshot(commercialization=["Mistral"]),
                create=True,
            ) as calculate_snapshot,
            patch.object(
                module,
                "save_theme_snapshot",
                create=True,
            ) as save_snapshot,
        ):
            self.run_backfill()

        reconstructed_rows = reconstruct.call_args.args[0]
        self.assertEqual(
            sorted(row[1] for row in reconstructed_rows),
            ["Mistral", "Not Watchlisted"],
        )
        calculate_snapshot.assert_called_once_with(eligible_rows)
        self.assertEqual(
            save_snapshot.call_args.kwargs["eligible_company_count"],
            1,
        )

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import company_history


class BuildCompanyHistoryTests(unittest.TestCase):
    def test_calculates_persistence_from_active_and_total_snapshots(self):
        snapshot_times = [0, 86_400, 172_800, 259_200]
        snapshot_counts = {
            "Acme": {
                0: 2,
                86_400: 4,
                259_200: 3,
            }
        }

        history = company_history.build_company_history(
            "Acme",
            snapshot_counts,
            snapshot_times,
        )

        self.assertEqual(history["snapshots_active"], 3)
        self.assertEqual(history["total_snapshots"], 4)
        self.assertAlmostEqual(history["persistence_score"], 0.75)
        self.assertEqual(history["first_postings"], 2)
        self.assertEqual(history["current_postings"], 3)
        self.assertEqual(history["peak_postings"], 4)

    def test_current_postings_is_zero_when_company_misses_latest_snapshot(self):
        snapshot_times = [0, 86_400, 172_800]
        snapshot_counts = {"Acme": {0: 2, 86_400: 4}}

        history = company_history.build_company_history(
            "Acme",
            snapshot_counts,
            snapshot_times,
        )

        self.assertEqual(history["current_postings"], 0)
        self.assertAlmostEqual(history["persistence_score"], 2 / 3)

    def test_calculates_observation_window_days_between_first_and_latest_active(self):
        snapshot_times = [0, 86_400, 172_800, 259_200]
        snapshot_counts = {"Acme": {0: 2, 172_800: 3}}

        history = company_history.build_company_history(
            "Acme",
            snapshot_counts,
            snapshot_times,
        )

        self.assertEqual(history["observation_window_hours"], 48)
        self.assertEqual(history["observation_window_days"], 2)


class GetCompanyHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "jobs.db"

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE job_snapshots (
                snapshot_time INTEGER,
                company TEXT
            )
            """
        )
        conn.executemany(
            "INSERT INTO job_snapshots (snapshot_time, company) VALUES (?, ?)",
            [
                (100, "Acme"),
                (100, "Acme"),
                (200, "Acme"),
                (200, "Other"),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_company_history_lookup_is_case_insensitive(self):
        with patch.object(company_history, "DB_NAME", str(self.db_path)):
            history = company_history.get_company_history("aCmE")

        self.assertIsNotNone(history)
        self.assertEqual(history["company"], "Acme")
        self.assertEqual(history["snapshots_active"], 2)
        self.assertEqual(history["first_postings"], 2)
        self.assertEqual(history["current_postings"], 1)

    def test_returns_none_for_unknown_company(self):
        with patch.object(company_history, "DB_NAME", str(self.db_path)):
            history = company_history.get_company_history("Missing")

        self.assertIsNone(history)


if __name__ == "__main__":
    unittest.main()

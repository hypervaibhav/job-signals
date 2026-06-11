import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseInitializationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "jobs.db"

    def table_names(self):
        conn = sqlite3.connect(self.db_path)
        self.addCleanup(conn.close)
        return {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    def test_init_db_creates_strategic_theme_snapshots_table(self):
        with patch.object(database, "DB_NAME", str(self.db_path)):
            database.init_db()

        self.assertIn("strategic_theme_snapshots", self.table_names())

    def test_init_db_creates_strategic_theme_companies_table(self):
        with patch.object(database, "DB_NAME", str(self.db_path)):
            database.init_db()

        self.assertIn("strategic_theme_companies", self.table_names())


if __name__ == "__main__":
    unittest.main()

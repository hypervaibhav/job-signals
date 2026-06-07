import sqlite3
import time

DB_NAME = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        source TEXT,
        description TEXT,
        snapshot_time INTEGER
    )
    """)

    try:
        c.execute("ALTER TABLE jobs ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def save_jobs(jobs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    snapshot_time = int(time.time())

    for job in jobs:
        c.execute("""
        INSERT INTO jobs (title, company, source, description, snapshot_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            job["title"],
            job["company"],
            job["source"],
            job.get("description", ""),
            snapshot_time
        ))

    conn.commit()
    conn.close()


def get_previous_snapshot(limit=100):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    SELECT title, company, snapshot_time, description
    FROM jobs
    ORDER BY snapshot_time DESC
    LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    return rows

def get_latest_snapshot_time():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT MAX(snapshot_time) FROM jobs")
    latest = c.fetchone()[0]

    conn.close()
    return latest
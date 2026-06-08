import hashlib
import sqlite3
import time

DB_NAME = "jobs.db"


def normalize_text(value):
    return " ".join((value or "").strip().lower().split())


def make_job_key(job):
    source = normalize_text(job.get("source", ""))
    external_id = normalize_text(job.get("external_id", ""))

    if external_id:
        raw_key = f"{source}|{external_id}"
    else:
        title = normalize_text(job.get("title", ""))
        company = normalize_text(job.get("company", ""))
        raw_key = f"{source}|{title}|{company}"

    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_key TEXT UNIQUE,
        title TEXT,
        company TEXT,
        source TEXT,
        external_id TEXT,
        description TEXT,
        first_seen INTEGER,
        last_seen INTEGER,
        snapshot_time INTEGER,
        active INTEGER DEFAULT 1
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS job_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_time INTEGER,
        job_key TEXT,
        title TEXT,
        company TEXT,
        source TEXT,
        external_id TEXT,
        description TEXT,
        UNIQUE(snapshot_time, job_key)
    )
    """)

    columns_to_add = [
        ("job_key", "TEXT"),
        ("external_id", "TEXT"),
        ("first_seen", "INTEGER"),
        ("last_seen", "INTEGER"),
        ("active", "INTEGER DEFAULT 1"),
        ("description", "TEXT"),
    ]

    for column_name, column_type in columns_to_add:
        try:
            c.execute(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}")
        except sqlite3.OperationalError:
            pass

    try:
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_job_key ON jobs(job_key)")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def save_jobs(jobs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    snapshot_time = int(time.time())
    c.execute("SELECT MAX(snapshot_time) FROM job_snapshots")
    latest_snapshot = c.fetchone()[0]

    if latest_snapshot is not None and snapshot_time <= latest_snapshot:
        snapshot_time = latest_snapshot + 1

    seen_job_keys = set()

    for job in jobs:
        job_key = make_job_key(job)
        seen_job_keys.add(job_key)

        title = job.get("title", "")
        company = job.get("company", "")
        source = job.get("source", "")
        external_id = job.get("external_id", "")
        description = job.get("description", "")

        c.execute("""
        INSERT INTO jobs (
            job_key,
            title,
            company,
            source,
            external_id,
            description,
            first_seen,
            last_seen,
            snapshot_time,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(job_key) DO UPDATE SET
            title = excluded.title,
            company = excluded.company,
            source = excluded.source,
            external_id = excluded.external_id,
            description = excluded.description,
            last_seen = excluded.last_seen,
            snapshot_time = excluded.snapshot_time,
            active = 1
        """, (
            job_key,
            title,
            company,
            source,
            external_id,
            description,
            snapshot_time,
            snapshot_time,
            snapshot_time,
        ))

        c.execute("""
        INSERT OR IGNORE INTO job_snapshots (
            snapshot_time,
            job_key,
            title,
            company,
            source,
            external_id,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_time,
            job_key,
            title,
            company,
            source,
            external_id,
            description,
        ))

    if seen_job_keys:
        placeholders = ",".join("?" for _ in seen_job_keys)
        c.execute(f"""
        UPDATE jobs
        SET active = 0
        WHERE source IN ({','.join('?' for _ in set(job.get('source', '') for job in jobs))})
        AND job_key NOT IN ({placeholders})
        """, tuple(set(job.get("source", "") for job in jobs)) + tuple(seen_job_keys))

    conn.commit()
    conn.close()


def get_previous_snapshot(limit=100):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    SELECT title, company, last_seen, description
    FROM jobs
    ORDER BY last_seen DESC
    LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    return rows


def get_latest_snapshot_time():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT MAX(last_seen) FROM jobs")
    latest = c.fetchone()[0]

    conn.close()
    return latest


def get_job_change_summary():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    latest_snapshot = get_latest_snapshot_time()

    if latest_snapshot is None:
        conn.close()
        return {
            "new_jobs": 0,
            "active_jobs": 0,
            "inactive_jobs": 0,
            "latest_snapshot": None,
        }

    c.execute("SELECT COUNT(*) FROM jobs WHERE first_seen = ?", (latest_snapshot,))
    new_jobs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM jobs WHERE active = 1")
    active_jobs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM jobs WHERE active = 0")
    inactive_jobs = c.fetchone()[0]

    conn.close()

    return {
        "new_jobs": new_jobs,
        "active_jobs": active_jobs,
        "inactive_jobs": inactive_jobs,
        "latest_snapshot": latest_snapshot,
    }
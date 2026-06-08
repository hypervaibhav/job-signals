import sqlite3
from datetime import datetime
from trends import classify_role


DB_NAME = "jobs.db"


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

c.execute("SELECT MAX(snapshot_time) FROM job_snapshots")
latest_snapshot = c.fetchone()[0]

c.execute(
    """
    SELECT title, company, source
    FROM job_snapshots
    WHERE snapshot_time = ?
    ORDER BY company, title
    """,
    (latest_snapshot,),
)

rows = c.fetchall()
conn.close()

print(f"Latest snapshot: {format_snapshot_time(latest_snapshot)}")
print("\n--- JOBS CLASSIFIED AS OTHER ---\n")

other_jobs = []

for title, company, source in rows:
    category = classify_role(title)

    if category == "Other":
        other_jobs.append((title, company, source))

if not other_jobs:
    print("No jobs classified as Other. Beautiful. Suspicious, but beautiful.")
else:
    for title, company, source in other_jobs:
        print(f"- {title} — {company} [{source}]")

    print(f"\nTotal Other jobs: {len(other_jobs)}")
import sqlite3
from collections import defaultdict
from datetime import datetime

DB_NAME = "jobs.db"


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


def get_snapshot_times():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT snapshot_time
        FROM job_snapshots
        ORDER BY snapshot_time ASC
        """
    )

    snapshot_times = [row[0] for row in cursor.fetchall()]
    conn.close()

    return snapshot_times


def get_company_snapshot_counts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT company, snapshot_time, COUNT(*) as posting_count
        FROM job_snapshots
        GROUP BY company, snapshot_time
        ORDER BY company ASC, snapshot_time ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    company_counts = defaultdict(dict)

    for company, snapshot_time, posting_count in rows:
        normalized_company = company.strip()
        company_counts[normalized_company][snapshot_time] = posting_count

    return company_counts


def build_company_history(company, snapshot_counts, snapshot_times):
    company_timeline = snapshot_counts.get(company, {})

    if not company_timeline:
        return None

    active_snapshots = sorted(company_timeline.keys())
    total_snapshots = len(snapshot_times)
    snapshots_active = len(active_snapshots)

    latest_snapshot = snapshot_times[-1] if snapshot_times else None
    current_postings = company_timeline.get(latest_snapshot, 0)
    peak_postings = max(company_timeline.values())

    persistence_score = (
        snapshots_active / total_snapshots
        if total_snapshots
        else 0
    )

    return {
        "company": company,
        "first_seen": active_snapshots[0],
        "latest_seen": active_snapshots[-1],
        "first_seen_formatted": format_snapshot_time(active_snapshots[0]),
        "latest_seen_formatted": format_snapshot_time(active_snapshots[-1]),
        "snapshots_active": snapshots_active,
        "total_snapshots": total_snapshots,
        "persistence_score": persistence_score,
        "current_postings": current_postings,
        "peak_postings": peak_postings,
    }


def get_company_histories():
    snapshot_times = get_snapshot_times()
    snapshot_counts = get_company_snapshot_counts()

    histories = []

    for company in snapshot_counts:
        history = build_company_history(company, snapshot_counts, snapshot_times)

        if history:
            histories.append(history)

    histories.sort(
        key=lambda row: (
            row["persistence_score"],
            row["current_postings"],
            row["peak_postings"],
        ),
        reverse=True,
    )

    return histories


def get_company_history(company_name):
    snapshot_times = get_snapshot_times()
    snapshot_counts = get_company_snapshot_counts()

    matching_company = None

    for company in snapshot_counts:
        if company.lower() == company_name.lower():
            matching_company = company
            break

    if not matching_company:
        return None

    return build_company_history(matching_company, snapshot_counts, snapshot_times)
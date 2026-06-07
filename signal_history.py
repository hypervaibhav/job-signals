import sqlite3
from datetime import datetime

DB_NAME = "jobs.db"


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


def get_latest_signal_time(table_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(f"SELECT MAX(snapshot_time) FROM {table_name}")
    result = c.fetchone()[0]

    conn.close()
    return result


def get_leaderboard(table_name, label_column, snapshot_time):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        f'''
        SELECT {label_column}, count
        FROM {table_name}
        WHERE snapshot_time = ?
        ORDER BY count DESC, {label_column} ASC
        ''',
        (snapshot_time,),
    )

    rows = c.fetchall()
    conn.close()
    return rows


def print_leaderboard(title, rows):
    print(f"\n--- {title} ---\n")

    if not rows:
        print("No leaderboard data found yet.")
        return

    total = sum(count for _, count in rows)

    for rank, (label, count) in enumerate(rows, start=1):
        percentage = (count / total) * 100 if total else 0
        print(f"{rank}. {label}: {count} ({percentage:.1f}%)")


def main():
    category_time = get_latest_signal_time("category_signals")
    skill_time = get_latest_signal_time("skill_signals")

    if category_time is None and skill_time is None:
        print("No signal data found yet. Run trends.py first.")
        return

    if category_time is not None:
        print(f"Latest category snapshot: {format_snapshot_time(category_time)}")
        category_rows = get_leaderboard("category_signals", "category", category_time)
        print_leaderboard("CATEGORY LEADERBOARD", category_rows)

    if skill_time is not None:
        print(f"\nLatest skill snapshot: {format_snapshot_time(skill_time)}")
        skill_rows = get_leaderboard("skill_signals", "skill", skill_time)
        print_leaderboard("SKILL LEADERBOARD", skill_rows)


if __name__ == "__main__":
    main()
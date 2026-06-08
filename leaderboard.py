import sqlite3
from datetime import datetime

from trends import extract_skills
from signal_taxonomy import normalize_signal, normalize_skill_counts

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


def get_skill_company_counts(snapshot_time):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        '''
        SELECT title, company, description
        FROM job_snapshots
        WHERE snapshot_time = ?
        ''',
        (snapshot_time,),
    )

    rows = c.fetchall()
    conn.close()

    signal_companies = {}

    for title, company, description in rows:
        for skill in extract_skills(title, description or ""):
            signal = normalize_signal(skill)
            signal_companies.setdefault(signal, set()).add(company)

    return {signal: len(companies) for signal, companies in signal_companies.items()}


def calculate_signal_scores(rows, company_counts=None):
    scored_rows = []

    for label, count in rows:
        company_count = company_counts.get(label, 1) if company_counts else 1
        score = count * company_count
        scored_rows.append((label, count, company_count, score))

    scored_rows.sort(key=lambda row: row[3], reverse=True)
    return scored_rows


def print_leaderboard(title, rows, company_counts=None):
    print(f"\n--- {title} ---\n")

    if not rows:
        print("No leaderboard data found yet.")
        return

    total = sum(count for _, count in rows)
    scored_rows = calculate_signal_scores(rows, company_counts)

    for rank, (label, count, company_count, score) in enumerate(scored_rows, start=1):
        percentage = (count / total) * 100 if total else 0

        if company_counts:
            company_word = "company" if company_count == 1 else "companies"
            print(
                f"{rank}. {label}: {count} postings ({percentage:.1f}%) | "
                f"{company_count} {company_word} | score {score}"
            )
        else:
            print(f"{rank}. {label}: {count} postings ({percentage:.1f}%) | score {score}")


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
        raw_skill_rows = get_leaderboard("skill_signals", "skill", skill_time)
        normalized_skill_counts = normalize_skill_counts(dict(raw_skill_rows))
        skill_rows = list(normalized_skill_counts.items())
        company_counts = get_skill_company_counts(skill_time)
        print_leaderboard("SIGNAL LEADERBOARD", skill_rows, company_counts)


if __name__ == "__main__":
    main()
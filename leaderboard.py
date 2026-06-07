import re
import sqlite3
from datetime import datetime

DB_NAME = "jobs.db"


def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


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
        FROM jobs
        WHERE snapshot_time = ?
        ''',
        (snapshot_time,),
    )

    rows = c.fetchall()
    conn.close()

    skill_companies = {}

    skills = [
        "ai",
        "artificial intelligence",
        "llm",
        "mcp",
        "react",
        "typescript",
        "aws",
        "seo",
        "hubspot",
        "excel",
    ]

    for title, company, description in rows:
        text = f"{title} {description or ''}".lower()

        for skill in skills:
            if contains_keyword(text, skill):
                skill_companies.setdefault(skill, set()).add(company)

    return {skill: len(companies) for skill, companies in skill_companies.items()}


def print_leaderboard(title, rows, company_counts=None):
    print(f"\n--- {title} ---\n")

    if not rows:
        print("No leaderboard data found yet.")
        return

    total = sum(count for _, count in rows)

    for rank, (label, count) in enumerate(rows, start=1):
        percentage = (count / total) * 100 if total else 0

        if company_counts and label in company_counts:
            company_count = company_counts[label]
            company_word = "company" if company_count == 1 else "companies"
            print(
                f"{rank}. {label}: {count} ({percentage:.1f}%) | {company_count} {company_word}"
            )
        else:
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
        company_counts = get_skill_company_counts(skill_time)
        print_leaderboard("SKILL LEADERBOARD", skill_rows, company_counts)


if __name__ == "__main__":
    main()
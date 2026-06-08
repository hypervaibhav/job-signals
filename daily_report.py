import sqlite3
from collections import Counter
from datetime import datetime

from trends import (
    classify_role,
    extract_skills,
)

from signal_taxonomy import normalize_signal

DB_NAME = "jobs.db"


def get_latest_two_snapshots():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT snapshot_time
        FROM job_snapshots
        ORDER BY snapshot_time DESC
        LIMIT 2
    """)
    times = [row[0] for row in c.fetchall()]

    if len(times) < 2:
        conn.close()
        return None, None, [], []

    latest_time, previous_time = times[0], times[1]

    c.execute("""
        SELECT title, company, snapshot_time, description
        FROM job_snapshots
        WHERE snapshot_time = ?
    """, (latest_time,))
    latest = c.fetchall()

    c.execute("""
        SELECT title, company, snapshot_time, description
        FROM job_snapshots
        WHERE snapshot_time = ?
    """, (previous_time,))
    previous = c.fetchall()

    conn.close()
    return latest_time, previous_time, latest, previous


def fmt_time(ts):
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %I:%M %p")


# Helper: normalized skill counts
def calculate_normalized_skill_counts(rows):
    skill_counts = Counter()

    for row in rows:
        title = row[0]
        description = row[3] or ""

        for skill in extract_skills(title, description):
            signal = normalize_signal(skill)
            skill_counts[signal] += 1

    return skill_counts


# Helper: normalized skill companies

def calculate_normalized_skill_companies(rows):
    signal_companies = {}

    for row in rows:
        title = row[0]
        company = row[1]
        description = row[3] or ""

        for skill in extract_skills(title, description):
            signal = normalize_signal(skill)
            signal_companies.setdefault(signal, set()).add(company)

    return signal_companies


# --- MARKET NARRATIVE ---
def print_market_narrative(net_change, category_changes, company_changes, skill_changes):
    print("\n--- MARKET NARRATIVE ---\n")

    if net_change > 0:
        print(f"Market direction: expanding (+{net_change} net jobs).")
    elif net_change < 0:
        print(f"Market direction: contracting ({net_change} net jobs).")
    else:
        print("Market direction: flat between the latest two snapshots.")

    strongest_signals = [row for row in skill_changes if row[1] > 0]
    strongest_signals.sort(key=lambda row: row[4], reverse=True)

    if strongest_signals:
        signal, count, diff, companies, score = strongest_signals[0]
        print(
            f"Strongest signal: {signal} appears in {count} postings "
            f"across {companies} companies (strength {score})."
        )

    growing_categories = [row for row in category_changes if row[2] > 0]
    growing_categories.sort(key=lambda row: row[2], reverse=True)

    if growing_categories:
        category, count, diff = growing_categories[0]
        print(f"Fastest category movement: {category} increased by {diff} roles.")
    else:
        print("Category movement: no meaningful category increase detected.")

    growing_companies = [row for row in company_changes if row[2] > 0]
    growing_companies.sort(key=lambda row: row[2], reverse=True)

    if growing_companies:
        company, count, diff = growing_companies[0]
        print(f"Top company movement: {company} increased by {diff} postings.")
    else:
        print("Company movement: no company showed clear positive movement.")

    broad_signals = [row for row in strongest_signals if row[3] >= 3]

    if broad_signals:
        signal, count, diff, companies, score = broad_signals[0]
        print(
            f"Broad demand note: {signal} is spread across {companies} companies, "
            "making it more meaningful than a single-company spike."
        )


def print_daily_report():
    latest_time, previous_time, latest, previous = get_latest_two_snapshots()

    if not latest or not previous:
        print("Need at least 2 snapshots to generate report.")
        return

    latest_categories = Counter(classify_role(row[0]) for row in latest)
    previous_categories = Counter(classify_role(row[0]) for row in previous)

    latest_companies = Counter(row[1] for row in latest)
    previous_companies = Counter(row[1] for row in previous)

    latest_skills = calculate_normalized_skill_counts(latest)
    previous_skills = calculate_normalized_skill_counts(previous)

    latest_skill_companies = calculate_normalized_skill_companies(latest)

    print("\n==============================")
    print("JOB SIGNALS DAILY REPORT")
    print("==============================\n")

    print(f"Latest snapshot:   {fmt_time(latest_time)}")
    print(f"Previous snapshot: {fmt_time(previous_time)}")

    print("\n--- MARKET DIRECTION ---\n")
    net_change = len(latest) - len(previous)
    print(f"Latest jobs: {len(latest)}")
    print(f"Previous jobs: {len(previous)}")
    print(f"Net job change: {net_change:+}")

    print("\n--- CATEGORY MOVEMENT ---\n")
    all_categories = set(latest_categories) | set(previous_categories)

    category_changes = []
    for category in all_categories:
        diff = latest_categories[category] - previous_categories[category]
        category_changes.append((category, latest_categories[category], diff))

    category_changes.sort(key=lambda x: x[2], reverse=True)

    for category, count, diff in category_changes[:8]:
        print(f"{category}: {count} roles ({diff:+})")

    print("\n--- COMPANY MOMENTUM ---\n")
    all_companies = set(latest_companies) | set(previous_companies)

    company_changes = []
    for company in all_companies:
        diff = latest_companies[company] - previous_companies[company]
        company_changes.append((company, latest_companies[company], diff))

    company_changes.sort(key=lambda x: x[2], reverse=True)

    for company, count, diff in company_changes[:10]:
        print(f"{company}: {count} postings ({diff:+})")

    print("\n--- SIGNAL LEADERS ---\n")
    all_skills = set(latest_skills) | set(previous_skills)

    skill_changes = []
    for skill in all_skills:
        diff = latest_skills[skill] - previous_skills[skill]
        companies = len(latest_skill_companies.get(skill, set()))
        score = latest_skills[skill] * companies
        skill_changes.append((skill, latest_skills[skill], diff, companies, score))

    skill_changes.sort(key=lambda x: x[4], reverse=True)

    for skill, count, diff, companies, score in skill_changes[:10]:
        print(
            f"{skill}: {count} postings ({diff:+}), "
            f"{companies} companies, signal strength {score}"
        )

    print_market_narrative(net_change, category_changes, company_changes, skill_changes)

    print("\n--- QUICK READ ---\n")

    growing_categories = [x for x in category_changes if x[2] > 0]
    growing_skills = [x for x in skill_changes if x[2] > 0]
    growing_companies = [x for x in company_changes if x[2] > 0]

    if growing_categories:
        print(f"Top category movement: {growing_categories[0][0]} ({growing_categories[0][2]:+})")
    else:
        print("Top category movement: none detected")

    if growing_skills:
        print(f"Top signal movement: {growing_skills[0][0]} ({growing_skills[0][2]:+})")
    else:
        print("Top signal movement: none detected")

    if growing_companies:
        print(f"Top company movement: {growing_companies[0][0]} ({growing_companies[0][2]:+})")
    else:
        print("Top company movement: none detected")

    print("\n==============================\n")


if __name__ == "__main__":
    print_daily_report()
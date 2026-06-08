import re
import sqlite3
from collections import Counter
from datetime import datetime

DB_NAME = "jobs.db"

CATEGORIES = {
    "AI": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml engineer",
        "llm",
        "genai",
        "generative ai",
        "prompt engineer",
    ],
    "People / HR": [
        "people",
        "human resources",
        "hr",
        "recruiter",
        "talent",
        "staffing",
        "sourcing",
        "sourcing specialist",
    ],
    "Admin / Executive": [
        "executive assistant",
        "assistant",
        "administrator",
        "administrative",
        "office manager",
        "chief of staff",
        "chief financial officer",
        "chief operating officer",
        "cfo",
        "coo",
        "executive",
    ],
    "Education": [
        "teacher",
        "professor",
        "instructor",
        "tutor",
        "education",
    ],
    "Production / Labour": [
        "production",
        "labourer",
        "laborer",
        "operator",
        "warehouse",
        "manufacturing",
        "builder",
        "buffer",
    ],
    "Healthcare": [
        "medical",
        "healthcare",
        "clinical",
        "nurse",
        "physician",
        "doctor",
        "nanny",
        "care",
        "claims",
        "psychologist",
        "psicologo",
        "coach psicologo",
    ],
    "Engineering": [
        "software",
        "engineer",
        "developer",
        "backend",
        "front end",
        "frontend",
        "full stack",
        "fullstack",
        "python",
        "javascript",
        "react",
        "devops",
        "cloud",
    ],
    "Data / Analytics": [
        "data analyst",
        "online data analyst",
        "data labeling",
        "data labeler",
        "data annotator",
        "annotator",
        "data specialist",
        "data engineer",
        "data scientist",
        "analytics",
        "business intelligence",
        "bi analyst",
    ],
    "Product": [
        "product manager",
        "product owner",
        "product designer",
        "ux",
        "ui designer",
    ],
    "Sales": [
        "sales",
        "account executive",
        "business development",
        "revenue",
        "partnerships",
    ],
    "Marketing": [
        "marketing",
        "seo",
        "content",
        "copywriter",
        "brand",
        "growth marketer",
        "writer",
        "freelance writer",
    ],
    "Support": [
        "customer support",
        "customer success",
        "support specialist",
        "help desk",
        "technical support",
        "customer service",
        "atención al cliente",
        "atencion al cliente",
        "cliente",
    ],
    "Operations": [
        "operations",
        "operations staff",
        "chief of staff",
        "chief operating officer",
        "coo",
        "coordinator",
        "analyst",
        "program manager",
        "project manager",
        "implementation specialist",
        "delivery services",
    ],
}

SKILLS = [
    "python",
    "javascript",
    "typescript",
    "react",
    "node",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "sqlite",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "linux",
    "git",
    "api",
    "machine learning",
    "artificial intelligence",
    "ai",
    "llm",
    "genai",
    "langchain",
    "langgraph",
    "mcp",
    "data analysis",
    "data science",
    "excel",
    "seo",
    "salesforce",
    "hubspot",
]


def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


def get_snapshots():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT title, company, snapshot_time, description
        FROM job_snapshots
        ORDER BY snapshot_time DESC
    """)

    rows = c.fetchall()
    conn.close()

    return rows


# Save signals to dedicated tables
def save_signal_snapshot(snapshot_time, latest_categories, latest_skills):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS category_signals (
            snapshot_time INTEGER,
            category TEXT,
            count INTEGER
        )
        '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS skill_signals (
            snapshot_time INTEGER,
            skill TEXT,
            count INTEGER
        )
        '''
    )

    c.execute("DELETE FROM category_signals WHERE snapshot_time = ?", (snapshot_time,))
    c.execute("DELETE FROM skill_signals WHERE snapshot_time = ?", (snapshot_time,))

    for category, count in latest_categories.items():
        c.execute(
            "INSERT INTO category_signals VALUES (?, ?, ?)",
            (snapshot_time, category, count),
        )

    for skill, count in latest_skills.items():
        c.execute(
            "INSERT INTO skill_signals VALUES (?, ?, ?)",
            (snapshot_time, skill, count),
        )

    conn.commit()
    conn.close()


def classify_role(title):
    title = title.lower()

    for category, keywords in CATEGORIES.items():
        if any(contains_keyword(title, keyword) for keyword in keywords):
            return category

    return "Other"


def extract_skills(title, description=""):
    text = f"{title} {description}".lower()
    return [skill for skill in SKILLS if contains_keyword(text, skill)]


# Helper: Calculate for each skill, the set of companies that mention it in the rows
def calculate_skill_companies(rows):
    skill_companies = {}

    for row in rows:
        title = row[0]
        company = row[1]
        description = row[3] or ""

        for skill in extract_skills(title, description):
            skill_companies.setdefault(skill, set()).add(company)

    return skill_companies


# Helper: Print emerging technology score
def print_emerging_technology_score(growing_skills, latest_skill_companies):
    print("\n--- EMERGING TECHNOLOGY SCORE ---\n")

    if not growing_skills:
        print("No emerging technology signals detected yet.")
        return

    scored_skills = []

    for skill, growth in growing_skills.items():
        company_count = len(latest_skill_companies.get(skill, set()))
        score = growth * company_count
        scored_skills.append((skill, growth, company_count, score))

    scored_skills.sort(key=lambda item: item[3], reverse=True)

    for skill, growth, company_count, score in scored_skills[:10]:
        company_word = "company" if company_count == 1 else "companies"
        print(
            f"📊 {skill}: score {score} "
            f"(+{growth} postings × {company_count} {company_word})"
        )


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


# Print job lifecycle summary for the latest snapshot
def print_job_lifecycle_summary(latest_time):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM jobs WHERE first_seen = ?", (latest_time,))
    new_jobs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM jobs WHERE active = 1")
    active_jobs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM jobs WHERE active = 0")
    removed_jobs = c.fetchone()[0]

    net_change = new_jobs - removed_jobs

    c.execute("""
        SELECT title, company, source
        FROM jobs
        WHERE first_seen = ?
        ORDER BY company, title
        LIMIT 10
    """, (latest_time,))
    newest_rows = c.fetchall()

    c.execute("""
        SELECT title, company, source
        FROM jobs
        WHERE active = 0
        ORDER BY last_seen DESC
        LIMIT 10
    """)
    removed_rows = c.fetchall()

    conn.close()

    print("\n--- JOB LIFECYCLE ---\n")
    print(f"New jobs this snapshot: {new_jobs}")
    print(f"Removed jobs: {removed_jobs}")
    print(f"Active jobs: {active_jobs}")
    print(f"Net change: {net_change:+}")

    if newest_rows:
        print("\nNewest jobs:")
        for title, company, source in newest_rows:
            print(f"+ {title} — {company} [{source}]")
    else:
        print("\nNewest jobs: none detected in latest snapshot")

    if removed_rows:
        print("\nRecently removed jobs:")
        for title, company, source in removed_rows:
            print(f"- {title} — {company} [{source}]")
    else:
        print("Recently removed jobs: none detected yet")


def compare_latest_snapshots():
    data = get_snapshots()

    if len(data) < 10:
        print("Not enough data yet. Run scraper a few more times.")
        return

    # get snapshot timestamps (unique, newest first)
    snapshot_times = sorted(list(set([row[2] for row in data])), reverse=True)

    if len(snapshot_times) < 2:
        print("Need at least 2 snapshots.")
        return

    latest_time = snapshot_times[0]
    previous_time = snapshot_times[1]

    latest = [row for row in data if row[2] == latest_time]
    previous = [row for row in data if row[2] != latest_time and row[2] == previous_time]

    latest_categories = Counter([classify_role(row[0]) for row in latest])
    previous_categories = Counter([classify_role(row[0]) for row in previous])

    print("\n--- CATEGORY TREND SIGNALS ---\n")
    print(f"Latest snapshot: {format_snapshot_time(latest_time)}")
    print(f"Previous snapshot: {format_snapshot_time(previous_time)}\n")
    print_job_lifecycle_summary(latest_time)

    all_categories = set(list(latest_categories.keys()) + list(previous_categories.keys()))
    latest_total = sum(latest_categories.values())

    for category in sorted(all_categories):
        latest_count = latest_categories[category]
        previous_count = previous_categories[category]
        diff = latest_count - previous_count
        percentage = (latest_count / latest_total) * 100 if latest_total else 0

        if diff > 0:
            print(f"📈 {category}: {latest_count} roles ({percentage:.1f}%) (+{diff})")
        elif diff < 0:
            print(f"📉 {category}: {latest_count} roles ({percentage:.1f}%) ({diff})")
        else:
            print(f"➖ {category}: {latest_count} roles ({percentage:.1f}%) (stable)")

    growing_categories = {
        category: latest_categories[category] - previous_categories[category]
        for category in all_categories
        if latest_categories[category] > previous_categories[category]
    }

    if growing_categories:
        emerging_category = max(growing_categories, key=growing_categories.get)
        print(f"\nEmerging category: {emerging_category} (+{growing_categories[emerging_category]})")
    else:
        print("\nEmerging category: none detected yet")

    latest_companies = Counter([row[1] for row in latest])
    previous_companies = Counter([row[1] for row in previous])

    print("\n--- COMPANY MOMENTUM ---\n")

    all_companies = set(
        list(latest_companies.keys()) + list(previous_companies.keys())
    )

    company_changes = []

    for company in all_companies:
        diff = latest_companies[company] - previous_companies[company]
        latest_count = latest_companies[company]
        company_changes.append((company, latest_count, diff))

    company_changes.sort(key=lambda item: item[2], reverse=True)

    for company, latest_count, diff in company_changes[:10]:
        if diff > 0:
            print(f"📈 {company}: {latest_count} postings (+{diff})")
        elif diff < 0:
            print(f"📉 {company}: {latest_count} postings ({diff})")
        else:
            print(f"➖ {company}: {latest_count} postings (stable)")

    latest_skills = Counter(
        skill
        for row in latest
        for skill in extract_skills(row[0], row[3] or "")
    )
    previous_skills = Counter(
        skill
        for row in previous
        for skill in extract_skills(row[0], row[3] or "")
    )
    latest_skill_companies = calculate_skill_companies(latest)

    save_signal_snapshot(
        latest_time,
        latest_categories,
        latest_skills,
    )

    print("\n--- SKILL SIGNALS ---\n")

    if latest_skills:
        print("Top skills in latest snapshot:")
        for skill, count in latest_skills.most_common(10):
            company_count = len(latest_skill_companies.get(skill, set()))
            company_word = "company" if company_count == 1 else "companies"
            print(f"- {skill}: {count} postings, {company_count} {company_word}")
    else:
        print("No known skills detected in latest snapshot yet.")

    all_skills = set(list(latest_skills.keys()) + list(previous_skills.keys()))
    growing_skills = {
        skill: latest_skills[skill] - previous_skills[skill]
        for skill in all_skills
        if latest_skills[skill] > previous_skills[skill]
    }

    if growing_skills:
        print("\nEmerging skills:")
        for skill, diff in sorted(growing_skills.items(), key=lambda item: item[1], reverse=True)[:10]:
            print(f"📈 {skill}: +{diff}")
    else:
        print("\nEmerging skills: none detected yet")

    print_emerging_technology_score(growing_skills, latest_skill_companies)
    print("\n--- SIGNAL DATABASE ---\n")
    print("Category signals saved to: category_signals")
    print("Skill signals saved to: skill_signals")


if __name__ == "__main__":
    compare_latest_snapshots()
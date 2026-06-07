

import re
import sqlite3
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
    ],
    "Support": [
        "customer support",
        "customer success",
        "support specialist",
        "help desk",
        "technical support",
        "customer service",
    ],
    "People / HR": [
        "people",
        "human resources",
        "hr",
        "recruiter",
        "talent",
        "staffing",
    ],
    "Admin / Executive": [
        "executive assistant",
        "assistant",
        "administrator",
        "administrative",
        "office manager",
    ],
    "Education": [
        "teacher",
        "professor",
        "profesor",
        "instructor",
        "tutor",
        "education",
        "enseñanza",
    ],
    "Production / Labour": [
        "production",
        "labourer",
        "laborer",
        "operator",
        "warehouse",
        "manufacturing",
    ],
    "Healthcare": [
        "medical",
        "healthcare",
        "clinical",
        "nurse",
        "physician",
        "doctor",
    ],
    "Operations": [
        "operations",
        "coordinator",
        "analyst",
        "program manager",
        "project manager",
    ],
}


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


def classify_role(title):
    for category, keywords in CATEGORIES.items():
        if any(contains_keyword(title, keyword) for keyword in keywords):
            return category

    return "Other"


conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

c.execute("SELECT MAX(snapshot_time) FROM jobs")
latest_snapshot = c.fetchone()[0]

c.execute(
    """
    SELECT title, company, source
    FROM jobs
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
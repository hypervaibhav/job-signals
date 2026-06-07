import re
import sqlite3
from collections import defaultdict
from datetime import datetime

DB_NAME = "jobs.db"

SKILLS_TO_CHECK = [
    "mcp",
    "aws",
    "react",
    "typescript",
    "ai",
]


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


def find_keyword_snippet(text, keyword, window=80):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    match = re.search(pattern, text.lower())

    if not match:
        return ""

    start = max(match.start() - window, 0)
    end = min(match.end() + window, len(text))
    snippet = text[start:end].replace("\n", " ").strip()

    return f"...{snippet}..."


conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

c.execute("SELECT MAX(snapshot_time) FROM jobs")
latest_snapshot = c.fetchone()[0]

c.execute(
    """
    SELECT title, company, description
    FROM jobs
    WHERE snapshot_time = ?
    ORDER BY company, title
    """,
    (latest_snapshot,),
)

rows = c.fetchall()
conn.close()

matches = defaultdict(list)

for title, company, description in rows:
    text = f"{title} {description or ''}"

    for skill in SKILLS_TO_CHECK:
        if contains_keyword(text, skill):
            snippet = find_keyword_snippet(text, skill)
            matches[skill].append((title, company, snippet))

print(f"Latest snapshot: {format_snapshot_time(latest_snapshot)}")

for skill in SKILLS_TO_CHECK:
    print(f"\n=== {skill.upper()} ===\n")

    if not matches[skill]:
        print("No matches found.")
        continue

    for title, company, snippet in matches[skill]:
        print(f"{title} — {company}")
        print(snippet)
        print()
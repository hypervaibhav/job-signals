import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime

from company_history import (
    classify_company_trend,
    classify_company_trend_confidence,
    get_company_history,
)
from role_taxonomy import classify_role as classify_role_from_taxonomy
from signal_taxonomy import is_ai_related

DB_NAME = "jobs.db"

SKILLS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "llm",
    "genai",
    "mcp",
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
    "salesforce",
    "hubspot",
    "seo",
    "excel",
]

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
    ],
    "People / HR": [
        "people",
        "human resources",
        "hr",
        "recruiter",
        "talent",
        "staffing",
        "sourcing specialist",
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
    ],
    "Operations": [
        "operations",
        "coordinator",
        "analyst",
        "program manager",
        "project manager",
        "implementation specialist",
        "delivery services",
    ],
}


def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


def format_snapshot_time(snapshot_time):
    return datetime.fromtimestamp(int(snapshot_time)).strftime("%Y-%m-%d %I:%M:%S %p")


def classify_role(title):
    return classify_role_from_taxonomy(title)


def extract_skills(title, description=""):
    text = f"{title} {description or ''}".lower()
    return [skill for skill in SKILLS if contains_keyword(text, skill)]


def detect_hiring_archetype(
    category_counts,
    skill_counts,
    representative_roles,
    latest_count,
    ai_related_count=None,
):
    role_text = " ".join(representative_roles).lower()
    research_role_count = sum(
        1
        for role in representative_roles
        if any(
            term in role.lower()
            for term in ["research scientist", "research engineer", "researcher"]
        )
    )

    ai_count = category_counts.get("AI", 0)
    ai_skill_mentions = (
        skill_counts.get("ai", 0)
        + skill_counts.get("artificial intelligence", 0)
        + skill_counts.get("machine learning", 0)
        + skill_counts.get("llm", 0)
        + skill_counts.get("genai", 0)
    )
    engineering_count = category_counts.get("Engineering", 0)
    sales_count = category_counts.get("Sales", 0)
    marketing_count = category_counts.get("Marketing", 0)
    product_count = category_counts.get("Product", 0)
    support_count = category_counts.get("Support", 0)
    operations_count = category_counts.get("Operations", 0)
    data_count = category_counts.get("Data / Analytics", 0)

    ai_share = ai_count / latest_count if latest_count else 0
    if ai_related_count is None:
        ai_related_count = min(ai_count + ai_skill_mentions, latest_count)

    ai_signal_share = ai_related_count / latest_count if latest_count else 0
    engineering_share = engineering_count / latest_count if latest_count else 0
    sales_share = sales_count / latest_count if latest_count else 0
    gtm_share = (sales_count + marketing_count + support_count) / latest_count if latest_count else 0
    product_engineering_share = (engineering_count + product_count + data_count) / latest_count if latest_count else 0

    if research_role_count >= 2:
        return "AI Research Expansion"

    if ai_signal_share >= 0.5 and gtm_share >= 0.4:
        return "AI Commercialization / GTM Expansion"

    if ai_signal_share >= 0.5 and (
        product_engineering_share >= 0.3
        or any(term in role_text for term in ["product", "platform", "engineer", "engineering"])
    ):
        return "AI Product Expansion"

    if engineering_share >= 0.5:
        return "Engineering Platform Expansion"

    if sales_share >= 0.5:
        return "Sales Expansion"

    if operations_count >= max(2, latest_count * 0.3):
        return "Operations Expansion"

    if data_count >= max(2, latest_count * 0.3):
        return "Data / Analytics Expansion"

    return "Mixed Hiring Activity"


def explain_hiring_archetype(archetype):
    explanations = {
        "AI Research Expansion": "Hiring pattern suggests investment in research-oriented AI capability.",
        "AI Commercialization / GTM Expansion": "Hiring pattern suggests the company is commercializing AI through sales, marketing, partnerships, or customer-facing roles.",
        "AI Product Expansion": "Hiring pattern suggests investment in AI product development or applied AI capabilities.",
        "Engineering Platform Expansion": "Hiring pattern suggests expansion of engineering, infrastructure, or platform capacity.",
        "Sales Expansion": "Hiring pattern suggests go-to-market or revenue expansion.",
        "Operations Expansion": "Hiring pattern suggests operational scaling or internal capacity expansion.",
        "Data / Analytics Expansion": "Hiring pattern suggests investment in data, analytics, or intelligence capabilities.",
        "Mixed Hiring Activity": "Hiring activity is distributed across multiple functions without one dominant archetype yet.",
    }

    return explanations.get(archetype, "No archetype explanation available yet.")


def get_company_rows(company_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        """
        SELECT title, company, source, description, snapshot_time
        FROM jobs
        WHERE LOWER(company) = LOWER(?)
        ORDER BY snapshot_time ASC
        """,
        (company_name,),
    )

    rows = c.fetchall()
    conn.close()
    return rows


def get_available_companies(limit=25):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        """
        SELECT company, COUNT(*) as posting_count
        FROM jobs
        GROUP BY company
        ORDER BY posting_count DESC, company ASC
        LIMIT ?
        """,
        (limit,),
    )

    rows = c.fetchall()
    conn.close()
    return rows


def build_company_report(company_name):
    rows = get_company_rows(company_name)

    if not rows:
        print(f"No jobs found for company: {company_name}")
        print("\nAvailable companies:")
        for company, count in get_available_companies():
            print(f"- {company}: {count} postings")
        return

    history = get_company_history(company_name)

    if not history:
        print(f"No company history found for company: {company_name}")
        return

    latest_rows = [row for row in rows if row[4] == history["latest_seen"]]
    latest_count = len(latest_rows)
    persistence = history["snapshots_active"]
    momentum = history["current_postings"] - history["first_postings"]
    observation_window_days = history["observation_window_days"]
    hiring_trend = classify_company_trend(history)
    trend_confidence = classify_company_trend_confidence(history)
    trend_narrative = generate_company_trend_narrative(hiring_trend, history)
    trend_confidence_narrative = generate_company_trend_confidence_narrative(
        trend_confidence,
        history,
    )

    category_counts = Counter(classify_role(row[0]) for row in latest_rows)

    skill_counts = Counter(
        skill
        for row in latest_rows
        for skill in extract_skills(row[0], row[3])
    )

    source_counts = Counter(row[2] for row in latest_rows)
    representative_roles = []
    seen_roles = set()

    for row in latest_rows:
        role = row[0]
        normalized_role = role.lower().strip()

        if normalized_role not in seen_roles:
            representative_roles.append(role)
            seen_roles.add(normalized_role)

        if len(representative_roles) == 5:
            break

    ai_related_count = sum(
        1
        for row in latest_rows
        if is_ai_related(extract_skills(row[0], row[3]))
    )
    ai_concentration = (ai_related_count / latest_count) * 100 if latest_count else 0

    top_category = category_counts.most_common(1)[0][0] if category_counts else "Unknown"
    top_skills = skill_counts.most_common(5)
    hiring_archetype = detect_hiring_archetype(
        category_counts,
        skill_counts,
        representative_roles,
        latest_count,
        ai_related_count=ai_related_count,
    )

    if history["current_postings"] >= 10 and persistence >= 3:
        conviction = "High"
    elif history["current_postings"] >= 5 and persistence >= 2:
        conviction = "Medium"
    else:
        conviction = "Early"

    if persistence < 2:
        momentum_label = "Newly detected"
    elif momentum > 0:
        momentum_label = f"Rising (+{momentum})"
    elif momentum < 0:
        momentum_label = f"Declining ({momentum})"
    else:
        momentum_label = "Stable"

    print("\n========================================")
    print("COMPANY INTELLIGENCE")
    print("========================================\n")

    print(f"Company: {company_name}")
    print(f"Latest snapshot: {format_snapshot_time(history['latest_seen'])}")
    print(f"First seen: {format_snapshot_time(history['first_seen'])}")
    print(f"Persistence: {persistence} snapshots")
    print(f"Current postings: {history['current_postings']}")
    print(f"Peak postings: {history['peak_postings']}")
    print(f"Hiring momentum: {momentum_label}")
    print(f"Hiring trend: {hiring_trend}")
    if trend_narrative is not None:
        print(f"Trend explanation: {trend_narrative}")
    print(f"Trend confidence: {trend_confidence}")
    if trend_confidence_narrative is not None:
        print(f"Confidence explanation: {trend_confidence_narrative}")
    print(f"Conviction: {conviction}")
    print(f"AI concentration: {ai_concentration:.1f}%")
    if persistence < 2:
        print("Signal maturity: Early observation")
    elif conviction == "High":
        print("Signal maturity: Established")
    else:
        print("Signal maturity: Developing")
    print(f"Hiring archetype: {hiring_archetype}")

    print("\n--- Source Mix ---\n")
    for source, count in source_counts.most_common():
        print(f"- {source}: {count}")

    print("\n--- Top Categories ---\n")
    for category, count in category_counts.most_common(5):
        percentage = (count / latest_count) * 100 if latest_count else 0
        print(f"- {category}: {count} ({percentage:.1f}%)")

    print("\n--- Top Skills ---\n")
    if top_skills:
        for skill, count in top_skills:
            print(f"- {skill}: {count}")
    else:
        print("No tracked skills detected.")

    print("\n--- Representative Roles ---\n")
    for role in representative_roles:
        print(f"- {role}")

    print("\n--- Narrative ---\n")
    print(
        generate_narrative(
            company_name,
            momentum,
            conviction,
            ai_concentration,
            top_category,
            top_skills,
            hiring_archetype,
            observation_window_days=observation_window_days,
        )
    )


def generate_company_trend_narrative(trend, history):
    if not history:
        return None

    first_postings = history["first_postings"]
    current_postings = history["current_postings"]
    peak_postings = history["peak_postings"]

    if trend == "Emerging":
        posting_label = "posting" if current_postings == 1 else "postings"
        snapshot_label = (
            "snapshot" if history["snapshots_active"] == 1 else "snapshots"
        )
        return (
            f"Hiring activity is newly observed, with {current_postings} current "
            f"{posting_label} across {history['snapshots_active']} active "
            f"{snapshot_label} over {history['observation_window_days']:.1f} days."
        )

    if trend == "Expanding":
        return (
            f"Current postings increased from {first_postings} to {current_postings} "
            f"and remain near the observed peak of {peak_postings}."
        )

    if trend == "Stable":
        if first_postings == current_postings == peak_postings:
            return (
                f"Current postings remain at {current_postings}, matching the first "
                "observed and peak levels."
            )

        return (
            f"Current postings are {current_postings}, compared with {first_postings} "
            f"when first observed and an observed peak of {peak_postings}; the "
            "changes do not meet the material expansion or contraction thresholds."
        )

    if trend == "Contracting":
        if current_postings == 0:
            return (
                "No postings are present in the latest snapshot, down from "
                f"{first_postings} when first observed and an observed peak of "
                f"{peak_postings}."
            )

        return (
            f"Current postings declined from {first_postings} to {current_postings} "
            f"and remain below the observed peak of {peak_postings}."
        )

    return None


def generate_company_trend_confidence_narrative(trend_confidence, history):
    if not history:
        return None

    if trend_confidence == "Low":
        reasons = []

        if history["observation_window_days"] < 7:
            reasons.append("the observation window is under 7 days")
        if history["snapshots_active"] < 6:
            reasons.append("there are fewer than 6 active snapshots")
        if history["persistence_score"] < 0.25:
            reasons.append("persistence is below 25%")

        if not reasons:
            return None

        if len(reasons) == 1:
            reason_text = reasons[0]
        elif len(reasons) == 2:
            reason_text = f"{reasons[0]} and {reasons[1]}"
        else:
            reason_text = f"{', '.join(reasons[:-1])}, and {reasons[-1]}"

        return f"Trend confidence is low because {reason_text}."

    if trend_confidence == "Medium":
        return (
            "Trend confidence is medium: the history clears the low-confidence "
            "thresholds but does not meet all established-history thresholds of "
            "30 days, 12 active snapshots, and 75% persistence."
        )

    if trend_confidence == "High":
        return (
            "Trend confidence is high: the history spans "
            f"{history['observation_window_days']:.1f} days across "
            f"{history['snapshots_active']} active snapshots, with "
            f"{history['persistence_score']:.1%} persistence."
        )

    return None


def generate_narrative(
    company_name,
    momentum,
    conviction,
    ai_concentration,
    top_category,
    top_skills,
    hiring_archetype,
    observation_window_days=None,
):
    skill_text = (
        ", ".join(skill for skill, _ in top_skills[:3])
        if top_skills
        else "limited tracked skills"
    )
    archetype_explanation = explain_hiring_archetype(hiring_archetype)

    if conviction == "Early":
        opening = (
            f"{company_name} has recently entered the intelligence set and is still "
            "in the early observation stage."
        )
    elif momentum > 0:
        opening = f"{company_name} appears to be increasing hiring activity across observed roles."
    elif momentum < 0:
        opening = f"{company_name} appears to be reducing hiring activity relative to earlier observations."
    else:
        opening = f"{company_name} shows stable hiring activity across observed snapshots."

    category_sentence = (
        f"Current hiring is concentrated in {top_category}, "
        f"with leading signals including {skill_text}."
    )

    if ai_concentration >= 75:
        ai_sentence = "AI-related hiring dominates the current role mix, suggesting a highly focused investment strategy."
    elif ai_concentration >= 50:
        ai_sentence = "AI-related hiring represents a major share of current recruiting activity."
    elif ai_concentration >= 25:
        ai_sentence = "AI-related hiring is a meaningful component of current recruiting activity."
    elif ai_concentration > 0:
        ai_sentence = "Some AI-related hiring activity is present, but it is not yet a dominant pattern."
    else:
        ai_sentence = "No strong AI hiring concentration is visible at the moment."

    conviction_sentence = (
        f"Signal conviction is {conviction.lower()} based on observed posting volume and persistence."
    )

    if observation_window_days is not None and observation_window_days < 7:
        conviction_sentence += (
            f" The observation window currently spans only {observation_window_days:.1f} days, "
            "so long-term durability is not yet established."
        )

    return (
        f"{opening} "
        f"{category_sentence} "
        f"The dominant hiring pattern is {hiring_archetype}. "
        f"{archetype_explanation} "
        f"{ai_sentence} "
        f"{conviction_sentence}"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python company_intelligence.py \"Company Name\"")
        print("\nAvailable companies:")
        for company, count in get_available_companies():
            print(f"- {company}: {count} postings")
        return

    company_name = " ".join(sys.argv[1:])
    build_company_report(company_name)


if __name__ == "__main__":
    main()

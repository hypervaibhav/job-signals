

SIGNAL_GROUPS = {
    "AI": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "llm",
        "genai",
        "generative ai",
        "langchain",
        "langgraph",
        "prompt engineering",
        "prompt engineer",
    ],
    "AI Infrastructure": [
        "mcp",
        "model context protocol",
        "vector database",
        "rag",
        "embedding",
        "embeddings",
    ],
    "Frontend": [
        "react",
        "javascript",
        "typescript",
        "frontend",
        "front end",
        "ui",
    ],
    "Backend": [
        "python",
        "node",
        "django",
        "flask",
        "api",
        "backend",
    ],
    "Cloud / DevOps": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "linux",
        "devops",
        "cloud",
    ],
    "Data": [
        "sql",
        "postgresql",
        "mysql",
        "sqlite",
        "data analysis",
        "data science",
        "analytics",
        "excel",
    ],
    "CRM / Sales Tools": [
        "salesforce",
        "hubspot",
    ],
    "Marketing / Growth": [
        "seo",
        "content",
        "copywriting",
        "growth",
    ],
}


def normalize_signal(skill):
    normalized = (skill or "").strip().lower()

    for group_name, aliases in SIGNAL_GROUPS.items():
        if normalized in aliases:
            return group_name

    return skill


def is_ai_related(skills):
    return any(normalize_signal(skill) == "AI" for skill in skills)


def normalize_skill_counts(skill_counts):
    grouped = {}

    for skill, count in skill_counts.items():
        group = normalize_signal(skill)
        grouped[group] = grouped.get(group, 0) + count

    return grouped


def normalize_skill_company_counts(skill_company_counts):
    grouped_companies = {}

    for skill, companies in skill_company_counts.items():
        group = normalize_signal(skill)
        grouped_companies.setdefault(group, set()).update(companies)

    return grouped_companies

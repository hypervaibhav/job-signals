

from collections import defaultdict


THEME_DEFINITIONS = {
    "AI Commercialization": {
        "description": (
            "Companies showing AI-related hiring signals appear to be expanding customer-facing, "
            "revenue-generating, and enterprise adoption functions."
        )
    },
    "AI Product Expansion": {
        "description": (
            "Companies are increasing product and engineering investment "
            "around AI-enabled offerings."
        )
    },
    "AI Research Expansion": {
        "description": (
            "Companies continue investing in research-oriented hiring, "
            "suggesting ongoing model, platform, or capability development."
        )
    },
    "Revenue / GTM Expansion": {
        "description": (
            "Companies appear to be expanding revenue, sales, "
            "partnerships, or go-to-market capacity."
        )
    },
    "Engineering Platform Expansion": {
        "description": (
            "Companies appear to be expanding engineering, "
            "infrastructure, or platform capacity."
        )
    },
    "Data & Analytics Investment": {
        "description": (
            "Companies appear to be investing in data, analytics, "
            "or business intelligence capacity."
        )
    },
}


LABEL_TO_THEME = {
    "AI Commercialization / GTM Expansion": "AI Commercialization",
    "AI Product Expansion": "AI Product Expansion",
    "AI Research Expansion": "AI Research Expansion",
    "Sales Expansion": "Revenue / GTM Expansion",
    "Engineering Platform Expansion": "Engineering Platform Expansion",
    "Data / Analytics Expansion": "Data & Analytics Investment",
}



def _strength_label(company_count: int) -> str:
    if company_count >= 4:
        return "Strong"
    if company_count >= 3:
        return "Moderate"
    return "Emerging"


def calculate_theme_snapshot(company_intelligence_rows):
    theme_companies = defaultdict(set)

    for row in company_intelligence_rows:
        intelligence_label = row.get("intelligence")
        company = row.get("company")

        theme_name = LABEL_TO_THEME.get(intelligence_label)

        if not theme_name or not company:
            continue

        theme_companies[theme_name].add(company)

    ordered_theme_names = list(theme_companies)
    ordered_theme_names.extend(
        theme_name
        for theme_name in THEME_DEFINITIONS
        if theme_name not in theme_companies
    )

    themes = []

    for theme_name in ordered_theme_names:
        company_list = sorted(theme_companies[theme_name])
        company_count = len(company_list)

        themes.append(
            {
                "theme": theme_name,
                "strength": _strength_label(company_count),
                "company_count": company_count,
                "companies": company_list,
                "description": THEME_DEFINITIONS[theme_name]["description"],
            }
        )

    return themes


def detect_strategic_themes(company_intelligence_rows):
    """
    company_intelligence_rows should contain dictionaries with:

    {
        "company": "...",
        "intelligence": "AI Product Expansion"
    }
    """

    themes = [
        {
            "theme": theme["theme"],
            "strength": theme["strength"],
            "company_count": theme["company_count"],
            "companies": theme["companies"],
            "narrative": theme["description"],
        }
        for theme in calculate_theme_snapshot(company_intelligence_rows)
        if theme["company_count"] >= 2
    ]

    themes.sort(key=lambda x: x["company_count"], reverse=True)

    return themes

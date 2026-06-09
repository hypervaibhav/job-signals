

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
}


LABEL_TO_THEME = {
    "AI Commercialization / GTM Expansion": "AI Commercialization",
    "AI Product Expansion": "AI Product Expansion",
    "AI Research Expansion": "AI Research Expansion",
}



def _strength_label(company_count: int) -> str:
    if company_count >= 4:
        return "Strong"
    if company_count >= 3:
        return "Moderate"
    return "Emerging"


def detect_strategic_themes(company_intelligence_rows):
    """
    company_intelligence_rows should contain dictionaries with:

    {
        "company": "...",
        "intelligence": "AI Product Expansion"
    }
    """

    theme_companies = defaultdict(set)

    for row in company_intelligence_rows:
        intelligence_label = row.get("intelligence")
        company = row.get("company")

        theme_name = LABEL_TO_THEME.get(intelligence_label)

        if not theme_name or not company:
            continue

        theme_companies[theme_name].add(company)

    themes = []

    for theme_name, companies in theme_companies.items():
        company_list = sorted(companies)
        company_count = len(company_list)

        if company_count < 2:
            continue

        themes.append(
            {
                "theme": theme_name,
                "strength": _strength_label(company_count),
                "company_count": company_count,
                "companies": company_list,
                "narrative": THEME_DEFINITIONS[theme_name]["description"],
            }
        )

    themes.sort(key=lambda x: x["company_count"], reverse=True)

    return themes
import re


# Rules are evaluated in order. Specific functional phrases must appear before
# broad terms such as "executive", "assistant", "engineer", and "analyst".
ROLE_CATEGORIES = (
    (
        "Sales",
        (
            "account executive",
            "account manager",
            "account expansion",
            "account associate",
            "business development",
            "business value manager",
            "client account manager",
            "client partner",
            "commercial hunter",
            "customer manager",
            "enterprise grower",
            "enterprise hunter",
            "new business",
            "revenue",
            "sales engineering",
            "sales",
            "partnerships",
            "解决方案工程师",
            "客户经理",
        ),
    ),
    (
        "Marketing",
        (
            "director of product communications",
            "product communications",
            "marketing",
            "growth marketer",
            "copywriter",
            "freelance writer",
            "writer",
            "content",
            "brand",
            "seo",
        ),
    ),
    (
        "Support",
        (
            "customer experience",
            "customer support",
            "customer success",
            "customer service",
            "support specialist",
            "technical support",
            "help desk",
            "call center",
            "atención al cliente",
            "atencion al cliente",
            "cliente",
        ),
    ),
    (
        "Legal",
        (
            "commercial counsel",
            "legal",
            "counsel",
            "attorney",
            "lawyer",
            "compliance",
        ),
    ),
    (
        "Healthcare",
        (
            "behavior technician",
            "coach psicologo",
            "teleradiology",
            "patient scheduler",
            "psychologist",
            "psicologo",
            "healthcare",
            "clinical",
            "medical",
            "physician",
            "doctor",
            "nurse",
            "nanny",
            "claims",
            "care",
        ),
    ),
    (
        "Data / Analytics",
        (
            "online data analyst",
            "data analyst",
            "data annotator",
            "data labeling",
            "data labeler",
            "data specialist",
            "data engineer",
            "data scientist",
            "business intelligence",
            "bi analyst",
            "annotator",
            "analytics",
        ),
    ),
    (
        "Product",
        (
            "product manager",
            "product owner",
            "product designer",
            "director, ai products",
            "product design",
            "web designer",
            "ui designer",
            "ux",
        ),
    ),
    (
        "People / HR",
        (
            "human resources",
            "sourcing specialist",
            "recruiter",
            "staffing",
            "talent",
            "sourcing",
            "people",
            "hr",
        ),
    ),
    (
        "Education",
        (
            "teacher",
            "professor",
            "profesor",
            "instructor",
            "instructional designer",
            "tutor",
            "education",
            "enseñanza",
        ),
    ),
    (
        "Production / Labour",
        (
            "production",
            "labourer",
            "laborer",
            "operator",
            "warehouse",
            "manufacturing",
            "builder",
            "buffer",
            "valeter",
        ),
    ),
    (
        "Engineering",
        (
            "director of engineering",
            "ai research scientist",
            "reinforcement learning",
            "software",
            "engineering",
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
        ),
    ),
    (
        "Admin / Executive",
        (
            "chief financial officer",
            "chief operating officer",
            "chief of staff",
            "accounting manager",
            "accounts payable",
            "finance manager",
            "executive assistant",
            "office manager",
            "administrator",
            "administrative",
            "assistant",
            "executive",
            "cfo",
            "coo",
        ),
    ),
    (
        "Operations",
        (
            "on-site associate",
            "onsite associate",
            "operations staff",
            "implementation specialist",
            "delivery services",
            "developer solutions",
            "partnerships manager",
            "scrum master",
            "supply chain",
            "crm qa",
            "operations",
            "program manager",
            "project manager",
            "coordinator",
            "analyst",
        ),
    ),
)


def contains_keyword(text, keyword):
    normalized_text = (text or "").lower()
    normalized_keyword = keyword.lower()

    if not normalized_keyword.isascii():
        return normalized_keyword in normalized_text

    pattern = r"\b" + re.escape(normalized_keyword) + r"\b"
    return re.search(pattern, normalized_text) is not None


def classify_role(title):
    for category, phrases in ROLE_CATEGORIES:
        if any(contains_keyword(title, phrase) for phrase in phrases):
            return category

    return "Other"

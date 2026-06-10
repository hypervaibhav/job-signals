import unittest

import company_intelligence
import trends


APPROVED_TAXONOMY = {
    "Sales": [
        "Account Executive - Enterprise, Grower",
        "Account Executive - Japan",
        "Account Executive - Tech",
        "Account Executive, Commercial Hunter (Japanese fluency)",
        "Account Executive, Cross Border China",
        "Account Executive, Digital Native US",
        "Account Executive, Enterprise - New York",
        "Account Executive, Enterprise - SF Bay Area",
        "Account Executive, Enterprise Grower (Australia)",
        "Account Executive, Enterprise Grower (Billing)",
        "Account Executive, Enterprise Hunter (DACH Market)  ",
        "Account Executive, Enterprise Hunter (French fluency)",
        "Account Executive, Enterprise, DACH",
        "Account Executive, Enterprise, France - Paris",
        "Account Executive, Enterprise, UK - London",
        "Commercial Account Executive",
        "DE - Senior Account Executive",
        "ES - Senior Enterprise Account Executive",
        "Enterprise Account Executive  (US, Remote)",
        "Navy Account Executive",
        "Area Vice President, Sales Engineering",
        "Associate Client Partner - Emerging & Scaled (New Business)",
        "Associate Client Partner - Emerging & Scaled (New Business, German Speaking)",
        "Business Value Manager - Sao Paulo",
        "Client Account Manager, App Dev Enterprise",
        "ES - Account Expansion Manager",
        "售前解决方案工程师",
        "高级客户经理",
    ],
    "Admin / Executive": [
        "Accounting Manager (R2R)",
        "Accounts Payable Analyst",
        "Accounts Payable Manager",
        "Chief Financial Officer",
        "Finance Manager",
    ],
    "Operations": [
        "ES - On-Site Associate (Galicia)",
        "ES - On-Site Associate (Getafe)",
        "ES - Onsite Associate (Marchamalo)",
        "ES - Onsite Associate (Miralcampo)",
        "ES - Onsite Associate (Sevilla)",
    ],
    "Marketing": [
        "Assistant Manager, Music Marketing - South Korea (Contractor)",
        "Director of Product Communications",
    ],
    "Engineering": [
        "Director of Engineering, Safety",
    ],
    "Support": [
        "Director, Customer Experience",
    ],
    "Healthcare": [
        "Behavior Technician",
    ],
    "Legal": [
        "Commercial Counsel",
    ],
}


class TaxonomyConflictGoldenTests(unittest.TestCase):
    def test_approved_taxonomy_contains_all_conflict_decisions(self):
        self.assertEqual(
            set(APPROVED_TAXONOMY),
            {
                "Sales",
                "Admin / Executive",
                "Operations",
                "Marketing",
                "Engineering",
                "Support",
                "Healthcare",
                "Legal",
            },
        )
        self.assertEqual(sum(map(len, APPROVED_TAXONOMY.values())), 44)

    def assert_classifier_matches(self, classifier_name, classifier, expected_category):
        for title in APPROVED_TAXONOMY[expected_category]:
            with self.subTest(
                classifier=classifier_name,
                expected_category=expected_category,
                title=title,
            ):
                self.assertEqual(classifier(title), expected_category)


def add_category_test(expected_category):
    test_name = expected_category.lower().replace(" / ", "_").replace(" ", "_")

    def test_trends(self):
        self.assert_classifier_matches(
            "trends",
            trends.classify_role,
            expected_category,
        )

    def test_company_intelligence(self):
        self.assert_classifier_matches(
            "company_intelligence",
            company_intelligence.classify_role,
            expected_category,
        )

    setattr(
        TaxonomyConflictGoldenTests,
        f"test_trends_{test_name}",
        test_trends,
    )
    setattr(
        TaxonomyConflictGoldenTests,
        f"test_company_intelligence_{test_name}",
        test_company_intelligence,
    )


for category in APPROVED_TAXONOMY:
    add_category_test(category)


if __name__ == "__main__":
    unittest.main()

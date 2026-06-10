import unittest

import company_intelligence
import role_taxonomy
import trends


APPROVED_OTHER_MAPPINGS = {
    "Healthcare": [
        "$100k starting bonus... Overnight Teleradiology...",
        "Patient Scheduler",
    ],
    "Operations": [
        "Scrum Master",
        "Supply Chain Specialist",
        "CRM QA Specialist",
    ],
    "Education": [
        "Instructional Designer",
    ],
    "Engineering": [
        "AI Research Scientist - Datadog AI Research (DAIR)",
        "AI Research Scientist – Datadog AI Research (DAIR)",
        "Research Intern – Reinforcement Learning (RL)",
    ],
    "Product": [
        "Director, AI Products",
        "Product Design Intern(Delhi)",
        "Web Designer",
    ],
    "Production / Labour": [
        "Valeter",
    ],
    "Support": [
        "Asesor a call center remoto",
    ],
}

EXPECTED_OTHER = [
    "General Application",
    "<<ENTER DISPLAY JOB TITLE>>",
    "test",
]

PRECEDENCE_DECISIONS = {
    "AI Research Scientist - Datadog AI Research (DAIR)": "Engineering",
    "Environmental Scientists": "Other",
    "Director of Product Communications": "Marketing",
}

CLASSIFIERS = {
    "role_taxonomy": role_taxonomy.classify_role,
    "trends": trends.classify_role,
    "company_intelligence": company_intelligence.classify_role,
}


class OtherTaxonomyMappingGoldenTests(unittest.TestCase):
    def test_approved_mapping_set_is_complete(self):
        self.assertEqual(sum(map(len, APPROVED_OTHER_MAPPINGS.values())), 14)

    def test_approved_other_mappings(self):
        for classifier_name, classifier in CLASSIFIERS.items():
            for expected_category, titles in APPROVED_OTHER_MAPPINGS.items():
                for title in titles:
                    with self.subTest(
                        classifier=classifier_name,
                        expected_category=expected_category,
                        title=title,
                    ):
                        self.assertEqual(classifier(title), expected_category)

    def test_intentional_other_titles_remain_other(self):
        for classifier_name, classifier in CLASSIFIERS.items():
            for title in EXPECTED_OTHER:
                with self.subTest(classifier=classifier_name, title=title):
                    self.assertEqual(classifier(title), "Other")

    def test_precedence_decisions(self):
        for classifier_name, classifier in CLASSIFIERS.items():
            for title, expected_category in PRECEDENCE_DECISIONS.items():
                with self.subTest(
                    classifier=classifier_name,
                    expected_category=expected_category,
                    title=title,
                ):
                    self.assertEqual(classifier(title), expected_category)


if __name__ == "__main__":
    unittest.main()

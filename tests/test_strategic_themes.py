import unittest

from strategic_themes import THEME_DEFINITIONS, detect_strategic_themes


def make_row(company, intelligence):
    return {
        "company": company,
        "intelligence": intelligence,
    }


class StrategicThemesV1CharacterizationTests(unittest.TestCase):
    def test_ai_commercialization_archetype_maps_to_ai_commercialization(self):
        themes = detect_strategic_themes(
            [
                make_row("Mistral", "AI Commercialization / GTM Expansion"),
                make_row("Acme", "AI Commercialization / GTM Expansion"),
            ]
        )

        self.assertEqual(themes[0]["theme"], "AI Commercialization")

    def test_ai_product_expansion_archetype_maps_to_ai_product_expansion(self):
        themes = detect_strategic_themes(
            [
                make_row("Integrate", "AI Product Expansion"),
                make_row("Levelai", "AI Product Expansion"),
            ]
        )

        self.assertEqual(themes[0]["theme"], "AI Product Expansion")

    def test_ai_research_expansion_archetype_maps_to_ai_research_expansion(self):
        themes = detect_strategic_themes(
            [
                make_row("Datadog", "AI Research Expansion"),
                make_row("Acme", "AI Research Expansion"),
            ]
        )

        self.assertEqual(themes[0]["theme"], "AI Research Expansion")

    def test_unknown_archetypes_are_ignored(self):
        themes = detect_strategic_themes(
            [
                make_row("Acme", "Sales Expansion"),
                make_row("Beta", "Sales Expansion"),
                make_row("Gamma", "Unknown Expansion"),
            ]
        )

        self.assertEqual(themes, [])

    def test_missing_company_or_intelligence_values_are_ignored(self):
        themes = detect_strategic_themes(
            [
                {"company": "Acme"},
                {"intelligence": "AI Product Expansion"},
                make_row("", "AI Product Expansion"),
                make_row("Beta", ""),
                make_row(None, "AI Product Expansion"),
                make_row("Gamma", None),
            ]
        )

        self.assertEqual(themes, [])

    def test_duplicate_company_rows_count_once(self):
        themes = detect_strategic_themes(
            [
                make_row("Acme", "AI Product Expansion"),
                make_row("Acme", "AI Product Expansion"),
                make_row("Beta", "AI Product Expansion"),
            ]
        )

        self.assertEqual(themes[0]["company_count"], 2)
        self.assertEqual(themes[0]["companies"], ["Acme", "Beta"])

    def test_one_company_themes_are_suppressed(self):
        themes = detect_strategic_themes(
            [make_row("Acme", "AI Product Expansion")]
        )

        self.assertEqual(themes, [])

    def test_two_company_themes_produce_emerging_strength(self):
        themes = detect_strategic_themes(
            [
                make_row("Beta", "AI Product Expansion"),
                make_row("Acme", "AI Product Expansion"),
            ]
        )

        self.assertEqual(themes[0]["strength"], "Emerging")
        self.assertEqual(themes[0]["company_count"], 2)
        self.assertEqual(themes[0]["companies"], ["Acme", "Beta"])

    def test_three_company_themes_produce_moderate_strength(self):
        themes = detect_strategic_themes(
            [
                make_row("Acme", "AI Product Expansion"),
                make_row("Beta", "AI Product Expansion"),
                make_row("Gamma", "AI Product Expansion"),
            ]
        )

        self.assertEqual(themes[0]["strength"], "Moderate")
        self.assertEqual(themes[0]["company_count"], 3)

    def test_four_company_themes_produce_strong_strength(self):
        themes = detect_strategic_themes(
            [
                make_row("Acme", "AI Product Expansion"),
                make_row("Beta", "AI Product Expansion"),
                make_row("Gamma", "AI Product Expansion"),
                make_row("Delta", "AI Product Expansion"),
            ]
        )

        self.assertEqual(themes[0]["strength"], "Strong")
        self.assertEqual(themes[0]["company_count"], 4)

    def test_static_narrative_text_remains_unchanged(self):
        expected_narratives = {
            "AI Commercialization": (
                "Companies showing AI-related hiring signals appear to be expanding "
                "customer-facing, revenue-generating, and enterprise adoption functions."
            ),
            "AI Product Expansion": (
                "Companies are increasing product and engineering investment around "
                "AI-enabled offerings."
            ),
            "AI Research Expansion": (
                "Companies continue investing in research-oriented hiring, suggesting "
                "ongoing model, platform, or capability development."
            ),
        }

        for theme_name, expected in expected_narratives.items():
            with self.subTest(theme=theme_name):
                self.assertEqual(
                    THEME_DEFINITIONS[theme_name]["description"],
                    expected,
                )

    def test_themes_sort_by_company_count_descending(self):
        themes = detect_strategic_themes(
            [
                make_row("Research A", "AI Research Expansion"),
                make_row("Research B", "AI Research Expansion"),
                make_row("Product A", "AI Product Expansion"),
                make_row("Product B", "AI Product Expansion"),
                make_row("Product C", "AI Product Expansion"),
                make_row("Product D", "AI Product Expansion"),
                make_row("Commercial A", "AI Commercialization / GTM Expansion"),
                make_row("Commercial B", "AI Commercialization / GTM Expansion"),
                make_row("Commercial C", "AI Commercialization / GTM Expansion"),
            ]
        )

        self.assertEqual(
            [(theme["theme"], theme["company_count"]) for theme in themes],
            [
                ("AI Product Expansion", 4),
                ("AI Commercialization", 3),
                ("AI Research Expansion", 2),
            ],
        )

    def test_equal_count_themes_retain_first_seen_theme_order(self):
        themes = detect_strategic_themes(
            [
                make_row("Research B", "AI Research Expansion"),
                make_row("Product B", "AI Product Expansion"),
                make_row("Research A", "AI Research Expansion"),
                make_row("Product A", "AI Product Expansion"),
                make_row("Commercial B", "AI Commercialization / GTM Expansion"),
                make_row("Commercial A", "AI Commercialization / GTM Expansion"),
            ]
        )

        self.assertEqual(
            [theme["theme"] for theme in themes],
            [
                "AI Research Expansion",
                "AI Product Expansion",
                "AI Commercialization",
            ],
        )


if __name__ == "__main__":
    unittest.main()

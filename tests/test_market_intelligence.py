import unittest

try:
    import market_intelligence
except ModuleNotFoundError:
    market_intelligence = None


def build_market(**overrides):
    inputs = {
        "latest_job_count": 10,
        "previous_job_count": 8,
        "net_change": 2,
        "evidence_confidence": "HIGH",
        "evidence_confidence_reason": "Snapshot size and source mix are stable.",
        "signal_rows": [
            {
                "signal": "AI",
                "postings": 8,
                "signal_strength": 80,
                "opportunity_score": 70,
            },
            {
                "signal": "Frontend",
                "postings": 6,
                "signal_strength": 90,
                "opportunity_score": 40,
            },
        ],
        "category_changes": [
            {"category": "Engineering", "current_roles": 5, "change": 2},
            {"category": "Sales", "current_roles": 3, "change": -1},
        ],
        "company_changes": [
            {"company": "Mistral", "current_postings": 10, "change": 3},
            {"company": "Stripe", "current_postings": 4, "change": 1},
        ],
        "company_intelligence_rows": [
            {
                "company": "Integrate",
                "intelligence": "AI Product Expansion",
                "trend_confidence": "High",
            },
            {
                "company": "Levelai",
                "intelligence": "AI Product Expansion",
                "trend_confidence": "Medium",
            },
            {
                "company": "Mistral",
                "intelligence": "AI Commercialization / GTM Expansion",
                "trend_confidence": "High",
            },
        ],
        "strategic_theme_rows": [
            {
                "theme": "AI Product Expansion",
                "lifecycle": "Stable",
                "confidence": "High",
                "current_company_count": 2,
                "peak_company_count": 2,
                "snapshots_active": 6,
                "total_eligible_snapshots": 6,
                "persistence_score": 1.0,
            }
        ],
    }
    inputs.update(overrides)
    module = market_module()
    return module.build_market_intelligence(**inputs)


def market_module():
    if market_intelligence is None:
        raise AssertionError(
            "market_intelligence.py must implement structured market synthesis"
        )
    return market_intelligence


class MarketIntelligenceTests(unittest.TestCase):
    def test_expanding_market_direction(self):
        intelligence = build_market(net_change=3)

        self.assertEqual(intelligence["market_direction"], "Expanding")

    def test_contracting_market_direction(self):
        intelligence = build_market(net_change=-2)

        self.assertEqual(intelligence["market_direction"], "Contracting")

    def test_flat_market_direction(self):
        intelligence = build_market(net_change=0)

        self.assertEqual(intelligence["market_direction"], "Flat")

    def test_top_signal_prefers_highest_opportunity_score(self):
        intelligence = build_market(
            signal_rows=[
                {
                    "signal": "AI",
                    "postings": 8,
                    "signal_strength": 80,
                    "opportunity_score": 70,
                },
                {
                    "signal": "Frontend",
                    "postings": 6,
                    "signal_strength": 90,
                    "opportunity_score": 90,
                },
            ]
        )

        self.assertEqual(intelligence["top_signal"]["signal"], "Frontend")

    def test_top_signal_falls_back_to_signal_strength_then_postings(self):
        intelligence = build_market(
            signal_rows=[
                {"signal": "AI", "postings": 8, "signal_strength": 80},
                {"signal": "Frontend", "postings": 12, "signal_strength": 70},
            ]
        )

        self.assertEqual(intelligence["top_signal"]["signal"], "AI")

    def test_top_signal_falls_back_to_postings_when_strength_is_missing(self):
        intelligence = build_market(
            signal_rows=[
                {"signal": "AI", "postings": 8},
                {"signal": "Frontend", "postings": 12},
            ]
        )

        self.assertEqual(intelligence["top_signal"]["signal"], "Frontend")

    def test_company_strategy_mix_counts_archetypes(self):
        intelligence = build_market()

        self.assertEqual(
            intelligence["company_strategy_mix"],
            {
                "AI Product Expansion": 2,
                "AI Commercialization / GTM Expansion": 1,
            },
        )

    def test_company_strategy_mix_ignores_missing_archetypes(self):
        intelligence = build_market(
            company_intelligence_rows=[
                {"company": "Integrate", "intelligence": "AI Product Expansion"},
                {"company": "Unknown"},
                {"company": "Blank", "intelligence": ""},
            ]
        )

        self.assertEqual(
            intelligence["company_strategy_mix"],
            {"AI Product Expansion": 1},
        )

    def test_strategic_theme_rows_are_preserved(self):
        themes = [
            {
                "theme": "AI Product Expansion",
                "lifecycle": "Emerging",
                "confidence": "Low",
                "current_company_count": 3,
                "current_members": ["Integrate", "Levelai", "Ryzlabs"],
            }
        ]

        intelligence = build_market(strategic_theme_rows=themes)

        self.assertEqual(intelligence["strategic_themes"], themes)

    def test_caveats_include_low_theme_confidence(self):
        intelligence = build_market(
            strategic_theme_rows=[
                {
                    "theme": "AI Product Expansion",
                    "confidence": "Low",
                    "total_eligible_snapshots": 6,
                }
            ]
        )

        self.assertIn(
            "One or more strategic themes have low confidence.",
            intelligence["caveats"],
        )

    def test_caveats_include_low_evidence_confidence(self):
        intelligence = build_market(
            evidence_confidence="LOW",
            evidence_confidence_reason="Source mix changed significantly.",
        )

        self.assertIn(
            "Evidence confidence is LOW: Source mix changed significantly.",
            intelligence["caveats"],
        )

    def test_caveats_include_small_net_movement(self):
        intelligence = build_market(net_change=1)

        self.assertIn(
            "Net movement is small; treat direction as near-flat.",
            intelligence["caveats"],
        )

    def test_caveats_include_young_theme_history(self):
        intelligence = build_market(
            strategic_theme_rows=[
                {
                    "theme": "AI Product Expansion",
                    "confidence": "High",
                    "total_eligible_snapshots": 2,
                }
            ]
        )

        self.assertIn(
            "One or more strategic themes have fewer than 3 eligible snapshots.",
            intelligence["caveats"],
        )

    def test_caveats_include_low_company_trend_confidence(self):
        intelligence = build_market(
            company_intelligence_rows=[
                {
                    "company": "Mistral",
                    "intelligence": "AI Commercialization / GTM Expansion",
                    "trend_confidence": "Low",
                }
            ]
        )

        self.assertIn(
            "One or more company trend signals have low confidence.",
            intelligence["caveats"],
        )

    def test_market_read_is_deterministic_and_concise(self):
        intelligence = build_market(net_change=2)

        self.assertEqual(
            intelligence["market_read"],
            "The market is expanding with HIGH evidence confidence. AI is "
            "the strongest current signal. Strategic theme coverage is led "
            "by AI Product Expansion.",
        )

    def test_empty_minimal_input_behavior(self):
        module = market_module()

        intelligence = module.build_market_intelligence(
            latest_job_count=0,
            previous_job_count=0,
            net_change=0,
            evidence_confidence="LOW",
            evidence_confidence_reason="Insufficient history",
            signal_rows=[],
            category_changes=[],
            company_changes=[],
            company_intelligence_rows=[],
            strategic_theme_rows=[],
        )

        self.assertEqual(intelligence["market_direction"], "Flat")
        self.assertEqual(
            intelligence["evidence_confidence"],
            {"level": "LOW", "reason": "Insufficient history"},
        )
        self.assertIsNone(intelligence["top_signal"])
        self.assertIsNone(intelligence["top_category_movement"])
        self.assertIsNone(intelligence["top_company_momentum"])
        self.assertEqual(intelligence["company_strategy_mix"], {})
        self.assertEqual(intelligence["strategic_themes"], [])
        self.assertEqual(
            intelligence["market_read"],
            "The market is flat with LOW evidence confidence. No leading "
            "signal is available. No strategic theme rows are available.",
        )


if __name__ == "__main__":
    unittest.main()

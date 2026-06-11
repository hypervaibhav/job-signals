# Job Signals Agent Instructions

## Mission

Job Signals is a labor market intelligence platform.

It is NOT:
- a job board
- an ATS
- a recruiting platform

The purpose is to infer:
- hiring trends
- company strategy
- market direction
- skill demand
- hiring archetypes

from public job postings.

## Current Phase

Phase 2: Intelligence Layer

## Business Objective

Job Signals should evolve toward monetizable labor market intelligence.

Prefer features that improve:
- signal quality
- strategic insight
- predictive value
- productization potential

Avoid features that are interesting but do not increase intelligence value.

## Architecture Ownership

scraper.py
- collection

database.py
- persistence

company_history.py
- company memory
- persistence
- observation windows

company_intelligence.py
- interpretation
- conviction
- archetypes
- narratives

trends.py
- market intelligence

daily_report.py
- orchestration
- presentation

signal_taxonomy.py
- signal definitions

role_taxonomy.py
- canonical role classification

strategic_themes.py
- strategic theme calculation
- theme snapshot calculation

strategic_theme_history.py
- strategic theme persistence
- theme memory
- historical theme metrics

strategic_theme_lifecycle.py
- theme lifecycle classification
- emerging / stable / expanding / contracting / disappeared labels

strategic_theme_narratives.py
- theme lifecycle explanations
- theme narrative generation

strategic_theme_backfill.py
- historical theme reconstruction
- version-isolated backfill

theme_history_report.py
- standalone theme history readout
- theme lifecycle and narrative presentation

Company History

* company_history.py is the authoritative source for:
    * persistence
    * observation windows
    * first seen timestamps
    * latest seen timestamps
    * peak postings
    * company memory metrics
* Do not reconstruct persistence directly from job rows when company history is available.

Role Taxonomy

* role_taxonomy.py is the canonical role-classification layer.
* trends.py and company_intelligence.py must use the shared taxonomy.
* Role categories and strategic signals are separate concepts.
* AI should not be treated as a role category.

Signal Taxonomy

* signal_taxonomy.py owns:
    * signal normalization
    * signal grouping
    * canonical AI-related detection
* Use signal_taxonomy.is_ai_related() when determining whether a posting is AI-related.
* Avoid creating additional AI-detection implementations.

Strategic Theme Intelligence

* strategic_themes.py owns:
    * strategic theme calculation
    * theme snapshot calculation
    * canonical mapping from company archetypes to strategic themes
* strategic_theme_history.py is the authoritative source for:
    * theme persistence
    * theme first detected timestamps
    * theme latest detected timestamps
    * theme active snapshot counts
    * theme eligible snapshot counts
    * theme persistence score
    * current company count
    * peak company count
    * theme membership history
* strategic_theme_lifecycle.py owns lifecycle classification:
    * Emerging
    * Stable
    * Expanding
    * Contracting
    * Disappeared
* strategic_theme_narratives.py owns deterministic theme lifecycle explanations.
* strategic_theme_backfill.py owns historical reconstruction and should default to an isolated engine version such as v2-backfill.
* theme_history_report.py owns standalone inspection and presentation of theme history.
* Do not use detect_strategic_themes() for persistence or backfill because it applies presentation filtering.
* Use calculate_theme_snapshot() when complete internal theme snapshots are required.
* Keep daily_report.py focused on orchestration and presentation.

Testing Strategy

* Prefer characterization tests before major refactors.
* Preserve approved taxonomy decisions through golden tests.
* New intelligence logic should be covered by focused unit tests before large refactors.

## Codex Workflow

## Codex Task Principles

When proposing Codex tasks:

1. Prefer inspection before implementation.
2. Prefer characterization tests before production code.
3. Keep tasks small and bounded.
4. Optimize for minimal diffs and clean commits.
5. Respect AGENTS.md ownership rules.
6. Do not propose architecture that duplicates existing persistence, taxonomy, lifecycle, or narrative logic.
7. When uncertain, inspect the repository before proposing implementation.
8. Assume Codex usage is valuable and avoid unnecessarily large tasks.
9. Preserve architectural layering:

   calculation
   ↓
   persistence
   ↓
   lifecycle
   ↓
   narratives
   ↓
   presentation

10. Extend existing intelligence systems before introducing new systems.

Development Process

* For non-trivial features:
    1. Inspect existing implementation.
    2. Add characterization tests for current behavior.
    3. Run the full test suite.
    4. Propose the smallest implementation that satisfies the tests.
    5. Re-run the full test suite.
    6. Summarize changes, risks, and next steps.

Implementation Rules

* Prefer extending existing intelligence systems over creating parallel systems.
* Do not duplicate taxonomy, trend, persistence, or narrative logic.
* Use authoritative sources already defined in this document.
* Separate calculation, persistence, and presentation responsibilities.

Commit Policy

* Do not create commits unless explicitly instructed.
* Before any commit, provide:
    * files changed
    * behavior changed
    * test results
    * risks and follow-ups

Strategic Theme Engine

* Preserve separation between:
    * calculation
    * persistence
    * lifecycle classification
    * narrative generation
    * presentation
* Keep daily_report.py focused on orchestration and presentation.
* Keep strategic intelligence calculations inside domain modules.
* Do not duplicate strategic theme persistence, lifecycle, narrative, or backfill logic.
* Keep live observed history and reconstructed backfill history version-isolated unless explicitly instructed otherwise.

## Rules

- Do not change product direction.
- Do not introduce dashboards unless requested.
- Prefer small changes.
- Prefer refactors over rewrites.
- Add tests for new behavior.
- Preserve CLI behavior.
- Do not commit directly to main unless instructed.
- Prefer characterization tests before implementing new intelligence features.

## Verification

Run:

./venv/bin/python -m unittest discover -v

./venv/bin/python -m compileall .

git diff --check

If relevant:

./venv/bin/python daily_report.py

## Required Output

1. Files changed
2. Summary
3. Tests
4. Verification
5. Risks
6. Follow-up recommendations
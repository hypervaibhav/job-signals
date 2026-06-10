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

Testing Strategy

* Prefer characterization tests before major refactors.
* Preserve approved taxonomy decisions through golden tests.
* New intelligence logic should be covered by focused unit tests before large refactors.

## Codex Workflow

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
    * presentation
* Keep daily_report.py focused on orchestration and presentation.
* Keep strategic intelligence calculations inside domain modules.

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

If relevant:

./venv/bin/python daily_report.py

## Required Output

1. Files changed
2. Summary
3. Tests
4. Verification
5. Risks
6. Follow-up recommendations
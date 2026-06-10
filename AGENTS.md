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

## Rules

- Do not change product direction.
- Do not introduce dashboards unless requested.
- Prefer small changes.
- Prefer refactors over rewrites.
- Add tests for new behavior.
- Preserve CLI behavior.
- Do not commit directly to main unless instructed.

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
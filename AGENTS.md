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
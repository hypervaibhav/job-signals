# Job Signals - Project Context

## Mission

Job Signals is a labor market intelligence platform.

The goal is not to build a job board.

The goal is to infer company strategy, technology adoption, skill demand, and market direction from hiring behavior.

## Business Objective

Job Signals is intended to become a monetizable labor market intelligence asset.

Potential customers may eventually include:
- job seekers
- recruiters
- founders
- operators
- investors

New intelligence features should improve at least one of:
- predictive power
- signal quality
- strategic insight
- monetization potential

Avoid building features that are interesting but do not increase intelligence value.

---

## Project Thesis

Hiring behavior is an early indicator of company and market change.

Companies reveal future priorities through recruiting before those priorities appear in earnings calls, press releases, public narratives, or product announcements.

Job Signals converts hiring activity into actionable intelligence.

---

## Current Phase

Phase 1: Data Collection & Signal Detection
Status: Complete

Phase 2: Company & Market Intelligence
Status: In Progress

Future Phase: Predictive Intelligence

---

## Current Reality

Sources:
- Lever
- Greenhouse
- Remotive
- RemoteOK

Database:
- SQLite (jobs.db)

Historical Coverage:
- 27 snapshots
- ~4 days of history
- Strategic theme history exists
- Strategic theme lifecycle classification exists
- Strategic theme narratives exist
- Historical strategic theme backfill exists

Important:
- Historical snapshot architecture exists.
- Company history is technically possible.
- Long-term trend intelligence is not yet reliable due to limited history.
- Current history is best used for persistence analysis, not forecasting.

---

## North Star

Jobs
→ Signals
→ Company Intelligence
→ Market Intelligence
→ Predictive Intelligence

The objective is to move up this ladder without becoming a job board.

---

## Current Focus

Priority 1
- Theme Confidence
- Theme Acceleration
- Market Intelligence Layer

Priority 2
- Theme Relationships
- Hiring Cluster Detection
- Company Similarity Analysis

Priority 3
- Strategic Theme Refinement
- Market Narrative Intelligence

Not Prioritized Right Now
- Dashboards
- Complex visualizations
- Similarity graphs
- UI work
- Feature expansion without intelligence value
- Job board functionality
- Applicant workflows
- Resume tooling
- Candidate matching

---

## Recent Decisions

2026-06-08
- Completed Company Intelligence v1
- Added hiring archetypes
- Added persistence-aware conviction
- Added persistence-aware narratives
- Added company watchlists

2026-06-09
- Added Company Memory layer
- Added historical company persistence tracking
- Added observation window tracking
- Refactored persistence into a single-source architecture
- Company history designated as the authoritative source for persistence metrics
- Deferred full company trend intelligence
- Reason: only 12 snapshots spanning ~14 hours
- Current history supports persistence analysis but not reliable trend forecasting

2026-06-11
- Implemented Strategic Theme History
- Added strategic theme persistence
- Added strategic theme lifecycle classification
- Added strategic theme narratives
- Added standalone theme history reporting
- Added human-readable lifecycle readouts
- Added historical strategic theme backfill
- Backfilled 27 historical job snapshots into theme history using engine_version=v2-backfill
- Strategic theme history designated as the authoritative source for theme persistence metrics
- Lifecycle classification separated from persistence
- Narrative generation separated from lifecycle classification

---

## Architecture Snapshot

company_history.py
- Owns company memory
- Owns persistence metrics
- Owns observation windows
- Owns first/latest seen tracking

company_intelligence.py
- Owns hiring archetype detection
- Owns conviction interpretation
- Owns narrative generation

strategic_theme_history.py
- Owns strategic theme memory
- Owns theme persistence metrics
- Owns first/latest detected tracking

strategic_theme_lifecycle.py
- Owns theme lifecycle classification
- Owns Emerging/Stable/Expanding/Contracting/Disappeared interpretation

strategic_theme_narratives.py
- Owns theme lifecycle explanations
- Owns deterministic theme narratives

theme_history_report.py
- Owns strategic theme inspection
- Consumes history, lifecycle, and narrative layers

daily_report.py
- Owns report presentation
- Consumes history and intelligence layers

Design Rule:
Company history is the authoritative source for company persistence-related metrics.
Strategic theme history is the authoritative source for theme persistence-related metrics.

---

## Success Criteria

Job Signals succeeds if it can identify:

- Emerging technologies
- Emerging skills
- Company expansion signals
- Talent demand shifts
- Strategic themes that persist across companies and time
- Market direction changes

Before those developments become obvious to the broader market.

Ultimate Goal:

Build a valuable labor market intelligence asset that can eventually be monetized.
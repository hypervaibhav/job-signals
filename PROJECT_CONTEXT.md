# Job Signals - Project Context

## Mission

Job Signals is a labor market intelligence platform.

The goal is not to build a job board.

The goal is to infer company strategy, technology adoption, skill demand, and market direction from hiring behavior.

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
- 12 snapshots
- ~14 hours of history

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
- Historical Company Trends
- Company Intelligence v2
- Narrative Intelligence

Priority 2
- Hiring Cluster Detection
- Market Intelligence

Priority 3
- Strategic Theme Refinement
- Company Similarity Analysis

Not Prioritized Right Now
- Dashboards
- Complex visualizations
- Similarity graphs
- UI work
- Feature expansion without intelligence value

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

daily_report.py
- Owns report presentation
- Consumes history and intelligence layers

Design Rule:
Company history is the authoritative source for persistence-related metrics.

---

## Success Criteria

Job Signals succeeds if it can identify:

- Emerging technologies
- Emerging skills
- Company expansion signals
- Talent demand shifts
- Market direction changes

Before those developments become obvious to the broader market.

Ultimate Goal:

Build a valuable labor market intelligence asset that can eventually be monetized.


# Job Signals - Architecture

## System Overview

Job Signals transforms job postings into labor market intelligence.

Data Flow:

Sources
→ scraper.py
→ database.py
→ jobs.db
→ trends.py
→ company_intelligence.py
→ daily_report.py
→ Intelligence Report

---

## Core Principles

1. Separate collection from intelligence.
2. Separate intelligence from reporting.
3. Prefer new modules over expanding daily_report.py.
4. Preserve historical data whenever possible.
5. Build intelligence layers, not dashboard features.

---

## File Responsibilities

### scraper.py

Purpose:
- Collect jobs from external sources.

Responsibilities:
- Source ingestion
- Job normalization
- Deduplication preparation
- Snapshot creation

Should NOT contain:
- Intelligence logic
- Signal scoring
- Report generation

---

### database.py

Purpose:
- Persistence layer.

Responsibilities:
- Database creation
- Database queries
- Snapshot storage
- Job lifecycle storage

Tables:
- jobs
- job_snapshots
- snapshot_metadata

Should NOT contain:
- Intelligence interpretation
- Narrative generation

---

### trends.py

Purpose:
- Signal intelligence engine.

Responsibilities:
- Skill extraction
- Category classification
- Signal taxonomy usage
- Momentum detection
- Acceleration detection
- Opportunity scoring

Owns:
- Market signals
- Skills
- Categories

Should NOT contain:
- Company narratives
- Report formatting

---

### signal_taxonomy.py

Purpose:
- Signal normalization.

Responsibilities:
- Skill grouping
- Signal vocabulary
- Canonical signal definitions

Owns:
- AI
- Frontend
- Backend
- Cloud / DevOps
- Data
- CRM
- Marketing
- Future signal groups

---

### signal_history.py

Purpose:
- Historical signal tracking.

Responsibilities:
- Signal persistence
- Historical signal comparisons
- Signal memory

Owns:
- Signal history

---

### company_intelligence.py

Purpose:
- Company interpretation layer.

Responsibilities:
- Hiring archetypes
- Company conviction
- Company narratives
- Company watchlists
- Expansion signal detection

Current Intelligence:
- AI Commercialization / GTM Expansion
- AI Product Expansion
- AI Research Expansion

Owns:
- Company-level intelligence

Should NOT contain:
- Report formatting
- Database management

---

### leaderboard.py

Purpose:
- Rankings and leaderboards.

Responsibilities:
- Signal rankings
- Opportunity rankings
- Report helper outputs

---

### daily_report.py

Purpose:
- Report orchestration.

Responsibilities:
- Load intelligence modules
- Assemble report sections
- Print final report

Should NOT contain:
- Major business logic
- New intelligence systems

Rule:
If a feature requires more than a few helper functions, create a dedicated module instead of adding it here.

---

### category_debug.py

Purpose:
- Category debugging and validation.

---

### skill_debug.py

Purpose:
- Skill extraction debugging and validation.

---

## Current Data Model

jobs
- Current job state
- first_seen
- last_seen
- active/inactive lifecycle

job_snapshots
- Historical observations
- Snapshot history
- Company history source

snapshot_metadata
- Snapshot tracking
- Collection metadata

---

## Planned Modules

### company_history.py

Purpose:
- Company persistence tracking
- Company memory layer
- Historical company observations

Future Responsibilities:
- Active snapshots
- First seen
- Persistence scoring
- Company trend history

---

### strategic_themes.py

Purpose:
- Market theme detection.

Examples:
- AI Commercialization
- Enterprise Expansion
- Platform Maturity
- AI Infrastructure Growth

---

### market_intelligence.py

Purpose:
- Cross-company intelligence.

Future Responsibilities:
- Emerging clusters
- Market narratives
- Market direction analysis

---

## Architecture Rule

When adding a feature, first determine what level it belongs to:

Jobs
→ Signals
→ Companies
→ Market
→ Prediction

Then place it in the module that owns that level.

Avoid placing new intelligence logic directly into daily_report.py.
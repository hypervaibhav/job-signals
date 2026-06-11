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
- Signal intelligence
- Opportunity scoring

Uses:
- role_taxonomy.py
- signal_taxonomy.py

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
- Signal normalization
- AI-related detection

Owns:
- normalize_signal()
- is_ai_related()
- AI
- Frontend
- Backend
- Cloud / DevOps
- Data
- CRM
- Marketing
- Future signal groups

---

### role_taxonomy.py

Purpose:
- Canonical role classification.

Responsibilities:
- Shared role categorization
- Category precedence rules
- Classification consistency across intelligence systems
- Multilingual role matching support

Owns:
- Sales
- Engineering
- Data / Analytics
- Marketing
- Support
- Legal
- Healthcare
- Product
- Operations
- Admin / Executive
- People / HR
- Education
- Production / Labour

Design Rule:
Role categories describe job function.
Role categories are not strategic signals.

All role classification should flow through role_taxonomy.py.

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

### company_history.py

Purpose:
- Company memory and persistence layer.

Responsibilities:
- Company persistence tracking
- Company memory
- First seen tracking
- Latest seen tracking
- Observation window tracking
- Historical company observations

Owns:
- snapshots_active
- persistence_score
- observation_window_days
- first_seen
- latest_seen
- current_postings
- peak_postings

Should NOT contain:
- Narrative generation
- Hiring archetype detection
- Report formatting

---

### company_intelligence.py

Purpose:
- Company interpretation layer.

Responsibilities:
- Hiring archetypes
- Company conviction
- Company narratives
- Expansion signal detection
- Interpretation of company history

Current Intelligence:
- AI Commercialization / GTM Expansion
- AI Product Expansion
- AI Research Expansion
- Observation-window-aware conviction
- Canonical AI-related detection
- Taxonomy-driven role interpretation

Uses:
- company_history.py
- role_taxonomy.py
- signal_taxonomy.py

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

## Intelligence Modules


The following modules are active components of the intelligence architecture.

### strategic_themes.py

Purpose:
- Market theme detection.

Examples:
- AI Commercialization
- Enterprise Expansion
- Platform Maturity
- AI Infrastructure Growth

---

### strategic_theme_history.py

Purpose:
- Strategic theme memory and persistence layer.

Responsibilities:
- Theme persistence tracking
- Theme history storage
- First seen tracking
- Latest seen tracking
- Theme persistence metrics
- Historical theme observations

Owns:
- first_detected
- latest_detected
- snapshots_active
- total_eligible_snapshots
- persistence_score
- current_company_count
- peak_company_count
- membership history

Should NOT contain:
- Lifecycle classification
- Narrative generation
- Report formatting

---

### strategic_theme_lifecycle.py

Purpose:
- Strategic theme lifecycle classification.

Responsibilities:
- Emerging detection
- Stable detection
- Expanding detection
- Contracting detection
- Disappeared detection

Uses:
- strategic_theme_history.py

Owns:
- Theme lifecycle interpretation

Should NOT contain:
- Persistence storage
- Narrative generation
- Report formatting

---

### strategic_theme_narratives.py

Purpose:
- Strategic theme interpretation layer.

Responsibilities:
- Lifecycle explanations
- Theme narratives
- Human-readable interpretation of theme history

Uses:
- strategic_theme_history.py
- strategic_theme_lifecycle.py

Owns:
- Theme-level narratives

Should NOT contain:
- Persistence storage
- Lifecycle classification
- Report formatting

---

### strategic_theme_backfill.py

Purpose:
- Historical strategic theme reconstruction.

Responsibilities:
- Historical theme backfill
- Reconstructing theme snapshots from historical job snapshots
- Safe version-isolated reconstruction

Uses:
- company intelligence reconstruction
- strategic_themes.py
- strategic_theme_history.py

Should NOT contain:
- Live reporting
- Narrative generation

---

### theme_history_report.py

Purpose:
- Strategic theme inspection and debugging report.

Responsibilities:
- Theme history readout
- Lifecycle display
- Narrative display
- Human-readable theme memory inspection

Uses:
- strategic_theme_history.py
- strategic_theme_lifecycle.py
- strategic_theme_narratives.py

Should NOT contain:
- Persistence logic
- Theme calculation

---

### market_intelligence.py

Purpose:
- Cross-company intelligence.

Future Responsibilities:
- Emerging clusters
- Market narratives
- Market direction analysis

---

### theme_confidence.py

Purpose:
- Strategic theme confidence scoring.

Future Responsibilities:
- Theme confidence calculation
- Confidence normalization
- Confidence interpretation
- Confidence support for market intelligence

Uses:
- strategic_theme_history.py
- strategic_theme_lifecycle.py

---

## Company Intelligence Data Flow

job_snapshots
→ company_history.py
→ daily_report.py
→ company_intelligence.py
→ Intelligence Report

Design Rule:
company_history.py is the authoritative source for persistence and observation-window metrics.

---

## Strategic Theme Intelligence Data Flow

job_snapshots
→ company_intelligence.py
→ strategic_themes.py
→ strategic_theme_history.py
→ strategic_theme_lifecycle.py
→ strategic_theme_narratives.py
→ theme_history_report.py

Design Rule:
strategic_theme_history.py is the authoritative source for theme persistence and historical metrics.
Lifecycle classification should flow through strategic_theme_lifecycle.py.
Narrative generation should flow through strategic_theme_narratives.py.

Never use detect_strategic_themes() for persistence or backfill.
Use calculate_theme_snapshot() whenever complete internal theme snapshots are required.

---

## Taxonomy Layer

Role Taxonomy
→ role_taxonomy.py
→ Job-function classification

Signal Taxonomy
→ signal_taxonomy.py
→ Strategic signal classification

Design Rule:

Role categories answer:
"What kind of job is this?"

Signals answer:
"What market trend does this represent?"

These concepts should remain separate.

---

## Architecture Rule

When adding a feature, first determine what level it belongs to:

Jobs
→ Signals
→ Companies
→ Market
→ Prediction

Then place it in the module that owns that level.

Do not duplicate persistence, taxonomy, lifecycle, or narrative logic across modules.

Avoid placing new intelligence logic directly into daily_report.py.
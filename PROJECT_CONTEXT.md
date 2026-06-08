Job Signals - Project Context

IMPORTANT:

The purpose of this project is not to build a job board.

The purpose is to build a labor market intelligence asset that identifies hiring, skill, technology, and company signals before they become obvious and eventually monetizes those insights.

Project Purpose

Job Signals is being built as a labor market intelligence engine.

Primary motivation:

* User is pursuing PR in Canada.
* If PR is unsuccessful, user may need to return to India.
* User wants to build a digital asset that can continue generating value regardless of location.
* Focus is on creating something useful, monetizable, and capable of producing market intelligence.

The goal is not merely to scrape jobs.

The goal is to discover hiring, technology, and skill signals before they become obvious.

⸻

Current Status

Version: v0.2

Repository Status:

* Git initialized
* GitHub connected
* First major checkpoint committed

Latest Commit:

* normalize signals in daily report

⸻

Current Architecture

Data Sources

Active Sources:

* Remotive
* RemoteOK

Planned Sources:

* Greenhouse
* Lever
* Ashby
* Company career pages

⸻

Storage

Database:

* SQLite

Primary Database:

* jobs.db

Stores:

* Job postings
* Historical snapshots
* Skill signals
* Category signals
* job_snapshots
* Historical signal snapshots

⸻

Core Features

Job Collection

Implemented:

* Multi-source ingestion
* Snapshot storage
* Historical tracking

⸻

Category Intelligence

Implemented:

* Category classification
* Category momentum
* Emerging category detection

Current Categories:

* AI
* Engineering
* Data / Analytics
* Product
* Sales
* Marketing
* Support
* Operations
* People / HR
* Admin / Executive
* Education
* Production / Labour
* Healthcare

Category quality improved:

* Other reduced from roughly 35% to roughly 7.5%

⸻

Skill Intelligence

Implemented:

* Skill extraction from descriptions
* Skill frequency tracking
* Skill momentum tracking
* Company diversity tracking
* Signal taxonomy normalization
* Cross-skill signal grouping

Tracked Skills Include:

* AI
* LLM
* MCP
* React
* TypeScript
* AWS
* Python
* PostgreSQL
* SQL
* Git
* Salesforce
* HubSpot
* SEO
* Excel

Signal Taxonomy

Implemented:

* signal_taxonomy.py
* Skill normalization
* Signal grouping

Current Signal Groups:

* AI
* AI Infrastructure
* Frontend
* Backend
* Cloud / DevOps
* Data
* CRM / Sales Tools
* Marketing / Growth

Purpose:

Convert raw skills into durable market signals.

Examples:

AI:
* ai
* llm
* machine learning
* langchain

Frontend:
* react
* typescript
* javascript

⸻

Emerging Technology Score

Formula:

score = growth × company_diversity

Purpose:

Distinguish:

* Broad market movement
    from
* Single-company hiring noise

Example:

AI:

* Growth across multiple companies
* High score

MCP:

* Strong growth
* Concentrated in one company
* Lower strategic importance

⸻

Company Intelligence

Implemented:

* Company hiring momentum

Examples observed:

* LawnStarter
* TELUS Digital
* KIPP Foundation
* Dana Incorporated

Purpose:

Identify:

* Expanding companies
* Newly hiring companies
* Stable major hirers

⸻

Reporting

Implemented:

* trends.py
* daily_report.py
* leaderboard.py
* signal_taxonomy.py
* signal_history.py
* category_debug.py
* skill_debug.py

Outputs:

* Category trends
* Skill trends
* Company momentum
* Emerging technology scores
* Historical signals
* Leaderboards
* Daily intelligence reports
* Signal strength rankings
* Normalized signal leaders

⸻

Main Files

scraper.py

* Collects jobs from external sources

trends.py

* Core intelligence engine
* Categories
* Skills
* Momentum
* Technology scoring

leaderboard.py

* Snapshot rankings

signal_taxonomy.py

* Signal normalization
* Signal grouping
* Market signal vocabulary

signal_history.py

* Historical trend tracking

database.py

* Database utilities

category_debug.py

* Category classification debugging

skill_debug.py

* Skill extraction debugging

⸻

Current Insights

Most recent observations:

* AI is currently the strongest broad market signal.
* Frontend remains the highest-volume technical signal.
* AI Infrastructure appears frequently but remains concentrated.
* Salesforce and HubSpot show cross-company presence.
* Company diversity scoring is functioning.
* Category classification improved significantly.
* Other category reduced from roughly 35% to roughly 7.5%.

⸻

Current Priorities

Priority 1:

* Add third data source

Priority 2:

* Improve company trend history

Priority 3:

* Improve narrative intelligence reporting

Priority 4:

* Improve distribution

Priority 5:

* Explore monetization

Next Session Plan

Priority 1: Third Data Source

Candidates:

* Greenhouse
* Lever
* Ashby

Reason:

* Improve signal quality.
* Reduce dependence on job boards.
* Move closer to company hiring signals.

Priority 2: Narrative Intelligence Layer

Goal:

* Explain signal movement.
* Identify meaningful changes.
* Surface emerging themes automatically.

Priority 3: Long-Term Trend Tracking

Goal:

* Track company momentum over time.
* Track signal persistence.
* Improve forecasting capability.

Completed:
- Job identity layer
- Deduplication system
- first_seen tracking
- last_seen tracking
- active/inactive tracking
- Historical snapshot architecture
- Job lifecycle tracking
- Daily intelligence report
- Signal taxonomy
- Normalized signal leaderboard
- Normalized daily report

Current Focus:
- Narrative intelligence layer
- Signal quality improvements
- Third data source integration
- Long-term company trend tracking

⸻

Long-Term Vision

Create a system that can identify:

* Emerging technologies
* Emerging skills
* Hiring momentum
* Company expansion
* Talent demand shifts

before they become obvious.

Ultimate goal:

Transform Job Signals into a valuable intelligence asset that produces useful market signals and can eventually generate revenue.
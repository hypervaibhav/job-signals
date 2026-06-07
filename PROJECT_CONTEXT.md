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

Version: v0

Repository Status:

* Git initialized
* GitHub connected
* First major checkpoint committed

Latest Commit:

* build v0 labor market signal engine

⸻

Current Architecture

Data Sources

Active Sources:

* Remotive
* RemoteOK

Planned Sources:

* Additional job boards
* Additional hiring datasets
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

* Other reduced from roughly 35% to roughly 2.5%

⸻

Skill Intelligence

Implemented:

* Skill extraction from descriptions
* Skill frequency tracking
* Skill momentum tracking
* Company diversity tracking

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
* leaderboard.py
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

* AI is the strongest multi-company signal.
* MCP appears frequently but is concentrated.
* Salesforce is emerging.
* Python is emerging.
* Company momentum tracking works.
* Category system is largely stabilized.

⸻

Current Priorities

Priority 1:

* Add third data source

Priority 2:

* Improve company trend history

Priority 3:

* Build daily intelligence report

Priority 4:

* Improve distribution

Priority 5:

* Explore monetization

Next Session Plan

Priority 1: Job Deduplication

Problem:

* Same jobs can appear in multiple snapshots.
* Historical analysis can become distorted.
* Future trend calculations may overcount demand.

Goal:

* Identify jobs using source + external id when available.
* Fall back to source + title + company.
* Prevent duplicate storage.
* Track first_seen and last_seen timestamps.

Priority 2: New vs Existing Job Detection

Goal:

* Detect newly appeared jobs.
* Detect jobs that disappeared.
* Calculate net hiring change.

Expected Output:

* New jobs today
* Removed jobs today
* Net job change

Priority 3: Third Data Source

Candidates:

* Greenhouse
* Lever
* Ashby
* Wellfound

Reason:

* Improve signal quality and reduce dependence on Remotive/RemoteOK.


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
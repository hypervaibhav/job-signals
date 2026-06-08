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

Version: v0.4

Repository Status:

* Git initialized
* GitHub connected
* First major checkpoint committed

Latest Commit:

* add lever source and snapshot context memory
* add signal acceleration analysis
* add normalized opportunity ranking
* add category conviction scoring
* add signal opportunity intelligence layer

⸻

Current Architecture

Data Sources

Active Sources:

* Remotive
* RemoteOK
* Greenhouse
* Lever

Planned Sources:

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
* snapshot_metadata
* skill signal history
* Job lifecycle history

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
* snapshot context memory
* signal acceleration analysis
* opportunity ranking
* conviction scoring
* signal opportunity summaries
* normalized opportunity scoring

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
* Signal acceleration rankings
* Opportunity rankings
* Conviction-ranked signals
* Signal opportunity analysis
* Market opportunity summaries

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

* AI remains the strongest broad-market signal.
* Lever integration significantly expanded market coverage and improved signal diversity.
* AI demand is spread across 15 companies.
* Engineering is the strongest category by volume.
* Source-aware confidence scoring is functioning.
* Snapshot context memory can distinguish signal growth from source expansion.
* Category classification quality continues to improve.
* Other category reduced substantially from early project levels.
* Signal acceleration now identifies momentum rather than only signal size.
* Backend, Data, AI, and Cloud / DevOps currently show the strongest acceleration.
* Tiny-sample acceleration noise is filtered out.
* Source-expansion events are considered when evaluating signal momentum.
* Signal growth can now be distinguished from source-expansion artifacts.
* Opportunity scoring now combines signal size, company diversity, conviction, and momentum.
* AI currently ranks as the strongest market opportunity signal.
* Frontend, Cloud / DevOps, Backend, and Data remain secondary opportunity clusters.
* Conviction scoring helps distinguish broad market demand from isolated hiring noise.
* Category conviction now incorporates company diversity rather than raw posting count alone.

⸻

Current Priorities

Priority 1:

* Signal conviction scoring
* Distinguish broad market demand from concentrated demand
* Improve confidence in emerging signals

Priority 2:

* Company trend intelligence
* Hiring persistence tracking
* Company watchlists

Priority 3:

* Geographic intelligence
* Regional hiring trends
* Location-based signal analysis

Priority 4:

* Ashby integration
* Additional ATS coverage

Priority 5:

* Distribution and monetization

⸻

Completed

* Job identity layer
* Deduplication system
* first_seen tracking
* last_seen tracking
* active/inactive tracking
* Historical snapshot architecture
* Job lifecycle tracking
* Daily intelligence report
* Signal taxonomy
* Normalized signal leaderboard
* Normalized daily report
* Greenhouse integration
* Lever integration
* Source mix reporting
* Confidence scoring
* Snapshot context memory
* Signal memory
* Signal acceleration
* Source expansion detection
* Source-aware baseline filtering
* Opportunity ranking system
* Normalized opportunity scoring (0-100)
* Category conviction scoring
* Signal opportunity intelligence layer
* Company diversity weighted rankings

⸻

Current Focus

* Signal quality improvements
* Narrative intelligence layer
* Company trend intelligence
* Opportunity score refinement
* Company watchlists
* Signal persistence tracking
* Ashby integration
* Forecasting and trend persistence

⸻

Next Session Plan

Priority 1: Company Watchlists

Goals:

* Track strategic companies over time
* Detect hiring persistence
* Monitor AI hiring concentration
* Identify repeat hiring leaders

Priority 2: Geographic Intelligence

Goals:

* Extract location trends
* Compare regional demand patterns
* Build geographic signal layers

Priority 3: Trend Persistence

Goals:

* Measure how long signals remain strong
* Detect temporary spikes versus durable trends
* Improve forecasting quality

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
import sqlite3
from collections import Counter
from datetime import datetime

from trends import (
    classify_role,
    extract_skills,
)

from signal_taxonomy import is_ai_related, normalize_signal

from company_intelligence import (
    detect_hiring_archetype,
    generate_company_trend_confidence_narrative,
    generate_company_trend_narrative,
    generate_narrative as generate_company_narrative,
    classify_role as company_classify_role,
    extract_skills as company_extract_skills,
)

from market_intelligence import build_market_intelligence
from strategic_theme_confidence import classify_theme_confidence
from strategic_theme_history import (
    get_latest_theme_snapshot,
    get_theme_history,
    save_theme_snapshot,
)
from strategic_theme_lifecycle import (
    classify_theme_lifecycle,
    has_presentable_theme_activity,
)
from strategic_themes import calculate_theme_snapshot, detect_strategic_themes
from company_history import (
    classify_company_trend,
    classify_company_trend_confidence,
    get_company_histories,
    get_company_history,
)

DB_NAME = "jobs.db"

CURRENT_LATEST_JOBS = 0
CURRENT_PREVIOUS_JOBS = 0
CURRENT_LATEST_SOURCE_MIX = {}
CURRENT_PREVIOUS_SOURCE_MIX = {}

WATCHLIST_COMPANIES = [
    "Mistral",
    "Datadog",
    "Stripe",
    "Reddit",
    "Discord",
    "Spotify",
    "Levelai",
    "Ryzlabs",
    "Integrate",
]


def get_latest_two_snapshots():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT snapshot_time
        FROM job_snapshots
        ORDER BY snapshot_time DESC
        LIMIT 2
    """)
    times = [row[0] for row in c.fetchall()]

    if len(times) < 2:
        conn.close()
        return None, None, [], []

    latest_time, previous_time = times[0], times[1]

    c.execute("""
        SELECT title, company, snapshot_time, description, source
        FROM job_snapshots
        WHERE snapshot_time = ?
    """, (latest_time,))
    latest = c.fetchall()

    c.execute("""
        SELECT title, company, snapshot_time, description, source
        FROM job_snapshots
        WHERE snapshot_time = ?
    """, (previous_time,))
    previous = c.fetchall()

    conn.close()
    return latest_time, previous_time, latest, previous


def fmt_time(ts):
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %I:%M %p")


# Helper: normalized skill counts
def calculate_normalized_skill_counts(rows):
    skill_counts = Counter()

    for row in rows:
        title = row[0]
        description = row[3] or ""

        for skill in extract_skills(title, description):
            signal = normalize_signal(skill)
            skill_counts[signal] += 1

    return skill_counts


# Helper: normalized skill companies

def calculate_normalized_skill_companies(rows):
    signal_companies = {}

    for row in rows:
        title = row[0]
        company = row[1]
        description = row[3] or ""

        for skill in extract_skills(title, description):
            signal = normalize_signal(skill)
            signal_companies.setdefault(signal, set()).add(company)

    return signal_companies

def calculate_source_mix(rows):
    return Counter(row[4] if len(row) > 4 else "unknown" for row in rows)

def calculate_conviction(count, company_count):
    if count >= 10 and company_count >= 5:
        return "HIGH"

    if count >= 5 and company_count >= 2:
        return "MEDIUM"

    return "LOW"

# --- OPPORTUNITY SCORE ---
def calculate_opportunity_score(
    count,
    companies,
    diff,
    conviction,
    max_count,
    max_companies,
    max_positive_diff,
):
    strength_score = (count / max_count) * 40 if max_count else 0
    diversity_score = (companies / max_companies) * 25 if max_companies else 0

    conviction_score = {
        "HIGH": 25,
        "MEDIUM": 10,
        "LOW": 0,
    }.get(conviction, 0)

    movement_score = 0
    if diff > 0 and max_positive_diff > 0:
        movement_score = (diff / max_positive_diff) * 10

    total = strength_score + diversity_score + conviction_score + movement_score
    return round(min(total, 100))

def get_signal_examples(rows, target_signal, limit=3):
    companies = Counter()
    roles = Counter()

    for row in rows:
        title = row[0]
        company = row[1]
        description = row[3] or ""

        normalized_signals = {
            normalize_signal(skill)
            for skill in extract_skills(title, description)
        }

        if target_signal in normalized_signals:
            companies[company] += 1
            roles[title] += 1

    return companies.most_common(limit), roles.most_common(limit)


def calculate_company_watchlist(rows):
    watchlist = {}

    for company_name in WATCHLIST_COMPANIES:
        company_rows = [row for row in rows if row[1] == company_name]

        if not company_rows:
            continue

        ai_postings = 0

        for row in company_rows:
            title = row[0]
            description = row[3] or ""

            if is_ai_related(extract_skills(title, description)):
                ai_postings += 1

        total_postings = len(company_rows)
        ai_concentration = (
            (ai_postings / total_postings) * 100
            if total_postings
            else 0
        )

        watchlist[company_name] = {
            "total_postings": total_postings,
            "ai_postings": ai_postings,
            "ai_concentration": ai_concentration,
        }

    return watchlist


def print_company_watchlist(rows):
    print("\n--- COMPANY WATCHLIST ---\n")

    watchlist = calculate_company_watchlist(rows)

    if not watchlist:
        print("No watchlist companies found in latest snapshot.")
        return

    ranked_companies = sorted(
        watchlist.items(),
        key=lambda item: (item[1]["ai_concentration"], item[1]["total_postings"]),
        reverse=True,
    )

    for company, stats in ranked_companies:
        print(company)
        print(f"Postings: {stats['total_postings']}")
        print(f"AI-related postings: {stats['ai_postings']}")
        print(f"AI concentration: {stats['ai_concentration']:.1f}%")
        print("")

    high_ai_companies = [
        company
        for company, stats in ranked_companies
        if stats["ai_concentration"] >= 50 and stats["ai_postings"] >= 3
    ]

    if high_ai_companies:
        print(
            "Watchlist observation: "
            + ", ".join(high_ai_companies[:3])
            + " show strong AI hiring concentration."
        )
    else:
        print(
            "Watchlist observation: no watchlist company shows strong AI hiring concentration yet."
        )


# --- COMPANY INTELLIGENCE HIGHLIGHTS ---

def calculate_company_intelligence_rows(rows):
    watchlist = calculate_company_watchlist(rows)

    if not watchlist:
        return []

    ranked_companies = sorted(
        watchlist.items(),
        key=lambda item: (
            item[1]["ai_concentration"],
            item[1]["total_postings"],
        ),
        reverse=True,
    )

    intelligence_rows = []

    for company_name, stats in ranked_companies:
        company_rows = [row for row in rows if row[1] == company_name]

        category_counts = Counter(
            company_classify_role(row[0])
            for row in company_rows
        )

        skill_counts = Counter()

        for row in company_rows:
            title = row[0]
            description = row[3] or ""

            for skill in company_extract_skills(title, description):
                skill_counts[skill] += 1

        representative_roles = []
        seen_roles = set()

        for row in company_rows:
            role = row[0]
            normalized_role = role.lower().strip()

            if normalized_role not in seen_roles:
                representative_roles.append(role)
                seen_roles.add(normalized_role)

            if len(representative_roles) == 5:
                break

        archetype = detect_hiring_archetype(
            category_counts,
            skill_counts,
            representative_roles,
            len(company_rows),
            ai_related_count=stats["ai_postings"],
        )

        top_category = (
            category_counts.most_common(1)[0][0]
            if category_counts
            else "Unknown"
        )
        top_skills = skill_counts.most_common(5)

        history = get_company_history(company_name)

        if history:
            persistence = history["snapshots_active"]
            momentum = history["current_postings"] - history["first_postings"]
            observation_window_days = history["observation_window_days"]
            try:
                trend = classify_company_trend(history)
                trend_narrative = generate_company_trend_narrative(trend, history)
            except KeyError:
                trend = None
                trend_narrative = None
            try:
                trend_confidence = classify_company_trend_confidence(history)
                trend_confidence_narrative = (
                    generate_company_trend_confidence_narrative(
                        trend_confidence,
                        history,
                    )
                )
            except KeyError:
                trend_confidence = None
                trend_confidence_narrative = None
        else:
            persistence = 1
            momentum = 0
            observation_window_days = None
            trend = None
            trend_narrative = None
            trend_confidence = None
            trend_confidence_narrative = None

        if stats["total_postings"] >= 10 and persistence >= 3:
            conviction = "High"
        elif stats["total_postings"] >= 5 and persistence >= 2:
            conviction = "Medium"
        else:
            conviction = "Early"

        narrative = generate_company_narrative(
            company_name,
            momentum,
            conviction,
            stats["ai_concentration"],
            top_category,
            top_skills,
            archetype,
            observation_window_days=observation_window_days,
        )


        intelligence_rows.append(
            {
                "company": company_name,
                "intelligence": archetype,
                "ai_concentration": stats["ai_concentration"],
                "total_postings": stats["total_postings"],
                "persistence": persistence,
                "observation_window_days": observation_window_days,
                "trend": trend,
                "trend_narrative": trend_narrative,
                "trend_confidence": trend_confidence,
                "trend_confidence_narrative": trend_confidence_narrative,
                "conviction": conviction,
                "narrative": narrative,
            }
        )

    return intelligence_rows


def persist_strategic_theme_snapshot(
    conn,
    snapshot_time,
    company_intelligence_rows,
):
    themes = calculate_theme_snapshot(company_intelligence_rows)
    save_theme_snapshot(
        conn,
        snapshot_time,
        themes,
        eligible_company_count=len(company_intelligence_rows),
    )


def build_strategic_theme_market_rows(conn):
    theme_rows = []

    for latest_theme in get_latest_theme_snapshot(conn):
        history = get_theme_history(conn, latest_theme["theme"])

        if not has_presentable_theme_activity(history):
            continue

        lifecycle = classify_theme_lifecycle(history)
        confidence = classify_theme_confidence(history, lifecycle)

        theme_rows.append(
            {
                "theme": latest_theme["theme"],
                "lifecycle": lifecycle,
                "confidence": confidence,
                "current_company_count": (
                    history["current_company_count"] if history else 0
                ),
                "peak_company_count": (
                    history["peak_company_count"] if history else 0
                ),
                "snapshots_active": (
                    history["snapshots_active"] if history else 0
                ),
                "total_eligible_snapshots": (
                    history["total_eligible_snapshots"] if history else 0
                ),
                "persistence_score": (
                    history["persistence_score"] if history else 0
                ),
                "current_members": (
                    history["current_companies"] if history else []
                ),
            }
        )

    theme_rows.sort(
        key=lambda row: (
            -row["current_company_count"],
            row["theme"],
        )
    )
    return theme_rows


def build_signal_market_rows(skill_changes):
    max_count = max((row[1] for row in skill_changes), default=0)
    max_companies = max((row[3] for row in skill_changes), default=0)
    max_positive_diff = max(
        (row[2] for row in skill_changes if row[2] > 0),
        default=0,
    )

    return [
        {
            "signal": signal,
            "postings": count,
            "change": diff,
            "companies": companies,
            "signal_strength": score,
            "conviction": conviction,
            "opportunity_score": calculate_opportunity_score(
                count,
                companies,
                diff,
                conviction,
                max_count,
                max_companies,
                max_positive_diff,
            ),
        }
        for signal, count, diff, companies, score, conviction in skill_changes
    ]


def build_category_market_rows(category_changes):
    return [
        {
            "category": category,
            "current_roles": count,
            "change": diff,
        }
        for category, count, diff in category_changes
    ]


def build_company_market_rows(company_changes):
    return [
        {
            "company": company,
            "current_postings": count,
            "change": diff,
        }
        for company, count, diff in company_changes
    ]


def build_market_intelligence_report_data(
    conn,
    latest_job_count,
    previous_job_count,
    net_change,
    latest_source_mix,
    previous_source_mix,
    skill_changes,
    category_changes,
    company_changes,
    company_intelligence_rows,
):
    evidence_confidence, evidence_confidence_reason = calculate_report_confidence(
        net_change,
        latest_job_count,
        previous_job_count,
        latest_source_mix,
        previous_source_mix,
    )

    return build_market_intelligence(
        latest_job_count=latest_job_count,
        previous_job_count=previous_job_count,
        net_change=net_change,
        evidence_confidence=evidence_confidence,
        evidence_confidence_reason=evidence_confidence_reason,
        signal_rows=build_signal_market_rows(skill_changes),
        category_changes=build_category_market_rows(category_changes),
        company_changes=build_company_market_rows(company_changes),
        company_intelligence_rows=company_intelligence_rows,
        strategic_theme_rows=build_strategic_theme_market_rows(conn),
    )


def print_market_intelligence(market_intelligence):
    print("\n--- MARKET INTELLIGENCE ---\n")
    print(f"Market direction: {market_intelligence['market_direction']}")
    print(
        "Evidence confidence: "
        f"{market_intelligence['evidence_confidence']['level']}"
    )

    top_signal = market_intelligence["top_signal"]
    if top_signal:
        print(f"Top signal: {top_signal['signal']}")
    else:
        print("Top signal: none")

    strategy_mix = market_intelligence["company_strategy_mix"]
    if strategy_mix:
        print("Company strategy mix:")
        for strategy, count in strategy_mix.items():
            print(f"- {strategy}: {count}")
    else:
        print("Company strategy mix: none")

    print("Strategic themes:")
    if market_intelligence["strategic_themes"]:
        for theme in market_intelligence["strategic_themes"]:
            company_label = (
                "company"
                if theme["current_company_count"] == 1
                else "companies"
            )
            print(
                f"- {theme['theme']}: {theme['lifecycle']}, "
                f"{theme['confidence']} confidence, "
                f"{theme['current_company_count']} {company_label}"
            )
    else:
        print("- none")

    print(f"Market read: {market_intelligence['market_read']}")

    if market_intelligence["caveats"]:
        print("Caveats:")
        for caveat in market_intelligence["caveats"]:
            print(f"- {caveat}")


def print_strategic_themes(company_intelligence_rows, limit=5):
    print("\n--- STRATEGIC THEMES ---\n")

    themes = detect_strategic_themes(company_intelligence_rows)

    if not themes:
        print("No broad strategic themes detected yet.")
        return

    for theme in themes[:limit]:
        print(theme["theme"])
        print(f"Strength: {theme['strength']}")
        print(f"Companies: {theme['company_count']}")
        print("Representative companies:")
        for company in theme["companies"][:5]:
            print(f"- {company}")
        print(f"Interpretation: {theme['narrative']}")
        print("")


def print_company_intelligence_highlights(company_intelligence_rows, limit=3):
    print("\n--- COMPANY INTELLIGENCE HIGHLIGHTS ---\n")

    if not company_intelligence_rows:
        print("No company intelligence available.")
        return

    for row in company_intelligence_rows[:limit]:
        print(row["company"])
        print(f"Archetype: {row['intelligence']}")
        print(f"AI concentration: {row['ai_concentration']:.1f}%")
        print(f"Postings: {row['total_postings']}")
        snapshot_label = "snapshot" if row["persistence"] == 1 else "snapshots"
        print(f"Persistence: {row['persistence']} {snapshot_label}")
        if row["observation_window_days"] is not None:
            print(f"Observed for: {row['observation_window_days']:.1f} days")
        if row["trend"] is not None:
            print(f"Hiring trend: {row['trend']}")
        if row.get("trend_narrative") is not None:
            print(f"Trend explanation: {row['trend_narrative']}")
        if row["trend_confidence"] is not None:
            print(f"Trend confidence: {row['trend_confidence']}")
        if row.get("trend_confidence_narrative") is not None:
            print(
                "Confidence explanation: "
                f"{row['trend_confidence_narrative']}"
            )
        print(f"Conviction: {row['conviction']}")
        print(f"Narrative: {row['narrative']}")
        print("")


def print_company_memory(limit=5):
    print("\n--- COMPANY MEMORY ---\n")

    histories = get_company_histories()

    if not histories:
        print("No company history available yet.")
        return

    meaningful_histories = [
        history for history in histories
        if history["current_postings"] >= 3
    ]

    if not meaningful_histories:
        print("No meaningful company memory available yet.")
        return

    for history in meaningful_histories[:limit]:
        snapshot_label = (
            "snapshot"
            if history["snapshots_active"] == 1
            else "snapshots"
        )

        print(history["company"])
        print(
            f"Persistence: {history['snapshots_active']}/"
            f"{history['total_snapshots']} {snapshot_label}"
        )
        print(f"Current postings: {history['current_postings']}")
        print(f"Peak postings: {history['peak_postings']}")
        print(f"First seen: {history['first_seen_formatted']}")
        print(f"Latest seen: {history['latest_seen_formatted']}")
        print("")

def print_opportunity_ranking(skill_changes, limit=10):
    print("\n--- OPPORTUNITY RANKING ---\n")

    ranked = []
    max_count = max((row[1] for row in skill_changes), default=0)
    max_companies = max((row[3] for row in skill_changes), default=0)
    max_positive_diff = max((row[2] for row in skill_changes if row[2] > 0), default=0)

    for signal, count, diff, companies, score, conviction in skill_changes:
        opportunity_score = calculate_opportunity_score(
            count,
            companies,
            diff,
            conviction,
            max_count,
            max_companies,
            max_positive_diff,
        )

        ranked.append(
            (
                signal,
                opportunity_score,
                conviction,
                count,
                companies,
            )
        )

    ranked.sort(key=lambda row: row[1], reverse=True)

    for rank, (signal, opportunity_score, conviction, count, companies) in enumerate(ranked[:limit], start=1):
        print(
            f"{rank}. {signal}: opportunity score {opportunity_score}/100 | "
            f"{conviction} conviction | {count} postings | {companies} companies"
        )

def print_signal_opportunities(latest_rows, skill_changes, limit=3):
    print("\n--- SIGNAL OPPORTUNITIES ---\n")

    opportunity_rows = [
        row for row in skill_changes
        if row[5] in {"HIGH", "MEDIUM"}
    ]

    opportunity_rows.sort(key=lambda row: (row[5] == "HIGH", row[4]), reverse=True)

    if not opportunity_rows:
        print("No strong signal opportunities detected yet.")
        return

    for signal, count, diff, companies, score, conviction in opportunity_rows[:limit]:
        representative_companies, representative_roles = get_signal_examples(
            latest_rows,
            signal,
        )

        print(f"{signal}")
        print(f"Conviction: {conviction}")
        print(f"Postings: {count}")
        print(f"Companies: {companies}")
        print(f"Signal strength: {score}")

        if representative_companies:
            print("Representative companies:")
            for company, _ in representative_companies:
                print(f"- {company}")

        if representative_roles:
            print("Representative roles:")
            for role, _ in representative_roles:
                print(f"- {role}")

        if conviction == "HIGH":
            print(
                "Why it matters: this signal is broad enough across companies "
                "to be treated as a meaningful market opportunity."
            )
        else:
            print(
                "Why it matters: this signal is visible, but still needs more "
                "breadth before it should be treated as a core market trend."
            )

        print("")

def calculate_report_confidence(
    net_change,
    latest_jobs,
    previous_jobs,
    latest_source_mix,
    previous_source_mix,
):
    if previous_jobs == 0:
        return "LOW", "Insufficient history"

    growth_ratio = abs(net_change) / max(previous_jobs, 1)

    max_source_shift = 0

    all_sources = set(latest_source_mix) | set(previous_source_mix)

    for source in all_sources:
        latest_pct = latest_source_mix.get(source, 0) / max(latest_jobs, 1)
        previous_pct = previous_source_mix.get(source, 0) / max(previous_jobs, 1)
        max_source_shift = max(max_source_shift, abs(latest_pct - previous_pct))

    if max_source_shift > 0.25:
        return (
            "LOW",
            "Source mix changed significantly. Results may be distorted by source expansion or source imbalance.",
        )

    if growth_ratio > 0.25:
        return (
            "LOW",
            "Large snapshot change detected. Results may be influenced by source expansion or sampling effects.",
        )

    if growth_ratio > 0.10 or max_source_shift > 0.10:
        return (
            "MEDIUM",
            "Moderate snapshot or source-mix change detected. Interpret directional signals carefully.",
        )

    return (
        "HIGH",
        "Snapshot size and source mix are stable. Signal comparisons are more reliable.",
    )

# --- MARKET NARRATIVE ---
def print_market_narrative(net_change, category_changes, company_changes, skill_changes):
    print("\n--- MARKET NARRATIVE ---\n")

    confidence, reason = calculate_report_confidence(
        net_change,
        CURRENT_LATEST_JOBS,
        CURRENT_PREVIOUS_JOBS,
        CURRENT_LATEST_SOURCE_MIX,
        CURRENT_PREVIOUS_SOURCE_MIX,
    )

    print(f"Confidence: {confidence}")
    print(f"Reason: {reason}\n")

    if net_change > 0:
        print(f"Market direction: expanding (+{net_change} net jobs).")
    elif net_change < 0:
        print(f"Market direction: contracting ({net_change} net jobs).")
    else:
        print("Market direction: flat between the latest two snapshots.")

    strongest_signals = [row for row in skill_changes if row[1] > 0]
    strongest_signals.sort(key=lambda row: row[4], reverse=True)

    if strongest_signals:
        signal, count, diff, companies, score, conviction = strongest_signals[0]
        print(
            f"{signal} remains the strongest {conviction}-conviction signal, "
            f"appearing in {count} postings across {companies} companies "
            f"(strength {score})."
        )

    growing_categories = [row for row in category_changes if row[2] > 0]
    growing_categories.sort(key=lambda row: row[2], reverse=True)

    if growing_categories:
        category, count, diff = growing_categories[0]
        print(f"Fastest category movement: {category} increased by {diff} roles.")
    else:
        print("Category movement: no meaningful category increase detected.")

    growing_companies = [row for row in company_changes if row[2] > 0]
    growing_companies.sort(key=lambda row: row[2], reverse=True)

    if growing_companies:
        company, count, diff = growing_companies[0]
        print(
            f"Company momentum leader: {company} increased by {diff} postings."
        )
    else:
        print("Company movement: no company showed clear positive movement.")

    broad_signals = [row for row in strongest_signals if row[3] >= 3]

    if broad_signals:
        signal, count, diff, companies, score, conviction = broad_signals[0]
        print(
            f"Broad demand note: {signal} has {conviction} conviction and is spread "
            f"across {companies} companies, which is generally more meaningful "
            "than demand concentrated in a single employer."
        )


def print_daily_report():
    latest_time, previous_time, latest, previous = get_latest_two_snapshots()

    if not latest or not previous:
        print("Need at least 2 snapshots to generate report.")
        return

    latest_categories = Counter(classify_role(row[0]) for row in latest)
    previous_categories = Counter(classify_role(row[0]) for row in previous)

    latest_companies = Counter(row[1] for row in latest)
    previous_companies = Counter(row[1] for row in previous)

    latest_skills = calculate_normalized_skill_counts(latest)
    previous_skills = calculate_normalized_skill_counts(previous)

    latest_skill_companies = calculate_normalized_skill_companies(latest)

    latest_source_mix = calculate_source_mix(latest)
    previous_source_mix = calculate_source_mix(previous)

    global CURRENT_LATEST_JOBS
    global CURRENT_PREVIOUS_JOBS
    global CURRENT_LATEST_SOURCE_MIX
    global CURRENT_PREVIOUS_SOURCE_MIX

    CURRENT_LATEST_JOBS = len(latest)
    CURRENT_PREVIOUS_JOBS = len(previous)
    CURRENT_LATEST_SOURCE_MIX = latest_source_mix
    CURRENT_PREVIOUS_SOURCE_MIX = previous_source_mix

    print("\n==============================")
    print("JOB SIGNALS DAILY REPORT")
    print("==============================\n")

    print(f"Latest snapshot:   {fmt_time(latest_time)}")
    print(f"Previous snapshot: {fmt_time(previous_time)}")

    print("\n--- MARKET DIRECTION ---\n")
    net_change = len(latest) - len(previous)
    print(f"Latest jobs: {len(latest)}")
    print(f"Previous jobs: {len(previous)}")
    print(f"Net job change: {net_change:+}")

    print("\n--- SOURCE MIX ---\n")
    total_latest_sources = sum(latest_source_mix.values())

    for source, count in latest_source_mix.most_common():
        percentage = (count / total_latest_sources) * 100 if total_latest_sources else 0
        previous_count = previous_source_mix.get(source, 0)
        diff = count - previous_count
        print(f"{source}: {count} jobs ({percentage:.1f}%) ({diff:+})")

    print("\n--- CATEGORY MOVEMENT ---\n")
    all_categories = set(latest_categories) | set(previous_categories)

    category_changes = []
    for category in all_categories:
        diff = latest_categories[category] - previous_categories[category]
        category_changes.append((category, latest_categories[category], diff))

    category_changes.sort(key=lambda x: x[2], reverse=True)

    for category, count, diff in category_changes[:8]:
        print(f"{category}: {count} roles ({diff:+})")

    print("\n--- COMPANY MOMENTUM ---\n")
    all_companies = set(latest_companies) | set(previous_companies)

    company_changes = []
    for company in all_companies:
        diff = latest_companies[company] - previous_companies[company]
        company_changes.append((company, latest_companies[company], diff))

    company_changes.sort(key=lambda x: x[2], reverse=True)

    for company, count, diff in company_changes[:10]:
        print(f"{company}: {count} postings ({diff:+})")

    print("\n--- SIGNAL LEADERS ---\n")
    all_skills = set(latest_skills) | set(previous_skills)

    skill_changes = []
    for skill in all_skills:
        diff = latest_skills[skill] - previous_skills[skill]
        companies = len(latest_skill_companies.get(skill, set()))
        score = latest_skills[skill] * companies
        conviction = calculate_conviction(latest_skills[skill], companies)
        skill_changes.append(
            (skill, latest_skills[skill], diff, companies, score, conviction)
        )

    skill_changes.sort(key=lambda x: x[4], reverse=True)

    for skill, count, diff, companies, score, conviction in skill_changes[:10]:
        print(
            f"{skill}: {count} postings ({diff:+}), "
            f"{companies} companies, signal strength {score}, "
            f"{conviction} conviction"
        )

    print_market_narrative(net_change, category_changes, company_changes, skill_changes)
    print_opportunity_ranking(skill_changes)

    company_intelligence_rows = calculate_company_intelligence_rows(latest)
    conn = sqlite3.connect(DB_NAME)
    try:
        persist_strategic_theme_snapshot(
            conn,
            latest_time,
            company_intelligence_rows,
        )
        market_intelligence = build_market_intelligence_report_data(
            conn,
            latest_job_count=len(latest),
            previous_job_count=len(previous),
            net_change=net_change,
            latest_source_mix=latest_source_mix,
            previous_source_mix=previous_source_mix,
            skill_changes=skill_changes,
            category_changes=category_changes,
            company_changes=company_changes,
            company_intelligence_rows=company_intelligence_rows,
        )
    finally:
        conn.close()

    print_signal_opportunities(latest, skill_changes)
    print_company_watchlist(latest)
    print_company_memory()
    print_strategic_themes(company_intelligence_rows)
    print_market_intelligence(market_intelligence)
    print_company_intelligence_highlights(company_intelligence_rows)

    print("\n--- QUICK READ ---\n")

    growing_categories = [x for x in category_changes if x[2] > 0]
    growing_skills = [x for x in skill_changes if x[2] > 0]
    growing_companies = [x for x in company_changes if x[2] > 0]

    if growing_categories:
        print(f"Top category movement: {growing_categories[0][0]} ({growing_categories[0][2]:+})")
    else:
        print("Top category movement: none detected")

    if growing_skills:
        print(f"Top signal movement: {growing_skills[0][0]} ({growing_skills[0][2]:+})")
    else:
        print("Top signal movement: none detected")

    if growing_companies:
        print(f"Top company movement: {growing_companies[0][0]} ({growing_companies[0][2]:+})")
    else:
        print("Top company movement: none detected")

    print("\n==============================\n")


if __name__ == "__main__":
    print_daily_report()

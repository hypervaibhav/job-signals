def initialize_strategic_theme_history(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategic_theme_snapshots (
            snapshot_time INTEGER NOT NULL,
            scope TEXT NOT NULL,
            engine_version TEXT NOT NULL,
            theme TEXT NOT NULL,
            company_count INTEGER NOT NULL,
            eligible_company_count INTEGER NOT NULL,
            PRIMARY KEY (snapshot_time, scope, engine_version, theme)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategic_theme_companies (
            snapshot_time INTEGER NOT NULL,
            scope TEXT NOT NULL,
            engine_version TEXT NOT NULL,
            theme TEXT NOT NULL,
            company TEXT NOT NULL,
            PRIMARY KEY (snapshot_time, scope, engine_version, theme, company)
        )
        """
    )
    conn.commit()


def save_theme_snapshot(
    conn,
    snapshot_time,
    themes,
    eligible_company_count,
    scope="watchlist",
    engine_version="v2",
):
    with conn:
        conn.execute(
            """
            DELETE FROM strategic_theme_companies
            WHERE snapshot_time = ?
              AND scope = ?
              AND engine_version = ?
            """,
            (snapshot_time, scope, engine_version),
        )
        conn.execute(
            """
            DELETE FROM strategic_theme_snapshots
            WHERE snapshot_time = ?
              AND scope = ?
              AND engine_version = ?
            """,
            (snapshot_time, scope, engine_version),
        )

        for theme in themes:
            theme_name = theme["theme"]
            companies = sorted(set(theme["companies"]))

            conn.execute(
                """
                INSERT INTO strategic_theme_snapshots (
                    snapshot_time,
                    scope,
                    engine_version,
                    theme,
                    company_count,
                    eligible_company_count
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_time,
                    scope,
                    engine_version,
                    theme_name,
                    theme["company_count"],
                    eligible_company_count,
                ),
            )
            conn.executemany(
                """
                INSERT INTO strategic_theme_companies (
                    snapshot_time,
                    scope,
                    engine_version,
                    theme,
                    company
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        snapshot_time,
                        scope,
                        engine_version,
                        theme_name,
                        company,
                    )
                    for company in companies
                ],
            )


def _get_companies(conn, snapshot_time, scope, engine_version, theme):
    rows = conn.execute(
        """
        SELECT company
        FROM strategic_theme_companies
        WHERE snapshot_time = ?
          AND scope = ?
          AND engine_version = ?
          AND theme = ?
        ORDER BY company ASC
        """,
        (snapshot_time, scope, engine_version, theme),
    ).fetchall()
    return [row[0] for row in rows]


def get_latest_theme_snapshot(conn, scope="watchlist", engine_version="v2"):
    latest_snapshot = conn.execute(
        """
        SELECT MAX(snapshot_time)
        FROM strategic_theme_snapshots
        WHERE scope = ?
          AND engine_version = ?
        """,
        (scope, engine_version),
    ).fetchone()[0]

    if latest_snapshot is None:
        return []

    rows = conn.execute(
        """
        SELECT theme, company_count, eligible_company_count
        FROM strategic_theme_snapshots
        WHERE snapshot_time = ?
          AND scope = ?
          AND engine_version = ?
        ORDER BY theme ASC
        """,
        (latest_snapshot, scope, engine_version),
    ).fetchall()

    return [
        {
            "snapshot_time": latest_snapshot,
            "scope": scope,
            "engine_version": engine_version,
            "theme": theme,
            "company_count": company_count,
            "eligible_company_count": eligible_company_count,
            "companies": _get_companies(
                conn,
                latest_snapshot,
                scope,
                engine_version,
                theme,
            ),
        }
        for theme, company_count, eligible_company_count in rows
    ]


def get_theme_history(
    conn,
    theme,
    scope="watchlist",
    engine_version="v2",
):
    rows = conn.execute(
        """
        SELECT snapshot_time, company_count, eligible_company_count
        FROM strategic_theme_snapshots
        WHERE scope = ?
          AND engine_version = ?
          AND theme = ?
        ORDER BY snapshot_time ASC
        """,
        (scope, engine_version, theme),
    ).fetchall()

    if not rows:
        return None

    snapshots = [
        {
            "snapshot_time": snapshot_time,
            "company_count": company_count,
            "eligible_company_count": eligible_company_count,
            "companies": _get_companies(
                conn,
                snapshot_time,
                scope,
                engine_version,
                theme,
            ),
        }
        for snapshot_time, company_count, eligible_company_count in rows
    ]
    active_snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot["company_count"] > 0
    ]
    total_eligible_snapshots = sum(
        snapshot["eligible_company_count"] > 0
        for snapshot in snapshots
    )
    persistence_score = (
        len(active_snapshots) / total_eligible_snapshots
        if total_eligible_snapshots
        else 0
    )
    latest_snapshot = snapshots[-1]

    return {
        "theme": theme,
        "scope": scope,
        "engine_version": engine_version,
        "first_detected": (
            active_snapshots[0]["snapshot_time"]
            if active_snapshots
            else None
        ),
        "latest_detected": (
            active_snapshots[-1]["snapshot_time"]
            if active_snapshots
            else None
        ),
        "snapshots_active": len(active_snapshots),
        "total_eligible_snapshots": total_eligible_snapshots,
        "persistence_score": persistence_score,
        "latest_snapshot_time": latest_snapshot["snapshot_time"],
        "current_company_count": latest_snapshot["company_count"],
        "peak_company_count": max(
            snapshot["company_count"] for snapshot in snapshots
        ),
        "current_companies": latest_snapshot["companies"],
        "snapshots": snapshots,
    }

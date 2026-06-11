from daily_report import calculate_company_intelligence_rows
from strategic_theme_history import save_theme_snapshot
from strategic_themes import calculate_theme_snapshot


def _get_snapshot_times(conn):
    rows = conn.execute(
        """
        SELECT DISTINCT snapshot_time
        FROM job_snapshots
        ORDER BY snapshot_time ASC
        """
    ).fetchall()
    return [row[0] for row in rows]


def _get_snapshot_rows(conn, snapshot_time):
    return conn.execute(
        """
        SELECT title, company, snapshot_time, description, source
        FROM job_snapshots
        WHERE snapshot_time = ?
        """,
        (snapshot_time,),
    ).fetchall()


def backfill_strategic_theme_history(
    conn,
    scope="watchlist",
    engine_version="v2-backfill",
):
    for snapshot_time in _get_snapshot_times(conn):
        snapshot_rows = _get_snapshot_rows(conn, snapshot_time)
        company_intelligence_rows = calculate_company_intelligence_rows(
            snapshot_rows
        )
        themes = calculate_theme_snapshot(company_intelligence_rows)

        save_theme_snapshot(
            conn,
            snapshot_time,
            themes,
            eligible_company_count=len(company_intelligence_rows),
            scope=scope,
            engine_version=engine_version,
        )


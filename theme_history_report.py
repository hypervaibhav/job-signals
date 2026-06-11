import sqlite3
import sys
from datetime import datetime

from strategic_theme_confidence import classify_theme_confidence
from strategic_theme_lifecycle import (
    classify_theme_lifecycle,
    has_presentable_theme_activity,
)
from strategic_theme_history import get_theme_history
from strategic_theme_narratives import generate_theme_lifecycle_narrative


DEFAULT_DB_PATH = "jobs.db"


def _get_persisted_theme_names(conn, scope, engine_version):
    rows = conn.execute(
        """
        SELECT DISTINCT theme
        FROM strategic_theme_snapshots
        WHERE scope = ?
          AND engine_version = ?
        """,
        (scope, engine_version),
    ).fetchall()
    return [row[0] for row in rows]


def _format_timestamp(timestamp):
    if timestamp is None:
        return "never"
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %I:%M %p")


def _format_members(companies):
    return ", ".join(companies) if companies else "none"


def _format_theme_history(history):
    lifecycle = classify_theme_lifecycle(history)
    confidence = classify_theme_confidence(history, lifecycle)
    narrative = generate_theme_lifecycle_narrative(lifecycle, history)

    return (
        f"{history['theme']}\n"
        f"Lifecycle: {lifecycle}\n"
        f"Theme Confidence: {confidence}\n"
        f"Explanation: {narrative}\n"
        f"Persistence: {history['snapshots_active']}/"
        f"{history['total_eligible_snapshots']} snapshots\n"
        f"Persistence score: {history['persistence_score'] * 100:.1f}%\n"
        f"Current company count: {history['current_company_count']}\n"
        f"Peak company count: {history['peak_company_count']}\n"
        f"First seen: {_format_timestamp(history['first_detected'])}\n"
        f"Latest seen: {_format_timestamp(history['latest_detected'])}\n"
        f"Current members: {_format_members(history['current_companies'])}\n"
    )


def build_theme_history_report(conn, scope="watchlist", engine_version="v2"):
    theme_names = _get_persisted_theme_names(conn, scope, engine_version)
    histories = [
        get_theme_history(
            conn,
            theme,
            scope=scope,
            engine_version=engine_version,
        )
        for theme in theme_names
    ]
    histories = [history for history in histories if history is not None]

    if not histories:
        return (
            "STRATEGIC THEME HISTORY\n"
            "\n"
            "No strategic theme history found.\n"
        )

    histories = [
        history
        for history in histories
        if has_presentable_theme_activity(history)
    ]

    if not histories:
        return (
            "STRATEGIC THEME HISTORY\n"
            "\n"
            "No active strategic themes found.\n"
        )

    histories.sort(
        key=lambda history: (
            -history["current_company_count"],
            history["theme"],
        )
    )

    return (
        "STRATEGIC THEME HISTORY\n"
        "\n"
        + "\n".join(
            _format_theme_history(history)
            for history in histories
        )
    )


def main(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        print(build_theme_history_report(conn))
    finally:
        conn.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    main(path)

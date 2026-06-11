def classify_theme_confidence(history, lifecycle):
    if history is None:
        return "Low"

    current_company_count = history["current_company_count"]
    snapshots_active = history["snapshots_active"]
    total_eligible_snapshots = history["total_eligible_snapshots"]
    persistence_score = history["persistence_score"]

    if (
        current_company_count == 0
        or lifecycle == "Disappeared"
        or current_company_count < 2
        or snapshots_active < 2
        or total_eligible_snapshots < 3
        or persistence_score < 0.25
    ):
        return "Low"

    if (
        lifecycle in {"Stable", "Expanding"}
        and current_company_count >= 2
        and snapshots_active >= 3
        and total_eligible_snapshots >= 6
        and persistence_score >= 0.50
    ):
        return "High"

    return "Moderate"

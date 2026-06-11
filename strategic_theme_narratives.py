def _count_label(count, singular, plural):
    return singular if count == 1 else plural


def _first_active_snapshot_index(history):
    for index, snapshot in enumerate(history["snapshots"]):
        if snapshot["company_count"] > 0:
            return index
    return None


def _first_active_company_count(history):
    index = _first_active_snapshot_index(history)
    if index is None:
        return 0
    return history["snapshots"][index]["company_count"]


def _eligible_snapshots_since_first_active(history):
    index = _first_active_snapshot_index(history)
    if index is None:
        return history["total_eligible_snapshots"]
    return len(history["snapshots"][index:])


def generate_theme_lifecycle_narrative(lifecycle, history):
    if not history:
        return None

    theme = history["theme"]
    active_snapshots = history["snapshots_active"]
    total_eligible_snapshots = history["total_eligible_snapshots"]
    current_company_count = history["current_company_count"]
    peak_company_count = history["peak_company_count"]
    first_active_company_count = _first_active_company_count(history)
    active_snapshot_label = _count_label(
        active_snapshots,
        "active snapshot",
        "active snapshots",
    )
    eligible_snapshot_label = _count_label(
        total_eligible_snapshots,
        "eligible snapshot",
        "eligible snapshots",
    )
    current_company_label = _count_label(
        current_company_count,
        "company",
        "companies",
    )
    peak_company_label = _count_label(
        peak_company_count,
        "company",
        "companies",
    )
    first_active_company_label = _count_label(
        first_active_company_count,
        "company",
        "companies",
    )

    if lifecycle == "Emerging":
        emerging_active_snapshots = min(active_snapshots, 2)
        emerging_active_snapshot_label = _count_label(
            emerging_active_snapshots,
            "active snapshot",
            "active snapshots",
        )
        return (
            f"{theme} is newly detected, appearing in {emerging_active_snapshots} "
            f"{emerging_active_snapshot_label} out of {total_eligible_snapshots} "
            f"{eligible_snapshot_label}, which is fewer than the 3 active "
            "snapshots needed for an established lifecycle. Current coverage "
            f"is {current_company_count} {current_company_label}."
        )

    if lifecycle == "Expanding":
        eligible_snapshots = _eligible_snapshots_since_first_active(history)
        eligible_snapshot_label = _count_label(
            eligible_snapshots,
            "eligible snapshot",
            "eligible snapshots",
        )
        return (
            f"{theme} expanded from {first_active_company_count} "
            f"{first_active_company_label} when first detected to "
            f"{current_company_count} {current_company_label} now, remaining "
            f"near the observed peak of {peak_company_count} "
            f"{peak_company_label} across {eligible_snapshots} "
            f"{eligible_snapshot_label}."
        )

    if lifecycle == "Stable":
        if active_snapshots == 0:
            return (
                f"{theme} has not matched any companies across "
                f"{total_eligible_snapshots} {eligible_snapshot_label}."
            )

        return (
            f"{theme} is stable at {current_company_count} "
            f"{current_company_label}, with an observed peak of "
            f"{peak_company_count} {peak_company_label} across "
            f"{active_snapshots} {active_snapshot_label} out of "
            f"{total_eligible_snapshots} {eligible_snapshot_label}; current "
            "movement does not meet expansion or contraction thresholds."
        )

    if lifecycle == "Contracting":
        eligible_snapshots = _eligible_snapshots_since_first_active(history)
        eligible_snapshot_label = _count_label(
            eligible_snapshots,
            "eligible snapshot",
            "eligible snapshots",
        )
        return (
            f"{theme} contracted from {first_active_company_count} "
            f"{first_active_company_label} when first detected to "
            f"{current_company_count} {current_company_label} now, below the "
            f"observed peak of {peak_company_count} {peak_company_label} "
            f"across {eligible_snapshots} {eligible_snapshot_label}."
        )

    if lifecycle == "Disappeared":
        return (
            f"{theme} was previously detected in {active_snapshots} "
            f"{active_snapshot_label} out of {total_eligible_snapshots} "
            f"{eligible_snapshot_label}, but has {current_company_count} "
            f"{current_company_label} in the latest snapshot."
        )

    return None

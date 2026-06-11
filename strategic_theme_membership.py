def _empty_change(movement_label, current_members=None):
    return {
        "current_snapshot_time": None,
        "prior_snapshot_time": None,
        "current_members": sorted(current_members or []),
        "prior_members": [],
        "entrants": [],
        "exits": [],
        "retained_members": [],
        "new_contributors": [],
        "returning_members": [],
        "net_company_change": 0,
        "membership_changed": False,
        "meaningful_movement": False,
        "movement_label": movement_label,
        "movement_reason": (
            "Membership change requires at least two eligible snapshots."
        ),
    }


def _eligible_snapshots(history):
    return [
        snapshot
        for snapshot in history.get("snapshots", [])
        if snapshot.get("eligible_company_count", 0) > 0
    ]


def _sorted_members(snapshot):
    return sorted(set(snapshot.get("companies", [])))


def _prior_members_before_current(eligible_snapshots):
    members = set()
    for snapshot in eligible_snapshots[:-1]:
        members.update(snapshot.get("companies", []))
    return members


def _count_label(count):
    return "company" if count == 1 else "companies"


def _movement_label(prior_members, current_members, entrants, exits):
    if not entrants and not exits:
        return "No membership change"
    if not prior_members and current_members:
        return "Newly active"
    if prior_members and not current_members:
        return "Disappeared"
    if len(entrants) > len(exits):
        return "Expanded membership"
    if len(exits) > len(entrants):
        return "Contracted membership"
    return "Rotated membership"


def _movement_reason(label, entrants, exits):
    entrant_count = len(entrants)
    exit_count = len(exits)

    if label == "No membership change":
        return "No companies entered or exited since the prior eligible snapshot."
    if label == "Newly active":
        return (
            f"{entrant_count} {_count_label(entrant_count)} entered from "
            "zero prior members."
        )
    if label == "Disappeared":
        return (
            "All prior members exited; no companies remain in the latest "
            "eligible snapshot."
        )
    if label == "Expanded membership":
        return (
            f"{entrant_count} {_count_label(entrant_count)} entered and "
            f"{exit_count} {_count_label(exit_count)} exited."
        )
    if label == "Contracted membership":
        return (
            f"{exit_count} {_count_label(exit_count)} exited and "
            f"{entrant_count} {_count_label(entrant_count)} entered."
        )
    return (
        f"{entrant_count} {_count_label(entrant_count)} entered and "
        f"{exit_count} {_count_label(exit_count)} exited, leaving the "
        "company count unchanged."
    )


def calculate_theme_membership_change(history):
    if not history:
        return _empty_change("Insufficient history")

    eligible_snapshots = _eligible_snapshots(history)

    if len(eligible_snapshots) < 2:
        current_members = (
            _sorted_members(eligible_snapshots[-1])
            if eligible_snapshots
            else []
        )
        return _empty_change("Insufficient history", current_members)

    prior_snapshot = eligible_snapshots[-2]
    current_snapshot = eligible_snapshots[-1]
    prior_members = _sorted_members(prior_snapshot)
    current_members = _sorted_members(current_snapshot)

    prior_member_set = set(prior_members)
    current_member_set = set(current_members)
    entrants = sorted(current_member_set - prior_member_set)
    exits = sorted(prior_member_set - current_member_set)
    retained_members = sorted(current_member_set & prior_member_set)
    historical_members = _prior_members_before_current(eligible_snapshots)
    new_contributors = [
        company
        for company in entrants
        if company not in historical_members
    ]
    returning_members = [
        company
        for company in entrants
        if company in historical_members
    ]
    label = _movement_label(
        prior_members,
        current_members,
        entrants,
        exits,
    )
    membership_changed = bool(entrants or exits)

    return {
        "current_snapshot_time": current_snapshot["snapshot_time"],
        "prior_snapshot_time": prior_snapshot["snapshot_time"],
        "current_members": current_members,
        "prior_members": prior_members,
        "entrants": entrants,
        "exits": exits,
        "retained_members": retained_members,
        "new_contributors": new_contributors,
        "returning_members": returning_members,
        "net_company_change": len(current_members) - len(prior_members),
        "membership_changed": membership_changed,
        "meaningful_movement": membership_changed,
        "movement_label": label,
        "movement_reason": _movement_reason(label, entrants, exits),
    }

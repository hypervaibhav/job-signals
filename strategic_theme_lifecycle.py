import math


def _first_active_company_count(history):
    for snapshot in history["snapshots"]:
        if snapshot["company_count"] > 0:
            return snapshot["company_count"]
    return 0


def _growth_threshold(company_count):
    return max(1, math.ceil(company_count * 0.25))


def _decline_threshold(company_count):
    return max(1, math.ceil(company_count * 0.25))


def classify_theme_lifecycle(history):
    if history is None:
        return None

    current_company_count = history["current_company_count"]
    snapshots_active = history["snapshots_active"]

    if current_company_count == 0:
        if snapshots_active > 0:
            return "Disappeared"
        return "Stable"

    if snapshots_active < 3:
        return "Emerging"

    first_active_company_count = _first_active_company_count(history)
    peak_company_count = history["peak_company_count"]
    growth_threshold = _growth_threshold(first_active_company_count)
    decline_threshold = _decline_threshold(peak_company_count)

    if (
        current_company_count - first_active_company_count >= growth_threshold
        and current_company_count >= math.ceil(peak_company_count * 0.75)
    ):
        return "Expanding"

    if (
        first_active_company_count - current_company_count >= growth_threshold
        and peak_company_count - current_company_count >= decline_threshold
    ):
        return "Contracting"

    return "Stable"

from collections import Counter


def classify_market_direction(net_change, previous_job_count):
    change_ratio = abs(net_change) / max(previous_job_count, 1)

    if (
        net_change == 0
        or abs(net_change) < 3
        or change_ratio < 0.02
    ):
        return "Flat"

    if net_change > 0:
        return "Expanding"

    return "Contracting"


def _row_value(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    return default


def _numeric_value(row, key, default=0):
    value = _row_value(row, key, default)
    return value if isinstance(value, (int, float)) else default


def _top_signal(signal_rows):
    if not signal_rows:
        return None

    has_opportunity_score = any(
        _row_value(row, "opportunity_score") is not None
        for row in signal_rows
    )

    if has_opportunity_score:
        return max(
            signal_rows,
            key=lambda row: (
                _numeric_value(row, "opportunity_score"),
                _numeric_value(row, "signal_strength"),
                _numeric_value(row, "postings"),
            ),
        )

    return max(
        signal_rows,
        key=lambda row: (
            _numeric_value(row, "signal_strength"),
            _numeric_value(row, "postings"),
        ),
    )


def _top_movement(rows, name_key):
    if not rows:
        return None

    return max(
        rows,
        key=lambda row: (
            _numeric_value(row, "change"),
            _row_value(row, name_key, ""),
        ),
    )


def _company_strategy_mix(company_intelligence_rows):
    strategy_counts = Counter(
        row.get("intelligence")
        for row in company_intelligence_rows
        if row.get("intelligence")
    )
    return dict(strategy_counts)


def _theme_has_young_history(theme):
    eligible_snapshots = theme.get("total_eligible_snapshots")
    if isinstance(eligible_snapshots, (int, float)):
        return eligible_snapshots < 3

    persistence = theme.get("persistence")
    if not isinstance(persistence, str) or "/" not in persistence:
        return False

    try:
        _, total = persistence.split("/", 1)
        return int(total) < 3
    except ValueError:
        return False


def _build_caveats(
    net_change,
    evidence_confidence,
    evidence_confidence_reason,
    company_intelligence_rows,
    strategic_theme_rows,
):
    caveats = []

    if evidence_confidence != "HIGH":
        caveats.append(
            f"Evidence confidence is {evidence_confidence}: "
            f"{evidence_confidence_reason}"
        )

    if abs(net_change) <= 1:
        caveats.append(
            "Net movement is small; treat direction as near-flat."
        )

    if any(
        theme.get("confidence") == "Low"
        for theme in strategic_theme_rows
    ):
        caveats.append("One or more strategic themes have low confidence.")

    if any(_theme_has_young_history(theme) for theme in strategic_theme_rows):
        caveats.append(
            "One or more strategic themes have fewer than 3 eligible snapshots."
        )

    if any(
        row.get("trend_confidence") == "Low"
        for row in company_intelligence_rows
    ):
        caveats.append(
            "One or more company trend signals have low confidence."
        )

    return caveats


def _market_read(direction, evidence_confidence, top_signal, strategic_themes):
    signal_name = _row_value(top_signal, "signal")

    if signal_name:
        signal_sentence = f"{signal_name} is the strongest current signal."
    else:
        signal_sentence = "No leading signal is available."

    if strategic_themes:
        leading_theme = max(
            strategic_themes,
            key=lambda theme: (
                _numeric_value(theme, "current_company_count"),
                _row_value(theme, "theme", ""),
            ),
        )
        theme_sentence = (
            "Strategic theme coverage is led by "
            f"{leading_theme['theme']}."
        )
    else:
        theme_sentence = "No strategic theme rows are available."

    return (
        f"The market is {direction.lower()} with "
        f"{evidence_confidence} evidence confidence. "
        f"{signal_sentence} {theme_sentence}"
    )


def build_market_intelligence(
    latest_job_count,
    previous_job_count,
    net_change,
    evidence_confidence,
    evidence_confidence_reason,
    signal_rows,
    category_changes,
    company_changes,
    company_intelligence_rows,
    strategic_theme_rows,
):
    direction = classify_market_direction(net_change, previous_job_count)
    top_signal = _top_signal(signal_rows)
    themes = list(strategic_theme_rows)

    return {
        "market_direction": direction,
        "evidence_confidence": {
            "level": evidence_confidence,
            "reason": evidence_confidence_reason,
        },
        "latest_job_count": latest_job_count,
        "previous_job_count": previous_job_count,
        "net_change": net_change,
        "top_signal": top_signal,
        "top_category_movement": _top_movement(
            category_changes,
            "category",
        ),
        "top_company_momentum": _top_movement(
            company_changes,
            "company",
        ),
        "company_strategy_mix": _company_strategy_mix(
            company_intelligence_rows
        ),
        "strategic_themes": themes,
        "market_read": _market_read(
            direction,
            evidence_confidence,
            top_signal,
            themes,
        ),
        "caveats": _build_caveats(
            net_change,
            evidence_confidence,
            evidence_confidence_reason,
            company_intelligence_rows,
            themes,
        ),
    }

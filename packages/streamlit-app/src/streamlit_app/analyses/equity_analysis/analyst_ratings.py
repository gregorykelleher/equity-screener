# analyst_ratings.py

from typing import NamedTuple


class RatingResult(NamedTuple):
    """
    An analyst rating display label with its associated colour.
    """

    label: str
    color: str


def analyst_rating_label(
    value: str | float | None,
) -> RatingResult:
    """
    Map an analyst rating (string or numeric) to a display label and colour.

    Args:
        value: Raw analyst rating from the data source.

    Returns:
        RatingResult: A namedtuple with .label and .color fields.
    """
    if value is None:
        return RatingResult("N/A", "#808495")
    if isinstance(value, str):
        return _match_string_rating(value)
    return _coerce_numeric_rating(value)


def _match_string_rating(value: str) -> RatingResult:
    """
    Map a string rating to a label and colour via pattern matching.

    Args:
        value: Raw string rating (e.g. "Strong Buy", "HOLD").

    Returns:
        RatingResult: The matched label and colour.
    """
    lowered = value.strip().lower()
    patterns = (
        ("strong buy", "Strong Buy", "#15803d"),
        ("buy", "Buy", "#16a34a"),
        ("hold", "Hold", "#d97706"),
        ("neutral", "Hold", "#d97706"),
        ("strong sell", "Strong Sell", "#991b1b"),
        ("sell", "Sell", "#dc2626"),
        ("underperform", "Sell", "#dc2626"),
    )
    for pattern, label, color in patterns:
        if pattern in lowered:
            return RatingResult(label, color)
    return RatingResult(value, "#808495")


def _coerce_numeric_rating(value: float) -> RatingResult:
    """
    Coerce a value to float and dispatch to numeric rating lookup.

    Args:
        value: A numeric-like value to convert and match.

    Returns:
        RatingResult: From threshold lookup, or fallback on error.
    """
    try:
        return _match_numeric_rating(float(value))
    except (ValueError, TypeError):
        return RatingResult(str(value), "#808495")


def _match_numeric_rating(value: float) -> RatingResult:
    """
    Map a numeric rating to a label and colour via threshold lookup.

    Args:
        value: Numeric rating (typically 1.0-5.0 scale).

    Returns:
        RatingResult: The matched label and colour.
    """
    thresholds = (
        (1.5, "Strong Buy", "#15803d"),
        (2.5, "Buy", "#16a34a"),
        (3.5, "Hold", "#d97706"),
        (4.5, "Sell", "#dc2626"),
    )
    for threshold, label, color in thresholds:
        if value <= threshold:
            return RatingResult(label, color)
    return RatingResult("Strong Sell", "#991b1b")

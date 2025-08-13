# analyst_ratings.py

from typing import NamedTuple

_FALLBACK_COLOR = "#808495"


class RatingResult(NamedTuple):
    """
    An analyst rating display label with its associated color.
    """

    label: str
    color: str


_STRING_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("strong buy", "Strong Buy", "#15803d"),
    ("buy", "Buy", "#16a34a"),
    ("hold", "Hold", "#d97706"),
    ("neutral", "Hold", "#d97706"),
    ("strong sell", "Strong Sell", "#991b1b"),
    ("sell", "Sell", "#dc2626"),
    ("underperform", "Sell", "#dc2626"),
)

_NUMERIC_THRESHOLDS: tuple[tuple[float, str, str], ...] = (
    (1.5, "Strong Buy", "#15803d"),
    (2.5, "Buy", "#16a34a"),
    (3.5, "Hold", "#d97706"),
    (4.5, "Sell", "#dc2626"),
)


def _match_string_rating(value: str) -> RatingResult:
    """
    Map a string rating to a label and color via pattern matching.

    Args:
        value: Raw string rating (e.g. "Strong Buy", "HOLD").

    Returns:
        A RatingResult with the matched label and color.
    """
    lowered = value.strip().lower()
    for pattern, label, color in _STRING_PATTERNS:
        if pattern in lowered:
            return RatingResult(label, color)
    return RatingResult(value, _FALLBACK_COLOR)


def _match_numeric_rating(value: float) -> RatingResult:
    """
    Map a numeric rating to a label and color via threshold lookup.

    Args:
        value: Numeric rating (typically 1.0-5.0 scale).

    Returns:
        A RatingResult with the matched label and color.
    """
    for threshold, label, color in _NUMERIC_THRESHOLDS:
        if value <= threshold:
            return RatingResult(label, color)
    return RatingResult("Strong Sell", "#991b1b")


_FALLBACK_RESULT = RatingResult("N/A", _FALLBACK_COLOR)


def analyst_rating_label(
    value: str | float | None,
) -> RatingResult:
    """
    Map an analyst rating (string or numeric) to a display label and color.

    Args:
        value: Raw analyst rating from data source.

    Returns:
        A RatingResult namedtuple with .label and .color fields.
    """
    if value is None:
        return _FALLBACK_RESULT
    if isinstance(value, str):
        return _match_string_rating(value)
    return _coerce_numeric_rating(value)


def _coerce_numeric_rating(value: float) -> RatingResult:
    """
    Coerce a value to float and dispatch to numeric rating lookup.

    Args:
        value: A numeric-like value to convert and match.

    Returns:
        A RatingResult from threshold lookup, or fallback on error.
    """
    try:
        return _match_numeric_rating(float(value))
    except (ValueError, TypeError):
        return RatingResult(str(value), _FALLBACK_COLOR)

# formatters.py

_TRILLION = 1_000_000_000_000
_BILLION = 1_000_000_000
_MILLION = 1_000_000
_THOUSAND = 1_000

_CURRENCY_TIERS: tuple[tuple[float, float, str], ...] = (
    (_TRILLION, _TRILLION, "T"),
    (_BILLION, _BILLION, "B"),
    (_MILLION, _MILLION, "M"),
)

_LARGE_NUMBER_TIERS: tuple[tuple[float, float, str], ...] = (
    (_BILLION, _BILLION, "B"),
    (_MILLION, _MILLION, "M"),
    (_THOUSAND, _THOUSAND, "K"),
)


def fmt_currency(value: float | None) -> str:
    """
    Format a numeric value as a dollar currency string.

    Large values are abbreviated with T/B/M suffixes.
    Returns "N/A" for None.
    """
    if value is None:
        return "N/A"
    for threshold, divisor, suffix in _CURRENCY_TIERS:
        if abs(value) >= threshold:
            return f"${value / divisor:.2f}{suffix}"
    return f"${value:,.2f}"


def fmt_pct(value: float | None) -> str:
    """
    Format a decimal ratio as a percentage string.

    The value is always multiplied by 100 (e.g. 0.15 -> "15.00%").
    Returns "N/A" for None.
    """
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def fmt_number(value: float | str | None, decimals: int = 2) -> str:
    """
    Format a numeric value with thousands separators.

    Returns "N/A" for None and falls back to str() on conversion failure.
    """
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def fmt_large_number(value: float | None) -> str:
    """
    Format a large number with B/M/K abbreviations.

    Returns "N/A" for None.
    """
    if value is None:
        return "N/A"
    for threshold, divisor, suffix in _LARGE_NUMBER_TIERS:
        if abs(value) >= threshold:
            fmt = ".2f" if suffix != "K" else ".1f"
            return f"{value / divisor:{fmt}}{suffix}"
    return f"{value:,.0f}"


def fmt_ratio(value: float | str | None) -> str:
    """
    Format a ratio value with 'x' suffix (e.g. '15.2x').

    Returns "N/A" for None and falls back to str() on conversion failure.
    """
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}x"
    except (ValueError, TypeError):
        return str(value)

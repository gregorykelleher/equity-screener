# formatters.py


def fmt_currency(value: float | None) -> str:
    """
    Format a numeric value as a dollar currency string.

    Large values are abbreviated with T/B/M suffixes.

    Args:
        value: Numeric value to format, or None.

    Returns:
        str: Formatted currency string, or "N/A" for None.
    """
    if value is None:
        return "N/A"
    for divisor, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if abs(value) >= divisor:
            return f"${value / divisor:.2f}{suffix}"
    return f"${value:,.2f}"


def fmt_pct(value: float | None) -> str:
    """
    Format a decimal ratio as a percentage string.

    The value is always multiplied by 100 (e.g. 0.15 -> "15.00%").

    Args:
        value: Decimal ratio to format, or None.

    Returns:
        str: Formatted percentage string, or "N/A" for None.
    """
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def fmt_number(value: float | str | None, decimals: int = 2) -> str:
    """
    Format a numeric value with thousands separators.

    Args:
        value: Value to format, or None.
        decimals: Number of decimal places to display.

    Returns:
        str: Formatted number string, or "N/A" for None.
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

    Args:
        value: Numeric value to format, or None.

    Returns:
        str: Abbreviated number string, or "N/A" for None.
    """
    if value is None:
        return "N/A"
    tiers = ((1e9, "B", ".2f"), (1e6, "M", ".2f"), (1e3, "K", ".1f"))
    for divisor, suffix, fmt in tiers:
        if abs(value) >= divisor:
            return f"{value / divisor:{fmt}}{suffix}"
    return f"{value:,.0f}"


def fmt_ratio(value: float | str | None) -> str:
    """
    Format a ratio value with 'x' suffix (e.g. '15.2x').

    Args:
        value: Ratio value to format, or None.

    Returns:
        str: Formatted ratio string, or "N/A" for None.
    """
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}x"
    except (ValueError, TypeError):
        return str(value)

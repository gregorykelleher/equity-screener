# checks.py

from decimal import Decimal

from equity_aggregator import CanonicalEquity

from streamlit_app.reports.fields import has_field
from streamlit_app.reports.models import ConsistencyFinding


def run_cross_field_checks(
    equities: list[CanonicalEquity],
) -> tuple[ConsistencyFinding, ...]:
    """
    Detect cross-field logic inconsistencies across all equities.

    Args:
        equities: All canonical equities.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each consistency
            check performed.
    """
    total = len(equities)
    return (
        _finding(
            "Price recorded without market cap",
            equities,
            total,
            lambda eq: has_field(eq, "last_price") and not has_field(eq, "market_cap"),
        ),
        _finding(
            "Market cap recorded without price",
            equities,
            total,
            lambda eq: has_field(eq, "market_cap") and not has_field(eq, "last_price"),
        ),
        _finding(
            "Price and market cap both missing",
            equities,
            total,
            lambda eq: (
                not has_field(eq, "last_price") and not has_field(eq, "market_cap")
            ),
        ),
        _finding(
            "Partial 52-week range",
            equities,
            total,
            lambda eq: (
                has_field(eq, "fifty_two_week_min")
                != has_field(eq, "fifty_two_week_max")
            ),
        ),
    )


def run_ratio_checks(
    equities: list[CanonicalEquity],
) -> tuple[ConsistencyFinding, ...]:
    """
    Detect logically inconsistent financial ratio relationships.

    Args:
        equities: All canonical equities.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each ratio
            consistency check performed.
    """
    total = len(equities)
    return (
        _finding(
            "Profit margin exceeds gross margin",
            equities,
            total,
            _profit_exceeds_gross,
        ),
        _finding(
            "Operating margin exceeds gross margin",
            equities,
            total,
            _operating_exceeds_gross,
        ),
        _finding(
            "Trailing P/E without EPS",
            equities,
            total,
            lambda eq: (
                has_field(eq, "trailing_pe") and not has_field(eq, "trailing_eps")
            ),
        ),
        _finding(
            "Revenue/share without revenue",
            equities,
            total,
            lambda eq: (
                has_field(eq, "revenue_per_share") and not has_field(eq, "revenue")
            ),
        ),
        _finding(
            "Price/book without price",
            equities,
            total,
            lambda eq: (
                has_field(eq, "price_to_book") and not has_field(eq, "last_price")
            ),
        ),
    )


def run_plausibility_checks(
    equities: list[CanonicalEquity],
) -> tuple[ConsistencyFinding, ...]:
    """
    Detect individual field values outside plausible ranges.

    Args:
        equities: All canonical equities.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each value
            plausibility check performed.
    """
    total = len(equities)
    return (
        _finding(
            "52-week min exceeds max",
            equities,
            total,
            _has_inverted_range,
        ),
        _finding(
            "Price outside 52-week range",
            equities,
            total,
            _price_outside_range,
        ),
        _finding(
            "Extreme dividend yield (>100%)",
            equities,
            total,
            lambda eq: (
                eq.financials.dividend_yield is not None
                and eq.financials.dividend_yield > 1
            ),
        ),
        _finding(
            "Extreme trailing P/E (\u00b11000)",
            equities,
            total,
            _has_extreme_pe,
        ),
        _finding(
            "Holdings exceed 100%",
            equities,
            total,
            _holdings_exceed,
        ),
        _finding(
            "Extreme ROE or ROA (\u00b1500%)",
            equities,
            total,
            _has_extreme_return,
        ),
    )


def _finding(
    description: str,
    equities: list[CanonicalEquity],
    total: int,
    predicate: object,
) -> ConsistencyFinding:
    """
    Build a ConsistencyFinding by counting matches.

    Args:
        description: Human-readable check description.
        equities: All canonical equities.
        total: Total number of equities.
        predicate: Callable returning True for affected equities.

    Returns:
        ConsistencyFinding: The finding for this check.
    """
    count = sum(1 for eq in equities if predicate(eq))  # type: ignore[operator]
    return ConsistencyFinding(
        description=description,
        count=count,
        total=total,
    )


def _profit_exceeds_gross(equity: CanonicalEquity) -> bool:
    """
    Check whether profit margin is greater than gross margin.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if both margins are present and profit exceeds gross.
    """
    profit = equity.financials.profit_margin
    gross = equity.financials.gross_margin
    return profit is not None and gross is not None and profit > gross


def _operating_exceeds_gross(equity: CanonicalEquity) -> bool:
    """
    Check whether operating margin is greater than gross margin.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if both margins are present and operating exceeds gross.
    """
    operating = equity.financials.operating_margin
    gross = equity.financials.gross_margin
    return operating is not None and gross is not None and operating > gross


def _has_extreme_pe(equity: CanonicalEquity) -> bool:
    """
    Check whether trailing P/E has extreme magnitude.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if trailing P/E is present and exceeds ±1000.
    """
    pe_threshold = 1000
    pe = equity.financials.trailing_pe
    return pe is not None and abs(pe) > pe_threshold


def _has_inverted_range(equity: CanonicalEquity) -> bool:
    """
    Check whether the 52-week minimum exceeds the maximum.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if both bounds are present and min exceeds max.
    """
    min_val = equity.financials.fifty_two_week_min
    max_val = equity.financials.fifty_two_week_max
    return min_val is not None and max_val is not None and min_val > max_val


def _price_outside_range(equity: CanonicalEquity) -> bool:
    """
    Check whether the last price is outside the 52-week range.

    Note:
        Applies a 5% tolerance above the maximum to accommodate
        stale range data.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if price, min, and max are all present and price
            falls below min or above max with 5% tolerance.
    """
    price = equity.financials.last_price
    min_val = equity.financials.fifty_two_week_min
    max_val = equity.financials.fifty_two_week_max
    if price is None or min_val is None or max_val is None:
        return False
    return price < min_val or price > max_val * Decimal("1.05")


def _holdings_exceed(equity: CanonicalEquity) -> bool:
    """
    Check whether combined holdings exceed 105%.

    Note:
        Applies a 5% tolerance to accommodate rounding across sources.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if both holdings are present and sum exceeds 1.05.
    """
    insiders = equity.financials.held_insiders
    institutions = equity.financials.held_institutions
    if insiders is None or institutions is None:
        return False
    return insiders + institutions > Decimal("1.05")


def _has_extreme_return(equity: CanonicalEquity) -> bool:
    """
    Check whether ROE or ROA has extreme magnitude.

    Args:
        equity: A single canonical equity.

    Returns:
        bool: True if either metric is present and exceeds \u00b1500%.
    """
    threshold = 5
    roe = equity.financials.return_on_equity
    roa = equity.financials.return_on_assets
    if roe is not None and abs(roe) > threshold:
        return True
    return roa is not None and abs(roa) > threshold

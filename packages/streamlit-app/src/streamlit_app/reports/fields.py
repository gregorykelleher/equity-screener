# fields.py

from equity_aggregator import CanonicalEquity


def identity_fields() -> tuple[tuple[str, str], ...]:
    """
    Return the 7 identity field specifications.

    Returns:
        tuple[tuple[str, str], ...]: Pairs of (attr_name, label).
    """
    return (
        ("name", "Name"),
        ("symbol", "Symbol"),
        ("share_class_figi", "FIGI"),
        ("isin", "ISIN"),
        ("cusip", "CUSIP"),
        ("cik", "CIK"),
        ("lei", "LEI"),
    )


def financial_fields() -> tuple[tuple[str, str], ...]:
    """
    Return the 31 financial field specifications.

    Returns:
        tuple[tuple[str, str], ...]: Pairs of (attr_name, label).
    """
    return (
        ("mics", "MICs"),
        ("currency", "Currency"),
        ("last_price", "Last Price"),
        ("market_cap", "Market Cap"),
        ("fifty_two_week_min", "52W Min"),
        ("fifty_two_week_max", "52W Max"),
        ("dividend_yield", "Dividend Yield"),
        ("market_volume", "Market Volume"),
        ("held_insiders", "Held Insiders"),
        ("held_institutions", "Held Institutions"),
        ("short_interest", "Short Interest"),
        ("share_float", "Share Float"),
        ("shares_outstanding", "Shares Outstanding"),
        ("revenue_per_share", "Revenue/Share"),
        ("profit_margin", "Profit Margin"),
        ("gross_margin", "Gross Margin"),
        ("operating_margin", "Operating Margin"),
        ("free_cash_flow", "Free Cash Flow"),
        ("operating_cash_flow", "Operating Cash Flow"),
        ("return_on_equity", "ROE"),
        ("return_on_assets", "ROA"),
        ("performance_1_year", "1Y Performance"),
        ("total_debt", "Total Debt"),
        ("revenue", "Revenue"),
        ("ebitda", "EBITDA"),
        ("trailing_pe", "Trailing P/E"),
        ("price_to_book", "Price/Book"),
        ("trailing_eps", "Trailing EPS"),
        ("analyst_rating", "Analyst Rating"),
        ("industry", "Industry"),
        ("sector", "Sector"),
    )


def heatmap_fields() -> tuple[tuple[str, str], ...]:
    """
    Return financial fields excluding those trivially at 100% per sector.

    Note:
        Excludes 'industry', 'sector', and 'currency' because the heatmap
        groups by sector, so these are always fully populated within each
        group.

    Returns:
        tuple[tuple[str, str], ...]: Pairs of (attr_name, label).
    """
    excluded = {"industry", "sector", "currency"}
    return tuple(
        (attr, label) for attr, label in financial_fields() if attr not in excluded
    )


def has_field(
    equity: CanonicalEquity,
    attr: str,
) -> bool:
    """
    Check whether a financials attribute is populated.

    Args:
        equity: A single canonical equity.
        attr: Attribute name on the financials group.

    Returns:
        bool: True if the attribute is not None.
    """
    return getattr(equity.financials, attr, None) is not None

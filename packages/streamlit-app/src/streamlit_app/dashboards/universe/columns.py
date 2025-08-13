# columns.py

from typing import Any, NamedTuple

from streamlit_app.dashboards.universe.formatters import (
    CURRENCY_FMT,
    LARGE_CURRENCY_FMT,
    LARGE_NUMBER_FMT,
    PERCENTAGE_FMT,
    RATIO_FMT,
)


class FieldDef(NamedTuple):
    """
    Map a display column name to a dot-path accessor on CanonicalEquity.
    """

    column: str
    accessor: str


class ColumnGroup(NamedTuple):
    """
    A named header group containing one or more display columns.
    """

    header: str
    columns: tuple[str, ...]


class FormatterRule(NamedTuple):
    """
    Bind a JsCode formatter to a set of columns with optional extra kwargs.
    """

    formatter: Any
    columns: frozenset[str]
    extra_kwargs: dict[str, Any]


FIELD_MAPPING: tuple[FieldDef, ...] = (
    # Identity
    FieldDef("Name", "identity.name"),
    FieldDef("Symbol", "identity.symbol"),
    FieldDef("Share Class FIGI", "identity.share_class_figi"),
    FieldDef("ISIN", "identity.isin"),
    FieldDef("CUSIP", "identity.cusip"),
    FieldDef("CIK", "identity.cik"),
    FieldDef("LEI", "identity.lei"),
    # Financials
    FieldDef("MICs", "financials.mics"),
    FieldDef("Currency", "financials.currency"),
    FieldDef("Last Price", "financials.last_price"),
    FieldDef("Market Cap", "financials.market_cap"),
    FieldDef("52W Min", "financials.fifty_two_week_min"),
    FieldDef("52W Max", "financials.fifty_two_week_max"),
    FieldDef("Dividend Yield", "financials.dividend_yield"),
    FieldDef("Market Volume", "financials.market_volume"),
    # Ownership
    FieldDef("Held Insiders", "financials.held_insiders"),
    FieldDef("Held Institutions", "financials.held_institutions"),
    FieldDef("Short Interest", "financials.short_interest"),
    FieldDef("Share Float", "financials.share_float"),
    FieldDef("Shares Outstanding", "financials.shares_outstanding"),
    # Per-share
    FieldDef("Revenue/Share", "financials.revenue_per_share"),
    # Profitability
    FieldDef("Profit Margin", "financials.profit_margin"),
    FieldDef("Gross Margin", "financials.gross_margin"),
    FieldDef("Operating Margin", "financials.operating_margin"),
    # Cash flow
    FieldDef("Free Cash Flow", "financials.free_cash_flow"),
    FieldDef("Operating Cash Flow", "financials.operating_cash_flow"),
    # Returns
    FieldDef("ROE", "financials.return_on_equity"),
    FieldDef("ROA", "financials.return_on_assets"),
    FieldDef("1Y Performance", "financials.performance_1_year"),
    # Financial position
    FieldDef("Total Debt", "financials.total_debt"),
    # Income statement
    FieldDef("Revenue", "financials.revenue"),
    FieldDef("EBITDA", "financials.ebitda"),
    # Valuation
    FieldDef("Trailing P/E", "financials.trailing_pe"),
    FieldDef("Price/Book", "financials.price_to_book"),
    FieldDef("Trailing EPS", "financials.trailing_eps"),
    # Classification
    FieldDef("Analyst Rating", "financials.analyst_rating"),
    FieldDef("Industry", "financials.industry"),
    FieldDef("Sector", "financials.sector"),
)

DISPLAY_COLUMNS: tuple[str, ...] = tuple(f.column for f in FIELD_MAPPING)

COLUMN_GROUPS: tuple[ColumnGroup, ...] = (
    ColumnGroup("Equity", ("Name", "Symbol")),
    ColumnGroup(
        "Market", ("Last Price", "Market Cap", "52W Min", "52W Max", "Market Volume")
    ),
    ColumnGroup(
        "Ownership",
        (
            "Held Insiders",
            "Held Institutions",
            "Short Interest",
            "Share Float",
            "Shares Outstanding",
        ),
    ),
    ColumnGroup(
        "Valuation",
        (
            "Trailing P/E",
            "Price/Book",
            "Trailing EPS",
            "Revenue/Share",
            "Dividend Yield",
        ),
    ),
    ColumnGroup(
        "Profitability",
        ("Profit Margin", "Gross Margin", "Operating Margin", "ROE", "ROA"),
    ),
    ColumnGroup(
        "Financials",
        ("Revenue", "EBITDA", "Free Cash Flow", "Operating Cash Flow", "Total Debt"),
    ),
    ColumnGroup("Performance", ("1Y Performance", "Analyst Rating")),
    ColumnGroup("Classification", ("Industry", "Sector")),
)

CURRENCY_COLS: frozenset[str] = frozenset(
    {
        "Last Price",
        "52W Min",
        "52W Max",
        "Revenue/Share",
        "Trailing EPS",
    }
)
LARGE_CURRENCY_COLS: frozenset[str] = frozenset(
    {
        "Market Cap",
        "Free Cash Flow",
        "Operating Cash Flow",
        "Total Debt",
        "Revenue",
        "EBITDA",
    }
)
PERCENTAGE_COLS: frozenset[str] = frozenset(
    {
        "Dividend Yield",
        "Held Insiders",
        "Held Institutions",
        "Short Interest",
        "Profit Margin",
        "Gross Margin",
        "Operating Margin",
        "ROE",
        "ROA",
        "1Y Performance",
    }
)
LARGE_NUMBER_COLS: frozenset[str] = frozenset(
    {
        "Market Volume",
        "Share Float",
        "Shares Outstanding",
    }
)
RATIO_COLS: frozenset[str] = frozenset({"Trailing P/E", "Price/Book"})

PCT_STYLE_COLS: frozenset[str] = frozenset(
    {
        "Profit Margin",
        "Gross Margin",
        "Operating Margin",
        "ROE",
        "ROA",
        "1Y Performance",
        "Dividend Yield",
    }
)

IDENTIFIER_COLS: frozenset[str] = frozenset(
    {
        "Share Class FIGI",
        "ISIN",
        "CUSIP",
        "CIK",
        "LEI",
        "MICs",
        "Currency",
    }
)

FORMATTER_TABLE: tuple[FormatterRule, ...] = (
    FormatterRule(CURRENCY_FMT, CURRENCY_COLS, {"filter": "agNumberColumnFilter"}),
    FormatterRule(
        LARGE_CURRENCY_FMT, LARGE_CURRENCY_COLS, {"filter": "agNumberColumnFilter"}
    ),
    FormatterRule(PERCENTAGE_FMT, PERCENTAGE_COLS, {"filter": "agNumberColumnFilter"}),
    FormatterRule(
        LARGE_NUMBER_FMT, LARGE_NUMBER_COLS, {"filter": "agNumberColumnFilter"}
    ),
    FormatterRule(RATIO_FMT, RATIO_COLS, {"filter": "agNumberColumnFilter"}),
)

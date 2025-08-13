# grid_configurators.py

from st_aggrid import GridOptionsBuilder

from streamlit_app.dashboards.universe.columns import (
    FORMATTER_TABLE,
    IDENTIFIER_COLS,
    PCT_STYLE_COLS,
)
from streamlit_app.dashboards.universe.formatters import (
    ANALYST_STYLE,
    IDENTIFIER_TOOLTIP,
    PCT_STYLE,
    QUICK_FILTER_TEXT,
    TOOLTIP_VALUE_GETTER,
)


def configure_columns(gb: GridOptionsBuilder) -> None:
    """
    Apply all column configurations to the grid builder.

    Orchestrates defaults, visibility, pinning, classification, formatting,
    percentage styling, and analyst rating in sequence.

    Args:
        gb: Grid options builder to mutate.
    """
    _configure_defaults(gb)
    _configure_hidden_columns(gb)
    _configure_pinned_columns(gb)
    _configure_classification_columns(gb)
    _apply_formatters(gb)
    _apply_percentage_styles(gb)
    _configure_analyst_column(gb)


def _configure_defaults(gb: GridOptionsBuilder) -> None:
    """
    Apply pagination, selection mode, default column props, and sidebar.

    Args:
        gb: Grid options builder to mutate.
    """
    gb.configure_pagination(paginationAutoPageSize=True, paginationPageSize=50)
    gb.configure_selection("single")
    gb.configure_default_column(
        editable=False,
        sortable=True,
        resizable=True,
        minWidth=150,
        width=200,
        filter=True,
    )
    gb.configure_side_bar(filters_panel=True, columns_panel=True)


def _configure_hidden_columns(gb: GridOptionsBuilder) -> None:
    """
    Hide identifier columns while keeping data available for tooltips.

    Args:
        gb: Grid options builder to mutate.
    """
    for col in IDENTIFIER_COLS:
        gb.configure_column(col, hide=True)


def _configure_pinned_columns(gb: GridOptionsBuilder) -> None:
    """
    Pin Name and Symbol to the left, attach tooltip and quick-filter to Name.

    Args:
        gb: Grid options builder to mutate.
    """
    gb.configure_column(
        "Name",
        minWidth=200,
        pinned="left",
        tooltipValueGetter=TOOLTIP_VALUE_GETTER,
        tooltipComponent=IDENTIFIER_TOOLTIP,
        getQuickFilterText=QUICK_FILTER_TEXT,
    )
    gb.configure_column("Symbol", pinned="left")


def _configure_classification_columns(gb: GridOptionsBuilder) -> None:
    """
    Configure Industry and Sector columns with set filters.

    Args:
        gb: Grid options builder to mutate.
    """
    gb.configure_column("Industry", minWidth=150, filter="agSetColumnFilter")
    gb.configure_column("Sector", minWidth=150, filter="agSetColumnFilter")


def _configure_analyst_column(gb: GridOptionsBuilder) -> None:
    """
    Configure the Analyst Rating column with its unique colour style and set filter.

    Args:
        gb: Grid options builder to mutate.
    """
    gb.configure_column(
        "Analyst Rating",
        cellStyle=ANALYST_STYLE,
        filter="agSetColumnFilter",
    )


def _apply_formatters(gb: GridOptionsBuilder) -> None:
    """
    Apply value formatters from the FORMATTER_TABLE.

    Iterates each FormatterRule and assigns its JsCode formatter and extra
    kwargs to every column in the rule.

    Args:
        gb: Grid options builder to mutate.
    """
    for rule in FORMATTER_TABLE:
        for col in rule.columns:
            gb.configure_column(col, valueFormatter=rule.formatter, **rule.extra_kwargs)


def _apply_percentage_styles(gb: GridOptionsBuilder) -> None:
    """
    Colour positive/negative percentage columns green/red.

    Applies the PCT_STYLE JsCode cell style to every column listed in
    PCT_STYLE_COLS.

    Args:
        gb: Grid options builder to mutate.
    """
    for col in PCT_STYLE_COLS:
        gb.configure_column(col, cellStyle=PCT_STYLE)

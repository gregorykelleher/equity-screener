# charts.py

import pandas as pd
import plotly.graph_objects as go


def build_price_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a line chart of historical equity prices.

    Args:
        df: DataFrame containing snapshot_date and last_price columns.

    Returns:
        go.Figure | None: Price chart, or None if data is unavailable.
    """
    if not _has_data(df, "last_price"):
        return None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["snapshot_date"],
            y=df["last_price"],
            mode="lines+markers",
            name="Price",
        )
    )
    fig.update_layout(**_base_layout(), yaxis_title="Price")
    return fig


def build_margin_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a multi-line chart of gross, operating, and profit margins.

    Args:
        df: DataFrame containing snapshot_date and margin columns.

    Returns:
        go.Figure | None: Margin chart, or None if no margin data exists.
    """
    cols = {
        "gross_margin": "Gross Margin",
        "operating_margin": "Operating Margin",
        "profit_margin": "Profit Margin",
    }
    available = {c: label for c, label in cols.items() if _has_data(df, c)}
    if not available:
        return None

    fig = go.Figure()
    for col, label in available.items():
        fig.add_trace(
            go.Scatter(
                x=df["snapshot_date"],
                y=df[col],
                mode="lines+markers",
                name=label,
            )
        )
    fig.update_layout(
        **_base_layout(),
        yaxis_title="Margin",
        yaxis_tickformat=".1%",
    )
    return fig


def build_earnings_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a dual-axis chart of trailing EPS (line) and revenue per share (bar).

    Args:
        df: DataFrame containing snapshot_date and earnings columns.

    Returns:
        go.Figure | None: Earnings chart, or None if neither series exists.
    """
    has_eps = _has_data(df, "trailing_eps")
    has_rev = _has_data(df, "revenue_per_share")
    if not has_eps and not has_rev:
        return None

    fig = go.Figure()
    if has_rev:
        fig.add_trace(
            go.Bar(
                x=df["snapshot_date"],
                y=df["revenue_per_share"],
                name="Revenue/Share",
                yaxis="y2",
                opacity=0.5,
            )
        )
    if has_eps:
        fig.add_trace(
            go.Scatter(
                x=df["snapshot_date"],
                y=df["trailing_eps"],
                mode="lines+markers",
                name="Trailing EPS",
            )
        )
    fig.update_layout(
        **_base_layout(),
        yaxis_title="EPS",
        yaxis2={
            "title": "Revenue/Share",
            "overlaying": "y",
            "side": "right",
        },
    )
    return fig


def build_valuation_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a multi-line chart of valuation ratios (P/B and P/E).

    Args:
        df: DataFrame containing snapshot_date and valuation columns.

    Returns:
        go.Figure | None: Valuation chart, or None if no ratio data exists.
    """
    cols = {
        "price_to_book": "P/B",
        "trailing_pe": "P/E",
    }
    available = {c: label for c, label in cols.items() if _has_data(df, c)}
    if not available:
        return None

    fig = go.Figure()
    for col, label in available.items():
        fig.add_trace(
            go.Scatter(
                x=df["snapshot_date"],
                y=df[col],
                mode="lines+markers",
                name=label,
            )
        )
    fig.update_layout(**_base_layout(), yaxis_title="Ratio")
    return fig


def build_cash_flow_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a grouped bar chart of operating and free cash flow.

    Args:
        df: DataFrame containing snapshot_date and cash flow columns.

    Returns:
        go.Figure | None: Cash flow chart, or None if no data exists.
    """
    cols = {
        "operating_cash_flow": "Operating Cash Flow",
        "free_cash_flow": "Free Cash Flow",
    }
    available = {c: label for c, label in cols.items() if _has_data(df, c)}
    if not available:
        return None

    fig = go.Figure()
    for col, label in available.items():
        fig.add_trace(
            go.Bar(
                x=df["snapshot_date"],
                y=df[col],
                name=label,
            )
        )
    fig.update_layout(
        **_base_layout(),
        yaxis_title="Cash Flow",
        barmode="group",
    )
    return fig


def build_debt_shares_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a dual-axis chart of total debt (bar) and shares outstanding (line).

    Args:
        df: DataFrame containing snapshot_date, total_debt, and
            shares_outstanding columns.

    Returns:
        go.Figure | None: Debt/shares chart, or None if neither series exists.
    """
    has_debt = _has_data(df, "total_debt")
    has_shares = _has_data(df, "shares_outstanding")
    if not has_debt and not has_shares:
        return None

    fig = go.Figure()
    if has_debt:
        fig.add_trace(
            go.Bar(
                x=df["snapshot_date"],
                y=df["total_debt"],
                name="Total Debt",
            )
        )
    if has_shares:
        fig.add_trace(
            go.Scatter(
                x=df["snapshot_date"],
                y=df["shares_outstanding"],
                mode="lines+markers",
                name="Shares Outstanding",
                yaxis="y2",
            )
        )
    fig.update_layout(
        **_base_layout(),
        yaxis_title="Total Debt",
        yaxis2={
            "title": "Shares Outstanding",
            "overlaying": "y",
            "side": "right",
        },
    )
    return fig


def build_ownership_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Build a multi-line chart of insider and institutional ownership.

    Args:
        df: DataFrame containing snapshot_date and ownership columns.

    Returns:
        go.Figure | None: Ownership chart, or None if no data exists.
    """
    cols = {
        "held_insiders": "Insiders",
        "held_institutions": "Institutions",
    }
    available = {c: label for c, label in cols.items() if _has_data(df, c)}
    if not available:
        return None

    fig = go.Figure()
    for col, label in available.items():
        fig.add_trace(
            go.Scatter(
                x=df["snapshot_date"],
                y=df[col],
                mode="lines+markers",
                name=label,
            )
        )
    fig.update_layout(
        **_base_layout(),
        yaxis_title="Ownership %",
        yaxis_tickformat=".1%",
    )
    return fig


def _base_layout() -> dict:
    """
    Return the base Plotly layout configuration shared by all charts.

    Returns:
        dict: Layout kwargs for fig.update_layout().
    """
    return {
        "margin": {"l": 40, "r": 20, "t": 30, "b": 40},
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        "hovermode": "x unified",
        "template": "plotly_white",
        "xaxis": {"type": "category"},
    }


def _has_data(df: pd.DataFrame, col: str) -> bool:
    """
    Check whether a DataFrame column exists and contains at least one
    non-null value.

    Args:
        df: The DataFrame to inspect.
        col: Column name to check.

    Returns:
        bool: True if the column has data, False otherwise.
    """
    return col in df.columns and df[col].notna().any()

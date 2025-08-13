# renderers.py

from collections.abc import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from streamlit_app.analyses.equity_trends.charts import (
    build_cash_flow_chart,
    build_debt_shares_chart,
    build_earnings_chart,
    build_margin_chart,
    build_ownership_chart,
    build_price_chart,
    build_valuation_chart,
)


def render_header(name: str, df: pd.DataFrame) -> None:
    """
    Render the page header with equity name and snapshot date range.

    Args:
        name: The equity display name.
        df: Historical snapshot DataFrame.
    """
    st.header(f"Equity Trends \u2014 {name}")
    if df.empty or "snapshot_date" not in df.columns:
        return
    dates = df["snapshot_date"].dropna()
    if dates.empty:
        return
    st.caption(f"{len(dates)} snapshot(s) \u2014 {dates.min()} to {dates.max()}")


def render_trends(df: pd.DataFrame) -> None:
    """
    Render all trend charts: a full-width price chart followed by paired rows.

    Args:
        df: Historical snapshot DataFrame.
    """
    _render_price_chart(df)
    _render_paired_charts(df)


def _render_price_chart(df: pd.DataFrame) -> None:
    """
    Render the full-width price chart if data is available.

    Args:
        df: Historical snapshot DataFrame.
    """
    price_fig = build_price_chart(df)
    if price_fig is None:
        return
    st.subheader("Price")
    st.plotly_chart(
        price_fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def _render_paired_charts(df: pd.DataFrame) -> None:
    """
    Render paired chart rows in a two-column layout.

    Args:
        df: Historical snapshot DataFrame.
    """
    chart_rows: tuple[tuple[tuple[str, Callable[..., go.Figure | None]], ...], ...] = (
        (
            ("Margins", build_margin_chart),
            ("Earnings & Revenue", build_earnings_chart),
        ),
        (
            ("Valuation", build_valuation_chart),
            ("Cash Flow", build_cash_flow_chart),
        ),
        (
            ("Debt & Shares", build_debt_shares_chart),
            ("Ownership", build_ownership_chart),
        ),
    )
    for row in chart_rows:
        _render_chart_row(df, row)


def _render_chart_row(
    df: pd.DataFrame,
    row: tuple[tuple[str, Callable[..., go.Figure | None]], ...],
) -> None:
    """
    Render a single row of paired charts in two columns.

    Args:
        df: Historical snapshot DataFrame.
        row: Tuple of (title, chart_builder) pairs for this row.
    """
    figures = [(title, builder(df)) for title, builder in row]
    visible = [(t, f) for t, f in figures if f is not None]
    if not visible:
        return
    st.divider()
    cols = st.columns(2, gap="large")
    for idx, (title, fig) in enumerate(visible):
        with cols[idx]:
            st.subheader(title)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )

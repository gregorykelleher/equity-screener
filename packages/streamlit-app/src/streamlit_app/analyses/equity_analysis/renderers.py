# renderers.py

import contextlib
from typing import Any

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from streamlit_app.analyses.equity_analysis.analyst_ratings import (
    analyst_rating_label,
)
from streamlit_app.analyses.equity_analysis.formatters import (
    fmt_currency,
    fmt_large_number,
    fmt_number,
    fmt_pct,
    fmt_ratio,
)
from streamlit_app.analyses.equity_analysis.html_components import (
    render_colored_pct_metric,
)
from streamlit_app.analyses.equity_analysis.tradingview import (
    logo_url,
    render_profile,
)


def render_header(
    name: str,
    logoid: str | None,
    data: dict[str, Any],
) -> None:
    """
    Render the equity page header with logo, name, symbol, and badges.

    Args:
        name: The equity display name.
        logoid: TradingView logo identifier, or None if unavailable.
        data: Row dict from the Universe grid.
    """
    logo_img = ""
    if logoid:
        url = logo_url(logoid)
        logo_img = (
            f'<img src="{url}" width="36" height="36"'
            f' style="vertical-align:middle;margin-right:10px;">'
        )
    st.markdown(
        f'<div style="display:flex;align-items:center;">'
        f"{logo_img}"
        f'<span style="font-size:1.75em;font-weight:700;">'
        f"{name}</span></div>",
        unsafe_allow_html=True,
    )

    symbol = data.get("Symbol", "")
    left = f"<strong>{symbol}</strong>" if symbol else ""
    badges = _badge_html(data)
    st.markdown(
        f'<div style="display:flex;align-items:baseline;'
        f'font-size:0.85em;">'
        f"<span>{left}</span>"
        f'<span style="margin-left:auto;">{badges}</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()


def render_metrics_banner(data: dict[str, Any]) -> None:
    """
    Render the top-level metrics row: price, market cap, P/E, yield, rating.

    Args:
        data: Row dict from the Universe grid.
    """
    perf_1y = data.get("1Y Performance")
    delta = f"{fmt_pct(perf_1y)} (1Y)" if perf_1y is not None else None

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Last Price", fmt_currency(data.get("Last Price")), delta=delta)
    m2.metric("Market Cap", fmt_currency(data.get("Market Cap")))
    m3.metric("Trailing P/E", fmt_ratio(data.get("Trailing P/E")))
    m4.metric("Dividend Yield", fmt_pct(data.get("Dividend Yield")))
    _render_analyst_rating(m5, data.get("Analyst Rating"))
    st.divider()


def render_52w_range_and_profile(
    data: dict[str, Any],
    tv_symbol: str,
) -> None:
    """
    Render the 52-week range bar alongside the company profile widget.

    Args:
        data: Row dict from the Universe grid.
        tv_symbol: Resolved TradingView EXCHANGE:SYMBOL string.
    """
    low = data.get("52W Min")
    high = data.get("52W Max")
    price = data.get("Last Price")
    has_range = (
        low is not None and high is not None and price is not None and high > low
    )

    if not has_range:
        st.subheader("Company Profile")
        render_profile(tv_symbol)
        return

    _render_range_with_profile(low, high, price, tv_symbol)


def render_detail_tabs(data: dict[str, Any]) -> None:
    """
    Render the detail tabs for valuation, profitability, ownership,
    financials, and identifiers.

    Args:
        data: Row dict from the Universe grid.
    """
    tab_names = [
        "Valuation",
        "Profitability",
        "Ownership & Float",
        "Financials",
        "Identifiers",
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        _render_tab_valuation(data)
    with tabs[1]:
        _render_tab_profitability(data)
    with tabs[2]:
        _render_tab_ownership(data)
    with tabs[3]:
        _render_tab_financials(data)
    with tabs[4]:
        _render_tab_identifiers(data)


def _badge_html(data: dict[str, Any]) -> str:
    """
    Build HTML badge spans for sector and industry classification.

    Args:
        data: Row dict from the Universe grid.

    Returns:
        str: Concatenated HTML badge string.
    """
    sector_style = (
        "background-color:#4f46e5;padding:3px 10px;"
        "border-radius:12px;font-size:0.75em;color:#ffffff;"
        "margin-left:8px;display:inline-block;vertical-align:baseline;"
    )
    industry_style = (
        "background-color:#0d9488;padding:3px 10px;"
        "border-radius:12px;font-size:0.75em;color:#ffffff;"
        "margin-left:8px;display:inline-block;vertical-align:baseline;"
    )
    parts: list[str] = []
    sector = data.get("Sector", "")
    if sector:
        parts.append(f'<span style="{sector_style}">{sector}</span>')
    industry = data.get("Industry", "")
    if industry:
        parts.append(f'<span style="{industry_style}">{industry}</span>')
    return "".join(parts)


def _render_range_with_profile(
    low: float,
    high: float,
    price: float,
    tv_symbol: str,
) -> None:
    """
    Render a two-column layout with 52-week range bar and company profile.

    Args:
        low: 52-week low price.
        high: 52-week high price.
        price: Current last price.
        tv_symbol: Resolved TradingView EXCHANGE:SYMBOL string.
    """
    col_range, col_profile = st.columns(2, gap="large")
    with col_range:
        st.subheader("52-Week Range")
        pct = max(0.0, min(1.0, (price - low) / (high - low))) * 100
        st.markdown(_range_bar_html(low, high, price, pct), unsafe_allow_html=True)
    with col_profile:
        st.subheader("Company Profile")
        render_profile(tv_symbol)


def _render_analyst_rating(
    col: DeltaGenerator,
    rating_val: str | float | None,
) -> None:
    """
    Render a colour-coded analyst rating metric in the given column.

    Args:
        col: Streamlit column to render into.
        rating_val: Raw analyst rating value from the data source.
    """
    label, color = analyst_rating_label(rating_val)
    rating_number = ""
    if rating_val is not None:
        with contextlib.suppress(ValueError, TypeError):
            rating_number = fmt_number(float(rating_val), 1)
    label_style = (
        "font-size:0.82rem;color:rgb(120,120,120);font-weight:400;"
        'font-family:"Source Sans Pro",sans-serif;line-height:1.6;'
    )
    value_style = (
        "font-size:2.25rem;font-weight:400;"
        'font-family:"Source Sans Pro",sans-serif;line-height:1.2;'
    )
    sub_style = (
        "font-size:0.75rem;color:rgb(120,120,120);"
        'font-family:"Source Sans Pro",sans-serif;'
    )
    col.markdown(
        f"<div>"
        f'<label style="{label_style}">Analyst Rating</label>'
        f'<div style="{value_style}color:{color};">'
        f"{label}</div>"
        f'<div style="{sub_style}">{rating_number}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _range_bar_html(
    low: float,
    high: float,
    price: float,
    pct: float,
) -> str:
    """
    Build the HTML for a 52-week range progress bar.

    Args:
        low: 52-week low price.
        high: 52-week high price.
        price: Current last price.
        pct: Position within the range as a percentage (0-100).

    Returns:
        str: HTML string for the range bar visualisation.
    """
    muted = "#808495"
    track = "#e6e9ef"
    fill = "#16a34a"
    text = "#31333F"
    return (
        f'<div style="padding:8px 0 24px 0;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'font-size:0.8em;color:{muted};margin-bottom:6px;">'
        f"<span>{fmt_currency(low)}</span>"
        f"<span>{fmt_currency(high)}</span></div>"
        f'<div style="position:relative;height:10px;'
        f"background:{track};border-radius:5px;"
        f'overflow:visible;">'
        f'<div style="height:100%;width:{pct:.1f}%;'
        f"background:{fill};"
        f'border-radius:5px;"></div>'
        f'<div style="position:absolute;top:-4px;left:{pct:.1f}%;'
        f"transform:translateX(-50%);width:4px;height:18px;"
        f"background:{text};"
        f'border-radius:2px;"></div></div>'
        f'<div style="position:relative;height:20px;">'
        f'<div style="position:absolute;left:{pct:.1f}%;'
        f"transform:translateX(-50%);font-size:0.75em;"
        f'font-weight:600;color:{text};margin-top:4px;">'
        f"{fmt_currency(price)}</div></div></div>"
    )


def _render_tab_valuation(data: dict[str, Any]) -> None:
    """
    Render the Valuation tab metrics.

    Args:
        data: Row dict from the Universe grid.
    """
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trailing P/E", fmt_ratio(data.get("Trailing P/E")))
    c2.metric("Price/Book", fmt_ratio(data.get("Price/Book")))
    c3.metric("Trailing EPS", fmt_currency(data.get("Trailing EPS")))
    c4.metric("Dividend Yield", fmt_pct(data.get("Dividend Yield")))
    st.markdown("")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Market Volume", fmt_large_number(data.get("Market Volume")))
    c6.metric("Revenue/Share", fmt_currency(data.get("Revenue/Share")))
    c7.metric("52W Min", fmt_currency(data.get("52W Min")))
    c8.metric("52W Max", fmt_currency(data.get("52W Max")))


def _render_tab_profitability(data: dict[str, Any]) -> None:
    """
    Render the Profitability tab metrics with colour-coded percentages.

    Args:
        data: Row dict from the Universe grid.
    """
    c1, c2, c3, c4 = st.columns(4)
    render_colored_pct_metric(c1, "Profit Margin", data.get("Profit Margin"))
    render_colored_pct_metric(c2, "Gross Margin", data.get("Gross Margin"))
    render_colored_pct_metric(c3, "Operating Margin", data.get("Operating Margin"))
    render_colored_pct_metric(c4, "ROE", data.get("ROE"))
    st.markdown("")
    c5, c6 = st.columns(2)
    render_colored_pct_metric(c5, "ROA", data.get("ROA"))
    render_colored_pct_metric(c6, "1Y Performance", data.get("1Y Performance"))


def _render_tab_ownership(data: dict[str, Any]) -> None:
    """
    Render the Ownership & Float tab metrics.

    Args:
        data: Row dict from the Universe grid.
    """
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Held by Insiders", fmt_pct(data.get("Held Insiders")))
    c2.metric("Held by Institutions", fmt_pct(data.get("Held Institutions")))
    c3.metric("Short Interest", fmt_large_number(data.get("Short Interest")))
    c4.metric("Share Float", fmt_large_number(data.get("Share Float")))
    st.markdown("")
    c5, c6 = st.columns(2)
    c5.metric("Shares Outstanding", fmt_large_number(data.get("Shares Outstanding")))
    c6.metric("Market Cap", fmt_currency(data.get("Market Cap")))


def _render_tab_financials(data: dict[str, Any]) -> None:
    """
    Render the Financials tab metrics.

    Args:
        data: Row dict from the Universe grid.
    """
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue", fmt_currency(data.get("Revenue")))
    c2.metric("EBITDA", fmt_currency(data.get("EBITDA")))
    c3.metric("Total Debt", fmt_currency(data.get("Total Debt")))
    c4.metric("Free Cash Flow", fmt_currency(data.get("Free Cash Flow")))
    st.markdown("")
    c5, c6 = st.columns(2)
    c5.metric("Operating Cash Flow", fmt_currency(data.get("Operating Cash Flow")))
    c6.metric("Revenue/Share", fmt_currency(data.get("Revenue/Share")))


def _render_tab_identifiers(data: dict[str, Any]) -> None:
    """
    Render the Identifiers tab as a two-column table.

    Args:
        data: Row dict from the Universe grid.
    """
    fields = (
        "Symbol",
        "Share Class FIGI",
        "ISIN",
        "CUSIP",
        "CIK",
        "LEI",
        "MICs",
        "Currency",
    )
    id_data = {
        "Field": list(fields),
        "Value": [data.get(f) or "N/A" for f in fields],
    }
    st.dataframe(id_data, use_container_width=True, hide_index=True)

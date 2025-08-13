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

_SECTOR_BADGE = (
    "background-color:#4f46e5;padding:3px 10px;"
    "border-radius:12px;font-size:0.75em;color:#ffffff;"
    "margin-left:8px;display:inline-block;vertical-align:baseline;"
)
_INDUSTRY_BADGE = (
    "background-color:#0d9488;padding:3px 10px;"
    "border-radius:12px;font-size:0.75em;color:#ffffff;"
    "margin-left:8px;display:inline-block;vertical-align:baseline;"
)

_RATING_LABEL_STYLE = (
    "font-size:0.82rem;color:rgb(120,120,120);font-weight:400;"
    'font-family:"Source Sans Pro",sans-serif;line-height:1.6;'
)
_RATING_VALUE_STYLE = (
    "font-size:2.25rem;font-weight:400;"
    'font-family:"Source Sans Pro",sans-serif;line-height:1.2;'
)
_RATING_SUB_STYLE = (
    "font-size:0.75rem;color:rgb(120,120,120);"
    'font-family:"Source Sans Pro",sans-serif;'
)

_TEXT_COLOR = "#31333F"
_MUTED_COLOR = "#808495"
_RANGE_TRACK = "#e6e9ef"
_RANGE_FILL = "#16a34a"

_IDENTIFIER_FIELDS = (
    "Symbol",
    "Share Class FIGI",
    "ISIN",
    "CUSIP",
    "CIK",
    "LEI",
    "MICs",
    "Currency",
)


def render_header(
    name: str,
    logoid: str | None,
    data: dict[str, Any],
) -> None:
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


def _badge_html(data: dict[str, Any]) -> str:
    parts: list[str] = []
    sector = data.get("Sector", "")
    if sector:
        parts.append(f'<span style="{_SECTOR_BADGE}">{sector}</span>')
    industry = data.get("Industry", "")
    if industry:
        parts.append(f'<span style="{_INDUSTRY_BADGE}">{industry}</span>')
    return "".join(parts)


def render_metrics_banner(data: dict[str, Any]) -> None:
    perf_1y = data.get("1Y Performance")
    delta = f"{fmt_pct(perf_1y)} (1Y)" if perf_1y is not None else None

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Last Price", fmt_currency(data.get("Last Price")), delta=delta)
    m2.metric("Market Cap", fmt_currency(data.get("Market Cap")))
    m3.metric("Trailing P/E", fmt_ratio(data.get("Trailing P/E")))
    m4.metric("Dividend Yield", fmt_pct(data.get("Dividend Yield")))
    _render_analyst_rating(m5, data.get("Analyst Rating"))
    st.divider()


def _render_analyst_rating(
    col: DeltaGenerator,
    rating_val: str | float | None,
) -> None:
    label, color = analyst_rating_label(rating_val)
    rating_number = ""
    if rating_val is not None:
        with contextlib.suppress(ValueError, TypeError):
            rating_number = fmt_number(float(rating_val), 1)
    col.markdown(
        f"<div>"
        f'<label style="{_RATING_LABEL_STYLE}">Analyst Rating</label>'
        f'<div style="{_RATING_VALUE_STYLE}color:{color};">'
        f"{label}</div>"
        f'<div style="{_RATING_SUB_STYLE}">{rating_number}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_52w_range_and_profile(
    data: dict[str, Any],
    tv_symbol: str,
) -> None:
    low = data.get("52W Min")
    high = data.get("52W Max")
    price = data.get("Last Price")
    has_range = (
        low is not None
        and high is not None
        and price is not None
        and high > low
    )

    if not has_range:
        st.subheader("Company Profile")
        render_profile(tv_symbol)
        return

    col_range, col_profile = st.columns(2, gap="large")
    with col_range:
        st.subheader("52-Week Range")
        pct = max(0.0, min(1.0, (price - low) / (high - low))) * 100
        st.markdown(_range_bar_html(low, high, price, pct), unsafe_allow_html=True)
    with col_profile:
        st.subheader("Company Profile")
        render_profile(tv_symbol)


def _range_bar_html(low: float, high: float, price: float, pct: float) -> str:
    return (
        f'<div style="padding:8px 0 24px 0;">'
        f'<div style="display:flex;justify-content:space-between;'
        f"font-size:0.8em;color:{_MUTED_COLOR};margin-bottom:6px;\">"
        f"<span>{fmt_currency(low)}</span>"
        f"<span>{fmt_currency(high)}</span></div>"
        f'<div style="position:relative;height:10px;'
        f"background:{_RANGE_TRACK};border-radius:5px;"
        f'overflow:visible;">'
        f'<div style="height:100%;width:{pct:.1f}%;'
        f"background:{_RANGE_FILL};"
        f'border-radius:5px;"></div>'
        f'<div style="position:absolute;top:-4px;left:{pct:.1f}%;'
        f"transform:translateX(-50%);width:4px;height:18px;"
        f"background:{_TEXT_COLOR};"
        f'border-radius:2px;"></div></div>'
        f'<div style="position:relative;height:20px;">'
        f'<div style="position:absolute;left:{pct:.1f}%;'
        f"transform:translateX(-50%);font-size:0.75em;"
        f"font-weight:600;color:{_TEXT_COLOR};margin-top:4px;\">"
        f"{fmt_currency(price)}</div></div></div>"
    )


def render_detail_tabs(data: dict[str, Any]) -> None:
    tab_names = [
        "Valuation", "Profitability", "Ownership & Float",
        "Financials", "Identifiers",
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


def _render_tab_valuation(data: dict[str, Any]) -> None:
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
    id_data = {
        "Field": list(_IDENTIFIER_FIELDS),
        "Value": [data.get(f) or "N/A" for f in _IDENTIFIER_FIELDS],
    }
    st.dataframe(id_data, use_container_width=True, hide_index=True)

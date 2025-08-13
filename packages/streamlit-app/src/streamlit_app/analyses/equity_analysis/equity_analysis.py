# equity_analysis.py

import streamlit as st

from streamlit_app.analyses.equity_analysis.renderers import (
    render_52w_range_and_profile,
    render_detail_tabs,
    render_header,
    render_metrics_banner,
)
from streamlit_app.analyses.equity_analysis.tradingview import (
    fetch_logo,
    render_chart,
    resolve_tv_symbol,
)

# Session state guard
data = st.session_state.get("selected_equity_data")
name = st.session_state.get("selected_equity_name")

if not data or not name:
    st.info("Select an equity from the Universe table to view its analysis.")
    st.stop()

# Resolve TradingView data
tv_symbol = resolve_tv_symbol(data.get("Symbol", ""), name, data.get("MICs"))
tv_logoid = fetch_logo(tv_symbol)

# Page layout
render_header(name, tv_logoid, data)
render_metrics_banner(data)
render_chart(tv_symbol)
st.divider()
render_52w_range_and_profile(data, tv_symbol)
st.divider()
render_detail_tabs(data)
